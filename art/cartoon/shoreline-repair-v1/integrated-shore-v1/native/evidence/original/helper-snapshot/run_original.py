"""Run the original source cycle in the existing hidden Linux/Xvfb environment."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import uuid
from run import ROOT,HERE,IMAGE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    output=a.output.resolve();output.relative_to(ROOT/'build/shoreline-repair-v1')
    if output.exists():raise ValueError('preserve original capture output')
    source=a.archive.resolve();source.relative_to(ROOT);digest=sha(source);output.mkdir(parents=True)
    name='johnny-original-wave-'+uuid.uuid4().hex[:12];flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    command=['docker','run','--init','--rm','--name',name,'--network','none',
      '--mount','type=bind,source='+str(ROOT)+',target=/source,readonly','--mount','type=bind,source='+str(output)+',target=/out',IMAGE,
      'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B',
      '/source/'+(HERE/'original_cycle.py').relative_to(ROOT).as_posix(),'--archive','/source/'+source.relative_to(ROOT).as_posix(),
      '--archive-sha256',digest,'--output','/out/captures']
    result=None;started=time.time()
    try:
        with (output/'launch.log').open('wb') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=360,creationflags=flags)
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30,creationflags=flags)
        left=subprocess.run(['docker','ps','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'],capture_output=True,timeout=15,creationflags=flags)
        record={'image_id':IMAGE,'container_name':name,'archive_sha256':digest,'archive':source.relative_to(ROOT).as_posix(),
          'arguments':command[command.index('xvfb-run'):],'exit_code':result.returncode if result else None,'elapsed_seconds':time.time()-started,
          'no_surviving_task_container':left.returncode==0 and not left.stdout.strip(),'helper_sha256':sha(Path(__file__)),
          'source_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,creationflags=flags).strip()}
        (output/'launch.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    if result is None or result.returncode or not record['no_surviving_task_container']:raise RuntimeError('original capture failed; see '+str(output/'launch.log'))
    print('PASS original source cycle: '+str(output))
if __name__=='__main__':main()
