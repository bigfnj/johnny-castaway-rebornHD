"""Build a banner-only review using the frozen lossless native-atlas packer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
PACKER=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/offshore-scene-review-v1/build_review.py'
PACKER_SHA='b68c38f0e5cb0a25fecebcd2db966865707721db33be57f8a42ff3f705f71d21'
CASES={'day_banner':('Daylight',[4,0,0,0,0,0,20]),'night_banner':('Night',[4,1,0,0,0,0,20]),'shifted_banner':('Shifted island',[4,0,-80,20,0,0,20])}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def build(captures,output):
    assert sha(PACKER)==PACKER_SHA,'banner review: frozen atlas packer'
    assert not output.exists(),'banner review: fresh output required'
    summary=json.loads((captures/'summary.json').read_bytes())
    for key in CASES:
        assert summary['cases'][key]['loop_ms']==1440,'banner review: observed 1440 ms loop'
    spec=importlib.util.spec_from_file_location('frozen_scene_atlas',PACKER)
    packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    packer.CASES=CASES;packer.HERE=HERE
    packer.build(captures,output)
    manifest=json.loads((output/'manifest.json').read_bytes())
    manifest['default_case']='day_banner';manifest['labels']=['Current banner','Attached banner']
    manifest['scope']='Only the New Year banner differs. Exact native pixels and timing; both sides retain the selected offshore island and waves. Attachment and wave placement remain human review questions.'
    for key,clip in manifest['cases'].items():
        clip['recorded_duration_ms']=clip['duration_ms'];clip['recorded_display_count']=len(clip['frames'])
        clip['full_scene_pixels_close']=summary['cases'][key]['full_scene_pixels_close']
        clip['frames']=[r for r in clip['frames'] if r['time_ms']<=1440]
        clip['duration_ms']=1440
        dx,dy=clip['args'][2]*2,clip['args'][3]*2
        clip['views']={'banner':[690+dx,225+dy,375,220],'island':[510+dx,220+dy,700,610],
                       'waves':[660+dx,550+dy,430,185],'full':[0,0,1280,960]}
    save(output/'manifest.json',manifest)
    record=json.loads((output/'build.json').read_bytes())
    record.update(builder_sha256=sha(Path(__file__)),packer_sha256=PACKER_SHA,
                  manifest_sha256=sha(output/'manifest.json'),scope=manifest['scope'])
    save(output/'build.json',record)
    print('PASS banner review built',record['atlas_bytes'],'atlas bytes')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.captures.resolve(),a.output.resolve())
