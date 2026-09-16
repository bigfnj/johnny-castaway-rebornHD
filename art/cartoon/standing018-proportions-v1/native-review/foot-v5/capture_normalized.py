"""Final normalizedv5 candidate against reviewedv2, three native motion clips."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('motion',HERE.parent/'motion-v1/capture_motion.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT
OUT=Path('/out') if ROOT==Path('/source') else ROOT/'build/standing018-proportions/foot-v5-motion'
RUNTIME_SHA='5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f'
RECIPE_SHA='044d421dc3d0a33451f7c4dff34b9a5e375a544ddee848dca83f755b2382af8f'
COLOR=ROOT/'build/standing018-proportions/color-foot-v5'
V2=ROOT/'build/standing018-proportions/native-review/color-v2'
BASELINES={clip:(V2/'front_arc' if clip=='front_arc' else ROOT/'build/standing018-proportions/motion-v1'/clip) for clip in ('front_arc','waypoint_front','waypoint_rear')}

def capture_one(clip,phase,prep,codec):
    folder=OUT/clip/phase;assert not folder.exists(),'preserve normalizedv5 phase:'+clip+':'+phase;folder.mkdir(parents=True)
    shutil.copyfile(OUT/'scrantic_data.zip',folder/'scrantic_data.zip');(folder/'profile').mkdir()
    assert m.sha((folder/'scrantic_data.zip').read_bytes())==prep['archive_sha256'],'normalizedv5 execution archive'
    exe=m.BASE/'baseline-v1/connecting_walk_probe';assert m.sha(exe.read_bytes())==m.EXE_SHA,'unchanged observer'
    command=[str(exe),'cartoon','smoke' if phase=='smoke' else 'full',clip]
    with (folder/'capture.log').open('wb') as stream:
        result=subprocess.run(command,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==0,'normalizedv5 native exit:'+clip+':'+phase
    prior=BASELINES[clip]/phase
    for name,h in prep['baseline_report_bindings'][clip][phase].items():assert m.sha((prior/name).read_bytes())==h,'bound reviewedv2 record:'+clip+':'+phase+':'+name
    expected=json.loads((prior/'report.json').read_bytes());text=(folder/'capture.log').read_text()
    assert expected['clip']==clip and expected['phase']==phase and expected['archive_sha256']==m.PACKAGE_SHA and expected['runtime018_sha256']==m.RUNTIME_SHA,'reviewedv2 clip/phase/package/runtime'
    assert m.transcript(text)==m.transcript((prior/'capture.log').read_text()),'unchanged native API/path/draw/flip/time:'+clip+':'+phase
    assert f'TURN DRIVER: island_seed=11 path_seed=2 clip={clip} style=cartoon' in text,'configured native clip/style'
    assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text),'finite native completion'
    loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)));assert loaded==expected['loaded_art'] and m.MEMBER in loaded,'same selected018 asset path'
    displays=[];changed=0
    for old in expected['displays']:
        before=codec.ppm(prior/old['ppm']);after=codec.ppm(folder/old['ppm'])
        assert m.sha(before)==old['pixels_sha256'] and len(after)==1280*960*3,'bound reviewedv2 native image'
        different=m.compare_scene(before,after,old['actual_draw']);changed+=int(different)
        png=codec.png_bytes(after);(folder/old['png']).write_bytes(png)
        row={k:v for k,v in old.items() if k not in ('comparison','changed_scene_pixels','allowed_change_box','baseline_pixels_sha256')}
        row.update(pixels_sha256=m.sha(after),png_sha256=m.sha(png),comparison='differences confined to018 canvas' if different else 'entire display unchanged');displays.append(row)
    assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']),'normalizedv5 final image identity'
    report={k:expected[k] for k in ('clip','segments','completed_waits','display_count','duration_ms')}
    report.update(status='PASS',phase=phase,displays=displays,loaded_art=loaded,changed_displays=changed,unchanged_displays=len(displays)-changed,
        archive_sha256=prep['archive_sha256'],base_archive_sha256=m.PACKAGE_SHA,runtime018_sha256=RUNTIME_SHA,executable_sha256=m.EXE_SHA,
        command=command,exit_code=0,log_sha256=m.sha((folder/'capture.log').read_bytes()),helper_sha256=m.sha(Path(__file__).read_bytes()),
        comparison_helper_sha256=m.sha(Path(m.__file__).read_bytes()),scope='Normalizedv5 foot candidate, reviewedv2 baseline; human foot/contact/motion approval pending.')
    m.save(folder/'report.json',report);print(f'PASS normalizedv5 {clip} {phase}: {len(displays)} displays, {changed} scoped018 changes',flush=True)
    return report

def native():
    prep=json.loads((OUT/'preparation.json').read_bytes());assert prep['comparison_helper_sha256']==m.sha(Path(m.__file__).read_bytes()),'frozen reused scene comparator'
    codec=m.load_codec();clips={}
    for clip in BASELINES:
        capture_one(clip,'smoke',prep,codec)
        full=capture_one(clip,'full',prep,codec);repeat=capture_one(clip,'repeat',prep,codec)
        for key in ('displays','segments','completed_waits','loaded_art'):assert full[key]==repeat[key],'fresh normalizedv5 repeat:'+clip+':'+key
        clips[clip]={k:full[k] for k in ('display_count','duration_ms','changed_displays','unchanged_displays')}
    for name,h in prep['protected_sha256'].items():assert m.sha((ROOT/name).read_bytes())==h,'protected production/source unchanged:'+name
    m.save(OUT/'summary.json',{'status':'PASS','clips':clips,'ordered_phases_per_clip':['smoke','full','repeat'],'archive_sha256':prep['archive_sha256'],
        'base_archive_sha256':m.PACKAGE_SHA,'runtime018_sha256':RUNTIME_SHA,'executable_sha256':m.EXE_SHA,'color_recipe_sha256':RECIPE_SHA,
        'helper_sha256':m.sha(Path(__file__).read_bytes()),'comparison_helper_sha256':m.sha(Path(m.__file__).read_bytes()),
        'scope':'Three complete normalizedv5 clips against reviewedv2; all other art/pixels/timing retained. New human foot/contact/motion review pending.'})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--capture',action='store_true');args=parser.parse_args()
    if args.capture:return native()
    assert not OUT.exists(),'preserve normalizedv5 motion'
    recipe_path=COLOR/'recipe.json';assert m.sha(recipe_path.read_bytes())==RECIPE_SHA,'final color-v5 recipe'
    recipe=json.loads(recipe_path.read_bytes());assert recipe['operation']=='post-export-color-correction' and [r['frame'] for r in recipe['frames']]==[18],'single normalized018 handoff'
    row=recipe['frames'][0];runtime=COLOR/row['candidate_png'];raw=runtime.read_bytes()
    assert row['candidate_png_sha256']==m.sha(raw)==RUNTIME_SHA and row['member']==m.MEMBER and row['runtime_canvas']==[64,154],'final selected normalized018'
    for item in recipe['inputs'].values():assert m.sha((ROOT/item['path']).read_bytes())==item['sha256'],'final color input:'+item['path']
    from PIL import Image
    with Image.open(runtime) as image:assert image.mode=='RGBA' and image.size==(64,154),'018 RGBA runtime canvas'
    base=V2/'scrantic_data.zip';assert m.sha(base.read_bytes())==m.PACKAGE_SHA,'reviewedv2 baseline package'
    binding=json.loads((m.BASE/'baseline-v1/build.json').read_bytes())
    for name,h in binding['protected_sha256'].items():assert m.sha((ROOT/name).read_bytes())==h,'protected production/source:'+name
    OUT.mkdir(parents=True)
    with zipfile.ZipFile(base) as old:
        names=old.namelist();assert len(names)==len(set(names))==2594,'unique reviewedv2 members'
        with zipfile.ZipFile(OUT/'scrantic_data.zip','x') as new:
            new.comment=old.comment
            for info in old.infolist():new.writestr(copy.copy(info),raw if info.filename==m.MEMBER else old.read(info.filename))
        with zipfile.ZipFile(OUT/'scrantic_data.zip') as new:assert new.namelist()==names and all(new.read(n)==(raw if n==m.MEMBER else old.read(n)) for n in names),'2593 unchanged payloads, one selected018 replacement'
    shutil.copyfile(recipe_path,OUT/'color-recipe.json')
    prep={'status':'PASS','archive_sha256':m.sha((OUT/'scrantic_data.zip').read_bytes()),'base_archive_sha256':m.PACKAGE_SHA,'runtime018_sha256':RUNTIME_SHA,
        'executable_sha256':m.EXE_SHA,'color_recipe_sha256':RECIPE_SHA,'runtime_source':runtime.relative_to(ROOT).as_posix(),'unchanged_other_members':2593,'member_count':2594,
        'baseline_roots':{clip:path.relative_to(ROOT).as_posix() for clip,path in BASELINES.items()},
        'candidate_report_roots':{clip:(OUT/clip).relative_to(ROOT).as_posix() for clip in BASELINES},
        'baseline_report_bindings':{clip:{phase:{name:m.sha((path/phase/name).read_bytes()) for name in ('report.json','capture.log')} for phase in ('smoke','full','repeat')} for clip,path in BASELINES.items()},
        'protected_sha256':binding['protected_sha256'],'helper_sha256':m.sha(Path(__file__).read_bytes()),'comparison_helper_sha256':m.sha(Path(m.__file__).read_bytes()),
        'scope':'Private normalizedv5 contact candidate; reviewedv2 baseline; no human approval or production change.'}
    m.save(OUT/'preparation.json',prep)
    command=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly','--mount',f'type=bind,source={OUT.as_posix()},target=/out',m.IMAGE,
        'xvfb-run','-a','-s','-screen 0 1280x960x24','python3','-B','/source/'+Path(__file__).relative_to(ROOT).as_posix(),'--capture']
    m.save(OUT/'launch.json',{'command':command,'helper_sha256':m.sha(Path(__file__).read_bytes())})
    with (OUT/'launch.log').open('wb') as stream:r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=500)
    assert r.returncode==0,'normalizedv5 native launch; inspect retained launch.log'
    print((OUT/'launch.log').read_text(),end='')

if __name__=='__main__':main()
