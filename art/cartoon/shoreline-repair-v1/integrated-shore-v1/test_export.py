"""Static ownership readback, independent foam pixels and executed bad-alpha control."""
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

HERE=Path(__file__).resolve().parent


def load(path):
    spec=importlib.util.spec_from_file_location('tested_integrated_export',path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def command(args):
    p=subprocess.run(args,capture_output=True,text=True)
    return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}


def probe(path):
    actual=load(HERE/'export.py')
    m=load(path)
    # Relocate only file lookup globals for a scratch mutant. Source bytes and
    # changed guard are loaded from the named mutant and identified below.
    for name in ('HERE','ROOT','SOURCE','COMPARISON','ARCHIVE','FILTER','MASK'):
        setattr(m,name,getattr(actual,name))
    original_helpers=m.helpers
    base,_=original_helpers()
    print('EXECUTED EXPORT SHA '+base.sha(path.read_bytes()),flush=True)
    witnesses=[]
    def altered_helpers():
        b,mask=original_helpers()
        original=mask.occlude
        def inject(foam,ground,origin,box):
            retained,stats=original(foam,ground,origin,box)
            if not witnesses:
                for y in range(foam.height):
                    for x in range(foam.width):
                        gx,gy=x+origin[0]-box[0],y+origin[1]-box[1]
                        a=ground.getpixel((gx,gy))[3] if 0<=gx<ground.width and 0<=gy<ground.height else 0
                        pixel=foam.getpixel((x,y))
                        if pixel[3]==0 and a>0:
                            retained.putpixel((x,y),(*pixel[:3],a))
                            witnesses.append({'frame':3,'local':[x,y],'world':[x+origin[0],y+origin[1]],'source_foam_alpha':0,'introduced_ground_alpha':a})
                            print('INJECTED '+json.dumps(witnesses[0]),flush=True)
                            return retained,stats
                raise AssertionError('no actual ground/transparent-foam witness')
            return retained,stats
        mask.occlude=inject
        return b,mask
    m.helpers=altered_helpers
    try:
        outputs,_=m.render(m.prepared())
    except ValueError as exc:
        print('REFUSED '+str(exc),file=sys.stderr)
        return 1
    base.require(bool(witnesses),'injection actually executed')
    print('ACCEPTED CORRUPT003 SHA '+base.sha(outputs['BMP/BACKGRND.BMP/003.png']))
    return 0


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=('smoke','regression'))
    p.add_argument('--probe',type=Path)
    args=p.parse_args()
    if args.probe:
        return probe(args.probe)
    m=load(HERE/'export.py')
    base,_=m.helpers()
    base.require(args.phase is not None,'phase required')
    recipe=json.loads((HERE/'recipe-v1.json').read_bytes())
    original_helpers=m.helpers
    calls=[]
    def observed_helpers():
        b,mask=original_helpers()
        original=b.resample
        def observed(*args,**kwargs):
            calls.append(1)
            return original(*args,**kwargs)
        b.resample=observed
        return b,mask
    m.helpers=observed_helpers
    outputs,report=m.render(recipe)
    m.helpers=original_helpers
    base.require(len(calls)==1,'actual single resample call')
    outputs['export-report.json']=base.encode(report)
    for name,raw in outputs.items():
        base.require((HERE/'candidates/v1'/name).read_bytes()==raw,name+': saved readback')
    ground=Image.open(io.BytesIO(outputs['BMP/BACKGRND.BMP/000.png'])).convert('RGBA')
    audit=Image.open(io.BytesIO(outputs['ground-audit.png'])).convert('RGBA')
    base.require(ground.tobytes()==audit.crop((10,148,650,328)).tobytes(),'000: exact sole static ground crop')
    base.require(ground.getpixel((574,177))==(0,0,0,1) and ground.getpixel((574,178))==(0,0,0,1),'000: both alpha1 fringe pixels retained')
    base.require([r['frame'] for r in recipe['frames'] if 'footprint' in r]==[0],'footprint only on000')
    result={'status':'PASS','phase':args.phase,'exporter_sha256':base.sha((HERE/'export.py').read_bytes()),
            'test_sha256':base.sha(Path(__file__).read_bytes()),'recipe_sha256':base.sha((HERE/'recipe-v1.json').read_bytes()),
            'readback_files':len(outputs),'ground_ownership':'000 exact crop; zero filtered alpha outside; alpha1 fringe retained',
            'resample_count':report['uniform_resample_count'],'observed_resample_calls':len(calls)}
    if args.phase=='regression':
        smoke=json.loads((HERE/'verification-smoke.json').read_bytes())
        base.require(smoke['status']=='PASS' and smoke['exporter_sha256']==result['exporter_sha256'],'matching smoke before regression')
        rows=[]
        with zipfile.ZipFile(m.ARCHIVE) as archive:
            for row in recipe['frames'][1:]:
                foam=Image.open(io.BytesIO(archive.read(row['source_member']))).convert('RGBA')
                rendered=Image.open(io.BytesIO(outputs[row['path']])).convert('RGBA')
                empty_under_ground=0
                for y in range(foam.height):
                    for x in range(foam.width):
                        gx=x+row['logical_origin_hd'][0]-540
                        gy=y+row['logical_origin_hd'][1]-548
                        a=ground.getpixel((gx,gy))[3] if 0<=gx<640 and 0<=gy<180 else 0
                        source=foam.getpixel((x,y))
                        expected=(*source[:3],round(source[3]*(255-a)/255))
                        base.require(rendered.getpixel((x,y))==expected,f"{row['frame']:03}: independent foam-only RGB/alpha at {x},{y}")
                        empty_under_ground+=source[3]==0 and a>0
                rows.append({'frame':row['frame'],'checked_pixels':foam.width*foam.height,'transparent_foam_over_ground_witnesses':empty_under_ground})
        result['all_foam_pixels']=rows
        # Distinguish one static A128 draw from a ground copy in an animated layer.
        unit=Image.new('RGBA',(1,1),(170,120,60,128))
        empty=Image.new('RGBA',(1,1),(255,255,255,0))
        _,mask=m.helpers()
        foam_only,_=mask.occlude(empty,unit,(0,0),(0,0,1,1))
        single=Image.alpha_composite(unit,foam_only).getpixel((0,0))[3]
        duplicate=Image.alpha_composite(unit,unit).getpixel((0,0))[3]
        base.require(single==128 and duplicate==192,'A128 ownership witness versus duplicate draw')
        result['partial_alpha_control']={'one_owner':single,'duplicate_draw':duplicate}
        with tempfile.TemporaryDirectory(prefix='integrated-shore-') as temp:
            folder=Path(temp)
            replay=command([sys.executable,'-B',str(HERE/'export.py'),'--output',str(folder/'replay')])
            base.require(replay['exit_code']==0 and 'WITNESS integrated-shore '+result['exporter_sha256'] in replay['stdout'],'fresh selected exporter executed')
            for name,raw in outputs.items():
                base.require((folder/'replay'/name).read_bytes()==raw,name+': fresh replay exact')
            result['fresh_replay']=replay
            rejected=command([sys.executable,'-B',str(Path(__file__)),'--probe',str(HERE/'export.py')])
            expected='REFUSED 003: foam-only output introduced alpha outside source foam'
            base.require(rejected['exit_code']==1 and expected in rejected['stderr'] and 'EXECUTED EXPORT SHA '+result['exporter_sha256'] in rejected['stdout'],'actual003 bad ground alpha named refusal')
            source=(HERE/'export.py').read_text()
            old="base.require(all(a[3] or not b[3] for a,b in zip(original,actual)),label+': foam-only output introduced alpha outside source foam')"
            new="base.require(True,label+': foam-only output introduced alpha outside source foam')"
            base.require(source.count(old)==1,'one ownership guard-removal target')
            mutant=folder/'mutant-export.py'
            mutant.write_text(source.replace(old,new),encoding='utf-8')
            digest=base.sha(mutant.read_bytes())
            admitted=command([sys.executable,'-B',str(Path(__file__)),'--probe',str(mutant)])
            base.require(admitted['exit_code']==0 and 'EXECUTED EXPORT SHA '+digest in admitted['stdout'] and 'ACCEPTED CORRUPT003 SHA ' in admitted['stdout'],'guard removal executed and admitted changed actual003')
            result['ownership_mutation']={'status':'FIRED','original_refusal':rejected,'removed_guard':old,'replacement':new,'mutant_sha256':digest,'mutant_acceptance':admitted}
        restored,restored_report=m.render(recipe)
        base.require(all(restored[k]==v for k,v in outputs.items() if k!='export-report.json'),'restored selected outputs')
        base.require(base.encode(restored_report)==outputs['export-report.json'],'restored selected report')
        result['restored_positive']='PASS'
    path=HERE/f'verification-{args.phase}.json'
    path.write_bytes(base.encode(result))
    print('PASS '+args.phase+' '+base.sha(path.read_bytes()))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
