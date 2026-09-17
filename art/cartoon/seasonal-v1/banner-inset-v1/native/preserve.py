"""Freeze this capture and its baseline-selection wrappers before runtime changes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
OLD=HERE.parents[1]/'banner-attachment-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def preserve(run,selection,output):
    ancestor=OLD/'native/preserve.py'
    assert sha(ancestor)=='ad237841484555cb5b0a7ebe95fb0823e0b503ea426a346f86da517f999b7943','frozen native evidence writer'
    spec=importlib.util.spec_from_file_location('inset_native_preserve',ancestor);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    legacy.HERE=HERE;legacy.preserve(run,selection,output)
    record=json.loads((output/'evidence.json').read_bytes())
    sources=[(run/'captures/adapter-config.json','captures/adapter-config.json')]
    sources.extend((OLD/name,'dependencies/banner-'+name.replace('/','-')) for name in ('native/capture.py','native/run.py','native/preserve.py','prepare.py'))
    for source,relative in sources:
        dest=output/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
        assert sha(dest)==sha(source)
        record['copies'][relative]={'source':source.relative_to(ROOT).as_posix(),'sha256':sha(dest)}
    record['limits']='Inset banner versus tied draft, exact sources and small native records retained. No human attachment approval. Runtime unchanged during capture and checked before freeze; later footprint changes do not change this historical source snapshot.'
    save(output/'evidence.json',record)
    assert all(sha(output/name)==row['sha256'] for name,row in record['copies'].items())
    save(output/'readback.json',{'status':'PASS','evidence_sha256':sha(output/'evidence.json'),'exact_copies':len(record['copies']),'source_inputs_unchanged':len(record['protected_sha256'])})
    print('PASS inset native frozen',len(record['copies']),sha(output/'evidence.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    preserve(a.run.resolve(),a.selection.resolve(),a.output.resolve())
