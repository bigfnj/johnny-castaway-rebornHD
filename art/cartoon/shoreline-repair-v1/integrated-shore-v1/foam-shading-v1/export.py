"""Single-frame shading revision using the frozen offshore full-source transform."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FROZEN = HERE.parent / 'foam-refresh-v1/export_v2.py'
FROZEN_SHA = '364c6d69eb2b062982cd35568c364d9204ccb915e5da744f6bc79163c535c847'
SOURCE = HERE / '007-raw-v1.png'
SOURCE_SHA = 'bccf1e15c476c78ed7ffb6f842eaa001c763eff4209c63b3d47162097c5fa8f2'
OLD = HERE.parent / 'foam-refresh-v1/candidates/v2'
OLD_REPORT_SHA = 'ceb1dd987098c6f5ee36a77988009b1f290e44f421bfd7f08cd275c34bca999d'
WORLD = [696, 548, 1080, 804]
FOOTPRINT = {'id': 'cartoon-island-center-foam-v1', 'canvas': [384, 256], 'offset_hd': [-32, -90]}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def helpers():
    require(sha(FROZEN.read_bytes()) == FROZEN_SHA, 'export_v2.py: frozen helper differs')
    spec = importlib.util.spec_from_file_location('frozen_offshore_full_source', FROZEN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prior = module.load()
    return prior.inputs()

def source(raw):
    import io
    require(sha(raw) == SOURCE_SHA, '007: selected raw identity differs')
    with Image.open(io.BytesIO(raw)) as im:
        require(im.mode == 'RGBA' and im.size == (1536, 1024), '007: raw canvas/mode differs')
        return im.copy()

def shading(im):
    pixels = list(im.get_flattened_data())
    return {'alpha8_pixels': sum(p[3] >= 8 for p in pixels),
            'alpha8_dark_max_rgb_lt100': sum(p[3] >= 8 and max(p[:3]) < 100 for p in pixels),
            'alpha8_bounds': im.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()}

def prepared():
    parent, base, _, _, _ = helpers()
    source(SOURCE.read_bytes())
    report_raw = (OLD / 'export-report.json').read_bytes()
    require(sha(report_raw) == OLD_REPORT_SHA, 'prior report identity differs')
    report = json.loads(report_raw)
    for name, digest in report['outputs_sha256'].items():
        require(sha((OLD / name).read_bytes()) == digest, name + ': prior output differs')
    return {'schema_version': 1, 'accepted': False, 'scope': 'Only 007 shading candidate; native review pending.',
            'frame': 7, 'source': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': SOURCE_SHA,
            'frozen_exporter': FROZEN.relative_to(ROOT).as_posix(), 'frozen_exporter_sha256': FROZEN_SHA,
            'filter_sha256': parent.FILTER_SHA, 'mask_sha256': parent.MASK_SHA,
            'pillow_version': base.PIL.__version__, 'source_window': [0, 0, 1536, 1024],
            'source_to_world_affine': [.25, 0, 696, 0, .25, 548], 'world_box': WORLD,
            'footprint': FOOTPRINT, 'prior_report_sha256': OLD_REPORT_SHA,
            'unchanged_sibling_pngs': {k: v for k, v in report['outputs_sha256'].items()
                                      if k.startswith('BMP/') and not k.endswith('/007.png')}}

def render_source(im):
    parent, base, mask, _, ground = helpers()
    # Exact quarter-scale call and complete-source crops from frozen export_v2.py.
    padded = base.resample(im, [392, 264], [.25, 0, 4, 0, .25, 4])
    audit = padded.crop((32, 32, 424, 296))
    foam = audit.crop((4, 4, 388, 260))
    outside = audit.copy()
    outside.paste((0, 0, 0, 0), (4, 4, 388, 260))
    crop_stats = parent.stats(outside)
    require(crop_stats['nonzero_pixels'] == 0, '007: footprint crops filtered foam alpha')
    audit_outside = padded.copy()
    audit_outside.paste((0, 0, 0, 0), (32, 32, 424, 296))
    audit_stats = parent.stats(audit_outside)
    require(audit_stats['nonzero_pixels'] == 0, '007: audit crops filtered raw alpha')
    retained, visibility = mask.occlude(foam, ground, WORLD[:2], parent.WORLD_BOX)
    parent.validate_foam_only(foam, retained, '007')
    outputs = {'BMP/BACKGRND.BMP/007.png': base.png(retained),
               'audit/007-unmasked.png': base.png(foam), 'audit/007-padded.png': base.png(padded),
               'audit/007-audit.png': base.png(audit)}
    return outputs, {'cropped_filtered_alpha': crop_stats, 'audit_cropped_filtered_alpha': audit_stats,
                     'source_coverage': parent.stats(foam), 'retained_coverage': parent.stats(retained),
                     'visibility_measurements': visibility, 'raw_shading': shading(im),
                     'runtime_shading': shading(retained)}

def render(recipe):
    require(recipe == prepared(), 'recipe: source/registration contract differs')
    outputs, measurements = render_source(source(SOURCE.read_bytes()))
    report = {'schema_version': 1, 'status': 'DIAGNOSTIC_EXPORTED', 'accepted': False,
              'frame': 7, 'changed_frames': [7], 'canvas': [384, 256], 'footprint': FOOTPRINT,
              'uniform_resample_count': 1, 'exporter_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(encode(recipe)), 'source_sha256': SOURCE_SHA,
              'unchanged_sibling_pngs': recipe['unchanged_sibling_pngs'], **measurements,
              'outputs_sha256': {name: sha(raw) for name, raw in outputs.items()}}
    return outputs, report

def encode(value):
    return (json.dumps(value, indent=2) + '\n').encode()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v1.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v1')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS foam-shading ' + sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            require(not args.recipe.exists(), 'recipe: refusing overwrite')
        recipe = prepared() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = encode(report)
        if not args.check:
            require(not args.output.exists(), 'output: refusing overwrite')
            args.output.mkdir(parents=True)
        for name, raw in outputs.items():
            path = args.output / name
            if args.check:
                require(path.read_bytes() == raw, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        if args.prepare:
            args.recipe.write_bytes(encode(recipe))
        print('PASS ' + sha(outputs['BMP/BACKGRND.BMP/007.png']))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
