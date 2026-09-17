"""Three focused damaged-input/refusal controls for the scene builder."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
import build_review as builder


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(captures, work):
    assert not work.exists(), 'fresh control directory'
    fixture=work/'captures'
    fixture.mkdir(parents=True)
    # Report copies are editable; PNGs remain exact file copies, never hard links.
    for name in ('inputs.json','build.json','summary.json'):
        shutil.copyfile(captures/name,fixture/name)
    for key in builder.CASES:
        for side in ('baseline','candidate'):
            for phase in ('smoke','repeat'):
                src=captures/key/side/phase/'report.json'
                dst=fixture/key/side/phase/'report.json'
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(src,dst)
            # Only the first case needs image files: failures must happen there.
            if key=='day/none':
                record=json.loads((captures/key/side/'smoke/report.json').read_bytes())
                for row in record['displays']:
                    shutil.copyfile(captures/key/side/'smoke'/row['file'],fixture/key/side/'smoke'/row['file'])
    results=[]
    def refused(name,call,expected):
        try:call()
        except ValueError as error:
            assert expected in str(error), str(error)
            results.append({'name':name,'status':'FIRED','failure':str(error)})
        else:raise AssertionError('SURVIVED '+name)
    path=fixture/'day/none/baseline/smoke/report.json'
    raw=path.read_bytes()
    record=json.loads(raw)
    record['args'][0]=1
    path.write_text(json.dumps(record))
    refused('wrong_case_report',lambda:builder.build(fixture,work/'wrong-case'),'day/none/baseline report case')
    path.write_bytes(raw)
    image=fixture/'day/none/baseline/smoke'/json.loads(raw)['displays'][0]['file']
    original=image.read_bytes()
    with Image.open(image) as im:
        changed=im.convert('RGB')
        pixel=changed.getpixel((0,0));changed.putpixel((0,0),(pixel[0]^1,pixel[1],pixel[2]));changed.save(image)
    refused('changed_native_png',lambda:builder.build(fixture,work/'wrong-png'),'day/none/baseline/'+image.name+' PNG identity')
    image.write_bytes(original)
    existing=work/'existing';existing.mkdir();sentinel=existing/'keep.txt';sentinel.write_bytes(b'keep exact existing output')
    before=sha(sentinel)
    refused('existing_output',lambda:builder.build(captures,existing),'output already exists')
    assert sha(sentinel)==before and list(existing.iterdir())==[sentinel]
    assert path.read_bytes()==raw and image.read_bytes()==original
    # The original final review is the positive control; all damaged files were copies.
    result={'status':'PASS','builder_sha256':sha(Path(builder.__file__)),'checker_sha256':sha(Path(__file__)),
            'results':results,'scope':'Three executed damaged-input/refusal controls. Source captures unchanged; final positive browser checks are recorded separately.'}
    (work/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS three builder controls',sha(work/'result.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--captures',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();run(a.captures.resolve(),a.work.resolve())
