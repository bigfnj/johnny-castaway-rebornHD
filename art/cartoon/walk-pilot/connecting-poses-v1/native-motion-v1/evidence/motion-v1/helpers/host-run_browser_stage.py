"""Retain one executed browser-pipeline command and its exact output."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
label, helper, *arguments = sys.argv[1:]
assert label in ('build', 'validation', 'negatives', 'publication', 'preservation')
source = root / helper
assert source.parent == root / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
destination = root / 'build/connecting-poses/native-motion-v1/browser-execution' / label
destination.mkdir(parents=True, exist_ok=False)
command = [sys.executable, '-B', helper, *arguments]
started = time.time()
with (destination / 'stdout.txt').open('w', encoding='utf-8', newline='\n') as output:
    result = subprocess.run(command, cwd=root, stdout=output, stderr=subprocess.PIPE, text=True, timeout=900)
(destination / 'stderr.txt').write_text(result.stderr, encoding='utf-8', newline='\n')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
record = {'status': 'PASS' if result.returncode == 0 else 'FAIL',
          'command': ['${PYTHON}', '-B', helper, *arguments],
          'returncode': result.returncode, 'elapsed_seconds': time.time() - started,
          'executed_helper_sha256': sha(source),
          'runner_sha256': sha(Path(__file__)),
          'outputs_sha256': {p.name: sha(p) for p in destination.iterdir() if p.is_file()}}
(destination / 'execution.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
print((destination / 'stdout.txt').read_text(), end='')
print(result.stderr, end='', file=sys.stderr)
print(json.dumps(record))
sys.exit(result.returncode)
