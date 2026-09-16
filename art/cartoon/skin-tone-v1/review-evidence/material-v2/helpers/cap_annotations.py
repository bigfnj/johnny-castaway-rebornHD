from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'art/cartoon/skin-tone-v1'
OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=json.loads((HERE/'input-index.json').read_bytes())['frames']
# Hand-traced pixel-edge lower boundaries from enlarged frozen inputs.
middle={
0:[[38,19],[49,14],[58,14],[64,15]],
1:[[53,20],[65,15],[74,15],[82,18]],
2:[[53,20],[65,15],[73,15],[81,18]],
3:[[39,19],[49,14],[58,14],[65,15]],
4:[[47,21],[61,16],[69,16],[76,18]],
5:[[55,21],[68,15],[76,15],[83,18]],
6:[[53,21],[65,15],[73,15],[81,18]],
7:[[31,20],[43,15],[50,15],[57,16]],
8:[[44,21],[58,15],[66,15],[73,18]],
9:[[36,18],[48,14],[58,14],[64,16]],
10:[[24,16],[28,14],[40,14],[45,16]],
11:[[17,15],[22,19]],
12:[[1,18]],15:[[1,18]],
16:[[24,15],[28,13],[40,13],[45,15]],
17:[[42,17],[52,13],[61,13],[67,15]],
18:[[17,15],[22,19]],19:[[17,15],[22,19]],
20:[[17,15],[22,19]],21:[[17,15],[22,19]],
22:[[17,15],[22,19]],23:[[17,15],[22,19]],
24:[[13,15],[16,13],[24,13],[33,16]],
25:[[19,15],[22,13],[30,13],[39,16]],
26:[[21,15],[24,13],[32,13],[41,16]],
27:[[13,15],[16,13],[24,13],[33,16]],
28:[[13,15],[16,13],[24,13],[33,17]],
29:[[13,15],[16,13],[24,13],[33,17]],
}
records=[]
for row in rows:
    w,h=row['canvas']; m=middle[row['frame']]
    line=[[0,m[0][1]]]+m+[[w,m[-1][1]]]
    lower=np.interp(np.arange(w)+.5,[p[0] for p in line],[p[1] for p in line])
    mask=(np.arange(h)[:,None]+.5<lower[None,:])
    records.append(dict(frame=row['frame'],input=row['input'],input_sha256=row['sha256'],canvas=row['canvas'],
                        lower_boundary_pixel_edges=line,
                        polygon_pixel_edges=[[0,0],[w,0]]+list(reversed(line)),
                        protected_pixel_count=int(mask.sum()),
                        mask_l_sha256=sha((mask.astype(np.uint8)*255).tobytes())))
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',16)
for k in range(7):
    sheet=Image.new('RGB',(1920,360),'#3a4550');d=ImageDraw.Draw(sheet)
    for n,row in enumerate(records[k*4:k*4+4]):
        im=Image.open(HERE/row['input']).convert('RGBA')
        crop=im.crop((0,0,im.width,40)).resize((im.width*5,200),Image.Resampling.NEAREST)
        ox=n*480+15;oy=45;sheet.paste(crop,(ox,oy),crop)
        d.text((ox,5),f"{row['frame']:03}",font=font,fill='white')
        points=[(ox+x*5,oy+y*5) for x,y in row['lower_boundary_pixel_edges']]
        d.line(points,fill='#22ffee',width=1)
        d.text((ox,265),str(row['lower_boundary_pixel_edges']),font=font,fill='white')
    sheet.save(OUT/f'cap-boundaries-{k}.png')
document=dict(schema_version=1,scope='Original-only visual cap exclusion annotations for the color corrector; these become algorithm inputs, not independent evidence of mask correctness.',
              input_index_sha256=sha((HERE/'input-index.json').read_bytes()),
              coordinate_convention='Pixel-edge coordinates. Protect pixel (x,y) when y+0.5 is strictly less than the piecewise-linear lower boundary at x+0.5. The polygon includes transparent space above the cap and a narrow adjoining hair/ink margin; forehead skin is below the traced boundary.',
              limitations='Hand-traced lower boundaries protect the complete visible white crown, gold band, anchor and dark brim. Mixed antialias pixels on the cap/hair boundary have no unique material assignment. This does not segment other materials.',frames=records)
(OUT/'cap-polygons-proposed.json').write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
