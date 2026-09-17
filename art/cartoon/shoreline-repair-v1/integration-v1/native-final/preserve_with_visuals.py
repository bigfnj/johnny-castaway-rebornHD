"""Single checkpoint operation adding only the three requested exact scene PNGs.

The original preservation helper was snapshotted before the native run. Keep it
unchanged; this final wrapper completes the checkpoint before it is published.
"""
import json
from pathlib import Path
import shutil
import sys
import contract as c
import preserve

def main():
    preserve.main()
    run=Path(sys.argv[sys.argv.index('--run')+1]).resolve()
    out=c.HERE/'evidence-v1';record=json.loads((out/'evidence.json').read_bytes())
    for case in ('clover','pumpkin','banner'):
        source=run/'captures/day'/case/'candidate/smoke/final.png'
        report=json.loads((source.parent/'report.json').read_bytes())
        digest=c.sha(source.read_bytes());c.require(digest==report['png_sha256'],'representative scene '+case)
        name='representative/day-'+case+'.png';target=out/name;target.parent.mkdir(exist_ok=True)
        shutil.copyfile(source,target);c.require(c.sha(target.read_bytes())==digest,'exact representative copy '+case)
        record['files_sha256'][name]=digest;record['copied_from'][name]=source.relative_to(c.ROOT).as_posix()
    record['representative_scope']='Exactly three unmodified final-package native PNGs: day clovers, pumpkin and banner. Other frames stay ignored with their identities retained.'
    observations={
      'day/clover/candidate/smoke/final.png':'Full-size clover bases visibly sit on sand.',
      'day/pumpkin/candidate/smoke/final.png':'Pumpkin sits on the selected island without a visible floating base.',
      'day/tree/candidate/smoke/final.png':'Tree and its base remain fully visible on the sand.',
      'day/banner/candidate/smoke/final.png':'Both inset upper cloth corners visibly meet green fronds.',
      'motion/low_none/candidate/smoke/final.png':'Compared visually with the baseline: lower beach, rocks and low surf retain the known pixel-art fallback. This is not a claim that the low-tide artwork is complete.',
      'motion/night_shift_clover/candidate/smoke/final.png':'Island, clovers and waves follow the selected offset; existing NIGHT.SCR and cloud fallback remain visible.',
      'motion/johnny_front/candidate/smoke/display-044.png':'Observed frame018 at native433,225, unmirrored,3240ms; both feet visibly contact ground.',
      'motion/johnny_rear/candidate/smoke/display-064.png':'Observed frame018 at native394,209, mirrored,4920ms; both feet visibly contact ground.'}
    record['visual_readback']=[{'source':(run/'captures'/name).relative_to(c.ROOT).as_posix(),
       'png_sha256':c.sha((run/'captures'/name).read_bytes()),'observation':note} for name,note in observations.items()]
    record['visual_readback_scope']='Read-only assistant inspection of the exact smoke PNGs. No new visual blocker found; this does not replace or expand the separately recorded human approvals.'
    c.save(out/'evidence.json',record)
    for name,digest in record['files_sha256'].items():c.require(c.sha((out/name).read_bytes())==digest,'final retained bytes '+name)
    c.save(out/'readback.json',{'status':'PASS','evidence_sha256':c.sha((out/'evidence.json').read_bytes()),
       'exact_retained_files':len(record['files_sha256']),'exact_source_copies':len(record['copied_from']),
       'representative_native_pngs':3,'excluded_png_identities_checked':len(record['excluded_native_png_sha256'])})
    print('PASS final visual/native checkpoint',len(record['files_sha256']),c.sha((out/'evidence.json').read_bytes()))

if __name__=='__main__':main()
