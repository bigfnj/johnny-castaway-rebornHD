"""Fixed technical exports for the two static low-tide review drafts."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile
from PIL import Image, __version__ as pillow_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import inspect_png
from art_pack import build_archive

sha = lambda raw: hashlib.sha256(raw).hexdigest()
BASE_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
CONFIG = {
    1: {'source': 'shore-raw-v3.png', 'canvas': [768,138], 'scale': .525,
        'raw_anchor': [778.5,647], 'target_anchor': [384,137.5],
        'basis': 'V3 redrew at a wider raw scale despite requested padding. Uniform scale restores original shore span at horizontal center and bottom waterline. Raised upper lip fills joins; no contour, alpha or color paint in code.'},
    2: {'source': 'rock-raw-v2.png', 'canvas': [128,60], 'scale': .164,
        'raw_anchor': [756.5,717], 'target_anchor': [64,59.4],
        'basis': 'Rock horizontal midpoint and bottom contact; scale stays within two percent of original guide mapping1/6, retaining full silhouette.'},
}

def save_json(path, data):
    path.write_bytes((json.dumps(data, indent=2) + '\n').encode())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    helper = ROOT / 'art/cartoon/seasonal-v1/export.py'
    spec = importlib.util.spec_from_file_location('fixed_seasonal_filter', helper)
    filt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(filt)
    archive = ROOT / 'assets/scrantic_data.zip'
    assert sha(archive.read_bytes()) == BASE_SHA, 'production archive identity'
    outputs, rows = {}, []
    for frame, c in CONFIG.items():
        source = Image.open(HERE / c['source']).convert('RGBA')
        s = c['scale']
        affine = [s,0,c['target_anchor'][0]-s*c['raw_anchor'][0],
                  0,s,c['target_anchor'][1]-s*c['raw_anchor'][1]]
        padded = filt.resample(source, c['canvas'], affine)
        w,h = c['canvas']
        exported = padded.crop((filt.PAD,filt.PAD,filt.PAD+w,filt.PAD+h))
        raw = filt.png(exported)
        member = f'BMP/BACKGRND.BMP/{frame:03d}.png'
        inspect_png(raw, member, (w,h))
        outputs[member] = raw
        path = out / member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        outside = padded.getchannel('A').copy()
        outside.paste(0, (filt.PAD,filt.PAD,filt.PAD+w,filt.PAD+h))
        histogram = outside.histogram()
        rows.append({**c, 'frame': frame, 'path': member, 'affine_forward': affine,
                     'source_sha256': sha((HERE/c['source']).read_bytes()),
                     'png_sha256': sha(raw), 'alpha_extrema': source.getchannel('A').getextrema(),
                     'alpha8_bounds_source': source.getchannel('A').point(lambda a: 255 if a>=8 else 0).getbbox(),
                     'outside_canvas_max_alpha': outside.getextrema()[1],
                     'outside_canvas_alpha8_pixels': sum(histogram[8:]),
                     'outside_canvas_nonzero_pixels': sum(histogram[1:])})
    with zipfile.ZipFile(archive) as z:
        packed = {n.removeprefix('data/styles/cartoon/'): z.read(n) for n in z.namelist()
                  if n.startswith('data/styles/cartoon/') and n.endswith('.png')}
        packed.update(outputs)
        runtime = json.loads(z.read('data/styles/cartoon/manifest.json'))
        # This is an explicitly unapproved private package, not an acceptance ledger.
        build_archive(archive, args.candidate, runtime, packed)
        world = Image.open(io.BytesIO(z.read('data/styles/cartoon/SCR/OCEAN02.SCR.png'))).convert('RGBA')
        for frame, pos in [(0,(540,548)),(13,(884,296)),(12,(730,244)),(14,(792,558)),
                           (1,(498,606)),(2,(300,656))]:
            name = f'BMP/BACKGRND.BMP/{frame:03d}.png'
            world.alpha_composite(Image.open(io.BytesIO(outputs.get(name,packed.get(name)))).convert('RGBA'),pos)
        world.save(out / 'static-composition.png',compress_level=9)
        world.crop((240,520,1280,784)).save(out/'static-closeup.png',compress_level=9)
        before = {n: sha(z.read(n)) for n in z.namelist()}
    with zipfile.ZipFile(args.candidate) as z:
        after = {n: sha(z.read(n)) for n in z.namelist()}
    differences = sorted(n for n in before.keys() | after.keys() if before.get(n)!=after.get(n))
    save_json(out/'export.json', {'accepted': False, 'source_commit': 'da787d63279ea91bd6c637e02133821339470bfc',
              'scope': 'Two static draft assets; low waves unchanged and human scene review pending.',
              'production_sha256': BASE_SHA, 'candidate_sha256': sha(args.candidate.read_bytes()),
              'pillow_version': pillow_version, 'filter_sha256': sha(helper.read_bytes()),
              'exporter_sha256': sha(Path(__file__).read_bytes()), 'filter': filt.FILTERS,
              'frames': rows, 'changed_members': differences,
              'composition_limit': 'Static technical composition at native origins, before waves, clouds and Johnny. Not an application screenshot.'})
    print(json.dumps({'candidate_sha256': sha(args.candidate.read_bytes()), 'changed_members': differences,
                      'exports': [{k:r[k] for k in ['frame','canvas','outside_canvas_max_alpha','outside_canvas_alpha8_pixels']} for r in rows]}))

if __name__ == '__main__':
    main()
