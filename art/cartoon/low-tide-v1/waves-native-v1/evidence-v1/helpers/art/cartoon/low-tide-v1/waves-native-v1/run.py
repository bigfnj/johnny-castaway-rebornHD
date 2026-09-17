"""No-window Docker launcher for fresh low-wave evidence folders."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
IMAGE = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'


def source_path(path):
    return '/source/' + path.resolve().relative_to(ROOT).as_posix()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, default=ROOT / 'build/low-tide-v1/static-candidate-v2.zip')
    p.add_argument('--candidate', type=Path)
    p.add_argument('--candidate-sha256')
    p.add_argument('--baseline-captures', type=Path)
    p.add_argument('--group', choices=('initial', 'extended', 'all'), default='initial')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    output = a.output.resolve()
    allowed = (ROOT / 'build/low-tide-v1/waves-native-v1').resolve()
    output.relative_to(allowed)
    if output == allowed or output.exists():
        raise ValueError('fresh named scratch child required')
    output.mkdir(parents=True)
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    command = ['docker', 'run', '--init', '--rm', '--name', 'johnny-low-waves-' + uuid.uuid4().hex[:12], '--network', 'none',
        '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
        '--mount', 'type=bind,source=' + str(output) + ',target=/out', IMAGE,
        'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B', source_path(HERE / 'capture.py'),
        '--baseline', source_path(a.baseline), '--group', a.group, '--output', '/out/captures']
    if a.candidate:
        if not a.candidate_sha256 or not a.baseline_captures:
            raise ValueError('candidate requires explicit SHA and baseline captures')
        command += ['--candidate', source_path(a.candidate), '--candidate-sha256', a.candidate_sha256,
                    '--baseline-captures', source_path(a.baseline_captures)]
    container = command[5]
    result = None
    started = time.time()
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=flags).strip()
    try:
        with (output / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=1200, creationflags=flags)
    finally:
        subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=30, creationflags=flags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + container + '$', '--format', '{{.ID}}'], capture_output=True, timeout=15, creationflags=flags)
        record = {'source_commit': commit, 'command': command, 'image_id': IMAGE,
            'exit_code': result.returncode if result else None, 'elapsed_seconds': time.time() - started,
            'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
            'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (output / 'launch.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    if result is None or result.returncode or not record['no_surviving_task_container']:
        raise RuntimeError('native run failed; see launch.log')
    print('PASS ' + str(output / 'captures/summary.json'))


if __name__ == '__main__':
    main()
