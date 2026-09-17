"""Invoke the frozen gate launcher unchanged; retain exception context only."""
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time
import traceback

import psutil

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py'
OUTPUT = ROOT / 'build/seasonal-final-windows/low-tide-main-v2-observer.json'
ARGS = ['--root', str(ROOT), '--zip-sha256',
        'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66',
        '--label', 'low-tide-main-v2']


def identity(pid):
    try:
        process = psutil.Process(pid)
        return {'pid': pid, 'name': process.name(), 'created_epoch': process.create_time(),
                'parent_pid': process.ppid()}
    except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
        return {'pid': pid, 'unavailable': type(exc).__name__}


if OUTPUT.exists():
    raise SystemExit('Existing observer evidence preserved')
record = {'schema_version': 1, 'started_epoch': time.time(), 'argv': [str(LAUNCHER)] + ARGS,
          'launcher_sha256': hashlib.sha256(LAUNCHER.read_bytes()).hexdigest(),
          'observer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'policy': 'Exact frozen launcher executed with runpy. No hooks, guard changes or source edits.'}
sys.argv = record['argv']
try:
    runpy.run_path(str(LAUNCHER), run_name='__main__')
except BaseException as exc:
    record.update(status='FAILED', exception=repr(exc), traceback=traceback.format_exc())
    node = exc.__traceback__
    while node:
        frame = node.tb_frame
        if Path(frame.f_code.co_filename) == LAUNCHER and frame.f_code.co_name == 'main':
            values = frame.f_locals
            owner = values.get('owner')
            failed_pid = owner.value if owner is not None else None
            record['launcher_context'] = {
                'line': node.tb_lineno, 'checks': values.get('checks'),
                'foreground_pid_at_guard': failed_pid,
                'foreground_process_after_cleanup': identity(failed_pid) if failed_pid else None,
                'historical_seen_pids': sorted(values.get('seen', [])),
                'last_current_children': [identity(p.pid) for p in values.get('children', [])],
                'observed_inactive_windows': values.get('windows'),
                'gate_started_epoch': values.get('started'),
            }
        node = node.tb_next
    raise
else:
    record['status'] = 'COMPLETED'
finally:
    record['finished_epoch'] = time.time()
    OUTPUT.write_bytes((json.dumps(record, indent=2) + '\n').encode('utf-8'))
