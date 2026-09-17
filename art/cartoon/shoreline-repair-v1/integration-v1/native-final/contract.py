"""Exact final payload selection and native placement contract; no ZIP writes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
OBSERVER=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/capture.py'
OBSERVER_SHA='f2e0684f6726ce53951988b5d44c101d3efe44f07e6b3b66277499a9f12a1bae'
DRIVER_SHA='beb8beae0c3b54562fe51285d184d55ccd2b185fe34cf97b7801d2536abd1b59'
BASE_SHA='4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
RUNTIME_COMMIT='1aad361fe78dde2c956e05dc451b8d5bab100af0'
SELECTION=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/native/verification-v2/corrected-selection-v2.json'
SELECTION_SHA='0e24fc59fe7aea76c5b03d1c90ceac52aaf07cfcd622f72435950ad76c91b29e'
FRAMES=(0,*range(3,12))
HOLIDAYS={1:(0,410,298,80,68),2:(1,333,286,240,94),3:(2,404,267,112,130),4:(3,361,155,304,94)}
PROP_HASHES=('1f2ac522476d98afcade5f128c12c0c80f6993b871b611498971f23a44eabf79',
 'e6327c07e85d7d8610ed45a502efd283fe1c79fe5850c790bb2808a2ee02176e',
 '7d9c5406f8275a1af9c9369305575a24d807ac5b38200e6ad17913a0a8400265',
 'e36e103027d2eee53c58c903cd397770a66e5ffce2683e9c0c8ce6e2d988ff92')
CASES={**{'day/'+n:[h,0,0,0,0,0,1] for h,n in enumerate(('none','pumpkin','clover','tree','banner'))},
 'motion/high_none':[0,0,0,0,0,0,20],'motion/high_clover':[2,0,0,0,0,0,20],
 'motion/low_none':[0,0,0,0,1,0,24],'motion/low_clover':[2,0,0,0,1,0,24],
 'motion/night_shift_clover':[2,1,-80,20,0,0,20],
 'motion/johnny_front':[0,0,0,0,0,1,1],'motion/johnny_rear':[0,0,0,0,0,2,1],
 'banner/night':[4,1,0,0,0,0,20],'banner/shifted':[4,0,-80,20,0,0,20]}
TIMING=('ordinal','ticks','time_ms','segment','phases','johnny')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,label):
    if not ok:raise ValueError('final native: '+label)
def save(path,value):path.write_bytes((json.dumps(value,indent=2)+'\n').encode())
def member(frame):return f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
def load_observer():
    require(sha(OBSERVER.read_bytes())==OBSERVER_SHA,'frozen observer identity')
    require(sha((OBSERVER.parent/'driver.c').read_bytes())==DRIVER_SHA,'frozen driver identity')
    spec=importlib.util.spec_from_file_location('final_native_observer',OBSERVER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def fixtures():
    require(sha(SELECTION.read_bytes())==SELECTION_SHA,'corrected source selection identity')
    rows=json.loads(SELECTION.read_bytes())['frames'];require([r['frame'] for r in rows]==list(FRAMES),'ten shore fixture frames')
    selected={member(r['frame']):{'sha256':r['sha256'],'canvas':r['canvas'],'source':r['source_path']} for r in rows}
    for f,digest in enumerate(PROP_HASHES):
        source=f'art/cartoon/seasonal-v1/candidates/v5/BMP/HOLIDAY.BMP/{f:03}.png' if f<3 else 'art/cartoon/seasonal-v1/banner-inset-v1/candidates/v2/BMP/HOLIDAY.BMP/003.png'
        selected[f'data/styles/cartoon/BMP/HOLIDAY.BMP/{f:03}.png']={'sha256':digest,'canvas':list(HOLIDAYS[f+1][-2:]),'source':source}
    for name,row in selected.items():require(sha((ROOT/row['source']).read_bytes())==row['sha256'],'selected source '+name)
    return selected

def archive(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist();require(len(names)==len(set(names)),'archive duplicate members')
        rows={n:{'sha256':sha(z.read(n))} for n in names}
        for name,row in rows.items():
            if name.endswith('.png'):row['canvas']=list(struct.unpack('>II',z.read(name)[16:24]))
        return rows

def validate_members(before,after,selected):
    additions={f'data/styles/cartoon/BMP/HOLIDAY.BMP/{f:03}.png' for f in range(4)}
    require(len(before)==2594 and len(after)==2598,'baseline/final member counts')
    require(before.keys()<=after.keys() and after.keys()-before.keys()==additions,'four seasonal additions only')
    require({n for n in before if before[n]!=after[n]}=={member(f) for f in FRAMES},'ten shore replacements only')
    require(len(selected)==14,'fourteen selected fixtures')
    for name,row in selected.items():
        require(after[name]['sha256']==row['sha256'],'selected payload '+name)
        require(after[name]['canvas']==row['canvas'],'selected canvas '+name)
    return {'member_count':2598,'unchanged_prior_members':2584,
            'changed_members':{member(f):{'before':before[member(f)]['sha256'],'after':after[member(f)]['sha256']} for f in FRAMES},
            'added_members':{n:after[n]['sha256'] for n in sorted(additions)}}

def package_pair(baseline,candidate,candidate_sha):
    require(sha(baseline.read_bytes())==BASE_SHA,'baseline archive identity')
    require(sha(candidate.read_bytes())==candidate_sha,'final archive identity')
    before,after=archive(baseline),archive(candidate);selected=fixtures()
    pair=validate_members(before,after,selected)
    pair.update(baseline_sha256=BASE_SHA,candidate_sha256=candidate_sha,fixtures=selected,
      canvases={side:{str(f):rows[member(f)]['canvas'] for f in FRAMES} for side,rows in (('baseline',before),('candidate',after))})
    return pair

def verify_log(text,args,candidate,canvases):
    h,night,ox,oy,low,mode,waits=args
    require(f'STATE: seed=11 holiday={h} night={night} offset={ox},{oy} low={low} raft=0 render=1280x960' in text,'native state')
    require('DONE: native calls returned; cleanup complete' in text,'native cleanup')
    backdrop='NIGHT.SCR' if night else 'OCEAN02.SCR'
    require('island backdrop: '+backdrop in text,'native backdrop')
    bg=[list(map(int,r)) for r in re.findall(r'BG DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    size=[640,180] if candidate else [560,104]
    require([r for r in bg if r[0]==0]==[[0,288,279,ox,oy,2,*size]],'logical ground origin/canvas')
    ground=[list(map(int,r)) for r in re.findall(r'GROUND SURFACE: x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)',text)]
    origin=[540+ox*2,548+oy*2] if candidate else [576+ox*2,558+oy*2]
    require(ground==[[*origin,*size]],'actual ground surface')
    props=[list(map(int,r)) for r in re.findall(r'PROP DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)',text)]
    expected=[]
    if h:
        f,x,y,w,hh=HOLIDAYS[h];expected=[[f,x,y,ox,oy,2,w,hh]]
    require(props==expected,'actual holiday origin/canvas')
    waves=[r for r in bg if 3<=r[0]<=11]
    surfaces=[list(map(int,r)) for r in re.findall(r'WAVE SURFACE: frame=(\d+) x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)',text)]
    require(len(waves)==len(surfaces),'every wave surface observed')
    for actual,row in zip(surfaces,waves):
        f,x,y,dx,dy,scale,w,hh=row;xy=((270,306),(364,319),(518,303))[(f-3)//3]
        require((x,y)==xy and [dx,dy,scale,w,hh]==[ox,oy,2,*canvases[str(f)]],f'{f:03} logical wave origin/canvas')
        offset=((-6,0) if f<6 else (-32,-90) if f<9 else (0,0)) if candidate else (0,0)
        require(actual==[f,(x+dx)*2+offset[0],(y+dy)*2+offset[1],w,hh],f'{f:03} actual wave surface')
    displays=[]
    for row in re.findall(r'DISPLAY: n=(\d+) ticks=(\d+) segment=(\d+) phases=(-?\d+),(-?\d+),(-?\d+),(-?\d+) johnny=(-?\d+),(\d+),(-?\d+),(-?\d+)',text):
        n,t,segment,*tail=map(int,row);displays.append(dict(ordinal=n,ticks=t,time_ms=t*20,segment=segment,phases=tail[:4],johnny=tail[4:]))
    require(displays and [r['ordinal'] for r in displays]==list(range(1,len(displays)+1)),'contiguous displays')
    require(displays[0]['ticks']==0 and all(a['ticks']<=b['ticks'] for a,b in zip(displays,displays[1:])),'native timing')
    calls=[list(map(int,r)) for r in re.findall(r'NATIVE CALL: segment=(\d+) args=(\d+),(\d+),(\d+),(\d+)',text)]
    expected=[[i+1,0,0,0,0] for i in range(waits)] if mode==0 else ([[1,3,7,3,7],[2,3,7,5,3]] if mode==1 else [[1,1,3,1,3],[2,1,3,4,5]])
    require(calls==expected,'public native calls')
    returns=[list(map(int,r)) for r in re.findall(r'NATIVE RETURN: segment=(\d+) ticks=(\d+)',text)]
    require([r[0] for r in returns]==[r[0] for r in calls],'native calls returned')
    seen={f for row in displays for f in row['phases'] if f>=0}
    if not low:require(displays[0]['phases']==[3,7,9,-1],'initial high phases')
    if mode==0 and waits>1:require(seen==set(range(30,42) if low else range(3,12)),'all wave phases')
    if low:require(not waves and not surfaces,'no high waves at low tide')
    loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)))
    require({member(f) for f in FRAMES}<=set(loaded),'selected shore dependencies')
    expected_props={f'data/{"styles/cartoon" if candidate else "hd"}/BMP/HOLIDAY.BMP/{f:03}.png' for f in range(4)} if h else set()
    require({n for n in loaded if '/HOLIDAY.BMP/' in n}==expected_props,'selected holiday dependencies')
    return dict(displays=displays,native_calls=calls,native_returns=returns,background_draws=bg,ground_surface_placement=ground,
                wave_surface_placements=surfaces,holiday_draws=props,displayed_phases=sorted(seen),backdrop=backdrop,
                loaded_art=loaded,duration_ms=displays[-1]['time_ms'])

def compare_facts(before,after):
    require([[r[k] for k in TIMING] for r in before['displays']]==[[r[k] for k in TIMING] for r in after['displays']],'paired timing/phases/Johnny')
    require(before['native_calls']==after['native_calls'] and before['native_returns']==after['native_returns'],'paired calls/returns')
    require([r[:6] for r in before['background_draws']]==[r[:6] for r in after['background_draws']],'paired logical background positions')
    require(before['holiday_draws']==after['holiday_draws'],'paired holiday positions')

def scoped_pixels(before,after,args):
    require(len(before)==len(after)==1280*960*3,'native pixel dimensions')
    h,_,ox,oy,low,_,_=args;dx,dy=ox*2,oy*2
    rects=[(540+dx,548+dy,1180+dx,728+dy)]
    if not low:rects += [(534+dx,612+dy,684+dx,678+dy),(696+dx,548+dy,1080+dx,804+dy),(1036+dx,606+dy,1190+dx,680+dy)]
    if h:
        _,x,y,w,hh=HOLIDAYS[h];rects.append((x*2+dx,y*2+dy,x*2+dx+w,y*2+dy+hh))
    changed=0
    for y in range(960):
        start=y*3840;spans=sorted((l,r) for l,t,r,b in rects if t<=y<b);merged=[]
        for l,r in spans:
            if merged and l<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],r)
            else:merged.append([l,r])
        cursor=0
        for l,r in merged:
            require(before[start+cursor*3:start+l*3]==after[start+cursor*3:start+l*3],'pixel outside selected ground/waves/holiday')
            changed+=sum(before[start+x*3:start+x*3+3]!=after[start+x*3:start+x*3+3] for x in range(l,r));cursor=r
        require(before[start+cursor*3:start+3840]==after[start+cursor*3:start+3840],'pixel outside selected ground/waves/holiday')
    return changed
