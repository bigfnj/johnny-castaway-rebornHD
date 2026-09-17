"""Fixed uniform technical exports for four independent seasonal decorations.

The RGBa bicubic8x/Lanczos filter is copied from the frozen profile-walk-v1
exporter. Static-asset scales and semantic registration are explicit here;
there is no silhouette normalization, color painting or anatomical warp.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys

import PIL
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAD = 32
FILTERS = {'working_mode': 'RGBa', 'affine': 'BICUBIC', 'oversample': 8,
           'downsample': 'LANCZOS', 'output_mode': 'RGBA', 'png_compress_level': 9}
REFERENCE_SHA = '750dad7500e029214e2576f34c86fec4eeaf4b51bac3427272e47d06cce8fc1b'
CONFIG = {
    0: {'scale': .162, 'canvas': [80, 68], 'raw_anchor': [631.5, 855], 'target_anchor': [39, 67.75],
        'basis': 'Pumpkin body horizontal center at original visible-canvas midpoint39HD; raw shadow bottom855 maps to original bottom68HD minus0.25 filter margin.'},
    1: {'scale': .19, 'canvas': [240, 94], 'raw_anchor': [1239.5, 774], 'target_anchor': [205, 93.75],
        'basis': 'Lowest front clover ground patch: raw final alpha8 row x[1233,1246) midpoint1239.5; original row46 shadow x[99,106) midpoint102.5 doubled. Bottom94HD minus0.25 margin.'},
    2: {'scale': .163, 'canvas': [112, 130], 'raw_anchor': [626.5, 1046], 'target_anchor': [49.25, 129.75],
        'basis': 'Star/trunk axis: raw alpha128 star-tip x[625,628) midpoint626.5; original top pixel x24 midpoint24.5 doubled49HD, plus0.25 margin to retain left branch. Shadow bottom1046 maps to130HD minus0.25 margin.'},
    3: {'scale': .23, 'canvas': [304, 94], 'raw_anchor': [770, 322], 'target_anchor': [150, .08],
        'basis': 'Hanging-banner span center raw770 maps to original visible span midpoint75 doubled150HD. Highest hanging endpoint alpha8 top322 maps to0.08HD; source height408 at0.23 occupies93.84HD. Ends retain generated asymmetry; no separate endpoint warp.'},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def encode(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf-8')


def png(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG', compress_level=9)
    return stream.getvalue()


def expected_affine(frame):
    c = CONFIG[frame]
    s = c['scale']
    return [s, 0, c['target_anchor'][0] - c['raw_anchor'][0] * s,
            0, s, c['target_anchor'][1] - c['raw_anchor'][1] * s]


def prepare():
    require(sha((HERE / 'reference/source.json').read_bytes()) == REFERENCE_SHA, 'reference/source.json: identity differs')
    rows = []
    for frame, config in CONFIG.items():
        name = f'raw/{frame:03}-v1.png'
        data = (HERE / name).read_bytes()
        with Image.open(io.BytesIO(data)) as im:
            require(im.mode == 'RGBA', f'{frame:03}: source mode differs')
            canvas = list(im.size)
        rows.append({'frame': frame, 'path': f'BMP/HOLIDAY.BMP/{frame:03}.png',
                     'source': name, 'source_sha256': sha(data), 'generated_canvas': canvas,
                     'runtime_canvas': config['canvas'], 'scale': config['scale'],
                     'raw_anchor': config['raw_anchor'], 'target_anchor': config['target_anchor'],
                     'anchor_basis': config['basis'], 'affine_forward': expected_affine(frame)})
    return {'schema_version': 1, 'accepted': False, 'scope': 'Technical candidates pending human scene review.',
            'normalization': 'none', 'pillow_version': PIL.__version__, 'resampling': FILTERS,
            'padding_hd': PAD, 'reference_sha256': REFERENCE_SHA,
            'filter_ancestor': 'art/cartoon/walk-pilot/profile-walk-v1/export.py',
            'filter_ancestor_sha256': sha((HERE.parent / 'walk-pilot/profile-walk-v1/export.py').read_bytes()),
            'frames': rows}


def resample(source, canvas, affine):
    s, _, tx, _, _, ty = affine
    size = (canvas[0] + PAD * 2, canvas[1] + PAD * 2)
    high = source.convert('RGBa').transform((size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
        (1 / (s * 8), 0, -(tx + PAD) / s, 0, 1 / (s * 8), -(ty + PAD) / s),
        resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
    return high.resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def render(recipe):
    require(recipe['schema_version'] == 1 and recipe['accepted'] is False and recipe['normalization'] == 'none'
            and recipe['pillow_version'] == PIL.__version__ and recipe['resampling'] == FILTERS
            and recipe['padding_hd'] == PAD, 'recipe: render contract differs')
    require(recipe['reference_sha256'] == REFERENCE_SHA == sha((HERE / 'reference/source.json').read_bytes()), 'recipe: reference identity differs')
    require([r['frame'] for r in recipe['frames']] == [0, 1, 2, 3], 'recipe: frame coverage differs')
    outputs, rows, visuals = {}, [], []
    for row in recipe['frames']:
        frame, label = row['frame'], f"{row['frame']:03}"
        config = CONFIG[frame]
        require(row['source'] == f'raw/{label}-v1.png' and row['path'] == f'BMP/HOLIDAY.BMP/{label}.png', label + ': slot/source identity differs')
        data = (HERE / row['source']).read_bytes()
        require(sha(data) == row['source_sha256'], label + ': source hash differs')
        require(row['runtime_canvas'] == config['canvas'], label + ': runtime canvas differs')
        require(row['scale'] == config['scale'] and row['affine_forward'] == expected_affine(frame) and row['raw_anchor'] == config['raw_anchor'] and row['target_anchor'] == config['target_anchor'], label + ': fixed uniform registration differs')
        with Image.open(io.BytesIO(data)) as im:
            require(im.mode == 'RGBA' and list(im.size) == row['generated_canvas'], label + ': source canvas/mode differs')
            source = im.copy()
        a = source.getchannel('A')
        bounds = a.point(lambda v: 255 if v >= 8 else 0).getbbox()
        s, _, tx, _, _, ty = row['affine_forward']
        centers = [(bounds[0] + .5) * s + tx, (bounds[1] + .5) * s + ty,
                   (bounds[2] - .5) * s + tx, (bounds[3] - .5) * s + ty]
        width, height = config['canvas']
        require(centers[0] >= 0 and centers[1] >= 0 and centers[2] < width and centers[3] < height, label + ': meaningful source alpha overhang')
        padded = resample(source, config['canvas'], row['affine_forward'])
        alpha = padded.getchannel('A')
        outside = alpha.copy()
        outside.paste(0, (PAD, PAD, PAD + width, PAD + height))
        outside_hist = outside.histogram()
        clipped_max = outside.getextrema()[1]
        filtered_bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
        fixed = padded.crop((PAD, PAD, PAD + width, PAD + height))
        outputs[row['path']] = png(fixed)
        outputs[f'padded/{label}.png'] = png(padded)
        visuals.append((frame, fixed))
        rows.append({'frame': frame, 'path': row['path'], 'source_sha256': sha(data),
                     'runtime_canvas': config['canvas'], 'candidate_png_sha256': sha(outputs[row['path']]),
                     'affine_forward': row['affine_forward'], 'source_alpha_extrema': list(a.getextrema()),
                     'source_alpha8_bounds': list(bounds), 'alpha8_source_centers_hd': centers,
                     'filtered_alpha8_bounds_hd': [filtered_bounds[0] - PAD, filtered_bounds[1] - PAD,
                                                   filtered_bounds[2] - PAD, filtered_bounds[3] - PAD],
                     'outside_runtime_max_alpha': clipped_max,
                     'outside_runtime_alpha8_pixels': sum(outside_hist[8:]),
                     'outside_runtime_nonzero_pixels': sum(outside_hist[1:]),
                     'source_corners_alpha': [a.getpixel(point) for point in ((0, 0), (source.width - 1, 0), (0, source.height - 1), (source.width - 1, source.height - 1))]})
    sheet = Image.new('RGB', (1536, 1264), (226, 227, 218))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 12), 'HOLIDAY technical candidates: original geometry vs Cartoon | no scene approval yet', fill='black')
    for frame, candidate in visuals:
        original = Image.open(HERE / f'reference/{frame:03}-original-native.png').convert('RGBA')
        y = 64 + frame * 300
        for column, image, factor, label in ((0, original, 4, 'Original x4'), (1, candidate, 2, 'Cartoon runtime x2')):
            x = 16 + column * 768
            draw.text((x, y), f'{frame:03} {label}', fill='black')
            shown = image.resize((image.width * factor, image.height * factor), Image.Resampling.NEAREST)
            sheet.paste(shown, (x, y + 24), shown)
    outputs['comparison-enlarged.png'] = png(sheet)
    strip = Image.new('RGB', (832, 202), (226, 227, 218))
    draw = ImageDraw.Draw(strip)
    x = 12
    for frame, image in visuals:
        draw.text((x, 10), f'{frame:03} runtime 1:1', fill='black')
        strip.paste(image, (x, 36), image)
        x += image.width + 16
    outputs['comparison-runtime.png'] = png(strip)
    report = {'schema_version': 1, 'accepted': False, 'scope': 'Technical export; human native-scene acceptance pending.',
              'exporter_sha256': sha(Path(__file__).read_bytes()), 'pillow_version': PIL.__version__,
              'recipe_sha256': sha(encode(recipe)), 'frames': rows,
              'filter_limit': 'Padded outputs retain low-alpha resampling fringe. Alpha>=8 source centers fit; report lists actual filtered alpha outside each runtime crop.',
              'outputs_sha256': {name: sha(data) for name, data in outputs.items()}}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v1')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS seasonal-export ' + sha(Path(__file__).read_bytes()))
    try:
        if args.prepare:
            require(not args.recipe.exists(), 'recipe: refusing to overwrite')
            recipe = prepare()
        else:
            recipe = json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = encode(report)
        if not args.check:
            require(not args.output.exists(), 'output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name, data in outputs.items():
            path = args.output / name
            if args.check:
                require(path.read_bytes() == data, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        if args.prepare:
            args.recipe.write_bytes(encode(recipe))
        print('PASS seasonal-export ' + json.dumps([{'frame': r['frame'], 'outside_max': r['outside_runtime_max_alpha'], 'outside_alpha8': r['outside_runtime_alpha8_pixels']} for r in report['frames']]))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
