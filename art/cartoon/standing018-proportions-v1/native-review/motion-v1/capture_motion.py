"""Two new018 arrival routes, reusing the unchanged observer and accepted Front turn."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=Path('/source') if Path('/source/CMakeLists.txt').exists() else next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
BASE=ROOT/'build/skin-tone/native-review'
PRIOR=ROOT/'build/standing018-proportions/native-review/color-v2'
OUT=Path('/out') if ROOT==Path('/source') else ROOT/'build/standing018-proportions/motion-v1'
PACKAGE_SHA='7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52'
RUNTIME_SHA='21cf94cd90d369b20b6d3b8ef60b7cc2848f919ff828578320502aec9a17c55b'
EXE_SHA='203aebb8c15881a41108b2b4fb97f5f9c6d025aa595a678b4dd84906011f7563'
BASE_SHA='bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf'
MEMBER='data/styles/cartoon/BMP/JOHNWALK.BMP/018.png'
NEW_CLIPS=('waypoint_front','waypoint_rear')
IMAGE='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')

def transcript(text):
    return [s for s in text.splitlines() if re.search(r'TURN (?:SEGMENT|DRAW|ANIMATE|WAIT|DISPLAY):|TURN SEGMENT END:|\. chosen path:|WALKING:',s)]

def compare_scene(before,after,draw):
    flip,x,y,frame=draw
    if frame!=18:
        assert before==after,'prior pose and scene pixel identity:'+str(frame)
        return False
    assert flip in (0,1) and len(before)==len(after)==1280*960*3,'valid native018 mirrored canvas'
    x0,y0,x1,y1=x*2,y*2,x*2+64,y*2+154
    assert 0<=x0<x1<=1280 and 0<=y0<y1<=960,'placed018 canvas bounds'
    assert before!=after,'revised018 visibly present'
    # The full64x154 canvas is mirrored by the unchanged renderer at this same origin.
    for py in range(960):
        start=py*3840
        if y0<=py<y1:
            assert before[start:start+x0*3]==after[start:start+x0*3] and before[start+x1*3:start+3840]==after[start+x1*3:start+3840],'unchanged outside018 canvas'
        else:assert before[start:start+3840]==after[start:start+3840],'unchanged outside018 canvas'
    return True

def load_codec():
    path=ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
    spec=importlib.util.spec_from_file_location('codec',path);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    return codec

def capture_one(clip,phase,prep,codec):
    folder=OUT/clip/phase;assert not folder.exists(),'preserve018 motion phase:'+clip+':'+phase;folder.mkdir(parents=True)
    shutil.copyfile(OUT/'scrantic_data.zip',folder/'scrantic_data.zip');(folder/'profile').mkdir()
    assert sha((folder/'scrantic_data.zip').read_bytes())==PACKAGE_SHA,'exact still-approved018 package'
    exe=BASE/'baseline-v1/connecting_walk_probe';assert sha(exe.read_bytes())==EXE_SHA,'unchanged observer'
    command=[str(exe),'cartoon','smoke' if phase=='smoke' else 'full',clip]
    with (folder/'capture.log').open('wb') as stream:
        result=subprocess.run(command,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==0,'native018 motion exit:'+clip+':'+phase
    prior=BASE/'candidate-v2'/clip/phase
    for n,h in prep['baseline_capture_sha256'][clip][phase].items():assert sha((prior/n).read_bytes())==h,'bound accepted-color capture:'+clip+':'+n
    expected=json.loads((prior/'report.json').read_bytes());text=(folder/'capture.log').read_text()
    assert expected['clip']==clip and expected['phase']==phase and expected['archive_sha256']==BASE_SHA and expected['executable_sha256']==EXE_SHA,'baseline clip/phase/package identity'
    assert transcript(text)==transcript((prior/'capture.log').read_text()),'exact native018 API/path/draw/timing:'+clip+':'+phase
    assert f'TURN DRIVER: island_seed=11 path_seed=2 clip={clip} style=cartoon' in text,'configured native clip/style'
    assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text),'finite native completion'
    loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)));assert loaded==expected['loaded_art'] and MEMBER in loaded,'same selected018 PNG load paths'
    displays=[];changed=0
    for old in expected['displays']:
        row={k:v for k,v in old.items() if k not in ('comparison','changed_scene_pixels')}
        before=codec.ppm(prior/row['ppm']);after=codec.ppm(folder/row['ppm'])
        assert len(after)==1280*960*3 and sha(before)==row['pixels_sha256'],'bound full native baseline pixels'
        different=compare_scene(before,after,row['actual_draw']);changed+=int(different)
        png=codec.png_bytes(after);(folder/row['png']).write_bytes(png)
        row.update(pixels_sha256=sha(after),png_sha256=sha(png),comparison='differences confined to018 canvas' if different else 'entire display unchanged')
        displays.append(row)
    assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']),'native final arrival image identity'
    report={k:expected[k] for k in ('clip','segments','completed_waits','display_count','duration_ms')}
    report.update(status='PASS',phase=phase,displays=displays,loaded_art=loaded,changed_displays=changed,unchanged_displays=len(displays)-changed,
        archive_sha256=PACKAGE_SHA,executable_sha256=EXE_SHA,runtime018_sha256=RUNTIME_SHA,base_archive_sha256=BASE_SHA,command=command,exit_code=0,
        log_sha256=sha((folder/'capture.log').read_bytes()),helper_sha256=sha(Path(__file__).read_bytes()),scope='Still-approved018 proportions in native waypoint arrival; human motion approval pending.')
    save(folder/'report.json',report);print(f'PASS {clip} {phase}: {len(displays)} displays; {changed} scoped018 changes',flush=True)
    return report

def capture_all():
    prep=json.loads((OUT/'preparation.json').read_bytes());codec=load_codec();clips={}
    for clip in NEW_CLIPS:
        capture_one(clip,'smoke',prep,codec)
        full=capture_one(clip,'full',prep,codec);repeat=capture_one(clip,'repeat',prep,codec)
        for key in ('displays','segments','completed_waits','loaded_art'):assert full[key]==repeat[key],'fresh native exact repeat:'+clip+':'+key
        clips[clip]={k:full[k] for k in ('display_count','duration_ms','changed_displays','unchanged_displays')}
    # Earlier Front turn is imported by binding only. Its historical reports stay immutable.
    for phase,pins in prep['reused_front_arc_sha256'].items():
        for n,h in pins.items():assert sha((PRIOR/'front_arc'/phase/n).read_bytes())==h,'reused Front turn binding:'+phase+':'+n
    front=json.loads((PRIOR/'front_arc/full/report.json').read_bytes())
    assert front['archive_sha256']==PACKAGE_SHA and front['runtime018_sha256']==RUNTIME_SHA and front['executable_sha256']==EXE_SHA,'reused Front turn selected package/runtime'
    ordered={'front_arc':{k:front[k] for k in ('display_count','duration_ms','changed_displays','unchanged_displays')},**clips}
    for n,h in prep['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'protected source/production unchanged:'+n
    save(OUT/'summary.json',{'status':'PASS','clips':ordered,'new_clip_order':list(NEW_CLIPS),'new_clip_phases':['smoke','full','repeat'],
        'reused_front_arc_directory':'build/standing018-proportions/native-review/color-v2/front_arc','archive_sha256':PACKAGE_SHA,'runtime018_sha256':RUNTIME_SHA,
        'executable_sha256':EXE_SHA,'base_archive_sha256':BASE_SHA,'helper_sha256':sha(Path(__file__).read_bytes()),'scope':'Three native clips including reused exact Front turn; human motion review pending, no production change.'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--capture',action='store_true');args=parser.parse_args()
    if args.capture:return capture_all()
    assert not OUT.exists(),'preserve018 motion evidence'
    assert sha((PRIOR/'scrantic_data.zip').read_bytes())==PACKAGE_SHA,'unchanged still-approved package'
    with zipfile.ZipFile(PRIOR/'scrantic_data.zip') as z:assert sha(z.read(MEMBER))==RUNTIME_SHA,'unchanged selected018 member'
    assert sha((BASE/'baseline-v1/connecting_walk_probe').read_bytes())==EXE_SHA,'pinned observer'
    binding=json.loads((BASE/'baseline-v1/build.json').read_bytes())
    for n,h in binding['protected_sha256'].items():assert sha((ROOT/n).read_bytes())==h,'protected source/production:'+n
    OUT.mkdir(parents=True);shutil.copyfile(PRIOR/'scrantic_data.zip',OUT/'scrantic_data.zip')
    names=('report.json','capture.log')
    prep={'status':'PASS','archive_sha256':PACKAGE_SHA,'runtime018_sha256':RUNTIME_SHA,'base_archive_sha256':BASE_SHA,'executable_sha256':EXE_SHA,
        'candidate_source':'build/standing018-proportions/native-review/color-v2/scrantic_data.zip','prior_preparation_sha256':sha((PRIOR/'preparation.json').read_bytes()),
        'protected_sha256':binding['protected_sha256'],'baseline_capture_sha256':{clip:{phase:{n:sha((BASE/'candidate-v2'/clip/phase/n).read_bytes()) for n in names} for phase in ('smoke','full','repeat')} for clip in NEW_CLIPS},
        'reused_front_arc_sha256':{phase:{n:sha((PRIOR/'front_arc'/phase/n).read_bytes()) for n in names} for phase in ('smoke','full','repeat')},
        'helper_sha256':sha(Path(__file__).read_bytes()),'scope':'Package copied byte-for-byte; no art or production mutation. Front turn evidence reused, not rewritten.'}
    save(OUT/'preparation.json',prep)
    command=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly','--mount',f'type=bind,source={OUT.as_posix()},target=/out',IMAGE,
        'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/source/'+Path(__file__).relative_to(ROOT).as_posix(),'--capture']
    save(OUT/'launch.json',{'command':command,'helper_sha256':sha(Path(__file__).read_bytes())})
    with (OUT/'launch.log').open('wb') as stream:result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
    assert result.returncode==0,'native motion launch; inspect retained launch.log'
    print((OUT/'launch.log').read_text(),end='')

if __name__=='__main__':main()
