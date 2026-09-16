"""Match the selected018-foot-v5 runtime to canonical029 using pinned color functions.

Only color changes. A new source-bound018 cap/calibration/material annotation is
required; the old018 mask and calibration are never loaded.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
ALGORITHM = 'art/cartoon/skin-tone-v1/correct.py'
ALGORITHM_SHA = '70be24d13eb34317f602b0b66f952a4d3dbe8e29935b4f6c8353f15c8e9d3534'
INPUT_SHA = '183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2'
TARGET = [252, 148, 88]
REFERENCE_SHA = '8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a'
CALIBRATION_SHA = '6d960c6d70d6228f9c5285f3d7331f8c77083c75cca2c766a6c36ac84e9bfa65'
EXPORTER_SHA = 'c382582ad113c917ee8b5f8e0ebda392ceb5f746bdb4be9982b7a51f04418c63'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, label):
    if not value:
        raise ValueError(label)


def load_inputs(runtime, annotation_path, annotation_sha):
    algorithm_path = ROOT / ALGORITHM
    require(sha(algorithm_path.read_bytes()) == ALGORITHM_SHA, '018: frozen color algorithm')
    spec = importlib.util.spec_from_file_location('frozen_skin_color', algorithm_path)
    algorithm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(algorithm)
    source = runtime / 'BMP/JOHNWALK.BMP/018.png'
    raw = source.read_bytes()
    require(sha(raw) == INPUT_SHA, '018: runtime source identity')
    with Image.open(source) as image:
        require(image.mode == 'RGBA' and image.size == (64, 154), '018: runtime canvas')
        rgba = np.asarray(image).copy()
    recipe_path, report_path = runtime/'recipe.json', runtime/'export-report.json'
    export_recipe = json.loads(recipe_path.read_bytes())
    export_report = json.loads(report_path.read_bytes())
    require(export_report['outputs_sha256']['BMP/JOHNWALK.BMP/018.png'] == INPUT_SHA
            and export_report['export_source_sha256'] == EXPORTER_SHA
            and export_report['recipe_sha256'] == sha(recipe_path.read_bytes())
            and export_report['runtime_fit_all_source_centers'] is True
            and export_report['runtime_sprites_written'] is True
            and export_recipe['frames'][0]['frame'] == 18, '018: source export binding')
    require(sha(annotation_path.read_bytes()) == annotation_sha, '018: annotation identity')
    annotation = json.loads(annotation_path.read_bytes())
    require(annotation['frame'] == 18 and annotation['input_sha256'] == INPUT_SHA
            and annotation['canvas'] == [64, 154], '018: annotation input binding')
    patch = annotation['calibration']
    x, y = patch['sample_xy']
    region = rgba[y-1:y+2, x-1:x+2]
    require(patch['patch_radius'] == 1 and region.shape == (3, 3, 4)
            and int(region[:, :, 3].min()) >= 250
            and np.median(region[:, :, :3].reshape(-1, 3), axis=0).tolist() == patch['base_rgb'],
            '018: new calibration patch')
    cap = annotation['cap']
    require(cap['frame'] == 18 and cap['input_sha256'] == INPUT_SHA
            and cap['canvas'] == [64, 154], '018: new cap input binding')
    cap_mask = algorithm.cap_exclusion(cap)
    for point in annotation['landmarks']:
        x, y = point['xy']
        require(rgba[y, x].tolist() == point['rgba'], '018: material input ' + point['role'])
        if 'region_xywh' in point:
            x, y, width, height = point['region_xywh']
            require(sha(rgba[y:y+height, x:x+width].tobytes()) == point['region_rgba_sha256'],
                    '018: material input region ' + point['role'])
    canonical_path = ROOT/'art/cartoon/skin-tone-v1/inputs/029.png'
    calibration_path = ROOT/'art/cartoon/skin-tone-v1/calibration-v1.json'
    require(sha(canonical_path.read_bytes()) == REFERENCE_SHA
            and sha(calibration_path.read_bytes()) == CALIBRATION_SHA, '029: canonical identity')
    canonical = np.asarray(Image.open(canonical_path))
    original_patch = next(row for row in json.loads(calibration_path.read_bytes())['frames'] if row['frame'] == 29)
    x, y = original_patch['sample_xy']
    require(original_patch['base_rgb'] == TARGET
            and np.median(canonical[y-1:y+2, x-1:x+2, :3].reshape(-1, 3), axis=0).tolist() == TARGET,
            '029: canonical skin base')
    return algorithm, rgba, annotation, cap_mask, {
        'source': {'path': source.relative_to(ROOT).as_posix(), 'sha256': INPUT_SHA},
        'source_export_recipe': {'path': recipe_path.relative_to(ROOT).as_posix(), 'sha256': sha(recipe_path.read_bytes())},
        'source_export_report': {'path': report_path.relative_to(ROOT).as_posix(), 'sha256': sha(report_path.read_bytes())},
        'annotation': {'path': annotation_path.relative_to(ROOT).as_posix(), 'sha256': annotation_sha}}


def export(runtime, annotation_path, annotation_sha, output):
    require(not output.exists(), '018: preserve existing output')
    algorithm, rgba, annotation, protection, inputs = load_inputs(runtime, annotation_path, annotation_sha)
    patch = annotation['calibration']
    mask = algorithm.skin_confidence(rgba)
    mask[protection > 0] = 0
    result = algorithm.recolor(rgba, mask, patch['base_rgb'], TARGET)
    require(np.array_equal(result[:, :, 3], rgba[:, :, 3]), '018: alpha identity')
    require(np.array_equal(result[mask == 0], rgba[mask == 0]), '018: outside-mask identity')
    require(np.array_equal(result[protection > 0], rgba[protection > 0]), '018: full cap identity')
    for point in annotation['landmarks']:
        x, y = point['xy']
        require(result[y, x].tolist() == point['rgba'], '018: protected ' + point['role'])
    changed = np.any(result[:, :, :3] != rgba[:, :, :3], axis=2)
    require(bool(changed.any()), '018: expected skin correction')
    x, y = patch['sample_xy']
    measured = np.median(result[y-1:y+2, x-1:x+2, :3].reshape(-1, 3), axis=0).astype(int).tolist()
    require(measured == TARGET, '018: reference skin base')
    output.mkdir(parents=True, exist_ok=False)
    for relative, pixels in (('sprites/018.png', result), ('masks/018.png', mask), ('protected-cap/018.png', protection)):
        path = output/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(pixels).save(path)
    row = {'frame': 18, 'path': 'BMP/JOHNWALK.BMP/018.png', 'member': 'data/styles/cartoon/BMP/JOHNWALK.BMP/018.png',
           'runtime_canvas': [64, 154], 'input_sha256': INPUT_SHA,
           'candidate_png': 'sprites/018.png', 'candidate_png_sha256': sha((output/'sprites/018.png').read_bytes()),
           'rgba_sha256': sha(result.tobytes()), 'alpha_sha256': sha(result[:, :, 3].tobytes()),
           'mask': 'masks/018.png', 'mask_sha256': sha((output/'masks/018.png').read_bytes()),
           'protected_cap_mask_l_sha256': sha(protection.tobytes()),
           'base_before_rgb': patch['base_rgb'], 'base_target_rgb': TARGET, 'base_after_rgb': measured,
           'channel_gain': (np.asarray(TARGET)/np.asarray(patch['base_rgb'])).tolist(),
           'changed_pixels': int(changed.sum())}
    recipe = {'schema_version': 1, 'operation': 'post-export-color-correction',
              'scope': 'New018-foot-v5 contact and motion preview only; no production or revised-pose approval.',
              'algorithm': {'path': ALGORITHM, 'sha256': ALGORITHM_SHA}, 'adapter_sha256': sha(Path(__file__).read_bytes()),
              'pillow_version': PIL.__version__, 'numpy_version': np.__version__,
              'canonical_reference': {'frame': 29, 'input_sha256': REFERENCE_SHA, 'calibration_sha256': CALIBRATION_SHA},
              'target_base_rgb': TARGET, 'inputs': inputs, 'frames': [row]}
    (output/'recipe.json').write_text(json.dumps(recipe, indent=2)+'\n', encoding='utf-8', newline='\n')
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--annotations', type=Path, required=True)
    parser.add_argument('--annotations-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print('WITNESS correct018.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    try:
        recipe = export(args.runtime.resolve(), args.annotations.resolve(), args.annotations_sha256, args.output.resolve())
    except (ValueError, KeyError, OSError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps({'status': 'PASS', 'changed_pixels': recipe['frames'][0]['changed_pixels'],
                      'candidate_png_sha256': recipe['frames'][0]['candidate_png_sha256']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


