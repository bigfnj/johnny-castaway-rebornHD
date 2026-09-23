"""Tighten only the circled belly silhouette of the authorized 004 composite."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE.parent / 'direct-composite-004-v2/004-composite-v2.png'
source = Image.open(SOURCE).convert('RGBA')
ROI = (410,650,642,768)
SCALE = 4

def curve(a,b,c,d):
    return [tuple((1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i] for i in (0,1)) for t in [n/80 for n in range(81)]]

path = curve((416,685),(476,715),(502,691),(550,708)) + curve((550,708),(583,720),(601,741),(636,746))
local = lambda points:[((x-ROI[0])*SCALE,(y-ROI[1])*SCALE) for x,y in points]
size = ((ROI[2]-ROI[0])*SCALE,(ROI[3]-ROI[1])*SCALE)
keep = Image.new('L',size,255)
draw = ImageDraw.Draw(keep)
draw.polygon(local(path+[(636,ROI[3]+2),(416,ROI[3]+2)]),fill=0)
keep = keep.resize((ROI[2]-ROI[0],ROI[3]-ROI[1]),Image.Resampling.LANCZOS)
part = source.crop(ROI)
underfill = Image.new('RGBA',size)
ImageDraw.Draw(underfill).polygon(local([(447,669),(469,662),(511,674),(510,684),(447,680)]),fill='#ffa14f')
underfill = underfill.resize(part.size,Image.Resampling.LANCZOS)
filled = Image.alpha_composite(underfill,part)
pixels, patched = np.array(part),np.array(filled)
gap = (pixels[:,:,3]<250) & (np.array(underfill)[:,:,3]>0)
pixels[gap] = patched[gap]
part = Image.fromarray(pixels)
part.putalpha(ImageChops.multiply(part.getchannel('A'),keep))
ink = Image.new('RGBA',size)
ImageDraw.Draw(ink).line(local(path),fill='#100b08',width=6*SCALE,joint='curve')
ink = ink.resize(part.size,Image.Resampling.LANCZOS)
part.alpha_composite(ink)
result = source.copy()
result.paste(part,(ROI[0],ROI[1]))
result.save(HERE/'004-composite-v3.png')
for label,color in [('light','#eeeae0'),('dark','#263540')]:
    preview = Image.new('RGBA',result.size,color)
    preview.alpha_composite(result)
    preview.convert('RGB').save(HERE/f'004-composite-v3-{label}.jpg')
    detail = preview.crop((390,630,715,790)).resize((975,480),Image.Resampling.LANCZOS)
    detail.convert('RGB').save(HERE/f'belly-detail-{label}.jpg')

old,new = np.array(source),np.array(result)
different = np.any(old!=new,axis=2)
outside = different.copy()
outside[ROI[1]:ROI[3],ROI[0]:ROI[2]] = False
assert not outside.any(), '004-composite-v3.png: pixels outside belly edit changed'
ys,xs = np.where(different)
def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

alpha = result.getchannel('A')
checks = {'edit_box':list(ROI),'changed_pixels':int(different.sum()),
          'actual_change_bounds':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
          'outside_box_changed':int(outside.sum())}
record = {
    'schema_version':1,'resource':'SSUZY1.BMP','frame':'004','version':3,
    'tool':'Pillow','mode':'direct-png-composite',
    'requested_change':'Smooth the circled protruding belly edge into an inward curve, retaining the current proportions and stacked-leg pose.',
    'method':'Direct contour refinement of composite v2. Trim only the belly silhouette with an antialiased inward curve, redraw its short outline, and close the tiny forearm-join transparency gap. Every pixel outside the recorded belly box is unchanged.',
    'output':pin(HERE/'004-composite-v3.png'),
    'request':pin(HERE/'request.json'),
    'references':[pin(SOURCE)],
    'previous_candidate_record':pin(SOURCE.parent/'record.json'),
    'image':{'canvas':list(result.size),'mode':result.mode,'alpha_range':list(alpha.getextrema()),
             'alpha8_bounds':list(alpha.point(lambda a:255 if a>=8 else 0).getbbox())},
    'pixel_checks':checks,'build_script':pin(Path(__file__).resolve()),
    'appearance_approval':None,'production_integrated':False,'native_motion_checked':False,
}
(HERE/'record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':record['output'],'pixel_checks':checks}))
