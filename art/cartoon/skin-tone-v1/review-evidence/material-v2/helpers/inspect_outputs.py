from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3];HERE=ROOT/'art/cartoon/skin-tone-v1';OUT=Path(__file__).resolve().parent
EXPORT=ROOT/'build/skin-tone/export-v2'
sha=lambda b:hashlib.sha256(b).hexdigest()
landmarks=json.loads((HERE/'protected-landmarks-v2.json').read_bytes())
caps=json.loads((HERE/'protected-cap-polygons-v1.json').read_bytes())
recipe=json.loads((EXPORT/'recipe.json').read_bytes())
caprows={r['frame']:r for r in caps['frames']};exportrows={r['frame']:r for r in recipe['frames']}
results=[];images=[]
for row in landmarks['frames']:
    f=row['frame'];erow=exportrows[f];cap=caprows[f]
    with Image.open(HERE/row['input']) as im:before=im.convert('RGBA')
    with Image.open(EXPORT/erow['candidate_png']) as im:after=im.convert('RGBA')
    with Image.open(EXPORT/erow['mask']) as im:mask=im.convert('L')
    a=np.array(before);b=np.array(after);m=np.array(mask);w,h=before.size
    line=cap['lower_boundary_pixel_edges'];boundary=np.interp(np.arange(w)+.5,[p[0] for p in line],[p[1] for p in line]);cm=np.arange(h)[:,None]+.5<boundary[None,:]
    failures=[]
    for p in row['landmarks']:
        x,y=p['xy']
        if list(after.getpixel((x,y)))!=p['rgba']:failures.append(dict(role=p['role'],xy=p['xy'],expected=p['rgba'],actual=list(after.getpixel((x,y)))))
        if 'region_xywh' in p:
            x,y,cw,ch=p['region_xywh']
            if sha(after.crop((x,y,x+cw,y+ch)).tobytes())!=p['region_rgba_sha256']:failures.append(dict(role=p['role'],region=p['region_xywh']))
    results.append(dict(frame=f,input_hash_valid=sha((HERE/row['input']).read_bytes())==row['input_sha256'],output_hash_valid=sha((EXPORT/erow['candidate_png']).read_bytes())==erow['candidate_png_sha256'],canvas_equal=before.size==after.size,alpha_equal=bool(np.array_equal(a[:,:,3],b[:,:,3])),outside_mask_equal=bool(np.array_equal(a[m==0],b[m==0])),cap_rgba_equal=bool(np.array_equal(a[cm],b[cm])),cap_mask_empty=bool(not(m[cm]>0).any()),protected_failures=failures,changed_pixels=int(np.any(a!=b,axis=2).sum())))
    alpha=np.array(before.getchannel('A'));ys,xs=np.where(alpha[:40]>0);lo=max(0,int(xs.min())-1);hi=min(w,int(xs.max())+2)
    images.append((f,before.crop((lo,0,hi,40)),after.crop((lo,0,hi,40)),mask.crop((lo,0,hi,40))))
font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
for g in range(7):
    sheet=Image.new('RGB',(1480,1480),'#3a4550');d=ImageDraw.Draw(sheet)
    for n,(f,old,new,mask) in enumerate(images[g*4:g*4+4]):
        oy=n*365+30
        for col,(im,label) in enumerate([(old,'original'),(new,'corrected'),(mask,'skin mask')]):
            ox=col*490+20;d.text((ox,oy-24),f'{f:03} {label}',font=font,fill='white');large=im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST)
            sheet.paste(large,(ox,oy),large if large.mode=='RGBA' else None)
    sheet.save(OUT/f'head-mask-check-{g}.png')
document=dict(scope='Independent landmark/region/canvas/cap readback and visual head-mask review preparation; no corrector module imported.',recipe_sha256=sha((EXPORT/'recipe.json').read_bytes()),landmarks_sha256=sha((HERE/'protected-landmarks-v2.json').read_bytes()),cap_annotations_sha256=sha((HERE/'protected-cap-polygons-v1.json').read_bytes()),frames=results)
(OUT/'export-v2-readback.json').write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(frames=len(results),protected_failures=sum(len(r['protected_failures']) for r in results),nonidentity=sum(r['changed_pixels']>0 for r in results),geometry_and_mask_failures=[r['frame'] for r in results if not all(r[k] for k in ['input_hash_valid','output_hash_valid','canvas_equal','alpha_equal','outside_mask_equal','cap_rgba_equal','cap_mask_empty'])])))
