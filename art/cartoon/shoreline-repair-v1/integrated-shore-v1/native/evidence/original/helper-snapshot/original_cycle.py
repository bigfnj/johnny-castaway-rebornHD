"""Authentic source-asset wave cycle in the port, with original clovers."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import traceback
import zipfile
import capture as shared

ROOT=shared.ROOT
ARCHIVE_SHA='4301aad91184789727688cb3dac9ade7a8f04152cbde056a29396c9bfaeeac8f'
PAIR={'RESOURCE.MAP':'3d9ec330aab96bbe5a44ce34f5945703862e82b195088590b7adfef5d7345da7',
      'RESOURCE.001':'df9c2213f7c0abacf4e302cb53a476f9f220579c07ba350b167e351eed548eae'}
sha,save,require=shared.sha,shared.save,shared.require

def verify(text):
    require('STATE: seed=11 holiday=2 night=0 offset=0,0 low=0 raft=0 render=1280x960' in text,'original native state')
    require('DONE: native calls returned; cleanup complete' in text,'original cleanup returned')
    require('island backdrop: OCEAN02.SCR' in text,'original native backdrop')
    require('Art asset: ' not in text,'no replacement PNG loaded')
    bg=[list(map(int,r)) for r in re.findall(r'BG DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    require([r for r in bg if r[0]==0]==[[0,288,279,0,0,2,560,104]],'original ground native geometry')
    surfaces=[list(map(int,r)) for r in re.findall(r'GROUND SURFACE: x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)',text)]
    require(surfaces==[[576,558,560,104]],'original actual surface placement')
    props=[list(map(int,r)) for r in re.findall(r'PROP DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    require(props==[[1,333,286,0,0,2,240,94]],'original clover native geometry')
    for f,x,y,dx,dy,scale,w,h in (r for r in bg if 3<=r[0]<=11):
        expected=((270,306,144,58),(364,319,320,50),(518,303,144,64))[(f-3)//3]
        require((x,y,w,h)==expected and [dx,dy,scale]==[0,0,2],'original wave geometry')
    displays=[]
    for row in re.findall(r'DISPLAY: n=(\d+) ticks=(\d+) segment=(\d+) phases=(-?\d+),(-?\d+),(-?\d+),(-?\d+) johnny=(-?\d+),(\d+),(-?\d+),(-?\d+)',text):
        n,t,s,*values=map(int,row);displays.append({'ordinal':n,'ticks':t,'time_ms':t*20,'segment':s,'phases':values[:4],'johnny':values[4:]})
    require(displays and [r['ordinal'] for r in displays]==list(range(1,len(displays)+1)),'original contiguous displays')
    require(displays[0]['ticks']==0 and all(a['ticks']<=b['ticks'] for a,b in zip(displays,displays[1:])),'original observed timing')
    require(displays[0]['phases']==[3,7,9,-1],'original initial phase order')
    require({f for r in displays for f in r['phases'] if f>=0}==set(range(3,12)),'original complete wave phase coverage')
    calls=[list(map(int,r)) for r in re.findall(r'NATIVE CALL: segment=(\d+) args=(\d+),(\d+),(\d+),(\d+)',text)]
    returns=[list(map(int,r)) for r in re.findall(r'NATIVE RETURN: segment=(\d+) ticks=(\d+)',text)]
    require(calls==[[i+1,0,0,0,0] for i in range(20)] and [r[0] for r in returns]==list(range(1,21)),'original twenty real waits returned')
    return {'displays':displays,'native_calls':calls,'native_returns':returns,'background_draws':bg,
      'holiday_draws':props,'ground_surface_placement':surfaces,'duration_ms':displays[-1]['time_ms'],'source':'original source assets; port rendering; diagnostic palette'}

def one(exe,archive,folder):
    folder.mkdir();shutil.copyfile(archive,folder/'scrantic_data.zip');(folder/'profile').mkdir()
    command=[str(exe),'2','0','0','0','0','0','20']
    with (folder/'capture.log').open('wb') as log:
        result=subprocess.run(command,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=log,stderr=subprocess.STDOUT,timeout=60)
    require(result.returncode==0,'original process returned')
    text=(folder/'capture.log').read_text();report=verify(text);images={}
    for row in report['displays']:
        pixels=shared.codec.ppm(folder/f"display-{row['ordinal']:03}.ppm");digest=sha(pixels)
        if digest not in images:
            name=f"display-{row['ordinal']:03}.png";png=shared.codec.png_bytes(pixels);(folder/name).write_bytes(png)
            images[digest]={'file':name,'png_sha256':sha(png)}
        row.update(images[digest],pixels_sha256=digest)
    report.update(status='PASS',command=command,archive_sha256=sha(archive.read_bytes()),executable_sha256=sha(exe.read_bytes()),log_sha256=sha((folder/'capture.log').read_bytes()))
    save(folder/'report.json',report);print('PASS original '+folder.name,flush=True);return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--archive-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'fresh original output');a.output.mkdir(parents=True)
    try:
        require(sha(a.archive.read_bytes())==a.archive_sha256==ARCHIVE_SHA,'pinned authentic original package')
        with zipfile.ZipFile(a.archive) as z:
            require(not any(n.endswith('.png') and n.startswith(('data/hd/','data/styles/')) for n in z.namelist()),'original overrides absent')
            require({n:sha(z.read('data/'+n)) for n in PAIR}==PAIR,'supplied original resource pair')
        protected=shared.legacy.protected();driver=(shared.HERE/'driver.c').read_text()
        old='artStyleSelect("cartoon")';require(driver.count(old)==1,'single explicit reference style selector')
        adapted=driver.replace(old,'artStyleSelect("hd")');sources=a.output/'observer';sources.mkdir();(sources/'driver.c').write_text(adapted,encoding='utf-8',newline='\n')
        save(a.output/'inputs.json',{'archive_sha256':ARCHIVE_SHA,'supplied_resource_pair_sha256':PAIR,'source_observer_sha256':sha((shared.HERE/'driver.c').read_bytes()),
          'adapted_observer_sha256':sha((sources/'driver.c').read_bytes()),'exact_adaptation':'Only select HD instead of Cartoon; absent override PNGs force nearest2x authentic source assets.',
          'protected_sha256':protected,'capture_helper_sha256':sha(Path(__file__).read_bytes()),'shared_helper_sha256':sha((shared.HERE/'capture.py').read_bytes()),
          'scope':'Original artwork rendered by current native port. Diagnostic colors, not original-executable or palette parity. Original clovers are included. No phase forcing or art edits.'})
        shared.HERE=sources;exe=shared.build(a.output)
        first=one(exe,a.archive,a.output/'smoke')
        repeated=one(exe,a.archive,a.output/'repeat')
        require(first['displays']==repeated['displays'] and first['background_draws']==repeated['background_draws'],'exact original fresh-process repeat')
        text=(a.output/'smoke/capture.log').read_text();results=[]
        for name,bad,witness in (
          ('omitted_phase008',re.sub(r'(phases=\d+,)8(,)',r'\g<1>7\2',text),'original complete wave phase coverage'),
          ('wrong_clover_origin',text.replace('PROP DRAW: frame=1 x=333 ','PROP DRAW: frame=1 x=334 '),'original clover native geometry'),
          ('wrong_observed_timing',text.replace('DISPLAY: n=1 ticks=0 ','DISPLAY: n=1 ticks=1 '),'original observed timing')):
            try:verify(bad)
            except ValueError as e:require(str(e)=='integrated shore: '+witness,'named original negative:'+name);results.append({'name':name,'status':'FIRED','failure':str(e)})
            else:raise ValueError('survived original control:'+name)
        verify(text);require(shared.legacy.protected()==protected,'original capture source inputs unchanged')
        save(a.output/'negative-controls.json',{'status':'PASS','method':'Actual original native logs mutated in memory, explicit failure witnesses and restored positive. No output edits.','results':results})
        save(a.output/'summary.json',{'status':'PASS','smoke':'PASS','fresh_repeat':'PASS','displays':len(first['displays']),'duration_ms':first['duration_ms'],
          'archive_sha256':ARCHIVE_SHA,'phase_coverage':list(range(3,12)),'original_clovers':True,'negatives':len(results),'protected_inputs_unchanged':len(protected),
          'scope':'Source-art diagnostic cycle in port, not original executable. Exact native timing/phase/order; no source/art modifications.'})
    except Exception:
        save(a.output/'failure.json',{'traceback':traceback.format_exc()});raise
if __name__=='__main__':main()
