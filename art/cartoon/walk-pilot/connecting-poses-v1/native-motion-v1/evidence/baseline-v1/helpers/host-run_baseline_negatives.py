"""Retain one pinned Docker execution log without a shell pipeline."""
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
out = root / 'build/connecting-poses/native-motion-v1'
assert (out / 'baseline-v1/summary.json').is_file(), 'baseline completed first'
command = ['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={root.as_posix()},target=/source,readonly','--mount',f'type=bind,source={out.as_posix()},target=/out',
           'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72','python3','-B','/source/art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/negative_baseline.py']
started = time.time_ns()
run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
destination = out / 'negative-controls/baseline'
destination.mkdir(parents=True, exist_ok=True)
(destination / 'execution.log').write_bytes(run.stdout)
(destination / 'execution.json').write_text(json.dumps({'command': command, 'started_ns':started, 'finished_ns':time.time_ns(), 'exit_code':run.returncode}, indent=2)+'\n', encoding='utf-8')
sys.stdout.buffer.write(run.stdout)
sys.exit(run.returncode)
