"""Windows integration of actual application CMake wiring and stale-data gate.

Builds an isolated source copy. Only `version` and a gate that refuses before
smoke are launched; no graphical engine process or production ZIP mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, source, log, check=True):
    env = dict(os.environ)
    for key in list(env):
        if key.lower() == 'psmodulepath':
            del env[key]
    result = subprocess.run([str(a) for a in args], cwd=source, env=env, capture_output=True, timeout=300)
    text = (result.stdout + result.stderr).decode('utf-8', 'replace')
    log.write_text(text, encoding='utf-8')
    if check:
        assert result.returncode == 0, f'tests/test_runtime_data_project.py: command failed; {log}: {text[-2000:]}'
    return result.returncode, text


def assert_fresh(archive, deployed):
    assert deployed.exists() and sha(archive) == sha(deployed), f'CMakeLists.txt: explicit jc_reborn target left stale {deployed}'


def verify(work, mutations):
    protected = sha(ROOT / 'assets/scrantic_data.zip')
    source = work / 'source'; source.mkdir()
    for directory in ('cmake', 'src', 'platform', 'third_party', 'vs', 'tests', 'tools'):
        shutil.copytree(ROOT / directory, source / directory)
    for name in ('CMakeLists.txt', 'gate.ps1'):
        shutil.copyfile(ROOT / name, source / name)
    (source / 'assets').mkdir()
    archive = source / 'assets/scrantic_data.zip'
    shutil.copyfile(ROOT / 'assets/scrantic_data.zip', archive)
    build = source / 'build'
    configure = ['cmake', '-S', source, '-B', build, '-A', 'x64']
    compile_command = ['cmake', '--build', build, '--config', 'Release', '--target', 'jc_reborn']
    run(configure, source, work / 'configure.log')
    run(compile_command, source, work / 'build.log')
    exe = build / 'Release/jc_reborn.exe'; deployed = exe.parent / 'scrantic_data.zip'
    _, version = run([exe, 'version'], source, work / 'execution.log')
    assert re.search(r'\b\d+\.\d+\.\d+\b', version), 'CMakeLists.txt: application version witness did not execute'
    binary_identity = (sha(exe), exe.stat().st_mtime_ns)
    def change(label):
        with zipfile.ZipFile(archive, 'a') as z:
            z.writestr(f'tests/runtime-data-{label}.txt', label)
    change('control')
    # A real stale deployed ZIP must be rejected by both supported shells.
    gate_results = []
    for shell in ('powershell.exe', 'pwsh'):
        code, text = run([shell, '-NoProfile', '-File', source / 'gate.ps1', '-NoBuild', '-SmokeOnly'], source, work / f'gate-{shell}.log', check=False)
        failures = [line for line in text.splitlines() if line.startswith('FAIL ')]
        prefix = 'FAIL runtime archive differs from assets/scrantic_data.zip: '
        same_archive = (len(failures) == 1 and failures[0].startswith(prefix)
                        and Path(failures[0][len(prefix):]).samefile(deployed))
        assert code != 0 and same_archive and '=== smoke ===' not in text, f'gate.ps1: {shell} did not reject exactly one stale {deployed} before smoke; status={code}; log={work / f"gate-{shell}.log"}; actual output:\n{text}'
        gate_results.append({'shell': shell, 'failure': failures[0], 'smoke_reached': False})
        print(f'FIRED 1/1 gate.ps1 ({shell}): stale {deployed} refused before smoke', flush=True)
    run(compile_command, source, work / 'refresh.log')
    assert_fresh(archive, deployed)
    assert (sha(exe), exe.stat().st_mtime_ns) == binary_identity, 'CMakeLists.txt: artwork-only refresh relinked application'
    print('PASS CMakeLists.txt: real application explicit-target art refresh; binary unchanged', flush=True)
    record = None
    if mutations:
        cmake = source / 'CMakeLists.txt'; original = cmake.read_text(encoding='utf-8')
        needle = '    jc_add_runtime_data("${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip" ${JC_RUNTIME_TARGETS})'
        assert original.count(needle) == 1, 'CMakeLists.txt: expected one runtime-data integration call'
        project_file = build / 'jc_reborn.vcxproj'
        before_time = project_file.stat().st_mtime_ns
        cmake.write_text(original.replace(needle, '    # Runtime-data integration disabled by mutation'), encoding='utf-8')
        run(configure, source, work / 'mutant-configure.log')
        assert project_file.stat().st_mtime_ns > before_time, 'CMakeLists.txt: mutation did not regenerate actual application project'
        change('mutant')
        run(compile_command, source, work / 'mutant-build.log')
        _, executed = run([exe, 'version'], source, work / 'mutant-execution.log')
        assert executed == version, 'CMakeLists.txt: mutant application execution witness differs'
        try:
            assert_fresh(archive, deployed)
        except AssertionError as exc:
            expected = f'CMakeLists.txt: explicit jc_reborn target left stale {deployed}'
            assert str(exc) == expected, f'Wrong integration mutation failure: {exc}'
            record = {'result': 'FIRED', 'failure': str(exc), 'cmake_sha256': sha(cmake),
                      'generated_project_timestamp_advanced': True, 'application_executed': executed.strip()}
            print(f'FIRED 1/1 {exc}', flush=True)
        else:
            raise AssertionError('CMakeLists.txt: disabled archive wiring survived')
        cmake.write_text(original, encoding='utf-8')
        run(configure, source, work / 'restored-configure.log')
        run(compile_command, source, work / 'restored-build.log')
        assert_fresh(archive, deployed)
    assert sha(ROOT / 'assets/scrantic_data.zip') == protected, 'Production archive changed'
    (work / 'report.json').write_text(json.dumps({'status': 'PASS', 'gate_mutations': gate_results,
        'wiring_mutation': record, 'production_archive_sha256': protected, 'application_sha256': sha(exe)}, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path); parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    if os.name != 'nt':
        print('FAIL tests/test_runtime_data_project.py: requires the Windows application and PowerShell gate')
        return 1
    try:
        if args.work:
            work = args.work.resolve(); work.mkdir(parents=True, exist_ok=False); verify(work.resolve(strict=True), args.mutations)
        else:
            base = ROOT / 'build/cleanup-fixtures'; base.mkdir(parents=True, exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix='runtime-project-', dir=base)).resolve(strict=True)
            print(f'Fixture logs retained: {work}', flush=True)
            verify(work, args.mutations)
        return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}'); return 1


if __name__ == '__main__': raise SystemExit(main())
