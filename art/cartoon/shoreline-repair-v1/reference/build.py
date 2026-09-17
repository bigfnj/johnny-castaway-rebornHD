"""Create exact nearest-scaled references; no paint, masking, or asset export."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCTION_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
SOURCE = ROOT / 'art/cartoon/character-inventory-v1/reference-originals.zip'
PRODUCTION = ROOT / 'assets/scrantic_data.zip'
CAPTURE = ROOT / 'build/seasonal-v1/island-footprint/native/cartoon/high/none/final.png'
CAPTURE_SUMMARY = ROOT / 'art/cartoon/seasonal-v1/island-footprint-v1/native-summary.json'
FRAMES = {3: ((540, 612), (144, 58)), 7: ((728, 638), (320, 50)), 9: ((1036, 606), (144, 64))}
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def verify(canvas, source, scale, offset, label):
    wanted = source.resize((source.width * scale, source.height * scale), Image.Resampling.NEAREST)
    x, y = offset
    actual = canvas.crop((x, y, x + wanted.width, y + wanted.height))
    assert actual.tobytes() == wanted.tobytes(), label + ':pixel-replication'
    alpha = canvas.getchannel('A')
    alpha.paste(0, (x, y, x + wanted.width, y + wanted.height))
    assert alpha.getbbox() is None, label + ':transparent-padding'

def make(source, name, scale, details):
    offset = ((1536 - source.width * scale) // 2, (1024 - source.height * scale) // 2)
    assert min(offset) >= 0
    canvas = Image.new('RGBA', (1536, 1024))
    canvas.paste(source.resize((source.width * scale, source.height * scale), Image.Resampling.NEAREST), offset)
    verify(canvas, source, scale, offset, name)
    path = HERE / name
    assert not path.exists(), name
    canvas.save(path, compress_level=9)
    row = {'file': name, 'sha256': sha(path.read_bytes()), 'canvas': [1536, 1024],
           'source_canvas': list(source.size), 'source_decoded_rgba_sha256': sha(source.tobytes()),
           'nearest_scale': scale, 'offset_xy': list(offset), **details}
    return row, (canvas, source, scale, offset)

def main():
    assert sha(PRODUCTION.read_bytes()) == PRODUCTION_SHA
    summary = json.loads(CAPTURE_SUMMARY.read_bytes())
    match = [row for row in summary['cases'] if row['kind'] == 'cartoon' and row['low_tide'] == 0 and row['holiday'] == 0]
    assert len(match) == 1 and sha(CAPTURE.read_bytes()) == match[0]['png_sha256']
    scene = Image.open(CAPTURE).convert('RGBA')
    rows = []
    with zipfile.ZipFile(SOURCE) as original, zipfile.ZipFile(PRODUCTION) as production:
        for frame, (origin, size) in FRAMES.items():
            sources = [('original-native', original, f'native/BMP/BACKGRND.BMP/{frame:03}.png', 8),
                       ('original-hd', production, f'data/hd/BMP/BACKGRND.BMP/{frame:03}.png', 4),
                       ('cartoon', production, f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png', 4)]
            for label, archive, member, scale in sources:
                raw = archive.read(member)
                source = Image.open(io.BytesIO(raw)).convert('RGBA')
                assert source.size == (tuple(v // 2 for v in size) if label == 'original-native' else size)
                row, witness = make(source, f'{frame:03}-{label}-geometry.png', scale,
                                    {'frame': frame, 'member': member, 'source_png_sha256': sha(raw),
                                     'runtime_canvas': list(size), 'scene_origin_hd': list(origin),
                                     'role': 'geometry' if label.startswith('original') else 'current foam style only; missing sand is the defect'})
                row['guide_to_runtime_affine'] = [0.25, 0, -row['offset_xy'][0] / 4, 0, 0.25, -row['offset_xy'][1] / 4]
                rows.append(row)
            x, y = origin
            w, h = size
            box = (x - 32, y - 32, x + w + 32, y + h + 32)
            crop = scene.crop(box)
            row, _ = make(crop, f'{frame:03}-cartoon-scene-context.png', 4,
                          {'frame': frame, 'role': 'native scene style context only; captured wave phases uninstrumented',
                           'source_capture_sha256': sha(CAPTURE.read_bytes()), 'scene_crop_xyxy': list(box),
                           'scene_origin_hd': list(origin), 'runtime_canvas': list(size)})
            rows.append(row)
    # Execute two focused witnesses against this exact embedding check.
    canvas, source, scale, offset = witness
    controls = []
    for name, point, expected in [('changed-source-pixel', offset, ':pixel-replication'),
                                  ('opaque-padding', (0, 0), ':transparent-padding')]:
        mutant = canvas.copy()
        rgba = mutant.getpixel(point)
        mutant.putpixel(point, ((rgba[0] + 1) % 256, rgba[1], rgba[2], 255))
        try:
            verify(mutant, source, scale, offset, name)
        except AssertionError as exc:
            assert str(exc) == name + expected
            controls.append({'name': name, 'status': 'FIRED', 'witness': str(exc)})
        else:
            raise AssertionError(name + ':survived')
    verify(canvas, source, scale, offset, 'restored-positive')
    record = {'schema_version': 1, 'source_archive_sha256': sha(SOURCE.read_bytes()),
              'production_archive_sha256': PRODUCTION_SHA, 'capture_summary_sha256': sha(CAPTURE_SUMMARY.read_bytes()),
              'helper_sha256': sha(Path(__file__).read_bytes()), 'guides': rows,
              'checks': {'exact_embeddings': len(rows), 'negative_controls': controls, 'restored_positive': 'PASS'},
              'limitations': 'Source colors are port diagnostic/HD colors, not original-executable palette. No material masking, recolor, artistic change or production export. Scene context is one captured state, not the exact labeled frame phase.'}
    (HERE / 'source.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'guides': len(rows), 'negative_controls': len(controls),
                      'source_json_sha256': sha((HERE / 'source.json').read_bytes())}))

if __name__ == '__main__':
    main()
