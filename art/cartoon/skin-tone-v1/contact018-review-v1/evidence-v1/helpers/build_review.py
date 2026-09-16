"""Three-panel fixed-camera comparison of initial standing018; no artwork edits."""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
OUT=ROOT/'build/skin-tone/contact018-review-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    target=OUT/'review-v2'
    assert not target.exists(), 'preserve existing018 review'
    summary=json.loads((OUT/'summary.json').read_bytes())
    assert summary['status']=='PASS', 'both diagnostic full/repeat captures complete'
    sources={kind:OUT/kind/'full' for kind in ('original_scene','original_johnny')}
    sources['cartoon']=ROOT/'build/skin-tone/native-review/candidate-v2/front_arc/full'
    labels={'original_scene':'Original pose geometry','original_johnny':'Original pose on Cartoon island','cartoon':'Current Cartoon'}
    notes={'original_scene':'Original sprite and island. Diagnostic colors; judge contact and shape.',
           'original_johnny':'Original sprite, same Cartoon island. Diagnostic sprite colors.',
           'cartoon':'Current pose with the approved skin colors. Geometry is unchanged.'}
    rows=[]
    for kind,source in sources.items():
        raw=(source/'report.json').read_bytes()
        report=json.loads(raw)
        assert report['status']=='PASS' and report['clip']=='front_arc' and report['phase']=='full', 'complete scoped capture:'+kind
        first=report['displays'][0]
        assert first['actual_draw']==[0,478,216,18] and first['logical_ms']==0, 'same initial018 placement:'+kind
        png=(source/first['png']).read_bytes()
        assert sha(png)==first['png_sha256'], 'bound018 image:'+kind
        with Image.open(source/first['png']) as image:
            assert image.size==(1280,960) and sha(image.convert('RGB').tobytes())==first['pixels_sha256'], 'actual native pixels:'+kind
        rows.append({'kind':kind,'label':labels[kind],'note':notes[kind],'image':kind+'.png',
                     'png_sha256':sha(png),'report':str((source/'report.json').relative_to(ROOT)).replace('\\','/'),
                     'report_sha256':sha(raw),'archive_sha256':report['archive_sha256'],'source':source/first['png']})
    # Independently prove the middle panel isolates018 at this display.
    original=Image.open(rows[1]['source']).convert('RGB')
    current=Image.open(rows[2]['source']).convert('RGB')
    outside=0
    a,b=original.load(),current.load()
    for y in range(960):
        for x in range(1280):
            if not (956<=x<1020 and 432<=y<586) and a[x,y]!=b[x,y]:
                outside+=1
    original.close();current.close()
    assert outside==0, 'middle/current scene identical outside018 canvas'
    target.mkdir()
    for row in rows:
        shutil.copyfile(row.pop('source'),target/row['image'])
    bundle={'panels':rows,'pose':[940,425,95,175],'feet':[954,548,66,40],'frame':18,'draw':[0,478,216,18],'logical_ms':0}
    template=(HERE/'review-template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__')==1
    (target/'review.html').write_text(template.replace('__DATA__',json.dumps(bundle,separators=(',',':'))),encoding='utf-8',newline='\n')
    record={'status':'PASS; local diagnostic, not a new art approval','panels':rows,'bundle':bundle,
            'files_sha256':{p.name:sha(p.read_bytes()) for p in target.iterdir()},
            'summary_sha256':sha((OUT/'summary.json').read_bytes()),'outside018_changed_pixels':outside,
            'builder_sha256':sha(Path(__file__).read_bytes()),'template_sha256':sha((HERE/'review-template.html').read_bytes()),
            'limits':'Supplied original resource pixels rendered by port with its diagnostic palette. Not original-executable colors or DOSBox output. Geometry/placement untouched; camera crops identical and nearest-neighbor.'}
    (target/'review-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('PASS three bound native018 panels; identical camera and placement; zero changes outside018 in isolation panel')

if __name__=='__main__':main()
