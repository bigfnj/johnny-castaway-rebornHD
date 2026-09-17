"""Export three rock-ring phases through one common uniform registration."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from PIL import Image, __version__ as pillow_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import inspect_png

sha = lambda raw: hashlib.sha256(raw).hexdigest()
AFFINE = [.157, 0, 104 - .157 * 777.5, 0, .157, 1 - .157 * 335]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stats(image):
    alpha = image.getchannel('A')
    h = alpha.histogram()
    return {'alpha8_bounds': alpha.point(lambda a:255 if a>=8 else 0).getbbox(),
            'nonzero_pixels':sum(h[1:]), 'alpha8_pixels':sum(h[8:]),
            'maximum_alpha':alpha.getextrema()[1],
            'dark_alpha8_pixels':sum(a>=8 and max(r,g,b)<100 for r,g,b,a in image.get_flattened_data())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    filter_path = ROOT / 'art/cartoon/seasonal-v1/export.py'
    mask_path = ROOT / 'art/cartoon/shoreline-repair-v1/foam-contact-v2/export.py'
    filt = load(filter_path, 'low_ring_filter')
    mask = load(mask_path, 'low_ring_mask')
    rock_path = HERE.parent / 'static-v2/BMP/BACKGRND.BMP/002.png'
    rock = Image.open(rock_path).convert('RGBA')
    base_path = HERE.parent / 'native-v1/images/prewave-candidate.png'
    base = Image.open(base_path).convert('RGBA')
    rows = []
    for frame in range(39, 42):
        source_path = HERE / f'{frame:03}-raw-v1.png'
        source = Image.open(source_path).convert('RGBA')
        padded = filt.resample(source, [208,58], AFFINE)
        unmasked = padded.crop((filt.PAD,filt.PAD,filt.PAD+208,filt.PAD+58))
        outside = padded.copy()
        outside.paste((0,0,0,0), (filt.PAD,filt.PAD,filt.PAD+208,filt.PAD+58))
        foam, visibility = mask.occlude(unmasked, rock, [258,680], [300,656,428,716])
        member = f'BMP/BACKGRND.BMP/{frame:03}.png'
        raw = filt.png(foam)
        inspect_png(raw, member, (208,58))
        path = out / member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        (out / 'audit').mkdir(exist_ok=True)
        (out / f'audit/{frame:03}-unmasked.png').write_bytes(filt.png(unmasked))
        composition = base.copy()
        composition.alpha_composite(foam, (258,680))
        composition.crop((240,620,484,762)).save(out / f'audit/{frame:03}-rock-closeup.png', compress_level=9)
        record = json.loads((HERE / f'generation-{frame:03}-v1.json').read_bytes())
        rows.append({'frame':frame, 'source':source_path.relative_to(ROOT).as_posix(),
                     'source_sha256':sha(source_path.read_bytes()), 'png_sha256':sha(raw),
                     'canvas':[208,58], 'world_origin':[258,680],
                     'source_stats':stats(source), 'outside_canvas':stats(outside),
                     'runtime_stats':stats(foam), 'visibility':visibility,
                     'prompt_record_sha256':sha((HERE/f'generation-{frame:03}-v1.json').read_bytes()),
                     'ordered_references':[{'path':p,'sha256':sha((ROOT/p).read_bytes())}
                                           for p in record['referenced_image_paths']]})
    report = {'accepted':False, 'scope':'Rock-ring motion draft. White ripple style reused; ring geometry newly generated.',
              'affine_common_to_all_phases':AFFINE, 'pillow_version':pillow_version,
              'filter_sha256':sha(filter_path.read_bytes()), 'mask_sha256':sha(mask_path.read_bytes()),
              'exporter_sha256':sha(Path(__file__).read_bytes()), 'rock_sha256':sha(rock_path.read_bytes()),
              'operation':'One uniform resample, fixed canvas crop, existing rock-alpha visibility mask. No RGB painting or alpha thresholding.',
              'limit':'Visibility masking keeps offshore foam off the rock. It is not exact translucent rock-over-foam compositing.',
              'frames':rows}
    (out / 'export.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps([{'frame':r['frame'],'cropped':r['outside_canvas'],'runtime':r['runtime_stats']} for r in rows]))


if __name__ == '__main__':
    main()
