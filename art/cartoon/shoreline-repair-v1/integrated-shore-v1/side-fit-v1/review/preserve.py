"""One-time exact viewer checkpoint; native images remain in the lossless atlases."""
import argparse
import json
from pathlib import Path
import shutil
import build_review as b

HERE = Path(__file__).resolve().parent

def preserve(review, captures, controls, clock_control, native_evidence):
    page, evidence = HERE/'page', HERE/'evidence-v1'
    assert not page.exists() and not evidence.exists(), 'fresh viewer checkpoint required'
    build=json.loads((review/'build.json').read_bytes())
    manifest=json.loads((review/'manifest.json').read_bytes())
    publication=json.loads((review/'publication.json').read_bytes())
    for name,digest in publication['files_sha256'].items():
        assert b.sha(review/name)==digest, 'published identity '+name
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json'):
        report=json.loads((review/name).read_bytes())
        assert report['status']=='PASS' and report['html_sha256']==build['html_sha256'] and report['manifest_sha256']==build['manifest_sha256'], 'matching browser record'
    control=json.loads(controls.read_bytes())
    assert control['status']=='PASS' and control['builder_sha256']==b.sha(HERE/'build_review.py'), 'matching input controls'
    clock=json.loads(clock_control.read_bytes())
    assert clock['status']=='PASS' and clock['html_sha256']==build['html_sha256'] and clock['manifest_sha256']==build['manifest_sha256'], 'matching clock control'
    native=json.loads(native_evidence.read_bytes())
    assert native.get('status')=='PASS', 'native evidence complete'
    for path,digest in manifest['reports_sha256'].items():
        assert b.sha(b.ROOT/path)==digest, 'native report changed '+path
    assert build['native_summary_sha256']==b.sha(captures/'summary.json'), 'native summary identity'
    page.mkdir()
    evidence.mkdir()
    copies={}
    def copy(source,dest):
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        assert b.sha(source)==b.sha(dest)
        copies[dest.relative_to(HERE).as_posix()]={'source':source.relative_to(b.ROOT).as_posix(),'sha256':b.sha(dest)}
    for name in publication['files_sha256']:
        copy(review/name,page/name)
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json','publication.json'):
        copy(review/name,evidence/name)
    for path in review.glob('browser-*.png'):
        copy(path,evidence/path.name)
    copy(controls,evidence/'input-controls.json')
    copy(clock_control,evidence/'clock-control.json')
    for name in ('failed-attempt.json','checker-before-polling-fix.py'):
        copy(b.ROOT/'build/shoreline-repair-v1/waves-fit-clean-review-v1'/name,evidence/'first-attempt'/name)
    for name in ('inputs.json','summary.json','build.json'):
        copy(captures/name,evidence/'native'/name)
    for rel in manifest['reports_sha256']:
        source=b.ROOT/rel
        copy(source,evidence/'native'/source.relative_to(captures))
    for rel,digest in build['selection_provenance_sha256'].items():
        assert b.sha(b.ROOT/rel)==digest
        copy(b.ROOT/rel,evidence/'selection'/Path(rel).name)
    helpers={p.relative_to(b.ROOT).as_posix():b.sha(p) for p in [*HERE.glob('*.py'),HERE/'review-template.html',HERE/'README.md',b.PACKER]}
    record={'schema_version':1,'status':'PASS','copies':copies,'helpers_sha256':helpers,
            'native_evidence':{'path':native_evidence.relative_to(b.ROOT).as_posix(),'sha256':b.sha(native_evidence)},
            'html_sha256':b.sha(page/'review.html'),'manifest_sha256':b.sha(page/'manifest.json'),
            'url':publication['url'],'package_pair':manifest['package_pair'],
            'scope':'Exact combined wave A/B checkpoint. Earlier placement and new side positions/clean007 use actual native captures; human appearance approval pending at freeze.',
            'limits':'High/night presentation repeats observed wave phases at1440ms, not a whole-scene closure claim. Low tide and Johnny routes retain complete clocks. Native source snapshots and reports are in the linked native binder.'}
    b.save(evidence/'evidence.json',record)
    assert all(b.sha(HERE/p)==v['sha256'] for p,v in copies.items())
    b.save(evidence/'readback.json',{'status':'PASS','exact_copies':len(copies),'evidence_sha256':b.sha(evidence/'evidence.json')})
    print('PASS viewer checkpoint',len(copies),b.sha(evidence/'evidence.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--review',type=Path,required=True)
    p.add_argument('--captures',type=Path,required=True)
    p.add_argument('--controls',type=Path,required=True)
    p.add_argument('--clock-control',type=Path,required=True)
    p.add_argument('--native-evidence',type=Path,required=True)
    a=p.parse_args()
    preserve(a.review.resolve(),a.captures.resolve(),a.controls.resolve(),a.clock_control.resolve(),a.native_evidence.resolve())
