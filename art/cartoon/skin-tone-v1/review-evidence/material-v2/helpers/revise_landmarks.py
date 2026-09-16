from pathlib import Path
import copy
import hashlib
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'art/cartoon/skin-tone-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
old_path=HERE/'protected-landmarks-v1.json'
assert sha(old_path.read_bytes())=='44d904d6c72fd9706036dd746391e3bae180c3dbe9df2a918eec36bb05c49c97'
old=json.loads(old_path.read_bytes());new=copy.deepcopy(old)
replacements={4:[54,54],5:[61,54],8:[49,54]}
changes=[]
for row in new['frames']:
    with Image.open(HERE/row['input']) as opened: im=opened.convert('RGBA')
    for p in row['landmarks']:
        if p['role']!='chest-hair':continue
        before=copy.deepcopy(p)
        p['role']='lower-hair'
        if row['frame'] in replacements:
            p['xy']=replacements[row['frame']]
            p['rgba']=list(im.getpixel(tuple(p['xy'])))
            changes.append(dict(frame=row['frame'],before=before,after=copy.deepcopy(p),reason='Original-only pixel-grid review shows the previous coordinate on shaded/mixed skin beside the strand. The replacement is visibly inside brown hair. No corrected output was used to choose it.'))
new['schema_version']=2
new['supersedes']=dict(path='protected-landmarks-v1.json',sha256=sha(old_path.read_bytes()),reason='Three mislabeled chest-hair coordinates corrected after magnified original-only review. The frozen v1 remains unchanged as rejected semantic evidence.')
new['selection_method']+=' All 17 lower-hair samples were then reviewed on 20x original-only pixel grids. Three initial chest-hair coordinates were classified as skin and corrected; all lower samples are named lower-hair because several are the lower beard rather than chest hair.'
new['semantic_corrections']=changes
new['limitations']='Sparse protected-material samples, not exhaustive segmentation. Lower-hair denotes either lower beard or a chest strand, without claiming which at uncertain junctions. Hidden rear-view eyes are explicitly excluded. Regions cover only interior hat white, hair/beard and shorts white.'
for row in new['frames']:
    assert sha((HERE/row['input']).read_bytes())==row['input_sha256']
    im=Image.open(HERE/row['input']).convert('RGBA')
    for p in row['landmarks']:
        assert list(im.getpixel(tuple(p['xy'])))==p['rgba']
        if 'region_xywh' in p:
            x,y,w,h=p['region_xywh'];assert sha(im.crop((x,y,x+w,y+h)).tobytes())==p['region_rgba_sha256']
dest=HERE/'protected-landmarks-v2.json';assert not dest.exists()
dest.write_text(json.dumps(new,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest.read_bytes()),landmarks=new['landmark_count'],regions=new['region_count'],corrected_coordinates=3,reviewed_lower_hair_samples=17)))
