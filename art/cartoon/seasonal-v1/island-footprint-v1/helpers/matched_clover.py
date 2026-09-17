from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import uuid
import zipfile
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
folder=OUT/'native/original-hd-clover';assert not folder.exists();folder.mkdir()
member='data/hd/BMP/HOLIDAY.BMP/001.png'
with zipfile.ZipFile(ROOT/'assets/scrantic_data.zip') as prod:raw=prod.read(member)
with zipfile.ZipFile(OUT/'original-full.zip') as source,zipfile.ZipFile(folder/'scrantic_data.zip','w',compression=zipfile.ZIP_DEFLATED) as target:
    for item in source.infolist():target.writestr(copy.copy(item),source.read(item.filename))
    target.writestr(member,raw)
(folder/'profile').mkdir()
name='johnny-footprint-match-'+uuid.uuid4().hex[:10]
image='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
cmd=['docker','run','--init','--rm','--name',name,'--network','none','--mount',f'type=bind,source={OUT},target=/out',
     '--workdir','/out/native/original-hd-clover','--env','HOME=/out/native/original-hd-clover/profile',image,
     'xvfb-run','-a','-s','-screen 0 1280x960x24','/out/native/seasonal_probe','2','0','0','0','hd','0']
flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
try:
    with (folder/'capture.log').open('wb') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=flags)
finally:
    subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30,creationflags=flags)
    status=subprocess.run(['docker','ps','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'],capture_output=True,timeout=15,creationflags=flags)
    assert status.returncode==0 and not status.stdout.strip()
assert r.returncode==0
text=(folder/'capture.log').read_text()
assert sorted(set(re.findall(r'Art asset: (\S+)',text)))==[member]
assert 'SEASONAL DRAW: frame=1 x=333 y=286 dx=0 dy=0 scale=2 canvas=240x94' in text
assert 'holiday=2 night=0 offset=0,0 lowTide=0 raft=0 render=1280x960' in text
assert 'island backdrop: OCEAN02.SCR' in text and 'SEASONAL DONE:' in text
codecpath=ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec=importlib.util.spec_from_file_location('codec',codecpath);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
pixels=codec.ppm(folder/'final.ppm');(folder/'final.png').write_bytes(codec.png_bytes(pixels))
original=Image.open(folder/'final.png').convert('RGB')
cartoon=Image.open(OUT/'native/cartoon/high/clover/final.png').convert('RGB')
whole=(536,236,1192,700);detail=(650,566,922,690)
for label,box,scale in [('island',whole,1),('clover-detail',detail,3)]:
    width=(box[2]-box[0])*scale;height=(box[3]-box[1])*scale
    sheet=Image.new('RGB',(width*2+12,height+42),(24,29,36))
    draw=ImageDraw.Draw(sheet)
    draw.text((8,12),'Original island + same HD clover',fill='white')
    draw.text((width+20,12),'Cartoon island + same HD clover',fill='white')
    for i,im in enumerate([original,cartoon]):
        crop=im.crop(box)
        if scale!=1:crop=crop.resize((width,height),Image.Resampling.NEAREST)
        sheet.paste(crop,(i*(width+12),42))
    sheet.save(OUT/f'matched-{label}.png')
record={'status':'PASS','source_resources':'Supplied original RESOURCE.MAP/.001; no original island/background/tree/Johnny overridePNG; original art rendered by the port, not the original executable.',
        'shared_hd_clover_member':member,'shared_hd_clover_sha256':sha(raw),
        'original_diagnostic_archive_sha256':sha((folder/'scrantic_data.zip').read_bytes()),
        'original_capture_sha256':sha((folder/'final.png').read_bytes()),
        'cartoon_capture_sha256':sha((OUT/'native/cartoon/high/clover/final.png').read_bytes()),
        'whole_crop_xyxy':whole,'detail_crop_xyxy':detail,'detail_scale':'integer nearest3',
        'owned_container_absent':True,'scope':'Matched high-tide same-origin render. Both panels use exact same HD clover PNG; diagnostic original palette is not original-executable color proof.'}
(OUT/'matched-clover.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('PASS matched original-island/Cartoon-island clover crops; owned container absent')
