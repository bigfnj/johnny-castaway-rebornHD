"""User-requested uniform banner inset through the existing technical filter."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
SOURCE=PARENT/'raw/003-v1.png'
SOURCE_SHA='8cada55c5d6156efcb5a2c29a49a56d8f2662ac31c3201662ec2f66456e7ab17'
ANCESTOR=PARENT/'banner-attachment-v1/export.py'
ANCESTOR_SHA='749823dcd4a31ec352ce35e45cae72412807eabe4e9fafb7d258e7c245df400c'
AFFINE=[.2116,0,-10.932,0,.2116,-68.0552]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def load():
    assert sha(ANCESTOR)==ANCESTOR_SHA,'frozen banner filter adapter identity'
    spec=importlib.util.spec_from_file_location('inset_filter',ANCESTOR);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.HERE=HERE;module.prepare=recipe
    return module

def recipe(source=SOURCE):
    assert source.resolve()==SOURCE.resolve() and sha(SOURCE)==SOURCE_SHA,'inset original clean source identity'
    old=json.loads((PARENT/'recipe-v5.json').read_bytes())
    row=copy.deepcopy(old['frames'][3]);row.update(source='../raw/003-v1.png',scale=.2116,target_anchor=[152,.08],affine_forward=AFFINE,
        anchor_basis='Explicit user-requested 8% uniform inset, centered at world874. Measured upper cloth corners overlap existing palm fronds; no palm or source repaint.')
    return {'schema_version':1,'accepted':False,'scope':'8% clean-banner inset supersedes tie-only approach; human native attachment review pending.',
        'pillow_version':old['pillow_version'],'normalization':'none','resampling':old['resampling'],'padding_hd':old['padding_hd'],
        'reused_exporter_sha256':old['adapter']['reused_exporter_sha256'],'parent_recipe_sha256':sha(PARENT/'recipe-v5.json'),
        'measurements_sha256':sha(HERE/'measurements-v1.json'),'reduction_fraction':.08,'frames':[row]}

def render(selected):
    legacy=load();outputs,report=legacy.render(selected,False)
    report.update(exporter_sha256=sha(Path(__file__)),fit_adapter_sha256=ANCESTOR_SHA,
                  scope=selected['scope'],measurements_sha256=selected['measurements_sha256'])
    return outputs,report

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--recipe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    print('WITNESS banner-inset-export '+sha(Path(__file__)))
    selected=recipe() if a.prepare else json.loads(a.recipe.read_bytes())
    outputs,report=render(selected);outputs['export-report.json']=(json.dumps(report,indent=2)+'\n').encode()
    if a.prepare:assert not a.recipe.exists(),'fresh recipe required'
    if not a.check:assert not a.output.exists(),'fresh export output required'
    for name,data in outputs.items():
        target=a.output/name
        if a.check:assert target.read_bytes()==data,'exact replay: '+name
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    if a.prepare:a.recipe.write_text(json.dumps(selected,indent=2)+'\n',encoding='utf-8')
    print('PASS inset export',report['outputs_sha256']['BMP/HOLIDAY.BMP/003.png'],report['outside_runtime_max_alpha'])

if __name__=='__main__':main()
