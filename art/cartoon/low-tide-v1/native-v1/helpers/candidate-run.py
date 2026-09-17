"""Launch only after an explicit selected candidate SHA has been supplied."""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=ROOT / 'build/low-tide-v1/static-candidate-v1.zip')
    parser.add_argument('--candidate-sha256', required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    relative = candidate.relative_to(ROOT).as_posix()
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != args.candidate_sha256:
        raise ValueError('explicit candidate SHA256 mismatch')
    if (HERE / 'captures-v1').exists() or (HERE / 'launch.json').exists():
        raise ValueError('refusing existing candidate output')
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=flags).strip()
    name = 'johnny-low-tide-candidate-' + uuid.uuid4().hex[:12]
    command = ['docker', 'run', '--init', '--rm', '--name', name, '--network', 'none',
        '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
        '--mount', 'type=bind,source=' + str(HERE) + ',target=/out', IMAGE,
        'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B',
        '/source/' + (HERE / 'capture.py').relative_to(ROOT).as_posix(),
        '--candidate', '/source/' + relative, '--candidate-sha256', args.candidate_sha256]
    result = None
    started = time.time()
    try:
        with (HERE / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=600, creationflags=flags)
    finally:
        cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30, creationflags=flags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}'],
                                   capture_output=True, timeout=15, creationflags=flags)
        record = {'source_commit': commit, 'candidate_sha256': args.candidate_sha256, 'image_id': IMAGE,
            'command': command, 'exit_code': result.returncode if result else None,
            'elapsed_seconds': time.time() - started,
            'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
            'cleanup_exit_code': cleanup.returncode,
            'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (HERE / 'launch.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    if result is None or result.returncode or not record['no_surviving_task_container']:
        raise RuntimeError('candidate failed; inspect retained launch.log')
    print('PASS low-tide candidate: ' + str(HERE / 'captures-v1/summary.json'))


if __name__ == '__main__':
    main()
