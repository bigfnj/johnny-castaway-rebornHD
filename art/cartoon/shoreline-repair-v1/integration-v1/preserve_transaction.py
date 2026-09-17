"""Freeze the selected V2 transaction proof without changing earlier binders."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
WORK=ROOT/'build/shoreline-repair-v1/integration-v1/promotion-transaction-v3'
OUT=HERE/'promotion-transaction-v2'
sha=lambda raw:hashlib.sha256(raw).hexdigest()


def main():
    report=json.loads((WORK/'verification.json').read_bytes())
    assert report['status']=='PASS' and report['executed_rollback_removal_detected']
    OUT.mkdir(exist_ok=True)
    sources={p.name:p for p in WORK.iterdir() if p.is_file() and p.suffix in ('.json','.txt','.py')}
    local=WORK/'fixture'/HERE.relative_to(ROOT)
    sources.update({p.name:p for p in local.glob('fault-*.py')})
    for name,path in sources.items():
        raw=path.read_bytes();target=OUT/name
        if target.exists():assert target.read_bytes()==raw,name
        target.write_bytes(raw)
    files={('promotion-transaction-v2/'+name):sha((OUT/name).read_bytes()) for name in sorted(sources)}
    external={name:sha((HERE/name).read_bytes()) for name in ('promote_v2.py','promote.py','integrate.py','test_promote_v2.py','preserve_transaction.py','PROMOTION.md')}
    binder={'schema_version':1,'status':'PASS','paths_relative_to':HERE.relative_to(ROOT).as_posix(),
            'files_sha256':files,'external_files_sha256':external,'case_count':5,
            'scope':'Disposable transaction fault injection and rollback-removal/restoration proof. Synthetic native data; no actual production promotion.',
            'excluded':'Copied source fixture and archives remain in ignored scratch. Earlier promotion-preflight binder is immutable.'}
    target=OUT/'evidence.json';target.write_text(json.dumps(binder,indent=2)+'\n',encoding='utf-8',newline='\n')
    for path,digest in {**files,**external}.items():assert sha((HERE/path).read_bytes())==digest,path
    print(json.dumps({'status':'PASS','copied_files':len(files),'external_files':len(external),'binder_sha256':sha(target.read_bytes())}))


if __name__=='__main__':main()
