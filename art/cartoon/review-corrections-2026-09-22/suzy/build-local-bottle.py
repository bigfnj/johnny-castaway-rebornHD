"""Apply the generated upright bottle locally to the approved 004 drawing."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ART = ROOT / 'art/cartoon'
SOURCE = ART / 'visitor-leg-pose-corrections-v2/direct-composite-004-v3/004-composite-v3.png'
GENERATED = HERE / '004-generated-v1.png'
source = Image.open(SOURCE).convert('RGBA')
generated = Image.open(GENERATED).convert('RGBA').resize(source.size, Image.Resampling.LANCZOS)
mask = Image.new('L', source.size)
draw = ImageDraw.Draw(mask)
draw.polygon([(74,325),(262,325),(262,401),(285,444),(294,453),
              (308,486),(318,539),(350,574),(430,588),(445,611),(442,638),(398,651),(288,622),
              (254,609),(250,673),(211,725),(91,751),(54,705),(59,528)], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(2))
ImageDraw.Draw(mask).rectangle((380,650,source.width,source.height),fill=0)
result = Image.composite(generated, source, mask)
output = HERE / '004-upright-bottle-local-v1.png'
result.save(output)
mask.save(HERE / '004-edit-mask.png')
before, after = np.array(source), np.array(result)
changed = np.any(before != after, axis=2)
allowed = np.array(mask) > 0
assert not np.any(changed & ~allowed)
assert np.array_equal(before[770:], after[770:])
assert np.array_equal(before[650:770,380:], after[650:770,380:])
def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
record = {'mode':'built-in-imagegen-with-local-composite', 'resource':'SSUZY1.BMP','frame':'004',
          'source':pin(SOURCE),'generated':pin(GENERATED),'output':pin(output),
          'request':pin(HERE/'004-request.json'),'edit_mask':pin(HERE/'004-edit-mask.png'),
          'changed_pixels':int(changed.sum()),'approved_belly_and_lower_body_preserved':True,
          'appearance_approval':None,'production_integrated':False,'native_motion_checked':False}
(HERE/'004-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
for label, color in [('light',(238,237,228,255)),('dark',(25,48,59,255))]:
    bg = Image.new('RGBA',result.size,color)
    bg.alpha_composite(result)
    bg.convert('RGB').save(HERE/f'004-{label}-preview.jpg')
    bg.crop((65,310,400,750)).resize((670,880)).convert('RGB').save(HERE/f'004-{label}-detail.jpg')
print(json.dumps(record,indent=2))
