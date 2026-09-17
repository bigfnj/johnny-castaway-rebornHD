"""Diagnostic rotting-pumpkin adapter; reuse the frozen v3 renderer/filter."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
PRIOR_SHA = '261923eec27a9919a48384095246cb3fc122251ea27637bd50805ceb1c9ad024'
RAW_SHA = '7c1abdf9245e2b7714891225e5c0180c7d7b8acba0a6ff25e75d4145998310fa'
GENERATION_SHA = '9372e1b9b8afdde311f6a06a7e749e8b8c633b2e8dff5aadff3fec3a1b213938'
if hashlib.sha256((HERE / 'export_v3.py').read_bytes()).hexdigest() != PRIOR_SHA:
    raise ValueError('export_v3.py: frozen adapter differs')
spec = importlib.util.spec_from_file_location('seasonal_v3_for_v4', HERE / 'export_v3.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
base = prior.base


def selected_recipe():
    recipe = prior.selected_recipe()
    base.require(base.sha((HERE / 'raw/000-v3.png').read_bytes()) == RAW_SHA, '000: v4 source differs')
    base.require(base.sha((HERE / 'generation-pumpkin-v3.json').read_bytes()) == GENERATION_SHA, '000: v4 generation record differs')
    recipe['scope'] = 'Slightly rotting pumpkin appearance pending; same placement is diagnostic while the Cartoon island footprint is investigated. No compatibility or production approval.'
    recipe['adapter'].update(previous_adapter_sha256=PRIOR_SHA, changed_frames=[0],
                             generation_record='generation-pumpkin-v3.json', generation_record_sha256=GENERATION_SHA,
                             appearance_status='pending for decay variant; earlier face direction approved')
    recipe['frames'][0].update(source='raw/000-v3.png', source_sha256=RAW_SHA)
    return recipe


def render(recipe):
    base.require(recipe == selected_recipe(), 'recipe-v4: selected inputs or placement differ')
    # The isolated imported adapter supplies its tested fit/filter/unchanged-slot
    # checks. Substitute only its recipe provider for this already validated v4
    # call; no historical file or shared module is changed.
    saved = prior.selected_recipe
    try:
        prior.selected_recipe = lambda: recipe
        outputs, report = prior.render(recipe)
    finally:
        prior.selected_recipe = saved
    del outputs['pumpkin-v2-v3-comparison.png']
    sheet = Image.new('RGB', (680, 324), (226, 227, 218))
    draw = ImageDraw.Draw(sheet)
    for x, title, folder in ((12, 'Approved face before decay', 'v3'), (348, 'Slightly rotting draft / diagnostic placement', None)):
        image = Image.open(HERE / f'candidates/{folder}/BMP/HOLIDAY.BMP/000.png').convert('RGBA') if folder else Image.open(__import__('io').BytesIO(outputs['BMP/HOLIDAY.BMP/000.png'])).convert('RGBA')
        draw.text((x, 12), title, fill='black')
        shown = image.resize((320, 272), Image.Resampling.NEAREST)
        sheet.paste(shown, (x, 36), shown)
    outputs['pumpkin-v3-v4-comparison.png'] = base.png(sheet)
    alpha = Image.open(HERE / 'raw/000-v3.png').getchannel('A')
    report['exporter_sha256'] = base.sha(Path(__file__).read_bytes())
    report['reused_adapter_sha256'] = PRIOR_SHA
    report['frames'][0].update(source_sha256=RAW_SHA, source_alpha_extrema=list(alpha.getextrema()),
                              source_corners_alpha=[alpha.getpixel(p) for p in ((0,0),(1253,0),(0,1253),(1253,1253))])
    report['outputs_sha256'] = {name: base.sha(data) for name, data in outputs.items()}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v4.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v4')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS seasonal-v4 ' + base.sha(Path(__file__).read_bytes()))
    try:
        recipe = selected_recipe() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if args.prepare:
            base.require(not args.recipe.exists(), 'recipe-v4: refusing to overwrite')
        if not args.check:
            base.require(not args.output.exists(), 'v4 output: refusing to overwrite')
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
        print('PASS seasonal-v4 ' + report['frames'][0]['candidate_png_sha256'])
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
