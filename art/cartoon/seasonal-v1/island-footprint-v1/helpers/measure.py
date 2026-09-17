from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import statistics

HERE=Path(__file__).resolve().parent
images=HERE/'images'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
origin=(576,558)
def opened(name):return Image.open(images/name).convert('RGBA')
original=opened('original-BACKGRND-000.png').resize((560,104),Image.Resampling.NEAREST)
hd=opened('hd-BACKGRND-000.png')
cartoon=opened('cartoon-BACKGRND-000.png')
def mask(image,threshold=128,legacy=False):
    return [[image.getpixel((x,y))[3]>=threshold and (not legacy or image.getpixel((x,y))[:3]!=(168,0,168)) for x in range(image.width)] for y in range(image.height)]
masks={'original':mask(original),'hd':mask(hd,legacy=True),'cartoon':mask(cartoon)}
def lower(m,x):
    ys=[y for y,row in enumerate(m) if 0<=x<len(row) and row[x]]
    return max(ys) if ys else None
def facts(m):
    points=[(x,y) for y,row in enumerate(m) for x,yes in enumerate(row) if yes]
    return {'area_pixels':len(points),'bounds_xyxy':[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1]}
clover=opened('original-HOLIDAY-001.png')
green=(0,168,0,255);gray=(128,128,128,255)
roots=[]
for x in range(clover.width):
    for y in range(clover.height-1):
        if clover.getpixel((x,y))==green and clover.getpixel((x,y+1))==gray:
            roots.append((x,y))
# Adjacent green pixels terminating at the same ground mark identify one endpoint.
groups=[]
for point in sorted(roots):
    if groups and point[0]==groups[-1][-1][0]+1 and abs(point[1]-groups[-1][-1][1])<=1:
        groups[-1].append(point)
    else:groups.append([point])
root_points=[(round(statistics.mean(x for x,y in group)),max(y for x,y in group)) for group in groups]
scene={}
for kind in ('original','hd','cartoon'):
    for tide in ('high','low'):
        im=Image.open(HERE/'native'/kind/tide/'none/final.png').convert('RGB')
        scene[kind,tide]=im
def warm(kind,rgb):
    r,g,b=rgb
    if kind in ('original','hd'):
        return r>=120 and g>=120 and b<128
    return r>=95 and g>=65 and r>b*1.25 and g>b*1.08
def shore(kind,tide,x):
    im=scene[kind,tide]
    ys=[y for y in range(558,730) if warm(kind,im.getpixel((x,y)))]
    return max(ys) if ys else None
rows=[]
for x,y in root_points:
    # Original pixels become2x2 blocks; use their left x and bottom y center-row.
    wx,wy=666+x*2,572+y*2+1
    static={k:lower(m,wx-origin[0])+origin[1] if lower(m,wx-origin[0]) is not None else None for k,m in masks.items()}
    native={t:{k:shore(k,t,wx) for k in ('original','hd','cartoon')} for t in ('high','low')}
    rows.append({'source_xy':[x,y],'world_hd_stem_bottom':[wx,wy],
                 'base_sprite_lower_alpha128_y':static,'native_lower_sand_y':native,
                 'high_tide_cartoon_retreat_hd':native['high']['original']-native['high']['cartoon'],
                 'base_only_cartoon_retreat_hd':static['original']-static['cartoon'],
                 'high_tide_clearance_hd':{k:native['high'][k]-wy for k in ('original','hd','cartoon')}})
# Fixed original root points make the distinction between base silhouette and
# whole native sand coverage inspectable, without classifying foliage as ground.
annotated=clover.resize((960,376),Image.Resampling.NEAREST)
draw=ImageDraw.Draw(annotated)
for i,(x,y) in enumerate(root_points):
    draw.ellipse((x*8-4,y*8-4,x*8+12,y*8+12),outline=(255,0,255,255),width=2)
    draw.text((x*8+5,y*8-14),str(i+1),fill=(255,255,255,255))
annotated.save(images/'clover-stem-endpoints.png')
overlay=Image.new('RGBA',(560,104),(0,0,0,0))
for y in range(104):
    for x in range(560):
        a,b=masks['original'][y][x],masks['cartoon'][y][x]
        if a or b:overlay.putpixel((x,y),(215,215,215,255) if a and b else (255,0,100,255) if a else (0,190,255,255))
overlay.resize((1120,208),Image.Resampling.NEAREST).save(images/'sand-alpha-overlay-nearest2.png')
samples=[]
for label,x in [('pumpkin-center',860),('tree-center',856),('clover-left',680),('clover-middle',784),('clover-right',894)]:
    samples.append({'name':label,'world_x':x,'native_high_sand_bottom':{k:shore(k,'high',x) for k in ('original','hd','cartoon')}})
report={'scope':'Column-wise lower sand geometry. Original source PNGs derive from hash-bound supplied-original dump. Native captures use the supplied original resource pair for original and current production forHD/Cartoon. No original executable or original palette-parity claim.',
        'inputs_sha256':{p.name:sha(p) for p in [images/'original-BACKGRND-000.png',images/'hd-BACKGRND-000.png',images/'cartoon-BACKGRND-000.png',images/'original-HOLIDAY-001.png']},
        'base_canvas':[560,104],'base_scene_origin_hd':list(origin),'mask_definition':'original alpha255/HD alpha>=128 excluding legacy magenta/Cartoon alpha>=128; purely diagnostic, no edited production alpha',
        'base_masks':{k:facts(m) for k,m in masks.items()},'original_hd_base_alpha_identical':masks['original']==masks['hd'],
        'clover_endpoints_method':'Every source green pixel immediately above a gray ground/shadow pixel; adjacent same-level endpoints grouped. Visually inspected annotated source. These are visible stem endpoints, not inferred botanical attachment.',
        'native_sand_definition':'original/HD r>=120,g>=120,b<128 (yellow shades); Cartoon r>=95,g>=65,r>1.25b,g>1.08b (warm sand). Lower border/foam not counted. Sampling no-holiday scene avoids green props. Deterministic color separation here, not a universal material classifier.',
        'clover_stem_endpoints':rows,'selected_native_columns':samples,
        'high_tide_stem_samples_below_sand':{k:sum(row['high_tide_clearance_hd'][k]<0 for row in rows) for k in ('original','hd','cartoon')},
        'max_composed_retreat_hd':max(row['high_tide_cartoon_retreat_hd'] for row in rows),
        'max_base_retreat_hd':max(row['base_only_cartoon_retreat_hd'] for row in rows)}
(HERE/'measurements.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'base_masks':report['base_masks'],'roots':len(rows),'below_sand':report['high_tide_stem_samples_below_sand'],'max_composed_retreat_hd':report['max_composed_retreat_hd'],'max_base_retreat_hd':report['max_base_retreat_hd'],'samples':samples},indent=2))
