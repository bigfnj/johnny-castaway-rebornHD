import argparse,hashlib,json,subprocess,time,uuid,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
IMAGE='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=argparse.ArgumentParser();p.add_argument('--tag',type=int,required=True);p.add_argument('--seed',type=int,default=11);p.add_argument('--label',required=True);p.add_argument('--style',choices=('hd','cartoon'),default='hd');a=p.parse_args()
out=HERE/a.label
if out.exists():raise ValueError('fresh output required')
source=ROOT/'assets/scrantic_data.zip';original=HERE/'original-only.zip'
if not original.exists():
 with zipfile.ZipFile(source) as z,zipfile.ZipFile(original,'w',zipfile.ZIP_DEFLATED) as target:
  kept={}
  for row in z.infolist():
   if row.filename.startswith(('data/hd/','data/styles/')):continue
   raw=z.read(row.filename);target.writestr(row,raw);kept[row.filename]=sha(raw)
 save(HERE/'archive.json',{'source':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source.read_bytes()),'diagnostic_sha256':sha(original.read_bytes()),'method':'Private archive omits data/hd and data/styles so unchanged native loader decodes original resources at scale1. No image or original payload changes.','retained_payloads_sha256':kept})
out.mkdir();flags=getattr(subprocess,'CREATE_NO_WINDOW',0);container='johnny-fish-'+uuid.uuid4().hex[:12]
cmd=['docker','run','--init','--rm','--name',container,'--network','none','--mount','type=bind,source='+str(ROOT)+',target=/source,readonly','--mount','type=bind,source='+str(out)+',target=/out',IMAGE,'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/source/build/fish-scene-review/capture.py','--tag',str(a.tag),'--seed',str(a.seed)]
started=time.time();result=None
cmd.extend(['--style',a.style])
try:
 with (out/'launch.log').open('wb') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=flags,timeout=240)
finally:
 subprocess.run(['docker','rm','-f',container],capture_output=True,creationflags=flags,timeout=30)
 left=subprocess.run(['docker','ps','-a','--filter','name=^/'+container+'$','--format','{{.ID}}'],capture_output=True,creationflags=flags,timeout=15)
 save(out/'launch.json',{'command':cmd,'image':IMAGE,'source_head':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,creationflags=flags).strip(),'returncode':result.returncode if result else None,'elapsed_seconds':time.time()-started,'no_surviving_task_container':left.returncode==0 and not left.stdout.strip(),'source_archive_unchanged':sha(source.read_bytes())==json.loads((HERE/'archive.json').read_bytes())['source_sha256'],'helpers_sha256':{n:sha((HERE/n).read_bytes()) for n in ('driver.c','capture.py','run.py')}})
if result is None or result.returncode:raise RuntimeError('capture failed; inspect launch.log')
print(out)
