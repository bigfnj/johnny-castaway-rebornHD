"""Coherent-ground still preview, reusing the frozen v1 native observer."""
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'native/capture.py'
PREVIOUS_SHA = '923332f7b45be500588fd85eb67d274f913b32490edb44822b405f0e3cbe1c8b'
spec = importlib.util.spec_from_file_location('shore_previous_capture', PREVIOUS)
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
native, require, sha, save = previous.native, previous.require, previous.sha, previous.save
require(sha(PREVIOUS.read_bytes()) == PREVIOUS_SHA, 'frozen v1 capture identity')
CANVASES = {0: (560, 104), **{i: (144, 58) for i in range(3, 6)},
            **{i: (320, 50) for i in range(6, 9)}, **{i: (144, 64) for i in range(9, 12)}}
WAVE_FRAMES = (3, 7, 9)
PROP_HASHES = {f'data/styles/cartoon/BMP/HOLIDAY.BMP/{frame:03}.png': digest for frame, digest in enumerate((
    '1f2ac522476d98afcade5f128c12c0c80f6993b871b611498971f23a44eabf79',
    'e6327c07e85d7d8610ed45a502efd283fe1c79fe5850c790bb2808a2ee02176e',
    '7d9c5406f8275a1af9c9369305575a24d807ac5b38200e6ad17913a0a8400265',
    '03ab2762a2924aa39431cf9940555da96ed76bd20043ef73eb130a61ae879740'))}
_previous_one = previous.one


def member(frame):
    return f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'


def package_pair(baseline, candidate):
    metadata = native.selected_archive(baseline)
    props = {f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png' for i in range(4)}
    require(set(metadata['new_cartoon_members']) == props, 'four selected seasonal additions')
    require(metadata['holiday_members_sha256'] == PROP_HASHES, 'exact V5 prop payloads')
    with zipfile.ZipFile(baseline) as archive:
        before = {name: sha(archive.read(name)) for name in archive.namelist()}
    with zipfile.ZipFile(candidate) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'candidate duplicate members')
        after = {name: sha(archive.read(name)) for name in names}
        require(set(before) == set(after), 'candidate member set unchanged')
        changed = {name for name in before if before[name] != after[name]}
        require(changed == {member(frame) for frame in CANVASES}, 'only ten selected ground/wave payloads changed')
        for frame, size in CANVASES.items():
            raw = archive.read(member(frame))
            require(raw[:8] == b'\x89PNG\r\n\x1a\n' and native.struct.unpack('>II', raw[16:24]) == size,
                    'ground/wave fixed canvas:' + member(frame))
    candidate_metadata = dict(metadata, archive_sha256=sha(candidate.read_bytes()))
    return metadata, candidate_metadata, {'baseline_archive_sha256': metadata['archive_sha256'],
        'candidate_archive_sha256': candidate_metadata['archive_sha256'], 'member_count': len(before),
        'unchanged_members': len(before) - len(changed),
        'changed_members': {name: {'before': before[name], 'after': after[name]} for name in sorted(changed)},
        'holiday_members_sha256': metadata['holiday_members_sha256']}


def outside_ground(before, after):
    require(len(before) == len(after) == 1280 * 960 * 3, 'scene dimensions')
    # Six unused phases are packaged, but cannot enlarge this still's allowance.
    rectangles = [(576, 558, 1136, 662), (540, 612, 684, 670),
                  (728, 638, 1048, 688), (1036, 606, 1180, 670)]
    changed = 0
    for y in range(960):
        for x in range(1280):
            index = (y * 1280 + x) * 3
            if before[index:index+3] != after[index:index+3]:
                require(any(l <= x < r and t <= y < b for l, t, r, b in rectangles), 'changed pixel outside drawn ground canvases')
                changed += 1
    require(changed > 0, 'ground repair visibly changed native scene')
    return {'changed_pixels': changed, 'allowed_drawn_ground_rectangles': rectangles,
            'actually_drawn_modified_frames': [0, 3, 7, 9]}


def ground_log(text):
    facts = previous.wave_log(text)
    base = [row for row in facts['all_background_draws'] if row[0] == 0]
    require(base == [[0, 288, 279, 0, 0, 2, 560, 104]], 'actual base island origin/canvas')
    return facts


def one(exe, archive, metadata, folder, holiday, codec):
    pixels, report = _previous_one(exe, archive, metadata, folder, holiday, codec)
    ground_log((folder / 'capture.log').read_text())
    require({member(frame) for frame in CANVASES} <= set(report['loaded_art']), 'all ten selected ground/wave PNG dependencies')
    report['adapter_sha256'] = sha(Path(__file__).read_bytes())
    report['reused_capture_sha256'] = PREVIOUS_SHA
    save(folder / 'report.json', report)
    return pixels, report


def controls(output, before, after, report, text):
    ground_log(text)
    outside_ground(before, after)
    damaged = bytearray(after)
    damaged[0] = before[0] ^ 1
    cases = (
        ('wrong_base_origin', lambda: ground_log(text.replace('SHORE DRAW: frame=0 x=288 ', 'SHORE DRAW: frame=0 x=289 ')), 'actual base island origin/canvas'),
        ('wrong_final_wave', lambda: ground_log(text.replace('SHORE DRAW: frame=7 ', 'SHORE DRAW: frame=8 ')), 'final native wave phases 003/007/009'),
        ('outside_ground_pixel', lambda: outside_ground(before, bytes(damaged)), 'changed pixel outside drawn ground canvases'),
    )
    results = []
    for name, call, expected in cases:
        try:
            call()
        except ValueError as error:
            require(str(error) == 'seasonal: ' + expected, 'named refusal:' + name)
            results.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('control survived:' + name)
    ground_log(text)
    outside_ground(before, after)
    save(output / 'negative-controls.json', {'status': 'PASS', 'adapter_sha256': sha(Path(__file__).read_bytes()),
         'controls': results, 'method': 'Actual completed candidate log/pixels copied and altered in memory; originals unchanged; positive before and after.'})


def main():
    require('--phase-probe' not in sys.argv, 'use frozen v1 for historical phase probe')
    # Share the established eight-smoke then eight-repeat flow and unchanged driver.
    previous.package_pair = package_pair
    previous.outside_waves = outside_ground
    previous.one = one
    previous.controls = controls
    previous.main()
    output = Path(sys.argv[sys.argv.index('--output') + 1])
    for name in ('inputs.json', 'summary.json'):
        path = output / name
        data = json.loads(path.read_text())
        data['adapter_sha256'] = sha(Path(__file__).read_bytes())
        data['reused_capture_sha256'] = PREVIOUS_SHA
        data['modified_package_frames'] = list(CANVASES)
        data['actually_drawn_modified_frames'] = [0, 3, 7, 9]
        save(path, data)


if __name__ == '__main__':
    main()
