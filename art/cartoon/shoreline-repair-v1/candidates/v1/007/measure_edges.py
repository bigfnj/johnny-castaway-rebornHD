"""Read-only image measurements; top/bottom own corner pixels to avoid double count."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
recipe = json.loads((HERE / 'recipe.json').read_bytes())
alpha = Image.open(HERE / 'full-guide-padded.png').getchannel('A')
pad = recipe['padding_hd']
scale = recipe['affine_forward'][0]
x, y = [int(n*scale)+pad for n in recipe['guide_offset_xy']]
w, h = recipe['runtime_canvas']
regions = {'top': (0,0,alpha.width,y), 'bottom': (0,y+h,alpha.width,alpha.height),
           'left': (0,y,x,y+h), 'right': (x+w,y,alpha.width,y+h)}
rows = {}
for name, rect in regions.items():
    hist = alpha.crop(rect).histogram()
    rows[name] = {'nonzero_pixels': sum(hist[1:]), 'alpha8_pixels': sum(hist[8:]),
                  'maximum_alpha': max(i for i,n in enumerate(hist) if n),
                  'alpha_sum': sum(i*n for i,n in enumerate(hist))}
report = {'frame': 7, 'method': 'Disjoint edge regions over entire filtered guide, not only local pad; top/bottom include corners.',
          'source_png_sha256': hashlib.sha256((HERE / 'full-guide-padded.png').read_bytes()).hexdigest(),
          'recipe_sha256': hashlib.sha256((HERE / 'recipe.json').read_bytes()).hexdigest(),
          'measurement_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'runtime_window_in_full_padded': [x,y,x+w,y+h], 'edges': rows,
          'context': 'Top is the straight sand join overlapping into the island; bottom is foam extent. Geometric edge counts are not material segmentation or approval.'}
(HERE / 'edge-crop.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(rows))
