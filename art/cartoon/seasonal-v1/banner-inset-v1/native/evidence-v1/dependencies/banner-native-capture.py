"""Banner-only orchestration around the frozen integrated-shore native observer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import traceback
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
OBSERVER=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/capture.py'
OBSERVER_SHA='f2e0684f6726ce53951988b5d44c101d3efe44f07e6b3b66277499a9f12a1bae'
BASE_SHA='ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac'
MEMBER='data/styles/cartoon/BMP/HOLIDAY.BMP/003.png'
CASES={'day_banner':[4,0,0,0,0,0,20],'night_banner':[4,1,0,0,0,0,20],'shifted_banner':[4,0,-80,20,0,0,20]}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,label):
    if not ok:raise ValueError('banner native: '+label)
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def pair(before,after,expected):
    require(sha(before.read_bytes())==BASE_SHA,'selected offshore baseline identity')
    require(sha(after.read_bytes())==expected,'candidate identity')
    with zipfile.ZipFile(before) as z:
        require(len(z.namelist())==len(set(z.namelist())),'baseline duplicate members')
        old={n:sha(z.read(n)) for n in z.namelist()}
    with zipfile.ZipFile(after) as z:
        require(len(z.namelist())==len(set(z.namelist())),'candidate duplicate members')
        new={n:sha(z.read(n)) for n in z.namelist()}
        require(old.keys()==new.keys() and [n for n in old if old[n]!=new[n]]==[MEMBER],'only HOLIDAY003 payload changed')
        require(struct.unpack('>II',z.read(MEMBER)[16:24])==(304,94),'banner canvas')
        canvases={str(f):list(struct.unpack('>II',z.read(f'data/styles/cartoon/BMP/BACKGRND.BMP/{f:03}.png')[16:24])) for f in (0,*range(3,12))}
    return {'baseline_sha256':BASE_SHA,'candidate_sha256':expected,'member_count':len(old),'unchanged_members':len(old)-1,
            'changed_member':MEMBER,'before_png_sha256':old[MEMBER],'after_png_sha256':new[MEMBER],'candidate_canvases':canvases}


def pixels(before,after,offset):
    require(len(before)==len(after)==1280*960*3,'scene pixel dimensions')
    x,y=722+offset[0]*2,310+offset[1]*2
    changed=0
    for row in range(960):
        start=row*1280*3
        if not y<=row<y+94:
            require(before[start:start+3840]==after[start:start+3840],'pixel outside banner canvas')
        else:
            left,right=start+x*3,start+(x+304)*3
            require(before[start:left]==after[start:left] and before[right:start+3840]==after[right:start+3840],'pixel outside banner canvas')
            changed+=sum(before[i:i+3]!=after[i:i+3] for i in range(left,right,3))
    require(changed>0,'banner change visible')
    return changed


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--candidate-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'fresh capture output');a.output.mkdir(parents=True)
    try:
        require(sha(OBSERVER.read_bytes())==OBSERVER_SHA,'frozen observer identity')
        require(sha((OBSERVER.parent/'driver.c').read_bytes())=='beb8beae0c3b54562fe51285d184d55ccd2b185fe34cf97b7801d2536abd1b59','frozen native driver identity')
        spec=importlib.util.spec_from_file_location('banner_frozen_observer',OBSERVER)
        observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
        packages=pair(a.baseline,a.candidate,a.candidate_sha256)
        protected=observer.legacy.protected()
        save(a.output/'inputs.json',{'pair':packages,'cases':CASES,'protected_sha256':protected,
             'observer_sha256':OBSERVER_SHA,'adapter_sha256':sha(Path(__file__).read_bytes()),
             'scope':'Both sides are the selected offshore island. Only banner003 differs. No calendar or original-executable fidelity claim.'})
        exe=observer.build(a.output);results={}
        for name,args in CASES.items():
            rows={}
            for side,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                rows[side]=observer.one(exe,archive,a.output/name/side/'smoke',args,True,packages['candidate_canvases'])
            keys=('ordinal','ticks','time_ms','segment','phases','johnny')
            require([[r[k] for k in keys] for r in rows['baseline']['displays']]==[[r[k] for k in keys] for r in rows['candidate']['displays']],name+' timing/poses/phases')
            counts=[]
            for left,right in zip(rows['baseline']['displays'],rows['candidate']['displays']):
                counts.append(pixels(observer.codec.ppm(a.output/name/'baseline/smoke'/f"display-{left['ordinal']:03}.ppm"),
                                     observer.codec.ppm(a.output/name/'candidate/smoke'/f"display-{right['ordinal']:03}.ppm"),args[2:4]))
            closures={}
            for side in ('baseline','candidate'):
                displays=rows[side]['displays'];at_loop=[r for r in displays if r['time_ms']==1440]
                require(at_loop and at_loop[-1]['phases']==displays[0]['phases'],name+' actual1440 phase closure')
                closures[side]=at_loop[-1]['pixels_sha256']==displays[0]['pixels_sha256']
            results[name]={'smoke':'PASS','args':args,'display_count':len(counts),'changed_banner_pixels':counts,'loop_ms':1440,'full_scene_pixels_close':closures}
            print('PASS banner pair '+name,flush=True)
        save(a.output/'smoke.json',{'status':'PASS','cases':results})
        for name,args in CASES.items():
            for side,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                old=json.loads((a.output/name/side/'smoke/report.json').read_bytes())
                fresh=observer.one(exe,archive,a.output/name/side/'repeat',args,True,packages['candidate_canvases'])
                require(old['displays']==fresh['displays'] and old['background_draws']==fresh['background_draws'],name+'/'+side+' fresh exact repeat')
            results[name]['fresh_repeat']='PASS'
        # Reach the narrow native scene boundary with one actual damaged pixel.
        before=observer.codec.ppm(a.output/'day_banner/baseline/smoke/final.ppm')
        after=observer.codec.ppm(a.output/'day_banner/candidate/smoke/final.ppm')
        pixels(before,after,[0,0]);damaged=bytearray(after);damaged[0]=before[0]^1
        try:pixels(before,bytes(damaged),[0,0])
        except ValueError as error:require(str(error)=='banner native: pixel outside banner canvas','named outside-pixel control')
        else:raise ValueError('banner native: outside-pixel control survived')
        pixels(before,after,[0,0])
        save(a.output/'negative.json',{'status':'PASS','failure':'banner native: pixel outside banner canvas','restored_positive':'PASS','adapter_sha256':sha(Path(__file__).read_bytes())})
        require(protected==observer.legacy.protected(),'runtime/production inputs stable')
        require(pair(a.baseline,a.candidate,a.candidate_sha256)==packages,'private packages stable')
        save(a.output/'summary.json',{'status':'PASS','phase':'full','package_pair':packages,'cases':results,'accepted':False,'scope':'Exact native banner-only comparison. Banner attachment and shoreline placement remain human review questions.'})
    except Exception:
        save(a.output/'failure.json',{'traceback':traceback.format_exc()});raise


if __name__=='__main__':main()
