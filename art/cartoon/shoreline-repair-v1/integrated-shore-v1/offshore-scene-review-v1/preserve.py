"""Freeze the checked atlas page and small browser/native evidence links once."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preserve(review,controls):
    page=HERE/'page';evidence=HERE/'evidence'
    assert not page.exists() and not evidence.exists(), 'historical review already preserved'
    manifest=json.loads((review/'manifest.json').read_bytes())
    build=json.loads((review/'build.json').read_bytes())
    smoke=json.loads((review/'browser-smoke.json').read_bytes())
    regression=json.loads((review/'browser-regression.json').read_bytes())
    negative=json.loads(controls.read_bytes())
    publication=json.loads((review/'publication.json').read_bytes())
    assert smoke['status']==regression['status']==negative['status']=='PASS'
    for record in (smoke,regression):
        assert record['html_sha256']==sha(review/'review.html')
        assert record['manifest_sha256']==sha(review/'manifest.json')
        assert record['checker_sha256']==sha(HERE/'check_review.py')
    assert negative['builder_sha256']==sha(HERE/'build_review.py')
    assert negative['checker_sha256']==sha(HERE/'check_inputs.py')
    assert build['html_sha256']==sha(HERE/'review-template.html')
    assert all(sha(review/name)==value for name,value in publication['files_sha256'].items())
    native=HERE.parent/'native/offshore-full-evidence-v1'
    assert sha(native/'evidence.json')=='129a41cd347e05c9a8beb914d156c4b4c1d2aaf35e3d74d109d9a315018addfd'
    assert sha(native/'readback.json')=='62315849d691826e7e4f6fe98ea5175d2347199bc61390c803e0c37e9cb8b0e9'
    page.mkdir();evidence.mkdir()
    copied=[]
    def copy(source,dest):
        shutil.copyfile(source,dest)
        assert sha(source)==sha(dest)
        copied.append({'source':source.relative_to(ROOT).as_posix(),'path':dest.relative_to(HERE).as_posix(),'sha256':sha(dest)})
    for name in publication['files_sha256']:
        copy(review/name,page/name)
    for name in ('browser-smoke.json','browser-regression.json','publication.json'):
        copy(review/name,evidence/name)
    copy(controls,evidence/'input-controls.json')
    for record in (smoke,regression):
        for name,value in record['screenshots_sha256'].items():
            assert sha(review/name)==value
            if not (evidence/name).exists():copy(review/name,evidence/name)
    # Preserve the failed first delivery format as a scoped observation, not a
    # reconstructed execution log. Its actual captures remained unchanged.
    (evidence/'superseded-delivery.json').write_text(json.dumps({
        'status':'SUPERSEDED','format':'3,322 individual crop PNG requests',
        'observations':['First smoke stopped with initial scene load error.',
                        'A second smoke verified the default Pumpkin pixels but timed out after 90 seconds switching to high_clover.',
                        'Replaced by four atlas PNGs; final smoke and regression passed.'],
        'scope':'Observed tool outcomes; not a verbatim captured log. No native capture or artwork change.'},indent=2)+'\n')
    files={p.relative_to(HERE).as_posix():sha(p) for folder in (page,evidence) for p in sorted(folder.rglob('*')) if p.is_file()}
    helpers={p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.html','.md')}
    result={'schema_version':1,'status':'PASS','url':publication['url'],'files_sha256':files,'helper_sha256':helpers,
            'exact_copies':copied,'native_binders':{(native/name).relative_to(ROOT).as_posix():sha(native/name) for name in ('evidence.json','readback.json')},
            'scene_count':len(manifest['cases']),'recorded_frames_in_viewer':sum(len(c['frames']) for c in manifest['cases'].values()),
            'unique_native_images':len(manifest['images']),'atlas_count':len(manifest['atlases']),
            'atlas_bytes':sum((page/name).stat().st_size for name in manifest['atlases']),
            'approval':'Human seasonal placement review pending; offshore direction already selected separately.',
            'limits':'Exact port-rendered scene pixels and logical timing. Existing low-tide, night-background and cloud fallback artwork is retained. No production promotion.'}
    (evidence/'evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    assert all(sha(HERE/name)==value for name,value in files.items())
    print('PASS preserved browser evidence',sha(evidence/'evidence.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review',type=Path,required=True);p.add_argument('--controls',type=Path,required=True)
    a=p.parse_args();preserve(a.review.resolve(),a.controls.resolve())
