"""Preserve the user's rear-view, grounded-clothes and stick corrections."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent/'gull-clothes-batch-v1'

def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

screenshots = {}
for name,filename in {
    'away':'codex-clipboard-b2d10b55-f3ee-4977-9300-b5dc74f3f6bc.png',
    'clothes':'codex-clipboard-81bf13cc-6d89-4f45-9517-7f413097e603.png',
    'stick':'codex-clipboard-807e5825-1b23-42fb-9b4c-5b0f8f41e8eb.png'
}.items():
    original=Path('C:/Users/Admin/AppData/Local/Temp')/filename
    target=HERE/'reference/user-feedback'/f'{name}.png'
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): shutil.copyfile(original,target)
    assert target.read_bytes()==original.read_bytes()
    screenshots[name]=pin(target)
prior_versions=json.loads((PREVIOUS/'selected-versions.json').read_text(encoding='utf-8'))
notes={
    '037':'Rear-quarter flight away. Back of head and body visible, eyes entirely hidden; clothes remain in the far-side beak.',
    '040':'Rear-quarter flight away. Back of head and body visible, eyes entirely hidden; clothes remain in the far-side beak.',
    '046':'Rear view flying away with wings down. Show back of head/body and tail feathers, no eyes or frontal face.',
    '047':'Rear view flying away with wings near level. Show back of head/body and tail feathers, no eyes or frontal face.',
    '048':'Rear view flying away with wings up. Show back of head/body and tail feathers, no eyes or frontal face.',
    '004':'White clothes in a grounded heap, with the black belt resting on/among them. No floating cloth arches.',
    '034':'White clothes in a grounded heap, with the black belt resting on/among them. No floating cloth arches.',
    '016':'White clothes in a grounded heap, preserving the source diagonal footprint; the black item is a belt.',
    '045':'White clothes in a low grounded heap, with the black belt resting on/among them. No floating strips.',
    '000':'One continuous C-shaped bend. Remove the extra lower reverse bend; retain the source motion strokes.'
}
rows=[]
for frame,note in notes.items():
    group='away' if int(frame) in [37,40,46,47,48] else ('stick' if frame=='000' else 'clothes')
    version=prior_versions.get(f'GJGULL2.BMP-{frame}',1)
    rows.append({'resource':'GJGULL2.BMP','frame':frame,'group':group,'correction':note,
                 'original':pin(PREVIOUS/f'reference/original/GJGULL2.BMP/{frame}.png'),
                 'nearest8':pin(PREVIOUS/f'reference/nearest8/GJGULL2.BMP/{frame}.png'),
                 'prior_raw':pin(PREVIOUS/f'generation/GJGULL2.BMP/{frame}-generated-v{version}.png'),
                 'user_screenshot':screenshots[group]})
feedback={'schema_version':1,'date':'2026-09-19','status':'Ten corrections requested; appearance review pending',
          'user_request':'037 & 040 the gull is flying away, with its eyes unseen and the back of his head shown, with the back of the body present, with the clothes in the beak. 046 & 047 & 048 , same, the gull is flying away, we see the tail feathers and the back of the head. 004 & 034 & 016 & 045, clothes dont "float", have them in a heap, the BLACK item is a belt. in 000 the stick does not have another bend at the bottom, its one continues "c" chape.',
          'prior_review_url':'http://127.0.0.1:8941/gull-clothes-batch-v1/review.html',
          'prior_review':pin(PREVIOUS/'review-record.json'),'screenshots':screenshots,'frames':rows,
          'unmentioned_frames':'No new appearance approval inferred for the other 29 drawings.',
          'source_note_correction':'The user resolves these five views as rear-facing. Earlier front/side interpretation is rejected history, not pose authority. The black clothing item is a belt.',
          'production_package_changed':False}
(HERE/'feedback.json').write_text(json.dumps(feedback,indent=2)+'\n',encoding='utf-8')
print('Saved three exact screenshots and ten correction records.')
