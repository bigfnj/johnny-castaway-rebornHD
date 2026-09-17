"""Lossless native cloud playback, packed into a few PNG tile atlases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
spec = importlib.util.spec_from_file_location('cloud_capture_for_review', HERE / 'capture.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
CASES = {'day_left': ('Wind to the left', 'Both larger clouds move left with their original placement and speed.'),
         'day_right': ('Wind to the right', 'The same cloud shapes are mirrored by the game as they move right.'),
         'night_shift_right': ('Night', 'Night backdrop is still the existing fallback; this checks cloud edges and brightness.')}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('cloud review: ' + label)


def report_check(report, args, archive, executable):
    require(report['status'] == 'PASS' and report['args'] == args, 'native report case')
    require(report['archive_sha256'] == archive and report['executable_sha256'] == executable, 'native report source')


def reconstruct(data, tiles, atlases):
    full = Image.new('RGB', (1280, 960))
    for j, number in enumerate(data['tiles']):
        t = tiles[number]
        full.paste(atlases[t['atlas']].crop((t['x'], t['y'], t['x'] + 64, t['y'] + 64)), ((j % 20) * 64, (j // 20) * 64))
    require(sha(full.tobytes()) == data['pixels_sha256'], 'exact native reconstruction')


def build(captures, output):
    require(not output.exists(), 'fresh review output')
    summary = json.loads((captures / 'summary.json').read_bytes())
    inputs = json.loads((captures / 'inputs.json').read_bytes())
    compiled = json.loads((captures / 'build.json').read_bytes())
    require(summary['status'] == 'PASS' and summary['baseline_sha256'] == native.BASE_SHA, 'completed native baseline')
    require(summary['inputs_sha256'] == sha((captures / 'inputs.json').read_bytes()) and summary['build_sha256'] == sha((captures / 'build.json').read_bytes()), 'native summary linkage')
    require(summary['candidate_sha256'] == inputs['candidate_sha256'], 'native candidate linkage')
    images, cases, reports = {}, {}, {}
    positive = None
    for case, (label, note) in CASES.items():
        require(summary['cases'][case]['smoke'] == summary['cases'][case]['fresh_repeat'] == 'PASS', case + ' smoke/repeat')
        rows = {}
        for side in ('baseline', 'candidate'):
            path = captures / case / side / 'smoke/report.json'
            report = json.loads(path.read_bytes())
            archive = summary[side + '_sha256']
            report_check(report, native.CASES[case], archive, compiled['executable_sha256'])
            repeated_path = captures / case / side / 'repeat/report.json'
            repeated = json.loads(repeated_path.read_bytes())
            report_check(repeated, native.CASES[case], archive, compiled['executable_sha256'])
            require(repeated['displays'] == report['displays'], 'fresh repeat display identity')
            for p in (path, repeated_path):
                reports[p.relative_to(ROOT).as_posix()] = sha(p.read_bytes())
            rows[side] = report
            positive = (report, native.CASES[case], archive, compiled['executable_sha256'])
            for row in report['displays']:
                source = path.parent / row['file']
                require(source.parent == path.parent and source.suffix == '.png', 'local native PNG')
                require(sha(source.read_bytes()) == row['png_sha256'], 'native PNG bytes')
                images.setdefault(row['pixels_sha256'], {'source': source.relative_to(ROOT).as_posix(), 'png_sha256': row['png_sha256'], 'pixels_sha256': row['pixels_sha256']})
        fields = (*native.c.TIMING, 'clouds')
        require([[r[k] for k in fields] for r in rows['baseline']['displays']] == [[r[k] for k in fields] for r in rows['candidate']['displays']], 'paired native timeline')
        cases[case] = {'label': label, 'note': note, 'duration_ms': rows['candidate']['duration_ms'],
            'frames': [{'time_ms': a['time_ms'], 'baseline': a['pixels_sha256'], 'candidate': b['pixels_sha256']}
                       for a, b in zip(rows['baseline']['displays'], rows['candidate']['displays'])]}
    output.mkdir(parents=True)
    tiles, tile_images = {}, []
    for data in images.values():
        full = Image.open(ROOT / data['source']).convert('RGB')
        require(full.size == (1280, 960) and sha(full.tobytes()) == data['pixels_sha256'], 'decoded native pixels')
        data['tiles'] = []
        for y in range(0, 960, 64):
            for x in range(0, 1280, 64):
                crop = full.crop((x, y, x + 64, y + 64))
                digest = sha(crop.tobytes())
                if digest not in tiles:
                    n = len(tiles)
                    tiles[digest] = {'id': n, 'atlas': f'atlas-{n // 1024:02}.png',
                                     'x': (n % 32) * 64, 'y': ((n % 1024) // 32) * 64, 'pixels_sha256': digest}
                    tile_images.append(crop)
                data['tiles'].append(tiles[digest]['id'])
    atlas_hashes, opened = {}, {}
    for start in range(0, len(tile_images), 1024):
        image = Image.new('RGB', (2048, 2048))
        for i, tile in enumerate(tile_images[start:start + 1024]):
            image.paste(tile, ((i % 32) * 64, (i // 32) * 64))
        name = f'atlas-{start // 1024:02}.png'
        image.save(output / name, compress_level=9)
        atlas_hashes[name] = sha((output / name).read_bytes())
        opened[name] = Image.open(output / name).convert('RGB')
    tile_rows = list(tiles.values())
    for data in images.values():
        reconstruct(data, tile_rows, opened)
    # Two focused input mutations establish the new report/reconstruction guards.
    bad_report = json.loads(json.dumps(positive[0]))
    bad_report['args'][1] ^= 1
    one = next(iter(images.values()))
    bad_frame = dict(one, pixels_sha256='0' * 64)
    controls = []
    for name, call, expected in (
        ('wrong_case', lambda: report_check(bad_report, *positive[1:]), 'native report case'),
        ('wrong_reconstruction', lambda: reconstruct(bad_frame, tile_rows, opened), 'exact native reconstruction')):
        try:
            call()
        except ValueError as exc:
            require(str(exc) == 'cloud review: ' + expected, 'named review control')
            controls.append({'name': name, 'status': 'FIRED', 'failure': str(exc)})
        else:
            raise ValueError('cloud review control survived: ' + name)
    report_check(*positive)
    reconstruct(one, tile_rows, opened)
    manifest = {'schema_version': 1, 'default_case': 'day_left', 'cases': cases, 'images': images,
        'tiles': tile_rows, 'atlases': atlas_hashes, 'reports_sha256': reports,
        'baseline_sha256': summary['baseline_sha256'], 'candidate_sha256': summary['candidate_sha256'],
        'native_summary': {'path': (captures / 'summary.json').relative_to(ROOT).as_posix(), 'sha256': sha((captures / 'summary.json').read_bytes())}}
    shutil.copyfile(HERE / 'review-template.html', output / 'review.html')
    (output / 'manifest.json').write_bytes((json.dumps(manifest, separators=(',', ':')) + '\n').encode())
    record = {'status': 'PASS', 'builder_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha((HERE / 'review-template.html').read_bytes()),
        'manifest_sha256': sha((output / 'manifest.json').read_bytes()), 'html_sha256': sha((output / 'review.html').read_bytes()),
        'cases': len(cases), 'native_images_reconstructed_exactly': len(images), 'unique_tiles': len(tiles),
        'atlas_bytes': sum((output / n).stat().st_size for n in atlas_hashes), 'controls': controls,
        'scope': 'Lossless native pixels and recorded timing. Browser behavior and human appearance are separate checks.'}
    (output / 'build.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.captures.resolve(), args.output.resolve())
