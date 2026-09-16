"""Prepare/check original-only profile001-008 references, never Cartoon art."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
BASE = 'art/cartoon/walk-expansion-v1/reference/'
PINS = {
    'extract.py': '9f2ac986ae7f29c84a672f2a77fd0f2ba75be135a3c2c8666a31a4b34adca5cc',
    'source.json': '040106d15a0c6460a044a7989ddcfea12d494bc6838ee1fad83a3793e2f2cfa4',
    'metadata.json': 'd710eb638f84f7da2dcdfe004cf5e8010125cb9c4c142b8033641d83098dd629',
}
FRAMES = tuple(range(1, 9))
LIMIT = 'Original indices use the port dump palette and index0 transparency. Original executable colors, compositing and timing are not established. Shadow-inclusive bounds are not foot contact or anatomy.'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def load(path):
    return json.loads(path.read_bytes())


def inputs():
    for name, expected in PINS.items():
        require(sha((ROOT / BASE / name).read_bytes()) == expected, name + ': pinned source identity')
    original = load(ROOT / BASE / 'source.json')
    facts = {row['frame']: row for row in load(ROOT / BASE / 'metadata.json')['frames']}
    return original, facts


def registration(fact):
    span = fact['first_row_visible_span_x_exclusive']
    return {'native_canvas': fact['canvas'], 'runtime_canvas': [v * 2 for v in fact['canvas']],
            'native_top_visible_span_x_exclusive': span,
            'native_top_pixel_edge_midpoint_x': sum(span) / 2,
            'suggested_cap_target_hd': [sum(span), 0.25],
            'generated_art_scale_exact': {'numerator': 1, 'denominator': 10},
            'limit': 'X measures the original first opaque row midpoint at2x. Y0.25 is the inherited filter margin. These are authoring observations, not engine/anatomical anchors. Do not normalize the whole body to a common height or shadow bottom.'}


def check(output):
    original, facts = inputs()
    index = load(output / 'source-index.json')
    require(index['frames'] == list(FRAMES), 'source-index.json: frame scope')
    require(index['source_pins'] == {BASE + k: v for k, v in PINS.items()}, 'source-index.json: source pins')
    for frame in FRAMES:
        key = f'{frame:03}'
        record = load(output / (key + '-source.json'))
        fact = facts[frame]
        require(record['original_source_record'] == BASE + 'source.json' and
                record['original_source_record_sha256'] == PINS['source.json'] and
                record['original_metadata_record'] == BASE + 'metadata.json' and
                record['original_metadata_record_sha256'] == PINS['metadata.json'] and
                record['resource_sha256'] == original['resource_sha256'] and
                record['historical_dump_engine_sha256'] == original['dump_engine_sha256'] and
                record['palette_compositing_limit'] == LIMIT and
                record['nearest8'] == {'scale_exact': {'numerator': 8, 'denominator': 1}, 'filter': 'NEAREST'} and
                record['status'] == 'ORIGINAL-ONLY PREPARATION; no generated art or artistic approval',
                key + '-source.json: provenance/limit differs')
        require(record['original_frame'] == fact, key + '-source.json: original fact row differs')
        require(record['registration'] == registration(fact), key + '-source.json: registration differs')
        native_path = output / (key + '-original-native.png')
        nearest_path = output / (key + '-original-nearest8.png')
        with Image.open(native_path) as opened:
            require(opened.mode == 'RGBA' and list(opened.size) == fact['canvas'], key + '-original-native.png: canvas/mode')
            native = opened.copy()
        require(sha(native.tobytes()) == fact['rgba_sha256'], key + '-original-native.png: original RGBA differs')
        with Image.open(nearest_path) as opened:
            require(opened.mode == 'RGBA' and opened.size == (native.width * 8, native.height * 8), key + '-original-nearest8.png: canvas/mode')
            enlarged = opened.tobytes()
        # Independent byte replication, not the resize operation used to write.
        rgba = native.tobytes()
        expanded = b''.join(b''.join(rgba[(y * native.width + x) * 4:(y * native.width + x + 1) * 4] * 8
                                      for x in range(native.width)) * 8 for y in range(native.height))
        require(enlarged == expanded, key + '-original-nearest8.png: exact8 pixel replication differs')
        top = [x for x in range(native.width) if native.getpixel((x, 0))[3]]
        require([min(top), max(top) + 1] == fact['first_row_visible_span_x_exclusive'], key + ': original cap extent differs')
        for path in (native_path, nearest_path):
            require(sha(path.read_bytes()) == record['files_sha256'][path.name], path.name + ': file identity')
        require(sha((output / (key + '-source.json')).read_bytes()) == index['record_sha256'][key + '-source.json'], key + '-source.json: index identity')
    return {'frames': 8, 'native_pngs': 8, 'exact_nearest8_pngs': 8, 'original_facts_unchanged': True}


def prepare(dump_root, output):
    require(not output.exists(), 'output: must be a fresh directory')
    require(PIL.__version__ == '12.3.0', 'Pillow: byte reproduction requires12.3.0')
    original, facts = inputs()
    spec = importlib.util.spec_from_file_location('profile_original_extractor', ROOT / BASE / 'extract.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    images, metadata = module.prepare(dump_root, (ROOT / 'src/data/walk_data.h').read_bytes(), original)
    require(metadata == load(ROOT / BASE / 'metadata.json'), 'metadata.json: reconstructed facts differ')
    output.mkdir(parents=True)
    records = {}
    for frame in FRAMES:
        key = f'{frame:03}'
        native_path = output / (key + '-original-native.png')
        nearest_path = output / (key + '-original-nearest8.png')
        im = images[frame]
        im.save(native_path)
        im.resize((im.width * 8, im.height * 8), Image.Resampling.NEAREST).save(nearest_path)
        record = {'schema_version': 1, 'status': 'ORIGINAL-ONLY PREPARATION; no generated art or artistic approval',
                  'original_frame': facts[frame], 'original_source_record': BASE + 'source.json',
                  'original_source_record_sha256': PINS['source.json'],
                  'original_metadata_record': BASE + 'metadata.json', 'original_metadata_record_sha256': PINS['metadata.json'],
                  'resource_sha256': original['resource_sha256'], 'historical_dump_engine_sha256': original['dump_engine_sha256'],
                  'dump_report_sha256': sha((dump_root / 'report.json').read_bytes()),
                  'scope': 'Reconstructed from all36 validated preserved original XPMs. Commercial RESOURCE inputs and original executable were not reread or rerun.',
                  'palette_compositing_limit': LIMIT, 'nearest8': {'scale_exact': {'numerator': 8, 'denominator': 1}, 'filter': 'NEAREST'},
                  'registration': registration(facts[frame]),
                  'files_sha256': {p.name: sha(p.read_bytes()) for p in (native_path, nearest_path)}}
        path = output / (key + '-source.json')
        path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
        records[path.name] = sha(path.read_bytes())
    index = {'schema_version': 1, 'frames': list(FRAMES), 'source_pins': {BASE + k: v for k, v in PINS.items()},
             'record_sha256': records, 'pillow_version': PIL.__version__, 'palette_compositing_limit': LIMIT}
    (output / 'source-index.json').write_text(json.dumps(index, indent=2) + '\n', encoding='utf-8', newline='\n')
    return check(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump-root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS profile-reference SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    try:
        require(args.check or args.dump_root is not None, 'dump-root: required to prepare')
        result = check(args.output) if args.check else prepare(args.dump_root, args.output)
    except (ValueError, OSError, KeyError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1
    print('PASS ' + json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
