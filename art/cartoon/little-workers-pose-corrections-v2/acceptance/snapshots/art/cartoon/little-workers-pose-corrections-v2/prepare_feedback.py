"""Bind18 user-requested worker corrections to the reviewed72-drawing batch."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=HERE.parent/'little-workers-batch-v1'
REQUEST="002 - in frame 001 you have the right foot forward, so in 002 i need the left foot forward, hes walking. 013 014 this is the left foot, its walking progression. 016 again, walking, im not sure what you were doing but the right foot should be \"starting\" to move forward. in 017 it has completed its step forward. 020 its the final \"gait\" of the walk, you are trying to cross legs mid-stride, but its the end of the stride from 018 and 019. 021 lean him forward, hes STARTING to run. 026 remove the back arm. its not visible. 029, swap the arms, the foreground arm is reaching out to the left, and the faraway arm (left arm) is slightly forward. 032, he has 3 arms, dial it down to two please. looook at the original. 036, the far arm you have going up and back, is \"crossing\" the body and slightly covering the face. 037 is confusing, the far arm is wrapping across the body, with the \"right\" or foreground arm at his side. 039 the \"rear arm\" is actually moving in front across the body, not behind and back. 040 is closer to 041 with the far arm coming out not back, and the other arm is correct. 046 & 047 the \"closer arm, right arm) should have a slight bend in it. 054 the \"rear/left arm\" should be forward, further than the closer arm. 063 is him \"looking right which you got right, but the arms are pointing to something behind him."
NOTES={"2":["gait","Left foot forward, alternating from the right foot forward in 001. Keep the character facing right."],"13":["gait","Left foot moves forward in this phase of the walking progression."],"14":["gait","Left foot extends forward, continuing the walking progression from 013."],"16":["gait","Right foot is starting to move forward in a low walking step."],"17":["gait","Right foot has completed its forward step."],"20":["gait","Complete the stride from 018 and 019. This is the end of the gait, not crossed legs mid-stride."],"21":["gait","Lean the torso forward as he starts to run."],"26":["arms","Hide the rear arm behind the body; it is not visible in this pose."],"29":["arms","Swap the arm roles: near/right arm extends toward image-left; far/left arm is slightly forward."],"32":["arms","Exactly two arms, following the original. Remove the extra arm or sleeve shape."],"36":["arms","Far/left arm crosses the body and partly covers the face; it does not swing up and behind."],"37":["arms","Far/left arm wraps across the front of the body. Near/right arm stays at his side."],"39":["arms","Rear/left arm moves across the front of the body, not behind him."],"40":["arms","Far/left arm comes forward as in 041. Preserve the nearer arm."],"46":["arms","Give the near/right arm a slight elbow bend."],"47":["arms","Give the near/right arm a slight elbow bend."],"54":["arms","Far/left arm reaches forward farther than the nearer arm."],"63":["arms","Keep him looking right, while both arms point behind him toward image-left."]}
TOKENS=["bcdba9b4-c9d5-4fd3-bee5-73b2399cd6c3","9e1b161b-9234-4458-a38a-dddf4b8a887e","6aa6208b-a3b5-49d4-b486-695ad1060ca6","8ed2865a-70b8-417e-89c0-98c364a5b194","aadca15d-9f9e-4392-a03c-3a107bce9ca2","6f749fdc-cb52-411d-8941-6c5d6e88f475","3417f108-ac75-4e8a-85e8-181ef7e4727d","adfc62e5-bf16-4230-95e1-12627bd43fe0","4893a2f6-adfb-4577-b766-76cd1fca8958","5b187a40-e548-4d5c-876a-04f6d113bfe4","2b2b67f5-3a04-4eb1-87b9-f4aa66567859","5fa6d7b6-4bc0-468a-a7db-3173d25bb9c8"]
def pin(p):
    return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rows=json.loads((PRIOR/'review-data.json').read_text())['assets']
frames=[]
for r in rows:
    n=int(r['frame'])
    if r['resource']!='LILIPUTS.BMP' or str(n) not in NOTES:continue
    group,correction=NOTES[str(n)]
    frames.append({'key':r['key'],'resource':r['resource'],'frame':r['frame'],'group':group,'correction':correction,
      'original':r['original_reference'],'prior_raw':r['selected_raw'],'prior_record':r['generation_record'],'prior_request':r['request']})
frames.sort(key=lambda r:int(r['frame']))
assert len(frames)==18
attachments=[]
for n,token in enumerate(TOKENS,1):
    src=Path('C:/Users/Admin/AppData/Local/Temp')/f'codex-clipboard-{token}.png'
    dest=HERE/'reference'/f'user-feedback-{n:02}.png'
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dest)
    attachments.append(pin(dest))
feedback={'schema_version':1,'date':'2026-09-20','user_request':REQUEST,
 'reviewed_url':'http://127.0.0.1:8941/little-workers-batch-v1/review.html',
 'frames':frames,'attachments':attachments,'prior_review':pin(PRIOR/'review-record.json'),
 'scope':'18 requested appearance corrections; other drawings retain their prior status. User anatomical leg identity, gait interpretation and arm occlusion override earlier pose notes.'}
(HERE/'feedback.json').write_text(json.dumps(feedback,indent=2)+'\n',encoding='utf-8')
(HERE/'selected-versions.json').write_text(json.dumps({r['key']:1 for r in frames},indent=2)+'\n',encoding='utf-8')
print('Prepared 18 worker corrections')
