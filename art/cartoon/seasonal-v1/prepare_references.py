"""Extract fixed HOLIDAY000-003 original/HD references without changing art."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INDEX = 'art/cartoon/character-inventory-v1/source/frame-index.json'
ORIGINALS = 'art/cartoon/character-inventory-v1/reference-originals.zip'
PRODUCTION = 'assets/scrantic_data.zip'
PINS = {
    INDEX: '04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2',
    ORIGINALS: 'b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912',
    PRODUCTION: '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be',
}
CANVASES = {0: [40, 34], 1: [120, 47], 2: [56, 65], 3: [152, 47]}
LABELS = {0: 'Pumpkin', 1: 'Clovers', 2: 'Christmas tree', 3: 'New Year banner'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def png(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def rgba(data):
    with Image.open(io.BytesIO(data)) as image:
        return image.convert('RGBA')


def display_hd(image):
    """Apply the existing opaque-magenta HD key only to reference display copies."""
    image = image.copy()
    image.putdata([(r, g, b, 0 if (r, g, b, a) == (168, 0, 168, 255) else a)
                   for r, g, b, a in image.get_flattened_data()])
    return image


def prepare(originals_path, production_path):
    paths = {INDEX: ROOT / INDEX, ORIGINALS: originals_path, PRODUCTION: production_path}
    for name, path in paths.items():
        require(sha(path.read_bytes()) == PINS[name], name + ': source identity differs')
    index = json.loads(paths[INDEX].read_bytes())
    rows = [r for r in index['frames'] if r['resource'] == 'HOLIDAY.BMP']
    require([r['frame'] for r in rows] == [0, 1, 2, 3], 'HOLIDAY.BMP: frame coverage differs')
    outputs, records = {}, []
    sheet = Image.new('RGB', (1536, 1264), (232, 231, 222))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 12), 'HOLIDAY.BMP: supplied-original geometry (left) and current HD (right)', fill=(20, 28, 36))
    draw.text((16, 32), 'Original colors use the port diagnostic palette. Native canvases and exact PNGs remain separate.', fill=(20, 28, 36))
    with zipfile.ZipFile(originals_path) as original_zip, zipfile.ZipFile(production_path) as hd_zip:
        for row in rows:
            frame = row['frame']
            label = f'{frame:03}'
            native_raw = original_zip.read(row['path'])
            hd_raw = hd_zip.read(row['bundled']['hd_member'])
            require(sha(native_raw) == row['png_sha256'], label + ': original member identity differs')
            require(sha(hd_raw) == row['bundled']['hd_png_sha256'], label + ': HD member identity differs')
            native, hd = rgba(native_raw), rgba(hd_raw)
            require(list(native.size) == row['canvas'] == CANVASES[frame], label + ': original canvas differs')
            require(sha(native.tobytes()) == row['rgba_sha256'], label + ': original RGBA differs')
            require(hd.size == (native.width * 2, native.height * 2), label + ': HD canvas differs from2x original')
            enlarged = native.resize((native.width * 8, native.height * 8), Image.Resampling.NEAREST)
            guide_canvas = (1024, 1024) if frame in (0, 2) else (1536, 1024)
            offset = ((guide_canvas[0] - enlarged.width) // 2, (guide_canvas[1] - enlarged.height) // 2)
            original_guide = Image.new('RGBA', guide_canvas, (0, 0, 0, 0))
            original_guide.paste(enlarged, offset)
            hd_display = display_hd(hd)
            hd_enlarged = hd_display.resize(enlarged.size, Image.Resampling.NEAREST)
            hd_guide = Image.new('RGBA', guide_canvas, (0, 0, 0, 0))
            hd_guide.paste(hd_enlarged, offset)
            files = {
                f'{label}-original-native.png': native_raw,
                f'{label}-original-nearest8.png': png(enlarged),
                f'{label}-original-guide.png': png(original_guide),
                f'{label}-hd-native.png': hd_raw,
                f'{label}-hd-guide.png': png(hd_guide),
            }
            outputs.update(files)
            # Matched physical scale: native x4 and HD x2. Large originals
            # remain on their full canvases, without individual silhouette fit.
            for col, visual in enumerate((native, hd_display)):
                factor = 4 if col == 0 else 2
                shown = visual.resize((visual.width * factor, visual.height * factor), Image.Resampling.NEAREST)
                x, y = col * 768 + 16, 64 + frame * 300
                draw.text((x, y), f'{label} {LABELS[frame]} | ' + ('original x4' if col == 0 else 'HD x2'), fill=(20, 28, 36))
                sheet.paste(shown, (x, y + 24), shown)
            records.append({
                'frame': frame, 'path': row['bundled']['path'], 'label': LABELS[frame],
                'native_canvas': list(native.size), 'runtime_canvas': list(hd.size),
                'original_member': row['path'], 'original_png_sha256': sha(native_raw),
                'original_rgba_sha256': sha(native.tobytes()), 'original_index_plane_sha256': row['index_plane_sha256'],
                'original_xpm_sha256': row['xpm_sha256'], 'hd_member': row['bundled']['hd_member'],
                'hd_png_sha256': sha(hd_raw), 'hd_rgba_sha256': sha(hd.tobytes()),
                'guide': {'canvas': list(guide_canvas), 'original_integer_scale': 8, 'hd_integer_scale': 4,
                          'offset': list(offset), 'registration': 'source pixel edges map to offset +8*[x,y]',
                          'hd_display_only_key': 'opaque RGB168,0,168 becomes alpha0; saved hd-native PNG is byte-exact'},
                'files_sha256': {name: sha(raw) for name, raw in files.items()},
            })
    outputs['original-vs-hd-contact.png'] = png(sheet)
    manifest = {
        'schema_version': 1, 'resource': 'HOLIDAY.BMP', 'frame_count': 4,
        'scope': 'Exact original and current HD references; no artwork generation or approval.',
        'palette': 'Original index planes use the port diagnostic dump palette, not calibrated original executable colors. HD is separate appearance guidance.',
        'pillow_version': PILLOW_VERSION, 'prepare_sha256': sha(Path(__file__).read_bytes()),
        'inputs_sha256': PINS, 'frames': records,
        'contact_sheet': {'path': 'original-vs-hd-contact.png', 'sha256': sha(outputs['original-vs-hd-contact.png']),
                          'original_scale': 4, 'hd_scale': 2, 'background_rgb': [232, 231, 222]},
    }
    outputs['source.json'] = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    return outputs, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--originals', type=Path, default=ROOT / ORIGINALS)
    parser.add_argument('--production', type=Path, default=ROOT / PRODUCTION)
    parser.add_argument('--output', type=Path, default=HERE / 'reference')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS seasonal-reference ' + sha(Path(__file__).read_bytes()))
    try:
        outputs, manifest = prepare(args.originals, args.production)
        if not args.check:
            require(not args.output.exists(), 'reference output: refusing to overwrite')
            args.output.mkdir(parents=True)
        for name, data in outputs.items():
            target = args.output / name
            if args.check:
                require(target.read_bytes() == data, name + ': reproduced bytes differ')
            else:
                target.write_bytes(data)
        print('PASS seasonal-reference ' + json.dumps({'frames': len(manifest['frames']), 'files': len(outputs), 'check': args.check}))
        return 0
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('FAIL ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
