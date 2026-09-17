"""Source-only V4 adapter over the pinned V3 contact-ground wrapper."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ANCESTOR=HERE/'export_v3.py'
ANCESTOR_SHA='1745fccf514821726d33687f00b21ad2b4e5e50ab4ce06e1a6daaf9d8db6236a'
SOURCE=HERE/'ground-contact-v4-raw.png'
SOURCE_SHA='4a9afed1148a03f8ed01d012e221e740a3efae831aac59a9c6f3294737b325c8'


def delegate():
    if hashlib.sha256(ANCESTOR.read_bytes()).hexdigest()!=ANCESTOR_SHA:
        raise ValueError('export_v3.py: frozen wrapper differs')
    spec=importlib.util.spec_from_file_location('contact_ground_v4_delegate',ANCESTOR)
    base=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    base.SOURCE=SOURCE
    base.SOURCE_SHA=SOURCE_SHA
    return base


def prepared():
    base=delegate()
    return {'schema_version':1,'accepted':False,
            'scope':'V4 generated contact-ground source; same fixed mapping, crops and V2 foam visibility math. Human/native review pending.',
            'wrapper_ancestor':ANCESTOR.relative_to(ROOT).as_posix(),'wrapper_ancestor_sha256':ANCESTOR_SHA,
            'delegated_recipe':base.prepared()}


def render(recipe):
    base=delegate()
    mask,_=base.helpers()
    mask.require(recipe==prepared(),'recipe: V4 selected source or delegate differs')
    outputs,report=base.render(recipe['delegated_recipe'])
    report['delegated_exporter_sha256']=report['exporter_sha256']
    report['delegated_recipe_sha256']=report['recipe_sha256']
    report['exporter_sha256']=mask.sha(Path(__file__).read_bytes())
    report['recipe_sha256']=mask.sha(mask.encode(recipe))
    report['scope']=recipe['scope']
    report['wrapper_ancestor']=recipe['wrapper_ancestor']
    report['wrapper_ancestor_sha256']=ANCESTOR_SHA
    return outputs,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v4.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v4')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    mask,_=delegate().helpers()
    print('WITNESS contact-ground-v4 '+mask.sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            mask.require(not args.recipe.exists(),'recipe: refusing overwrite')
        recipe=prepared() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs,report=render(recipe)
        outputs['export-report.json']=mask.encode(report)
        if not args.check:
            mask.require(not args.output.exists(),'output: refusing overwrite')
            args.output.mkdir(parents=True)
        for name,raw in outputs.items():
            path=args.output/name
            if args.check:
                mask.require(path.read_bytes()==raw,name+': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
        if args.prepare:
            args.recipe.write_bytes(mask.encode(recipe))
        print('PASS '+json.dumps({'contacts':report['ground_contacts'],'outside_union':report['shared_ground_measurements']['master_alpha_outside_original_canvas_union']}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('FAIL '+str(exc),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
