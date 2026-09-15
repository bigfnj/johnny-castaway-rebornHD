"""Replay real capture inputs with one changed walking pixel against capture.py."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
LABEL = 'capture.py:full:unchanged-full-frame:1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def probe(source, output):
    spec = importlib.util.spec_from_file_location('arrival_capture_replay', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = HERE
    print('WITNESS source=' + sha(source.read_bytes()) + ' compiled=' + module.capture.__code__.co_filename, flush=True)
    saved = HERE / 'candidate-v1/full'
    binding = json.loads((HERE / 'source-reuse.json').read_bytes())
    candidate = json.loads((HERE / 'candidate-v1/preparation.json').read_bytes())
    manifest = json.loads((saved / 'report.json').read_bytes())
    assert manifest['status'] == 'PASS' and manifest['displays'][0]['frame'] == 11
    for row in manifest['displays']:
        assert sha(module.ppm(saved / row['ppm'])) == row['pixels_sha256']
    assert sha((saved / 'capture.log').read_bytes()) == manifest['log_sha256']

    def replay(*args, **kwargs):
        target = kwargs['cwd']
        kwargs['stdout'].write((saved / 'capture.log').read_bytes())
        kwargs['stdout'].flush()
        for path in saved.glob('*.ppm'):
            if path.name == 'display-001.ppm':
                raw = bytearray(path.read_bytes())
                header = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\s', raw)
                raw[header.end()] ^= 1
                (target / path.name).write_bytes(raw)
            else:
                os.link(path, target / path.name)
        return subprocess.CompletedProcess(args[0], 0)

    actual_run = module.subprocess.run
    module.subprocess.run = replay
    try:
        module.capture(HERE / 'baseline/rear_route_probe', HERE / 'candidate-v1/scrantic_data.zip', output,
                       'full', candidate, binding)
    except ValueError as error:
        assert str(error) == 'full: unchanged-full-frame:1', str(error)
        print('PASS expected refusal ' + LABEL)
        return 0
    finally:
        module.subprocess.run = actual_run
    print('FAIL ' + LABEL)
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.source:
        return probe(args.source, args.output)
    output = HERE / 'walking-replay-v1'
    assert not output.exists(), 'preserve-prior-replay-evidence'
    output.mkdir()
    source = HERE / 'capture.py'
    text = source.read_text()
    old = "require(pixels == reference, f'{phase}: unchanged-full-frame:{index}')"
    assert text.count(old) == 1
    mutant = HERE / 'capture-walking-guard-mutant.py'
    mutant.write_text(text.replace(old, 'pass  # isolated removed exact-walking guard'), encoding='utf-8', newline='\n')
    records = []
    for label, path, expected in [('normal-refusal', source, 0), ('removed-guard', mutant, 1)]:
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--source', str(path),
                                 '--output', str(output / label)], text=True, capture_output=True, timeout=90)
        digest = sha(path.read_bytes())
        assert result.returncode == expected and not result.stderr, result.stdout + result.stderr
        assert 'WITNESS source=' + digest in result.stdout
        failures = [s for s in result.stdout.splitlines() if s.startswith('FAIL ')]
        assert failures == ([] if not expected else ['FAIL ' + LABEL]), result.stdout
        records.append({'case': label, 'source_sha256': digest, 'exit_code': result.returncode,
                        'named_failures': failures, 'stdout': result.stdout})
    report = {'status': 'PASS', 'mutation': 'FIRED', 'failure_count': 1, 'label': LABEL,
              'test_sha256': sha(Path(__file__).read_bytes()), 'records': records,
              'original_capture_report_sha256': sha((HERE / 'candidate-v1/full/report.json').read_bytes()),
              'scope': 'Actual capture.py comparison replay with hash-verified saved native PPM/log inputs; only one first-walking background pixel changed. The subprocess execution seam is substituted to replay captures. No new native execution, production mutation, or browser-page change. The real source refuses; removing its guard reaches exactly one named external failure.'}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS changed walking pixel refused; actual source guard removal fired one named replay failure')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
