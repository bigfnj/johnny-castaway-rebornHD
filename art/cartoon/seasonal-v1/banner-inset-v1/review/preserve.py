"""One-time inset browser/evidence freeze, never a replay output target."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def preserve(review,controls,captures):
    page=HERE/'page';out=HERE/'evidence'
    assert not page.exists() and not out.exists(),'fresh inset browser evidence'
    publication=json.loads((review/'publication.json').read_bytes());manifest=json.loads((review/'manifest.json').read_bytes())
    for name,digest in publication['files_sha256'].items():assert sha(review/name)==digest,'published file identity '+name
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json'):
        proof=json.loads((review/name).read_bytes())
        assert proof['status']=='PASS' and proof['html_sha256']==sha(review/'review.html') and proof['manifest_sha256']==sha(review/'manifest.json'),'matching final browser proof'
    page.mkdir();out.mkdir();copies={}
    def copy(src,dst):
        dst.write_bytes(src.read_bytes());assert sha(src)==sha(dst)
        copies[dst.relative_to(HERE).as_posix()]={'source':src.relative_to(ROOT).as_posix(),'sha256':sha(dst)}
    for name in publication['files_sha256']:copy(review/name,page/name)
    for name in ('browser-smoke.json','browser-regression.json','browser-served-smoke.json','publication.json'):
        copy(review/name,out/name)
    for source in review.glob('browser-*.png'):copy(source,out/source.name)
    assert json.loads(controls.read_bytes())['status']=='PASS';copy(controls,out/'inherited-builder-controls.json')
    original=ROOT/'build/shoreline-repair-v1/offshore-full-v1/captures/day/none/candidate/smoke/display-001.png'
    actual=captures/'day_banner/candidate/smoke/display-001.png'
    runtime=HERE.parent/'candidates/v1/BMP/HOLIDAY.BMP/003.png'
    points=[]
    with Image.open(original) as a,Image.open(actual) as b,Image.open(runtime) as r:
        for p in ((739,311),(1009,313)):
            points.append({'world_hd':p,'without_banner_rgb':a.convert('RGB').getpixel(p),
                           'new_native_rgb':b.convert('RGB').getpixel(p),'inset_runtime_rgba':r.convert('RGBA').getpixel((p[0]-722,p[1]-310))})
    save(out/'corner-observation.json',{'sources':{p.relative_to(ROOT).as_posix():sha(p) for p in (original,actual,runtime)},
        'observed_points':points,'scope':'Two previously measured interior cloth-corner samples render over native green fronds. Visual attachment judgment remains with the user; these samples are not a generic leaf detector.'})
    old=HERE.parents[1]/'banner-attachment-v1/review'
    dependencies=[old/name for name in ('build_review.py','review-template.html','check_review.py','check_inputs.py')]
    dependencies.extend(ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/offshore-scene-review-v1'/name for name in ('build_review.py','publish.py'))
    helpers={p.relative_to(ROOT).as_posix():sha(p) for p in [*HERE.glob('*.py'),HERE/'README.md',*dependencies]}
    owned=('export.py','check_export.py','measure.py','measurements-v1.json','prepare.py','recipe-v1.json','user-direction-v1.json','verification-smoke.json','verification-regression.json')
    authoring={(HERE.parent/name).relative_to(ROOT).as_posix():sha(HERE.parent/name) for name in owned}
    authoring.update({p.relative_to(ROOT).as_posix():sha(p) for p in (HERE.parent/'candidates/v1').rglob('*') if p.is_file()})
    binders={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE.parent/'native/evidence-v1/evidence.json',HERE.parent/'native/evidence-v1/readback.json']}
    files={p.relative_to(HERE).as_posix():sha(p) for folder in (page,out) for p in folder.rglob('*') if p.is_file()}
    save(out/'evidence.json',{'status':'PASS','files_sha256':files,'copies':copies,'helper_sha256':helpers,'authoring_sha256':authoring,'native_binders':binders,
        'url':publication['url'],'html_sha256':sha(page/'review.html'),'manifest_sha256':sha(page/'manifest.json'),
        'limits':'Technical inset-banner comparison and exact browser delivery. Human attachment decision pending at freeze. Previous waves remain visible; their correction is separate. Production unchanged.'})
    assert all(sha(HERE/name)==digest for name,digest in files.items())
    print('PASS inset browser frozen',len(files),sha(out/'evidence.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);p.add_argument('--controls',type=Path,required=True);p.add_argument('--captures',type=Path,required=True);a=p.parse_args()
    preserve(a.review.resolve(),a.controls.resolve(),a.captures.resolve())
