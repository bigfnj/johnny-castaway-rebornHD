"""Compact readback of the unchanged full Windows gate and reviewed cloud bytes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
OUT = ROOT / 'build/seasonal-final-windows/clouds-feature-v1'
EXPECTED = 'a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d'
NATIVE = ROOT / 'art/cartoon/clouds-v1/native-v1/evidence-v1'
NATIVE_SHA = '1d156cb3f398643d4a8d4be9a9d65943396bd15c61a9b9c87d76efcf46045ce0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())


def require(ok, label):
    if not ok:
        raise ValueError('Windows cloud readback: ' + label)


def validate_result(result):
    require(result['passed'] and result['exit_code'] == 0, 'result.json full gate PASS')
    require(result['input_desktop_preserved'] and result['observed_inactive_windows'], 'result.json inactive desktop')
    require(result['protected_inputs_unchanged'] and not result['changed_inputs'], 'result.json protected inputs')
    require(result['source_archive_sha256'] == result['deployed_archive_sha256'] == EXPECTED, 'result.json approved archive')
    require(len(result['retained_captures']) == 32, 'result.json 32 renderer captures')
    for row in result['retained_captures']:
        require(row['complete_ppm'] and row['capture_marker'], row['path'] + ' complete PPM and marker')


def main():
    require(not (HERE / 'evidence.json').exists(), 'existing evidence is immutable')
    result = json.loads((OUT / 'result.json').read_bytes())
    running = json.loads((OUT / 'running.json').read_bytes())
    validate_result(result)
    require(sha(OUT / 'gate.log') == result['log_sha256'], 'gate.log identity')
    for row in result['retained_captures']:
        path = ROOT / row['path']
        require(sha(path) == row['ppm_sha256'], row['path'] + ' PPM hash')
        require(sha(path.with_suffix('.log')) == row['log_sha256'], row['path'] + ' native log hash')
    for path, digest in running['protected_sha256'].items():
        require(sha(ROOT / path) == digest, path + ' post-gate source identity')
    require(sha(NATIVE / 'evidence.json') == NATIVE_SHA, 'reviewed native evidence identity')
    native = json.loads((NATIVE / 'native/inputs.json').read_bytes())
    native_summary = json.loads((NATIVE / 'native/summary.json').read_bytes())
    require(native_summary['candidate_sha256'] == EXPECTED, 'reviewed native candidate identity')
    runtime_pins = {p: h for p, h in native['protected_sha256'].items() if p != 'assets/scrantic_data.zip'}
    for path, digest in {**runtime_pins, **native['helpers_sha256']}.items():
        require(sha(ROOT / path) == digest, path + ' historical native source identity')
    require(sha(ROOT / 'assets/scrantic_data.zip') == sha(ROOT / 'build/Release/scrantic_data.zip') == EXPECTED, 'actual source/deployed ZIP')
    pack = json.loads((ROOT / 'art/cartoon/pack.json').read_bytes())
    require(len(pack['assets']) == 63, 'art/cartoon/pack.json 63 assets')
    # Actual result copied in memory: a missing native capture marker must fail
    # exactly at that named capture. The untouched positive is checked again.
    damaged = json.loads(json.dumps(result))
    damaged['retained_captures'][0]['capture_marker'] = False
    label = damaged['retained_captures'][0]['path'] + ' complete PPM and marker'
    try:
        validate_result(damaged)
    except ValueError as exc:
        require(str(exc) == 'Windows cloud readback: ' + label, 'named damaged marker control')
        negative = {'status': 'FIRED', 'failure': str(exc)}
    else:
        raise ValueError('Windows cloud readback: missing marker survived')
    validate_result(result)
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    binding = {'status': 'PASS', 'source_commit_at_readback': commit, 'archive_sha256': EXPECTED,
        'asset_count': 63, 'pack_sha256': sha(ROOT / 'art/cartoon/pack.json'),
        'native_evidence': {'path': (NATIVE / 'evidence.json').relative_to(ROOT).as_posix(), 'sha256': NATIVE_SHA},
        'native_readback_sha256': sha(NATIVE / 'readback.json'), 'runtime_source_sha256': runtime_pins,
        'capture_helper_sha256': native['helpers_sha256'], 'historical_native_cases': native_summary['cases'],
        'scope': 'Identity link to eight previously executed smokes and eight fresh native repeats. This is not a new Linux scene run. Fresh Windows build/deployment is separate.'}
    save(HERE / 'native-binding.json', binding)
    originals = {name: OUT / name for name in ('running.json', 'adaptation.json', 'gate-adaptation.diff', 'gate-retained.ps1', 'gate.log', 'result.json')}
    originals['CMakeCache.txt'] = ROOT / 'build/CMakeCache.txt'
    for path in (ROOT / 'build/CMakeFiles').glob('*/CMakeCCompiler.cmake'):
        originals['compiler/' + path.parent.name + '-' + path.name] = path
    copies = []
    for name, source in originals.items():
        target = HERE / name
        require(not target.exists(), name + ' fresh copy')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        copies.append({'path': name, 'source': source.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'bytes': source.stat().st_size})
    dependencies = ('art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py',
                    'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py', 'gate.ps1', 'CMakeLists.txt')
    pins = {p: sha(ROOT / p) for p in dependencies}
    require(pins[dependencies[0]] == running['launcher_sha256'] and pins[dependencies[1]] == running['helper_sha256'], 'executed launcher/helper identity')
    text = (OUT / 'gate.log').read_text(encoding='utf-8', errors='replace')
    record = {'schema_version': 1, 'status': 'PASS', 'exact_copies': copies, 'dependency_sha256': pins,
        'protected_before_run_sha256': running['protected_sha256'], 'command': running['command'],
        'source_commit_at_preservation': commit, 'source_archive_sha256': EXPECTED,
        'deployed_archive_sha256': result['deployed_archive_sha256'], 'binary_sha256': sha(ROOT / 'build/Release/jc_reborn.exe'),
        'poll_checks': result['poll_checks'], 'observed_inactive_window_count': len(result['observed_inactive_windows']),
        'input_desktop_preserved': result['input_desktop_preserved'], 'native_binding_sha256': sha(HERE / 'native-binding.json'),
        'warnings_and_skips': [line for line in text.splitlines() if 'WARN' in line or ': warning ' in line or re.search(r'\bskipped\b|^\s*SKIP\b', line)],
        'retained_captures_read_back': len(result['retained_captures']), 'damaged_marker_control': negative,
        'preserver_sha256': sha(Path(__file__)),
        'excluded': 'No binaries, archives, PPMs or duplicate per-renderer logs copied. All 32 native PPM/log hashes and capture markers were read back and remain in result.json.',
        'scope': 'Unchanged full Windows gate on an inactive desktop, fresh configure/build then smoke/regression. No original executable or physical display behavior claim.'}
    save(HERE / 'evidence.json', record)
    for row in copies:
        require(sha(HERE / row['path']) == sha(ROOT / row['source']) == row['sha256'], row['path'] + ' exact-copy readback')
    save(HERE / 'readback.json', {'status': 'PASS', 'evidence_sha256': sha(HERE / 'evidence.json'),
        'exact_copies_checked': len(copies), 'copied_bytes': sum(row['bytes'] for row in copies),
        'renderer_capture_and_log_pairs_checked': 32, 'restored_result_control': 'PASS'})
    print(json.dumps({'evidence_sha256': sha(HERE / 'evidence.json'), 'readback_sha256': sha(HERE / 'readback.json'), 'copied_files': len(copies)}, indent=2))


if __name__ == '__main__':
    main()
