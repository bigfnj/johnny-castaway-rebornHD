#!/usr/bin/env python3
"""Reproduce the six side-wave candidate PNGs in a new output directory."""
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
EXPECTED_PATHS = [f'BMP/BACKGRND.BMP/{n:03}.png' for n in (3, 4, 5, 9, 10, 11)]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory for the recorded exports')
    args = parser.parse_args()
    print(f'EXPORT_WITNESS source={digest(Path(__file__).read_bytes())} pillow={PIL.__version__}', flush=True)
    recipe = json.loads((HERE / 'recipe.json').read_text(encoding='utf-8'))
    output = args.output.resolve()
    if output.exists():
        parser.error(f'refusing to overwrite existing output: {output}')
    if ([a['path'] for a in recipe['assets']] != EXPECTED_PATHS or
            recipe['required_assets'] != EXPECTED_PATHS):
        parser.error('recipe.json: expected exactly the six recorded side-wave asset paths')
    if recipe['normalization'] != 'none':
        parser.error('recipe.json: side-wave export requires no normalization')
    bundle = HERE / recipe['source_bundle']['file']
    if digest(bundle.read_bytes()) != recipe['source_bundle']['sha256']:
        parser.error('source-images.zip: source bundle hash mismatch')
    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(recipe['generated_images']):
            parser.error('source-images.zip: unexpected, missing or duplicate entries')
        sources = {name: archive.read(name) for name in names}
    for name, data in sources.items():
        if digest(data) != recipe['generated_images'][name]['sha256']:
            parser.error(f'{name}: generated source hash mismatch')
    with zipfile.ZipFile(REPO / recipe['original_archive']['file']) as archive:
        for reference in recipe['original_references'].values():
            if digest(archive.read(reference['member'])) != reference['sha256']:
                parser.error(f"{reference['member']}: original geometry reference hash mismatch")

    # Validate and render every asset before creating the output directory.
    rendered = []
    for asset in recipe['assets']:
        name = asset['generated_image']
        source = Image.open(io.BytesIO(sources[name]))
        if source.mode != 'RGBA' or list(source.size) != asset['generated_canvas']:
            parser.error(f'{name}: source RGBA dimensions differ from recipe')
        if digest(sources[name]) != asset['source_sha256']:
            parser.error(f'{name}: asset source hash mismatch')
        scale, xy, tx, yx, scale_y, ty = asset['affine_forward']
        declared = asset['scale_exact']['numerator'] / asset['scale_exact']['denominator']
        family_scale = .097 if Path(asset['path']).stem in ('003', '004', '005') else .09
        if xy != 0 or yx != 0 or scale != family_scale or scale != declared or scale_y != scale:
            parser.error(f"{asset['path']}: transform differs from the declared uniform scale")
        anchor, target = asset['landmark_raw'], asset['landmark_target_local_hd']
        if not all(math.isclose(value, expected, rel_tol=0, abs_tol=1e-12)
                   for value, expected in zip((anchor[0]*scale+tx, anchor[1]*scale+ty), target)):
            parser.error(f"{asset['path']}: semantic registration differs from recipe")
        original = recipe['original_references'][Path(asset['path']).stem]
        if asset['runtime_canvas'] != original['canvas']:
            parser.error(f"{asset['path']}: runtime canvas differs from the original")
        width, height = asset['runtime_canvas']
        high = source.convert('RGBa').transform(
            (width*8, height*8), Image.Transform.AFFINE,
            (1/(scale*8), 0, -tx/scale, 0, 1/(scale*8), -ty/scale),
            resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        image = high.resize((width, height), Image.Resampling.LANCZOS).convert('RGBA')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG', compress_level=9)
        data = buffer.getvalue()
        if digest(data) != asset['candidate_png_sha256']:
            parser.error(f"{asset['path']}: export differs from recorded candidate PNG bytes")
        rendered.append((asset['path'], data))
    for name, data in rendered:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({'status': 'all six recorded candidate PNG hashes matched',
                      'assets': len(rendered), 'output': str(output), 'pillow_version': PIL.__version__,
                      'coverage': 'partial', 'human_runtime_acceptance': False,
                      'production_acceptance': False}, sort_keys=True))


if __name__ == '__main__':
    main()
