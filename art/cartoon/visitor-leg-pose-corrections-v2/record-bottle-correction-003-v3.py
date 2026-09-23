"""Select the returned bottle correction for review, preserving prior approval."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

selection_path = HERE / 'selected-versions.json'
selection = json.loads(selection_path.read_text(encoding='utf-8'))
key = 'SSUZY1.BMP-003'
state = selection['frames'][key]
assert state['display_version'] in (2, 3)
prior = copy.deepcopy(state['appearance_approval'])
others = {k: copy.deepcopy(v) for k, v in selection['frames'].items() if k != key}
record_path = HERE / 'generation/SSUZY1.BMP/003-record-v3.json'
record = json.loads(record_path.read_text(encoding='utf-8'))
assert record['appearance_approval'] is None
assert pin(ROOT / record['output']['path']) == record['output']
feedback_path = HERE / 'feedback-bottle-continuity-v1.json'
save(feedback_path, {
    'schema_version': 1,
    'user_feedback': 'it looks like in 003 we forgot to keep the sunblock bottle in her hand. in 009 and 010 it drops from the image, it should still be on the ground in the exact same spot.',
    'frame_003_direction': 'Restore the sunblock bottle in her hand while preserving the selected pose and palette.',
    'ground_bottle_direction': 'Maintain the same ground location through 008, 009 and 010; inspect the separate source prop layer before redrawing body frames.',
    'supersedes': 'The earlier instruction to remove the bottle from 003 is superseded by this latest user correction.',
    'appearance_approval': None,
})
if not any(h.get('status') == 'reopened_for_correction' and h.get('version') == 2 for h in state['history']):
    state['history'].append({'version': 2, 'status': 'reopened_for_correction', 'reason': 'User requested restoring the bottle in hand.', 'appearance_approval': prior})
state.update(display_version=3, latest_version=3, latest_status='returned', review_status='ready_for_review',
    status_text='New v3 restores the sunblock bottle in her hand while retaining the reclining pose. Awaiting appearance review.',
    display_label='Bottle correction v3', previous_label='Previous selected drawing v2', comparison_previous=prior['output'],
    requested_change='Restore the sunblock bottle in her hand. Preserve the selected reclining pose, palette and overlapping legs.',
    latest_feedback=pin(feedback_path))
selection['status'] = 'bottle_correction_003_awaiting_review'
selection['selection_scope'] = '003 v3 is a new bottle correction awaiting review. Prior appearance approvals remain attached to their exact earlier outputs. Other selected visitor drawings are unchanged; 004 and 005 color candidates are reviewed in the separate color sequence viewer.'
assert state['appearance_approval'] == prior
assert {k:v for k,v in selection['frames'].items() if k != key} == others
save(selection_path, selection)
print(json.dumps({'frame': key, 'display_version': 3, 'status': state['review_status'], 'prior_approval_preserved': True}))
