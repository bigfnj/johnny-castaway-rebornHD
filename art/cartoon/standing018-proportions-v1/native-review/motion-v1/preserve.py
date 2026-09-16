"""One-time small018 motion evidence writer; historical captures remain untouched."""
import hashlib
import json
from pathlib import Path
import shutil
import capture_motion as c

def main():
    dest=c.HERE/'evidence-v1';assert not dest.exists(),'preserve immutable018 motion evidence'
    summary=json.loads((c.OUT/'summary.json').read_bytes());prep=json.loads((c.OUT/'preparation.json').read_bytes())
    controls=json.loads((c.OUT/'negative-controls.json').read_bytes())
    assert summary['status']==controls['status']=='PASS' and controls['summary_sha256']==c.sha((c.OUT/'summary.json').read_bytes()),'bound complete018 motion proof'
    assert summary['archive_sha256']==controls['archive_sha256']==c.PACKAGE_SHA and summary['runtime018_sha256']==c.RUNTIME_SHA,'selected runtime/package'
    for n,h in prep['protected_sha256'].items():assert c.sha((c.ROOT/n).read_bytes())==h,'protected source/production unchanged:'+n
    selected={name:c.OUT/name for name in ('summary.json','preparation.json','launch.json','launch.log','negative-controls.json')}
    for clip in c.NEW_CLIPS:
        for phase in ('smoke','full','repeat'):
            for name in ('report.json','capture.log'):selected[f'{clip}/{phase}/{name}']=c.OUT/clip/phase/name
    for phase,pins in prep['reused_front_arc_sha256'].items():
        for name,h in pins.items():
            source=c.PRIOR/'front_arc'/phase/name;assert c.sha(source.read_bytes())==h,'unchanged reused Front turn:'+phase+':'+name
            selected[f'reused-front-arc/{phase}/{name}']=source
    selected['reused-front-arc/summary.json']=c.PRIOR/'summary.json'
    selected['reused-front-arc/preparation.json']=c.PRIOR/'preparation.json'
    for source in c.HERE.iterdir():
        if source.is_file():selected['helpers/'+source.name]=source
    dest.mkdir();files={};sources={}
    for name,source in selected.items():
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        assert target.read_bytes()==source.read_bytes(),'exact native evidence copy:'+name
        files[name]=c.sha(target.read_bytes());sources[name]=source.relative_to(c.ROOT).as_posix()
    links={
        'prior_still_evidence':'art/cartoon/standing018-proportions-v1/native-review/evidence-still-v2/evidence.json',
        'color_evidence':'art/cartoon/standing018-proportions-v1/color/evidence-v2/evidence.json',
        'accepted_color_native_evidence':'art/cartoon/skin-tone-v1/native-review/evidence-v1/evidence.json'}
    bindings={key:{'path':path,'sha256':c.sha((c.ROOT/path).read_bytes())} for key,path in links.items()}
    result={'status':'PASS technical motion; human motion approval pending','files_sha256':files,'exact_copy_sources':sources,'linked_evidence':bindings,
        'archive_sha256':c.PACKAGE_SHA,'runtime018_sha256':c.RUNTIME_SHA,'executable_sha256':c.EXE_SHA,'baseline_archive_sha256':c.BASE_SHA,
        'clips':summary['clips'],'front_arc_reuse':'Exact previously completed smoke/full/repeat reports/logs and selected package/runtime rechecked; original files remain unchanged.',
        'new_sequence':'For each new clip: smoke, full, fresh repeat. Actual API/path/flip/origin/timing transcript equals accepted-color baseline; full pixel parity outside018 and for every non018 display.',
        'negative_controls':'Two altered actual full-capture buffers: mirrored018 pixel just outside its canvas, and retained023 pixel. Each named guard fires and restored positive passes. No capture files modified.',
        'visual_observation':'In mirrored rear arrival display063 at[1,394,209,18], the shorter screen-left foot appears just above the sand. This is a visual review item, not a failed timing/pixel-isolation check. Human motion judgment remains pending.',
        'excluded_bulk':'Private ZIP, executable and full PPM/PNG series remain scratch; selected and per-display identities are retained in preparation/build links/reports. Browser evidence is owned separately.',
        'reconstruction':'Restore pinned prior candidate and baseline captures/observer, run capture_motion.py into fresh scratch, then check_motion.py in the same Docker image/mounts. Skip this one-time historical evidence writer on replay.'}
    c.save(dest/'evidence.json',result)
    assert all(c.sha((dest/n).read_bytes())==h for n,h in files.items()),'native evidence final readback'
    c.save(dest/'readback.json',{'status':'PASS','evidence_sha256':c.sha((dest/'evidence.json').read_bytes()),'files_checked':len(files),'links_checked':len(bindings),'protected_inputs_checked':len(prep['protected_sha256'])})
    print('PASS frozen018 motion evidence: '+str(len(files))+' exact files; three linked checkpoints; protected inputs unchanged')

if __name__=='__main__':main()
