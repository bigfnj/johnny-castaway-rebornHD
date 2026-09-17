"""Explicit LF recipe serialization; identical inset pixels to the shown V1."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ANCESTOR=HERE/'export.py'
ANCESTOR_SHA='6fab1fa6f5335ca6ddbac22fcba5172d5a86cdd733e48f27034bd39f4d224a74'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,indent=2)+'\n').encode('utf-8')

def read_recipe(path):
    raw=path.read_bytes();value=json.loads(raw)
    if raw!=encode(value):raise ValueError(path.name+': recipe bytes must be canonical UTF-8 LF')
    return value,raw

def render(recipe):
    assert sha(ANCESTOR.read_bytes())==ANCESTOR_SHA,'frozen historical inset exporter'
    spec=importlib.util.spec_from_file_location('inset_v1_pixels',ANCESTOR);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    selected=legacy.recipe() if recipe is None else recipe
    outputs,report=legacy.render(selected);raw=encode(selected)
    assert report['recipe_sha256']==sha(raw),'inherited canonical recipe-content hash'
    report.update(exporter_sha256=sha(Path(__file__).read_bytes()),historical_exporter_sha256=ANCESTOR_SHA,
        recipe_sha256=sha(raw),recipe_serialization='UTF-8 without BOM, LF newlines; hash is of the exact saved recipe bytes.',
        historical_v1_recipe={'path':'recipe-v1.json','actual_bytes_sha256':sha((HERE/'recipe-v1.json').read_bytes()),
            'canonical_content_sha256':sha(encode(json.loads((HERE/'recipe-v1.json').read_bytes()))),
            'limitation':'V1 report hashed canonical LF content, while its Windows recipe writer saved CRLF. V1 pixels and frozen evidence remain historical; use this V2 for integration.'})
    return selected,raw,outputs,report

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--recipe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    print('WITNESS banner-inset-export-v2 '+sha(Path(__file__).read_bytes()))
    if a.prepare:
        assert not a.recipe.exists(),'fresh V2 recipe required';value=None;actual=None
    else:value,actual=read_recipe(a.recipe)
    selected,raw,outputs,report=render(value)
    if actual is not None:assert raw==actual and report['recipe_sha256']==sha(actual),'exact saved V2 recipe hash'
    outputs['export-report.json']=encode(report)
    if not a.check:assert not a.output.exists(),'fresh V2 export directory required'
    for name,data in outputs.items():
        target=a.output/name
        if a.check:assert target.read_bytes()==data,'V2 exact replay: '+name
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    if a.prepare:a.recipe.write_bytes(raw)
    assert sha(a.recipe.read_bytes())==report['recipe_sha256'],'V2 saved recipe/report identity'
    print('PASS inset export V2',report['recipe_sha256'],report['outputs_sha256']['BMP/HOLIDAY.BMP/003.png'])

if __name__=='__main__':main()
