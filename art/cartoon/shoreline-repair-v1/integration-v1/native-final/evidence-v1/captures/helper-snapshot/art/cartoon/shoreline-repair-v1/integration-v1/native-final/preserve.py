"""One-time compact native evidence; replay captures into a fresh build directory."""
import argparse
import json
from pathlib import Path
import shutil
import contract as c

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--checks',type=Path,required=True);a=p.parse_args()
    out=c.HERE/'evidence-v1';c.require(not out.exists(),'fresh evidence output')
    summary=json.loads((a.run/'captures/summary.json').read_bytes());launch=json.loads((a.run/'launch.json').read_bytes())
    c.require(summary['status']=='PASS' and summary['smoke_captures']==28 and summary['fresh_repeat_captures']==28,'completed native matrix')
    c.require(launch['exit_code']==0 and launch['no_surviving_task_container'],'isolated launch completed')
    checks=json.loads((a.checks/'regression.json').read_bytes())
    c.require(checks['status']=='PASS' and checks['package_pair']==summary['package_pair'],'matching package controls')
    out.mkdir();files={};copies={}
    def copy(source,destination):
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        digest=c.sha(source.read_bytes());c.require(c.sha(destination.read_bytes())==digest,'exact evidence copy '+str(source))
        name=destination.relative_to(out).as_posix();files[name]=digest;copies[name]=source.resolve().relative_to(c.ROOT).as_posix()
    for name in ('launch.json','launch.log'):copy(a.run/name,out/name)
    for source in (a.run/'captures').rglob('*'):
        if source.is_file() and (source.suffix in ('.json','.log','.txt') or 'snapshot' in source.as_posix()):
            copy(source,out/'captures'/source.relative_to(a.run/'captures'))
    for source in a.checks.rglob('*'):
        if source.is_file():copy(source,out/'input-checks'/source.relative_to(a.checks))
    sources={p.relative_to(c.ROOT).as_posix():c.sha(p.read_bytes()) for p in c.HERE.glob('*.py')}
    source_inputs=json.loads((a.run/'captures/inputs.json').read_bytes())
    for name,digest in source_inputs['helpers_sha256'].items():c.require(c.sha((c.ROOT/name).read_bytes())==digest,'executed helper unchanged '+name)
    excluded={}
    for report in (a.run/'captures').rglob('report.json'):
        data=json.loads(report.read_bytes())
        for row in data['displays']:
            name=(report.parent/row['file']).relative_to(a.run).as_posix();excluded[name]=row['png_sha256']
        excluded[(report.parent/'final.png').relative_to(a.run).as_posix()]=data['png_sha256']
    for name,digest in excluded.items():c.require(c.sha((a.run/name).read_bytes())==digest,'retained scratch capture '+name)
    record={'schema_version':1,'status':'PASS','files_sha256':files,'copied_from':copies,'helper_sha256':sources,
      'package_pair':summary['package_pair'],'native_smoke':28,'fresh_repeats':28,'native_negative_controls':8,
      'excluded_native_png_sha256':excluded,'excluded':'Bulk PPMs, PNGs, runtime ZIP copies and executable stay ignored. Report pixel hashes and PNG identities retained; selected asset sources remain in their existing tracked bundles.',
      'scope':'Final standard package observed through unchanged native renderer and public walk calls in isolated Docker/Xvfb. Logical coordinates/timing unchanged; differences scoped to selected ground, enabled high waves and active holiday. Calendar/cargo decisions and original-executable parity not exercised.'}
    c.save(out/'evidence.json',record)
    c.require(all(c.sha((out/name).read_bytes())==digest for name,digest in files.items()),'all retained evidence bytes')
    c.save(out/'readback.json',{'status':'PASS','evidence_sha256':c.sha((out/'evidence.json').read_bytes()),'exact_retained_files':len(files),
      'exact_source_copies':len(copies),'excluded_png_identities_checked':len(excluded)})
    print('PASS preserved',len(files),'files',c.sha((out/'evidence.json').read_bytes()))

if __name__=='__main__':main()
