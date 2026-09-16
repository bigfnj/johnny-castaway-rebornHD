"""Private one-frame018 geometry inspection. No promotion, palette approval or full motion claim."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=Path('/source') if Path('/source/CMakeLists.txt').exists() else next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
BASE=ROOT/'build/skin-tone/native-review'
BASE_SHA='bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf'
MEMBER='data/styles/cartoon/BMP/JOHNWALK.BMP/018.png'
IMAGE='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')

def capture():
    out=Path('/out');prep=json.loads((out/'preparation.json').read_bytes())
    folder=out/'front_arc-smoke';assert not folder.exists(),'preserve018 smoke';folder.mkdir()
    exe=BASE/'baseline-v1/connecting_walk_probe'
    assert sha(exe.read_bytes())==prep['executable_sha256'],'same native observer'
    shutil.copyfile(out/'scrantic_data.zip',folder/'scrantic_data.zip')
    assert sha((folder/'scrantic_data.zip').read_bytes())==prep['archive_sha256'],'private018 archive identity'
    (folder/'profile').mkdir()
    cmd=[str(exe),'cartoon','smoke','front_arc']
    with (folder/'capture.log').open('wb') as log:
        result=subprocess.run(cmd,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=log,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==0,'018 native smoke exit'
    text=(folder/'capture.log').read_text();prior=BASE/'candidate-v2/front_arc/smoke'
    reference=json.loads((prior/'report.json').read_bytes())
    assert sha((prior/'report.json').read_bytes())==prep['baseline_report_sha256'],'bound earlier018 report'
    assert sha((prior/'capture.log').read_bytes())==prep['baseline_log_sha256'],'bound earlier018 log'
    def transcript(t):return [s for s in t.splitlines() if re.search(r'TURN (?:SEGMENT|DRAW|ANIMATE|WAIT|DISPLAY):|TURN SEGMENT END:|\. chosen path:|WALKING:',s)]
    assert transcript(text)==transcript((prior/'capture.log').read_text()),'same actual018 native path/origin/timing'
    assert 'TURN DRIVER: island_seed=11 path_seed=2 clip=front_arc style=cartoon' in text and 'stopping after 1 frame(s)' in text,'configured finite smoke'
    assert sorted(set(re.findall(r'Art asset: (\S+)',text)))==reference['loaded_art'],'same PNG load paths including018'
    codec_path=ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
    spec=importlib.util.spec_from_file_location('codec',codec_path);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    before=codec.ppm(prior/'display-001.ppm');after=codec.ppm(folder/'display-001.ppm')
    assert len(after)==1280*960*3 and sha(before)==reference['displays'][0]['pixels_sha256'],'bound full native pixels'
    changed=0
    for y in range(960):
        for x in range(1280):
            i=(y*1280+x)*3
            if before[i:i+3]!=after[i:i+3]:
                assert 956<=x<1020 and 432<=y<586,'pixel outside018 canvas changed'
                changed+=1
    assert changed>0 and after==codec.ppm(folder/'final.ppm'),'visible018 revision and final capture identity'
    encoded=codec.png_bytes(after);(folder/'display-001.png').write_bytes(encoded)
    report={'status':'PASS','scope':'ONE smoke display; geometry inspection only, palette and motion approval pending','clip':'front_arc','phase':'smoke',
        'actual_draw':[0,478,216,18],'logical_ms':0,'changed_pixels_inside018':changed,'changed_pixels_outside018':0,
        'png_sha256':sha(encoded),'pixels_sha256':sha(after),'archive_sha256':prep['archive_sha256'],'runtime018_sha256':prep['runtime018_sha256'],
        'executable_sha256':prep['executable_sha256'],'helper_sha256':sha(Path(__file__).read_bytes()),'command':cmd,'exit_code':0,'log_sha256':sha((folder/'capture.log').read_bytes())}
    save(folder/'report.json',report);print('PASS018 smoke: one actual display at478,216, all differences inside64x154 canvas',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');p.add_argument('--runtime',type=Path);p.add_argument('--export-report',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.capture:return capture()
    assert a.runtime and a.export_report and a.output,'explicit reviewed export and fresh output required'
    assert not a.output.exists(),'preserve native inspection output'
    runtime=a.runtime.read_bytes();export=json.loads(a.export_report.read_bytes())
    assert export['runtime_sprites_written'] and export['runtime_fit_all_source_centers'] and not export['preview_only'],'completed fixed-canvas018 export'
    assert [r['frame'] for r in export['frames']]==[18] and export['frames'][0]['runtime_canvas']==[64,154],'only018 native canvas'
    assert sha(runtime)==export['outputs_sha256']['BMP/JOHNWALK.BMP/018.png'],'exact exported018 bytes'
    from PIL import Image
    with Image.open(a.runtime) as im:assert im.mode=='RGBA' and im.size==(64,154),'RGBA64x154 runtime'
    base=BASE/'candidate-v2/scrantic_data.zip';assert sha(base.read_bytes())==BASE_SHA,'approved-color private baseline'
    binding=json.loads((BASE/'baseline-v1/build.json').read_bytes())
    for n,h in binding['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'protected source/production:'+n
    a.output.mkdir(parents=True)
    with zipfile.ZipFile(base) as old:
        names=old.namelist();assert len(names)==len(set(names))==2594 and MEMBER in names,'unique existing018 replacement'
        with zipfile.ZipFile(a.output/'scrantic_data.zip','x') as new:
            new.comment=old.comment
            for info in old.infolist():new.writestr(copy.copy(info),runtime if info.filename==MEMBER else old.read(info.filename))
        with zipfile.ZipFile(a.output/'scrantic_data.zip') as new:
            assert new.namelist()==names and all(new.read(n)==(runtime if n==MEMBER else old.read(n)) for n in names),'2593 retained exact payloads and one018 replacement'
    prior=BASE/'candidate-v2/front_arc/smoke'
    prep={'status':'PASS','scope':'PRIVATE018 geometry inspection only; no palette approval or production change','base_archive_sha256':BASE_SHA,
        'archive_sha256':sha((a.output/'scrantic_data.zip').read_bytes()),'runtime018_sha256':sha(runtime),'member_count':2594,'unchanged_other_members':2593,
        'export_report_sha256':sha(a.export_report.read_bytes()),'executable_sha256':binding['executable_sha256'],
        'baseline_report_sha256':sha((prior/'report.json').read_bytes()),'baseline_log_sha256':sha((prior/'capture.log').read_bytes()),'helper_sha256':sha(Path(__file__).read_bytes())}
    save(a.output/'preparation.json',prep)
    cmd=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly','--mount',f'type=bind,source={a.output.resolve().as_posix()},target=/out',IMAGE,
         'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/source/'+Path(__file__).relative_to(ROOT).as_posix(),'--capture']
    save(a.output/'launch.json',{'command':cmd,'helper_sha256':sha(Path(__file__).read_bytes())})
    with (a.output/'launch.log').open('wb') as stream:result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=150)
    assert result.returncode==0,'native smoke launch; inspect retained launch.log'
    print((a.output/'launch.log').read_text(),end='')

if __name__=='__main__':main()
