"""Run only this task's Linux/Xvfb container; retain logs and always remove it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
IMAGE = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'assets/scrantic_data.zip')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--diagnostics', action='store_true')
    args = parser.parse_args()
    archive, output = args.archive.resolve(), args.output.resolve()
    relative_archive = archive.relative_to(ROOT).as_posix()
    output.relative_to(ROOT / 'build/seasonal-v1')
    if output.exists():
        raise ValueError('refusing existing capture output: ' + str(output))
    output.mkdir(parents=True)
    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    name = 'johnny-seasonal-' + uuid.uuid4().hex[:12]
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    command = ['docker', 'run', '--init', '--rm', '--name', name, '--network', 'none',
               '--mount', 'type=bind,source=' + str(ROOT) + ',target=/source,readonly',
               '--mount', 'type=bind,source=' + str(output) + ',target=/out', IMAGE,
               'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B',
               '/source/art/cartoon/seasonal-v1/native/capture.py', '--archive', '/source/' + relative_archive,
               '--archive-sha256', digest, '--output', '/out/captures']
    if args.diagnostics:
        command.append('--diagnostics')
    started = time.time()
    result = None
    cleanup = None
    try:
        with (output / 'launch.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=420, creationflags=creationflags)
    finally:
        # The unique name belongs solely to this run. Never select other containers.
        cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30, creationflags=creationflags)
        remaining = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}'], capture_output=True, timeout=15, creationflags=creationflags)
        record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, creationflags=creationflags).strip(),
                  'container_name': name, 'image_id': IMAGE, 'archive': relative_archive, 'archive_sha256': digest,
                  'output': output.relative_to(ROOT).as_posix(), 'capture_arguments': command[command.index('xvfb-run'):],
                  'exit_code': result.returncode if result else None, 'elapsed_seconds': time.time() - started,
                  'no_surviving_task_container': remaining.returncode == 0 and not remaining.stdout.strip(),
                  'cleanup_exit_code': cleanup.returncode, 'launch_helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (output / 'launch.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    if result is None or result.returncode != 0 or not record['no_surviving_task_container']:
        raise RuntimeError('seasonal capture failed; retained ' + str(output / 'launch.log'))
    print('PASS headless seasonal capture; task container absent: ' + str(output / 'captures/summary.json'))


if __name__ == '__main__':
    main()
