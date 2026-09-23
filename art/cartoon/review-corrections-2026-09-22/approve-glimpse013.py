"""Record the user's approval of the displayed swimmer-context 013 v5."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED = '93169db219cdc814b368a06b0693419e2ef71d962e3cc7bee99436fcedbfdaed'
QUOTE = 'approved, now it sounds like we can finally start on the next batch. Are there any other images that refused to be rendered that we put in the backlog ?'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def main():
    path = HERE / 'glimse/manifest.json'
    manifest = read(path)
    before = copy.deepcopy(manifest)
    entry = next(row for row in manifest['entries'] if row['frame'] == '013')
    output = pin(ROOT / entry['output'])
    assert output['sha256'] == EXPECTED
    acceptance_path = HERE / 'acceptance/appearance-glimpse013-v5.json'
    if not acceptance_path.exists():
        save(acceptance_path, {'schema_version': 1, 'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
             'key': 'SMGLIMSE.BMP-013', 'user_response_exact': QUOTE,
             'approval_scope': 'Appearance of the displayed Glimpse013 v5 with the head turned away. This completes appearance approval of all12 focused corrections; native integration and motion remain separate.',
             'output': output, 'previous_review_entry': copy.deepcopy(entry),
             'production_integrated': False, 'native_motion_checked': False})
    acceptance = read(acceptance_path)
    assert acceptance['output'] == output and acceptance['user_response_exact'] == QUOTE
    approval = {'record': pin(acceptance_path), 'scope': acceptance['approval_scope'], 'output': output}
    if entry.get('appearance_approval') != approval:
        entry.setdefault('review_history', []).append({'status': entry['status'], 'visual_review': entry.get('visual_review')})
    entry.update(status='approved_by_user', appearance_approval=approval,
                 visual_review='User approved the swimmer-context013 v5. Head turns away while retaining the upward tilt. Earlier output blocks remain linked as history.')
    for row, old in zip(manifest['entries'], before['entries']):
        if row['frame'] != '013':
            assert row == old
    save(path, manifest)
    print(json.dumps({'approved': 'SMGLIMSE.BMP-013', 'output': output, 'acceptance': pin(acceptance_path), 'other_entries_unchanged': True}))

if __name__ == '__main__':
    main()
