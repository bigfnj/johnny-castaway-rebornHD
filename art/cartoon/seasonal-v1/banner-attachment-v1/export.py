"""Export a banner attachment trial with the exact frozen V5 registration.

The existing premultiplied filter is imported by hash. Preview-only mode retains
the padded image and an explicitly diagnostic crop when meaningful pixels fail
the established fit rule; it never creates a runtime asset in that case.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
BASE_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
V5_SHA = '5e60af35fd517663b4c0f3c4c26da97d61f81ccad807fadc5bb858c6ed3c848f'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_base():
    assert sha((PARENT / 'export.py').read_bytes()) == BASE_SHA, 'frozen export.py identity'
    assert sha((PARENT / 'recipe-v5.json').read_bytes()) == V5_SHA, 'frozen V5 recipe identity'
    spec = importlib.util.spec_from_file_location('banner_frozen_filter', PARENT / 'export.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    return base


def prepare(source):
    base = load_base()
    prior = json.loads((PARENT / 'recipe-v5.json').read_bytes())
    row = copy.deepcopy(prior['frames'][3])
    with Image.open(source) as image:
        base.require(image.mode == 'RGBA', '003: source mode differs')
        row.update(source=source.relative_to(HERE).as_posix(),
                   source_sha256=sha(source.read_bytes()), generated_canvas=list(image.size))
    return {'schema_version': 1, 'accepted': False,
            'scope': 'Banner attachment trial; fixed V5 geometry, pending fit and native scene review.',
            'pillow_version': PIL.__version__, 'normalization': 'none',
            'resampling': base.FILTERS, 'padding_hd': base.PAD,
            'reused_exporter_sha256': BASE_SHA, 'parent_recipe_sha256': V5_SHA,
            'frames': [row]}


def render(recipe, preview_only):
    base = load_base()
    row = recipe['frames'][0]
    source_path = HERE / row['source']
    base.require(recipe == prepare(source_path), '003: source or fixed V5 recipe differs')
    with Image.open(source_path) as image:
        source = image.copy()
    alpha = source.getchannel('A')
    box = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
    s, _, tx, _, _, ty = row['affine_forward']
    centers = [(box[0]+.5)*s+tx, (box[1]+.5)*s+ty,
               (box[2]-.5)*s+tx, (box[3]-.5)*s+ty]
    w, h = row['runtime_canvas']
    padded = base.resample(source, [w, h], row['affine_forward'])
    outside = padded.getchannel('A')
    outside.paste(0, (base.PAD, base.PAD, base.PAD+w, base.PAD+h))
    fits = (0 <= centers[0] < centers[2] < w and 0 <= centers[1] < centers[3] < h
            and outside.getextrema()[1] < 8)
    if not preview_only:
        base.require(fits, '003: meaningful source or filtered alpha overhang')
    crop = padded.crop((base.PAD, base.PAD, base.PAD+w, base.PAD+h))
    output_name = row['path'] if fits else 'diagnostic-crop/003.png'
    outputs = {'padded/003.png': base.png(padded), output_name: base.png(crop)}
    prior = json.loads((PARENT / 'recipe-v5.json').read_bytes())
    unchanged = {}
    for old in prior['frames'][:3]:
        data = (PARENT / 'candidates/v5' / old['path']).read_bytes()
        unchanged[old['path']] = sha(data)
        if fits:
            outputs[old['path']] = data
    edges = {'top': (0, 0, padded.width, base.PAD),
             'bottom': (0, base.PAD+h, padded.width, padded.height),
             'left': (0, base.PAD, base.PAD, base.PAD+h),
             'right': (base.PAD+w, base.PAD, padded.width, base.PAD+h)}
    edge_stats = {}
    for edge, bounds in edges.items():
        a = padded.getchannel('A').crop(bounds)
        edge_stats[edge] = {'nonzero_pixels': sum(a.histogram()[1:]),
                            'alpha8_pixels': sum(a.histogram()[8:]),
                            'maximum_alpha': a.getextrema()[1]}
    filtered = padded.getchannel('A').point(lambda v: 255 if v >= 8 else 0).getbbox()
    report = {'schema_version': 1, 'accepted': False,
              'status': 'FIT_PASS_PENDING_NATIVE_REVIEW' if fits else 'REJECTED_MEANINGFUL_OVERHANG',
              'runtime_ready': fits, 'preview_only': preview_only,
              'exporter_sha256': sha(Path(__file__).read_bytes()),
              'reused_exporter_sha256': BASE_SHA, 'parent_recipe_sha256': V5_SHA,
              'recipe_sha256': sha(base.encode(recipe)), 'pillow_version': PIL.__version__,
              'frame': 3, 'source_sha256': row['source_sha256'],
              'runtime_canvas': [w, h], 'affine_forward': row['affine_forward'],
              'source_alpha8_bounds': list(box), 'alpha8_source_centers_hd': centers,
              'filtered_alpha8_bounds_hd': [v-base.PAD for v in filtered],
              'outside_runtime_max_alpha': outside.getextrema()[1],
              'outside_runtime_alpha8_pixels': sum(outside.histogram()[8:]),
              'outside_runtime_nonzero_pixels': sum(outside.histogram()[1:]),
              'outside_by_edge': edge_stats, 'unchanged_v5_props_sha256': unchanged,
              'outputs_sha256': {name: sha(data) for name, data in outputs.items()}}
    return outputs, report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--preview-only', action='store_true')
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    print('WITNESS banner-export ' + sha(Path(__file__).read_bytes()))
    try:
        base = load_base()
        recipe = prepare(a.source.resolve()) if a.source else json.loads(a.recipe.read_bytes())
        outputs, report = render(recipe, a.preview_only)
        outputs['export-report.json'] = base.encode(report)
        if a.source:
            base.require(not a.recipe.exists(), 'recipe: refusing to overwrite')
        if not a.check:
            base.require(not a.output.exists(), 'output: refusing to overwrite')
        for name, data in outputs.items():
            target = a.output / name
            if a.check:
                base.require(target.read_bytes() == data, name + ': reproduced bytes differ')
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        if a.source:
            a.recipe.write_bytes(base.encode(recipe))
        print('PASS banner-export ' + report['status'])
        return 0
    except (AssertionError, ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
