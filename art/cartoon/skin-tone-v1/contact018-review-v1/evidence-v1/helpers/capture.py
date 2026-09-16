"""Scoped front_arc diagnostic parser; frozen production parsers remain untouched."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT, OUT = Path('/source'), Path('/out')
sha = lambda b: hashlib.sha256(b).hexdigest()
save = lambda p,o: p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
codec_path = ROOT/'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec=importlib.util.spec_from_file_location('codec',codec_path)
codec=importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)

def transcript(text):
    # These are native API/path/draw/delay/wait/display events, not PNG-load notices.
    return [line for line in text.splitlines() if re.search(r'TURN (?:SEGMENT|DRAW|ANIMATE|WAIT|DISPLAY):|TURN SEGMENT END:|\. chosen path:|WALKING:',line)]

def validate(text, reference_text, style, kind, expected_loaded):
    assert f'TURN DRIVER: island_seed=11 path_seed=2 clip=front_arc style={style}' in text, 'diagnostic style/clip witness:'+kind
    assert 'TURN ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text, 'fixed diagnostic island state'
    assert 'Captured frame: final.ppm (1280x960)' in text, 'native diagnostic resolution'
    assert transcript(text) == transcript(reference_text), 'unchanged native path/draw/timing transcript:'+kind
    loaded = sorted(set(re.findall(r'Art asset: (\S+)',text)))
    assert loaded == expected_loaded, 'exact diagnostic PNG-load set:'+kind
    if kind == 'original_scene':
        assert not loaded, 'all-original fallback has no PNG loads'
    else:
        usage = re.search(r'Art assets decoded: cartoon=(\d+), HD fallback=(\d+), original fallback=(\d+)',text)
        assert usage and int(usage[3]) > 0, '018 original fallback decode witness'
        assert not any('/JOHNWALK.BMP/018.png' in p for p in loaded), '018 neither Cartoon nor HD override loaded'
    return loaded

def capture(kind,phase,prep):
    data=prep['packages'][kind]
    folder=OUT/kind/phase
    assert not folder.exists(), 'preserve diagnostic capture:'+str(folder)
    folder.mkdir(parents=True)
    shutil.copyfile(OUT/(kind+'.zip'),folder/'scrantic_data.zip')
    (folder/'profile').mkdir()
    exe=OUT/'connecting_walk_probe'
    assert sha(exe.read_bytes())==prep['executable_sha256'], 'pinned unchanged executable'
    assert sha((folder/'scrantic_data.zip').read_bytes())==data['archive_sha256'], 'pinned diagnostic archive'
    command=[str(exe),data['style'],'smoke' if phase=='smoke' else 'full','front_arc']
    with (folder/'capture.log').open('wb') as stream:
        result=subprocess.run(command,cwd=folder,env=dict(os.environ,HOME=str(folder/'profile')),stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    assert result.returncode==0, 'native diagnostic exit:'+kind+':'+phase
    refphase='smoke' if phase=='smoke' else 'full'
    reference=OUT/'current'/refphase
    for name,digest in prep['reference_capture_sha256'][refphase].items():
        assert sha((reference/name).read_bytes())==digest, 'bound current capture:'+name
    record=json.loads((reference/'report.json').read_bytes())
    text=(folder/'capture.log').read_text()
    assert ('stopping after 1 frame(s)' in text) if phase=='smoke' else ('finite clips returned; cleanup complete;' in text), 'native completion witness'
    expected=[] if kind=='original_scene' else [n for n in record['loaded_art'] if not n.endswith('/JOHNWALK.BMP/018.png')]
    loaded=validate(text,(reference/'capture.log').read_text(),data['style'],kind,expected)
    displays=[]
    for display in record['displays']:
        row={k:v for k,v in display.items() if k not in ('comparison','changed_scene_pixels')}
        pixels=codec.ppm(folder/row['ppm'])
        png=codec.png_bytes(pixels)
        (folder/row['png']).write_bytes(png)
        row.update(pixels_sha256=sha(pixels),png_sha256=sha(png))
        displays.append(row)
    assert codec.ppm(folder/'final.ppm')==codec.ppm(folder/displays[-1]['ppm']), 'diagnostic final display identity'
    (folder/'final.png').write_bytes(codec.png_bytes(codec.ppm(folder/'final.ppm')))
    report={k:record[k] for k in ('clip','segments','completed_waits','display_count','duration_ms')}
    report.update(status='PASS',phase=phase,kind=kind,style=data['style'],displays=displays,loaded_art=loaded,command=command,exit_code=0,
                  archive_sha256=data['archive_sha256'],executable_sha256=prep['executable_sha256'],log_sha256=sha((folder/'capture.log').read_bytes()),
                  capture_helper_sha256=sha(Path(__file__).read_bytes()),reference_report_sha256=prep['reference_capture_sha256'][refphase]['report.json'],
                  scope='Supplied original artwork decoded by unchanged port; exact same observed path, draw and timing. Not DOSBox or original-executable parity.')
    save(folder/'report.json',report)
    print(f'PASS {kind} {phase}: {len(displays)} displays; {report["duration_ms"]}ms; exact fallback/load witness',flush=True)
    return report

def main():
    prep=json.loads((OUT/'preparation.json').read_bytes())
    kinds=list(prep['packages'])
    for kind in kinds:
        capture(kind,'smoke',prep)
    print('PASS both diagnostic smoke checks before full/regression',flush=True)
    for kind in kinds:
        full=capture(kind,'full',prep)
        repeat=capture(kind,'repeat',prep)
        for key in ('segments','displays','completed_waits','loaded_art'):
            assert full[key]==repeat[key], 'fresh native exact repeat:'+kind+':'+key
    for path,digest in prep['protected_sha256'].items():
        assert sha((ROOT/path).read_bytes())==digest, 'protected production/source unchanged:'+path
    save(OUT/'summary.json',{'status':'PASS','packages':{k:v['archive_sha256'] for k,v in prep['packages'].items()},
        'executable_sha256':prep['executable_sha256'],'capture_helper_sha256':sha(Path(__file__).read_bytes()),
        'sequence':['both smoke','each full then fresh repeat'],'display_count_per_full':36,'duration_ms':3400,'protected_inputs_unchanged':True})
    print('PASS two original-art diagnostic routes and fresh repeats; protected inputs unchanged',flush=True)

if __name__=='__main__':
    main()
