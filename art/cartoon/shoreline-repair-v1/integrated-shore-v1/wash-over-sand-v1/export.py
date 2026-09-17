"""Unmasked incoming-wash comparison at the fixed full-source registration."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PARENT = HERE.parent / 'export.py'
PARENT_SHA = '7b9071272c7cee320fcc7c2a38167510313c8475cd4e3215bdb70752779c7fcf'
OLD = HERE.parent / 'candidates/v1'
OLD_REPORT_SHA = '9a09c9fd870f150499726b3eb5f17b2f22f391949b3f58cbce1fe3d236f638a4'
SOURCES = {
    6: ('007-raw.png', '445d15b6625168e5f154f4fa69e157d4e8e19e1811c8219b225d4989fe5680bd'),
    7: ('006-raw.png', 'd804502abace0fe36419e72152c095a80e7c082434ed9a598ae3da6f0224d34b'),
    8: ('008-raw.png', '8e08675c0a797090b2a6b0f11829e8920a320b8946b74c77331a06a04b3d2b10')}
WORLD = [696, 548, 1080, 804]
FOOTPRINT = {'id': 'cartoon-island-center-foam-v1', 'canvas': [384, 256], 'offset_hd': [-32, -90]}


def helpers():
    if hashlib.sha256(PARENT.read_bytes()).hexdigest() != PARENT_SHA:
        raise ValueError('integrated export.py: frozen helper differs')
    spec = importlib.util.spec_from_file_location('wash_integrated_parent', PARENT)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    base, _ = parent.helpers()
    return parent, base


def prepared():
    parent, base = helpers()
    raw_report = (OLD / 'export-report.json').read_bytes()
    base.require(base.sha(raw_report) == OLD_REPORT_SHA, 'parent report identity differs')
    prior = json.loads(raw_report)
    frames = []
    for old in prior['frames']:
        frame = old['frame']
        if frame not in SOURCES:
            raw = (OLD / old['path']).read_bytes()
            base.require(base.sha(raw) == old['sha256'], f'{frame:03}: retained parent PNG differs')
            frames.append({k:v for k,v in old.items() if k not in ('coverage', 'retained_coverage', 'source_coverage', 'visibility_measurements')})
            continue
        name, digest = SOURCES[frame]
        path = HERE / name
        base.require(base.sha(path.read_bytes()) == digest, f'{frame:03}: assigned raw identity differs')
        with Image.open(path) as image:
            base.require(image.mode == 'RGBA' and image.size == (1536, 1024), f'{frame:03}: assigned source canvas/mode')
        frames.append({'frame': frame, 'path': f'BMP/BACKGRND.BMP/{frame:03}.png',
                       'canvas': [384, 256], 'logical_origin_hd': [728, 638],
                       'asset_offset_hd': [-32, -90], 'world_box': WORLD, 'footprint': FOOTPRINT,
                       'source': path.relative_to(ROOT).as_posix(), 'source_sha256': digest,
                       'role': 'unmasked incoming wash, including water intentionally covering land'})
    return {'schema_version': 1, 'accepted': False,
            'scope': 'Incoming-wash center study for the three-way comparison only; unchanged masked side waves remain from the offshore/base approach.',
            'parent_exporter': PARENT.relative_to(ROOT).as_posix(), 'parent_exporter_sha256': PARENT_SHA,
            'parent_report_sha256': OLD_REPORT_SHA, 'filter_sha256': parent.FILTER_SHA,
            'pillow_version': base.PIL.__version__, 'source_to_world_affine': [.25, 0, 696, 0, .25, 548],
            'world_box': WORLD, 'footprint': FOOTPRINT,
            'policy': 'One fixed uniform resample per phase; no ground mask, alpha threshold, pose fit or phase translation. Full-source canvas preserves faint filtered alpha.',
            'assignment': '007-raw to006,006-raw to007,008-raw to008. Median central strong-white crest advances y680,678,675; local splash details and water amounts are not monotonic.',
            'frames': frames}


def render(recipe):
    parent, base = helpers()
    base.require(recipe == prepared(), 'recipe: source/phase/registration contract differs')
    outputs, rows = {}, []
    for row in recipe['frames']:
        frame = row['frame']
        if frame not in SOURCES:
            raw = (OLD / row['path']).read_bytes()
            outputs[row['path']] = raw
            rows.append({**row, 'sha256': base.sha(raw), 'byte_identical_to_parent': True})
            continue
        source = Image.open(ROOT / row['source']).convert('RGBA')
        padded = base.resample(source, [384, 256], [.25, 0, 0, 0, .25, 0])
        runtime = padded.crop((32, 32, 416, 288))
        outside = padded.copy()
        outside.paste((0, 0, 0, 0), (32, 32, 416, 288))
        clipped = parent.stats(outside)
        base.require(clipped['nonzero_pixels'] == 0, f'{frame:03}: footprint crops filtered wash alpha')
        raw = base.png(runtime)
        outputs[row['path']] = raw
        outputs[f'audit/{frame:03}-padded.png'] = base.png(padded)
        rows.append({**row, 'sha256': base.sha(raw), 'uniform_resample_count': 1,
                     'ground_mask_applied': False, 'coverage': parent.stats(runtime),
                     'raw_alpha_bounds': source.getchannel('A').getbbox(),
                     'raw_alpha8_bounds': source.getchannel('A').point(lambda a:255 if a >= 8 else 0).getbbox(),
                     'cropped_filtered_alpha': clipped})
    report = {'schema_version': 1, 'accepted': False, 'status': 'DIAGNOSTIC_EXPORTED',
              'exporter_sha256': base.sha(Path(__file__).read_bytes()), 'recipe_sha256': base.sha(base.encode(recipe)),
              'changed_frames': [6, 7, 8], 'retained_frames': [0, 3, 4, 5, 9, 10, 11],
              'scope': recipe['scope'], 'assignment': recipe['assignment'], 'policy': recipe['policy'],
              'footprint': FOOTPRINT, 'frames': rows,
              'outputs_sha256': {name: base.sha(raw) for name, raw in outputs.items()}}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v1.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v1')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS incoming-wash ' + hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    try:
        _, base = helpers()
        if args.prepare:
            base.require(not args.recipe.exists(), 'recipe: refusing overwrite')
        recipe = prepared() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if not args.check:
            base.require(not args.output.exists(), 'output: refusing overwrite')
            args.output.mkdir(parents=True)
        for name, raw in outputs.items():
            path = args.output / name
            if args.check:
                base.require(path.read_bytes() == raw, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        if args.prepare:
            args.recipe.write_bytes(base.encode(recipe))
        print('PASS ' + json.dumps({'files': len(outputs), 'footprint': FOOTPRINT}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
