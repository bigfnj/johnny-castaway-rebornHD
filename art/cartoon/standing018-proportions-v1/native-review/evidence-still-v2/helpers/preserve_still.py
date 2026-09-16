"""One-time evidence writer for the pending-human018 proportion still review."""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
BUILD=ROOT/'build/standing018-proportions'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    dest=HERE/'evidence-still-v2';assert not dest.exists(),'preserve018 still evidence'
    review=BUILD/'still-review-v2-final';native=BUILD/'native-review/color-v2'
    record=json.loads((review/'review-record.json').read_bytes());browser=json.loads((review/'browser-served.json').read_bytes())
    assert browser['status']=='PASS' and browser['record_sha256']==sha((review/'review-record.json').read_bytes()),'bound served018 review record'
    assert browser['html_sha256']==sha((review/'review.html').read_bytes()),'bound served018 HTML'
    for name,digest in record['files_sha256'].items():assert sha((review/name).read_bytes())==digest,'unchanged reviewed file:'+name
    prep=json.loads((native/'preparation.json').read_bytes());summary=json.loads((native/'summary.json').read_bytes())
    assert summary['status']=='PASS' and record['candidate_summary_sha256']==sha((native/'summary.json').read_bytes()),'bound native018 summary'
    assert record['candidate_preparation_sha256']==sha((native/'preparation.json').read_bytes()),'bound candidate preparation'
    for n,h in prep['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'unchanged protected source/production:'+n
    selected=[]
    selected += [p for p in review.iterdir() if p.is_file()]
    selected += [native/n for n in ('preparation.json','summary.json','launch.json','launch.log','color-record.json')]
    selected += [native/'front_arc'/phase/name for phase in ('smoke','full','repeat') for name in ('report.json','capture.log')]
    selected += [p for p in (BUILD/'still-binding-v2-final').iterdir() if p.is_file()]
    # Keep the preceding unnormalized v2 smoke as separate historical evidence.
    selected += [BUILD/'native-review/v2'/n for n in ('preparation.json','launch.json','launch.log','front_arc-smoke/report.json','front_arc-smoke/capture.log','front_arc-smoke/display-001.png')]
    dest.mkdir();files={}
    for source in selected:
        name=source.relative_to(BUILD).as_posix();target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        assert source.read_bytes()==target.read_bytes(),'exact evidence copy:'+name
        files[name]=sha(target.read_bytes())
    for source in HERE.iterdir():
        if source.is_file():
            name='helpers/'+source.name;target=dest/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target);files[name]=sha(target.read_bytes())
    check=ROOT/'art/cartoon/skin-tone-v1/contact018-review-v1/check_review.py'
    target=dest/'helpers/reused-check_review.py';shutil.copyfile(check,target);files['helpers/reused-check_review.py']=sha(target.read_bytes())
    links={
        'color_evidence':'art/cartoon/standing018-proportions-v1/color/evidence-v2/evidence.json',
        'original_contact_evidence':'art/cartoon/skin-tone-v1/contact018-review-v1/evidence-v1/evidence.json',
        'skin_motion_evidence':'art/cartoon/skin-tone-v1/native-review/evidence-v1/evidence.json',
        'generation_request':'art/cartoon/standing018-proportions-v1/generation-request-v2.json',
        'generation_result':'art/cartoon/standing018-proportions-v1/generation-result-v2.json'}
    bindings={key:{'path':name,'sha256':sha((ROOT/name).read_bytes())} for key,name in links.items()}
    data={'status':'PASS; human still proportion review pending','files_sha256':files,'linked_evidence':bindings,
        'publication_url':'http://127.0.0.1:8932/cartoon-standing018-proportions-v2/review.html','html_sha256':browser['html_sha256'],
        'candidate_archive_sha256':prep['archive_sha256'],'runtime018_sha256':prep['runtime018_sha256'],'executable_sha256':prep['executable_sha256'],
        'native_result':summary,'browser_result':browser,'scope':'Original diagnostic geometry / earlier color-matched018 / revised color-matched018 at identical first Front turn display. Still proportions only; full waypoint and mirrored motion approval remain pending.',
        'regression_scope':'Front turn smoke then36-display full and fresh repeat. Only2 initial018 displays change inside their placed64x154 canvas;34 other displays stay exact. Local and served six pixel crops/four hashes/expand-collapse pass. Changed valid PNG with stale capture report is rejected; restored positive passes.',
        'preserved_prior_attempts':'Unnormalized v2 one-frame smoke is separate, not selected for publication. Earlier unpublished caption review/control remain scratch; final caption explicitly says longer torso and lower shorts.',
        'excluded_bulk':'Private ZIP/executable/full native PPM series are not copied. Identities and per-display hashes are in retained preparation/reports. Three displayed initial PNGs and prior raw smoke PNG are copied.',
        'reconstruction':'Run the captured launch after restoring pinned baseline observer/archive and color/export inputs. Build a fresh page; do not rerun this writer into historical evidence or overwrite immutable publication.'}
    (dest/'evidence.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    assert all(sha((dest/n).read_bytes())==h for n,h in files.items()),'retained files readback'
    (dest/'readback.json').write_text(json.dumps({'status':'PASS','evidence_sha256':sha((dest/'evidence.json').read_bytes()),'files_checked':len(files),'links_checked':len(bindings),'protected_inputs_checked':len(prep['protected_sha256'])},indent=2)+'\n',encoding='utf-8')
    print('PASS018 still evidence freeze and readback: '+str(len(files))+' exact files, '+str(len(bindings))+' linked records')

if __name__=='__main__':main()
