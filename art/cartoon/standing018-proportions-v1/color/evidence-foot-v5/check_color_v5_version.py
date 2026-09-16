"""Exercise the new adapter's source pin with the valid historical v2 export."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
base = Path('art/cartoon/standing018-proportions-v1/color')
output = Path('build/standing018-proportions/color-checks-foot-v5')
adapter = base / 'correct018_foot_v5.py'
annotation = base / 'reference-foot-v5.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
args = ['-B', adapter.as_posix(), '--runtime', 'build/standing018-proportions/stage-v2/runtime',
        '--annotations', annotation.as_posix(), '--annotations-sha256', sha((ROOT / annotation).read_bytes()),
        '--output', (output / 'rejected-v2-runtime').as_posix()]
completed = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
witness = 'WITNESS correct018.py SHA256=' + sha((ROOT / adapter).read_bytes())
assert completed.returncode == 1 and completed.stderr.strip() == 'FAIL 018: runtime source identity'
assert completed.stdout.strip() == witness
assert not (ROOT / output / 'rejected-v2-runtime').exists()
record = {'case': 'valid-historical-v2-runtime-refused-by-v5-source-pin', 'result': 'FIRED',
          'command': ['python', *args], 'returncode': completed.returncode,
          'stdout': completed.stdout, 'stderr': completed.stderr,
          'adapter_sha256': sha((ROOT / adapter).read_bytes()),
          'test_source_sha256': sha(Path(__file__).read_bytes()),
          'scope': 'Executed source-version refusal only; no new guard or removal mutation. The adapter changes the source constant and preview scope, while existing guard logic is unchanged.'}
path = ROOT / output / 'source-version-control.json'
assert not path.exists()
path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(record))
