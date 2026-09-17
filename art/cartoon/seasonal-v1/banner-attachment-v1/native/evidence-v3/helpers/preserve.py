"""One-time compact capture/source preservation; skip this writer on replay."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def preserve(run,selection,output):
    assert not output.exists(),'fresh evidence folder required'
    captures=run/'captures';summary=json.loads((captures/'summary.json').read_bytes());inputs=json.loads((captures/'inputs.json').read_bytes())
    assert summary['status']=='PASS' and all(r['fresh_repeat']=='PASS' for r in summary['cases'].values()),'complete native evidence'
    protected=inputs['protected_sha256']
    assert all(sha(ROOT/p)==digest for p,digest in protected.items()),'capture source changed before freeze'
    copies={};output.mkdir(parents=True)
    def copy(source,relative):
        dest=output/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
        assert sha(dest)==sha(source)
        copies[relative]={'source':source.relative_to(ROOT).as_posix(),'sha256':sha(dest)}
    for name in ('launch.json','launch.log'):copy(run/name,name)
    for name in ('inputs.json','summary.json','smoke.json','negative.json','build.json','build.stdout.txt','build.stderr.txt'):copy(captures/name,'captures/'+name)
    for key in summary['cases']:
        for side in ('baseline','candidate'):
            for phase in ('smoke','repeat'):
                for name in ('report.json','capture.log'):
                    rel=key+'/'+side+'/'+phase+'/'+name;copy(captures/rel,'captures/'+rel)
    copy(selection/'preparation.json','preparation.json')
    for path in sorted(HERE.glob('*.py')):copy(path,'helpers/'+path.name)
    copy(HERE.parent/'prepare.py','helpers/prepare.py')
    for rel in protected:
        if rel!='assets/scrantic_data.zip':copy(ROOT/rel,'source/'+rel)
    observer=ROOT/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/native'
    for name in ('capture.py','driver.c'):copy(observer/name,'dependencies/integrated-'+name)
    copy(ROOT/'art/cartoon/seasonal-v1/native/capture.py','dependencies/seasonal-capture.py')
    images={p.relative_to(ROOT).as_posix():sha(p) for p in captures.rglob('*.png')}
    record={'status':'PASS','copies':copies,'native_images_sha256':images,'protected_sha256':protected,
            'archive_pair':summary['package_pair'],'native_summary_sha256':sha(captures/'summary.json'),
            'limits':'No art or attachment approval. Exact sources and small records retained; PNG bytes are losslessly represented in the separate browser atlases. Archives, executables and PPMs remain ignored.'}
    save(output/'evidence.json',record)
    assert all(sha(output/p)==v['sha256'] for p,v in copies.items())
    save(output/'readback.json',{'status':'PASS','evidence_sha256':sha(output/'evidence.json'),'exact_copies':len(copies),'source_inputs_unchanged':len(protected)})
    print('PASS native evidence',len(copies),sha(output/'evidence.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();preserve(a.run.resolve(),a.selection.resolve(),a.output.resolve())
