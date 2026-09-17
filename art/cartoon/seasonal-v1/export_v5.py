"""Restore V1 seasonal registration with the approved slightly rotting pumpkin.

Reuse the frozen original exporter directly. V2-V4 helpers are not dependencies.
Only000 is resampled from a newer raw image;001-003 retain exact V1 PNG bytes.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
BASE_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
RECIPE_SHA = '13a3363b72338c07bdb5d75d242a98a547bf688cf5daa676cc0a0ce0f3761d83'
RAW_SHA = '7c1abdf9245e2b7714891225e5c0180c7d7b8acba0a6ff25e75d4145998310fa'
APPROVAL_SHA = '37034347373c6456adcd9a9f7a95003fff0568696718b2909d774ce714435db8'
if hashlib.sha256((HERE / 'export.py').read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('export.py: frozen V1 exporter differs')
spec = importlib.util.spec_from_file_location('seasonal_v1_for_v5', HERE / 'export.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def selected_recipe():
    original = (HERE / 'recipe-v1.json').read_bytes()
    base.require(base.sha(original) == RECIPE_SHA, 'recipe-v1.json: frozen recipe differs')
    base.require(base.sha((HERE / 'raw/000-v3.png').read_bytes()) == RAW_SHA, '000: selected decay source differs')
    base.require(base.sha((HERE / 'pumpkin-appearance-v4.json').read_bytes()) == APPROVAL_SHA, '000: appearance approval differs')
    recipe = json.loads(original)
    recipe['scope'] = 'Approved pumpkin appearance at restored V1 registration; exact V1 other props. Enlarged-island/tide compatibility and composed-scene approval remain pending.'
    recipe['adapter'] = {'original_recipe': 'recipe-v1.json', 'original_recipe_sha256': RECIPE_SHA,
                         'reused_exporter': 'export.py', 'reused_exporter_sha256': BASE_SHA,
                         'changed_from_v1_frames': [0], 'exact_v1_frames': [1, 2, 3],
                         'appearance_record': 'pumpkin-appearance-v4.json', 'appearance_record_sha256': APPROVAL_SHA}
    recipe['frames'][0].update(source='raw/000-v3.png', source_sha256=RAW_SHA)
    return recipe


def render(recipe):
    base.require(recipe == selected_recipe(), 'recipe-v5: selected inputs or V1 registration differ')
    original_outputs, original_report = base.render(json.loads((HERE / 'recipe-v1.json').read_bytes()))
    outputs = {}
    for row in recipe['frames']:
        saved = (HERE / 'candidates/v1' / row['path']).read_bytes()
        base.require(saved == original_outputs[row['path']], row['path'] + ': frozen V1 candidate differs')
        outputs[row['path']] = saved
    row = recipe['frames'][0]
    with Image.open(HERE / row['source']) as image:
        base.require(image.mode == 'RGBA' and list(image.size) == row['generated_canvas'], '000: source canvas/mode differs')
        source = image.copy()
    alpha = source.getchannel('A')
    bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
    s, _, tx, _, _, ty = row['affine_forward']
    centers = [(bounds[0]+.5)*s+tx, (bounds[1]+.5)*s+ty, (bounds[2]-.5)*s+tx, (bounds[3]-.5)*s+ty]
    width, height = row['runtime_canvas']
    base.require(0 <= centers[0] < centers[2] < width and 0 <= centers[1] < centers[3] < height,
                 '000: meaningful source alpha overhang')
    padded = base.resample(source, row['runtime_canvas'], row['affine_forward'])
    outside = padded.getchannel('A')
    outside.paste(0, (base.PAD, base.PAD, base.PAD+width, base.PAD+height))
    maximum = outside.getextrema()[1]
    base.require(maximum < 8, '000: meaningful filtered alpha overhang')
    fixed = padded.crop((base.PAD, base.PAD, base.PAD+width, base.PAD+height))
    outputs[row['path']] = base.png(fixed)
    outputs['padded/000.png'] = base.png(padded)
    rows = copy.deepcopy(original_report['frames'])
    rows[0].update(source_sha256=RAW_SHA, candidate_png_sha256=base.sha(outputs[row['path']]),
                   source_alpha_extrema=list(alpha.getextrema()), source_alpha8_bounds=list(bounds),
                   alpha8_source_centers_hd=centers,
                   filtered_alpha8_bounds_hd=[v-base.PAD for v in padded.getchannel('A').point(lambda v:255 if v>=8 else 0).getbbox()],
                   outside_runtime_max_alpha=maximum, outside_runtime_alpha8_pixels=0,
                   outside_runtime_nonzero_pixels=sum(outside.histogram()[1:]),
                   source_corners_alpha=[alpha.getpixel(p) for p in ((0,0),(source.width-1,0),(0,source.height-1),(source.width-1,source.height-1))])
    report = {'schema_version': 1, 'accepted': False, 'scope': recipe['scope'],
              'exporter_sha256': base.sha(Path(__file__).read_bytes()), 'reused_exporter_sha256': BASE_SHA,
              'pillow_version': recipe['pillow_version'], 'recipe_sha256': base.sha(base.encode(recipe)),
              'frames': rows, 'unchanged_v1_frames': [1,2,3],
              'filter_limit': 'Alpha>=8 source centers and filtered pixels fit. Padded output retains resampling fringe; runtime crop discards the explicitly reported low-alpha fringe, not a promise to retain every faint source pixel.',
              'outputs_sha256': {name: base.sha(data) for name, data in outputs.items()}}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v5.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v5')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS seasonal-v5 ' + base.sha(Path(__file__).read_bytes()))
    try:
        recipe = selected_recipe() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if args.prepare:
            base.require(not args.recipe.exists(), 'recipe-v5: refusing to overwrite')
        if not args.check:
            base.require(not args.output.exists(), 'v5 output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name, data in outputs.items():
            path = args.output / name
            if args.check:
                base.require(path.read_bytes() == data, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if args.prepare:
            args.recipe.write_bytes(base.encode(recipe))
        print('PASS seasonal-v5 ' + report['frames'][0]['candidate_png_sha256'])
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
