from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

ROOT=Path('/source');OUT=Path('/out')
sys.path.insert(0,str(ROOT/'art/cartoon/seasonal-v1/native'))
# Avoid importing this scratch file recursively, since it shares a basename.
spec=importlib.util.spec_from_file_location('seasonal_capture',ROOT/'art/cartoon/seasonal-v1/native/capture.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.HERE=OUT
spec=importlib.util.spec_from_file_location('seasonal_codec',c.CODEC)
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
prep=json.loads((OUT/'preparation.json').read_bytes())
assert c.sha((OUT/'original-full.zip').read_bytes())==prep['original_full_sha256']
assert c.sha((ROOT/'assets/scrantic_data.zip').read_bytes())==prep['production_sha256']
build=OUT/'native'
assert not build.exists();build.mkdir()
exe=c.build(build)
cases=[('original',OUT/'original-full.zip','hd'),('hd',ROOT/'assets/scrantic_data.zip','hd'),('cartoon',ROOT/'assets/scrantic_data.zip','cartoon')]
reports=[]
for kind,archive,style in cases:
    for tide in [0,1]:
        for holiday in [0,2]:
            folder=build/kind/('low' if tide else 'high')/('clover' if holiday else 'none')
            folder.mkdir(parents=True)
            shutil.copyfile(archive,folder/'scrantic_data.zip');(folder/'profile').mkdir()
            cmd=[str(exe),str(holiday),'0','0','0',style,str(tide)]
            with (folder/'capture.log').open('wb') as log:
                run=subprocess.run(cmd,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=log,stderr=subprocess.STDOUT,timeout=40)
            assert run.returncode==0,folder
            text=(folder/'capture.log').read_text()
            assert f'holiday={holiday} night=0 offset=0,0 lowTide={tide} raft=0 render=1280x960' in text
            assert 'island backdrop: OCEAN02.SCR' in text and 'SEASONAL DONE: finite native wait returned; cleanup complete' in text
            assert 'Captured frame: final.ppm (1280x960)' in text
            pixels=codec.ppm(folder/'final.ppm');png=codec.png_bytes(pixels);(folder/'final.png').write_bytes(png)
            loaded=sorted(set(re.findall(r'Art asset: (\S+)',text)))
            if kind=='original':assert not loaded,'supplied original fallback only'
            elif kind=='hd':assert loaded and all(n.startswith('data/hd/') for n in loaded)
            else:assert 'data/styles/cartoon/BMP/BACKGRND.BMP/000.png' in loaded
            if holiday:assert 'SEASONAL DRAW: frame=1 x=333 y=286 dx=0 dy=0 scale=2 canvas=240x94' in text
            row={'kind':kind,'low_tide':tide,'holiday':holiday,'png':(folder/'final.png').relative_to(OUT).as_posix(),
                 'png_sha256':c.sha(png),'pixels_sha256':c.sha(pixels),'loaded_art':loaded,'log_sha256':c.sha((folder/'capture.log').read_bytes()),'command':cmd}
            c.save(folder/'report.json',row);reports.append(row)
            print('PASS '+kind+' '+('low' if tide else 'high')+' '+str(holiday),flush=True)
assert c.sha((ROOT/'assets/scrantic_data.zip').read_bytes())==prep['production_sha256']
c.save(OUT/'native-summary.json',{'status':'PASS','cases':reports,'executable_sha256':c.sha(exe.read_bytes()),
       'scope':'Twelve bounded diagnostic stills. Each variant starts with a no-holiday high-tide smoke; no extra native repeat. Native renderer and scene positions unchanged, explicit high/low tide states. Supplied-original geometry through port palette, not original executable.'})
