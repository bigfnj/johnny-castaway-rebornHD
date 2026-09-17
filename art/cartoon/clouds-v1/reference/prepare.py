"""Reproduce exact original cloud references and diagnostic nearest-neighbor guides."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INDEX = 'art/cartoon/character-inventory-v1/source/frame-index.json'
ORIGINALS = 'art/cartoon/character-inventory-v1/reference-originals.zip'
PRODUCTION = 'assets/scrantic_data.zip'
PINS = {
    INDEX: '04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2',
    ORIGINALS: 'b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912',
    PRODUCTION: 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66',
}
SELECTION = [('CLOUDS.BMP', n) for n in range(4)] + [('BACKGRND.BMP', 16), ('BACKGRND.BMP', 17)]
SCALES = [6, 12, 14, 20, 6, 5]
STYLE_MEMBER = 'data/styles/cartoon/BMP/BACKGRND.BMP/015.png'
STYLE_SHA = 'd7f6f6608cb18ac169b6e4378cb5c12c30a9139d7925c36e8a02f1c8eea41649'
HELPER = 'art/cartoon/character-inventory-v1/source/prepare.py'
spec = importlib.util.spec_from_file_location('original_reference', ROOT / HELPER)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def text_sha(raw):
    return sha(raw.replace(b'\r\n', b'\n'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def png(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def rgba(raw):
    return Image.open(io.BytesIO(raw)).convert('RGBA')


def display_hd(image):
    result = image.copy()
    result.putdata([(r, g, b, 0 if (r, g, b, a) == (168, 0, 168, 255) else a)
                    for r, g, b, a in image.get_flattened_data()])
    return result


def prepare(args):
    inputs = {INDEX: ROOT / INDEX, ORIGINALS: args.originals, PRODUCTION: args.production}
    for name, path in inputs.items():
        require(sha(path.read_bytes()) == PINS[name], name + ': source identity differs')
    require(PILLOW_VERSION == '12.3.0', 'Pillow: reproduction requires 12.3.0')
    index = json.loads(inputs[INDEX].read_bytes())
    pair = {name: (args.original_root / name).read_bytes() for name in original.PAIR}
    for name, raw in pair.items():
        require(sha(raw) == original.PAIR[name], name + ': supplied-original identity differs')
    report_bytes = (args.dump_root / 'report.json').read_bytes()
    require(sha(report_bytes) == original.DUMP_REPORT, 'report.json: native dump identity differs')
    report = json.loads(report_bytes)
    require(report['input_sha256'] == original.PAIR and report['engine_sha256'] == original.DUMP_ENGINE,
            'report.json: native decoder provenance differs')
    _, resources = original.resource_catalog(pair['RESOURCE.MAP'], pair['RESOURCE.001'])
    outputs, rows = {}, []
    sheet = Image.new('RGB', (1280, 1448), (72, 98, 118))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 12), 'CLOUD REFERENCES | original geometry x2 (left) | existing HD x1 (right)', fill='white')
    draw.text((16, 32), 'Original colors use the port diagnostic palette, not calibrated original executable colors.', fill='white')
    with zipfile.ZipFile(args.originals) as native_zip, zipfile.ZipFile(args.production) as hd_zip:
        _, bundled = original.resource_catalog(hd_zip.read('data/RESOURCE.MAP'), hd_zip.read('data/RESOURCE.001'))
        for resource_name in ('CLOUDS.BMP', 'BACKGRND.BMP'):
            recorded = next(row for row in index['resources'] if row['resource'] == resource_name)
            require(resources[resource_name]['payload_sha256'] == recorded['original_payload_sha256'], resource_name + ': original resource differs')
            require(bundled[resource_name]['payload_sha256'] == recorded['bundled_payload_sha256'], resource_name + ': bundled resource differs')
        for i, ((resource, frame), scale) in enumerate(zip(SELECTION, SCALES)):
            row = next(r for r in index['frames'] if r['resource'] == resource and r['frame'] == frame)
            label = f'{resource.split(".")[0].lower()}-{frame:03}'
            native_raw = native_zip.read(row['path'])
            hd_raw = hd_zip.read(row['bundled']['hd_member'])
            require(sha(native_raw) == row['png_sha256'], label + ': original PNG identity differs')
            require(sha(hd_raw) == row['bundled']['hd_png_sha256'], label + ': HD identity differs')
            xpm = (args.dump_root / 'dump' / row['xpm_member']).read_bytes()
            require(sha(xpm) == row['xpm_sha256'] == report['dump_sha256'][row['xpm_member']], label + ': XPM identity differs')
            decoded, facts = original.image_from_xpm(xpm, row)
            native, hd = rgba(native_raw), rgba(hd_raw)
            require(native.tobytes() == decoded.tobytes(), label + ': decoded original pixels differ')
            require(facts['index_plane_sha256'] == row['index_plane_sha256'], label + ': index plane differs')
            require(list(native.size) == original.original_canvas(resources[resource], frame), label + ': original geometry differs')
            require(hd.size == (native.width * 2, native.height * 2), label + ': HD mapping differs')
            enlarged = native.resize((native.width * scale, native.height * scale), Image.Resampling.NEAREST)
            offset = [(1536 - enlarged.width) // 2, (1024 - enlarged.height) // 2]
            guide = Image.new('RGBA', (1536, 1024))
            guide.paste(enlarged, tuple(offset))
            files = {label + '-original.png': native_raw, label + '-hd.png': hd_raw,
                     label + '-guide.png': png(guide)}
            outputs.update(files)
            for column, image in enumerate((native.resize((native.width * 2, native.height * 2), Image.Resampling.NEAREST), display_hd(hd))):
                x, y = 16 + 640 * column, 64 + 184 * i
                draw.text((x, y), f'{resource}/{frame:03} | ' + ('original x2' if column == 0 else 'HD x1'), fill='white')
                sheet.paste(image, (x, y + 24), image)
            rows.append({**row, 'runtime_canvas': list(hd.size), 'original_alpha_values': sorted(set(native.getchannel('A').get_flattened_data())),
                         'guide': {'canvas': [1536, 1024], 'integer_scale': scale, 'offset': offset,
                                   'registration': 'source pixel edges map to offset + integer_scale * [x,y]'},
                         'files_sha256': {name: sha(data) for name, data in files.items()}})
        style_raw = hd_zip.read(STYLE_MEMBER)
        require(sha(style_raw) == STYLE_SHA, 'BACKGRND015: accepted style identity differs')
        style = rgba(style_raw)
        outputs['backgrnd-015-accepted.png'] = style_raw
        style_big = style.resize((style.width * 4, style.height * 4), Image.Resampling.NEAREST)
        outputs['backgrnd-015-accepted-nearest4.png'] = png(style_big)
        draw.text((16, 1184), 'Accepted Cartoon BACKGRND015 | actual runtime x2 | style context only, not original geometry', fill='white')
        style_shown = style.resize((style.width * 2, style.height * 2), Image.Resampling.NEAREST)
        sheet.paste(style_shown, (16, 1216), style_shown)
    outputs['original-hd-style-contact.png'] = png(sheet)
    manifest = {'schema_version': 1, 'scope': 'Six exact original references, current HD, and accepted015 context; no new art or approval.',
                'palette_limit': index['palette_limit'], 'pillow_version': PILLOW_VERSION,
                'prepare_lf_sha256': text_sha(Path(__file__).read_bytes()), 'inputs_sha256': PINS,
                'supplied_original_pair_sha256': original.PAIR, 'dump_report_sha256': original.DUMP_REPORT,
                'historical_decoder_sha256': original.DUMP_ENGINE,
                'helper_lf_sha256': {p: text_sha((ROOT / p).read_bytes()) for p in [HELPER] + original.TOOL_PATHS},
                'method': 'Verify supplied RESOURCE pair, selected original/bundled resources and six pinned XPMs; byte-copy six archived originals and current HD. No decoder rerun.',
                'frames': rows, 'style': {'member': STYLE_MEMBER, 'sha256': STYLE_SHA, 'runtime_canvas': list(style.size)},
                'guide_note': 'Different integer guide scales are inspection aids, not a proposed runtime transform. Original alpha and all pixel cells are retained.',
                'contact': {'original_scale': 2, 'hd_scale': 1, 'style_scale': 2, 'background_rgb': [72, 98, 118],
                            'hd_display_only_key': 'Opaque RGB168,0,168 keyed to transparent only in contact sheet; saved HD PNGs are untouched.'},
                'files_sha256': {name: sha(data) for name, data in outputs.items()}}
    outputs['source.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--originals', type=Path, default=ROOT / ORIGINALS)
    parser.add_argument('--production', type=Path, default=ROOT / PRODUCTION)
    parser.add_argument('--original-root', type=Path, default=Path('C:/JohnCast/SIERRA/SCRANTIC'))
    parser.add_argument('--dump-root', type=Path, default=Path('D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference'))
    parser.add_argument('--output', type=Path, default=HERE)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS cloud-reference ' + text_sha(Path(__file__).read_bytes()))
    try:
        outputs = prepare(args)
        if not args.check:
            for name in outputs:
                require(not (args.output / name).exists(), name + ': refusing to overwrite')
            args.output.mkdir(parents=True, exist_ok=True)
        for name, raw in outputs.items():
            target = args.output / name
            if args.check:
                require(target.read_bytes() == raw, name + ': replay bytes differ')
            else:
                target.write_bytes(raw)
        print('PASS cloud-reference ' + json.dumps({'frames': 6, 'files': len(outputs), 'check': args.check}))
        return 0
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('FAIL ' + str(exc))
        return 1


if __name__ == '__main__':
    sys.exit(main())
