import argparse, hashlib, importlib.util, json, os, shutil, subprocess
from pathlib import Path
ROOT=Path('/source')
HERE=ROOT/'build/fish-scene-review'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
p=argparse.ArgumentParser();p.add_argument('--tag',type=int,required=True);p.add_argument('--seed',type=int,default=11);p.add_argument('--style',choices=('hd','cartoon'),default='hd');a=p.parse_args()
out=Path('/out');shared_path=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/capture.py'
spec=importlib.util.spec_from_file_location('retained',shared_path);shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
shared.HERE=HERE
exe=shared.build(out)
run=out/'scene';run.mkdir();(run/'profile').mkdir()
shutil.copyfile(HERE/'original-only.zip' if a.style=='hd' else ROOT/'assets/scrantic_data.zip',run/'scrantic_data.zip')
cmd=[str(exe),str(a.tag),str(a.seed),a.style]
with (run/'capture.log').open('wb') as log:
 result=subprocess.run(cmd,cwd=run,env=dict(os.environ,HOME=str(run/'profile')),stdout=log,stderr=subprocess.STDOUT,timeout=90)
save(out/'run.json',{'returncode':result.returncode,'command':cmd,'archive_sha256':sha(run/'scrantic_data.zip'),'executable_sha256':sha(exe),'driver_sha256':sha(HERE/'driver.c'),'shared_build_helper':str(shared_path),'shared_build_helper_sha256':sha(shared_path)})
if result.returncode: raise RuntimeError('native process failed')
