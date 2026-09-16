"""Ordered checks and executed isolated source-negative control witnesses."""
import hashlib,json,os,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'build/character-inventory/scene-map/checks'
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def run(label,phase,override=None):
    env=os.environ.copy()
    if override:
        env['SCENE_MAP_HELPER']=str(override)
    result=subprocess.run([sys.executable,'-B',str(HERE/'test_scene_map.py'),'--phase',phase],
        cwd=ROOT,env=env,capture_output=True)
    (OUT/(label+'.stdout.txt')).write_bytes(result.stdout)
    (OUT/(label+'.stderr.txt')).write_bytes(result.stderr)
    return result

records=[]
for phase in ['smoke','regression']:
    result=run(phase,phase)
    assert result.returncode==0,result.stderr.decode()
    records.append({'name':phase,'exit_code':result.returncode,'stderr_sha256':sha(result.stderr)})
source=(HERE/'build_scene_map.py').read_text(encoding='utf-8')
for name,old,new,witness in [
    ('ambiguous-slot-resolved','unique = len(candidates)==1','unique = len(candidates)>=1','test_reused_slot_stays_ambiguous'),
    ('load-slot-guard-disabled','if selected is None:','if False and selected is None:','test_missing_load_selector_is_refused'),
    ('original-identity-disabled','if digest != inputs[key]:','if False and digest != inputs[key]:','test_original_identity_guard'),
    ('identity-guard-disabled',"if value['payload_sha256'] != known[name]['payload_sha256']:","if False and value['payload_sha256'] != known[name]['payload_sha256']:",'test_current_resource_identity_guard')]:
    assert source.count(old)==1
    mutant=OUT/(name+'.py')
    mutant.write_text(source.replace(old,new),encoding='utf-8',newline='\n')
    result=run(name,'regression',mutant)
    text=result.stderr.decode()
    assert result.returncode!=0 and ('FAIL: '+witness in text) and text.count('FAIL: ')==1 and 'ERROR: ' not in text,text
    records.append({'name':name,'status':'FIRED','exit_code':result.returncode,'helper_sha256':sha(mutant.read_bytes()),
        'witness':witness,'stderr_sha256':sha(result.stderr),
        'method':'Fresh Python process imported this distinct mutated helper path; maintained/source files untouched.'})
result=run('restored-regression','regression')
assert result.returncode==0,result.stderr.decode()
records.append({'name':'restored-regression','exit_code':0,'stderr_sha256':sha(result.stderr)})
report={'status':'PASS','helper_sha256':sha((HERE/'build_scene_map.py').read_bytes()),
    'tests_sha256':sha((HERE/'test_scene_map.py').read_bytes()),'runner_sha256':sha(Path(__file__).read_bytes()),
    'records':records,'native_scenes_executed':False}
(OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))
