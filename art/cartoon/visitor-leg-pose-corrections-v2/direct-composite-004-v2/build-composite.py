"""Authorized direct PNG combination for the SSUZY004 leg-placement review."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
import json
import hashlib
import numpy as np

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]
UPPER = ART / 'mermaid-expression-corrections-v1/generation/SSUZY1.BMP/004-generated-v2.png'
LOWER = HERE.parent / 'generation/SSUZY1.BMP/003-generated-v2.png'
ROOT = ART.parents[1]

upper = Image.open(UPPER).convert('RGBA')
lower = Image.open(LOWER).convert('RGBA')
upper_polygon = [(0,0),(800,0),(800,500),(728,641),(708,655),(686,673),
                 (660,686),(637,692),(596,692),(543,682),(477,666),(447,670),
                 (420,684),(402,690),(0,740)]
lower_polygon = [(704,0),(1724,0),(1724,912),(658,912),(658,731),
                 (649,721),(665,680),(680,630),(697,587),(704,557)]

def masked(im, points):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    out = im.copy()
    out.putalpha(ImageChops.multiply(im.getchannel('A'), mask))
    return out, mask

upper_cut, upper_mask = masked(upper, upper_polygon)
lower_cut, lower_mask = masked(lower, lower_polygon)
upper_mask.save(HERE / 'upper-mask.png')
lower_mask.save(HERE / 'lower-mask.png')
variants = [
    ('004-composite-v2',1.0,-140,20),
]
for name,scale,dx,dy in variants:
    canvas = Image.new('RGBA',upper.size)
    scaled = lower_cut if scale == 1.0 else lower_cut.resize((round(lower.width*scale),round(lower.height*scale)),Image.Resampling.LANCZOS)
    canvas.alpha_composite(scaled,(dx,dy))
    # Close the small waist join with an antialiased extension in the existing
    # skin palette. The complete donor hips, knees, calves and feet are intact.
    def curve(a,b,c,d):
        return [tuple((1-t)**3*a[i]+3*(1-t)**2*t*b[i]+3*(1-t)*t*t*c[i]+t**3*d[i] for i in (0,1)) for t in [n/40 for n in range(41)]]
    origin = (390,640)
    seam = Image.new('RGBA',(250*4,150*4))
    draw = ImageDraw.Draw(seam)
    to_local = lambda points: [(round((x-origin[0])*4),round((y-origin[1])*4)) for x,y in points]
    edge = curve((412,681),(457,699),(484,719),(510,741)) + curve((510,741),(540,748),(566,743),(590,736))
    shape = [(412,668)] + edge + [(605,720),(605,674)]
    draw.polygon(to_local(shape),fill='#ffa14f')
    draw.line(to_local(edge),fill='#100b08',width=24,joint='curve')
    seam = seam.resize((250,150),Image.Resampling.LANCZOS)
    pixels = seam.load()
    beneath = canvas.load()
    for sy in range(seam.height):
        for sx in range(seam.width):
            gx,gy = sx+origin[0],sy+origin[1]
            if gx > 545 and beneath[gx,gy][3] > 245:
                r,g,b,a = pixels[sx,sy]
                pixels[sx,sy] = (r,g,b,round(a*max(0,min(1,(610-gx)/65))))
    canvas.alpha_composite(seam,origin)
    canvas.alpha_composite(upper_cut)
    # The input has near-opaque alpha across its painted interior. Retain those
    # source RGBA pixels exactly instead of baking the donor through that alpha.
    source_pixels = np.array(upper)
    canvas_pixels = np.array(canvas)
    retain = (np.array(upper_mask) == 255) & (source_pixels[:,:,3] >= 8)
    canvas_pixels[retain] = source_pixels[retain]
    canvas = Image.fromarray(canvas_pixels)
    canvas.save(HERE / f'{name}.png')
    preview = Image.new('RGBA',canvas.size,'#eeeae0')
    preview.alpha_composite(canvas)
    preview.convert('RGB').save(HERE / f'{name}-light.jpg')
    preview = Image.new('RGBA',canvas.size,'#263540')
    preview.alpha_composite(canvas)
    preview.convert('RGB').save(HERE / f'{name}-dark.jpg')

def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

result = np.array(canvas)
original_upper = np.array(upper)
preserved_upper = (np.array(upper_mask) == 255) & (original_upper[:,:,3] >= 8)
upper_differences = int(np.any(result != original_upper,axis=2)[preserved_upper].sum())
leg_source = np.array(lower)[690:890,880:1700]
leg_result = result[710:910,740:1560]
visible_leg = leg_source[:,:,3] > 0
leg_differences = int(np.any(leg_source != leg_result,axis=2)[visible_leg].sum())
assert upper_differences == 0, '004-composite-v2.png: upper-body source pixels changed'
assert leg_differences == 0, '004-composite-v2.png: donor lower-leg source pixels changed'
alpha = canvas.getchannel('A')
edge_alpha = int(max(result[0,:,3].max(),result[-1,:,3].max(),result[:,0,3].max(),result[:,-1,3].max()))
assert edge_alpha == 0, '004-composite-v2.png: image reaches canvas edge'
record = {
    'schema_version':1,'resource':'SSUZY1.BMP','frame':'004','version':2,
    'tool':'Pillow','mode':'direct-png-composite',
    'method':'Authorized direct combination of 004 v2 upper body and approved 003 v2 hips and legs. Both sources retain native scale. Lower body is translated (-140,+20), without rotation or limb deformation. A short waist join beneath the foreground forearm is reconstructed in the existing skin palette and outline, with a faded color seam.',
    'output':pin(HERE/'004-composite-v2.png'),
    'request':pin(HERE/'request.json'),
    'references':[pin(UPPER),pin(LOWER)],
    'transforms':{'upper':{'scale':1.0,'translation':[0,0],'rotation_degrees':0},
                  'lower':{'scale':1.0,'translation':[-140,20],'rotation_degrees':0}},
    'waist_join_region':[390,640,640,790],
    'image':{'canvas':list(canvas.size),'mode':canvas.mode,'alpha_range':list(alpha.getextrema()),
             'alpha8_bounds':list(alpha.point(lambda a:255 if a>=8 else 0).getbbox()),'edge_alpha_max':edge_alpha},
    'pixel_checks':[{'region':'visible 004 head, upper body, arms, hands and bottle retained by upper mask (alpha at least 8)',
                     'visible_pixels_checked':int(preserved_upper.sum()),'different_pixels':upper_differences},
                    {'region':'003 folded lower leg and feet, source box [880,690,1700,890]',
                     'visible_pixels_checked':int(visible_leg.sum()),'different_pixels':leg_differences}],
    'build_script':pin(Path(__file__).resolve()),
    'masks':[pin(HERE/'upper-mask.png'),pin(HERE/'lower-mask.png')],
    'appearance_approval':None,'production_integrated':False,'native_motion_checked':False,
}
(HERE/'record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
