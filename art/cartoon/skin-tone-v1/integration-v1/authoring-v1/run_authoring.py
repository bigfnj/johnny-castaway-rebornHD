"""Run maintained authoring smoke suites before their regressions and checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/connecting-poses/authoring-v1'
OUT.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
inputs = ['assets/scrantic_data.zip', 'art/cartoon/pack.json',
          'art/cartoon/skin-tone-v1/production-acceptance.json',
          'docs/art-style-learnings.md']
inputs += [f'docs/knowledge-base/{name}.{ext}' for name in
           ('cartoon-art-metadata', 'cartoon-production-catalog') for ext in ('json', 'md')]
inputs += [p.relative_to(ROOT).as_posix() for folder in ('tools', 'tests')
           for p in sorted((ROOT / folder).glob('*.py'))]
before = {name: sha(ROOT / name) for name in inputs}
commands = [
    ('inventory-smoke', ['tests/test_art_inventory.py', '--smoke']),
    ('history-smoke', ['tests/test_art_pilot_history.py', '--phase', 'smoke']),
    ('metadata-smoke', ['tests/test_art_review_metadata.py', '--phase', 'smoke']),
    ('catalog-smoke', ['tests/test_art_production_catalog.py', '--phase', 'smoke']),
    ('inventory-regression', ['tests/test_art_inventory.py']),
    ('history-regression', ['tests/test_art_pilot_history.py', '--phase', 'regression']),
    ('metadata-regression', ['tests/test_art_review_metadata.py', '--phase', 'regression']),
    ('catalog-regression', ['tests/test_art_production_catalog.py', '--phase', 'regression']),
    ('art-tools-regression', ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_art_tools.py', '-v']),
    ('metadata-reproduction', ['tools/art_review_metadata.py', '--check']),
    ('catalog-reproduction', ['tools/art_production_catalog.py', '--check']),
]
report = {'scope': 'Unmodified maintained suites; all smoke stages before regressions; checks do not reread external originals.',
          'python': sys.version, 'inputs': before, 'runs': [], 'passed': False}
for label, args in commands:
    start = time.monotonic()
    command = [sys.executable, '-B', *args]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log = OUT / f'{label}.log'
    log.write_bytes(result.stdout)
    row = {'label': label, 'command': command, 'exit_code': result.returncode,
           'elapsed_seconds': round(time.monotonic() - start, 3),
           'log': log.name, 'sha256': sha(log)}
    report['runs'].append(row)
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'{label}: exit {result.returncode}, {row["elapsed_seconds"]}s', flush=True)
    if result.returncode:
        print(result.stdout.decode('utf-8', errors='replace'), flush=True)
        raise SystemExit(result.returncode)
after = {name: sha(ROOT / name) for name in inputs}
report['changed_inputs'] = [name for name in before if before[name] != after[name]]
report['passed'] = not report['changed_inputs'] and len(report['runs']) == len(commands)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
if not report['passed']:
    raise SystemExit('authoring inputs changed during verification')
print('PASS maintained authoring checks with unchanged inputs', flush=True)
