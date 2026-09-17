"""Final standard package through the existing real native observer, windowless."""
import argparse
import json
import re
import traceback
from pathlib import Path
import contract as c

def controls(observer,out,pair):
    args=c.CASES['motion/high_clover'];folder=out/'motion/high_clover'
    text=(folder/'candidate/smoke/capture.log').read_text();sizes=pair['canvases']['candidate']
    before=observer.codec.ppm(folder/'baseline/smoke/final.ppm');after=observer.codec.ppm(folder/'candidate/smoke/final.ppm')
    wrong=bytearray(after);wrong[0]=before[0]^1
    lowargs=c.CASES['motion/low_clover'];low=out/'motion/low_clover'
    lowb=observer.codec.ppm(low/'baseline/smoke/final.ppm');lowa=observer.codec.ppm(low/'candidate/smoke/final.ppm')
    lowwrong=bytearray(lowa);at=(750*1280+800)*3;lowwrong[at]=lowb[at]^1
    bannerargs=c.CASES['day/banner'];banner=(out/'day/banner/candidate/smoke/capture.log').read_text()
    cases=[
      ('ground_offset',lambda:c.verify_log(text.replace('GROUND SURFACE: x=540 ','GROUND SURFACE: x=541 '),args,True,sizes),'actual ground surface'),
      ('left_offset',lambda:c.verify_log(text.replace('WAVE SURFACE: frame=3 x=534 ','WAVE SURFACE: frame=3 x=535 '),args,True,sizes),'003 actual wave surface'),
      ('native_time',lambda:c.verify_log(text.replace('DISPLAY: n=1 ticks=0 ','DISPLAY: n=1 ticks=1 '),args,True,sizes),'native timing'),
      ('phase_omission',lambda:c.verify_log(re.sub(r'(phases=\d+,)8(,)',r'\g<1>7\2',text),args,True,sizes),'all wave phases'),
      ('banner_origin',lambda:c.verify_log(banner.replace('PROP DRAW: frame=3 x=361 ','PROP DRAW: frame=3 x=362 '),bannerargs,True,sizes),'actual holiday origin/canvas'),
      ('banner_fallback',lambda:c.verify_log(banner.replace('Art asset: data/styles/cartoon/BMP/HOLIDAY.BMP/003.png','Art asset: data/hd/BMP/HOLIDAY.BMP/003.png'),bannerargs,True,sizes),'selected holiday dependencies'),
      ('outside_pixel',lambda:c.scoped_pixels(before,bytes(wrong),args),'pixel outside selected ground/waves/holiday'),
      ('inactive_low_wave_pixel',lambda:c.scoped_pixels(lowb,bytes(lowwrong),lowargs),'pixel outside selected ground/waves/holiday')]
    results=[]
    c.verify_log(text,args,True,sizes);c.scoped_pixels(before,after,args)
    for name,run,label in cases:
        try:run()
        except ValueError as error:
            c.require(str(error)=='final native: '+label,'named negative '+name)
            results.append({'name':name,'status':'FIRED','failure':str(error)})
        else:raise ValueError('final native: negative survived '+name)
    c.verify_log(text,args,True,sizes);c.verify_log(banner,bannerargs,True,sizes)
    c.scoped_pixels(before,after,args);c.scoped_pixels(lowb,lowa,lowargs)
    c.save(out/'negative-controls.json',{'status':'PASS','contract_sha256':c.sha((c.HERE/'contract.py').read_bytes()),
       'results':results,'restored_positive':'PASS','method':'Actual logs and pixels damaged in memory; captured files unchanged.'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--baseline-sha256',required=True);p.add_argument('--candidate-sha256',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--phase',choices=('full',),required=True);a=p.parse_args()
    c.require(not a.output.exists(),'fresh output');a.output.mkdir(parents=True)
    try:
        c.require(a.baseline_sha256==c.BASE_SHA,'pinned baseline argument')
        observer=c.load_observer();observer.verify_log=c.verify_log
        pair=c.package_pair(a.baseline,a.candidate,a.candidate_sha256)
        protected=observer.legacy.protected()
        helper_paths=[*c.HERE.glob('*.py'),c.OBSERVER,c.OBSERVER.parent/'driver.c',c.OBSERVER.parent/'run.py',observer.LEGACY,observer.legacy.CODEC]
        helpers={q.relative_to(c.ROOT).as_posix():c.sha(q.read_bytes()) for q in helper_paths}
        for name,digest in protected.items():
            if name=='assets/scrantic_data.zip':continue
            dest=a.output/'source-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((c.ROOT/name).read_bytes())
            c.require(c.sha(dest.read_bytes())==digest,'frozen source '+name)
        for name in helpers:
            dest=a.output/'helper-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((c.ROOT/name).read_bytes())
        c.save(a.output/'inputs.json',{'pair':pair,'cases':c.CASES,'protected_sha256':protected,'helpers_sha256':helpers,
          'runtime_commit':c.RUNTIME_COMMIT,'scope':'Final standard package vs prior production. Explicit state selection bypasses calendar/cargo policy; port native ticks and calls, not original-executable parity.'})
        exe=observer.build(a.output)
        print('WITNESS final native contract '+c.sha((c.HERE/'contract.py').read_bytes())+' executable '+c.sha(exe.read_bytes()),flush=True)
        results={}
        for name,args in c.CASES.items():
            rows={}
            for side,path in (('baseline',a.baseline),('candidate',a.candidate)):
                rows[side]=observer.one(exe,path,a.output/name/side/'smoke',args,side=='candidate',pair['canvases'][side])
            c.compare_facts(rows['baseline'],rows['candidate']);counts=[]
            for left,right in zip(rows['baseline']['displays'],rows['candidate']['displays']):
                before=observer.codec.ppm(a.output/name/'baseline/smoke'/f"display-{left['ordinal']:03}.ppm")
                after=observer.codec.ppm(a.output/name/'candidate/smoke'/f"display-{right['ordinal']:03}.ppm")
                counts.append(c.scoped_pixels(before,after,args))
            c.require(any(counts),'visible integrated change '+name)
            if name.startswith('motion/johnny'):
                expected=[18,0,433,225] if name.endswith('front') else [18,1,394,209]
                c.require(any(r['johnny']==expected for r in rows['candidate']['displays']),'accepted Johnny contact position '+name)
            results[name]={'args':args,'smoke':'PASS','display_count':len(counts),'changed_pixel_counts':counts,
                           'duration_ms':rows['candidate']['duration_ms'],'displayed_phases':rows['candidate']['displayed_phases']}
            c.save(a.output/'smoke-progress.json',{'status':'IN_PROGRESS','completed_cases':results})
        c.save(a.output/'smoke.json',{'status':'PASS','captures':len(c.CASES)*2,'cases':results})
        print('PASS all 28 smoke captures before fresh regression',flush=True)
        for name,args in c.CASES.items():
            for side,path in (('baseline',a.baseline),('candidate',a.candidate)):
                prior=json.loads((a.output/name/side/'smoke/report.json').read_bytes())
                fresh=observer.one(exe,path,a.output/name/side/'repeat',args,side=='candidate',pair['canvases'][side])
                fields=('displays','native_calls','native_returns','background_draws','ground_surface_placement','wave_surface_placements','holiday_draws','png_sha256')
                c.require(all(prior[k]==fresh[k] for k in fields),'fresh exact native repeat '+name+'/'+side)
            results[name]['fresh_repeat']='PASS'
        controls(observer,a.output,pair)
        c.require(protected==observer.legacy.protected(),'runtime and live production stable')
        c.require(helpers=={q.relative_to(c.ROOT).as_posix():c.sha(q.read_bytes()) for q in helper_paths},'native helper sources stable')
        c.require(c.package_pair(a.baseline,a.candidate,a.candidate_sha256)==pair,'selected package inputs stable')
        c.save(a.output/'summary.json',{'status':'PASS','phase':'full','package_pair':pair,'cases':results,
          'smoke_captures':28,'fresh_repeat_captures':28,'negative_controls':8,'protected_inputs_unchanged':len(protected),
          'scope':'Final package native application validation. Actual wave phases, surface offsets, holidays and accepted Johnny contact coordinates; no new artwork approval inferred.'})
    except Exception:
        c.save(a.output/'failure.json',{'traceback':traceback.format_exc()});raise

if __name__=='__main__':main()
