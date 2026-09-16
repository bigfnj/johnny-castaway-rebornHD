"""Focused018 color checks against source pixels and independent annotations."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image
import correct018 as adapter

ROOT = adapter.ROOT
sha = adapter.sha
load = lambda p: json.loads(p.read_bytes())


def require(value, label):
    if not value:
        raise AssertionError('018.png: ' + label)


def verify(folder, recipe):
    row = recipe['frames'][0]
    require(recipe['adapter_sha256'] == sha(Path(adapter.__file__).read_bytes()), 'adapter identity')
    annotation = load(ROOT/recipe['inputs']['annotation']['path'])
    source_path = ROOT/recipe['inputs']['source']['path']
    require(sha(source_path.read_bytes()) == adapter.INPUT_SHA == annotation['input_sha256'], 'source identity')
    original = np.asarray(Image.open(source_path))
    with Image.open(folder/row['candidate_png']) as image:
        require(image.mode == 'RGBA' and image.size == (64, 154), 'canvas identity')
        actual = np.asarray(image).copy()
    require(np.array_equal(actual[:, :, 3], original[:, :, 3]), 'alpha identity')
    with Image.open(folder/row['mask']) as image:
        require(image.mode == 'L' and image.size == (64, 154), 'mask canvas')
        mask = np.asarray(image).copy()
    boundary = annotation['cap']['lower_boundary_pixel_edges']
    cap = np.array([[y+.5 < np.interp(x+.5, [p[0] for p in boundary], [p[1] for p in boundary])
                     for x in range(64)] for y in range(154)])
    require(np.all(mask[cap] == 0), 'full cap mask exclusion')
    require(np.array_equal(actual[cap], original[cap]), 'full cap identity')
    for point in annotation['landmarks']:
        x, y = point['xy']
        require(actual[y, x].tolist() == point['rgba'], 'protected ' + point['role'] + ' point')
        if 'region_xywh' in point:
            x, y, width, height = point['region_xywh']
            require(sha(actual[y:y+height, x:x+width].tobytes()) == point['region_rgba_sha256'],
                    'protected ' + point['role'] + ' region')
    require(np.array_equal(actual[mask == 0], original[mask == 0]), 'outside-mask identity')
    require(bool(np.any(actual[:, :, :3] != original[:, :, :3])), 'expected skin correction')
    x, y = annotation['calibration']['sample_xy']
    median = np.median(actual[y-1:y+2, x-1:x+2, :3].reshape(-1, 3), axis=0).astype(int).tolist()
    require(median == [252, 148, 88], 'reference skin base')
    require(sha((folder/row['candidate_png']).read_bytes()) == row['candidate_png_sha256'], 'candidate hash')
    require(sha((folder/row['mask']).read_bytes()) == row['mask_sha256'], 'mask hash')
    return {'frame': 18, 'material_points': len(annotation['landmarks']),
            'material_regions': sum('region_xywh' in p for p in annotation['landmarks']),
            'changed_pixels': int(np.any(actual[:, :, :3] != original[:, :, :3], axis=2).sum()),
            'reference_base_rgb': median}


def run(folder, output, phase):
    output.mkdir(parents=True, exist_ok=True)
    target = output/(phase+'.json')
    require(not target.exists(), 'preserve test report')
    recipe_path = folder/'recipe.json'
    recipe = load(recipe_path)
    inputs = {'recipe': sha(recipe_path.read_bytes()), 'adapter': sha(Path(adapter.__file__).read_bytes()),
              'test': sha(Path(__file__).read_bytes()), 'annotation': recipe['inputs']['annotation']['sha256']}
    result = verify(folder, recipe)
    negative = []
    replay = None
    if phase == 'regression':
        smoke = load(output/'smoke.json')
        require(smoke['status'] == 'PASS' and smoke['inputs_sha256'] == inputs, 'matching smoke before regression')
        row = recipe['frames'][0]
        annotation = load(ROOT/recipe['inputs']['annotation']['path'])
        controls = [('alpha', 'alpha identity'), ('cap-pixel', 'full cap identity'),
                    ('cap-mask', 'full cap mask exclusion'), ('outside-mask', 'outside-mask identity'),
                    ('wrong-base', 'reference skin base'), ('unchanged-input', 'expected skin correction')]
        for role in ('hair-or-beard', 'shorts-white', 'lower-beard'):
            controls.append((role, 'protected '+role+' point'))
        for role in ('hair-or-beard', 'shorts-white'):
            controls.append((role+'-region', 'protected '+role+' region'))
        for name, expected in controls:
            with tempfile.TemporaryDirectory(prefix='color018-negative-', dir=output) as scratch:
                temp = Path(scratch)
                for key in ('candidate_png', 'mask'):
                    destination = temp/row[key]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(folder/row[key], destination)
                path, mask_path = temp/row['candidate_png'], temp/row['mask']
                pixels = np.asarray(Image.open(path)).copy()
                mask = np.asarray(Image.open(mask_path)).copy()
                x, y = annotation['calibration']['sample_xy']
                if name == 'alpha': pixels[y, x, 3] ^= 1
                elif name == 'cap-pixel': pixels[6, 20, 0] ^= 1
                elif name == 'cap-mask': mask[6, 20] = 255
                elif name == 'outside-mask': pixels[153, 0, 0] ^= 1
                elif name == 'wrong-base': pixels[y-1:y+2, x-1:x+2, 1] = 1
                elif name == 'unchanged-input': pixels = np.asarray(Image.open(ROOT/recipe['inputs']['source']['path'])).copy()
                else:
                    role = name.removesuffix('-region')
                    point = next(p for p in annotation['landmarks'] if p['role'] == role)
                    x, y = point['xy']
                    if name.endswith('-region'): x, y = point['region_xywh'][:2]
                    pixels[y, x, 0] ^= 1
                Image.fromarray(pixels).save(path)
                Image.fromarray(mask).save(mask_path)
                changed = copy.deepcopy(recipe)
                changed['frames'][0]['candidate_png_sha256'] = sha(path.read_bytes())
                changed['frames'][0]['mask_sha256'] = sha(mask_path.read_bytes())
                caught = None
                try:
                    verify(temp, changed)
                except AssertionError as error:
                    caught = str(error)
                require(caught == '018.png: '+expected, 'negative '+name+' named refusal; got '+str(caught))
                negative.append({'case': name, 'result': 'FIRED', 'failure': caught})
        runtime = (ROOT/recipe['inputs']['source_export_recipe']['path']).parent
        annotations = ROOT/recipe['inputs']['annotation']['path']
        # Source binding errors are exercised with new annotation bytes, never edits to the reviewed document.
        for key, expected in (('input', '018: annotation input binding'), ('cap', '018: new cap input binding'),
                              ('calibration', '018: new calibration patch')):
            changed = copy.deepcopy(annotation)
            if key == 'input': changed['input_sha256'] = '0'*64
            elif key == 'cap': changed['cap']['input_sha256'] = '0'*64
            else: changed['calibration']['base_rgb'] = [1, 1, 1]
            path = output/('damaged-'+key+'.json')
            path.write_text(json.dumps(changed)+'\n', encoding='utf-8')
            command = [sys.executable, '-B', str(Path(adapter.__file__).resolve()), '--runtime', str(runtime),
                       '--annotations', str(path), '--annotations-sha256', sha(path.read_bytes()),
                       '--output', str(output/('rejected-'+key))]
            completed = subprocess.run(command, capture_output=True, text=True)
            witness = 'WITNESS correct018.py SHA256='+inputs['adapter']
            require(witness in completed.stdout and completed.returncode == 1
                    and completed.stderr.strip() == 'FAIL '+expected, 'input negative '+key)
            negative.append({'case': 'stale-'+key, 'result': 'FIRED', 'failure': expected,
                             'stdout': completed.stdout, 'stderr': completed.stderr, 'exit_code': completed.returncode})
        command = [sys.executable, '-B', str(Path(adapter.__file__).resolve()), '--runtime', str(runtime),
                   '--annotations', str(annotations), '--annotations-sha256', inputs['annotation'],
                   '--output', str(output/'fresh-replay')]
        completed = subprocess.run(command, capture_output=True, text=True)
        require(completed.returncode == 0 and 'WITNESS correct018.py SHA256='+inputs['adapter'] in completed.stdout,
                'fresh-process replay')
        relative = ('sprites/018.png', 'masks/018.png', 'protected-cap/018.png', 'recipe.json')
        for name in relative:
            require((folder/name).read_bytes() == (output/'fresh-replay'/name).read_bytes(), 'exact replay '+name)
        replay = {'files_identical': list(relative), 'stdout': completed.stdout, 'stderr': completed.stderr}
        algorithm, rgba, annotation, cap, info = adapter.load_inputs(runtime, annotations, inputs['annotation'])
        mask = algorithm.skin_confidence(rgba)
        mask[cap > 0] = 0
        base = annotation['calibration']['base_rgb']
        require(np.array_equal(algorithm.recolor(rgba, mask, base, base), rgba), 'same-base no-op control')
        require(np.array_equal(algorithm.recolor(rgba, np.zeros_like(mask), base, adapter.TARGET), rgba),
                'zero-mask no-op control')
        verify(folder, recipe)
    record = {'status': 'PASS', 'phase': phase, 'inputs_sha256': inputs, 'actual_frame': result,
              'negative_controls': negative, 'fresh_replay': replay,
              'no_op_controls': ['same-base', 'zero-mask'] if phase == 'regression' else [],
              'scope': 'Only new018-v2 color; no anatomy, native-playback or full28-pose revalidation.'}
    target.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'phase': phase, 'frame': 18, 'negative_controls_fired': len(negative)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    options = parser.parse_args()
    run(options.export.resolve(), options.output.resolve(), options.phase)
