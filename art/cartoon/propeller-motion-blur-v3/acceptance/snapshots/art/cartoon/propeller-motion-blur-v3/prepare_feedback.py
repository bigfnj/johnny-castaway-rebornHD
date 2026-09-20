"""Bind the requested five blurred propellers to the preceding review."""
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = HERE.parent/'gulls-clock-props-corrections-v2'
def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
rows = json.loads((PRIOR/'review-data.json').read_text(encoding='utf-8'))['frames']
frames = []
for old in rows:
    if old['resource'] != 'GJVIS3.BMP': continue
    frames.append({'key':old['key'],'resource':old['resource'],'frame':old['frame'],'group':old['group'],
        'correction':('Blur the spinning blades themselves into soft rotational sweeps, keeping the hub and engine sharp.' if old['group']=='propellers' else 'Blur the small lower propeller blades into fast rotational motion. Preserve the large top rotor.'),
        'original':old['images']['original'],'prior_raw':old['images']['corrected'],
        'prior_record':old['record'],'prior_request':old['request']})
assert len(frames)==5
feedback={'schema_version':1,'date':'2026-09-20',
    'user_request':'can you make the propeller more "blurred", like fast motion looking as opposed to a static propeller with action wind. same with the lower propeller on "rotors".',
    'reviewed_url':'http://127.0.0.1:8941/gulls-clock-props-corrections-v2/review.html',
    'frames':frames,'attachments':[],'prior_review':pin(PRIOR/'review-record.json'),
    'scope':'Five requested motion-blur refinements; no new appearance approval.'}
(HERE/'feedback.json').write_text(json.dumps(feedback,indent=2)+'\n',encoding='utf-8')
(HERE/'selected-versions.json').write_text(json.dumps({r['key']:1 for r in frames},indent=2)+'\n',encoding='utf-8')
print('Prepared five motion-blur refinements')
