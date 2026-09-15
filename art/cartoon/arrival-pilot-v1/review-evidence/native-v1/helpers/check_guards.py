"""Bounded real-Python guard controls; does not rerun or mutate native production."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    spec = importlib.util.spec_from_file_location('arrival_guard_subject', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def probe(module_path, fixture, label):
    module = load(module_path)
    print('WITNESS source=' + sha(module_path.read_bytes()) + ' file=' + str(module_path), flush=True)
    if label == 'arrival-outside-pixels':
        # Same pixels and changes inside the permitted rectangle are controls;
        # changes to left, right, above and below must each be rejected.
        base = bytes(1280 * 960 * 3)
        box = [596, 480, 660, 634]
        assert module.outside_equal(base, base, box)
        for x, y, allowed in [(600, 500, True), (595, 500, False), (660, 500, False), (600, 479, False), (600, 634, False)]:
            altered = bytearray(base)
            altered[(y * 1280 + x) * 3] = 1
            if module.outside_equal(base, altered, box) != allowed:
                print('FAIL ' + label)
                return 1
        print('PASS ' + label)
        return 0
    try:
        module.read_candidate(fixture)
    except ValueError as error:
        if str(error) == label:
            print('PASS expected-refusal:' + label)
            return 0
        raise
    if label == 'valid-candidate':
        print('PASS valid-candidate')
        return 0
    print('FAIL expected-refusal:' + label)
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe-module', type=Path)
    parser.add_argument('--fixture', type=Path)
    parser.add_argument('--label')
    args = parser.parse_args()
    if args.probe_module:
        return probe(args.probe_module, args.fixture, args.label)
    folder = HERE / 'guard-checks-v1'
    assert not folder.exists(), 'preserve-prior-guard-evidence'
    folder.mkdir()
    source = HERE / 'prepare_candidate.py'
    source_text = source.read_text()
    valid = ROOT / 'build/arrival-export-v1'
    records = []

    def run(module, fixture, label, expected):
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--probe-module', str(module), '--fixture', str(fixture), '--label', label]
        result = subprocess.run(command, text=True, capture_output=True, timeout=30)
        digest = sha(module.read_bytes())
        assert result.returncode == expected, result.stdout + result.stderr
        assert 'WITNESS source=' + digest in result.stdout
        failures = [line for line in result.stdout.splitlines() if line.startswith('FAIL ')]
        assert len(failures) == expected and not result.stderr, result.stdout + result.stderr
        return {'source_sha256': digest, 'exit_code': result.returncode, 'stdout': result.stdout,
                'exact_named_failures': failures}

    records.append({'control': 'valid-candidate', **run(source, valid, 'valid-candidate', 0)})
    cases = [
        ('runtime-export-required', "require(report['preview_only'] is False and report['runtime_sprites_written'] is True\n            and report['runtime_fit_all_source_centers'] is True, 'runtime-export-required')"),
        ('arrival-only-frame-set', "require([r['frame'] for r in recipe['frames']] == [18]\n            and [r['frame'] for r in report['frames']] == [18], 'arrival-only-frame-set')"),
        ('raw-source-identity', "require(sha(source.read_bytes()) == entry['source_sha256'] == observed['source_sha256'], 'raw-source-identity')"),
    ]
    for index, (label, old) in enumerate(cases):
        fixture = folder / label
        shutil.copytree(valid, fixture)
        recipe = json.loads((fixture / 'recipe.json').read_bytes())
        report = json.loads((fixture / 'export-report.json').read_bytes())
        if index == 0:
            report['preview_only'] = True
        elif index == 1:
            recipe['frames'][0]['frame'] = report['frames'][0]['frame'] = 19
        else:
            recipe['frames'][0]['source_sha256'] = report['frames'][0]['source_sha256'] = '0' * 64
        raw = (json.dumps(recipe, indent=2) + '\n').encode()
        (fixture / 'recipe.json').write_bytes(raw)
        report['recipe_sha256'] = sha(raw)
        (fixture / 'export-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
        control = run(source, fixture, label, 0)
        assert source_text.count(old) == 1
        mutant = HERE / f'prepare-guard-mutant-{index}.py'
        mutant.write_text(source_text.replace(old, 'pass  # isolated removed guard'), encoding='utf-8', newline='\n')
        fired = run(mutant, fixture, label, 1)
        assert fired['source_sha256'] != control['source_sha256']
        records.append({'guard': label, 'normal_refusal': control, 'mutation': fired, 'result': 'FIRED'})
    capture = HERE / 'capture.py'
    control = run(capture, valid, 'arrival-outside-pixels', 0)
    code = capture.read_text()
    start, end = code.index('def outside_equal('), code.index('\n\ndef capture(')
    mutant = HERE / 'capture-outside-mutant.py'
    mutant.write_text(code[:start] + 'def outside_equal(a, b, box):\n    return True\n' + code[end:], encoding='utf-8', newline='\n')
    fired = run(mutant, valid, 'arrival-outside-pixels', 1)
    records.append({'guard': 'arrival-outside-pixels', 'normal_control': control, 'mutation': fired, 'result': 'FIRED'})
    report = {'status': 'PASS', 'test_sha256': sha(Path(__file__).read_bytes()), 'records': records,
              'scope': 'Python source copies executed by fresh child interpreters with exact source SHA witnesses. Four mutations each produce exactly one named failure. No native binary was rebuilt or modified; baseline/candidate native runs have separate evidence.'}
    (folder / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS valid candidate, three bad-input refusals, varied inside/outside pixel axes; 4/4 exact-source mutations fired')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
