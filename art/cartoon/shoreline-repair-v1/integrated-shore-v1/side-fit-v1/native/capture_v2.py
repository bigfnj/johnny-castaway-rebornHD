"""Seven-member native comparison, using the unchanged observer and six-side parser."""
import argparse
import json
from pathlib import Path
import re
import traceback
import combined as c


def controls(observer, output, pair, support):
    folder = output/'high_clover'
    text = (folder/'candidate/smoke/capture.log').read_text()
    canvases = pair['canvases']['candidate']
    report = json.loads((folder/'candidate/smoke/report.json').read_bytes())
    # Use the actual initial007 display, not the terminal phase.
    row = report['displays'][0]
    before = observer.codec.ppm(folder/'baseline/smoke/display-001.ppm')
    after = observer.codec.ppm(folder/'candidate/smoke/display-001.ppm')
    damaged = bytearray(after)
    at = (650*1280+690)*3  # Protected gap between left and center canvases.
    damaged[at] = before[at] ^ 1
    low = observer.codec.ppm(output/'low_clover/candidate/smoke/final.ppm')
    low_bad = bytearray(low); low_bad[0] ^= 1
    omitted = re.sub(r'(phases=\d+,)8(,)',r'\g<1>7\2',text)
    c.require(omitted != text, 'phase mutation changed actual log')
    inactive = bytearray(before)
    sy,sl,sr = next(r for r in support['row_spans'] if 700 <= r[1] < 1000)
    at = (sy*1280+sl)*3; inactive[at] ^= 1
    tests = [
        ('actual_left_offset',lambda:c.old.verify_log(text.replace('WAVE SURFACE: frame=3 x=534 ','WAVE SURFACE: frame=3 x=535 '),c.old.CASES['high_clover'],True,canvases),'003 actual registered wave surface'),
        ('native_timestamp',lambda:c.old.verify_log(text.replace('DISPLAY: n=1 ticks=0 ','DISPLAY: n=1 ticks=1 '),c.old.CASES['high_clover'],True,canvases),'actual native timing'),
        ('phase_omission',lambda:c.old.verify_log(omitted,c.old.CASES['high_clover'],True,canvases),'complete low/high phase coverage'),
        ('protected_gap_pixel',lambda:c.scoped_pixels(before,bytes(damaged),[0,0],False,row['phases'],support),'pixel outside active selected wave support'),
        ('inactive007_pixel',lambda:c.scoped_pixels(before,bytes(inactive),[0,0],False,[3,6,9,-1],support),'pixel outside active selected wave support'),
        ('low_tide_changed_pixel',lambda:c.scoped_pixels(low,bytes(low_bad),[0,0],True,[30,33,36,39],support),'low tide exact full-scene pixels'),
    ]
    results = []
    for name,call,label in tests:
        try:
            call()
        except ValueError as error:
            c.require(str(error) == 'side native: '+label, 'named negative '+name)
            results.append({'name':name,'status':'FIRED','failure':str(error)})
        else:
            raise ValueError('side native: negative survived '+name)
    c.old.verify_log(text,c.old.CASES['high_clover'],True,canvases)
    c.scoped_pixels(before,after,[0,0],False,row['phases'],support)
    c.scoped_pixels(low,low,[0,0],True,[30,33,36,39],support)
    c.save(output/'negative-controls.json',{'status':'PASS','results':results,'restored_positive':'PASS',
        'capture_sha256':c.sha(Path(__file__).read_bytes()),'combined_sha256':c.sha((c.HERE/'combined.py').read_bytes()),
        'package_pair':pair,'method':'Actual native logs and pixels damaged only in memory; no renderer/capture edits.'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--candidate-sha256',required=True)
    p.add_argument('--preparation',type=Path,required=True)
    p.add_argument('--preparation-sha256',required=True)
    p.add_argument('--runtime-commit',required=True)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    c.require(not a.output.exists(),'fresh combined capture output')
    a.output.mkdir(parents=True)
    try:
        c.require(c.sha(a.preparation.read_bytes()) == a.preparation_sha256,'combined preparation identity')
        preparation = json.loads(a.preparation.read_bytes())
        pair = c.package_pair(a.baseline,a.candidate,a.candidate_sha256)
        c.require(preparation['package_pair'] == pair,'combined preparation package binding')
        support_path = c.ROOT/preparation['center_support']['path']
        c.require(c.sha(support_path.read_bytes()) == preparation['center_support']['sha256'],'007 support identity')
        support = json.loads(support_path.read_bytes())
        observer = c.old.load_observer()
        observer.verify_log = c.old.verify_log
        protected = observer.legacy.protected()
        c.require(protected['assets/scrantic_data.zip'] == observer.legacy.PRODUCTION_SHA,'production archive unchanged')
        for name,digest in protected.items():
            if name == 'assets/scrantic_data.zip':
                continue
            path = a.output/'source-snapshot'/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((c.ROOT/name).read_bytes())
            c.require(c.sha(path.read_bytes()) == digest,'source snapshot '+name)
        helper_paths = [*c.HERE.glob('*.py'),c.old.OBSERVER,c.old.OBSERVER.parent/'driver.c',observer.LEGACY,observer.legacy.CODEC]
        helpers = {q.relative_to(c.ROOT).as_posix():c.sha(q.read_bytes()) for q in helper_paths}
        for source in helper_paths:
            target = a.output/'helper-snapshot'/source.relative_to(c.ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read_bytes())
        c.save(a.output/'inputs.json',{'pair':pair,'cases':c.old.CASES,'protected_sha256':protected,'helpers_sha256':helpers,
            'preparation_sha256':a.preparation_sha256,'center_support':preparation['center_support'],
            'runtime_commit_authorized_by_root':a.runtime_commit,
            'scope':'Both variants keep exact ground/props. Six side placements and one generated007 edit; actual port behavior, human appearance pending.'})
        exe = observer.build(a.output)
        results = {}
        for name,args in c.old.CASES.items():
            rows = {}
            for side,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                rows[side] = observer.one(exe,archive,a.output/name/side/'smoke',args,side == 'candidate',pair['canvases'][side])
            c.old.compare_facts(rows['baseline'],rows['candidate'])
            counts = []
            for left,right in zip(rows['baseline']['displays'],rows['candidate']['displays']):
                before = observer.codec.ppm(a.output/name/'baseline/smoke'/f"display-{left['ordinal']:03}.ppm")
                after = observer.codec.ppm(a.output/name/'candidate/smoke'/f"display-{right['ordinal']:03}.ppm")
                counts.append(c.scoped_pixels(before,after,args[2:4],bool(args[4]),left['phases'],support))
            c.require(bool(args[4]) or any(counts),name+' selected changes visible')
            results[name] = {'args':args,'smoke':'PASS','display_count':len(counts),'changed_pixel_counts':counts,
                             'displayed_phases':rows['baseline']['displayed_phases'],'duration_ms':rows['baseline']['duration_ms']}
        c.save(a.output/'smoke.json',{'status':'PASS','variant_case_captures':10,'cases':results})
        for name,args in c.old.CASES.items():
            for side,archive in (('baseline',a.baseline),('candidate',a.candidate)):
                prior = json.loads((a.output/name/side/'smoke/report.json').read_bytes())
                fresh = observer.one(exe,archive,a.output/name/side/'repeat',args,side == 'candidate',pair['canvases'][side])
                c.require(all(prior[k] == fresh[k] for k in ('displays','native_calls','native_returns','background_draws','wave_surface_placements','png_sha256')),name+'/'+side+' fresh native repeat')
            results[name]['fresh_repeat'] = 'PASS'
        controls(observer,a.output,pair,support)
        c.require(protected == observer.legacy.protected(),'compiled sources and production stable during run')
        c.require(helpers == {q.relative_to(c.ROOT).as_posix():c.sha(q.read_bytes()) for q in helper_paths},'capture helpers stable during run')
        c.require(c.package_pair(a.baseline,a.candidate,a.candidate_sha256) == pair,'combined package stable')
        c.save(a.output/'summary.json',{'status':'PASS','phase':'full','package_pair':pair,'cases':results,
            'smoke_captures':10,'fresh_repeat_captures':10,'protected_inputs_unchanged':len(protected),'accepted':False,
            'scope':'Seven-member wave comparison. No production promotion or human approval.'})
    except Exception:
        c.save(a.output/'failure.json',{'traceback':traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
