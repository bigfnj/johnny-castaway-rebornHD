"""One-time compact readback of the two main gate attempts and reviewed sources."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
OUT = Path(__file__).resolve().parent
SHA = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
HEAD = '024c9943a08ede16cfa24ed37aa768cf1f020b63'
RUNS = ROOT / 'build/seasonal-final-windows'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def save(name, value):
    path = OUT / name
    data = (json.dumps(value, indent=2) + '\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes() == data, 'Existing record differs: ' + str(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def command(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


if (OUT / 'evidence.json').exists():
    raise SystemExit('Existing evidence preserved')
assert command('rev-parse', 'HEAD') == HEAD
observer = RUNS / 'low-tide-main-v2-observer.json'
observed = read(observer)
first = RUNS / 'low-tide-main-v1'
second = RUNS / 'low-tide-main-v2'
result = read(second / 'result.json') if (second / 'result.json').exists() else None
source = ROOT / 'assets/scrantic_data.zip'
deployed = ROOT / 'build/Release/scrantic_data.zip'
assert sha(source) == sha(deployed) == SHA
feature = ROOT / 'art/cartoon/low-tide-v1/integration-v1/windows-feature-v1/native-binding.json'
native = read(feature)
for group in ('runtime_source_sha256', 'capture_helper_sha256'):
    assert all(sha(ROOT / p) == digest for p, digest in native[group].items()), group
for group in ('accepted_native_evidence', 'accepted_native_readback'):
    assert sha(ROOT / native[group]['path']) == native[group]['sha256'], group
attempt_stability = {}
for folder in (first, second):
    launch = read(folder / 'running.json')
    changed = [p for p, digest in launch['protected_sha256'].items() if sha(ROOT / p) != digest]
    assert not changed, changed
    attempt_stability[folder.name] = {'protected_file_count': len(launch['protected_sha256']),
                                     'all_current_bytes_match_launch': True}

copies = []
for tag, folder in (('attempt-v1', first), ('attempt-v2', second)):
    for name in ('running.json', 'adaptation.json', 'gate-adaptation.diff', 'gate-retained.ps1', 'gate.log', 'result.json'):
        path = folder / name
        if not path.exists():
            continue
        target = OUT / tag / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(path, target)
        assert sha(target) == sha(path)
        copies.append({'path': target.relative_to(OUT).as_posix(),
                       'source': path.relative_to(ROOT).as_posix(), 'sha256': sha(target)})
for path, name in ((observer, 'retry-observer.json'),
                   (ROOT / 'build/seasonal-post-merge/observe_gate_retry.py', 'retry-observer.py')):
    target = OUT / name
    if not target.exists():
        shutil.copyfile(path, target)
    assert sha(path) == sha(target)
    copies.append({'path': name, 'source': path.relative_to(ROOT).as_posix(), 'sha256': sha(target)})

save('attempt-v1/failure.json', {
    'status': 'INCOMPLETE', 'reported_exception': 'AssertionError: gate-child-became-foreground',
    'exception_source': 'Launcher stderr returned by local exec session 66452, chunk 80d26b',
    'location': 'run_gate.py:136', 'full_gate_pass': False,
    'completed_scope': 'Clean build, smoke groups and native wave/palm regression; stopped during approval-history regression.',
    'cause': 'Unresolved: original launcher retained neither failing foreground PID nor creation time.',
    'no_result_json': not (first / 'result.json').exists()})

reviewed = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'platform').iterdir()) if p.is_file()]
reviewed += ['src/engine/jc_reborn.c', 'src/engine/events.c', 'src/engine/sound.c', 'src/engine/utils.c',
             'src/engine/graphics.c', 'src/engine/island.c', 'src/engine/art_style.c', 'index.html',
             'tools/build_web.py', 'scripts/build_web.ps1', 'scripts/build_web_local.ps1',
             'CMakeLists.txt', 'cmake/RuntimeData.cmake', '.github/workflows/ci.yml', 'tests/platform-cleanup.md']
delta = command('diff', '9b0a4ed1fb5920faf426c4d3aa89e45afadebf07', HEAD, '--', *reviewed)
assert not delta
save('source-bindings.json', {'reviewed_commit': HEAD, 'working_tree_sha256': {p: sha(ROOT / p) for p in reviewed},
    'git_blob_ids': {p: command('rev-parse', HEAD + ':' + p) for p in reviewed},
    'comparison_commit': '9b0a4ed1fb5920faf426c4d3aa89e45afadebf07', 'reviewed_paths_git_diff_empty': True,
    'scope': 'All platform files and named entry/Web/build files; graphics/island/art_style integration regions only.'})
save('native-binding.json', {'status': 'PASS', 'main_commit': HEAD, 'archive_sha256': SHA,
    'deployed_archive_sha256': sha(deployed), 'feature_binding': {'path': feature.relative_to(ROOT).as_posix(), 'sha256': sha(feature)},
    'runtime_source_count': len(native['runtime_source_sha256']), 'capture_helper_count': len(native['capture_helper_sha256']),
    'all_bound_runtime_helpers_exact': True, 'accepted_native_evidence': native['accepted_native_evidence'],
    'accepted_native_readback': native['accepted_native_readback'],
    'scope': 'Identity readback only; the accepted native scene captures were not rerun.'})

launcher = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py'
helper = ROOT / 'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py'
cache = ROOT / 'build/CMakeCache.txt'
fields = dict(re.findall(r'^([A-Z_]+):[^=\r\n]+=([^\r\n]*)$', cache.read_text(), re.M))
dependencies = {str(p): sha(p) for p in (Path(sys.executable), launcher, helper, cache)}
if 'CMAKE_C_COMPILER' not in fields:
    compiler_records = list((ROOT / 'build/CMakeFiles').glob('*/CMakeCCompiler.cmake'))
    assert len(compiler_records) == 1, compiler_records
    compiler_record = compiler_records[0]
    fields['CMAKE_C_COMPILER'] = re.search(r'set\(CMAKE_C_COMPILER "([^"]+)"\)', compiler_record.read_text())[1]
    dependencies[str(compiler_record)] = sha(compiler_record)
for key in ('CMAKE_COMMAND', 'CMAKE_C_COMPILER'):
    path = Path(fields[key])
    dependencies[str(path)] = sha(path)
log = (second / 'gate.log').read_text(encoding='utf-8', errors='replace')
capture_rows = result['retained_captures'] if result else []
save('verification.json', {'status': 'PASS' if result and result['passed'] else 'LOCAL_GATE_INCOMPLETE',
    'main_commit': HEAD, 'attempt_count': 2, 'first_attempt_incomplete': True,
    'retry_observer_status': observed['status'], 'gate_result': result is not None and result['passed'],
    'exit_code': result['exit_code'] if result else None,
    'elapsed_seconds': result['elapsed_seconds'] if result else None,
    'poll_checks': result['poll_checks'] if result else None,
    'private_window_count': len(result['observed_inactive_windows']) if result else None,
    'input_desktop_preserved': result['input_desktop_preserved'] if result else None,
    'protected_snapshot_readback': attempt_stability, 'source_and_deployed_zip_sha256': SHA,
    'retained_complete_ppms': sum(row['complete_ppm'] for row in capture_rows),
    'retained_capture_markers': sum(row['capture_marker'] for row in capture_rows),
    'clean_build_marker': 'OK   build clean, no warnings' in log,
    'explicit_symlink_skips': [line for line in log.splitlines() if '... skipped' in line],
    'dependencies_sha256': dependencies,
    'cmake_cache_fields': {k: fields.get(k) for k in ('CMAKE_COMMAND', 'CMAKE_C_COMPILER', 'CMAKE_GENERATOR', 'CMAKE_HOME_DIRECTORY')},
    'built_outputs_sha256': {n: sha(ROOT / 'build/Release' / n) for n in ('jc_reborn.exe', 'jc_reborn.scr')},
    'main_ci_reference': '../main-ci.json',
    'excluded_bulk': 'PPMs, renderer logs, executables and archives remain in scratch; result.json binds retained capture/log hashes.'})

manifest = {p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
save('evidence.json', {'schema_version': 1, 'main_commit': HEAD, 'files_sha256': manifest, 'exact_copies': copies})
assert all(sha(OUT / name) == digest for name, digest in manifest.items())
assert all(sha(OUT / row['path']) == sha(ROOT / row['source']) == row['sha256'] for row in copies)
save('readback.json', {'status': 'PASS', 'evidence_sha256': sha(OUT / 'evidence.json'),
    'manifest_files': len(manifest), 'exact_copies': len(copies),
    'manifest_bytes': sum((OUT / name).stat().st_size for name in manifest),
    'scope': 'Every manifest member and every retained copy was reread byte-for-byte.'})
print(json.dumps({'verification': read(OUT / 'verification.json')['status'],
                  'evidence_sha256': sha(OUT / 'evidence.json'), 'readback_sha256': sha(OUT / 'readback.json')}, indent=2))
