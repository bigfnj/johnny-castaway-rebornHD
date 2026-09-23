"""Read-only palette comparison. Writes numerical analysis, never edited images."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

here = Path(__file__).resolve().parent
visitor = here.parent / 'visitor-leg-pose-corrections-v2'
items = {
    '004_import': visitor / 'imported-004-v1/004-transparent-v1.png',
    '005_import': visitor / 'imported-005-v1/005-transparent-v1.png',
    '003_reference': visitor / 'generation/SSUZY1.BMP/003-generated-v2.png',
    '006_reference': visitor / 'generation/SSUZY1.BMP/006-generated-v3.png',
}
result = {}
for name, path in items.items():
    im = Image.open(path).convert('RGBA')
    rgba = np.asarray(im)
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(float)
    h, s, v = hsv[:,:,0] * 360/255, hsv[:,:,1] / 255, hsv[:,:,2] / 255
    alpha = rgba[:,:,3]
    interior = np.asarray(im.getchannel('A').filter(ImageFilter.MinFilter(3))) >= 240
    masks = {
        'skin_orange': (h >= 16) & (h <= 44) & (s >= .35) & (v >= .40),
        'hair_red': ((h <= 15) | (h >= 350)) & (s >= .5) & (v >= .25),
        'suit_magenta': (h >= 285) & (h <= 330) & (s >= .5) & (v >= .25),
        'glasses_cyan': (h >= 170) & (h <= 205) & (s >= .4) & (v >= .3),
        'dark_outline': v <= .25,
    }
    palette = {}
    for label, mask in masks.items():
        use = mask & interior
        n = int(use.sum())
        palette[label] = {
            'pixels': n,
            'rgb_median': [round(float(x), 1) for x in np.median(rgba[:,:,:3][use], axis=0)] if n else None,
            'hsv_median_deg_pct': [round(float(np.median(c[use]) * scale), 2) for c,scale in [(h,1),(s,100),(v,100)]] if n else None,
            'value_quartiles_pct': [round(float(x),2) for x in np.quantile(v[use],[.25,.5,.75])*100] if n else None,
        }
    result[name] = {'path': str(path), 'size': list(im.size), 'mode': im.mode,
                    'alpha_range': [int(alpha.min()),int(alpha.max())],
                    'opaque_pixels': int((alpha >= 240).sum()), 'palette': palette}
out = here / 'ssuzy-color-statistics.json'
out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, indent=2))
