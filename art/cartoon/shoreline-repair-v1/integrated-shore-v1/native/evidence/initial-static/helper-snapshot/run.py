"""Hidden, isolated Linux/Xvfb capture using the existing pinned Docker image."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
IMAGE='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--phase',choices=('initial','full'),required=True);a=p.parse_args()
    output=a.output.resolve();output.relative_to(ROOT/'build/shoreline-repair-v1')
    if output.exists():raise ValueError('refusing existing native output: '+str(output))
    inputs={key:{'path':path.resolve().relative_to(ROOT).as_posix(),'sha256':sha(path)} for key,path in (('baseline',a.baseline),('candidate',a.candidate))}
    output.mkdir(parents=True);name='johnny-integrated-shore-'+uuid.uuid4().hex[:12]
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    command=['docker','run','--init','--rm','--name',name,'--network','none',
      '--mount','type=bind,source='+str(ROOT)+',target=/source,readonly',
      '--mount','type=bind,source='+str(output)+',target=/out',IMAGE,
      'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B',
      '/source/'+(HERE/'capture.py').relative_to(ROOT).as_posix(),'--output','/out/captures','--phase',a.phase]
    for key,value in inputs.items():command+=['--'+key,'/source/'+value['path'],'--'+key+'-sha256',value['sha256']]
    result=None;started=time.time()
    try:
        with (output/'launch.log').open('wb') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1500,creationflags=flags)
    finally:
        cleanup=subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30,creationflags=flags)
        remaining=subprocess.run(['docker','ps','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'],capture_output=True,timeout=15,creationflags=flags)
        record={'source_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,creationflags=flags).strip(),
          'image_id':IMAGE,'container_name':name,'inputs':inputs,'phase':a.phase,
          'capture_arguments':command[command.index('xvfb-run'):],'exit_code':result.returncode if result else None,
          'elapsed_seconds':time.time()-started,'no_surviving_task_container':remaining.returncode==0 and not remaining.stdout.strip(),
          'cleanup_exit_code':cleanup.returncode,'launcher_sha256':sha(Path(__file__)),
          'helpers_sha256':{q.name:sha(q) for q in HERE.iterdir() if q.suffix in ('.py','.c')}}
        (output/'launch.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    if result is None or result.returncode!=0 or not record['no_surviving_task_container']:raise RuntimeError('capture failed; retained '+str(output/'launch.log'))
    print('PASS isolated native capture: '+str(output))
if __name__=='__main__':main()
