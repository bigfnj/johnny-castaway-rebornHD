"""Independent material/geometry checks and executed negative controls.

Expected material colors come from original-only reviewed annotations. Expected
skin base comes from the user-selected frame, not the correction formula.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

BUNDLE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_frame(row, output, index, protected, calibration):
    frame = row['frame']
    name = f'{frame:03}.png'
    original_path = BUNDLE / index[frame]['input']
    original = np.asarray(Image.open(original_path))
    path = output / row['candidate_png']
    with Image.open(path) as image:
        require(image.mode == 'RGBA', f'{name}: RGBA mode')
        require(list(image.size) == index[frame]['canvas'], f'{name}: canvas identity')
        actual = np.asarray(image).copy()
    require(np.array_equal(actual[:, :, 3], original[:, :, 3]), f'{name}: alpha identity')
    for point in protected[frame]['landmarks']:
        x, y = point['xy']
        role = point['role']
        require(actual[y, x].tolist() == point['rgba'], f'{name}: protected {role} point')
        if 'region_xywh' in point:
            x, y, width, height = point['region_xywh']
            require(sha(actual[y:y+height, x:x+width].tobytes()) == point['region_rgba_sha256'],
                    f'{name}: protected {role} region')
    mask = np.asarray(Image.open(output / row['mask']))
    require(mask.shape == original.shape[:2], f'{name}: mask canvas')
    cap = next(r for r in json.loads((BUNDLE / 'protected-cap-polygons-v1.json').read_bytes())['frames'] if r['frame'] == frame)
    boundary = cap['lower_boundary_pixel_edges']
    cap_pixels = np.array([[y + .5 < np.interp(x + .5, [p[0] for p in boundary], [p[1] for p in boundary])
                            for x in range(actual.shape[1])] for y in range(actual.shape[0])])
    require(np.all(mask[cap_pixels] == 0), f'{name}: cap excluded from mask')
    require(np.array_equal(actual[cap_pixels], original[cap_pixels]), f'{name}: full cap identity')
    require(np.array_equal(actual[mask == 0], original[mask == 0]), f'{name}: outside-mask identity')
    if frame == 29:
        require(path.read_bytes() == original_path.read_bytes(), f'{name}: canonical PNG identity')
    else:
        require(np.any(actual[:, :, :3] != original[:, :, :3]), f'{name}: expected skin correction')
    x, y = calibration[frame]['sample_xy']
    measured = np.median(actual[y-1:y+2, x-1:x+2, :3].reshape(-1, 3), axis=0).astype(int).tolist()
    require(measured == calibration[29]['base_rgb'], f'{name}: reference skin base')
    require(sha(path.read_bytes()) == row['candidate_png_sha256'], f'{name}: candidate hash')
    require(sha((output / row['mask']).read_bytes()) == row['mask_sha256'], f'{name}: mask hash')
    return {'frame': frame, 'status': 'PASS', 'material_points': len(protected[frame]['landmarks']),
            'material_regions': sum('region_xywh' in p for p in protected[frame]['landmarks']),
            'changed_pixels': int(np.any(actual[:, :, :3] != original[:, :, :3], axis=2).sum())}


def run(export, annotations, phase, output):
    output.mkdir(parents=True, exist_ok=False)
    recipe = json.loads((export / 'recipe.json').read_bytes())
    index_doc = json.loads((BUNDLE / 'input-index.json').read_bytes())
    index = {r['frame']: r for r in index_doc['frames']}
    protected_doc = json.loads(annotations.read_bytes())
    protected = {r['frame']: r for r in protected_doc['frames']}
    calibration = {r['frame']: r for r in json.loads((BUNDLE / 'calibration-v1.json').read_bytes())['frames']}
    rows = {r['frame']: r for r in recipe['frames']}
    require(set(rows) == set(index) == set(protected), 'Complete28-frame export and independent annotations required')
    require(recipe['algorithm_sha256'] == sha((BUNDLE / 'correct.py').read_bytes()), 'Export must use current corrector')
    require(protected_doc['source_index_sha256'] == sha((BUNDLE / 'input-index.json').read_bytes()), 'Protected input-index identity')
    for f, row in index.items():
        require(sha((BUNDLE / row['input']).read_bytes()) == row['sha256'], f'{f:03}.png: source identity')
        require(protected[f]['input_sha256'] == row['sha256'], f'{f:03}.png: protected-source identity')
    selected = [24, 29] if phase == 'smoke' else sorted(rows)
    results = [verify_frame(rows[f], export, index, protected, calibration) for f in selected]
    negatives = []
    if phase == 'regression':
        # Mutate one exported image at a time, updating its reported digest so
        # a semantic assertion, rather than a generic file hash, must fail.
        mutations = [('alpha', 24, None, 'alpha identity')]
        for role in ('hat-white', 'hat-gold', 'hair-or-beard', 'shorts-white', 'eye-white', 'eye-ink', 'cap-ink', 'lower-hair'):
            point = next((p for p in protected[24]['landmarks'] if p['role'] == role), None)
            require(point is not None, f'024.png: missing independent mutation witness {role}')
            mutations.append((role, 24, point['xy'], 'protected ' + role + ' point'))
        mutations += [('outside-mask', 24, None, 'outside-mask identity'),
                      ('wrong-skin-base', 24, calibration[24]['sample_xy'], 'reference skin base'),
                      ('changed-reference', 29, calibration[29]['sample_xy'], 'canonical PNG identity')]
        for label, frame, xy, expected in mutations:
            with tempfile.TemporaryDirectory(prefix='johnny-skin-negative-') as temp:
                temp = Path(temp)
                row = copy.deepcopy(rows[frame])
                for field in ('candidate_png', 'mask'):
                    destination = temp / row[field]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(export / row[field], destination)
                path = temp / row['candidate_png']
                a = np.asarray(Image.open(path)).copy()
                if label == 'alpha':
                    x, y = calibration[frame]['sample_xy']
                    a[y, x, 3] ^= 1
                elif label == 'outside-mask':
                    m = np.asarray(Image.open(temp / row['mask']))
                    y, x = next((y, x) for y in range(a.shape[0]-1, -1, -1)
                                for x in range(a.shape[1]) if m[y, x] == 0)
                    a[y, x, 0] ^= 1
                elif label == 'wrong-skin-base':
                    x, y = xy
                    a[y-1:y+2, x-1:x+2, 1] = np.clip(a[y-1:y+2, x-1:x+2, 1].astype(int) + 8, 0, 255)
                else:
                    x, y = xy
                    a[y, x, 0] ^= 1
                Image.fromarray(a).save(path)
                row['candidate_png_sha256'] = sha(path.read_bytes())
                expected_message = f'{frame:03}.png: {expected}'
                try:
                    verify_frame(row, temp, index, protected, calibration)
                except AssertionError as error:
                    require(str(error) == expected_message, f'{label}: wrong failure {error}')
                    negatives.append({'case': label, 'status': 'FIRED', 'failure': str(error)})
                else:
                    raise AssertionError(f'{label}: mutation survived')
        # A fresh real exporter execution proves deterministic reproduction.
        with tempfile.TemporaryDirectory(prefix='johnny-skin-replay-') as temp:
            temp = Path(temp)
            command = [sys.executable, '-B', str(BUNDLE / 'correct.py'), '--output', str(temp / 'replay')]
            result = subprocess.run(command, text=True, capture_output=True)
            require(result.returncode == 0 and '"frames": 28' in result.stdout, 'Fresh exporter replay witness')
            replay = json.loads((temp / 'replay/recipe.json').read_bytes())
            require(replay == recipe, 'Fresh exporter recipe identity')
            for row in recipe['frames']:
                for field in ('candidate_png', 'mask'):
                    require((temp / 'replay' / row[field]).read_bytes() == (export / row[field]).read_bytes(),
                            f"{row['frame']:03}.png: fresh replay bytes")
            (output / 'replay-stdout.txt').write_text(result.stdout, encoding='utf-8')
        # Execute changed corrector source in an isolated bundle. The altered
        # script must run and emit its own matching hash before judging a mutant.
        source = (BUNDLE / 'correct.py').read_text(encoding='utf-8')
        source_mutations = [
            ('disable-cap-exclusion', '        mask[protection > 0] = 0',
             '        # Deliberate mutation: omit cap exclusion', 'cap excluded from mask'),
            ('disable-color-gain', '    gain = target / source',
             '    gain = np.ones(3)', 'expected skin correction'),
        ]
        for label, old, new, expected in source_mutations:
            require(source.count(old) == 1, f'{label}: unique mutation target')
            with tempfile.TemporaryDirectory(prefix='johnny-skin-source-mutant-') as temp:
                temp = Path(temp)
                mutant = source.replace(old, new)
                (temp / 'correct.py').write_text(mutant, encoding='utf-8')
                for name in ('input-index.json', 'calibration-v1.json', 'protected-cap-polygons-v1.json'):
                    shutil.copyfile(BUNDLE / name, temp / name)
                shutil.copytree(BUNDLE / 'inputs', temp / 'inputs')
                run_result = subprocess.run([sys.executable, '-B', str(temp / 'correct.py'), '--output', str(temp / 'out')],
                                            capture_output=True, text=True)
                require(run_result.returncode == 0 and '"frames": 28' in run_result.stdout, f'{label}: executed exporter witness')
                changed_recipe = json.loads((temp / 'out/recipe.json').read_bytes())
                actual_hash = sha((temp / 'correct.py').read_bytes())
                require(changed_recipe['algorithm_sha256'] == actual_hash and actual_hash != recipe['algorithm_sha256'],
                        f'{label}: changed source hash witness')
                test_row = next(r for r in changed_recipe['frames'] if r['frame'] == 24)
                try:
                    verify_frame(test_row, temp / 'out', index, protected, calibration)
                except AssertionError as error:
                    require(str(error) == f'024.png: {expected}', f'{label}: wrong failure {error}')
                    negatives.append({'case': label, 'status': 'FIRED', 'failure': str(error),
                                      'executed_source_sha256': actual_hash,
                                      'execution_witness': json.loads(run_result.stdout)})
                else:
                    raise AssertionError(f'{label}: executed source mutant survived')
        spec = importlib.util.spec_from_file_location('skin_correct_under_test', BUNDLE / 'correct.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # A changed shadow's coverage cannot re-fit a separate flat sample.
        # Exercise both actual correction and identity gains explicitly.
        sample = np.array([[[252, 133, 85, 254], [210, 105, 70, 200], [30, 20, 10, 0]]], dtype=np.uint8)
        mask = np.array([[255, 255, 0]], dtype=np.uint8)
        first = module.recolor(sample, mask, [252, 133, 85], [252, 148, 88])
        more_shadow = np.repeat(sample, 9, axis=0)
        more_mask = np.repeat(mask, 9, axis=0)
        more_shadow[1:, 0, :3] = [210, 105, 70]
        second = module.recolor(more_shadow, more_mask, [252, 133, 85], [252, 148, 88])
        require(np.array_equal(first[0, 0], second[0, 0]), 'Shadow coverage changed flat calibration')
        require(first[0, 1, 1] < first[0, 0, 1], 'Shading was flattened')
        require(np.array_equal(module.recolor(sample, mask, [252, 133, 85], [252, 133, 85]), sample),
                'Identity gains must preserve shaded and partially transparent controls')
        # Positive restoration after all mutations.
        for frame in selected:
            verify_frame(rows[frame], export, index, protected, calibration)
    report = {'status': 'PASS', 'phase': phase, 'test_sha256': sha(Path(__file__).read_bytes()),
              'algorithm_sha256': recipe['algorithm_sha256'],
              'recipe_sha256': sha((export / 'recipe.json').read_bytes()),
              'protected_annotations_sha256': sha(annotations.read_bytes()),
              'frames': results, 'negative_controls': negatives,
              'positive_restoration': phase == 'regression',
              'limitations': 'Sparse independent material witnesses and exact mask/alpha checks complement visual review; they do not prove perfect semantic segmentation.'}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'phase': phase, 'frames': len(results), 'negative_controls': len(negatives)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--annotations', type=Path, required=True)
    parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.export.resolve(), args.annotations.resolve(), args.phase, args.output.resolve())
