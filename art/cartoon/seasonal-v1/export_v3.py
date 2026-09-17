"""Thin pumpkin-source adapter over the frozen seasonal v2 filter and placement."""
import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BASE_SHA = '50aa0da6717af65bfe51593ac29da28ccb93d571d49ce0809031b0c89fb788e7'
RECIPE_SHA = '68e8559a79a5abbf765d8cd6c8d9b7b1d45ff921a264e3aa174fed316ab57d38'
RAW_SHA = 'a6c47a0139e88634f9a28419879329a4931fa91b692811009614ad2a0ee0683d'
APPROVAL_SHA = '5b1cc06251ec696800e5b5067b30d42ce3fe1f273a1468f5382d16b3e7ee0f04'
spec = importlib.util.spec_from_file_location('seasonal_v2', HERE / 'export_v2.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def selected_recipe():
    base.require(base.sha((HERE / 'export_v2.py').read_bytes()) == BASE_SHA, 'export_v2.py: frozen helper differs')
    original = (HERE / 'recipe-v2.json').read_bytes()
    base.require(base.sha(original) == RECIPE_SHA, 'recipe-v2.json: frozen recipe differs')
    base.require(base.sha((HERE / 'raw/000-v2.png').read_bytes()) == RAW_SHA, '000: selected source differs')
    base.require(base.sha((HERE / 'generation-pumpkin-v2.json').read_bytes()) == APPROVAL_SHA, '000: appearance record differs')
    recipe = json.loads(original)
    recipe['scope'] = 'Pumpkin source appearance approved separately; technical batch pending composed-scene and production approval.'
    recipe['adapter'] = {'previous_recipe_sha256': RECIPE_SHA, 'reused_exporter_sha256': BASE_SHA,
                         'changed_frames': [0], 'appearance_record': 'generation-pumpkin-v2.json',
                         'appearance_record_sha256': APPROVAL_SHA}
    recipe['frames'][0].update(source='raw/000-v2.png', source_sha256=RAW_SHA)
    return recipe


def render(recipe):
    base.require(recipe == selected_recipe(), 'recipe-v3: selected inputs or placement differ')
    old_recipe = json.loads((HERE / 'recipe-v2.json').read_bytes())
    old_outputs, old_report = base.render(old_recipe)
    outputs = {}
    for row in old_recipe['frames']:
        name = row['path']
        saved = (HERE / 'candidates/v2' / name).read_bytes()
        base.require(saved == old_outputs[name], name + ': frozen v2 candidate differs')
        outputs[name] = saved
    row = recipe['frames'][0]
    source = Image.open(HERE / row['source']).convert('RGBA')
    base.require(list(source.size) == row['generated_canvas'], '000: source canvas differs')
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
    sheet = Image.new('RGB', (680, 324), (226, 227, 218))
    draw = ImageDraw.Draw(sheet)
    for x, title, image in ((12, 'Earlier face / same placement', Image.open(io.BytesIO(old_outputs[row['path']])).convert('RGBA')),
                            (348, 'Approved revised face / same placement', fixed)):
        draw.text((x, 12), title, fill='black')
        shown = image.resize((width*4, height*4), Image.Resampling.NEAREST)
        sheet.paste(shown, (x, 36), shown)
    outputs['pumpkin-v2-v3-comparison.png'] = base.png(sheet)
    report = {'schema_version': 1, 'accepted': False, 'scope': recipe['scope'],
              'exporter_sha256': base.sha(Path(__file__).read_bytes()), 'reused_exporter_sha256': BASE_SHA,
              'recipe_sha256': base.sha(base.encode(recipe)), 'frames': copy.deepcopy(old_report['frames'])}
    report['frames'][0] = dict(report['frames'][0], source_sha256=RAW_SHA,
                              candidate_png_sha256=base.sha(outputs[row['path']]),
                              source_alpha8_bounds=list(bounds), alpha8_source_centers_hd=centers,
                              filtered_alpha8_bounds_hd=[v-base.PAD for v in padded.getchannel('A').point(lambda v:255 if v>=8 else 0).getbbox()],
                              outside_runtime_max_alpha=maximum, outside_runtime_alpha8_pixels=0,
                              outside_runtime_nonzero_pixels=sum(outside.histogram()[1:]))
    report['unchanged_v2_frames'] = [1, 2, 3]
    report['outputs_sha256'] = {name: base.sha(data) for name, data in outputs.items()}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v3.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v3')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS seasonal-v3 ' + base.sha(Path(__file__).read_bytes()))
    try:
        recipe = selected_recipe() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if args.prepare:
            base.require(not args.recipe.exists(), 'recipe-v3: refusing to overwrite')
        if not args.check:
            base.require(not args.output.exists(), 'v3 output: refusing to overwrite')
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
        print('PASS seasonal-v3 ' + report['frames'][0]['candidate_png_sha256'])
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
