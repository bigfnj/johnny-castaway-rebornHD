"""Smoke then fresh exact replay and focused changed-recipe controls."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image
import export

HERE=Path(__file__).resolve().parent

def run(phase,output):
    assert not output.exists(),'fresh verification output'
    recipe=HERE/'recipe-v1.json';folder=HERE/'candidates/v1';selected=json.loads(recipe.read_bytes());report=json.loads((folder/'export-report.json').read_bytes())
    checks=[];commands=[]
    if phase=='regression':
        previous=json.loads((HERE/'verification-smoke.json').read_bytes())
        assert previous['status']=='PASS' and previous['exporter_sha256']==export.sha(HERE/'export.py'),'matching smoke first'
    with Image.open(folder/'BMP/HOLIDAY.BMP/003.png') as image:assert image.mode=='RGBA' and image.size==(304,94),'canvas and mode'
    checks.append('304x94 RGBA and original runtime origin')
    assert report['runtime_ready'] and report['outside_runtime_alpha8_pixels']==0 and report['outside_runtime_max_alpha']<8,'source and filtered meaningful fit'
    assert selected['frames'][0]['affine_forward']==[.2116,0,-10.932,0,.2116,-68.0552] and selected['frames'][0]['source_sha256']==export.SOURCE_SHA,'exact requested inset and clean raw'
    checks.append('Exact 8% clean-source affine and meaningful alpha fit')
    assert all(export.sha(folder/p)==export.sha(HERE.parent/'candidates/v5'/p) for p in report['unchanged_v5_props_sha256']),'unchanged other props'
    checks.append('Other three props byte-identical')
    controls=[]
    if phase=='regression':
        command=[sys.executable,'-B',str(HERE/'export.py'),'--recipe',str(recipe),'--output',str(folder),'--check']
        result=subprocess.run(command,capture_output=True,text=True);witness='WITNESS banner-inset-export '+export.sha(HERE/'export.py')
        assert result.returncode==0 and witness in result.stdout and 'PASS inset export' in result.stdout,'fresh exporter replay witness'
        commands.append({'argv':command,'stdout':result.stdout,'stderr':result.stderr,'exit_code':result.returncode})
        checks.append('Fresh process exact PNG, padded output and report replay')
        for name,change in [('wrong_scale',lambda r:r['frames'][0].update(scale=.23)),('wrong_anchor',lambda r:r['frames'][0].update(target_anchor=[150,.08])),('wrong_affine',lambda r:r['frames'][0]['affine_forward'].__setitem__(2,-27.1))]:
            damaged=copy.deepcopy(selected);change(damaged)
            try:export.render(damaged)
            except ValueError as error:
                assert str(error)=='003: source or fixed V5 recipe differs',str(error)
                controls.append({'name':name,'status':'FIRED','failure':str(error)})
            else:raise AssertionError('SURVIVED '+name)
        outputs,restored=export.render(selected)
        assert outputs['BMP/HOLIDAY.BMP/003.png']==(folder/'BMP/HOLIDAY.BMP/003.png').read_bytes(),'restored exact positive'
    output.write_text(json.dumps({'status':'PASS','phase':phase,'exporter_sha256':export.sha(HERE/'export.py'),
        'checker_sha256':export.sha(Path(__file__)),'recipe_sha256':export.sha(recipe),'runtime_sha256':export.sha(folder/'BMP/HOLIDAY.BMP/003.png'),
        'checks':checks,'controls':controls,'commands':commands},indent=2)+'\n',encoding='utf-8')
    print('PASS',phase,len(checks),'checks',len(controls),'controls',export.sha(output))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('smoke','regression'),required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.phase,a.output)
