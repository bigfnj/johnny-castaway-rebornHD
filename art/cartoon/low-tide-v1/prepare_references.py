"""Build unpainted low-tide geometry/style references from pinned archive pixels."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'reference'
PRODUCTION_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
ORIGINS = {0: (288, 279), 1: (249, 303), 2: (150, 328),
           30: (233, 323), 33: (367, 356), 36: (558, 323), 39: (129, 340)}
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    reference = ROOT / 'art/cartoon/character-inventory-v1/reference-originals.zip'
    production = ROOT / 'assets/scrantic_data.zip'
    assert sha(production.read_bytes()) == PRODUCTION_SHA
    rows = []
    with zipfile.ZipFile(reference) as originals, zipfile.ZipFile(production) as current:
        def read(z, member):
            raw = z.read(member)
            im = Image.open(io.BytesIO(raw)).convert('RGBA')
            rows.append({'member': member, 'sha256': sha(raw), 'size': list(im.size),
                         'alpha_bbox': im.getchannel('A').getbbox()})
            return im

        original = {i: read(originals, f'native/BMP/BACKGRND.BMP/{i:03d}.png')
                    for i in [0, 1, 2, *range(30, 42)]}
        for i, im in original.items():
            im.save(OUT / f'original-{i:03d}.png', compress_level=9)
        accepted = read(current, 'data/styles/cartoon/BMP/BACKGRND.BMP/000.png')
        accepted.save(OUT / 'approved-upper-island.png', compress_level=9)
        for name, im, scale, offset in [
            ('original-shore-guide.png', original[1], 3, (192, 400)),
            ('original-rock-guide.png', original[2], 12, (384, 332)),
            ('approved-island-style-guide.png', accepted, 2, (128, 300)),
        ]:
            guide = Image.new('RGBA', (1536, 1024))
            guide.alpha_composite(im.resize((im.width * scale, im.height * scale),
                                            Image.Resampling.NEAREST), offset)
            guide.save(OUT / name, compress_level=9)
        for label in ['original', 'current-cartoon']:
            for waves in [False, True]:
                world = Image.new('RGBA', (1280, 960))
                for i in ([0, 1, 2, 30, 33, 36, 39] if waves else [0, 1, 2]):
                    x, y = ORIGINS[i]
                    pos = (x * 2, y * 2)
                    if label == 'original':
                        im = original[i].resize((original[i].width * 2, original[i].height * 2),
                                                Image.Resampling.NEAREST)
                    elif i == 0:
                        im = accepted
                        pos = (pos[0] - 36, pos[1] - 10)
                    else:
                        im = read(current, f'data/hd/BMP/BACKGRND.BMP/{i:03d}.png')
                        # HD uses magenta color-keying; this technical reference applies it exactly.
                        im.putdata([(r, g, b, 0 if (r, g, b) == (255, 0, 255) else a)
                                    for r, g, b, a in im.getdata()])
                    world.alpha_composite(im, pos)
                world.save(OUT / f'{label}-{"waves" if waves else "static"}-world.png', compress_level=9)
                world.crop((240, 536, 1280, 784)).save(
                    OUT / f'{label}-{"waves" if waves else "static"}-crop.png', compress_level=9)
    report = {'role': 'Unpainted geometry/style references; not a native capture or approved draft.',
              'production_sha256': PRODUCTION_SHA,
              'original_archive_sha256': sha(reference.read_bytes()),
              'pillow_version': pillow_version, 'helper_sha256': sha(Path(__file__).read_bytes()),
              'origins_logical': ORIGINS, 'source_members': rows,
              'reference_order': 'original geometry first; approved upper island style second',
              'guide_mapping': {'shore': {'scale_original': 3, 'offset': [192,400]},
                                'rock': {'scale_original': 12, 'offset': [384,332]},
                                'style': {'scale_runtime': 2, 'offset': [128,300]}},
              'limitations': 'Originals use diagnostic colors, not original-executable palette. '
                             'No tree, shadow, ocean, props or Johnny. Wave view is first-phase '
                             'source composition in initial low-tide draw order, not native stamping history.',
              'files_sha256': {p.name: sha(p.read_bytes()) for p in sorted(OUT.glob('*.png'))}}
    (OUT / 'source.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps({'references': len(report['files_sha256']), 'path': str(OUT)}))

if __name__ == '__main__':
    main()
