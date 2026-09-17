"""Diagnostic shore export at the fixed original-guide transform, without fitting.

Each explicit frame/source recipe is immutable. Report cropped alpha, including
meaningful alpha, rather than shrinking, moving, thresholding or accepting art.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'seasonal-v1/export.py'
BASE_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
REFERENCE_SHA = '3c721e73170208378577f2320d8343afdf4e3eac05b802a581445045972c4867'
spec = importlib.util.spec_from_file_location('seasonal_filter_for_shore', BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def reference(frame):
    base.require(base.sha(BASE.read_bytes()) == BASE_SHA, 'seasonal-v1/export.py: filter identity differs')
    raw = (HERE / 'reference/source.json').read_bytes()
    base.require(base.sha(raw) == REFERENCE_SHA, 'reference/source.json: identity differs')
    rows = [r for r in json.loads(raw)['guides'] if r.get('member') == f'native/BMP/BACKGRND.BMP/{frame:03}.png']
    base.require(len(rows) == 1, f'{frame:03}: original guide missing')
    row = rows[0]
    base.require(base.sha((HERE / 'reference' / row['file']).read_bytes()) == row['sha256'], f'{frame:03}: guide identity differs')
    return row


def prepare(frame, source):
    guide = reference(frame)
    source = source.resolve()
    base.require(source.is_relative_to((HERE / 'raw').resolve()), f'{frame:03}: source outside raw folder')
    with Image.open(source) as image:
        base.require(image.mode == 'RGBA' and list(image.size) == guide['canvas'], f'{frame:03}: source canvas/mode differs')
    return {'schema_version': 1, 'accepted': False, 'frame': frame,
            'scope': 'Unapproved diagnostic fixed-registration shoreline; meaningful crop is reported, not hidden by fitting.',
            'source': source.relative_to(HERE).as_posix(), 'source_sha256': base.sha(source.read_bytes()),
            'source_canvas': guide['canvas'], 'runtime_canvas': guide['runtime_canvas'],
            'runtime_path': f'BMP/BACKGRND.BMP/{frame:03}.png',
            'guide_file': guide['file'], 'guide_sha256': guide['sha256'], 'reference_sha256': REFERENCE_SHA,
            'affine_forward': guide['guide_to_runtime_affine'], 'guide_offset_xy': guide['offset_xy'],
            'scene_origin_hd': guide['scene_origin_hd'], 'filter_sha256': BASE_SHA,
            'pillow_version': base.PIL.__version__, 'resampling': base.FILTERS, 'padding_hd': base.PAD}


def alpha_stats(alpha, rect):
    outside = alpha.copy()
    outside.paste(0, rect)
    hist = outside.histogram()
    return {'nonzero_pixels': sum(hist[1:]), 'alpha8_pixels': sum(hist[8:]),
            'alpha255_pixels': hist[255], 'maximum_alpha': outside.getextrema()[1],
            'alpha_sum': sum(i*n for i, n in enumerate(hist)),
            'alpha8_bounds': outside.point(lambda a:255 if a>=8 else 0).getbbox()}


def render(recipe):
    frame = recipe['frame']
    base.require(recipe == prepare(frame, HERE / recipe['source']), f'{frame:03}: recipe/source/original registration differs')
    source = Image.open(HERE / recipe['source']).convert('RGBA')
    width, height = recipe['runtime_canvas']
    s, _, tx, _, _, ty = recipe['affine_forward']
    padded = base.resample(source, [width, height], recipe['affine_forward'])
    crop = (base.PAD, base.PAD, base.PAD+width, base.PAD+height)
    fixed = padded.crop(crop)
    # Full source-guide rendering accounts for faint marks beyond the usual
    #32px local pad. All guide offsets are integral after the original .25 scale.
    offset = [v*s for v in recipe['guide_offset_xy']]
    base.require(all(v == int(v) for v in offset), f'{frame:03}: nonintegral guide origin')
    full = base.resample(source, [int(source.width*s), int(source.height*s)], [s,0,0,0,s,0])
    whole_crop = (base.PAD+int(offset[0]), base.PAD+int(offset[1]),
                  base.PAD+int(offset[0])+width, base.PAD+int(offset[1])+height)
    base.require(full.crop(whole_crop).tobytes() == fixed.tobytes(), f'{frame:03}: full-guide registration differs')
    x, y = recipe['guide_offset_xy']
    raw_crop = (x, y, x+int(width/s), y+int(height/s))
    alpha = source.getchannel('A')
    bounds = alpha.point(lambda a:255 if a>=8 else 0).getbbox()
    outputs = {recipe['runtime_path']: base.png(fixed), 'padded.png': base.png(padded),
               'full-guide-padded.png': base.png(full)}
    outside = alpha_stats(full.getchannel('A'), whole_crop)
    report = {'schema_version': 1, 'accepted': False, 'status': 'DIAGNOSTIC_EXPORTED', 'scope': recipe['scope'],
              'frame': frame, 'exporter_sha256': base.sha(Path(__file__).read_bytes()),
              'recipe_sha256': base.sha(base.encode(recipe)), 'source_sha256': recipe['source_sha256'],
              'filter_sha256': BASE_SHA, 'runtime_canvas': [width, height],
              'affine_forward': recipe['affine_forward'], 'source_alpha8_bounds': bounds,
              'source_alpha8_edge_bounds_hd': [bounds[0]*s+tx,bounds[1]*s+ty,bounds[2]*s+tx,bounds[3]*s+ty],
              'source_alpha_outside_guide_window': alpha_stats(alpha, raw_crop),
              'filtered_alpha_outside_runtime': outside,
              'filtered_alpha_outside_runtime_within_local_pad': alpha_stats(padded.getchannel('A'), crop),
              'meaningful_clipping_present': outside['alpha8_pixels'] > 0,
              'coordinate_note': 'Source bounds use raw coordinates; filtered full-guide stats include32HD padding. Runtime crop is the original fixed canvas.',
              'outputs_sha256': {name: base.sha(data) for name, data in outputs.items()}}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--frame', type=int, choices=(3,7,9))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS shore-export ' + base.sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            base.require(args.frame is not None and args.source is not None, 'prepare: explicit frame and source required')
            base.require(not args.recipe.exists(), 'recipe: refusing to overwrite')
            recipe = prepare(args.frame, args.source)
        else:
            recipe = json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if not args.check:
            base.require(not args.output.exists(), 'output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name, data in outputs.items():
            path = args.output / name
            if args.check:
                base.require(path.read_bytes() == data, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if args.prepare:
            args.recipe.parent.mkdir(parents=True, exist_ok=True)
            args.recipe.write_bytes(base.encode(recipe))
        print('DIAGNOSTIC ' + json.dumps({'frame': recipe['frame'], 'runtime_sha256': report['outputs_sha256'][recipe['runtime_path']],
                                        'crop': report['filtered_alpha_outside_runtime']}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
