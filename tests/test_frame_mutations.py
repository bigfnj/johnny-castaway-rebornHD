"""Build isolated frame-limit variants and require one named executed failure."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    root, work = args.source.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    source = work / 'source'
    source.mkdir()
    shutil.copyfile(root / 'CMakeLists.txt', source / 'CMakeLists.txt')
    for folder in ['src', 'platform', 'third_party', 'vs', 'tests', 'cmake', 'assets', 'tools']:
        shutil.copytree(root / folder, source / folder,
                        ignore=shutil.ignore_patterns('build', '__pycache__', '.vs'))
    builddir = work / 'build'
    bindir = builddir / 'Release' if os.name == 'nt' else builddir
    suffix = '.exe' if os.name == 'nt' else ''
    exe, probe = bindir / ('jc_reborn' + suffix), bindir / ('jc_frame_test' + suffix)

    def command(argv, label):
        run = subprocess.run(argv, capture_output=True, text=True, timeout=240)
        output = run.stdout + run.stderr
        (work / (label + '.log')).write_text(output, encoding='utf-8')
        assert run.returncode == 0, output

    command(['cmake', '-S', str(source), '-B', str(builddir), '-DCMAKE_BUILD_TYPE=Release'], 'configure')
    buildcmd = ['cmake', '--build', str(builddir), '--config', 'Release',
                '--target', 'jc_reborn', 'jc_frame_test', '--parallel', '4']
    command(buildcmd, 'baseline-build')
    testcmd = [sys.executable, '-B', str(source / 'tests/test_frame_limits.py'),
               '--exe', str(exe), '--probe', str(probe)]
    command(testcmd + ['--phase', 'smoke'], 'baseline-smoke')
    command(testcmd + ['--phase', 'regression'], 'baseline-regression')
    variants = [
        ('range-check', 'src/engine/jc_reborn.c', 'cli-invalid-4294967296', exe,
         '(unsigned long long)v > UINT32_MAX', '0', 'WITNESS frame CLI process'),
        ('counter-wrap', 'src/engine/events.c', 'tick-maximum', probe,
         'if (evFrameCount >= evMaxFrames) {', 'if (evFrameCount > evMaxFrames) {',
         'WITNESS events.c frame maximum BEGIN'),
        ('early-stop', 'src/engine/events.c', 'tick-ordinary', probe,
         'if (evFrameCount >= evMaxFrames) {', 'if (evFrameCount + 1 >= evMaxFrames) {',
         'WITNESS events.c frame ordinary BEGIN'),
    ]
    records = []
    for label, filename, case, artifact, old, new, witness in variants:
        path = source / filename
        original = path.read_bytes()
        contents = path.read_text()
        assert contents.count(old) == 1, (filename, old)
        try:
            before = artifact.stat().st_mtime_ns
            path.write_text(contents.replace(old, new))
            command(buildcmd, label + '-build')
            after = artifact.stat().st_mtime_ns
            assert after > before, f'{filename}: artifact not rebuilt'
            result = subprocess.run(testcmd + ['--only', case], capture_output=True,
                                    text=True, timeout=20)
            output = result.stdout + result.stderr
            (work / (label + '-test.log')).write_text(output, encoding='utf-8')
            failures = [line for line in output.splitlines() if line.startswith('FAIL ')]
            assert result.returncode == 1 and len(failures) == 1, output
            assert failures[0].startswith(f'FAIL tests/test_frame_limits.py:{case}:'), output
            assert f'WITNESS frame assertion {case} BEGIN' in output and witness in output, output
            records.append({'mutation': label, 'file': filename, 'case': case, 'result': 'FIRED',
                            'artifact_before_ns': before, 'artifact_after_ns': after,
                            'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                            'runtime_witness': witness, 'failure': failures[0]})
            print(f'FIRED {filename}: {label}, rebuilt and executed with one named failure', flush=True)
        finally:
            path.write_bytes(original)
            command(buildcmd, label + '-restored-build')
            command(testcmd + ['--only', case], label + '-restored-test')
    (work / 'report.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    print(f'Frame mutations: {len(records)}/{len(variants)} FIRED; source restored and rebuilt')


if __name__ == '__main__':
    main()
