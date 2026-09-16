"""Supplied-original018 at the exact mirrored rear arrival; smoke then one full route."""
import hashlib
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
OUT=ROOT/'build/standing018-proportions/original-mirror-v1'
ORIGINAL=ROOT/'build/skin-tone/contact018-review-v1/original_johnny.zip'
ORIGINAL_SHA='d7797181cf2e30699709946f0983b6899f0c7428785f9c596dea8ac150619f20'
REVISED=ROOT/'build/standing018-proportions/motion-v1/waypoint_rear'
EXE=ROOT/'build/skin-tone/native-review/baseline-v1/connecting_walk_probe'
EXE_SHA='203aebb8c15881a41108b2b4fb97f5f9c6d025aa595a678b4dd84906011f7563'
IMAGE='sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda p,o:p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')

def transcript(text):
    return [s for s in text.splitlines() if re.search(r'TURN (?:SEGMENT|DRAW|ANIMATE|WAIT|DISPLAY):|TURN SEGMENT END:|\. chosen path:|WALKING:',s)]

def main():
    assert not OUT.exists(),'preserve mirrored original diagnostic'
    assert sha(ORIGINAL.read_bytes())==ORIGINAL_SHA and sha(EXE.read_bytes())==EXE_SHA,'pinned original package/observer'
    original_prep=json.loads((ROOT/'build/skin-tone/contact018-review-v1/preparation.json').read_bytes())
    package=original_prep['packages']['original_johnny']
    with zipfile.ZipFile(ORIGINAL) as z:
        assert all(sha(z.read(n))==h for n,h in package['retained_members_sha256'].items()),'unchanged original diagnostic members'
        assert not any(n.endswith('/JOHNWALK.BMP/018.png') for n in z.namelist()),'018 uses original fallback only'
        for n,h in package['supplied_resource_replacements_sha256'].items():assert sha(z.read(n))==h,'supplied original resources'
    OUT.mkdir(parents=True);reports={}
    spec=importlib.util.spec_from_file_location('codec',ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py')
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    for phase in ('smoke','full'):
        folder=OUT/phase;folder.mkdir();(folder/'profile').mkdir();shutil.copyfile(ORIGINAL,folder/'scrantic_data.zip')
        command=['docker','run','--rm','--init','--network','none','--mount',f'type=bind,source={ROOT.as_posix()},target=/source,readonly',
            '--mount',f'type=bind,source={OUT.as_posix()},target=/out','--workdir','/out/'+phase,'--env','HOME=/out/'+phase+'/profile',IMAGE,
            'xvfb-run','-a','-s','-screen 0 1280x960x24','/source/'+EXE.relative_to(ROOT).as_posix(),'cartoon',phase,'waypoint_rear']
        with (folder/'capture.log').open('wb') as stream:r=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=150)
        assert r.returncode==0,'native original mirrored exit:'+phase
        reference=json.loads((REVISED/phase/'report.json').read_bytes());text=(folder/'capture.log').read_text()
        assert transcript(text)==transcript((REVISED/phase/'capture.log').read_text()),'exact mirrored original path/draw/time:'+phase
        assert 'TURN DRIVER: island_seed=11 path_seed=2 clip=waypoint_rear style=cartoon' in text,'configured route/style'
        assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text),'finite original capture completion'
        loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)))
        assert loaded==[n for n in reference['loaded_art'] if not n.endswith('/JOHNWALK.BMP/018.png')],'only018 switches to original decoder'
        fallback=re.search(r'Art assets decoded: cartoon=(\d+), HD fallback=(\d+), original fallback=(\d+)',text)
        assert fallback and int(fallback[3])>0,'actual original fallback decode witness'
        displays=[];outside=0;non018=0
        for old in reference['displays']:
            before=codec.ppm(folder/old['ppm']);after=codec.ppm(REVISED/phase/old['ppm'])
            assert len(before)==1280*960*3 and sha(after)==old['pixels_sha256'],'bound original and revised native display'
            flip,x,y,frame=old['actual_draw']
            if frame==18:
                x0,y0,x1,y1=x*2,y*2,x*2+64,y*2+154
                for py in range(960):
                    start=py*3840
                    if y0<=py<y1:
                        assert before[start:start+x0*3]==after[start:start+x0*3] and before[start+x1*3:start+3840]==after[start+x1*3:start+3840],'same island outside original/revised018'
                    else:assert before[start:start+3840]==after[start:start+3840],'same island outside original/revised018'
            else:
                assert before==after,'unchanged non018 original diagnostic display';non018+=1
            row={k:old[k] for k in ('index','logical_ms','duration_ms','role','actual_draw','ppm')}
            row.update(pixels_sha256=sha(before),revised_pixels_sha256=sha(after));displays.append(row)
            if frame==18 and flip==1:
                encoded=codec.png_bytes(before);path=folder/Path(old['ppm']).with_suffix('.png').name;path.write_bytes(encoded);row['png']=path.name;row['png_sha256']=sha(encoded)
        assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']),'final original display identity'
        result={'status':'PASS','clip':'waypoint_rear','phase':phase,'command':command,'exit_code':0,'archive_sha256':ORIGINAL_SHA,'executable_sha256':EXE_SHA,
            'displays':displays,'display_count':len(displays),'duration_ms':reference['duration_ms'],'unchanged_non018_displays':non018,'changed_pixels_outside018':outside,
            'loaded_art':loaded,'original_resource_sha256':package['supplied_resource_replacements_sha256'],'reference_report_sha256':sha((REVISED/phase/'report.json').read_bytes()),
            'helper_sha256':sha(Path(__file__).read_bytes()),'log_sha256':sha((folder/'capture.log').read_bytes()),'scope':'Supplied-original geometry rendered by port diagnostic palette; exact mirrored arrival against revised018. No original-executable color/timing claim.'}
        save(folder/'report.json',result);reports[phase]=result
        print('PASS original mirrored '+phase+': '+str(len(displays))+' exact native events, zero scene changes outside018',flush=True)
    row=next(d for d in reports['full']['displays'] if d['actual_draw']==[1,394,209,18])
    assert row['index']==63 and row['logical_ms']==4920,'requested mirrored arrival display'
    original_image=Image.open(OUT/'full'/row['png']).convert('RGB')
    revised_image=Image.open(REVISED/'full'/'display-063.png').convert('RGB')
    box=(784,410,864,588)
    original_image.crop(box).resize((320,712),Image.Resampling.NEAREST).save(OUT/'original-arrival-nearest4.png')
    revised_image.crop(box).resize((320,712),Image.Resampling.NEAREST).save(OUT/'revised-arrival-nearest4.png')
    original_image.close();revised_image.close()
    save(OUT/'summary.json',{'status':'PASS','sequence':['smoke','full'],'arrival_display':63,'arrival_ms':4920,'actual_draw':[1,394,209,18],
        'archive_sha256':ORIGINAL_SHA,'executable_sha256':EXE_SHA,'helper_sha256':sha(Path(__file__).read_bytes()),'original_resource_sha256':package['supplied_resource_replacements_sha256'],
        'reports_sha256':{phase:sha((OUT/phase/'report.json').read_bytes()) for phase in reports},'comparison_crop_xyxy':list(box),'enlargement':'nearest4, same scene crop',
        'scope':'One requested original mirrored-arrival comparison. No repeat, new browser, art changes or production writes.'})

if __name__=='__main__':main()
