"""Independent appearance-region proposals for manual landmark review."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label, distance_transform_edt

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'art/cartoon/skin-tone-v1'
OUT = Path(__file__).resolve().parent
index = json.loads((HERE / 'input-index.json').read_bytes())
rear = {11, 12, 15, 18, 19, 20, 21, 22, 23}
chest = {0:[48,54],3:[49,53],4:[55,54],5:[63,54],6:[56,54],7:[44,55],8:[51,53],
         9:[43,54],10:[34,54],16:[34,53],17:[46,53],24:[31,52],25:[37,53],26:[38,53],27:[31,52],28:[30,51],29:[29,53]}
proposals = []


def component(mask, area_min=1):
    labels, count = label(mask)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    if not count or sizes.max() < area_min:
        return None
    return labels == int(sizes.argmax())


def point(mask, mode='interior'):
    ys, xs = np.where(mask)
    assert len(xs)
    distance = distance_transform_edt(mask)
    y, x = np.unravel_index(distance.argmax(), distance.shape)
    return [int(x), int(y)]


for row in index['frames']:
    path = HERE / row['input']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    a = np.array(Image.open(path).convert('RGBA'))
    rgb = a[:, :, :3].astype(int)
    r, g, b = [rgb[:, :, i] for i in range(3)]
    ygrid, xgrid = np.indices(r.shape)
    opaque = a[:, :, 3] >= 240
    white = opaque & (np.min(rgb, axis=2) >= 200) & ((np.max(rgb, axis=2)-np.min(rgb, axis=2)) <= 35)
    hat = component(white & (ygrid < 22), 5)
    assert hat is not None
    hy, hx = np.where(hat)
    gold = component(opaque & (r >= 140) & (g >= 80) & (b <= g*.30) & (r > g)
                     & (ygrid <= int(hy.max())+7) & (xgrid >= hx.min()-3) & (xgrid <= hx.max()+5), 2)
    brown = opaque & (r >= 35) & (r <= 145) & (g >= 22) & (g <= 112) & (b <= 90) & (r > g+5) & (g > b+3)
    hair = component(brown & (ygrid >= hy.max()+2) & (ygrid <= 50), 8)
    shorts = component(white & (ygrid >= 62) & (ygrid <= 108), 5)
    cap_ink = opaque & (np.max(rgb, axis=2) <= 60) & (ygrid >= hy.min()) & (ygrid <= hy.max()) & (xgrid >= hx.min()) & (xgrid <= hx.max())
    selections = [('hat-white', hat), ('hat-gold', gold), ('hair-or-beard', hair), ('shorts-white', shorts), ('cap-ink', cap_ink)]
    if row['frame'] not in rear:
        eyes = component(white & (ygrid >= hy.max()+2) & (ygrid < 38), 1)
        assert eyes is not None, row['frame']
        ey, ex = np.where(eyes)
        eye_ink = opaque & (np.max(rgb, axis=2) <= 70) & (ygrid >= ey.min()-1) & (ygrid <= ey.max()+1) & (xgrid >= ex.min()-2) & (xgrid <= ex.max()+2)
        selections += [('eye-white', eyes), ('eye-ink', eye_ink)]
    landmarks = []
    for name, mask in selections:
        assert mask is not None and mask.any(), (row['frame'], name)
        xy = point(mask)
        landmarks.append(dict(role=name, xy=xy, rgba=a[xy[1], xy[0]].tolist()))
    # A brighter, still visibly brown interior landmark probes color classes
    # close to the correction boundary instead of checking only near-black ink.
    hair_interior = hair & (distance_transform_edt(hair) >= 1.4)
    if hair_interior.any():
        iy, ix = np.where(hair_interior)
        selected = np.argmax(r[iy, ix])
        xy = [int(ix[selected]), int(iy[selected])]
        if xy not in [p['xy'] for p in landmarks]:
            landmarks.append(dict(role='hair-brown-highlight', xy=xy, rgba=a[xy[1], xy[0]].tolist()))
    if row['frame'] in chest:
        xy = chest[row['frame']]
        landmarks.append(dict(role='chest-hair', xy=xy, rgba=a[xy[1],xy[0]].tolist()))
    proposals.append(dict(frame=row['frame'], input=row['input'], input_sha256=row['sha256'], canvas=row['canvas'], landmarks=landmarks,
                          hidden_roles=['eye-white','eye-ink'] if row['frame'] in rear else []))

font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 17)
small = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 14)
colors = ['#48e7ff','#fff245','#8af786','#fa9df4','#ff7979','#ffffff','#bbbbff','#00ff97','#ffad00']
for group in range(7):
    selected = proposals[group*4:group*4+4]
    sheet = Image.new('RGB', (2160, 1100), '#29333a')
    draw = ImageDraw.Draw(sheet)
    for col, entry in enumerate(selected):
        im = Image.open(HERE / entry['input']).convert('RGBA')
        scale = 5
        ox, oy = col*540+20, 40
        sheet.paste(im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST),(ox,oy),im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST))
        draw.text((ox,10),f"{entry['frame']:03} {im.width}x{im.height}",font=font,fill='white')
        for tick in range(0,im.width,10):
            draw.text((ox+tick*scale,oy+im.height*scale+4),str(tick),font=small,fill='#acbdc8')
        for number, p in enumerate(entry['landmarks']):
            x, y = p['xy']
            cx, cy = ox+x*scale, oy+y*scale
            color = colors[number]
            draw.rectangle((cx-1,cy-1,cx+5,cy+5),outline=color,width=1)
            draw.text((cx+7,cy-5),str(number+1),font=small,fill=color)
            draw.text((ox,840+number*28),f"{number+1} {p['role']} {p['xy']}",font=small,fill=color)
    sheet.save(OUT/f'proposed-{group}.png')
(OUT/'proposals.json').write_text(json.dumps(proposals,indent=2)+'\n',encoding='utf-8')
print('Prepared28 independent appearance proposals and7 diagnostic sheets; no skin-correction code imported.')
