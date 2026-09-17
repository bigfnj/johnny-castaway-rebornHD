"""Versioned native static-ground/foam observer; no forced wave phases."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import traceback
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
LEGACY=ROOT/'art/cartoon/seasonal-v1/native/capture.py'
LEGACY_SHA='5a325d6b3db2ae3e7362ede1144977c977542c668596bbfb24b1e0a5bcdfe730'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def require(ok,label):
    if not ok: raise ValueError('integrated shore: '+label)
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
require(sha(LEGACY.read_bytes())==LEGACY_SHA,'frozen seasonal helper identity')
legacy=load(LEGACY,'integrated_seasonal')
require(sha(legacy.CODEC.read_bytes())==legacy.CODEC_SHA,'frozen capture codec identity')
codec=load(legacy.CODEC,'integrated_codec')
FRAMES=(0,*range(3,12))
APPROVED_GROUND_SHA='22b426952abb1877e7c77111da0f4f0826dc86ff7a993c4390156c0f55166d9d'
PROP_HASHES={f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png':digest for i,digest in enumerate((
 '1f2ac522476d98afcade5f128c12c0c80f6993b871b611498971f23a44eabf79',
 'e6327c07e85d7d8610ed45a502efd283fe1c79fe5850c790bb2808a2ee02176e',
 '7d9c5406f8275a1af9c9369305575a24d807ac5b38200e6ad17913a0a8400265',
 '03ab2762a2924aa39431cf9940555da96ed76bd20043ef73eb130a61ae879740'))}
def member(frame): return f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
def snapshot_helpers(output):
    folder=output/'helper-snapshot';folder.mkdir()
    for source in HERE.iterdir():
        if source.suffix in ('.py','.c'):(folder/source.name).write_bytes(source.read_bytes())
    return {source.name:sha(source.read_bytes()) for source in folder.iterdir()}
DAY={name:[holiday,0,0,0,0,0,1] for holiday,name in ((0,'none'),(1,'pumpkin'),(2,'clover'),(3,'tree'),(4,'banner'))}
MOTION={
 'high_none':[0,0,0,0,0,0,20], 'high_clover':[2,0,0,0,0,0,20],
 'low_none':[0,0,0,0,1,0,24], 'low_clover':[2,0,0,0,1,0,24],
 'night_shift_clover':[2,1,-80,20,0,0,20],
 'johnny_front':[0,0,0,0,0,1,1], 'johnny_rear':[0,0,0,0,0,2,1]}

def package_pair(baseline,candidate):
    metadata=legacy.selected_archive(baseline)
    require(metadata['holiday_members_sha256']==PROP_HASHES and set(metadata['new_cartoon_members'])==set(PROP_HASHES),'exact full-size V5 props')
    with zipfile.ZipFile(baseline) as z: before={n:sha(z.read(n)) for n in z.namelist()}
    with zipfile.ZipFile(candidate) as z:
        require(len(z.namelist())==len(set(z.namelist())),'candidate duplicate members')
        after={n:sha(z.read(n)) for n in z.namelist()}
        require(set(before)==set(after),'candidate member set')
        require({n for n in before if before[n]!=after[n]}=={member(f) for f in FRAMES},'only ten ground/foam changes')
        require(after[member(0)]==APPROVED_GROUND_SHA,'exact approved static ground retained')
        sizes={str(f):list(struct.unpack('>II',z.read(member(f))[16:24])) for f in FRAMES}
        require(sizes['0']==[640,180],'registered ground canvas640x180')
        require(all(sizes[str(f)]==[144,58] for f in (3,4,5)) and all(sizes[str(f)]==[144,64] for f in (9,10,11)),'side foam canvases')
        center=sizes['6'];require(center in ([320,50],[384,256]) and all(sizes[str(f)]==center for f in (7,8)),'uniform registered center foam canvases')
    return {'baseline_sha256':sha(baseline.read_bytes()),'candidate_sha256':sha(candidate.read_bytes()),
      'member_count':len(before),'unchanged_members':len(before)-10,'holiday_members_sha256':PROP_HASHES,
      'changed_members':{member(f):{'before':before[member(f)],'after':after[member(f)]} for f in FRAMES},'candidate_canvases':sizes}

def build(output):
    text=(ROOT/'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n',1)[1].split('\n)',1)[0]
    names=[line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    names.remove('src/engine/jc_reborn.c');names.append('platform/platform_linux.c')
    exe=output/'integrated_shore_probe'
    wrappers=('grDrawSprite','grDrawSpriteFlip','platformBlitSurface','eventsWaitTick','platformUpdateWindow')
    command=['gcc','-std=gnu11','-O2','-g','-Wall','-Wextra','-DPLATFORM_LINUX',
      '-I/source/src/engine','-I/source/src/data','-I/source/platform','-I/source/third_party/miniz',
      str(HERE/'driver.c'),*[str(ROOT/n) for n in names],*['-Wl,--wrap='+n for n in wrappers],
      '-lX11','-lasound','-lpthread','-lm','-o',str(exe)]
    start=time.time_ns();result=subprocess.run(command,capture_output=True,timeout=180)
    (output/'build.stdout.txt').write_bytes(result.stdout);(output/'build.stderr.txt').write_bytes(result.stderr)
    require(result.returncode==0 and exe.is_file() and exe.stat().st_mtime_ns>=start,'fresh observer build')
    save(output/'build.json',{'command':command,'started_ns':start,'mtime_ns':exe.stat().st_mtime_ns,
      'executable_sha256':sha(exe.read_bytes()),'driver_sha256':sha((HERE/'driver.c').read_bytes()),
      'compiled_source_sha256':{n:sha((ROOT/n).read_bytes()) for n in names},
      'compiler':subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]})
    return exe

def verify_log(text,args,candidate,canvases):
    holiday,night,ox,oy,low,mode,waits=args
    require(f'STATE: seed=11 holiday={holiday} night={night} offset={ox},{oy} low={low} raft=0 render=1280x960' in text,'actual native state')
    require('DONE: native calls returned; cleanup complete' in text,'native cleanup returned')
    backdrop='NIGHT.SCR' if night else 'OCEAN02.SCR'
    require('island backdrop: '+backdrop in text,'selected native backdrop')
    bg=[list(map(int,r)) for r in re.findall(r'BG DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    base=[r for r in bg if r[0]==0]
    size=[640,180] if candidate else [560,104]
    require(base==[[0,288,279,ox,oy,2,*size]],'logical ground origin and selected canvas')
    actual=[list(map(int,r)) for r in re.findall(r'GROUND SURFACE: x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)',text)]
    origin=[540+ox*2,548+oy*2] if candidate else [576+ox*2,558+oy*2]
    require(actual==[[*origin,*size]],'actual ground surface placement')
    expected_props=[]
    if holiday:
        frame,x,y,w,h=legacy.HOLIDAYS[holiday][1];expected_props=[[frame,x,y,ox,oy,2,w,h]]
    props=[list(map(int,r)) for r in re.findall(r'PROP DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    require(props==expected_props,'full-size holiday origin/canvas')
    wave_rows=[r for r in bg if 3<=r[0]<=11]
    for f,x,y,dx,dy,scale,w,h in wave_rows:
        family=(f-3)//3;expected=((270,306),(364,319),(518,303))[family]
        wh=canvases[str(f)] if candidate else ([144,58],[320,50],[144,64])[family]
        require((x,y)==expected and [dx,dy,scale,w,h]==[ox,oy,2,*wh],'actual high-wave origin/canvas')
    surfaces=[list(map(int,r)) for r in re.findall(r'WAVE SURFACE: frame=(\d+) x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)',text)]
    require(len(surfaces)==len(wave_rows),'every high-wave surface observed')
    for actual,row in zip(surfaces,wave_rows):
        f,x,y,dx,dy,scale,w,h=row
        offset=(-32,-90) if candidate and 6<=f<=8 and [w,h]==[384,256] else (0,0)
        require(actual==[f,(x+dx)*2+offset[0],(y+dy)*2+offset[1],w,h],'actual high-wave surface placement')
    displays=[]
    for row in re.findall(r'DISPLAY: n=(\d+) ticks=(\d+) segment=(\d+) phases=(-?\d+),(-?\d+),(-?\d+),(-?\d+) johnny=(-?\d+),(\d+),(-?\d+),(-?\d+)',text):
        n,t,segment,*tail=map(int,row)
        displays.append({'ordinal':n,'ticks':t,'time_ms':t*20,'segment':segment,'phases':tail[:4],'johnny':tail[4:]})
    require(displays and [r['ordinal'] for r in displays]==list(range(1,len(displays)+1)),'contiguous native displays')
    require(displays[0]['ticks']==0 and all(a['ticks']<=b['ticks'] for a,b in zip(displays,displays[1:])),'observed monotonic native timing')
    calls=[list(map(int,r)) for r in re.findall(r'NATIVE CALL: segment=(\d+) args=(\d+),(\d+),(\d+),(\d+)',text)]
    expected=[[i+1,0,0,0,0] for i in range(waits)] if mode==0 else ([[1,3,7,3,7],[2,3,7,5,3]] if mode==1 else [[1,1,3,1,3],[2,1,3,4,5]])
    require(calls==expected,'exact public native calls')
    returns=[list(map(int,r)) for r in re.findall(r'NATIVE RETURN: segment=(\d+) ticks=(\d+)',text)]
    require([r[0] for r in returns]==[r[0] for r in calls],'every native call returned')
    seen={f for row in displays for f in row['phases'] if f>=0}
    if not low:require(displays[0]['phases']==[3,7,9,-1],'initial003007009 display phases')
    if mode==0 and waits>1:
        require(seen==set(range(30,42) if low else range(3,12)),'all displayed native wave phases')
    if mode==0 and waits==1 and not low:
        require(all(r['phases']==[3,7,9,-1] for r in displays),'initial003007009 display phases')
    loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)))
    require({member(f) for f in FRAMES}<=set(loaded),'selected ten background dependencies')
    if holiday: require(set(PROP_HASHES)<=set(loaded),'selected four full-size holiday dependencies')
    return {'displays':displays,'native_calls':calls,'native_returns':returns,'background_draws':bg,
      'ground_surface_placement':[[*origin,*size]],'wave_surface_placements':surfaces,'holiday_draws':props,'displayed_phases':sorted(seen),
      'backdrop':backdrop,'loaded_art':loaded,'duration_ms':displays[-1]['time_ms']}

def one(exe,archive,folder,args,candidate,canvases):
    folder.mkdir(parents=True);shutil.copyfile(archive,folder/'scrantic_data.zip');(folder/'profile').mkdir()
    command=[str(exe),*map(str,args)]
    with (folder/'capture.log').open('wb') as log:
        result=subprocess.run(command,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=log,stderr=subprocess.STDOUT,timeout=45)
    require(result.returncode==0,'native process exit:'+str(folder))
    text=(folder/'capture.log').read_text();facts=verify_log(text,args,candidate,canvases)
    images={}
    for row in facts['displays']:
        ppm=folder/f"display-{row['ordinal']:03}.ppm";pixels=codec.ppm(ppm);digest=sha(pixels)
        if digest not in images:
            image=f"display-{row['ordinal']:03}.png";png=codec.png_bytes(pixels);(folder/image).write_bytes(png)
            images[digest]={'file':image,'png_sha256':sha(png)}
        row.update(images[digest],pixels_sha256=digest)
    final=codec.ppm(folder/'final.ppm');png=codec.png_bytes(final);(folder/'final.png').write_bytes(png)
    require(sha(final)==facts['displays'][-1]['pixels_sha256'],'final capture matches last actual display')
    report={'status':'PASS','args':args,'archive_sha256':sha(archive.read_bytes()),'executable_sha256':sha(exe.read_bytes()),
      'command':command,'png_sha256':sha(png),'log_sha256':sha((folder/'capture.log').read_bytes()),**facts}
    save(folder/'report.json',report);print('PASS '+folder.relative_to(exe.parent).as_posix(),flush=True)
    return report

def scoped_pixels(before,after,offset,canvases,low=False):
    require(len(before)==len(after)==1280*960*3,'native pixel dimensions')
    # Only the registered ground plus actually enabled modified wave extents.
    # Center384x256 reaches beyond the ground; low tide does not draw it.
    dx,dy=2*offset[0],2*offset[1]
    rectangles=[[540+dx,548+dy,1180+dx,728+dy]]
    if not low and canvases['6']==[384,256]:rectangles.append([696+dx,548+dy,1080+dx,804+dy])
    changed=0
    for y in range(960):
        start=y*3840
        spans=[(l,r) for l,t,r,b in rectangles if t<=y<b]
        if not spans:require(before[start:start+3840]==after[start:start+3840],'pixel outside registered ground/foam');continue
        # Both selected intervals overlap whenever both exist at the same row.
        l,r=min(s[0] for s in spans),max(s[1] for s in spans)
        require(before[start:start+l*3]==after[start:start+l*3] and before[start+r*3:start+3840]==after[start+r*3:start+3840],'pixel outside registered ground/foam')
        changed+=sum(before[start+x*3:start+x*3+3]!=after[start+x*3:start+x*3+3] for x in range(l,r))
    require(changed>0,'native ground change visible')
    return changed

def controls(output,case,canvases,relative='day/none'):
    folder=output/relative;text=(folder/'candidate/smoke/capture.log').read_text()
    verify_log(text,case,True,canvases)
    before=codec.ppm(folder/'baseline/smoke/final.ppm');after=codec.ppm(folder/'candidate/smoke/final.ppm')
    damaged=bytearray(after);damaged[0]=before[0]^1
    wave_x=696 if canvases['6']==[384,256] else 728
    tests=[('actual_ground_offset',lambda:verify_log(text.replace('GROUND SURFACE: x=540 ','GROUND SURFACE: x=541 '),case,True,canvases),'actual ground surface placement'),
      ('actual_center_offset',lambda:verify_log(text.replace(f'WAVE SURFACE: frame=7 x={wave_x} ',f'WAVE SURFACE: frame=7 x={wave_x+1} '),case,True,canvases),'actual high-wave surface placement'),
      ('initial_wave_phase',lambda:verify_log(text.replace('phases=3,7,9,-1','phases=3,8,9,-1'),case,True,canvases),'initial003007009 display phases'),
      ('native_timestamp',lambda:verify_log(text.replace('DISPLAY: n=1 ticks=0 ','DISPLAY: n=1 ticks=1 '),case,True,canvases),'observed monotonic native timing'),
      ('outside_registered_pixel',lambda:scoped_pixels(before,bytes(damaged),[0,0],canvases),'pixel outside registered ground/foam')]
    motion=output/'motion/high_clover/candidate/smoke/capture.log'
    if motion.is_file():
        full=motion.read_text();verify_log(full,MOTION['high_clover'],True,canvases)
        altered=re.sub(r'(phases=\d+,)8(,)',r'\g<1>7\2',full)
        tests.append(('full_phase_coverage',lambda:verify_log(altered,MOTION['high_clover'],True,canvases),'all displayed native wave phases'))
    results=[]
    for name,call,label in tests:
        try: call()
        except ValueError as e: require(str(e)=='integrated shore: '+label,'named negative:'+name);results.append({'name':name,'failure':str(e),'status':'FIRED'})
        else: raise ValueError('survived:'+name)
    verify_log(text,case,True,canvases)
    scoped_pixels(before,after,[0,0],canvases)
    save(output/'negative-controls.json',{'status':'PASS','helper_sha256':sha(Path(__file__).read_bytes()),'results':results,'method':'Actual native logs copied/damaged in memory; restored positive re-executed. Original outputs preserved.'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--baseline-sha256',required=True);p.add_argument('--candidate-sha256',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--phase',choices=('initial','cycle','full'),required=True);a=p.parse_args()
    require(not a.output.exists(),'fresh output');a.output.mkdir(parents=True)
    try:
        protected=legacy.protected();require(protected['assets/scrantic_data.zip']==legacy.PRODUCTION_SHA,'production archive unchanged')
        require(sha(a.baseline.read_bytes())==a.baseline_sha256 and sha(a.candidate.read_bytes())==a.candidate_sha256,'explicit selected archive hashes')
        pair=package_pair(a.baseline,a.candidate);save(a.output/'inputs.json',{'pair':pair,'protected_sha256':protected,'helpers_sha256':snapshot_helpers(a.output),'scope':'Current port renderer, source unchanged during run. Explicit state selection bypasses calendar/cargo policy. Native timing is the port logical20ms tick, not original-executable proof.'})
        exe=build(a.output);results={};groups={'day':DAY}
        if a.phase=='cycle':groups={'motion':{'high_clover':MOTION['high_clover']}}
        if a.phase=='full':groups['motion']=MOTION
        for group,cases in groups.items():
            for name,args in cases.items():
                rows={}
                for label,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                    rows[label]=one(exe,archive,a.output/group/name/label/'smoke',args,label=='candidate',pair['candidate_canvases'])
                # Read corresponding raw captures without changing any image.
                counts=[];keys=('ordinal','ticks','time_ms','segment','phases','johnny')
                require([[r[k] for k in keys] for r in rows['baseline']['displays']]==[[r[k] for k in keys] for r in rows['candidate']['displays']],'native display timing/poses unchanged')
                for left,right in zip(rows['baseline']['displays'],rows['candidate']['displays']):
                    b=codec.ppm(a.output/group/name/'baseline/smoke'/f"display-{left['ordinal']:03}.ppm")
                    c=codec.ppm(a.output/group/name/'candidate/smoke'/f"display-{right['ordinal']:03}.ppm")
                    counts.append(scoped_pixels(b,c,args[2:4],pair['candidate_canvases'],bool(args[4])))
                results[group+'/'+name]={'args':args,'smoke':'PASS','display_count':len(counts),'changed_pixel_counts':counts,'baseline_report':(a.output/group/name/'baseline/smoke/report.json').relative_to(a.output).as_posix(),'candidate_report':(a.output/group/name/'candidate/smoke/report.json').relative_to(a.output).as_posix()}
            save(a.output/(group+'-smoke.json'),{'status':'PASS','cases':{k:v for k,v in results.items() if k.startswith(group+'/')}})
            print('PASS '+group+' smoke group',flush=True)
        if a.phase in ('full','cycle'):
            # Every initial smoke has succeeded before any fresh repeat regression.
            for group,cases in groups.items():
                for name,args in cases.items():
                    for label,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                        prior=json.loads((a.output/group/name/label/'smoke/report.json').read_bytes())
                        repeated=one(exe,archive,a.output/group/name/label/'repeat',args,label=='candidate',pair['candidate_canvases'])
                        require(prior['displays']==repeated['displays'] and prior['background_draws']==repeated['background_draws'] and prior['png_sha256']==repeated['png_sha256'],'fresh-process exact native repeat:'+group+'/'+name+'/'+label)
                    results[group+'/'+name]['fresh_repeat']='PASS'
        if a.phase=='cycle':controls(a.output,MOTION['high_clover'],pair['candidate_canvases'],'motion/high_clover')
        else:controls(a.output,DAY['none'],pair['candidate_canvases'])
        require(legacy.protected()==protected,'compiled source/production inputs stable during run')
        require(sha(a.baseline.read_bytes())==a.baseline_sha256 and sha(a.candidate.read_bytes())==a.candidate_sha256,'private archive inputs unchanged')
        save(a.output/'summary.json',{'status':'PASS','phase':a.phase,'package_pair':pair,'cases':results,'protected_inputs_unchanged':len(protected),'accepted':False,'scope':'Initial mode is smoke-only diagnostic, not full motion approval. Full mode records all high/low phases plus native Johnny routes with exact fresh repeats; visual tide/contact approval remains separate.'})
    except Exception:
        save(a.output/'failure.json',{'traceback':traceback.format_exc()});raise

if __name__=='__main__':main()
