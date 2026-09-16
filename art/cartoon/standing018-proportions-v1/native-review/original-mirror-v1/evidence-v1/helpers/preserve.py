"""Preserve the exact requested original/revised mirrored arrival comparison."""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
import capture as c

def main():
    dest=c.HERE/'evidence-v1';assert not dest.exists(),'preserve original mirror evidence'
    summary=json.loads((c.OUT/'summary.json').read_bytes());assert summary['status']=='PASS','completed original mirrored capture'
    source=c.ROOT/'art/cartoon/arrival-pilot-v1/reference/018-native.png'
    revised=c.ROOT/'build/standing018-proportions/color-v2/sprites/018.png'
    with Image.open(source) as image:
        original=[(x,y) for y in range(67,image.height) for x in range(18,image.width) if image.getpixel((x,y))[3] and image.getpixel((x,y))!=(128,128,128,255)]
    with Image.open(revised) as image:
        new=[(x,y) for y in range(120,image.height) for x in range(34,image.width) if image.getpixel((x,y))[3]>=8]
    original_y=max(y for x,y in original)*2+1;revised_y=max(y for x,y in new)
    observations={'method':'Screen-space smaller-foot regions: original native x>=18,y>=67 excluding exact gray shadow128,128,128,255; revised runtime x>=34,y>=120 withalpha>=8. This is a region observation, not an anatomical left/right label.',
        'original_reference':source.relative_to(c.ROOT).as_posix(),'original_reference_sha256':c.sha(source.read_bytes()),
        'revised_runtime':revised.relative_to(c.ROOT).as_posix(),'revised_runtime_sha256':c.sha(revised.read_bytes()),
        'original_smaller_foot_last_runtime_row':original_y,'revised_smaller_foot_last_runtime_row':revised_y,
        'original_last_scene_row':418+original_y,'revised_last_scene_row':418+revised_y,'revised_ends_higher_hd_pixels':original_y-revised_y,
        'visual_observation':'At the exact mirrored arrival, the original smaller foot visually joins its contact shadow at the shore; the revised smaller screen-left foot remains visibly higher above the shore. The original sprite includes a gray contact shadow that the revised sprite does not, so the difference includes both foot geometry and ground-contact artwork.',
        'limit':'Port diagnostic palette is not the original executable color rendering. No numerical claim of exact sand-boundary gap is made. The actual scene is identical outside018 in every captured display.'}
    c.save(c.OUT/'observations.json',observations)
    selected={n:c.OUT/n for n in ('summary.json','observations.json','original-arrival-nearest4.png','revised-arrival-nearest4.png')}
    for phase in ('smoke','full'):
        for n in ('report.json','capture.log'):selected[phase+'/'+n]=c.OUT/phase/n
    selected['full/original-display-063.png']=c.OUT/'full/display-063.png'
    selected['full/revised-display-063.png']=c.REVISED/'full/display-063.png'
    selected['full/revised-report.json']=c.REVISED/'full/report.json'
    for p in c.HERE.iterdir():
        if p.is_file():selected['helpers/'+p.name]=p
    dest.mkdir();files={};sources={}
    for n,p in selected.items():
        target=dest/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);assert p.read_bytes()==target.read_bytes(),'exact mirrored evidence copy:'+n
        files[n]=c.sha(target.read_bytes());sources[n]=p.relative_to(c.ROOT).as_posix()
    linked=['art/cartoon/skin-tone-v1/contact018-review-v1/evidence-v1/evidence.json','art/cartoon/standing018-proportions-v1/native-review/motion-v1/evidence-v1/evidence.json','art/cartoon/arrival-pilot-v1/reference/source.json']
    record={'status':'PASS requested diagnostic; no art correction or new approval','files_sha256':files,'copy_sources':sources,
        'linked_evidence':{n:c.sha((c.ROOT/n).read_bytes()) for n in linked},'summary':summary,'observations':observations,
        'scope':'One new supplied-original018 route smoke then full, same observer and original_johnny archive. No repeat, browser publication, source/art/production edits.',
        'excluded_bulk':'ZIP/executable/PPMs remain scratch and are hash-bound in reports; displayed arrival PNGs and nearest4 crops retained. Original and revised capture data remain unchanged.'}
    c.save(dest/'evidence.json',record)
    assert all(c.sha((dest/n).read_bytes())==h for n,h in files.items()),'final mirrored evidence readback'
    c.save(dest/'readback.json',{'status':'PASS','evidence_sha256':c.sha((dest/'evidence.json').read_bytes()),'files_checked':len(files),'links_checked':len(linked)})
    print('PASS original mirrored comparison preserved; smaller revised foot ends '+str(original_y-revised_y)+'HD pixels higher; gray original shadow is a separate contact cue')

if __name__=='__main__':main()
