"""Bounded readback: the face revision changes only pumpkin package/native pixels."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import zipfile

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'art/cartoon/seasonal-v1/native'))
import capture as c

base = root / 'build/seasonal-v1'
current = base / 'native-candidate-v3'
old = base / 'native-candidate-v2'
report_path = current / 'v2-delta.json'
assert not report_path.exists()
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def members(path):
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
        return {name: sha(archive.read(name)) for name in archive.namelist()}

before = members(base / 'cartoon-seasonal-draft-v2.zip')
after = members(base / 'cartoon-seasonal-draft-v3.zip')
assert before.keys() == after.keys()
changed = [name for name in before if before[name] != after[name]]
expected = ['data/styles/cartoon/BMP/HOLIDAY.BMP/000.png']
assert changed == expected, changed
assert sha(c.CODEC.read_bytes()) == c.CODEC_SHA
spec = importlib.util.spec_from_file_location('seasonal_codec', c.CODEC)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
records = []
for group in ('day', 'night', 'offset'):
    for holiday, (name, _) in c.HOLIDAYS.items():
        for phase in ('smoke', 'repeat'):
            rel = Path('captures') / group / name / phase
            prior = codec.ppm(old / rel / 'final.ppm')
            updated = codec.ppm(current / rel / 'final.ppm')
            ar = json.loads((old / rel / 'report.json').read_bytes())
            br = json.loads((current / rel / 'report.json').read_bytes())
            assert ar['pixels_sha256'] == sha(prior)
            assert br['pixels_sha256'] == sha(updated)
            assert ar['actual_holiday_draws'] == br['actual_holiday_draws']
            if holiday == 1:
                result = c.compare_pixels(prior, updated, holiday, ar['offset'])
            else:
                assert prior == updated, str(rel)
                assert (old / rel / 'final.png').read_bytes() == (current / rel / 'final.png').read_bytes(), str(rel)
                result = {'changed_pixels': 0, 'exact_unchanged': True}
            records.append({'capture': rel.as_posix(), **result})
assert sum(row['changed_pixels'] > 0 for row in records) == 6
assert sum(row['changed_pixels'] == 0 for row in records) == 24
report = {'status': 'PASS', 'method': 'Read actual two private archives and30 matched native capture pairs; previous captures/images remain unchanged.',
          'old_archive_sha256': sha((base / 'cartoon-seasonal-draft-v2.zip').read_bytes()),
          'new_archive_sha256': sha((base / 'cartoon-seasonal-draft-v3.zip').read_bytes()),
          'changed_members': changed, 'unchanged_member_count': len(before) - len(changed),
          'comparisons': records, 'unchanged_images': 24, 'pumpkin_images_changed': 6,
          'helper_sha256': sha(Path(__file__).read_bytes()),
          'reused_comparison_sha256': sha(Path(c.__file__).read_bytes()),
          'scope': 'Other3 seasonal assets and all original production payloads are exact. Pumpkin changes are inside its unchanged full canvas; this does not assert every non-face source pixel is unchanged or grant art approval.'}
report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print('PASS only pumpkin member changed;24 other native images exact;6 pumpkin images scoped')
