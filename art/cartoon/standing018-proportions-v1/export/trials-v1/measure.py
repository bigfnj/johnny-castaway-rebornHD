"""Read-only018 trial measurements; ROI/cloth labels are diagnostic observations."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--version', type=int, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
work = root / f'build/standing018-proportions/stage-v{args.version}'
recipe = json.loads((work / 'runtime/recipe.json').read_bytes())
source = root / f'art/cartoon/standing018-proportions-v1/018-torso-v{args.version}.png'
with Image.open(source) as image:
    raw = np.asarray(image).copy()
    mode, canvas = image.mode, list(image.size)
alpha = raw[:, :, 3]
yy, xx = np.indices(alpha.shape)
rgb = raw[:, :, :3].astype(int)
ty = recipe['frames'][0]['affine_forward'][5]
near = (alpha >= 8) & (xx >= 300) & (xx < 560) & (yy >= 1300)
far = (alpha >= 8) & (xx >= 580) & (xx < 740) & (yy >= 1250)
cloth = (alpha >= 128) & (rgb.min(2) >= 170) & ((rgb.max(2) - rgb.min(2)) < 45) & (yy >= 600) & (yy < 1150)
hd = lambda y: (int(y) + .5) * .1 + ty
runtime = work / 'runtime/BMP/JOHNWALK.BMP/018.png'
with Image.open(runtime) as image:
    rendered = np.asarray(image)
result = {
    'scope': 'Read-only technical measurements of a nonselected draft. ROI labels and neutral-white cloth bounds are diagnostic, not independent anatomical ground truth.',
    'source': {'path': source.relative_to(root).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()},
    'source_mode': mode, 'source_canvas': canvas, 'source_alpha_range': [int(alpha.min()), int(alpha.max())],
    'corner_alpha': [int(alpha[y, x]) for x, y in ((0, 0), (1023, 0), (0, 1535), (1023, 1535))],
    'cap_raw': recipe['frames'][0]['cap_raw'], 'affine_forward': recipe['frames'][0]['affine_forward'],
    'regions_raw': {'near_sole': '300<=x<560, y>=1300, alpha>=8', 'far_sole': '580<=x<740, y>=1250, alpha>=8',
                    'cloth': '600<=y<1150, alpha>=128, min(R,G,B)>=170, max(R,G,B)-min(R,G,B)<45'},
    'near_sole_raw_y': int(yy[near].max()), 'far_sole_raw_y': int(yy[far].max()),
    'near_sole_hd_center': hd(yy[near].max()), 'far_sole_hd_center': hd(yy[far].max()),
    'sole_separation_hd': (int(yy[near].max()) - int(yy[far].max())) * .1,
    'cloth_raw_y_range': [int(yy[cloth].min()), int(yy[cloth].max())],
    'cloth_hd_y_range': [hd(yy[cloth].min()), hd(yy[cloth].max())],
    'runtime': {'path': runtime.relative_to(root).as_posix(), 'sha256': hashlib.sha256(runtime.read_bytes()).hexdigest(),
                'mode': 'RGBA', 'canvas': [rendered.shape[1], rendered.shape[0]],
                'alpha_range': [int(rendered[:, :, 3].min()), int(rendered[:, :, 3].max())]},
    'measurement_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
target = work / 'measurements.json'
assert not target.exists()
target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result))
