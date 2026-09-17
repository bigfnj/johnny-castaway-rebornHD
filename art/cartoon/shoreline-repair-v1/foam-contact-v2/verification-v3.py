"""Focused contact-ground source binding, smoke and fresh replay."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contact_ground_v3',HERE/'export_v3.py')
export=importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
mask,_=export.helpers()
phase=sys.argv[1] if len(sys.argv)==2 else ''
mask.require(phase in ('smoke','regression'),'phase must be smoke or regression')
recipe=json.loads((HERE/'recipe-v3.json').read_bytes())
outputs,report=export.render(recipe)
outputs['export-report.json']=mask.encode(report)
for name,raw in outputs.items():
    mask.require((HERE/'candidates/v3'/name).read_bytes()==raw,name+': actual readback')
result={'status':'PASS','phase':phase,'exporter_sha256':mask.sha((HERE/'export_v3.py').read_bytes()),
        'checker_sha256':mask.sha(Path(__file__).read_bytes()),'recipe_sha256':mask.sha((HERE/'recipe-v3.json').read_bytes()),
        'readback_files':len(outputs),'uniform_resample_count':report['uniform_resample_count'],
        'fixed_affine':report['affine_forward'],'contact_samples':report['ground_contacts']}
mask.require(report['uniform_resample_count']==1 and report['affine_forward']==[.5,0,-64,0,.5,-192],'one resample with unchanged original affine')
if phase=='regression':
    smoke=json.loads((HERE/'verification-v3-smoke.json').read_bytes())
    mask.require(smoke['status']=='PASS' and smoke['exporter_sha256']==result['exporter_sha256'],'matching smoke before replay')
    with tempfile.TemporaryDirectory(prefix='ground-contact-v3-') as temp:
        replay=Path(temp)/'replay'
        command=[sys.executable,'-B',str(HERE/'export_v3.py'),'--output',str(replay)]
        p=subprocess.run(command,capture_output=True,text=True)
        mask.require(p.returncode==0 and 'WITNESS contact-ground-v3 '+result['exporter_sha256'] in p.stdout,'fresh selected exporter executed')
        for name,raw in outputs.items():
            mask.require((replay/name).read_bytes()==raw,name+': fresh replay identity')
        result['fresh_replay']={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'compared_files':len(outputs),
                                'command':'python -B art/cartoon/shoreline-repair-v1/foam-contact-v2/export_v3.py --output <fresh-directory>'}
    selected=export.SOURCE
    export.SOURCE=HERE.parent/'raw/ground-master-v2.png'
    try:
        export.prepared()
        raise AssertionError('wrong older raw was accepted')
    except ValueError as exc:
        mask.require(str(exc)=='ground-master-v2.png: source identity differs','wrong raw failed for selected source binding')
        result['wrong_raw_control']={'status':'FIRED','failure':str(exc),'method':'Only in-memory source path changed; selected7265... hash retained. No input or recipe file edited.'}
    finally:
        export.SOURCE=selected
    mask.require(export.prepared()==recipe,'restored selected source positive')
    prior=json.loads((HERE/'recipe-v2.json').read_bytes())
    mask.require(mask.prepared()==prior,'V2 frozen recipe and inputs unchanged')
    prior_report=json.loads((HERE/'candidates/v2/export-report.json').read_bytes())
    for name,digest in prior_report['outputs_sha256'].items():
        mask.require(mask.sha((HERE/'candidates/v2'/name).read_bytes())==digest,'V2 frozen output: '+name)
    result['v2_preserved']={'recipe_sha256':mask.sha((HERE/'recipe-v2.json').read_bytes()),
                            'report_sha256':mask.sha((HERE/'candidates/v2/export-report.json').read_bytes()),'runtime_pngs':10,'status':'PASS'}
path=HERE/f'verification-v3-{phase}.json'
path.write_bytes(mask.encode(result))
print('PASS '+phase+' '+mask.sha(path.read_bytes()))
