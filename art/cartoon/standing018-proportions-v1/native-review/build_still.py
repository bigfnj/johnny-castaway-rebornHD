"""Build a NEW original/earlier/revised018 still comparison from actual native captures."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
sha=lambda b:hashlib.sha256(b).hexdigest()
BASE_SHA='bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf'
ORIGINAL_SHA='d7797181cf2e30699709946f0983b6899f0c7428785f9c596dea8ac150619f20'

def main():
    print('WITNESS build_still.py SHA256='+sha(Path(__file__).read_bytes()),flush=True)
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists(),'preserve existing018 proportion review'
    summary=json.loads((a.candidate/'summary.json').read_bytes());prep=json.loads((a.candidate/'preparation.json').read_bytes())
    assert summary['status']=='PASS' and summary['ordered_phases']==['smoke','full','repeat'],'completed018 basic native regressions'
    assert summary['archive_sha256']==prep['archive_sha256'] and summary['runtime018_sha256']==prep['runtime018_sha256'],'selected018 capture identity'
    sources={
        'original':ROOT/'build/skin-tone/contact018-review-v1/original_johnny/full',
        'earlier':ROOT/'build/skin-tone/native-review/candidate-v2/front_arc/full',
        'revised':a.candidate/'front_arc/full'}
    labels={'original':'Original pose on Cartoon island','earlier':'Earlier Cartoon018','revised':'Revised Cartoon018'}
    notes={'original':'Original geometry. Diagnostic colors; compare proportions and contact.',
           'earlier':'The earlier pose, before this proportion revision.',
           'revised':'Longer torso and lower shorts. Please judge proportions and both feet.'}
    expected_archives={'original':ORIGINAL_SHA,'earlier':BASE_SHA,'revised':prep['archive_sha256']}
    rows=[];copies={};reports={}
    for kind,folder in sources.items():
        raw=(folder/'report.json').read_bytes();report=json.loads(raw);reports[kind]=report
        assert report['status']=='PASS' and report['clip']=='front_arc' and report['phase']=='full','actual full Front turn:'+kind
        assert report['archive_sha256']==expected_archives[kind] and report['executable_sha256']==prep['executable_sha256'],'bound package/observer:'+kind
        first=report['displays'][0]
        assert first['actual_draw']==[0,478,216,18] and first['logical_ms']==0,'same initial018 pose:'+kind
        png=(folder/first['png']).read_bytes();assert sha(png)==first['png_sha256'],'bound018 PNG:'+kind+':'+str(folder/first['png'])
        with Image.open(folder/first['png']) as image:
            assert image.size==(1280,960) and sha(image.convert('RGB').tobytes())==first['pixels_sha256'],'bound native pixels:'+kind
        copies[kind+'.png']=png
        rows.append({'kind':kind,'label':labels[kind],'note':notes[kind],'image':kind+'.png','png_sha256':sha(png),
            'report':(folder/'report.json').resolve().relative_to(ROOT).as_posix(),'report_sha256':sha(raw),'archive_sha256':report['archive_sha256']})
    for kind in ('original','revised'):
        assert reports[kind]['segments']==reports['earlier']['segments'] and reports[kind]['completed_waits']==reports['earlier']['completed_waits'],'same native path/timing:'+kind
    bundle={'panels':rows,'pose':[940,425,95,175],'feet':[954,548,66,40],'frame':18,'draw':[0,478,216,18],'logical_ms':0}
    template=(HERE/'still-template.html').read_text(encoding='utf-8');assert template.count('__DATA__')==1,'one still data slot'
    copies['review.html']=template.replace('__DATA__',json.dumps(bundle,separators=(',',':'))).encode()
    a.output.mkdir(parents=True)
    for name,raw in copies.items():(a.output/name).write_bytes(raw)
    record={'status':'PASS; HUMAN STILL PROPORTION REVIEW PENDING','bundle':bundle,'panels':rows,'files_sha256':{n:sha(b) for n,b in copies.items()},
        'candidate_preparation_sha256':sha((a.candidate/'preparation.json').read_bytes()),'candidate_summary_sha256':sha((a.candidate/'summary.json').read_bytes()),
        'runtime018_sha256':prep['runtime018_sha256'],'color_record_sha256':prep['color_record_sha256'],
        'builder_sha256':sha(Path(__file__).read_bytes()),'template_sha256':sha((HERE/'still-template.html').read_bytes()),
        'scope':'Original diagnostic geometry, earlier color-matched018 and revised color-matched018 at identical native position. Still proportions only; later three-route motion review remains pending.'}
    (a.output/'review-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('PASS three exact native018 still panels, selected candidate bindings and identical fixed cameras; human proportions pending')

if __name__=='__main__':main()
