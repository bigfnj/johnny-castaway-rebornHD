"""Fresh cloud review in an existing network-isolated Docker/Xvfb image."""
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


def source(path):
    return '/source/' + path.resolve().relative_to(ROOT).as_posix()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, default=ROOT / 'assets/scrantic_data.zip')
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--candidate-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    output = a.output.resolve()
    allowed = (ROOT / 'build/clouds-v1/native-v1').resolve()
    output.relative_to(allowed)
    if output == allowed or output.exists():
        raise ValueError('fresh named scratch child required')
    baseline, candidate = source(a.baseline), source(a.candidate)
    if hashlib.sha256(a.candidate.read_bytes()).hexdigest() != a.candidate_sha256:
        raise ValueError('explicit candidate SHA256 mismatch')
    output.mkdir(parents=True)
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    container = 'johnny-clouds-' + uuid.uuid4().hex[:12]
    command = ['docker', 'run', '--init', '--rm', '--name', container, '--network', 'none',
        '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
        '--mount', 'type=bind,source=' + str(output) + ',target=/out', IMAGE,
        'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B', source(HERE / 'capture.py'),
        '--baseline', baseline, '--candidate', candidate, '--candidate-sha256', a.candidate_sha256,
        '--output', '/out/captures']
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=flags).strip()
    result, started = None, time.time()
    try:
        with (output / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=1200, creationflags=flags)
    finally:
        subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=30, creationflags=flags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + container + '$', '--format', '{{.ID}}'],
                                   capture_output=True, timeout=15, creationflags=flags)
        record = {'source_commit': commit, 'command': command, 'image_id': IMAGE,
            'exit_code': result.returncode if result else None, 'elapsed_seconds': time.time() - started,
            'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
            'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (output / 'launch.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    if result is None or result.returncode or not record['no_surviving_task_container']:
        raise RuntimeError('native cloud run failed; see launch.log')
    print('PASS ' + str(output / 'captures/summary.json'))


if __name__ == '__main__':
    main()
