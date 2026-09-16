"""Exercise byte preservation in fresh indexes without changing the real index."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
out = root / 'build/standing018-proportions/checkout-proof-v1'
assert not out.exists()
out.mkdir()
name = 'art/cartoon/standing018-proportions-v1/generation-request-v2.json'
source = (root / name).read_bytes()
attrs = (root / '.gitattributes').read_bytes()
line = b'art/cartoon/standing018-proportions-v1/** -text whitespace=cr-at-eol'
assert attrs.count(line) == 1
rows = []
for label, protection in [('protected', True), ('removed', False), ('restored', True)]:
    repo = out / label / 'repo'
    repo.mkdir(parents=True)
    destination = out / label / 'fresh'
    destination.mkdir()
    path = repo / name
    path.parent.mkdir(parents=True)
    path.write_bytes(source)
    actual_attrs = attrs if protection else attrs.replace(line, b'')
    (repo / '.gitattributes').write_bytes(actual_attrs)
    for args in [('init', '--quiet'), ('add', '--', '.gitattributes', name),
                 ('checkout-index', '--all', '--prefix=' + destination.as_posix() + '/')]:
        process = subprocess.run(['git', '-C', str(repo), '-c', 'core.autocrlf=true', *args], capture_output=True)
        assert process.returncode == 0, process.stderr.decode(errors='replace')
    materialized = (destination / name).read_bytes()
    same = materialized == source
    assert same == protection, (label, name, same)
    rows.append({'case': label, 'file': name, 'status': 'PASS' if same else 'FIRED',
                 'failure': None if same else name + ': byte identity changed',
                 'source_sha256': hashlib.sha256(source).hexdigest(),
                 'checkout_sha256': hashlib.sha256(materialized).hexdigest()})
evidence = root / 'art/cartoon/standing018-proportions-v1/review-evidence/checkout-v1'
evidence.mkdir(parents=True, exist_ok=False)
(evidence / 'check_checkout.py').write_bytes(Path(__file__).read_bytes())
(evidence / 'report.json').write_text(json.dumps({'status': 'PASS', 'cases': rows,
    'attributes_sha256': hashlib.sha256(attrs).hexdigest()}, indent=2) + '\n', encoding='utf-8')
print('PASS protected checkout; FIRED removed attribute naming generation-request-v2.json; PASS restored checkout')
