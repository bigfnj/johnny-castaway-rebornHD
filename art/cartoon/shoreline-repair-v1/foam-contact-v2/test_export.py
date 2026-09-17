"""Focused visibility-mask witnesses, frozen inputs and fresh export replay."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent


def load(path):
    spec = importlib.util.spec_from_file_location('tested_foam_export',path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def witness(module):
    foam = Image.new('RGBA',(4,1))
    foam.putdata([(41,127,239,255),(71,183,217,255),(19,81,207,255),(29,137,233,173)])
    master = Image.new('RGBA',(4,1))
    master.putdata([(201,151,71,a) for a in (255,253,128,0)])
    masked,_ = module.occlude(foam,master,(0,0),(0,0,4,1))
    rows=[]
    for x,(a,expected) in enumerate(zip((255,253,128,0),(0,2,127,173))):
        before,after=foam.getpixel((x,0)),masked.getpixel((x,0))
        module.require(after[:3]==before[:3],f'foam RGB preserved at master alpha {a}')
        module.require(after[3]==expected,f'foam alpha visibility at master alpha {a}: expected {expected}, got {after[3]}')
        rows.append({'master_alpha':a,'before':list(before),'after':list(after)})
    return rows


def real_inputs(module):
    selected=HERE.parent/'shared-master/candidates/v1'
    master=Image.open(selected/'master-ground.png').convert('RGBA')
    recipe=json.loads((HERE/'recipe-v2.json').read_bytes())
    checks=[]
    with zipfile.ZipFile(module.ARCHIVE) as archive:
        for row in recipe['frames']:
            frame=row['frame']
            ground_path=selected/f"ground/{row['ground_family']:03}.png"
            ground_raw=ground_path.read_bytes()
            module.require(module.sha(ground_raw)==recipe['ancestor_outputs_sha256'][f"ground/{row['ground_family']:03}.png"],f'{frame:03}: frozen ground unchanged')
            actual=(HERE/'candidates/v2'/row['path']).read_bytes()
            if frame==0:
                module.require(actual==(selected/row['path']).read_bytes(),'000: byte identity')
                checks.append({'frame':0,'check':'byte identity','status':'PASS'})
                continue
            foam=Image.open(io.BytesIO(archive.read(row['previous_member']))).convert('RGBA')
            masked,_=module.occlude(foam,master,row['world_box'][:2],recipe['world_crop'])
            total=0
            for y in range(foam.height):
                for x in range(foam.width):
                    mx=x+row['world_box'][0]-recipe['world_crop'][0]
                    my=y+row['world_box'][1]-recipe['world_crop'][1]
                    ga=master.getpixel((mx,my))[3] if 0<=mx<master.width and 0<=my<master.height else 0
                    original=foam.getpixel((x,y))
                    expected_alpha=round(original[3]*(255-ga)/255)
                    module.require(masked.getpixel((x,y))==(*original[:3],expected_alpha),f'{frame:03}: actual source alpha/RGB at world {x+row["world_box"][0]},{y+row["world_box"][1]}')
                    total+=1
            composed=Image.alpha_composite(Image.open(io.BytesIO(ground_raw)).convert('RGBA'),masked)
            module.require(actual==module.png(composed),f'{frame:03}: actual composed runtime')
            checks.append({'frame':frame,'pixels_checked':total,'check':'all source RGB and exact visibility alpha; actual composition','status':'PASS'})
    return checks


def run(command):
    p=subprocess.run(command,capture_output=True,text=True)
    return {'argv':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=('smoke','regression'))
    p.add_argument('--probe',type=Path)
    args=p.parse_args()
    module_path=args.probe or HERE/'export.py'
    module=load(module_path)
    print('WITNESS foam-contact-test '+module.sha(module_path.read_bytes()))
    if args.probe:
        witness(module)
        print('PASS alpha visibility witnesses')
        return
    module.require(args.phase is not None,'phase is required')
    recipe=json.loads((HERE/'recipe-v2.json').read_bytes())
    result={'status':'PASS','phase':args.phase,'exporter_sha256':module.sha(module_path.read_bytes()),
            'test_sha256':module.sha(Path(__file__).read_bytes()),'recipe_sha256':module.sha((HERE/'recipe-v2.json').read_bytes()),
            'alpha_witnesses':witness(module)}
    outputs,report=module.render(recipe)
    module.require((HERE/'candidates/v2/export-report.json').read_bytes()==module.encode(report),'export report exact readback')
    for name,raw in outputs.items():
        module.require((HERE/'candidates/v2'/name).read_bytes()==raw,name+': exact readback')
    result['readback_files']=len(outputs)+1
    if args.phase=='regression':
        smoke=json.loads((HERE/'verification-smoke.json').read_bytes())
        module.require(smoke['status']=='PASS' and smoke['exporter_sha256']==result['exporter_sha256'],'matching prior smoke required')
        result['actual_source_checks']=real_inputs(module)
        with tempfile.TemporaryDirectory(prefix='foam-contact-') as temp:
            folder=Path(temp)
            replay=run([sys.executable,'-B',str(module_path),'--output',str(folder/'replay')])
            module.require(replay['exit_code']==0 and 'WITNESS foam-contact '+result['exporter_sha256'] in replay['stdout'],'fresh replay executed current exporter')
            for name in [*outputs,'export-report.json']:
                module.require((folder/'replay'/name).read_bytes()==(HERE/'candidates/v2'/name).read_bytes(),name+': fresh replay exact')
            result['fresh_replay']=replay
            source=module_path.read_text()
            old='alpha = (original[3] * (255 - a) + 127) // 255'
            new='alpha = 0 if a >= 250 else original[3]'
            module.require(source.count(old)==1,'mutation target exactly once')
            mutant=folder/'export-wrong-cutoff.py'
            mutant.write_text(source.replace(old,new),encoding='utf-8')
            bad=run([sys.executable,'-B',str(Path(__file__)), '--probe',str(mutant)])
            mutant_sha=module.sha(mutant.read_bytes())
            module.require(bad['exit_code']!=0 and 'foam alpha visibility at master alpha 253: expected 2, got 0' in bad['stderr'] and 'WITNESS foam-contact-test '+mutant_sha in bad['stdout'],'executed wrong-cutoff mutant named alpha253 failure')
            restored=run([sys.executable,'-B',str(Path(__file__)), '--probe',str(module_path)])
            module.require(restored['exit_code']==0 and 'WITNESS foam-contact-test '+result['exporter_sha256'] in restored['stdout'],'restored fresh-process positive')
            result['mutation']={'status':'FIRED','change':{'before':old,'after':new},'mutant_sha256':mutant_sha,'failure':bad,'restored':restored}
        result['final_frozen_input_check']=module.prepared()==recipe
    path=HERE/f'verification-{args.phase}.json'
    path.write_bytes(module.encode(result))
    print('PASS '+args.phase+' '+module.sha(path.read_bytes()))


if __name__=='__main__':
    main()
