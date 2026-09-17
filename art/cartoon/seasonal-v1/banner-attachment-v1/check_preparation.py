"""Execute narrow package-input controls against isolated scratch copies."""
import argparse
import importlib.util
import json
from pathlib import Path
import zipfile
from PIL import Image
import prepare

def check(baseline,runtime,candidate,work):
    assert not work.exists(),'fresh control output'
    work.mkdir(parents=True);results=[]
    spec=importlib.util.spec_from_file_location('banner_capture',Path(__file__).parent/'native/capture.py')
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    def refused(name,call,label):
        try:call()
        except (ValueError,AssertionError) as error:
            assert str(error)==label,str(error)
            results.append({'name':name,'status':'FIRED','failure':str(error)})
        else:raise AssertionError('SURVIVED '+name)
    original=runtime.read_bytes();damaged=work/'003.png';damaged.write_bytes(original+b'damaged')
    refused('stale_runtime_hash',lambda:prepare.prepare(baseline,damaged,prepare.sha(original),work/'bad-hash'),'banner preparation: runtime 003.png identity')
    Image.new('RGBA',(305,94),(255,0,0,255)).save(damaged)
    refused('wrong_runtime_canvas',lambda:prepare.prepare(baseline,damaged,prepare.sha(damaged.read_bytes()),work/'bad-canvas'),'banner preparation: 003.png original runtime canvas304x94')
    existing=work/'existing';existing.mkdir();sentinel=existing/'sentinel';sentinel.write_bytes(b'keep exactly')
    refused('existing_output',lambda:prepare.prepare(baseline,runtime,prepare.sha(original),existing),'banner preparation: existing output')
    assert sentinel.read_bytes()==b'keep exactly' and list(existing.iterdir())==[sentinel]
    alternate=work/'wrong-wave.zip'
    with zipfile.ZipFile(candidate) as source,zipfile.ZipFile(alternate,'w') as dest:
        for info in source.infolist():
            raw=source.read(info.filename)
            if info.filename=='data/styles/cartoon/BMP/BACKGRND.BMP/006.png':raw+=b'damaged'
            dest.writestr(info,raw)
    refused('changed_wave_payload',lambda:native.pair(baseline,alternate,prepare.sha(alternate.read_bytes())),'banner native: only HOLIDAY003 payload changed')
    native.pair(baseline,candidate,prepare.sha(candidate.read_bytes()))
    assert runtime.read_bytes()==original
    record={'status':'PASS','results':results,'restored_original_package_positive':'PASS',
            'helper_sha256':{p.name:prepare.sha(p.read_bytes()) for p in (Path(prepare.__file__),Path(native.__file__),Path(__file__))}}
    (work/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('PASS four package controls')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();check(a.baseline.resolve(),a.runtime.resolve(),a.candidate.resolve(),a.work.resolve())
