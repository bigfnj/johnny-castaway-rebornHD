"""Ordered fresh-main authoring checks; ignored evidence only."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = '9ea8293f8efbd45a25717b4f8dd3bc5139586259'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == COMMIT, 'exact merged commit'
    records = []
    cases = [
        ('smoke-inventory', ['tests/test_art_inventory.py', '--smoke']),
        ('smoke-history', ['tests/test_art_pilot_history.py', '--phase', 'smoke']),
        ('smoke-metadata', ['tests/test_art_review_metadata.py', '--phase', 'smoke']),
        ('smoke-production', ['tests/test_art_production_catalog.py', '--phase', 'smoke']),
        ('regression-inventory', ['tests/test_art_inventory.py']),
        ('regression-history', ['tests/test_art_pilot_history.py', '--phase', 'regression']),
        ('regression-metadata', ['tests/test_art_review_metadata.py', '--phase', 'regression']),
        ('regression-production', ['tests/test_art_production_catalog.py', '--phase', 'regression']),
        ('regression-pack-tools', ['tests/test_art_tools.py', '-v']),
        ('check-metadata', ['tools/art_review_metadata.py', '--check']),
        ('check-production', ['tools/art_production_catalog.py', '--check']),
    ]
    assert not (OUT/'checks.json').exists(), 'preserve prior check record'
    for label, args in cases:
        before = time.monotonic()
        command = [sys.executable, '-B', *args]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=300)
        logs = {}
        for stream in ('stdout', 'stderr'):
            data = getattr(result, stream).encode('utf-8')
            name = label+'.'+stream+'.txt'
            (OUT/name).write_bytes(data)
            logs[stream] = {'path': name, 'sha256': sha(data)}
        text = result.stdout+'\n'+result.stderr
        match = re.search(r'Ran (\d+) tests? in', text)
        record = {'order': len(records)+1, 'label': label, 'argv': ['python', '-B', *args],
                  'exit_code': result.returncode, 'elapsed_seconds': round(time.monotonic()-before, 3),
                  'tests_run': int(match[1]) if match else None,
                  'skip_lines': [line for line in text.splitlines() if 'skipped' in line.lower()],
                  'logs': logs}
        records.append(record)
        summary = {'commit': head, 'runner_sha256': sha(Path(__file__).read_bytes()),
                   'status': 'RUNNING' if result.returncode == 0 else 'FAIL', 'ordered_checks': records,
                   'scope': 'Fresh merged-main maintained authoring tests and catalog verification. No image generation or long raw-source replay. Existing mutation matrices are not repeated; built-in regression negative cases run normally.'}
        (OUT/'checks.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8', newline='\n')
        print(label, 'PASS' if result.returncode == 0 else 'FAIL', 'tests='+str(record['tests_run']), flush=True)
        if result.returncode:
            print(result.stderr[-3000:], flush=True)
            return 1
    summary['status'] = 'PASS'
    (OUT/'checks.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS all ordered authoring checks', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
