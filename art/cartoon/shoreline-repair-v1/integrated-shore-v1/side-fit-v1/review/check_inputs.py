"""Bounded damaged-input controls for the combined native wave adapter."""
import argparse
import copy
import json
from pathlib import Path
import shutil
from PIL import Image
import build_review as b

def run(captures, work):
    assert not work.exists(), 'fresh control directory'
    fixture = work / 'captures'
    fixture.mkdir(parents=True)
    for name in ('inputs.json','summary.json','build.json'):
        shutil.copyfile(captures / name, fixture / name)
    for key in b.CASES:
        for side in ('baseline','candidate'):
            for phase in ('smoke','repeat'):
                source = captures / key / side / phase / 'report.json'
                dest = fixture / key / side / phase / 'report.json'
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,dest)
            if key == 'high_clover':
                for row in json.loads((captures/key/side/'smoke/report.json').read_bytes())['displays']:
                    shutil.copyfile(captures/key/side/'smoke'/row['file'],fixture/key/side/'smoke'/row['file'])
    results = []
    def refused(name, expected):
        try:
            b.build(fixture, work/name)
        except (ValueError,AssertionError) as exc:
            assert expected in str(exc), str(exc)
            results.append({'name':name,'status':'FIRED','failure':str(exc)})
        else:
            raise AssertionError('SURVIVED '+name)
    inputs = fixture/'inputs.json'
    summary = fixture/'summary.json'
    orig_inputs, orig_summary = inputs.read_bytes(), summary.read_bytes()
    changed, changed_sum = json.loads(orig_inputs), json.loads(orig_summary)
    changed['pair']['candidate_sha256'] = '0'*64
    changed_sum['package_pair'] = changed['pair']
    b.save(inputs,changed)
    b.save(summary,changed_sum)
    refused('wrong-selected-archive','selected comparison archives')
    inputs.write_bytes(orig_inputs)
    summary.write_bytes(orig_summary)
    path = fixture/'high_clover/candidate/smoke/report.json'
    raw = path.read_bytes()
    record = json.loads(raw)
    record['displays'][0]['phases'][1] = 6
    b.save(path,record)
    refused('wrong-opening007','initial007 phase')
    path.write_bytes(raw)
    record = json.loads(raw)
    for row in record['displays']:
        if row['time_ms'] == 1440:
            row['phases'][1] = 6
    b.save(path,record)
    refused('wrong-loop-closure','observed1440 phase closure')
    path.write_bytes(raw)
    record = json.loads(raw)
    record['args'][0] = 1
    b.save(path,record)
    refused('wrong-clip-case','high_clover/candidate report case')
    path.write_bytes(raw)
    image = path.parent/json.loads(raw)['displays'][0]['file']
    original = image.read_bytes()
    with Image.open(image) as im:
        bad=im.convert('RGB')
        r,g,blue=bad.getpixel((0,0))
        bad.putpixel((0,0),(r^1,g,blue))
        bad.save(image)
    refused('wrong-native-png','PNG identity')
    image.write_bytes(original)
    existing=work/'existing'
    existing.mkdir()
    sentinel=existing/'keep.txt'
    sentinel.write_bytes(b'unchanged existing review')
    try:
        b.build(captures,existing)
    except AssertionError as exc:
        assert str(exc)=='fresh review output required'
        assert sentinel.read_bytes()==b'unchanged existing review' and list(existing.iterdir())==[sentinel]
        results.append({'name':'existing-output','status':'FIRED','failure':str(exc)})
    else:
        raise AssertionError('SURVIVED existing output')
    assert path.read_bytes()==raw and image.read_bytes()==original
    b.validate_inputs(captures)
    result={'status':'PASS','builder_sha256':b.sha(Path(b.__file__)),'checker_sha256':b.sha(Path(__file__)),
            'results':results,'restored_fixture_bytes':'PASS','restored_real_input_validation':'PASS',
            'positive':'The real native inputs build separately and pass browser smoke before regression.'}
    b.save(work/'result.json',result)
    print('PASS',len(results),'named wave input controls',b.sha(work/'result.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--captures',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    run(a.captures.resolve(),a.work.resolve())
