"""Focused damaged-input checks; never alter native capture originals."""
import argparse
import json
from pathlib import Path
import shutil
from PIL import Image
import build_review as builder

def run(captures,work):
    assert not work.exists(),'fresh control directory'
    fixture=work/'captures';fixture.mkdir(parents=True)
    for name in ('inputs.json','build.json','summary.json'):shutil.copyfile(captures/name,fixture/name)
    for key in builder.CASES:
        for side in ('baseline','candidate'):
            for phase in ('smoke','repeat'):
                src=captures/key/side/phase/'report.json';dst=fixture/key/side/phase/'report.json'
                dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
            if key=='day_banner':
                for row in json.loads((captures/key/side/'smoke/report.json').read_bytes())['displays']:
                    shutil.copyfile(captures/key/side/'smoke'/row['file'],fixture/key/side/'smoke'/row['file'])
    results=[]
    def refused(name,call,expected):
        try:call()
        except (ValueError,AssertionError) as error:
            assert expected in str(error),str(error)
            results.append({'name':name,'status':'FIRED','failure':str(error)})
        else:raise AssertionError('SURVIVED '+name)
    path=fixture/'day_banner/baseline/smoke/report.json';raw=path.read_bytes();record=json.loads(raw);record['args'][0]=1
    path.write_text(json.dumps(record))
    refused('wrong_case',lambda:builder.build(fixture,work/'wrong-case'),'day_banner/baseline report case');path.write_bytes(raw)
    image=path.parent/json.loads(raw)['displays'][0]['file'];original=image.read_bytes()
    with Image.open(image) as im:
        changed=im.convert('RGB');r,g,b=changed.getpixel((0,0));changed.putpixel((0,0),(r^1,g,b));changed.save(image)
    refused('changed_native_png',lambda:builder.build(fixture,work/'wrong-png'),'day_banner/baseline/'+image.name+' PNG identity');image.write_bytes(original)
    summary=fixture/'summary.json';summary_raw=summary.read_bytes();data=json.loads(summary_raw);data['cases']['day_banner']['loop_ms']=1441
    summary.write_text(json.dumps(data))
    refused('wrong_loop_interval',lambda:builder.build(fixture,work/'wrong-loop'),'banner review: observed 1440 ms loop');summary.write_bytes(summary_raw)
    existing=work/'existing';existing.mkdir();sentinel=existing/'keep.txt';sentinel.write_bytes(b'keep existing output exactly')
    before=builder.sha(sentinel)
    refused('existing_output',lambda:builder.build(captures,existing),'banner review: fresh output required')
    assert builder.sha(sentinel)==before and list(existing.iterdir())==[sentinel]
    assert path.read_bytes()==raw and image.read_bytes()==original and summary.read_bytes()==summary_raw
    result={'status':'PASS','builder_sha256':builder.sha(Path(builder.__file__)),'checker_sha256':builder.sha(Path(__file__)),
            'results':results,'restored_fixture_bytes':'PASS','positive':'Actual unmodified native inputs built successfully; matching smoke and regression are separate records.'}
    (work/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS four banner builder controls')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();run(a.captures.resolve(),a.work.resolve())
