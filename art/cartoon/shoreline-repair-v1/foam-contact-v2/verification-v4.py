"""Focused V4 readback and fresh replay; existing mask/filter tests are inherited."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contact_ground_v4',HERE/'export_v4.py')
export=importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
mask,_=export.delegate().helpers()
phase=sys.argv[1] if len(sys.argv)==2 else ''
mask.require(phase in ('smoke','regression'),'phase must be smoke or regression')
recipe=json.loads((HERE/'recipe-v4.json').read_bytes())
outputs,report=export.render(recipe)
outputs['export-report.json']=mask.encode(report)
for name,raw in outputs.items():
    mask.require((HERE/'candidates/v4'/name).read_bytes()==raw,name+': selected actual readback')
mask.require(report['uniform_resample_count']==1 and report['affine_forward']==[.5,0,-64,0,.5,-192],'unchanged fixed affine and one resample')
result={'status':'PASS','phase':phase,'exporter_sha256':mask.sha((HERE/'export_v4.py').read_bytes()),
        'checker_sha256':mask.sha(Path(__file__).read_bytes()),'recipe_sha256':mask.sha((HERE/'recipe-v4.json').read_bytes()),
        'source_sha256':export.SOURCE_SHA,'readback_files':len(outputs),
        'fixed_affine':report['affine_forward'],'resample_count':report['uniform_resample_count'],
        'contact_samples':report['ground_contacts']}
if phase=='regression':
    smoke=json.loads((HERE/'verification-v4-smoke.json').read_bytes())
    mask.require(smoke['status']=='PASS' and smoke['exporter_sha256']==result['exporter_sha256'],'matching smoke before replay')
    with tempfile.TemporaryDirectory(prefix='ground-contact-v4-') as temp:
        replay=Path(temp)/'replay'
        p=subprocess.run([sys.executable,'-B',str(HERE/'export_v4.py'),'--output',str(replay)],capture_output=True,text=True)
        mask.require(p.returncode==0 and 'WITNESS contact-ground-v4 '+result['exporter_sha256'] in p.stdout,'fresh selected exporter executed')
        for name,raw in outputs.items():
            mask.require((replay/name).read_bytes()==raw,name+': fresh replay identity')
        result['fresh_replay']={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'compared_files':len(outputs),
            'command':'python -B art/cartoon/shoreline-repair-v1/foam-contact-v2/export_v4.py --output <fresh-directory>'}
    result['preserved_ancestors']=[]
    for version,recipe_sha,report_sha in (
        (2,'fb4d5c4b826c4cacc7066e5562830175473bfd9e0eb5a51fe011d3aae44c9d52','55f6e0010e02fad0ef4adb416153d4af1f40cb487a58113ba4e6d68e41a0fbbb'),
        (3,'f81a4b2e0944537d98c7a06270dd5d514dc63a87a47e916b2d5baa340ac25d7a','54520d4d4e71d1fec9e757b11acc4a0bececcafd807bc04744c12a6ea27be882')):
        mask.require(mask.sha((HERE/f'recipe-v{version}.json').read_bytes())==recipe_sha,f'V{version}: prior recipe unchanged')
        prior_report=(HERE/f'candidates/v{version}/export-report.json').read_bytes()
        mask.require(mask.sha(prior_report)==report_sha,f'V{version}: prior report unchanged')
        prior=json.loads(prior_report)
        for name,digest in prior['outputs_sha256'].items():
            mask.require(mask.sha((HERE/f'candidates/v{version}'/name).read_bytes())==digest,f'V{version}: prior output '+name)
        result['preserved_ancestors'].append({'version':version,'recipe_sha256':recipe_sha,'report_sha256':report_sha,'output_files':len(prior['outputs_sha256']),'status':'PASS'})
path=HERE/f'verification-v4-{phase}.json'
path.write_bytes(mask.encode(result))
print('PASS '+phase+' '+mask.sha(path.read_bytes()))
