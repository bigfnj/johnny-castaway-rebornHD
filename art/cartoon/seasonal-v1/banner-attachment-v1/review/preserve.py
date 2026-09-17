"""One-time browser freeze. Replay uses fresh ignored outputs, not this writer."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageChops

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def preserve(review,controls,package_controls,captures):
    page=HERE/'page';evidence=HERE/'evidence'
    assert not page.exists() and not evidence.exists(),'fresh browser freeze required'
    manifest=json.loads((review/'manifest.json').read_bytes());publication=json.loads((review/'publication.json').read_bytes())
    for name,expected in publication['files_sha256'].items():assert sha(review/name)==expected,'publication identity '+name
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json'):
        record=json.loads((review/name).read_bytes())
        assert record['status']=='PASS' and record['html_sha256']==sha(review/'review.html') and record['manifest_sha256']==sha(review/'manifest.json'),'final matching browser proof'
    for source in (controls,package_controls):assert json.loads(source.read_bytes())['status']=='PASS'
    page.mkdir();evidence.mkdir();copies={}
    def copy(source,dest):
        dest.write_bytes(source.read_bytes());assert sha(source)==sha(dest)
        copies[dest.relative_to(HERE).as_posix()]={'source':source.relative_to(ROOT).as_posix(),'sha256':sha(dest)}
    for name in publication['files_sha256']:copy(review/name,page/name)
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json','publication.json'):
        copy(review/name,evidence/name)
    for source in review.glob('browser-*.png'):copy(source,evidence/source.name)
    copy(controls,evidence/'review-input-controls.json');copy(package_controls,evidence/'package-input-controls.json')
    endpoint={}
    for key in manifest['cases']:
        folder=captures/key/'candidate/smoke';rows=json.loads((folder/'report.json').read_bytes())['displays']
        first=rows[0];last=[r for r in rows if r['time_ms']==1440][-1]
        with Image.open(folder/first['file']) as a,Image.open(folder/last['file']) as b:
            bbox=ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox()
        endpoint[key]={'first_png_sha256':first['png_sha256'],'endpoint_png_sha256':last['png_sha256'],
                       'difference_bbox':bbox,'phase_tuple_equal':first['phases']==last['phases']}
    save(evidence/'loop-boundary.json',{'method':'Exact RGB difference of native first and last observed 1440 ms frames. Bounding boxes do not identify a particular animation routine.','cases':endpoint})
    binders={}
    for name in ('evidence.json','readback.json'):
        path=HERE.parent/'native/evidence-v3'/name;binders[path.relative_to(ROOT).as_posix()]=sha(path)
    dependencies=[ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/offshore-scene-review-v1'/name for name in ('build_review.py','publish.py')]
    helper_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in [*HERE.glob('*.py'),HERE/'review-template.html',HERE/'README.md',HERE.parent/'prepare.py',HERE.parent/'check_preparation.py',*dependencies]}
    files={p.relative_to(HERE).as_posix():sha(p) for folder in (page,evidence) for p in folder.rglob('*') if p.is_file()}
    save(evidence/'evidence.json',{'status':'PASS','files_sha256':files,'copies':copies,'helper_sha256':helper_hashes,'native_binders':binders,
        'url':publication['url'],'html_sha256':sha(page/'review.html'),'manifest_sha256':sha(page/'manifest.json'),
        'limits':'Three native banner comparisons and exact browser delivery. Human attachment approval pending at freeze. No production update or claim that shoreline placement is resolved.'})
    assert all(sha(HERE/rel)==digest for rel,digest in files.items())
    print('PASS browser freeze',len(files),'files',sha(evidence/'evidence.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);p.add_argument('--controls',type=Path,required=True);p.add_argument('--package-controls',type=Path,required=True);p.add_argument('--captures',type=Path,required=True)
    a=p.parse_args();preserve(a.review.resolve(),a.controls.resolve(),a.package_controls.resolve(),a.captures.resolve())
