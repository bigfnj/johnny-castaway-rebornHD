"""Ground-alpha visibility masking of retained foam; no resampling or redraw."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANCESTOR = HERE.parent / 'shared-master'
SELECTED = ANCESTOR / 'candidates/v1'
ARCHIVE = ROOT / 'assets/scrantic_data.zip'
PINS = {
    'export.py': '760beeb1919e9ec107245b8af1a8cccc208c30b0c3bca178d1495c594b4274f6',
    'recipe-v1.json': 'fd9006b0bd955234c9a5af718de55b69218bbbdeb7ce93d3063fdbcc6b5f4bff',
    'candidates/v1/export-report.json': '80f9c2c7eaaabce154f4a5b3bd89ee28145041763a8bc81af32629cb00994f33',
}
ARCHIVE_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def encode(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def png(im):
    stream = io.BytesIO()
    im.save(stream, format='PNG', compress_level=9)
    return stream.getvalue()


def prepared():
    for name, digest in PINS.items():
        require(sha((ANCESTOR/name).read_bytes()) == digest, name + ': frozen ancestor differs')
    require(sha(ARCHIVE.read_bytes()) == ARCHIVE_SHA, 'archive: frozen foam source differs')
    prior = json.loads((ANCESTOR/'recipe-v1.json').read_bytes())
    report = json.loads((SELECTED/'export-report.json').read_bytes())
    # Bind every frozen output, including the original runtime PNGs and padded master.
    for name, digest in report['outputs_sha256'].items():
        require(sha((SELECTED/name).read_bytes()) == digest, name + ': frozen ground/export differs')
    return {'schema_version': 1, 'accepted': False, 'pillow_version': PIL.__version__,
            'scope': 'Packing/layer occlusion diagnostic, pending human scene review.',
            'operation': 'Foam alpha becomes round(original alpha * (255 - world-aligned master alpha) / 255); foam RGB stays unchanged. Exact integer rule: (alpha * (255 - ground_alpha) + 127) // 255.',
            'limits': 'This alpha visibility mask changes partial-edge blending. It is not exact global ground-over-foam source-over. No cutoff, resample, shift, RGB painting or raw source edit.',
            'ancestor': ANCESTOR.relative_to(ROOT).as_posix(), 'ancestor_sha256': PINS,
            'ancestor_outputs_sha256': report['outputs_sha256'],
            'archive': ARCHIVE.relative_to(ROOT).as_posix(), 'archive_sha256': ARCHIVE_SHA,
            'world_crop': prior['world_crop'], 'master_canvas': prior['master_canvas'],
            'ground_ownership': prior['ground_ownership'],
            'frames': [{**row, 'foam_composition': 'none' if row['frame']==0 else 'ground-alpha visibility-masked foam OVER exact owned ground'} for row in prior['frames']]}


def occlude(foam, master, origin, world_crop):
    result = foam.copy()
    fp, mp, rp = foam.load(), master.load(), result.load()
    stats = {'opaque_ground_pixels': 0, 'omitted_nonzero_foam_pixels': 0,
             'changed_foam_alpha_pixels': 0, 'nonopaque_land_nonzero_foam_pixels': 0,
             'maximum_single_layer_continuous_blend_deviation_bound_rgb': 0.0,
             'partial_edge_witness': None}
    for y in range(foam.height):
        for x in range(foam.width):
            mx, my = x+origin[0]-world_crop[0], y+origin[1]-world_crop[1]
            a = mp[mx,my][3] if 0 <= mx < master.width and 0 <= my < master.height else 0
            original = fp[x,y]
            alpha = (original[3] * (255 - a) + 127) // 255
            rp[x,y] = (*original[:3],alpha)
            stats['opaque_ground_pixels'] += a == 255
            stats['omitted_nonzero_foam_pixels'] += original[3] > 0 and alpha == 0
            stats['changed_foam_alpha_pixels'] += original[3] != alpha
            stats['nonopaque_land_nonzero_foam_pixels'] += 0 < a < 255 and original[3] > 0
            # For one foam layer over one already-composited ground layer, the
            # continuous-RGB difference from exact ground-over-foam is
            # ag*(1-ag)*af*(background_rgb-ground_rgb). Native overlap/order and
            # byte rounding are separate; this is a bound, not a native error measurement.
            bound = a*(255-a)*original[3]/(255*255)
            if bound > stats['maximum_single_layer_continuous_blend_deviation_bound_rgb']:
                stats['maximum_single_layer_continuous_blend_deviation_bound_rgb'] = bound
                stats['partial_edge_witness'] = {'world':[x+origin[0],y+origin[1]], 'ground_alpha':a, 'foam_alpha':original[3], 'masked_foam_alpha':alpha}
    return result, stats


def render(recipe):
    require(recipe == prepared(), 'recipe: alpha visibility contract differs')
    master = Image.open(SELECTED/'master-ground.png').convert('RGBA')
    outputs, rows = {}, []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in recipe['frames']:
            frame = row['frame']
            ground_path = SELECTED/f"ground/{row['ground_family']:03}.png"
            ground_raw = ground_path.read_bytes()
            ground = Image.open(io.BytesIO(ground_raw)).convert('RGBA')
            details = {}
            if frame == 0:
                raw = (SELECTED/row['path']).read_bytes()
            else:
                foam_raw = archive.read(row['previous_member'])
                require(sha(foam_raw) == row['previous_member_sha256'], f'{frame:03}: foam source differs')
                foam = Image.open(io.BytesIO(foam_raw)).convert('RGBA')
                retained, details = occlude(foam,master,row['world_box'][:2],recipe['world_crop'])
                raw = png(Image.alpha_composite(ground,retained))
                details.update({'input_foam_rgba_sha256': sha(foam.tobytes()), 'occluded_foam_rgba_sha256': sha(retained.tobytes())})
            outputs[row['path']] = raw
            rows.append({**row, 'sha256': sha(raw), 'ground_png_sha256': sha(ground_raw),
                         'ground_rgba_sha256': sha(ground.tobytes()), **details})
    report = {'schema_version':1, 'status':'DIAGNOSTIC_EXPORTED', 'accepted':False,
              'scope':recipe['scope'], 'operation':recipe['operation'], 'limits':recipe['limits'],
              'exporter_sha256':sha(Path(__file__).read_bytes()), 'recipe_sha256':sha(encode(recipe)),
              'master_png_sha256':sha((SELECTED/'master-ground.png').read_bytes()),
              'blend_caveat':'For a single continuous layer with ground already below foam, masking differs from exact ground-over-foam by ag*(1-ag)*af*(background_rgb-ground_rgb). Maximum possible per-channel magnitude is 63.75 before byte rounding; this is an analytic bound, not measured native scene error. Multiple foam layers/order and static shadows are not covered by this single-layer formula.',
              'resample_count':0, 'sprite000_byte_identical':outputs[recipe['frames'][0]['path']] == (SELECTED/recipe['frames'][0]['path']).read_bytes(),
              'inherited_clipping':{k:json.loads((SELECTED/'export-report.json').read_bytes())[k] for k in ('filtered_alpha_outside_master_crop','master_alpha_outside_original_canvas_union')},
              'frames':rows, 'outputs_sha256':{name:sha(raw) for name,raw in outputs.items()}}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v2.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v2')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    print('WITNESS foam-contact '+sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            require(not args.recipe.exists(), 'recipe: refusing to overwrite')
        recipe = prepared() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = encode(report)
        if not args.check:
            require(not args.output.exists(), 'output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name, raw in outputs.items():
            path = args.output/name
            if args.check:
                require(path.read_bytes() == raw, name+': replay differs')
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
        if args.prepare:
            args.recipe.write_bytes(encode(recipe))
        print('PASS '+json.dumps({'frames':len(report['frames']), 'sprite000_byte_identical':report['sprite000_byte_identical']}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('FAIL '+str(exc),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
