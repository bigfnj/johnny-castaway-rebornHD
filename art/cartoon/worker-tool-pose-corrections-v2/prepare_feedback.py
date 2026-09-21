"""Bind seven user corrections to exact originals and previous selected drawings."""
from pathlib import Path
import hashlib, json, shutil
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT/'art/cartoon/workers-and-mermaids-batch-v1'
def pin(p):
    return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,value):
    p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def main():
    corrections = {
        '076': ('arms', 'The anatomical left/near arm reaches down; the anatomical right/far arm swings back. Correct shoulder ownership and overlap, preserving the crouched left-facing pose.'),
        '077': ('tools', 'Rotate the gripping hand naturally around the raised hammer handle so its inner/palm side faces the viewer. Preserve the source hammer direction and crouch.'),
        '078': ('tools', 'Correct the raised hammer grip to show the inner/palm side of the hand, with natural thumb and wrist orientation. Preserve this distinct source swing phase.'),
        '079': ('tools', 'Match the original hammer angle, including the shaft and head orientation relative to the raised hand. Do not reuse the previous upward diagonal hammer angle.'),
        '092': ('body', 'Turn the entire character left, including torso, hips, legs and both feet, with the head aligned to that body turn. Preserve both raised arms and the rope coil.'),
        '093': ('tools', 'The loose rope hangs in mid-air to the left. The wooden peg is closer to the worker under the hammer strike, not attached at the remote end of a long rope held in the free hand. Match the exact original spacing and arm/prop contact.'),
        '096': ('body', 'Turn the entire character left, including chest, pelvis, knees and both feet. Preserve the asymmetric empty-hand gesture and rope coil; a head-only turn is insufficient.'),
    }
    quote = '076 Look closer at the arms, the left arm is down and the far (right) arm is back. 077 the "hand" holding the hammer is backwards, your showing me the outer part of the hand, not the inner, its not natural, same for 078. 079, look cloer at the ANGLE of the hammer, and correct for it. 092 the entire body should be facing left, not forward with the head looking left. 093   the rope is "hanging in mid-air" and the wooden nail is what he is hitting closer to him, look closer at the original. 096, the body should be facing left, not just the head, look at the feet and orient the character properly. while you correct those, show me a workup of all of the "blocked" images originals so i can put them into context for you so we can tackle those.'
    prior = json.loads((PRIOR/'review-data.json').read_text(encoding='utf-8'))
    frames=[]
    for n,(group,correction) in corrections.items():
        row=next(r for r in prior['assets'] if r['resource']=='LILIPUTS.BMP' and r['frame']==n)
        frames.append({'key':row['key'],'resource':row['resource'],'frame':n,'group':group,'correction':correction,'original':row['original_reference'],'prior_raw':row['selected_raw'],'prior_record':row['generation_record'],'prior_request':row['request']})
    attachments=[]
    for filename in ['codex-clipboard-5e5a3a59-69dc-411d-81e1-a340561292b8.png','codex-clipboard-eca6fa1c-9c49-4cc4-9b4f-4fa774f4b2c8.png','codex-clipboard-2ebb2279-e280-4101-b5b2-7f3ebb17658d.png','codex-clipboard-27102d64-a44f-4b9e-b5f7-a17d99665baf.png','codex-clipboard-b627e491-da35-4675-bfb1-7caca90d95c7.png','codex-clipboard-de019106-d731-4230-848c-7b25c28cfa09.png']:
        dest=HERE/'feedback'/filename
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(Path('C:/Users/Admin/AppData/Local/Temp')/filename,dest)
        attachments.append(pin(dest))
    (HERE/'generation/LILIPUTS.BMP').mkdir(parents=True,exist_ok=True)
    if not (HERE/'record_output.py').exists():
        shutil.copyfile(PRIOR/'record_output.py',HERE/'record_output.py')
    save(HERE/'feedback.json',{'schema_version':1,'user_request':quote,'frames':frames,'attachments':attachments,'prior_review':pin(PRIOR/'review-record.json'),'scope':'Seven requested corrections only. No new approval of other drawings is inferred. Blocked-original context is a separate review.'})
    if not (HERE/'selected-versions.json').exists():
        save(HERE/'selected-versions.json',{f['key']:1 for f in frames})
    print('Prepared seven source/previous bindings and six feedback attachments.')
if __name__=='__main__':
    main()
