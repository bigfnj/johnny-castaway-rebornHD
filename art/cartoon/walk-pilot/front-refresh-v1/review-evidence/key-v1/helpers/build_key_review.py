import hashlib
import io
import json
import base64
import zipfile
from pathlib import Path
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[7]
ART = ROOT / 'art/cartoon/walk-pilot/front-refresh-v1'
OUT = ART / 'review-evidence/key-v1'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
png = lambda im: encode(im)

def encode(im):
    buffer=io.BytesIO()
    im.save(buffer,format='PNG',compress_level=9)
    return buffer.getvalue()

source = Image.open(ART / '028-foot-fit-v3.png').convert('RGBA')
alpha = source.getchannel('A')
top = alpha.point(lambda n: 255 if n>=128 else 0).getbbox()[1]
xs=[x for x in range(source.width) if alpha.getpixel((x,top))>=128]
cap=[(min(xs)+max(xs)+1)/2,top]
tx,ty=17.5-cap[0]*.1,.25-cap[1]*.1
PAD=8
size=(80,160)
high=source.convert('RGBa').transform((size[0]*8,size[1]*8),Image.Transform.AFFINE,
    (1/.8,0,-(tx+PAD)/.1,0,1/.8,-(ty+PAD)/.1),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
candidate=high.resize(size,Image.Resampling.LANCZOS).convert('RGBA')
original=Image.open(ART/'reference/028-original-native.png').convert('RGBA')
original_canvas=Image.new('RGBA',size)
original_canvas.paste(original.resize((64,144),Image.Resampling.NEAREST),(PAD,PAD))
archive_path=ROOT/'assets/scrantic_data.zip'
with zipfile.ZipFile(archive_path) as archive:
    approved_raw=archive.read('data/styles/cartoon/BMP/JOHNWALK.BMP/028.png')
    approved_im=Image.open(io.BytesIO(approved_raw)).convert('RGBA')
approved=Image.new('RGBA',size)
approved.paste(approved_im,(PAD,PAD))
images={'original':original_canvas,'approved':approved,'candidate':candidate}
labels={'original':'Original pose','approved':'Current Cartoon','candidate':'New 028 draft'}
encoded={key:png(value) for key,value in images.items()}
for key,value in encoded.items():
    (OUT/(key+'.png')).write_bytes(value)
bounds=alpha.point(lambda n:255 if n>=8 else 0).getbbox()
mapped=[(bounds[0]+.5)*.1+tx,(bounds[1]+.5)*.1+ty,(bounds[2]-.5)*.1+tx,(bounds[3]-.5)*.1+ty]
filtered=candidate.getchannel('A').point(lambda n:255 if n>=8 else 0).getbbox()
report={'scope':'Static pose comparison only; not animation or production approval.',
 'source':'028-foot-fit-v3.png','source_sha256':sha((ART/'028-foot-fit-v3.png').read_bytes()),
 'source_canvas':list(source.size),'pillow_version':PIL.__version__,
 'scale':.1,'cap_raw':cap,'cap_target_hd':[17.5,.25], 'affine_forward':[.1,0,tx,0,.1,ty],
 'runtime_canvas':[64,144],'preview_padding_hd':PAD,
 'filter':'premultiplied RGBa; 8x affine BICUBIC; LANCZOS downsample; RGBA PNG compress9',
 'source_alpha8_centers_hd':mapped,'source_alpha8_centers_fit':mapped[0]>=0 and mapped[1]>=0 and mapped[2]<64 and mapped[3]<144,
 'filtered_alpha8_bounds_hd':[filtered[0]-PAD,filtered[1]-PAD,filtered[2]-PAD,filtered[3]-PAD],
 'archive_sha256':sha(archive_path.read_bytes()),'approved_028_png_sha256':sha(approved_raw),
 'review_pngs':{key:sha(value) for key,value in encoded.items()}}
cards=''.join('<article><h2>'+labels[key]+'</h2><canvas id="'+key+'" width="320" height="640"></canvas></article>' for key in images)
data={key:'data:image/png;base64,'+base64.b64encode(value).decode('ascii') for key,value in encoded.items()}
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Front walk: frame 028</title>
<style>*{box-sizing:border-box}body{margin:0;padding:20px;background:#16222b;color:#f3f5f6;font:16px system-ui,sans-serif}main{max-width:1250px;margin:auto}h1{font-size:26px;margin:0 0 8px}p{line-height:1.45;margin:8px 0 14px;color:#cbd7de}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}article{background:#223440;border:1px solid #4c626e;border-radius:12px;padding:10px;text-align:center}h2{font-size:18px;margin:3px 0 10px}canvas{display:block;margin:auto;max-width:100%;height:min(61vh,640px);width:auto;background:#cbd5d9;border-radius:7px}button{font:inherit;padding:8px 16px;border:1px solid #92afb9;border-radius:7px;background:#dce8ee;color:#122129;margin:0 8px 14px 0;cursor:pointer}button[aria-pressed=true]{background:#71d4ba}small{display:block;margin-top:14px;color:#b9cbd4}@media(max-width:700px){body{padding:10px}section{gap:6px}article{padding:5px}h2{font-size:14px}canvas{height:auto;width:100%}}</style>
<main><h1>Front walk: frame 028</h1><p>Look at how the nearer hip connects to the forward leg, then compare the shorts and the heel-first step. The new draft is on the right.</p>
<button id="full" aria-pressed="true">Whole pose</button><button id="feet" aria-pressed="false">Shorts and feet</button><section>'''+cards+'''</section>
<small>Original colors are a diagnostic palette. Its gray ground shadow is part of the reference. This is a still-pose review; the full walking sequence and island arrival follow after the pose is settled.</small></main>
<script>const sources='''+json.dumps(data)+'''; const loaded={};let crop=false;
function draw(){for(const key of Object.keys(loaded)){const c=document.getElementById(key),ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);ctx.imageSmoothingEnabled=false;if(crop)ctx.drawImage(loaded[key],0,73,80,87,0,0,320,640);else ctx.drawImage(loaded[key],0,0,320,640);}document.getElementById('full').setAttribute('aria-pressed',String(!crop));document.getElementById('feet').setAttribute('aria-pressed',String(crop));}
window.reviewReady=Promise.all(Object.entries(sources).map(([key,url])=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{loaded[key]=im;resolve()};im.onerror=reject;im.src=url}))).then(draw);
document.getElementById('full').onclick=()=>{crop=false;draw()};document.getElementById('feet').onclick=()=>{crop=true;draw()};</script></html>'''
# Keep crop aspect ratio; a close-up must not distort the limbs.
html=html.replace('0,0,320,640);else','0,0,320,348);else')
html=html.replace("ctx.clearRect(0,0,c.width,c.height);", "c.height=crop?348:640;ctx.clearRect(0,0,c.width,c.height);")
html=html.replace("function draw(){", "function draw(){document.body.classList.toggle('cropped',crop);")
html=html.replace('max-width:100%;height:min(61vh,640px);width:auto;', 'width:min(100%,30vh);height:auto;')
html=html.replace('button{font:inherit;', 'body.cropped canvas{width:min(100%,55vh)}button{font:inherit;')
(OUT/'review.html').write_text(html,encoding='utf-8',newline='\n')
report['review_html_sha256']=sha((OUT/'review.html').read_bytes())
(OUT/'recipe.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))

