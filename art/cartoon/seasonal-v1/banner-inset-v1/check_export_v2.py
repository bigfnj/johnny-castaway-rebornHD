"""Focused recipe-byte proof; no artwork, native or browser re-execution."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import export_v2 as exporter

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
def digest(path):return exporter.sha(path.read_bytes())

def check(phase,output,scratch):
    assert not output.exists(),'fresh verification record'
    recipe=HERE/'recipe-v2.json';folder=HERE/'candidates/v2';prior=HERE/'candidates/v1'
    report=json.loads((folder/'export-report.json').read_bytes())
    checks=[];controls=[];runs=[]
    value,raw=exporter.read_recipe(recipe)
    assert digest(recipe)==report['recipe_sha256'],'exact recipe/report saved-byte hash'
    checks.append('Exact UTF-8 LF recipe bytes match export report SHA256')
    for name,expected in report['outputs_sha256'].items():
        assert digest(folder/name)==expected and (folder/name).read_bytes()==(prior/name).read_bytes(),'shown V1 payload unchanged: '+name
    checks.append('All runtime PNGs and padded banner are byte-identical to shown V1')
    assert digest(HERE/'recipe-v1.json')==report['historical_v1_recipe']['actual_bytes_sha256'],'historical V1 recipe unchanged'
    if phase=='regression':
        smoke=json.loads((HERE/'verification-v2-smoke.json').read_bytes())
        assert smoke['status']=='PASS' and smoke['exporter_sha256']==digest(HERE/'export_v2.py'),'matching V2 smoke first'
        command=[sys.executable,'-B',str(HERE/'export_v2.py'),'--recipe',str(recipe),'--output',str(folder),'--check']
        result=subprocess.run(command,capture_output=True,text=True)
        witness='WITNESS banner-inset-export-v2 '+digest(HERE/'export_v2.py')
        assert result.returncode==0 and witness in result.stdout and 'PASS inset export V2' in result.stdout,'fresh exporter replay witness'
        runs.append({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        checks.append('Fresh process reproduces exact recipe binding, PNGs and export report')
        assert not scratch.exists(),'fresh damaged-recipe scratch';scratch.mkdir(parents=True)
        damaged=scratch/'recipe-crlf.json';damaged.write_bytes(raw.replace(b'\n',b'\r\n'))
        command=[sys.executable,'-B',str(HERE/'export_v2.py'),'--recipe',str(damaged),'--output',str(scratch/'must-not-exist')]
        result=subprocess.run(command,capture_output=True,text=True)
        expected='recipe-crlf.json: recipe bytes must be canonical UTF-8 LF'
        assert result.returncode!=0 and witness in result.stdout and result.stderr.count('ValueError: '+expected)==1 and not (scratch/'must-not-exist').exists(),'named CRLF damaged-input refusal'
        controls.append({'name':'CRLF_recipe_bytes','status':'FIRED','failure':expected,'source_witness':witness})
        runs.append({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        exporter.read_recipe(recipe)
    record={'status':'PASS','phase':phase,'exporter_sha256':digest(HERE/'export_v2.py'),'checker_sha256':digest(Path(__file__)),
        'recipe_sha256':digest(recipe),'export_report_sha256':digest(folder/'export-report.json'),
        'historical_v1_actual_recipe_sha256':digest(HERE/'recipe-v1.json'),'checks':checks,'controls':controls,'runs':runs,
        'scope':'Metadata serialization correction only. V1 runtime PNGs and shown native/browser evidence remain exact.'}
    output.write_bytes(exporter.encode(record));print('PASS',phase,digest(output))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('smoke','regression'),required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--scratch',type=Path,required=True);a=p.parse_args()
    check(a.phase,a.output,a.scratch)
