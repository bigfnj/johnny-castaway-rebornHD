"""Preserve the requested partly hidden fish eye and two-wing card grips."""
import hashlib
import json
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREVIOUS=HERE.parent/'marine-scenes-batch-v1'
def pin(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
screenshots={}
for name,filename in {
    'fish':'codex-clipboard-80453a84-11e8-483d-8a5a-91904a3babc7.png',
    'gulls':'codex-clipboard-c3887fc6-3f9c-46b8-8987-a6acc23976b0.png'
}.items():
    source=Path('C:/Users/Admin/AppData/Local/Temp')/filename
    target=HERE/'reference/user-feedback'/f'{name}.png'
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copyfile(source,target)
    assert source.read_bytes()==target.read_bytes()
    screenshots[name]=pin(target)
notes={
    '025':'Restore the partly hidden far eye at the left edge of the fish head. Keep the large near eye, body and lowered scorecard.',
    '027':'Chest facing forward, head turned toward the left-hand card. Both wings hold the lowered diagonal card at separate edges. The fan behind the body is the tail.',
    '028':'Chest facing forward. Both wings hold the raised tilted card, with feather tips gripping its far-left and near/right lower edges. Tail stays behind the body.',
    '029':'Chest facing forward. Both wings hold the more upright card at separate edges. Keep the tail behind the body and the beak directed toward the card.'
}
rows=[]
for frame,note in notes.items():
    version=2 if frame=='025' else 1
    group='fish' if frame=='025' else 'gulls'
    rows.append({'resource':'GJDIVE.BMP','frame':frame,'group':group,'correction':note,
                 'original':pin(PREVIOUS/f'reference/original/GJDIVE.BMP/{frame}.png'),
                 'nearest8':pin(PREVIOUS/f'reference/nearest8/GJDIVE.BMP/{frame}.png'),
                 'prior_raw':pin(PREVIOUS/f'generation/GJDIVE.BMP/{frame}-generated-v{version}.png'),
                 'user_screenshot':screenshots[group]})
feedback={'schema_version':1,'date':'2026-09-19','status':'Four judge corrections requested; appearance review pending',
          'user_request':'025fish needs two eyes, one not fully shown, see it? 027 028 029, the seagull ifs facing forward, you have his butt up front, and he is using both his "wings" the way we would use hands,  look closely at the wing placement.',
          'prior_review_url':'http://127.0.0.1:8941/marine-scenes-batch-v1/review.html',
          'prior_review':pin(PREVIOUS/'review-record.json'),'screenshots':screenshots,'frames':rows,
          'source_note_correction':'Fish025 is a three-quarter head with a partly occluded second eye. Gull027-029 show the chest forward with both wings reaching to hold the card; the rear feather fan is the tail, not a spare raised wing. Earlier one-eye and wing interpretations are superseded.',
          'unmentioned_frames':'Other 32 drawings unchanged; no new approval inferred.',
          'production_package_changed':False}
(HERE/'feedback.json').write_text(json.dumps(feedback,indent=2)+'\n',encoding='utf-8')
print('Saved two exact screenshots and four correction records.')
