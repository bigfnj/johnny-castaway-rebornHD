"""One master resample, disjoint rectangular ground crops and existing foam."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BUNDLE = HERE.parent
BASE = BUNDLE.parent / 'seasonal-v1/export.py'
BASE_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
SOURCE_SHA = 'bde2f4f2111f532cb94a82ece74fa7745129d61e2ad909e8eadaa3fab4df7d14'
REFERENCE_SHA = '8cac030442054333c2a006a4914703b376c3f2e2bf83d7c034001f2a16d794a8'
ARCHIVE_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
SOURCE = BUNDLE / 'raw/ground-master-v2.png'
REFERENCE = BUNDLE / 'reference-master/source.json'
ARCHIVE = ROOT / 'assets/scrantic_data.zip'
if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('seasonal/export.py: frozen filter differs')
spec = importlib.util.spec_from_file_location('seasonal_filter_shared_ground', BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
BOXES = {0: (576,558,1136,662), 3: (540,612,684,670), 6: (728,638,1048,688), 9: (1036,606,1180,670)}
OWNERSHIP = {0: [(576,558,1136,662)],
             3: [(540,612,576,670), (576,662,684,670)],
             6: [(728,662,1048,688)],
             9: [(1136,606,1180,670), (1048,662,1136,670)]}
FRAMES = (0,3,4,5,6,7,8,9,10,11)


def family(frame):
    return 0 if frame == 0 else frame - (frame % 3)


def inside(x, y, box):
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def prepared():
    for path, checksum in [(SOURCE,SOURCE_SHA),(REFERENCE,REFERENCE_SHA),(ARCHIVE,ARCHIVE_SHA)]:
        base.require(base.sha(path.read_bytes()) == checksum, path.name + ': source identity differs')
    ref = json.loads(REFERENCE.read_bytes())
    with Image.open(SOURCE) as im:
        base.require(im.mode == 'RGBA' and list(im.size) == ref['guide_canvas'], 'master: source canvas/mode differs')
    frames = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for frame in FRAMES:
            group = family(frame)
            box = BOXES[group]
            member = f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
            data = archive.read(member)
            with Image.open(io.BytesIO(data)) as im:
                base.require(list(im.size) == [box[2]-box[0],box[3]-box[1]], f'{frame:03}: original canvas differs')
            frames.append({'frame': frame, 'path': f'BMP/BACKGRND.BMP/{frame:03}.png',
                           'canvas': [box[2]-box[0],box[3]-box[1]], 'world_box': list(box),
                           'ground_family': group, 'owned_ground_rectangles': [list(r) for r in OWNERSHIP[group]],
                           'previous_member': member, 'previous_member_sha256': base.sha(data),
                           'foam_composition': 'none' if frame == 0 else 'unchanged source foam OVER owned master ground'})
    return {'schema_version':1, 'accepted':False, 'source':SOURCE.relative_to(ROOT).as_posix(),
            'source_sha256':SOURCE_SHA, 'reference':REFERENCE.relative_to(ROOT).as_posix(), 'reference_sha256':REFERENCE_SHA,
            'archive':ARCHIVE.relative_to(ROOT).as_posix(), 'archive_sha256':ARCHIVE_SHA,
            'filter_sha256':BASE_SHA, 'pillow_version':base.PIL.__version__, 'resampling':base.FILTERS,
            'world_crop':ref['world_hd_crop_xyxy'], 'master_canvas':ref['cropped_runtime_canvas'],
            'affine_forward':ref['guide_to_crop_runtime_affine'], 'padding_hd':base.PAD,
            'ground_ownership': 'Disjoint rectangular crops;000 then left,center,right. Center owns the12x8 overlap outside000. No material mask or alpha threshold.',
            'scope':'Unapproved coherent-ground diagnostic; existing foam inputs unchanged before source-over composition. No tide/scene acceptance.',
            'frames':frames}


def alpha_stats(values):
    values = list(values)
    return {'nonzero_pixels':sum(a>0 for a in values), 'alpha8_pixels':sum(a>=8 for a in values),
            'maximum_alpha':max(values,default=0), 'alpha_sum':sum(values)}


def render(recipe):
    base.require(recipe == prepared(), 'recipe: selected master or fixed composition differs')
    source = Image.open(SOURCE).convert('RGBA')
    padded = base.resample(source, recipe['master_canvas'], recipe['affine_forward'])
    width,height = recipe['master_canvas']
    master = padded.crop((base.PAD,base.PAD,base.PAD+width,base.PAD+height))
    wx,wy,_,_ = recipe['world_crop']
    count = [0]*(width*height)
    ground = {}
    for group, rectangles in OWNERSHIP.items():
        box = BOXES[group]
        layer = Image.new('RGBA',(box[2]-box[0],box[3]-box[1]))
        for x0,y0,x1,y1 in rectangles:
            x0,y0,x1,y1 = max(x0,wx),max(y0,wy),min(x1,wx+width),min(y1,wy+height)
            if x1 <= x0 or y1 <= y0:
                continue
            piece = master.crop((x0-wx,y0-wy,x1-wx,y1-wy))
            layer.paste(piece,(x0-box[0],y0-box[1]))
            for y in range(y0,y1):
                for x in range(x0,x1):
                    count[(y-wy)*width+x-wx] += 1
        ground[group] = layer
    base.require(not any(n>1 for n in count), 'master: duplicate ground ownership')
    expected = [any(inside(x+wx,y+wy,b) for b in BOXES.values()) for y in range(height) for x in range(width)]
    base.require(all(bool(n)==covered for n,covered in zip(count,expected)), 'master: ground ownership differs from original-canvas union')
    alpha = list(master.getchannel('A').get_flattened_data())
    uncovered = alpha_stats(a for a,n in zip(alpha,count) if n==0)
    outside = padded.getchannel('A')
    outside.paste(0,(base.PAD,base.PAD,base.PAD+width,base.PAD+height))
    outputs = {'master-ground.png':base.png(master),'master-padded.png':base.png(padded)}
    for group,layer in ground.items():
        outputs[f'ground/{group:03}.png'] = base.png(layer)
    rows = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in recipe['frames']:
            frame = row['frame']
            layer = ground[row['ground_family']]
            if frame != 0:
                foam = Image.open(io.BytesIO(archive.read(row['previous_member']))).convert('RGBA')
                rendered = Image.alpha_composite(layer,foam)
            else:
                rendered = layer
            outputs[row['path']] = base.png(rendered)
            rows.append({**row,'sha256':base.sha(outputs[row['path']]), 'ground_rgba_sha256':base.sha(layer.tobytes())})
    raw_alpha = source.getchannel('A')
    raw_bounds = raw_alpha.point(lambda a:255 if a>=8 else 0).getbbox()
    s,_,tx,_,_,ty = recipe['affine_forward']
    raw_window = (int(-tx/s),int(-ty/s),int((width-tx)/s),int((height-ty)/s))
    raw_outside = raw_alpha.copy()
    raw_outside.paste(0,raw_window)
    report = {'schema_version':1,'status':'DIAGNOSTIC_EXPORTED','accepted':False,'scope':recipe['scope'],
              'exporter_sha256':base.sha(Path(__file__).read_bytes()),'recipe_sha256':base.sha(base.encode(recipe)),
              'source_sha256':SOURCE_SHA,'reference_sha256':REFERENCE_SHA,'archive_sha256':ARCHIVE_SHA,
              'uniform_resample_count':1,'source_alpha8_bounds':raw_bounds,
              'source_alpha8_bounds_in_master_hd':[raw_bounds[0]*s+tx,raw_bounds[1]*s+ty,raw_bounds[2]*s+tx,raw_bounds[3]*s+ty],
              'raw_alpha_outside_master_crop':alpha_stats(raw_outside.get_flattened_data()),
              'filtered_alpha_outside_master_crop':alpha_stats(outside.get_flattened_data()),
              'master_alpha_outside_original_canvas_union':uncovered,
              'ground_crop_ownership':{'duplicate_pixels':sum(n>1 for n in count),'coverage_matches_original_canvas_union':True,
                                       'meaningful_owned_pixels':sum(a>=8 and n==1 for a,n in zip(alpha,count))},
              'baked_foam_observation':'Selected raw visually inspected: sand and dark outline, no visible white/blue foam. This is a visual observation, not an automatic material classifier.',
              'alpha_note':'No alpha threshold or material mask. Runtime ground uses exact rectangular master crops. New wave PNG alpha is source-over composition of those crops and the unchanged foam inputs. Outside-union master pixels cannot be represented and are reported, not fitted away.',
              'frames':rows,'outputs_sha256':{name:base.sha(data) for name,data in outputs.items()}}
    return outputs,report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v1.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v1')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    print('WITNESS shared-ground '+base.sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            base.require(not args.recipe.exists(),'recipe: refusing to overwrite')
        recipe = prepared() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs,report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if not args.check:
            base.require(not args.output.exists(),'output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name,data in outputs.items():
            path = args.output/name
            if args.check:
                base.require(path.read_bytes()==data,name+': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
        if args.prepare:
            args.recipe.parent.mkdir(parents=True,exist_ok=True)
            args.recipe.write_bytes(base.encode(recipe))
        print('DIAGNOSTIC '+json.dumps({'frames':len(report['frames']),'outside_union':report['master_alpha_outside_original_canvas_union'],
                                      'outside_crop':report['filtered_alpha_outside_master_crop']}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('FAIL '+str(exc),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
