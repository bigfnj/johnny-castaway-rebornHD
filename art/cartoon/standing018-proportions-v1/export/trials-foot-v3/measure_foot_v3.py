"""Measure the fixed018 v3 export and preserve this rejected-fit study only."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'art/cartoon/standing018-proportions-v1'
WORK = ROOT / 'build/standing018-proportions/stage-v3'
OUT = BUNDLE / 'export/trials-foot-v3'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def rgba(path):
    with Image.open(path) as image:
        assert image.mode == 'RGBA'
        return np.asarray(image).copy()


def box(mask):
    y, x = np.where(mask)
    return [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1] if len(x) else None


def comparison(a, b, rows):
    a, b = a[rows[0]:rows[1]], b[rows[0]:rows[1]]
    aa, ba = a[:, :, 3], b[:, :, 3]
    support = (aa >= 8) | (ba >= 8)
    threshold_changed = (aa >= 8) != (ba >= 8)
    return {
        'row_range_exclusive': rows,
        'all_rgba_changed_pixels': int(np.any(a != b, axis=2).sum()),
        'rgba_changed_with_either_alpha8': int((np.any(a != b, axis=2) & support).sum()),
        'alpha_changed_with_either_alpha8': int(((aa != ba) & support).sum()),
        'alpha8_silhouette_changed_pixels': int(threshold_changed.sum()),
        'alpha8_union_pixels': int(support.sum()),
        'alpha8_intersection_over_union': float(((aa >= 8) & (ba >= 8)).sum() / support.sum()),
        'v2_alpha8_bounds_relative_rows': box(aa >= 8),
        'v3_alpha8_bounds_relative_rows': box(ba >= 8),
    }


raw_paths = [BUNDLE / '018-torso-v2.png', BUNDLE / '018-foot-v3.png']
raws = [rgba(path) for path in raw_paths]
runtime_paths = [ROOT / f'build/standing018-proportions/stage-v{v}/runtime/BMP/JOHNWALK.BMP/018.png' for v in (2, 3)]
runtimes = [rgba(path) for path in runtime_paths]
recipe = load(WORK / 'runtime/recipe.json')
row = recipe['frames'][0]
v3 = raws[1]
alpha = v3[:, :, 3]
yy, xx = np.indices(alpha.shape)
rgb = v3[:, :, :3].astype(int)
near = (xx >= 300) & (xx < 560) & (yy >= 1300)
far = (xx >= 580) & (xx < 740) & (yy >= 1250)
cloth = (alpha >= 128) & (rgb.min(2) >= 170) & ((rgb.max(2)-rgb.min(2)) < 45) & (yy >= 600) & (yy < 1150)
hd = lambda y: (int(y) + .5) * .1 + row['affine_forward'][5]
feet = {}
for threshold in (8, 128, 250):
    feet[str(threshold)] = {}
    for name, roi in [('near', near), ('far', far)]:
        mask = roi & (alpha >= threshold)
        y = int(yy[mask].max())
        feet[str(threshold)][name] = {'raw_y': y, 'hd_source_center_y': hd(y), 'bounds_raw_exclusive': box(mask)}

result = {
    'schema_version': 1,
    'scope': 'Technical draft measurement only. No color correction, native capture, human acceptance or full unchanged exporter-suite rerun.',
    'source': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())} for p in raw_paths],
    'raw_mode': 'RGBA', 'raw_canvas': [1024, 1536],
    'raw_alpha_range': [int(alpha.min()), int(alpha.max())],
    'raw_corner_rgba': [v3[y, x].tolist() for x, y in [(0, 0), (1023, 0), (0, 1535), (1023, 1535)]],
    'cap_raw': row['cap_raw'], 'affine_forward': row['affine_forward'],
    'runtime_canvas': [64, 154],
    'source_alpha8_centers_fit': load(WORK / 'runtime/export-report.json')['runtime_fit_all_source_centers'],
    'foot_regions_raw': {'near': '300<=x<560, y>=1300', 'far': '580<=x<740, y>=1250'},
    'foot_bounds_by_alpha_threshold': feet,
    'alpha8_near_hd': feet['8']['near']['hd_source_center_y'],
    'alpha8_far_hd': feet['8']['far']['hd_source_center_y'],
    'alpha8_separation_hd': feet['8']['near']['hd_source_center_y'] - feet['8']['far']['hd_source_center_y'],
    'v2_alpha8_near_far_hd': [146.0, 138.5],
    'requested_alpha8_far_target_hd': [144, 145],
    'target_observation': 'V3 moves the far sole only1.9HD lower, leaving3.6 to4.6HD to the requested range. Near sole remains146.0HD. This is a source-contour comparison, not proof of native sand contact.',
    'cloth_expression': '600<=y<1150, alpha>=128, min(R,G,B)>=170, max(R,G,B)-min(R,G,B)<45',
    'cloth_raw_y_range': [int(yy[cloth].min()), int(yy[cloth].max())],
    'cloth_hd_y_range': [hd(yy[cloth].min()), hd(yy[cloth].max())],
    'raw_region_comparisons': {
        'upper_body': comparison(*raws, [0, 700]),
        'shorts_region': comparison(*raws, [700, 1100]),
    },
    'runtime_region_comparisons': {
        'upper_body': comparison(*runtimes, [0, 67]),
        'shorts_region': comparison(*runtimes, [67, 107]),
    },
    'preservation_limit': 'Imagegen did not preserve upper-body or shorts bytes exactly. Threshold-silhouette overlap and bounds describe the size of differences; they do not prove anatomical identity. Hidden RGB changes are counted separately from alpha8-supported changes.',
    'runtime': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())} for p in runtime_paths],
    'measurement_source_sha256': sha(Path(__file__).read_bytes()),
}
assert not OUT.exists()
OUT.mkdir(parents=True)
files = {}
for name in ['staging.json', 'preview/recipe.json', 'preview/export-report.json', 'runtime/recipe.json', 'runtime/export-report.json']:
    files[name] = (WORK / name).read_bytes()
files['measurements.json'] = (json.dumps(result, indent=2) + '\n').encode()
files['measure_foot_v3.py'] = Path(__file__).read_bytes()
for name, payload in files.items():
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    assert path.read_bytes() == payload
record = {'schema_version': 1, 'scope': result['scope'], 'files_sha256': {name: sha(payload) for name, payload in files.items()}, 'measurement_source_path': Path(__file__).relative_to(ROOT).as_posix(), 'raw_sources_sha256': {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in raw_paths}, 'runtime_pngs_retained_in_ignored_build': result['runtime'], 'commands': ['python -B art/cartoon/standing018-proportions-v1/export/stage.py --source art/cartoon/standing018-proportions-v1/018-foot-v3.png --source-sha256 dc4bc9bb99baf226e7cd3086a5f88b8fcacb4faf521b53c1214d5c86fdb484b1 --work build/standing018-proportions/stage-v3', 'python -B build/standing018-proportions/stage-v3/authoring/export.py --prepare --source 018-foot-v3.png --output build/standing018-proportions/stage-v3/preview --preview-only', 'python -B build/standing018-proportions/stage-v3/authoring/export.py --recipe build/standing018-proportions/stage-v3/preview/recipe.json --output build/standing018-proportions/stage-v3/runtime', 'python -B build/standing018-proportions/measure_foot_v3.py'], 'command_results': ['PASS byte-exact018 authoring staging', 'PASS arrival018 PREVIEW ONLY', 'PASS arrival018 runtime-canvas candidate written; not promoted', 'PASS measurement and byte-exact evidence preservation'], 'interpreter': 'Python3.11.15 with Pillow12.3.0, NumPy2.4.6'}
(OUT / 'evidence.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result, indent=2))
print('EVIDENCE ' + sha((OUT / 'evidence.json').read_bytes()))
