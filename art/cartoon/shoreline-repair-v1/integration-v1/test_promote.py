"""Disposable preflight controls. Synthetic native PASS is never promotion proof."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    a = p.parse_args()
    assert not a.work.exists(), 'fresh work required'
    work = a.work.resolve()
    fixture = work / 'fixture'
    local = fixture / REL
    inputs = load(HERE / 'inputs.json')
    names = set(inputs['protected_files_sha256']) | set(inputs['maintained_tools_lf_sha256'])
    names |= {(REL / n).as_posix() for n in ('inputs.json', 'integrate.py', 'promote.py', 'evidence/fresh-replay/verification.json')}
    for name in names:
        dst = fixture / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dst)
    pack = fixture / 'art/cartoon/pack.json'
    pack.write_bytes((HERE / 'prior-pack.json').read_bytes())
    baseline = fixture / 'assets/scrantic_data.zip'
    baseline.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(a.baseline, baseline)
    candidate = work / 'candidate.zip'
    shutil.copy2(a.candidate, candidate)
    native = {'status': 'PASS', 'phase': 'full', 'package_pair': {'candidate_sha256': sha(candidate.read_bytes())},
              'smoke_captures': 28, 'fresh_repeat_captures': 28, 'negative_controls': 8}
    native_path = fixture / 'build/synthetic-native-summary.json'
    write(native_path, native)
    helper = local / 'promote.py'
    current_digest = sha(helper.read_bytes())
    records = []
    protected_real = {str(path): sha(path.read_bytes()) for path in (ROOT / 'assets/scrantic_data.zip', ROOT / 'art/cartoon/pack.json', a.candidate, a.baseline)}

    def run(name, expect=None, executable=helper, summary_digest=None, existing=False):
        out = work / (name+'.json')
        if existing:
            write(out, {'existing': True})
        argv = [sys.executable, '-B', str(executable), '--candidate', str(candidate), '--native-summary', str(native_path),
                '--native-summary-sha256', summary_digest or sha(native_path.read_bytes()), '--report', str(out)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=90)
        for stream in ('stdout', 'stderr'):
            (work / (name+'.'+stream+'.txt')).write_text(getattr(result, stream), encoding='utf-8', newline='\n')
        assert result.stdout.splitlines()[0] == 'WITNESS shore-promote ' + sha(executable.read_bytes()), name
        if expect:
            assert result.returncode == 1 and result.stderr.strip() == 'FAIL ' + expect, (name, result.stderr)
            assert not out.exists() or existing, name
        else:
            assert result.returncode == 0 and load(out)['production_promoted'] is False, (name, result.stderr)
        records.append({'name': name, 'status': 'FIRED' if expect else 'PASS', 'failure': expect,
                        'executed_helper_sha256': sha(executable.read_bytes()), 'exit_code': result.returncode})

    run('smoke-preflight')
    # Each fault has one expected named failure, then is restored before the next.
    raw = candidate.read_bytes(); candidate.write_bytes(raw+b'damaged')
    run('candidate-bytes', 'candidate: verified package identity'); candidate.write_bytes(raw)
    proof = local / 'evidence/fresh-replay/verification.json'; original = proof.read_bytes()
    changed = load(proof); changed['status'] = 'FAIL'; write(proof, changed)
    run('package-status', 'candidate: verified package identity'); proof.write_bytes(original)
    run('native-digest', 'native: summary identity', summary_digest='0'*64)
    for key, value in [('status', 'FAIL'), ('phase', 'smoke'), ('candidate_sha256', '0'*64)]:
        changed = copy.deepcopy(native)
        if key == 'candidate_sha256': changed['package_pair'][key] = value
        else: changed[key] = value
        write(native_path, changed)
        run('native-'+key, 'native: successful candidate composition required')
        write(native_path, native)
    for key in ('smoke_captures', 'fresh_repeat_captures', 'negative_controls'):
        changed = copy.deepcopy(native); changed[key] -= 1; write(native_path, changed)
        run('coverage-'+key, 'native: final scoped gate coverage'); write(native_path, native)
    raw = pack.read_bytes(); changed = load(pack); changed['scope'] += ' damaged'; write(pack, changed)
    run('live-ledger', 'production ledger differs from prior'); pack.write_bytes(raw)
    raw = baseline.read_bytes(); baseline.write_bytes(raw+b'damaged')
    run('live-archive', 'production archive differs from prior'); baseline.write_bytes(raw)
    recipe = local / 'runtime-recipe.json'; raw = recipe.read_bytes()
    changed = load(recipe); changed['frames'][0]['candidate_png_sha256'] = '0'*64; write(recipe, changed)
    pins = local / 'inputs.json'; old_pins = pins.read_bytes(); changed_pins = load(pins)
    changed_pins['protected_files_sha256'][(REL/'runtime-recipe.json').as_posix()] = sha(recipe.read_bytes()); write(pins, changed_pins)
    run('full-member-map', 'candidate: complete payload map differs'); recipe.write_bytes(raw); pins.write_bytes(old_pins)
    run('existing-report', 'report: use a fresh output', existing=True)
    # Disable the reachable native result/identity guard and execute the wrong
    # candidate summary again. No invocation includes --promote.
    text = helper.read_text(encoding='utf-8')
    needle = "    require(native['status'] == 'PASS' and native['phase'] == 'full' and native['package_pair']['candidate_sha256'] == sha(raw), 'native: successful candidate composition required')"
    assert text.count(needle) == 1
    mutant = local / 'promote-native-guard-removed.py'
    mutant.write_text(text.replace(needle, '    pass  # executed native guard-removal control'), encoding='utf-8', newline='\n')
    changed = copy.deepcopy(native); changed['package_pair']['candidate_sha256'] = '0'*64; write(native_path, changed)
    run('removed-native-guard', executable=mutant)
    write(native_path, native)
    run('restored-positive')
    assert sha(helper.read_bytes()) == current_digest
    assert protected_real == {name: sha(Path(name).read_bytes()) for name in protected_real}
    assert sha(pack.read_bytes()) == sha((HERE/'prior-pack.json').read_bytes()) and sha(baseline.read_bytes()) == inputs['baseline_archive_sha256']
    write(work / 'verification.json', {'status': 'PASS', 'helper_sha256': current_digest, 'test_sha256': sha(Path(__file__).read_bytes()),
          'scope': 'Disposable promotion preflight only. Synthetic native summaries test refusal logic; they provide no native execution or promotion authorization.',
          'smoke_before_regression': True, 'controls': records, 'guard_removal_accepts_wrong_native_candidate': True,
          'live_files_unchanged': protected_real, 'production_promoted': False,
          'files_sha256': {p.name: sha(p.read_bytes()) for p in sorted(work.iterdir()) if p.is_file() and p.suffix in ('.json', '.txt')},
          'mutant_sha256': sha(mutant.read_bytes()), 'mutant_source_path': str(mutant)})
    print(json.dumps({'status': 'PASS', 'controls': len(records), 'production_promoted': False}))


if __name__ == '__main__':
    main()
