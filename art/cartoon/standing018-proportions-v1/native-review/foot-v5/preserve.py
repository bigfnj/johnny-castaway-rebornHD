"""One-time finalv5 native evidence writer; earlier captures and approvals stay intact."""
import json
from pathlib import Path
import shutil
import capture_normalized as c

def main():
    dest=c.HERE/'evidence-v1';assert not dest.exists(),'preserve finalv5 native evidence'
    prep=json.loads((c.OUT/'preparation.json').read_bytes());summary=json.loads((c.OUT/'summary.json').read_bytes())
    controls=json.loads((c.OUT/'negative-controls.json').read_bytes())
    assert summary['status']==controls['status']=='PASS' and controls['summary_sha256']==c.m.sha((c.OUT/'summary.json').read_bytes()),'bound complete finalv5 native proof'
    assert summary['archive_sha256']==controls['archive_sha256']==prep['archive_sha256'] and summary['runtime018_sha256']==c.RUNTIME_SHA,'selected normalizedv5 identity'
    for name,h in prep['protected_sha256'].items():assert c.m.sha((c.ROOT/name).read_bytes())==h,'protected source/production unchanged:'+name
    selected={name:c.OUT/name for name in ('preparation.json','summary.json','negative-controls.json','launch.json','launch.log','color-recipe.json')}
    for clip in c.BASELINES:
        for phase in ('smoke','full','repeat'):
            for name in ('report.json','capture.log'):selected[f'{clip}/{phase}/{name}']=c.OUT/clip/phase/name
    raw=c.ROOT/'build/standing018-proportions/foot-v5-contact'
    for name in ('preparation.json','summary.json','front-nearest4.png','mirrored-nearest4.png'):selected['raw-contact/'+name]=raw/name
    for clip,phase in [('front_arc','smoke'),('waypoint_rear','smoke'),('waypoint_rear','full')]:
        for name in ('report.json','capture.log'):selected[f'raw-contact/{clip}/{phase}/{name}']=raw/clip/phase/name
    for source in c.HERE.iterdir():
        if source.is_file():selected['helpers/'+source.name]=source
    selected['helpers/reused-motion-comparison.py']=Path(c.m.__file__)
    dest.mkdir();files={};sources={}
    for name,source in selected.items():
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        assert source.read_bytes()==target.read_bytes(),'exact finalv5 evidence copy:'+name
        files[name]=c.m.sha(target.read_bytes());sources[name]=source.relative_to(c.ROOT).as_posix()
    links={
        'color_evidence':'art/cartoon/standing018-proportions-v1/color/evidence-foot-v5/evidence.json',
        'reviewedv2_still':'art/cartoon/standing018-proportions-v1/native-review/evidence-still-v2/evidence.json',
        'reviewedv2_arrivals':'art/cartoon/standing018-proportions-v1/native-review/motion-v1/evidence-v1/evidence.json',
        'supplied_original_mirrored_reference':'art/cartoon/standing018-proportions-v1/native-review/original-mirror-v1/evidence-v1/evidence.json'}
    linked={name:{'path':path,'sha256':c.m.sha((c.ROOT/path).read_bytes())} for name,path in links.items()}
    result={'status':'PASS technical contact/motion checks; human foot correction approval pending','files_sha256':files,'exact_copy_sources':sources,'linked_evidence':linked,
        'archive_sha256':prep['archive_sha256'],'base_archive_sha256':c.m.PACKAGE_SHA,'runtime018_sha256':c.RUNTIME_SHA,'executable_sha256':c.m.EXE_SHA,
        'color_recipe_sha256':c.RECIPE_SHA,'clips':summary['clips'],'full_displays':sum(r['display_count'] for r in summary['clips'].values()),
        'changed018_displays':sum(r['changed_displays'] for r in summary['clips'].values()),'unchanged_other_displays':sum(r['unchanged_displays'] for r in summary['clips'].values()),
        'raw_diagnostic_scope':'Front smoke and mirrored route smoke/full only. Rawv5 both feet visually contact shore/sand; not the final-color publication source.',
        'normalized_scope':'Three complete clips, each smoke/full/fresh repeat. Exact route/flip/origin/timing, all non018 pixels identical,018 changes confined to its placed64x154 canvas. Candidate changes only018;2593 other member payloads remain exact.',
        'controls':'Two memory-only altered final native buffers exercise mirrored018 outside-canvas and retained023 guards; exact named failures and restored positive controls.',
        'visual_observation':'Rawv5 front and mirrored crops show both feet meeting shore/sand. The normalized runtime has identical alpha/geometry to rawv5 as recorded in linked color evidence. Human contact and motion review remains separate.',
        'excluded_bulk':'Private ZIP/executable/full PPM/PNG series remain scratch; archive and each display hashes are retained. Browser evidence is separate. No original recapture was performed.',
        'reconstruction':'Restore the pinned reviewedv2 archive and split baseline capture roots, exact observer and normalized color input. Run capture_normalized.py into fresh scratch, then check_normalized.py in the pinned image/mounts. Do not rerun this writer into historical evidence.'}
    c.m.save(dest/'evidence.json',result)
    assert all(c.m.sha((dest/name).read_bytes())==h for name,h in files.items()),'finalv5 evidence readback'
    c.m.save(dest/'readback.json',{'status':'PASS','evidence_sha256':c.m.sha((dest/'evidence.json').read_bytes()),'files_checked':len(files),'links_checked':len(linked),'protected_inputs_checked':len(prep['protected_sha256'])})
    print('PASS finalv5 native evidence frozen: '+str(len(files))+' exact files and '+str(len(linked))+' linked checkpoints')

if __name__=='__main__':main()
