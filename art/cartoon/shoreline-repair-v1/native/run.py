"""Headless, isolated Docker/Xvfb runner for the bounded shoreline preview."""
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
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--phase-probe', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.phase_probe and not args.candidate:
        parser.error('candidate required unless phase-probe is explicit')
    output = args.output.resolve()
    output.relative_to(ROOT / 'build/shoreline-repair-v1')
    if output.exists():
        raise ValueError('refusing existing capture output: ' + str(output))
    sources = {'baseline': args.baseline.resolve()}
    if args.candidate:
        sources['candidate'] = args.candidate.resolve()
    identities = {name: {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in sources.items()}
    output.mkdir(parents=True)
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    name = 'johnny-shore-' + uuid.uuid4().hex[:12]
    command = ['docker', 'run', '--init', '--rm', '--name', name, '--network', 'none',
        '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
        '--mount', 'type=bind,source=' + str(output) + ',target=/out', IMAGE,
        'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B',
        '/source/art/cartoon/shoreline-repair-v1/native/capture.py', '--output', '/out/captures']
    for key, value in identities.items():
        command += ['--' + key, '/source/' + value['path'], '--' + key + '-sha256', value['sha256']]
    if args.phase_probe:
        command.append('--phase-probe')
    started, result = time.time(), None
    try:
        with (output / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=300, creationflags=flags)
    finally:
        cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30, creationflags=flags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}'], capture_output=True, timeout=15, creationflags=flags)
        record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=flags).strip(),
            'container_name': name, 'image_id': IMAGE, 'inputs': identities,
            'output': output.relative_to(ROOT).as_posix(), 'capture_arguments': command[command.index('xvfb-run'):],
            'exit_code': result.returncode if result else None, 'elapsed_seconds': time.time() - started,
            'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
            'cleanup_exit_code': cleanup.returncode, 'launch_helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (output / 'launch.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    if result is None or result.returncode != 0 or not record['no_surviving_task_container']:
        raise RuntimeError('shoreline capture failed; retained ' + str(output / 'launch.log'))
    print('PASS headless shoreline capture: ' + str(output / 'captures'))


if __name__ == '__main__':
    main()
