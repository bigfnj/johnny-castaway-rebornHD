"""Bind the corrected authoring metadata to unchanged historical shown pixels."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    output=HERE/'reproduction-v2.json';assert not output.exists(),'fresh V2 reproduction binder'
    report=json.loads((HERE/'candidates/v2/export-report.json').read_bytes())
    assert sha(HERE/'recipe-v2.json')==report['recipe_sha256'],'V2 exact saved recipe/report bytes'
    for name in ('verification-v2-smoke.json','verification-v2-regression.json'):
        data=json.loads((HERE/name).read_bytes());assert data['status']=='PASS' and data['recipe_sha256']==report['recipe_sha256'],'V2 verification identity'
    payloads={}
    for name,expected in report['outputs_sha256'].items():
        assert sha(HERE/'candidates/v2'/name)==sha(HERE/'candidates/v1'/name)==expected,'V1/V2 exact payload '+name
        payloads[name]=expected
    names=['export_v2.py','check_export_v2.py','recipe-v2.json','verification-v2-smoke.json','verification-v2-regression.json','REPRODUCTION-V2.md','preserve_export_v2.py']
    names.extend(p.relative_to(HERE).as_posix() for p in (HERE/'candidates/v2').rglob('*') if p.is_file())
    historical=['export.py','recipe-v1.json','candidates/v1/export-report.json','native/evidence-v1/evidence.json','native/evidence-v1/readback.json','review/evidence/evidence.json','review/page/review.html','review/page/manifest.json']
    record={'schema_version':1,'status':'PASS','files_sha256':{name:sha(HERE/name) for name in names},
        'historical_sha256':{name:sha(HERE/name) for name in historical},'identical_v1_v2_payloads_sha256':payloads,
        'v1_limitation':report['historical_v1_recipe'],'v2_recipe_sha256':report['recipe_sha256'],
        'scope':'Use V2 exact LF metadata for integration. PNG pixels match shown V1, so historical native/browser evidence remains applicable. No V1 overwrite, new capture or production promotion.'}
    output.write_bytes((json.dumps(record,indent=2)+'\n').encode('utf-8'))
    assert all(sha(HERE/p)==v for field in ('files_sha256','historical_sha256') for p,v in record[field].items())
    print('PASS V2 reproduction binder',sha(output))

if __name__=='__main__':main()
