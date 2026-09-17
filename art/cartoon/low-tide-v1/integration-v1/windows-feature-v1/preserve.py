"""Freeze compact Windows deployment proof and an identity-only native binding."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
OUT = ROOT / 'build/seasonal-final-windows/low-tide-feature-v1'
EXPECTED = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
NATIVE = ROOT / 'art/cartoon/low-tide-v1/waves-native-v1/evidence-v1/evidence.json'
NATIVE_SHA = '94461ceb13084a3a35446a9d3c7ce8d747c7a29eb868135a4d3b21e12857279e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_bytes((json.dumps(obj, indent=2) + '\n').encode())


def main():
    if (HERE / 'evidence.json').exists() or (HERE / 'native-binding.json').exists():
        raise ValueError('refusing existing verification evidence')
    result = json.loads((OUT / 'result.json').read_bytes())
    running = json.loads((OUT / 'running.json').read_bytes())
    native = json.loads(NATIVE.read_bytes())
    if sha(NATIVE) != NATIVE_SHA:
        raise ValueError('accepted native evidence identity changed')
    if sha(ROOT / 'assets/scrantic_data.zip') != EXPECTED or sha(ROOT / 'build/Release/scrantic_data.zip') != EXPECTED:
        raise ValueError('source/deployed archive differ from approved candidate')
    source_pins = {p: h for p, h in native['protected_source_sha256'].items() if p != 'assets/scrantic_data.zip'}
    helper_pins = native['capture_helper_sha256']
    for relative, digest in {**source_pins, **helper_pins}.items():
        if sha(ROOT / relative) != digest:
            raise ValueError('native source/helper changed; fresh scene proof required: ' + relative)
    pack = json.loads((ROOT / 'art/cartoon/pack.json').read_bytes())
    if len(pack['assets']) != 61:
        raise ValueError('integrated pack is not the expected61 assets')
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    save(HERE / 'native-binding.json', {'schema_version': 1, 'status': 'PASS', 'source_commit_at_readback': commit,
        'promoted_archive_sha256': EXPECTED, 'deployed_archive_sha256': EXPECTED,
        'pack_path': 'art/cartoon/pack.json', 'pack_sha256': sha(ROOT / 'art/cartoon/pack.json'), 'asset_count': 61,
        'accepted_native_evidence': {'path': NATIVE.relative_to(ROOT).as_posix(), 'sha256': NATIVE_SHA},
        'accepted_native_readback': {'path': NATIVE.with_name('readback.json').relative_to(ROOT).as_posix(),
                                     'sha256': sha(NATIVE.with_name('readback.json'))},
        'runtime_source_sha256': source_pins, 'capture_helper_sha256': helper_pins,
        'historical_smokes': native['smoke_captures'], 'historical_fresh_repeats': native['fresh_repeat_captures'],
        'historical_high_tide_identical_displays': native['high_tide_identical_displays'],
        'scope': 'Exact promoted/deployed bytes and unchanged runtime/helpers link to the already executed native scene proof. This is an identity readback, not a new Linux/Xvfb capture. Fresh Windows compilation/deployment is recorded separately.'})
    originals = ['running.json', 'adaptation.json', 'gate-adaptation.diff', 'gate-retained.ps1', 'gate.log', 'result.json']
    rows = []
    for name in originals:
        source = OUT / name
        target = HERE / name
        if target.exists():
            raise ValueError('refusing existing copied evidence: ' + name)
        raw = source.read_bytes()
        target.write_bytes(raw)
        rows.append({'path': name, 'source': source.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'bytes': len(raw)})
    cache = ROOT / 'build/CMakeCache.txt'
    (HERE / 'CMakeCache.txt').write_bytes(cache.read_bytes())
    rows.append({'path': 'CMakeCache.txt', 'source': 'build/CMakeCache.txt', 'sha256': sha(cache), 'bytes': cache.stat().st_size})
    compiler_files = list((ROOT / 'build/CMakeFiles').glob('*/CMakeCCompiler.cmake'))
    for source in compiler_files:
        relative = 'compiler/' + source.parent.name + '-' + source.name
        target = HERE / relative
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(source.read_bytes())
        rows.append({'path': relative, 'source': source.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'bytes': source.stat().st_size})
    # Existing helper sources are already durable; bind rather than duplicate them.
    dependencies = ('art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py',
                    'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py',
                    'gate.ps1', 'CMakeLists.txt')
    pins = {p: sha(ROOT / p) for p in dependencies}
    if pins[dependencies[0]] != running['launcher_sha256'] or pins[dependencies[1]] != running['helper_sha256']:
        raise ValueError('executed gate helper identity changed')
    # Preserve small renderer logs once; raw PPMs remain in scratch with result hashes.
    for family in ('wave-smoke', 'wave-regression', 'palm-smoke', 'palm-regression'):
        for source in sorted((OUT / family).rglob('*.log')):
            relative = 'renderer-logs/' + source.relative_to(OUT).as_posix()
            target = HERE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            rows.append({'path': relative, 'source': source.relative_to(ROOT).as_posix(), 'sha256': sha(source), 'bytes': source.stat().st_size})
    log = (OUT / 'gate.log').read_text(encoding='utf-8', errors='replace')
    warnings = [line for line in log.splitlines() if 'WARN' in line or ': warning ' in line
                or re.search(r'\bskipped\b|^\s*SKIP\b', line)]
    record = {'schema_version': 1, 'status': 'PASS' if result['passed'] else 'FAIL', 'exact_copies': rows,
        'dependency_sha256': pins, 'protected_before_run_sha256': running['protected_sha256'],
        'native_binding_sha256': sha(HERE / 'native-binding.json'), 'preserver_sha256': sha(Path(__file__)),
        'command': running['command'], 'source_commit_at_preservation': commit,
        'source_archive_sha256': EXPECTED, 'deployed_archive_sha256': result['deployed_archive_sha256'],
        'binary_sha256': sha(ROOT / 'build/Release/jc_reborn.exe'),
        'observed_inactive_window_count': len(result['observed_inactive_windows']),
        'input_desktop_preserved': result['input_desktop_preserved'], 'protected_inputs_unchanged': result['protected_inputs_unchanged'],
        'warnings_and_skips': warnings, 'retained_capture_count': len(result['retained_captures']),
        'excluded': 'No executables, ZIPs or bulk PPMs copied. result.json retains native PPM hashes, dimensions and capture-marker observations.',
        'scope': 'Fresh full Windows configure/build/smoke/regression on an inactive desktop. Gate assertions/order unchanged. No original executable test or new Linux scene capture claimed.'}
    save(HERE / 'evidence.json', record)
    for row in rows:
        if sha(HERE / row['path']) != row['sha256'] or sha(ROOT / row['source']) != row['sha256']:
            raise ValueError('exact-copy readback mismatch: ' + row['path'])
    save(HERE / 'readback.json', {'status': 'PASS', 'evidence_sha256': sha(HERE / 'evidence.json'),
        'exact_copies_checked': len(rows), 'original_sources_checked': len(rows), 'copied_bytes': sum(r['bytes'] for r in rows)})
    print(json.dumps({'evidence_sha256': sha(HERE / 'evidence.json'), 'readback_sha256': sha(HERE / 'readback.json'),
        'native_binding_sha256': sha(HERE / 'native-binding.json'), 'copied_files': len(rows),
        'copied_bytes': sum(r['bytes'] for r in rows), 'gate_passed': result['passed']}, indent=2))


if __name__ == '__main__':
    main()
