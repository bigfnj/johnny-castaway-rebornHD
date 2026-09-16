"""Quick rawv5 contact inspection against reviewedv2: front smoke, rear smoke/full."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
spec=importlib.util.spec_from_file_location('motion',HERE.parent/'motion-v1/capture_motion.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OUT=ROOT/'build/standing018-proportions/foot-v5-contact'
RUNTIME=ROOT/'build/standing018-proportions/stage-v5/runtime/BMP/JOHNWALK.BMP/018.png'
RUNTIME_SHA='183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2'
V2=ROOT/'build/standing018-proportions/native-review/color-v2'
BASELINES={'front_arc':V2/'front_arc','waypoint_rear':ROOT/'build/standing018-proportions/motion-v1/waypoint_rear'}

def main():
    assert not OUT.exists(),'preserve rawv5 contact'
    raw=RUNTIME.read_bytes();assert m.sha(raw)==RUNTIME_SHA,'selected rawv5 runtime'
    export_path=RUNTIME.parents[2]/'export-report.json';export=json.loads(export_path.read_bytes())
    assert export['runtime_sprites_written'] and export['runtime_fit_all_source_centers'] and export['outputs_sha256']['BMP/JOHNWALK.BMP/018.png']==RUNTIME_SHA,'completed fixed export'
    base=V2/'scrantic_data.zip';assert m.sha(base.read_bytes())==m.PACKAGE_SHA,'reviewedv2 package'
    exe=m.BASE/'baseline-v1/connecting_walk_probe';assert m.sha(exe.read_bytes())==m.EXE_SHA,'unchanged observer'
    OUT.mkdir(parents=True)
    with zipfile.ZipFile(base) as old:
        names=old.namelist();assert len(names)==len(set(names))==2594,'unique reviewedv2 members'
        with zipfile.ZipFile(OUT/'scrantic_data.zip','x') as new:
            new.comment=old.comment
            for info in old.infolist():new.writestr(copy.copy(info),raw if info.filename==m.MEMBER else old.read(info.filename))
        with zipfile.ZipFile(OUT/'scrantic_data.zip') as new:
            assert new.namelist()==names and all(new.read(n)==(raw if n==m.MEMBER else old.read(n)) for n in names),'only018 replacement,2593 exact other payloads'
    package_sha=m.sha((OUT/'scrantic_data.zip').read_bytes())
    m.save(OUT/'preparation.json',{'status':'PASS','scope':'Rawv5 geometry only, color normalization and human review pending','base_archive_sha256':m.PACKAGE_SHA,
        'archive_sha256':package_sha,'runtime018_sha256':RUNTIME_SHA,'export_report_sha256':m.sha(export_path.read_bytes()),'unchanged_other_members':2593,
        'executable_sha256':m.EXE_SHA,'helper_sha256':m.sha(Path(__file__).read_bytes()),'comparison_helper_sha256':m.sha(Path(m.__file__).read_bytes())})
    codec=m.load_codec();records={}
    for clip,phase in [('front_arc','smoke'),('waypoint_rear','smoke'),('waypoint_rear','full')]:
        folder=OUT/clip/phase;folder.mkdir(parents=True);(folder/'profile').mkdir();shutil.copyfile(OUT/'scrantic_data.zip',folder/'scrantic_data.zip')
        command=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly','--mount',f'type=bind,source={OUT.as_posix()},target=/out',
            '--workdir',f'/out/{clip}/{phase}','--env',f'HOME=/out/{clip}/{phase}/profile',m.IMAGE,'xvfb-run','-a','-s','-screen 0 1280x960x24',
            '/source/'+exe.relative_to(ROOT).as_posix(),'cartoon',phase,clip]
        with (folder/'capture.log').open('wb') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=150)
        assert r.returncode==0,'rawv5 native exit:'+clip+':'+phase
        prior=BASELINES[clip]/phase;expected=json.loads((prior/'report.json').read_bytes());text=(folder/'capture.log').read_text()
        assert m.transcript(text)==m.transcript((prior/'capture.log').read_text()),'unchanged actual native path/draw/timing'
        assert sorted(set(re.findall(r'Art asset: (\S+)',text)))==expected['loaded_art'],'unchanged selected PNG load set'
        assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text),'finite native completion'
        displays=[];changed=0
        for old in expected['displays']:
            before=codec.ppm(prior/old['ppm']);after=codec.ppm(folder/old['ppm']);assert m.sha(before)==old['pixels_sha256'],'bound reviewedv2 pixels'
            different=m.compare_scene(before,after,old['actual_draw']);changed+=int(different)
            png=codec.png_bytes(after);(folder/old['png']).write_bytes(png)
            row={k:old[k] for k in ('index','logical_ms','duration_ms','role','actual_draw','ppm','png')};row.update(pixels_sha256=m.sha(after),png_sha256=m.sha(png));displays.append(row)
        assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']),'final rawv5 capture identity'
        report={'status':'PASS','clip':clip,'phase':phase,'displays':displays,'display_count':len(displays),'duration_ms':expected['duration_ms'],
            'changed018_displays':changed,'unchanged_other_displays':len(displays)-changed,'changed_pixels_outside018':0,'archive_sha256':package_sha,'base_archive_sha256':m.PACKAGE_SHA,
            'runtime018_sha256':RUNTIME_SHA,'executable_sha256':m.EXE_SHA,'baseline_report_sha256':m.sha((prior/'report.json').read_bytes()),'command':command,'exit_code':0,
            'helper_sha256':m.sha(Path(__file__).read_bytes()),'comparison_helper_sha256':m.sha(Path(m.__file__).read_bytes()),'log_sha256':m.sha((folder/'capture.log').read_bytes()),
            'scope':'Rawv5 contact diagnostic only. No palette or geometry approval, no production changes.'}
        m.save(folder/'report.json',report);records[clip+'/'+phase]=m.sha((folder/'report.json').read_bytes())
        print(f'PASS rawv5 {clip} {phase}: {len(displays)} actual displays, all changes within018',flush=True)
    for name,path,box in [('front',OUT/'front_arc/smoke/display-001.png',(940,425,1035,600)),('mirrored',OUT/'waypoint_rear/full/display-063.png',(784,410,864,588))]:
        with Image.open(path) as im:im.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4),Image.Resampling.NEAREST).save(OUT/(name+'-nearest4.png'))
    m.save(OUT/'summary.json',{'status':'PASS','scope':'Rawv5 contact inspection only; no full3clip review or fresh repeat','reports_sha256':records,'archive_sha256':package_sha,
        'base_archive_sha256':m.PACKAGE_SHA,'runtime018_sha256':RUNTIME_SHA,'executable_sha256':m.EXE_SHA,'mirrored_arrival':[1,394,209,18],'mirrored_display':63,'mirrored_ms':4920})

if __name__=='__main__':main()
