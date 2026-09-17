"""New contact-ground source with frozen mapping, crops and visibility math."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE/'ground-contact-raw.png'
SOURCE_SHA = '7265fac3d191fe2d3d948fe81c0b465ead12ffc20a6c95a8996bc40b9e5cdca1'
HELPERS = {
    HERE/'export.py': 'fae28aba1181761777ae4ed43e088fb6a1cc51b08f20db39135ac81fe4ae1445',
    HERE.parent/'shared-master/export.py': '760beeb1919e9ec107245b8af1a8cccc208c30b0c3bca178d1495c594b4274f6',
}


def helpers():
    import hashlib
    loaded=[]
    for index,(path,digest) in enumerate(HELPERS.items()):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError(path.name+': frozen helper differs')
        spec=importlib.util.spec_from_file_location(f'contact_v3_helper_{index}',path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded.append(module)
    mask,shared=loaded
    # Explicit in-memory source substitution; old file and globals in other
    # processes remain untouched. All mapping/ownership/filter constants stay fixed.
    shared.SOURCE=SOURCE
    shared.SOURCE_SHA=SOURCE_SHA
    return mask,shared


def prepared():
    mask,shared=helpers()
    ground=shared.prepared()
    return {'schema_version':1,'accepted':False,
            'scope':'Technical contact-ground draft pending native/human review.',
            'source':SOURCE.relative_to(ROOT).as_posix(),'source_sha256':SOURCE_SHA,
            'helpers_sha256':{path.relative_to(ROOT).as_posix():digest for path,digest in HELPERS.items()},
            'ground_recipe':ground,
            'visibility':'Use frozen V2 occlude: foam alpha = (original alpha * (255 - master alpha) + 127) // 255; foam RGB unchanged.',
            'limits':'Intentional generated ground edit. No old-ground byte-identity claim. Fixed mapping and disjoint crop ownership are unchanged. Visibility masking is not exact global ground-over-foam compositing. Props are not exported or edited here.'}


def render(recipe):
    mask,shared=helpers()
    mask.require(recipe==prepared(),'recipe: selected contact source or frozen contract differs')
    intermediate,ground_report=shared.render(recipe['ground_recipe'])
    # Keep the shared single-resample master and exact ground crops. Its old
    # foam-over-ground outputs are intermediate only; replace those nine below.
    outputs=dict(intermediate)
    master=Image.open(io.BytesIO(outputs['master-ground.png'])).convert('RGBA')
    rows=[]
    with zipfile.ZipFile(shared.ARCHIVE) as archive:
        for row in recipe['ground_recipe']['frames']:
            frame=row['frame']
            ground_raw=outputs[f"ground/{row['ground_family']:03}.png"]
            ground=Image.open(io.BytesIO(ground_raw)).convert('RGBA')
            stats={}
            if frame:
                original=archive.read(row['previous_member'])
                mask.require(mask.sha(original)==row['previous_member_sha256'],f'{frame:03}: original foam identity')
                foam=Image.open(io.BytesIO(original)).convert('RGBA')
                retained,stats=mask.occlude(foam,master,row['world_box'][:2],recipe['ground_recipe']['world_crop'])
                outputs[row['path']]=mask.png(Image.alpha_composite(ground,retained))
                stats.update({'input_foam_rgba_sha256':mask.sha(foam.tobytes()),'masked_foam_rgba_sha256':mask.sha(retained.tobytes())})
            rows.append({**row,'foam_composition':'none' if not frame else 'V2 visibility-masked foam OVER new exact owned ground',
                         'sha256':mask.sha(outputs[row['path']]),'ground_png_sha256':mask.sha(ground_raw),**stats})
    wx,wy,_,_=recipe['ground_recipe']['world_crop']
    contacts=[{'world':[x,y],'ground_rgba':list(master.getpixel((x-wx,y-wy)))} for x,y in ((757,646),(785,656),(787,658))]
    crop=recipe['ground_recipe']['world_crop']
    uncovered=[]
    for y in range(master.height):
        for x in range(master.width):
            rgba=master.getpixel((x,y))
            if rgba[3] and not any(shared.inside(x+wx,y+wy,box) for box in shared.BOXES.values()):
                uncovered.append({'world':[x+wx,y+wy],'rgba':list(rgba)})
    fields=('source_alpha8_bounds','source_alpha8_bounds_in_master_hd','raw_alpha_outside_master_crop',
            'filtered_alpha_outside_master_crop','master_alpha_outside_original_canvas_union','ground_crop_ownership')
    report={'schema_version':1,'status':'DIAGNOSTIC_EXPORTED','accepted':False,
            'scope':recipe['scope'],'limits':recipe['limits'],
            'exporter_sha256':mask.sha(Path(__file__).read_bytes()),'recipe_sha256':mask.sha(mask.encode(recipe)),
            'source_sha256':SOURCE_SHA,'helpers_sha256':recipe['helpers_sha256'],
            'uniform_resample_count':ground_report['uniform_resample_count'],
            'world_crop':crop,'affine_forward':recipe['ground_recipe']['affine_forward'],
            'ground_contacts':contacts,'outside_union_nonzero_pixels':uncovered,
            'shared_ground_measurements':{key:ground_report[key] for key in fields},
            'blend_caveat':'The frozen V2 mask changes partial-edge semantics; its per-frame values are analytic single-layer bounds, not measured native scene error. Native packaging separately verifies all props unchanged.',
            'frames':rows,'outputs_sha256':{name:mask.sha(raw) for name,raw in outputs.items()}}
    return outputs,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v3.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v3')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    mask,_=helpers()
    print('WITNESS contact-ground-v3 '+mask.sha(Path(__file__).read_bytes()))
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
