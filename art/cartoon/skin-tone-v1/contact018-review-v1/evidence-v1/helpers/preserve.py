"""One-time small evidence writer for the018 comparison. Do not rerun into frozen evidence."""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
OUT=ROOT/'build/skin-tone/contact018-review-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    dest=HERE/'evidence-v1'
    assert not dest.exists(), 'preserve immutable018 evidence'
    prep=json.loads((OUT/'preparation.json').read_bytes())
    summary=json.loads((OUT/'summary.json').read_bytes())
    assert summary['status']=='PASS'
    review=OUT/'review-v2'
    record=json.loads((review/'review-record.json').read_bytes())
    checked=json.loads((review/'browser-served.json').read_bytes())
    assert checked['status']=='PASS' and checked['record_sha256']==sha((review/'review-record.json').read_bytes()), 'checked018 record identity'
    assert checked['html_sha256']==sha((review/'review.html').read_bytes()), 'checked018 HTML identity'
    for n,h in record['files_sha256'].items():assert sha((review/n).read_bytes())==h, 'review bytes:'+n
    for path,digest in prep['protected_sha256'].items():assert sha((ROOT/path).read_bytes())==digest, 'protected source/art:'+path
    paths=['preparation.json','original-build.json','route_driver.c','summary.json','parser-controls.json']
    paths += [f'{kind}/{phase}/{name}' for kind in ('original_scene','original_johnny') for phase in ('smoke','full','repeat') for name in ('report.json','capture.log')]
    paths += [f'current/{phase}/{name}' for phase in ('smoke','full') for name in ('report.json','capture.log')]
    paths += ['review-v2/'+p.name for p in review.iterdir() if p.is_file()]
    paths=sorted(paths)
    dest.mkdir()
    files={}
    for name in paths:
        source=OUT/name;target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        assert source.read_bytes()==target.read_bytes(), 'exact preserved evidence:'+name
        files[name]=sha(target.read_bytes())
    helpers={p.name:sha(p.read_bytes()) for p in HERE.iterdir() if p.is_file()}
    for name in helpers:
        target=dest/'helpers'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(HERE/name,target);files['helpers/'+name]=sha(target.read_bytes())
    commands={
        'prepare':'& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/contact018-review-v1/prepare.py',
        'capture':'docker run --rm --init --network none --mount type=bind,source=<repo>,target=/source,readonly --mount type=bind,source=<repo>/build/skin-tone/contact018-review-v1,target=/out sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72 xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /source/art/cartoon/skin-tone-v1/contact018-review-v1/capture.py',
        'parser_controls':'same docker mounts/image; python3 -B /source/art/cartoon/skin-tone-v1/contact018-review-v1/check_capture.py',
        'build':'& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/contact018-review-v1/build_review.py',
        'browser_local':'& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/contact018-review-v1/check_review.py --review build/skin-tone/contact018-review-v1/review-v2 --report build/skin-tone/contact018-review-v1/review-v2/browser-local.json',
        'publication':'One-time Python copy of the four review-record.files_sha256 entries to a new cartoon-contact018-v1 directory after local PASS and exact local byte checks; no historical publication overwritten.',
        'browser_served':'& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/contact018-review-v1/check_review.py --review build/skin-tone/contact018-review-v1/review-v2 --url http://127.0.0.1:8932/cartoon-contact018-v1/review.html --report build/skin-tone/contact018-review-v1/review-v2/browser-served.json'}
    data={'status':'PASS; diagnostic comparison, no geometry correction or new art approval','files_sha256':files,'helpers_sha256':helpers,
          'commands':commands,'publication_url':'http://127.0.0.1:8932/cartoon-contact018-v1/review.html','html_sha256':checked['html_sha256'],
          'native_summary':summary,'supplied_resource_sha256':prep['packages']['original_scene']['supplied_resource_replacements_sha256'],
          'outside018_canvas_changed_pixels':0,'excluded_bulk':'Diagnostic ZIPs, executable and full/repeat PPM/PNG series stay in scratch; their identities are bound by preparation/build/reports. Three displayed initial PNGs are retained.',
          'source_limits':'Supplied original resources rendered by unchanged port with diagnostic palette. No original-executable color/compositing/timing parity. Two prior failed preparation attempts remain scratch: ZipInfo reuse affected writer in-memory metadata only; subsequent assertion over-broadly rejected data/logo.png. Neither changed source ZIP bytes.',
          'verification':'Both smoke before full/fresh-repeat;36 displays3400ms each; exact native transcript; zero PNG loads original_scene;018 overrides absent and original fallback logged in isolation; six browser pixel crops/four served files/expand-collapse local and served; two altered-input controls.'}
    (dest/'evidence.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    assert all(sha((dest/n).read_bytes())==h for n,h in files.items()), 'all retained bytes re-read'
    (dest/'readback.json').write_text(json.dumps({'status':'PASS','evidence_sha256':sha((dest/'evidence.json').read_bytes()),'files_checked':len(files),'protected_inputs_checked':len(prep['protected_sha256'])},indent=2)+'\n',encoding='utf-8')
    print('PASS frozen018 comparison evidence and readback; '+str(len(files))+' exact bound files')

if __name__=='__main__':main()
