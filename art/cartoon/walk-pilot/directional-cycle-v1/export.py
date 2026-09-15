#!/usr/bin/env python3
"""Recreate the six recorded directional review PNGs in a new output directory."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory for this partial, pending-review export')
    args = parser.parse_args()
    recipe = json.loads((HERE / 'recipe.json').read_text(encoding='utf-8'))
    output = args.output.resolve()
    if output.exists():
        parser.error(f'refusing to overwrite existing output: {output}')
    expected_version = recipe['resampling']['pillow_version']
    if PIL.__version__ != expected_version:
        parser.error(f'byte-exact export requires Pillow {expected_version}; found {PIL.__version__}')
    if recipe['scale_exact'] != {'numerator': 1, 'denominator': 10} or recipe['normalization'] != 'none':
        parser.error('recipe.json: this record requires common scale1/10 with no normalization')
    expected_paths = [f'BMP/JOHNWALK.BMP/{n:03}.png' for n in range(24, 30)]
    if ([f['path'] for f in recipe['frames']] != expected_paths or
            recipe['required_assets'] != expected_paths):
        parser.error('recipe.json: expected exactly the six recorded024-029 paths')
    bundle = HERE / recipe['source_bundle']['file']
    if digest(bundle.read_bytes()) != recipe['source_bundle']['sha256']:
        parser.error('source-images.zip: source bundle hash mismatch')
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(recipe['generated_images']):
            parser.error('source-images.zip: unexpected or duplicate entries')
        sources = {name: archive.read(name) for name in names}
    for name, data in sources.items():
        if digest(data) != recipe['generated_images'][name]['sha256']:
            parser.error(f'{name}: generated source hash mismatch')
    with zipfile.ZipFile(REPO / recipe['original_archive']['file']) as archive:
        for reference in recipe['original_references'].values():
            if digest(archive.read(reference['member'])) != reference['sha256']:
                parser.error(f"{reference['member']}: original pose reference hash mismatch")

    # Every render and byte comparison finishes before the first output is written.
    rendered = []
    for frame in recipe['frames']:
        name = frame['generated_image']
        source = Image.open(io.BytesIO(sources[name]))
        if source.mode != 'RGBA' or list(source.size) != frame['generated_canvas']:
            parser.error(f'{name}: source RGBA dimensions differ from recipe')
        if digest(sources[name]) != frame['source_sha256']:
            parser.error(f'{name}: frame source hash mismatch')
        scale, xy, tx, yx, scale_y, ty = frame['affine_forward']
        if xy != 0 or yx != 0 or scale != 0.1 or scale_y != 0.1:
            parser.error(f"{frame['path']}: transform differs from the declared common uniform scale")
        cap, target = frame['cap_raw'], frame['cap_target_hd']
        if not all(math.isclose(value, expected, abs_tol=1e-12)
                   for value, expected in zip((cap[0]*scale+tx, cap[1]*scale+ty), target)):
            parser.error(f"{frame['path']}: cap registration differs from recipe")
        original = recipe['original_references'][str(frame['frame'])]
        if frame['runtime_canvas'] != original['canvas']:
            parser.error(f"{frame['path']}: runtime canvas differs from the original")
        width, height = frame['runtime_canvas']
        high = source.convert('RGBa').transform(
            (width*8, height*8), Image.Transform.AFFINE,
            (1/(scale*8), 0, -tx/scale, 0, 1/(scale*8), -ty/scale),
            resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        image = high.resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG', compress_level=9)
        data = buffer.getvalue()
        if digest(data) != frame['candidate_png_sha256']:
            parser.error(f"{frame['path']}: export differs from recorded candidate PNG bytes")
        rendered.append((frame['path'], data))
    for name, data in rendered:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({'status': 'all six recorded candidate PNG hashes matched',
                      'frames': len(rendered), 'output': str(output), 'coverage': 'partial',
                      'human_motion_acceptance': False, 'production_acceptance': False}, sort_keys=True))


if __name__ == '__main__':
    main()
