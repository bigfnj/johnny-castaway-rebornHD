"""Export every supplied-original BMP/SCR frame from the pinned native dump.

Only local review PNGs and derived provenance are emitted. Original binaries,
historical references and the production archive are never modified.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import source_catalog
from art_review_metadata import original_canvas, text_fingerprint, xpm_facts
from inventory_scenes import resource_catalog

PAIR = {
    'RESOURCE.MAP': '3d9ec330aab96bbe5a44ce34f5945703862e82b195088590b7adfef5d7345da7',
    'RESOURCE.001': 'df9c2213f7c0abacf4e302cb53a476f9f220579c07ba350b167e351eed548eae',
}
DUMP_REPORT = '1983679cff95f0abfd00d21451c46d905506c44ef7edad66f0accead749fcc73'
DUMP_ENGINE = '6ac61dc53dc926a311d89fcf2e27ff7cefbbac7f4c60e2491f69114230400865'
PALETTE_LIMIT = ('Supplied-original index planes rendered with the port diagnostic dump palette. '
                 'BMP index0 is transparent; all SCR indices are opaque. Original executable '
                 'palette, compositing, timing and exhaustive scene parity are not established. '
                 'Shadow-inclusive bounds are not anatomical or foot-contact measurements.')
TOOL_PATHS = ['tools/art_common.py', 'tools/art_review_metadata.py', 'tools/inventory_scenes.py']
SMOKE_IDS = ['BMP/JOHNWALK.BMP/018', 'BMP/SA_DEMO.BMP/000',
             'BMP/ENDCRDTS.BMP/000', 'SCR/INTRO.SCR']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def dump_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def read_inputs(dump_root, original_root, archive_path):
    report_bytes = (dump_root / 'report.json').read_bytes()
    require(sha(report_bytes) == DUMP_REPORT, 'report.json: original dump report identity')
    report = json.loads(report_bytes)
    require(report['input_sha256'] == PAIR and report['engine_sha256'] == DUMP_ENGINE
            and report['exit_code'] == 0, 'report.json: original dump provenance')
    pair = {name: (original_root / name).read_bytes() for name in PAIR}
    for name, data in pair.items():
        require(sha(data) == PAIR[name], name + ': supplied-original input identity')
    _, original = resource_catalog(pair['RESOURCE.MAP'], pair['RESOURCE.001'])
    with zipfile.ZipFile(archive_path) as archive:
        hd = source_catalog(archive)
        _, bundled = resource_catalog(archive.read('data/RESOURCE.MAP'), archive.read('data/RESOURCE.001'))
    frame_specs, resources = [], []
    for name, resource in sorted(original.items()):
        if resource['type'] not in ('BMP', 'SCR'):
            continue
        sprite = resource['type'] == 'BMP'
        # Maintained header reader determines each original canvas/count.
        original_canvas(resource, 0 if sprite else None)
        count = resource['image_count'] if sprite else 1
        counterpart = bundled.get(name)
        if counterpart:
            original_canvas(counterpart, 0 if sprite else None)
        resources.append({'resource': name, 'kind': 'sprite' if sprite else 'screen',
                          'original_frame_count': count, 'original_payload_sha256': resource['payload_sha256'],
                          'bundled_frame_count': (counterpart['image_count'] if sprite else 1) if counterpart else 0,
                          'bundled_payload_sha256': counterpart['payload_sha256'] if counterpart else None})
        for frame in range(count):
            relative = f'BMP/{name}/{frame:03}.png' if sprite else f'SCR/{name}.png'
            xpm = f'BMP/{name}.{frame:03}.xpm' if sprite else f'SCR/{name}.xpm'
            require(xpm in report['dump_sha256'], xpm + ': missing from original dump manifest')
            proxy = hd.get(relative)
            canvas = original_canvas(resource, frame if sprite else None)
            if proxy:
                require(canvas == [proxy['logical_width'], proxy['logical_height']], xpm + ': bundled canvas mapping differs')
            frame_specs.append({'id': relative[:-4], 'kind': 'sprite' if sprite else 'screen',
                                'resource': name, 'frame': frame if sprite else None,
                                'canvas': canvas, 'path': 'native/' + relative, 'xpm_member': xpm,
                                'xpm_sha256': report['dump_sha256'][xpm],
                                'bundled': {'path': relative, 'hd_member': proxy['source_member'],
                                            'hd_png_sha256': proxy['source_sha256'], 'canvas': canvas} if proxy else None})
    expected_xpms = {row['xpm_member'] for row in frame_specs}
    declared_xpms = {name for name in report['dump_sha256'] if name.endswith('.xpm')}
    actual_xpms = {path.relative_to(dump_root / 'dump').as_posix() for path in (dump_root / 'dump').rglob('*.xpm')}
    require(expected_xpms == declared_xpms == actual_xpms, 'original dump: complete BMP/SCR frame set differs')
    require({row['bundled']['path'] for row in frame_specs if row['bundled']} == set(hd),
            'bundled mapping: an HD inventory slot lacks original reference')
    require(len(frame_specs) == 2402 and sum(row['kind'] == 'sprite' for row in frame_specs) == 2392,
            'original inventory: expected 2392 BMP frames and 10 screens')
    for name, expected in report['dump_sha256'].items():
        require(sha((dump_root / 'dump' / name).read_bytes()) == expected, name + ': original dump bytes differ')
    require(len(report['dump_sha256']) == report['files'] == 2453, 'report.json: complete dump file count')
    return frame_specs, resources, report


def image_from_xpm(raw, row):
    # xpm_facts owns semantic parsing/validation. This separate construction is
    # checked against its RGBA digest, so conversion cannot silently drop rows.
    facts = xpm_facts(raw, row['xpm_member'], row['kind'] == 'sprite')
    require(facts['canvas'] == row['canvas'], row['xpm_member'] + ': original header canvas differs')
    strings = re.findall(r'^"([^"\\]*)"(?:,|\};?)?\r?$', raw.decode('ascii'), re.M)
    palette = {line[0]: bytes.fromhex(line[5:]) for line in strings[1:17]}
    lookup = {key: bytes(4) if row['kind'] == 'sprite' and key == '0' else rgb + b'\xff'
              for key, rgb in palette.items()}
    rgba = b''.join(lookup[key] for scanline in strings[17:] for key in scanline)
    require(sha(rgba) == facts['rgba_sha256'], row['xpm_member'] + ': conversion RGBA differs')
    return Image.frombytes('RGBA', tuple(row['canvas']), rgba), facts


def prepare(dump_root, original_root, archive_path, output):
    require(not output.exists(), str(output) + ': refusing to overwrite existing extraction')
    require(PIL.__version__ == '12.3.0', 'Pillow: byte reproduction requires 12.3.0')
    specs, resources, _ = read_inputs(dump_root, original_root, archive_path)
    rows = []
    for row in specs:
        image, facts = image_from_xpm((dump_root / 'dump' / row['xpm_member']).read_bytes(), row)
        destination = output / row['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination)
        rows.append({**row, 'png_sha256': sha(destination.read_bytes()),
                     'rgba_sha256': facts['rgba_sha256'], 'index_plane_sha256': facts['index_plane_sha256'],
                     'visible_bounds_exclusive': facts['visible_bounds_exclusive'],
                     'transparent_index': facts['transparent_index']})
    index = {'schema_version': 1, 'status': 'original-only visual inventory; no semantic Johnny classification or art approval',
             'palette_limit': PALETTE_LIMIT, 'original_executable_color_parity': False,
             'source': {'resource_sha256': PAIR, 'dump_report_sha256': DUMP_REPORT,
                        'historical_dump_engine_sha256': DUMP_ENGINE,
                        'method': 'Reused all 2453 exact-hash-verified native dump outputs; no original executable or decompressor rerun.',
                        'bundled_archive_sha256': sha(archive_path.read_bytes()),
                        'prepare_lf_utf8_sha256': text_fingerprint(Path(__file__).read_bytes()),
                        'maintained_tools_lf_utf8_sha256': {name: text_fingerprint((ROOT / name).read_bytes()) for name in TOOL_PATHS},
                        'pillow_version': PIL.__version__},
             'counts': {'original_resources': len(resources), 'bmp_resources': sum(r['kind'] == 'sprite' for r in resources),
                        'screen_resources': sum(r['kind'] == 'screen' for r in resources),
                        'original_frames': len(rows), 'original_bmp_frames': sum(r['kind'] == 'sprite' for r in rows),
                        'original_screens': sum(r['kind'] == 'screen' for r in rows),
                        'bundled_slots': sum(r['bundled'] is not None for r in rows),
                        'bundled_bmp_slots': sum(r['bundled'] is not None and r['kind'] == 'sprite' for r in rows),
                        'original_only_frames': [r['id'] for r in rows if r['bundled'] is None]},
             'resources': resources, 'frames': rows}
    dump_json(output / 'index.json', index)
    return index['counts']


def check(dump_root, original_root, archive_path, output, phase):
    specs, resources, _ = read_inputs(dump_root, original_root, archive_path)
    index = json.loads((output / 'index.json').read_bytes())
    require(index['palette_limit'] == PALETTE_LIMIT and index['original_executable_color_parity'] is False,
            'index.json: palette scope differs')
    require(index['resources'] == resources, 'index.json: resource completeness/mapping differs')
    require(index['source']['resource_sha256'] == PAIR and index['source']['dump_report_sha256'] == DUMP_REPORT
            and index['source']['bundled_archive_sha256'] == sha(archive_path.read_bytes()), 'index.json: source bindings differ')
    rows = {row['id']: row for row in index['frames']}
    require(len(rows) == len(index['frames']) == len(specs), 'index.json: missing or duplicate frame rows')
    selected = specs if phase == 'regression' else [s for s in specs if s['id'] in SMOKE_IDS]
    require(phase == 'regression' or len(selected) == len(SMOKE_IDS), 'smoke: fixture scope differs')
    for spec in selected:
        row = rows[spec['id']]
        require(all(row[k] == v for k, v in spec.items()), spec['id'] + ': frame/source mapping differs')
        raw = (dump_root / 'dump' / spec['xpm_member']).read_bytes()
        facts = xpm_facts(raw, spec['xpm_member'], spec['kind'] == 'sprite')
        path = output / row['path']
        with Image.open(path) as opened:
            require(opened.mode == 'RGBA' and list(opened.size) == spec['canvas'], row['path'] + ': PNG mode/canvas differs')
            require(sha(opened.tobytes()) == facts['rgba_sha256'], row['path'] + ': original RGBA pixel identity differs')
        require(sha(path.read_bytes()) == row['png_sha256'], row['path'] + ': PNG file identity differs')
        for key in ('rgba_sha256', 'index_plane_sha256', 'visible_bounds_exclusive', 'transparent_index'):
            require(row[key] == facts[key], row['path'] + ': recorded original facts differ')
    if phase == 'regression':
        actual = {p.relative_to(output).as_posix() for p in (output / 'native').rglob('*.png')}
        require(actual == {s['path'] for s in specs}, 'native/: complete PNG set differs')
        historic = json.loads((ROOT / 'art/cartoon/walk-expansion-v1/reference/metadata.json').read_bytes())
        for fact in historic['frames']:
            row = rows[f"BMP/JOHNWALK.BMP/{fact['frame']:03}"]
            require(row['rgba_sha256'] == fact['rgba_sha256'], row['id'] + ': historical original RGBA differs')
    return {'phase': phase, 'checked_frames': len(selected), 'total_frames': len(rows),
            'verified_dump_files': 2453, 'status': 'PASS', 'palette_limit': PALETTE_LIMIT}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump-root', type=Path, required=True)
    parser.add_argument('--original-root', type=Path, required=True)
    parser.add_argument('--archive', type=Path, default=ROOT / 'assets/scrantic_data.zip')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--phase', choices=('prepare', 'smoke', 'regression'), default='prepare')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    print('WITNESS original-inventory ' + text_fingerprint(Path(__file__).read_bytes()), flush=True)
    try:
        result = (prepare(args.dump_root, args.original_root, args.archive, args.output) if args.phase == 'prepare'
                  else check(args.dump_root, args.original_root, args.archive, args.output, args.phase))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1
    if args.report:
        dump_json(args.report, {'schema_version': 1, 'helper_lf_utf8_sha256': text_fingerprint(Path(__file__).read_bytes()),
                                'index_sha256': sha((args.output / 'index.json').read_bytes()), 'result': result})
    print('PASS ' + json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
