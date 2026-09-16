"""One private018 replacement, front_arc smoke then full/fresh repeat; no approval."""
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

def transcript(text):
    return [s for s in text.splitlines() if re.search(r'TURN (?:SEGMENT|DRAW|ANIMATE|WAIT|DISPLAY):|TURN SEGMENT END:|\. chosen path:|WALKING:',s)]

def native():
    out=Path('/out');prep=json.loads((out/'preparation.json').read_bytes())
    exe=BASE/'baseline-v1/connecting_walk_probe'
    assert sha(exe.read_bytes())==prep['executable_sha256'],'unchanged observer executable'
    codec_path=ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
    spec=importlib.util.spec_from_file_location('codec',codec_path);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    reports={}
    for phase in ('smoke','full','repeat'):
        folder=out/'front_arc'/phase;assert not folder.exists(),'preserve018 native phase:'+phase;folder.mkdir(parents=True)
        shutil.copyfile(out/'scrantic_data.zip',folder/'scrantic_data.zip');(folder/'profile').mkdir()
        assert sha((folder/'scrantic_data.zip').read_bytes())==prep['archive_sha256'],'bound018 private execution archive'
        cmd=[str(exe),'cartoon','smoke' if phase=='smoke' else 'full','front_arc']
        with (folder/'capture.log').open('wb') as stream:
            result=subprocess.run(cmd,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=stream,stderr=subprocess.STDOUT,timeout=120)
        assert result.returncode==0,'native018 exit:'+phase
        prior=BASE/'candidate-v2/front_arc'/phase
        for name,digest in prep['baseline_capture_sha256'][phase].items():assert sha((prior/name).read_bytes())==digest,'bound baseline:'+phase+':'+name
        expected=json.loads((prior/'report.json').read_bytes());text=(folder/'capture.log').read_text()
        assert transcript(text)==transcript((prior/'capture.log').read_text()),'exact native018 API/path/draw/timing:'+phase
        assert 'TURN DRIVER: island_seed=11 path_seed=2 clip=front_arc style=cartoon' in text,'same configured clip/style'
        assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text),'finite native completion'
        loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)))
        assert loaded==expected['loaded_art'] and MEMBER in loaded,'same PNG load set including selected018'
        displays=[];changed=0
        for prior_display in expected['displays']:
            row={k:v for k,v in prior_display.items() if k not in ('comparison','changed_scene_pixels')}
            before=codec.ppm(prior/row['ppm']);after=codec.ppm(folder/row['ppm'])
            assert len(after)==1280*960*3 and sha(before)==row['pixels_sha256'],'bound baseline/native full display pixels'
            flip,x,y,frame=row['actual_draw']
            if frame==18:
                assert before!=after,'revised018 visibly present'
                x0,y0,x1,y1=x*2,y*2,x*2+64,y*2+154
                for py in range(960):
                    start=py*3840
                    if y0<=py<y1:
                        assert before[start:start+x0*3]==after[start:start+x0*3] and before[start+x1*3:start+3840]==after[start+x1*3:start+3840],'unchanged outside018 canvas'
                    else:assert before[start:start+3840]==after[start:start+3840],'unchanged outside018 canvas'
                changed+=1;row['comparison']='differences confined to018 canvas'
            else:
                assert before==after,'prior pose and scene pixel identity:'+str(frame)
                row['comparison']='entire display unchanged'
            png=codec.png_bytes(after);(folder/row['png']).write_bytes(png);row.update(pixels_sha256=sha(after),png_sha256=sha(png));displays.append(row)
        assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']),'final018 route image identity'
        report={k:expected[k] for k in ('clip','segments','completed_waits','display_count','duration_ms')}
        report.update(status='PASS',phase=phase,displays=displays,loaded_art=loaded,changed_displays=changed,unchanged_displays=len(displays)-changed,
            archive_sha256=prep['archive_sha256'],executable_sha256=prep['executable_sha256'],runtime018_sha256=prep['runtime018_sha256'],command=cmd,exit_code=0,
            log_sha256=sha((folder/'capture.log').read_bytes()),helper_sha256=sha(Path(__file__).read_bytes()),scope='Front turn technical regression for still proportion review; not human approval or full motion-family coverage.')
        save(folder/'report.json',report);reports[phase]=report
        print(f'PASS018 {phase}: {len(displays)} actual displays; {changed} scoped018 changes',flush=True)
    for key in ('displays','segments','completed_waits','loaded_art'):
        assert reports['full'][key]==reports['repeat'][key],'fresh native repeat:'+key
    for n,h in prep['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'protected source/production:'+n
    save(out/'summary.json',{'status':'PASS','ordered_phases':['smoke','full','repeat'],'full_displays':36,'duration_ms':3400,
        'changed018_displays':reports['full']['changed_displays'],'unchanged_other_displays':reports['full']['unchanged_displays'],
        'archive_sha256':prep['archive_sha256'],'runtime018_sha256':prep['runtime018_sha256'],'executable_sha256':prep['executable_sha256'],
        'helper_sha256':sha(Path(__file__).read_bytes()),'scope':'Human still proportion review pending; no final geometry/motion approval.'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');p.add_argument('--runtime',type=Path);p.add_argument('--runtime-sha256');p.add_argument('--color-record',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.capture:return native()
    assert a.runtime and a.runtime_sha256 and a.color_record and a.output,'explicit normalized018 and color record required'
    assert not a.output.exists(),'preserve018 review output'
    raw=a.runtime.read_bytes();assert sha(raw)==a.runtime_sha256,'final normalized018 handoff hash'
    from PIL import Image
    with Image.open(a.runtime) as im:assert im.mode=='RGBA' and im.size==(64,154),'018 RGBA64x154'
    color_raw=a.color_record.read_bytes();color=json.loads(color_raw)
    assert color['operation']=='post-export-color-correction' and [r['frame'] for r in color['frames']]==[18],'single018 color handoff'
    row=color['frames'][0]
    assert row['member']==MEMBER and row['runtime_canvas']==[64,154] and row['candidate_png_sha256']==a.runtime_sha256,'color record binds exact normalized018 PNG'
    assert (a.color_record.parent/row['candidate_png']).resolve()==a.runtime.resolve(),'color recipe output path identity'
    for item in color['inputs'].values():assert sha((ROOT/item['path']).read_bytes())==item['sha256'],'bound018 color input:'+item['path']
    base=BASE/'candidate-v2/scrantic_data.zip';assert sha(base.read_bytes())==BASE_SHA,'accepted-color baseline archive'
    binding=json.loads((BASE/'baseline-v1/build.json').read_bytes())
    for n,h in binding['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'protected source/production:'+n
    a.output.mkdir(parents=True)
    with zipfile.ZipFile(base) as old:
        names=old.namelist();assert len(names)==len(set(names))==2594 and MEMBER in names,'only existing018 member'
        with zipfile.ZipFile(a.output/'scrantic_data.zip','x') as new:
            new.comment=old.comment
            for info in old.infolist():new.writestr(copy.copy(info),raw if info.filename==MEMBER else old.read(info.filename))
        with zipfile.ZipFile(a.output/'scrantic_data.zip') as new:
            assert new.namelist()==names and all(new.read(n)==(raw if n==MEMBER else old.read(n)) for n in names),'2593 unchanged member payloads'
    shutil.copyfile(a.color_record,a.output/'color-record.json')
    prep={'status':'PASS','base_archive_sha256':BASE_SHA,'archive_sha256':sha((a.output/'scrantic_data.zip').read_bytes()),'runtime018_sha256':sha(raw),
        'runtime_source':a.runtime.resolve().relative_to(ROOT).as_posix(),'color_record_source':a.color_record.resolve().relative_to(ROOT).as_posix(),'color_record_sha256':sha(color_raw),
        'executable_sha256':binding['executable_sha256'],'protected_sha256':binding['protected_sha256'],'member_count':2594,'unchanged_other_members':2593,
        'baseline_capture_sha256':{phase:{n:sha((BASE/'candidate-v2/front_arc'/phase/n).read_bytes()) for n in ('report.json','capture.log')} for phase in ('smoke','full','repeat')},
        'helper_sha256':sha(Path(__file__).read_bytes()),'scope':'Private candidate for HUMAN STILL PROPORTION REVIEW; no final approval or production changes.'}
    save(a.output/'preparation.json',prep)
    cmd=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly','--mount',f'type=bind,source={a.output.resolve().as_posix()},target=/out',IMAGE,
        'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/source/'+Path(__file__).relative_to(ROOT).as_posix(),'--capture']
    save(a.output/'launch.json',{'command':cmd,'helper_sha256':sha(Path(__file__).read_bytes())})
    with (a.output/'launch.log').open('wb') as stream:result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
    assert result.returncode==0,'native018 review capture launch; retained launch.log'
    print((a.output/'launch.log').read_text(),end='')

if __name__=='__main__':main()
