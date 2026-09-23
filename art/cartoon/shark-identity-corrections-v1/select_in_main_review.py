"""Apply the reviewed correction candidates while preserving the other 45 selections."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = HERE.parent / 'mermaid-departures-and-dates-batch-v1'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    plan = read(HERE / 'correction-plan.json')
    frozen = read(HERE / 'previous-batch-review-data.json')
    focused = read(HERE / 'review-data.json')
    expected = {row['key'] for row in plan['entries']}
    assert {row['key'] for row in focused['entries']} == expected
    assert len(expected) == 27
    assets = {}
    for row in focused['entries']:
        assert row['status'] == 'awaiting_review' and row['output'] and row['record'], row['key']
        assets[row['key']] = {'version': row['version'], 'review_note': row['visual_review'],
                              'output': row['output'], 'record': row['record']}
    for entry in plan['entries']:
        for field in ('original', 'nearest8', 'previous', 'previous_record'):
            pinned = entry[field]
            assert hashlib.sha256((ROOT / pinned['path']).read_bytes()).hexdigest() == pinned['sha256'], pinned['path']
    payload = {'schema_version': 1, 'reason': 'User correction: the animal is the established gray shark with razor teeth and sneaky demeanor.',
               'assets': assets, 'appearance_approval': None}
    (BATCH / 'shark-correction-overrides.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    subprocess.run([sys.executable, str(BATCH / 'merge_review_notes.py')], check=True)
    subprocess.run([sys.executable, str(BATCH / 'build_review.py')], check=True)
    current = {row['key']: row for row in read(BATCH / 'review-data.json')['assets']}
    previous = {row['key']: row for row in frozen['assets']}
    assert len(current) == 72 and current.keys() == previous.keys()
    unchanged = []
    for key, row in current.items():
        if key in assets:
            assert row['version'] == assets[key]['version']
            assert row['selected_raw']['sha256'] == assets[key]['output']['sha256']
        else:
            assert row['version'] == previous[key]['version'], key
            assert row['selected_raw']['sha256'] == previous[key]['selected_raw']['sha256'], key
            unchanged.append({'key': key, 'version': row['version'], 'sha256': row['selected_raw']['sha256']})
    assert len(unchanged) == 45
    result = {'corrected': 27, 'other_selections_unchanged': unchanged, 'historical_pins_verified': True,
              'appearance_approval': None, 'production_integrated': False, 'native_motion_checked': False}
    (HERE / 'main-review-selection-record.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Selected all 27 shark corrections; verified the other 45 selections and all frozen originals/previous candidates are unchanged.')

if __name__ == '__main__':
    main()
