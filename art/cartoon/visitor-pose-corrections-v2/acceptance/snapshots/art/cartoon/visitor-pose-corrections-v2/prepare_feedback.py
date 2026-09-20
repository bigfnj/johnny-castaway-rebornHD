"""Bind seven user-requested visitor corrections to the reviewed batch."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=HERE.parent/'visitors-and-props-batch-v1'
REQUEST='005 he is holding the camera with two hands, bring the outer hand over to touch the camera. 009 & 010 he has no sunglasses on. 012 013 014 you are missing the "angle" of the belly, the lady is shifting right, you have her shifting left or center. more like 015. 016 she is facing front looking down, not backwards.'
def pin(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
notes={5:('camera','Hold the camera with both hands. Bring the outer hand across to touch/support the camera.'),9:('camera','Remove the sunglasses entirely; preserve the leaning pose.'),10:('camera','Remove the sunglasses entirely; preserve the leaning pose.'),12:('woman','Shift the belly and waist toward screen-right, like 015. Preserve this frame\'s raised-arm gesture.'),13:('woman','Shift the belly and waist toward screen-right, like 015. Preserve this frame\'s overhead arm bend.'),14:('woman','Shift the belly and waist toward screen-right, like 015. Preserve this frame\'s overhead arm bend.'),16:('woman','Front-facing with head lowered and looking down, not a rear view. Preserve the left-up/right-out arm pose.')}
rows=json.loads((PRIOR/'review-data.json').read_text())['assets']
frames=[]
for r in rows:
    n=int(r['frame'])
    if r['resource']!='GJNAT3.BMP' or n not in notes:continue
    group,correction=notes[n]
    frames.append({'key':r['key'],'resource':r['resource'],'frame':r['frame'],'group':group,'correction':correction,
      'original':r['original_reference'],'prior_raw':r['selected_raw'],'prior_record':r['generation_record'],'prior_request':r['request']})
frames.sort(key=lambda r:int(r['frame']))
assert len(frames)==7
attachments=[]
for n,token in enumerate(['9b66ddc5-38c8-4290-ad86-c0580e6471b9','8719175d-6bb2-4331-a371-7074fcaf9682','8ca2de15-438f-4a02-afe1-008d98f4c1fe','d47cd6bd-1b39-4452-9e4d-93077d3f8b0c'],1):
    src=Path('C:/Users/Admin/AppData/Local/Temp')/f'codex-clipboard-{token}.png'
    dest=HERE/'reference'/f'user-feedback-{n:02}.png'
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dest)
    attachments.append(pin(dest))
feedback={'schema_version':1,'date':'2026-09-20','user_request':REQUEST,
 'reviewed_url':'http://127.0.0.1:8941/visitors-and-props-batch-v1/review.html',
 'frames':frames,'attachments':attachments,'prior_review':pin(PRIOR/'review-record.json'),
 'scope':'Seven requested appearance corrections; other drawings retain their prior status. User interpretation overrides earlier pose notes.'}
(HERE/'feedback.json').write_text(json.dumps(feedback,indent=2)+'\n',encoding='utf-8')
(HERE/'selected-versions.json').write_text(json.dumps({r['key']:1 for r in frames},indent=2)+'\n',encoding='utf-8')
print('Prepared seven visitor corrections')
