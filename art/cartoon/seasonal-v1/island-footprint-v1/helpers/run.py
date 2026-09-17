from pathlib import Path
import json
import subprocess
import uuid

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
name='johnny-island-footprint-'+uuid.uuid4().hex[:10]
image='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
cmd=['docker','run','--init','--rm','--name',name,'--network','none','--mount',f'type=bind,source={ROOT},target=/source,readonly',
     '--mount',f'type=bind,source={OUT},target=/out',image,'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/out/capture.py']
flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
try:
    with (OUT/'launch.log').open('wb') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=flags)
finally:
    subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30,creationflags=flags)
    status=subprocess.run(['docker','ps','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'],capture_output=True,timeout=15,creationflags=flags)
    assert status.returncode==0 and not status.stdout.strip(),'owned container cleanup'
    (OUT/'launch.json').write_text(json.dumps({'container':name,'image_id':image,'owned_container_absent':True})+'\n',encoding='utf-8')
assert r.returncode==0,'retained launch.log'
print('PASS island footprint diagnostic captures; owned container absent')
