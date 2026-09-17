"""Isolated Docker/Xvfb launch for the second bounded shoreline preview."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
IMAGE = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(ROOT / 'build/shoreline-repair-v1')
    if output.exists():
        raise ValueError('refusing existing capture output: ' + str(output))
    inputs = {name: {'path': path.resolve().relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
              for name, path in (('baseline', args.baseline), ('candidate', args.candidate))}
    adapter_sha = hashlib.sha256((Path(__file__).parent / 'capture.py').read_bytes()).hexdigest()
    output.mkdir(parents=True)
    name = 'johnny-shore-v2-' + uuid.uuid4().hex[:12]
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    command = ['docker', 'run', '--init', '--rm', '--name', name, '--network', 'none',
        '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
        '--mount', 'type=bind,source=' + str(output) + ',target=/out', IMAGE,
        'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B',
        '/source/art/cartoon/shoreline-repair-v1/native-v2/capture.py', '--output', '/out/captures']
    for key, value in inputs.items():
        command += ['--' + key, '/source/' + value['path'], '--' + key + '-sha256', value['sha256']]
    result, started = None, time.time()
    try:
        with (output / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=300, creationflags=flags)
    finally:
        cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30, creationflags=flags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}'], capture_output=True, timeout=15, creationflags=flags)
        record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=flags).strip(),
            'container_name': name, 'image_id': IMAGE, 'inputs': inputs,
            'output': output.relative_to(ROOT).as_posix(), 'capture_arguments': command[command.index('xvfb-run'):],
            'exit_code': result.returncode if result else None, 'elapsed_seconds': time.time() - started,
            'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
            'cleanup_exit_code': cleanup.returncode, 'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'capture_adapter_sha256': adapter_sha}
        (output / 'launch.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    if result is None or result.returncode != 0 or not record['no_surviving_task_container']:
        raise RuntimeError('coherent-ground capture failed; retained ' + str(output / 'launch.log'))
    print('PASS isolated coherent-ground preview: ' + str(output / 'captures'))


if __name__ == '__main__':
    main()
