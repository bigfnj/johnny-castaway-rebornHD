"""Copy exact native captures into a fresh, two-panel scene review."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
CASES = {
    'day/none': ('No decoration', [0,0,0,0,0,0,1]),
    'day/pumpkin': ('Pumpkin', [1,0,0,0,0,0,1]),
    'day/clover': ('Clovers', [2,0,0,0,0,0,1]),
    'day/tree': ('Christmas tree', [3,0,0,0,0,0,1]),
    'day/banner': ('New Year banner', [4,0,0,0,0,0,1]),
    'motion/high_clover': ('High tide with clovers', [2,0,0,0,0,0,20]),
    'motion/low_clover': ('Low tide with clovers', [2,0,0,0,1,0,24]),
    'motion/night_shift_clover': ('Night with clovers', [2,1,-80,20,0,0,20]),
    'motion/johnny_front': ('Johnny: front connection', [0,0,0,0,0,1,1]),
    'motion/johnny_rear': ('Johnny: rear connection', [0,0,0,0,0,2,1]),
}
TIMING = ('ordinal','ticks','time_ms','segment','phases','johnny')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError('scene review: ' + message)


def build(captures, output):
    require(not output.exists(), 'output already exists: ' + str(output))
    inputs = json.loads((captures / 'inputs.json').read_bytes())
    summary = json.loads((captures / 'summary.json').read_bytes())
    require(summary['status'] == 'PASS' and summary['phase'] == 'full', 'completed full native matrix')
    pair = inputs['pair']
    require(pair == summary['package_pair'], 'summary package identity')
    reports, cases, images = {}, {}, {}
    for key, (label, args) in CASES.items():
        require(summary['cases'][key]['smoke'] == 'PASS' and summary['cases'][key]['fresh_repeat'] == 'PASS', key + ' smoke and repeat')
        rows = {}
        for side in ('baseline', 'candidate'):
            path = captures / key / side / 'smoke/report.json'
            report = json.loads(path.read_bytes())
            require(report['status'] == 'PASS' and report['args'] == args, key + '/' + side + ' report case')
            require(report['archive_sha256'] == pair[side + '_sha256'], key + '/' + side + ' archive')
            require(report['executable_sha256'] == json.loads((captures / 'build.json').read_bytes())['executable_sha256'], key + '/' + side + ' executable')
            repeat_path = captures / key / side / 'repeat/report.json'
            repeated = json.loads(repeat_path.read_bytes())
            require(repeated['status'] == 'PASS' and repeated['args'] == args and repeated['archive_sha256'] == report['archive_sha256'] and repeated['displays'] == report['displays'], key + '/' + side + ' exact repeat')
            reports[path.relative_to(ROOT).as_posix()] = sha(path)
            reports[repeat_path.relative_to(ROOT).as_posix()] = sha(repeat_path)
            require(report['displays'] and report['displays'][0]['time_ms'] == 0, key + ' begins at zero')
            require(all(a['time_ms'] <= b['time_ms'] for a, b in zip(report['displays'], report['displays'][1:])), key + ' recorded timing')
            rows[side] = report
            for row in report['displays']:
                source = path.parent / row['file']
                require(source.parent == path.parent and source.suffix == '.png', key + ' local PNG path')
                require(sha(source) == row['png_sha256'], key + '/' + side + '/' + row['file'] + ' PNG identity')
                image = 'images/' + row['png_sha256'] + '.png'
                images[image] = {'source': source.relative_to(ROOT).as_posix(), 'sha256': row['png_sha256']}
        left, right = rows['baseline'], rows['candidate']
        require([[r[k] for k in TIMING] for r in left['displays']] == [[r[k] for k in TIMING] for r in right['displays']], key + ' actual timing and poses differ')
        frames = [{**{k: a[k] for k in TIMING}, 'baseline': 'images/' + a['png_sha256'] + '.png', 'candidate': 'images/' + b['png_sha256'] + '.png'}
                  for a, b in zip(left['displays'], right['displays'])]
        still = key.startswith('day/')
        if still:
            require(len({(r['baseline'], r['candidate']) for r in frames}) == 1, key + ' single still state')
            frames = [frames[0]]
        cases[key] = {'label': label, 'kind': 'still' if still else 'motion', 'args': args,
                      'frames': frames, 'duration_ms': 0 if still else left['duration_ms'],
                      'camera': [510 + args[2] * 2, 220 + args[3] * 2, 700, 610]}
    manifest = {'schema_version': 1, 'default_case': 'day/pumpkin', 'native_canvas': [1280,960],
                'labels': ['Earlier Cartoon', 'Selected offshore waves'],
                'cases': cases, 'images': images, 'reports_sha256': reports,
                'native_inputs': {'path': (captures / 'inputs.json').relative_to(ROOT).as_posix(), 'sha256': sha(captures / 'inputs.json')},
                'native_summary': {'path': (captures / 'summary.json').relative_to(ROOT).as_posix(), 'sha256': sha(captures / 'summary.json')},
                'package_pair': pair,
                'scope': 'Both sides use the same full-size draft decorations. Earlier Cartoon is a private comparison package, not the original artwork or the shipped production package. Actual port capture pixels and logical timing; still cases are not animated. Human seasonal scene review pending.'}
    output.mkdir(parents=True)
    tiles, tile_images = {}, []
    for name, data in images.items():
        with Image.open(ROOT / data['source']) as original:
            full = original.convert('RGBA')
            require(full.size == (1280,960), name + ' native canvas')
            data['rgba_sha256'] = hashlib.sha256(full.tobytes()).hexdigest()
            data['tiles'] = []
            for y in range(0, 960, 64):
                for x in range(0, 1280, 64):
                    crop = full.crop((x,y,x+64,y+64))
                    digest = hashlib.sha256(crop.tobytes()).hexdigest()
                    tile = digest
                    if tile not in tiles:
                        number = len(tiles)
                        tiles[tile] = {'id': number, 'atlas': f'atlas-{number//1024:02}.png',
                                       'x': (number%32)*64, 'y': ((number%1024)//32)*64, 'rgba_sha256': digest}
                        tile_images.append(crop)
                    data['tiles'].append(tiles[tile]['id'])
    manifest['tiles'] = list(tiles.values())
    manifest['tile_size'] = 64
    manifest['atlases'] = {}
    for start in range(0,len(tile_images),1024):
        atlas = Image.new('RGBA',(2048,2048))
        for i,tile in enumerate(tile_images[start:start+1024]):
            atlas.paste(tile,((i%32)*64,(i//32)*64))
        name = f'atlas-{start//1024:02}.png'
        atlas.save(output/name,compress_level=9)
        manifest['atlases'][name] = sha(output/name)
    shutil.copyfile(HERE / 'review-template.html', output / 'review.html')
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    record = {'status': 'BUILT', 'builder_sha256': sha(Path(__file__)), 'template_sha256': sha(HERE / 'review-template.html'),
              'html_sha256': sha(output / 'review.html'), 'manifest_sha256': sha(output / 'manifest.json'),
              'cases': len(cases), 'source_frames': len(images), 'unchanged_rgba_tiles': len(tiles),
              'atlas_bytes': sum((output / name).stat().st_size for name in manifest['atlases']),
              'native_summary_sha256': sha(captures / 'summary.json')}
    (output / 'build.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--captures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    build(a.captures.resolve(), a.output.resolve())
