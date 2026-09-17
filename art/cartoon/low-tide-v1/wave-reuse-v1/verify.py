"""Bounded ordered replay and damaged-input controls for the low-wave proposal."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reuse',HERE/'export.py')
e=importlib.util.module_from_spec(spec); spec.loader.exec_module(e)


def run(args, log):
    result=subprocess.run([sys.executable,'-B',str(HERE/'export.py'),*args],capture_output=True,text=True)
    raw=(result.stdout+result.stderr).encode('utf-8')
    log.write_bytes(raw)
    e.require(result.returncode==0 and 'WITNESS low-wave-reuse '+e.sha((HERE/'export.py').read_bytes()) in result.stdout,
              'fresh exporter process did not pass with current witness')
    return {'command':[sys.executable,'-B',str(HERE/'export.py'),*args], 'returncode':result.returncode,
            'log':log.name,'log_sha256':e.sha(raw)}


def damaged(call, expected, label):
    try:
        call()
    except ValueError as exc:
        e.require(str(exc)==expected,label+': unexpected failure '+str(exc))
        return {'name':label,'status':'FIRED','failure':str(exc)}
    raise ValueError(label+': damaged input survived')


def exact_outputs(folder,report):
    for path,digest in report['outputs_sha256'].items():
        e.require(e.sha((folder/path).read_bytes())==digest,path+': output binding differs')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=['smoke','regression'],required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    recipe=json.loads((HERE/'recipe-v1.json').read_bytes())
    record={'phase':a.phase,'status':'PASS','exporter_sha256':e.sha((HERE/'export.py').read_bytes()),
            'verifier_sha256':e.sha(Path(__file__).read_bytes()),'recipe_sha256':e.sha((HERE/'recipe-v1.json').read_bytes())}
    if a.phase=='smoke':
        record['fresh_process']=run(['--phase','smoke','--output',str(a.output/'smoke')],a.output/'smoke.log')
        report=json.loads((a.output/'smoke/export-report.json').read_bytes())
        e.require([r['frame'] for r in report['frames']]==[30,33,36],'smoke: family coverage differs')
        record['representative_frames']=[30,33,36]
    else:
        smoke=json.loads((a.output/'smoke.json').read_bytes())
        e.require(smoke['status']=='PASS' and smoke['exporter_sha256']==record['exporter_sha256'],
                  'regression: matching smoke prerequisite absent')
        record['preceding_smoke_sha256']=e.sha((a.output/'smoke.json').read_bytes())
        record['fresh_replay']=run(['--phase','full','--check'],a.output/'replay.log')
        report=json.loads((HERE/'candidates/v1/export-report.json').read_bytes())
        e.require([r['frame'] for r in report['frames']]==list(range(30,39)),'regression: nine frames missing')
        exact_outputs(HERE/'candidates/v1',report)
        # Byte checks cover all native-size images and the complete retained audit.
        checks=[]
        for row in report['frames']:
            frame=row['frame']
            with Image.open(HERE/'candidates/v1'/row['path']) as im:
                runtime=im.copy()
            with Image.open(HERE/f'candidates/v1/unmasked/{frame:03}.png') as im:
                raw=im.copy()
            e.require(list(runtime.size)==row['runtime_canvas'] and runtime.mode=='RGBA',f'{frame:03}: canvas/mode differs')
            e.require(runtime.convert('RGB').tobytes()==raw.convert('RGB').tobytes(),f'{frame:03}: masked RGB differs')
            pairs=list(zip(raw.getchannel('A').get_flattened_data(),runtime.getchannel('A').get_flattened_data()))
            e.require(all(b<=a for a,b in pairs),f'{frame:03}: mask increases alpha')
            e.require(any(a==b and b>=8 for a,b in pairs) and any(a>b for a,b in pairs),f'{frame:03}: mask axes degenerate')
            e.require(row['outside_runtime_max_alpha']==0,f'{frame:03}: crop loses alpha')
            checks.append({'frame':frame,'canvas':row['runtime_canvas'],'outside_max':0,
                'rgb_exact':True,'retained_and_occluded_foam_witnesses':True})
        record['frames']=checks
        controls=[]
        bad=copy.deepcopy(recipe); bad['frames'][0]['source']=bad['frames'][1]['source']
        controls.append(damaged(lambda:e.validate(bad),'recipe: fixed family transform or frame mapping differs','wrong phase source'))
        bad=copy.deepcopy(recipe); bad['frames'][0]['affine_forward'][2]+=1
        controls.append(damaged(lambda:e.validate(bad),'recipe: fixed family transform or frame mapping differs','single-phase translation'))
        bad=copy.deepcopy(recipe); path=recipe['frames'][0]['source']; bad['source_bindings'][path]='0'*64
        controls.append(damaged(lambda:e.validate(bad),path+': source binding differs','source hash substitution'))
        original_loader=e.load_tool
        def load_bad_filter(path,digest,name):
            module=original_loader(path,digest,name)
            if path==e.FILTER:
                original=module.resample
                def resample(*args):
                    im=original(*args); im.putpixel((0,0),(255,255,255,8)); return im
                module.resample=resample
            return module
        try:
            e.load_tool=load_bad_filter
            controls.append(damaged(lambda:e.render(recipe,[30]),'030: filtered alpha outside runtime canvas','filtered outside-alpha fixture'))
        finally:
            e.load_tool=original_loader
        def load_bad_mask(path,digest,name):
            module=original_loader(path,digest,name)
            if path==e.MASK:
                original=module.occlude
                def occlude(*args):
                    im,stats=original(*args); r,g,b,a=im.getpixel((0,0)); im.putpixel((0,0),((r+1)%256,g,b,a)); return im,stats
                module.occlude=occlude
            return module
        try:
            e.load_tool=load_bad_mask
            controls.append(damaged(lambda:e.render(recipe,[30]),'030: visibility mask changed RGB','mask RGB-change fixture'))
        finally:
            e.load_tool=original_loader
        # Guard fixtures only alter returned images inside this process, never live files.
        outputs,restored=e.render(recipe,[30])
        e.require(outputs[recipe['frames'][0]['path']]==(HERE/'candidates/v1'/recipe['frames'][0]['path']).read_bytes(),
                  'restored positive runtime differs')
        record['damaged_controls']=controls
        record['restored_positive']='Exact030 runtime after restoring both helper fixtures; live source files untouched.'
        record['coverage_limit']='Fixture mutations exercise actual runtime guards. No compiled runtime, native motion, or source-guard-removal claim.'
        record['bound_output_count']=len(report['outputs_sha256'])
    record['report_sha256']=e.sha(e.encode(report))
    (a.output/(a.phase+'.json')).write_bytes(e.encode(record))
    print('PASS '+a.phase+' '+json.dumps({'frames':len(report['frames']),'controls':len(record.get('damaged_controls',[]))}))


if __name__=='__main__':
    main()
