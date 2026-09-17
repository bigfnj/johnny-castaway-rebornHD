import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'build/clouds-v1/review-v1'
bad = ROOT / 'build/clouds-v1/preservation-negative-input-v2'
bad.mkdir()
for name in ('build.json', 'manifest.json', 'review.html'):
    shutil.copyfile(source / name, bad / name)
with (bad / 'review.html').open('ab') as handle:
    handle.write(b'\n<!-- Valid HTML alteration for identity refusal. -->\n')
helper = ROOT / 'art/cartoon/clouds-v1/native-v1/preserve.py'
command = [sys.executable, '-B', str(helper), '--run', str(ROOT / 'build/clouds-v1/native-v1/review-v1'), '--review', str(bad)]
run = subprocess.run(command, capture_output=True, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
expected = 'ValueError: cloud preservation: review.html identity'
assert run.returncode != 0 and run.stderr.strip().splitlines()[-1] == expected, run.stderr
assert not (helper.parent / 'evidence-v1').exists()
record = {'status': 'PASS', 'control': 'altered_valid_review_html', 'failure': expected,
          'command': command, 'returncode': run.returncode, 'stderr': run.stderr,
          'helper_sha256': hashlib.sha256(helper.read_bytes()).hexdigest(),
          'harness_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'restored_positive': 'Use the unchanged original review folder for the final preservation; its result is readback.json.',
          'historical_review_unchanged': hashlib.sha256((source / 'review.html').read_bytes()).hexdigest() == json.loads((source / 'build.json').read_bytes())['html_sha256']}
assert record['historical_review_unchanged']
(ROOT / 'build/clouds-v1/preservation-control.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
print('PASS altered valid HTML refused before evidence writes: review.html identity')
