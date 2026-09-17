"""Four fixed native stills; reuse the seasonal observer's build/pixel codec."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LEGACY = ROOT / 'art/cartoon/seasonal-v1/native/capture.py'
LEGACY_SHA = '5a325d6b3db2ae3e7362ede1144977c977542c668596bbfb24b1e0a5bcdfe730'
WAVES = {3: (270, 306, 144, 58), 7: (364, 319, 320, 50), 9: (518, 303, 144, 64)}
CASES = ((0, 'none'), (2, 'clover'), (1, 'pumpkin'), (3, 'tree'))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


native = load(LEGACY, 'shore_seasonal')
require, sha, save = native.require, native.sha, native.save
require(sha(LEGACY.read_bytes()) == LEGACY_SHA, 'reused seasonal helper identity')


def wave_log(text):
    """Observe every actual background draw, including neighbor redraws."""
    rows = [list(map(int, row)) for row in re.findall(
        r'SHORE DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)', text)]
    require(rows, 'observed BACKGRND draws')
    actual, last = [], {}
    for row in rows:
        frame, x, y, dx, dy, scale, width, height = row
        if 3 <= frame <= 11:
            family = (frame - 3) // 3
            expected = ((270, 306, 144, 58), (364, 319, 320, 50), (518, 303, 144, 64))[family]
            require((x, y, width, height) == expected and (dx, dy, scale) == (0, 0, 2), 'actual wave canvas/origin')
            actual.append(row)
            last[family] = frame
    require([last.get(i) for i in range(3)] == [3, 7, 9], 'final native wave phases 003/007/009')
    require('SHORE STAGE: init' in text and 'SHORE STAGE: native wait returned' in text, 'observed driver stages')
    return {'all_background_draws': rows, 'wave_draws': actual, 'final_wave_frames': [last[i] for i in range(3)]}


def package_pair(baseline, candidate):
    metadata = native.selected_archive(baseline)
    additions = {f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png' for i in range(4)}
    require(set(metadata['new_cartoon_members']) == additions, 'all four restored V5 holiday members')
    with zipfile.ZipFile(baseline) as archive:
        before = {name: sha(archive.read(name)) for name in archive.namelist()}
    with zipfile.ZipFile(candidate) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'candidate duplicate members')
        after = {name: sha(archive.read(name)) for name in names}
        require(set(before) == set(after), 'candidate member set unchanged')
        changed = {name for name in before if before[name] != after[name]}
        expected = {f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png' for frame in WAVES}
        require(changed == expected, 'only three selected wave payloads changed')
        for frame, (_, _, width, height) in WAVES.items():
            member = f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
            raw = archive.read(member)
            require(raw[:8] == b'\x89PNG\r\n\x1a\n' and native.struct.unpack('>II', raw[16:24]) == (width, height), 'wave fixed canvas:' + member)
    candidate_metadata = dict(metadata, archive_sha256=sha(candidate.read_bytes()))
    return metadata, candidate_metadata, {
        'baseline_archive_sha256': metadata['archive_sha256'], 'candidate_archive_sha256': candidate_metadata['archive_sha256'],
        'member_count': len(before), 'unchanged_members': len(before) - len(changed),
        'changed_members': {name: {'before': before[name], 'after': after[name]} for name in sorted(changed)},
        'holiday_members_sha256': metadata['holiday_members_sha256']}


def outside_waves(before, after):
    require(len(before) == len(after) == 1280 * 960 * 3, 'scene dimensions')
    rects = [(x*2, y*2, x*2+w, y*2+h) for x, y, w, h in WAVES.values()]
    count = 0
    for y in range(960):
        for x in range(1280):
            i = (y*1280+x)*3
            if before[i:i+3] != after[i:i+3]:
                require(any(l <= x < r and t <= y < b for l, t, r, b in rects), 'changed pixel outside selected wave canvases')
                count += 1
    require(count > 0, 'repair visibly changed native scene')
    return {'changed_pixels': count, 'allowed_wave_rectangles': rects}


def one(exe, archive, metadata, folder, holiday, codec):
    pixels, record = native.capture(exe, archive, metadata, folder, holiday, 0, [0, 0], codec)
    text = (folder / 'capture.log').read_text()
    record.update(wave_log(text))
    expected = {f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png' for frame in WAVES}
    require(expected <= set(record['loaded_art']), 'selected wave PNG dependencies')
    save(folder / 'report.json', record)
    return pixels, record


def controls(output, before, after, record, text):
    wave_log(text)
    outside_waves(before, after)
    damaged = bytearray(after)
    damaged[0] = before[0] ^ 1
    cases = (
        ('wrong_phase', lambda: wave_log(text.replace('SHORE DRAW: frame=7 ', 'SHORE DRAW: frame=8 ')), 'final native wave phases 003/007/009'),
        ('outside_wave_pixel', lambda: outside_waves(before, bytes(damaged)), 'changed pixel outside selected wave canvases'),
    )
    fired = []
    for name, call, expected in cases:
        try:
            call()
        except ValueError as error:
            require(str(error) == 'seasonal: ' + expected, 'named refusal:' + name)
            fired.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('control survived:' + name)
    wave_log(text)
    outside_waves(before, after)
    save(output / 'negative-controls.json', {'status': 'PASS', 'helper_sha256': sha(Path(__file__).read_bytes()),
        'candidate_report_sha256': sha(json.dumps(record, sort_keys=True).encode()), 'controls': fired,
        'method': 'Actual captured inputs copied and damaged in memory, positive before/after; capture files unchanged.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--baseline-sha256', required=True)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--candidate-sha256')
    parser.add_argument('--phase-probe', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.phase_probe or (args.candidate and args.candidate_sha256), 'candidate inputs or explicit phase probe required')
    require(not args.output.exists(), 'fresh output directory required')
    args.output.mkdir(parents=True)
    try:
        protected = native.protected()
        require(protected['assets/scrantic_data.zip'] == native.PRODUCTION_SHA, 'pinned production baseline')
        require(sha(args.baseline.read_bytes()) == args.baseline_sha256, 'explicit baseline archive identity')
        require(sha(native.CODEC.read_bytes()) == native.CODEC_SHA, 'reused capture codec identity')
        codec = load(native.CODEC, 'shore_codec')
        baseline_metadata = native.selected_archive(args.baseline)
        if args.candidate:
            require(sha(args.candidate.read_bytes()) == args.candidate_sha256, 'explicit candidate archive identity')
            baseline_metadata, candidate_metadata, pair = package_pair(args.baseline, args.candidate)
        else:
            pair = {'phase_probe_only': True, 'baseline_archive_sha256': args.baseline_sha256}
        save(args.output / 'inputs.json', {'protected_sha256': protected, 'packages': pair,
            'dependencies_sha256': {LEGACY.relative_to(ROOT).as_posix(): LEGACY_SHA, native.CODEC.relative_to(ROOT).as_posix(): native.CODEC_SHA},
            'driver_sha256': sha((HERE / 'driver.c').read_bytes()), 'capture_sha256': sha(Path(__file__).read_bytes())})
        # Reuse the exact compiler/source selection with only the new observation driver.
        native.HERE = HERE
        exe = native.build(args.output)
        if args.phase_probe:
            _, record = one(exe, args.baseline, baseline_metadata, args.output / 'phase-probe', 0, codec)
            save(args.output / 'phase-observation.json', record)
            require(native.protected() == protected, 'protected inputs unchanged')
            print('PASS observed native final wave phases: ' + str(record['final_wave_frames']), flush=True)
            return
        groups = (('baseline', args.baseline, baseline_metadata), ('candidate', args.candidate, candidate_metadata))
        captures = {}
        # Each actual case is smoked before any fresh-process repeat/regression.
        for group, archive, metadata in groups:
            captures[group] = {}
            for holiday, name in CASES:
                captures[group][name] = one(exe, archive, metadata, args.output / group / name / 'smoke', holiday, codec)
        print('PASS eight still smoke captures before regression', flush=True)
        summaries = {}
        for group, archive, metadata in groups:
            summaries[group] = {}
            for holiday, name in CASES:
                pixels, record = captures[group][name]
                repeated, repeat_record = one(exe, archive, metadata, args.output / group / name / 'repeat', holiday, codec)
                require(pixels == repeated and record['all_background_draws'] == repeat_record['all_background_draws'], 'exact fresh native repeat:' + group + '/' + name)
                holiday_comparison = native.compare_pixels(captures[group]['none'][0], pixels, holiday, [0, 0])
                summaries[group][name] = {'smoke': 'PASS', 'fresh_repeat': 'PASS', 'png_sha256': record['png_sha256'], 'holiday_comparison': holiday_comparison}
        comparisons = {name: outside_waves(captures['baseline'][name][0], captures['candidate'][name][0]) for _, name in CASES}
        controls(args.output, captures['baseline']['none'][0], captures['candidate']['none'][0], captures['candidate']['none'][1],
                 (args.output / 'candidate/none/smoke/capture.log').read_text())
        require(native.protected() == protected, 'protected inputs unchanged')
        require(sha(args.baseline.read_bytes()) == args.baseline_sha256 and sha(args.candidate.read_bytes()) == args.candidate_sha256, 'private inputs unchanged')
        save(args.output / 'summary.json', {'status': 'PASS', 'packages': pair, 'groups': summaries, 'comparisons': comparisons,
            'final_wave_frames': [3, 7, 9], 'helper_sha256': sha(Path(__file__).read_bytes()), 'driver_sha256': sha((HERE / 'driver.c').read_bytes()),
            'protected_inputs_unchanged': len(protected), 'scope': 'Four high-tide/day/zero-offset still cases only. Normal native initialization and finite same-heading wait; no phase forcing. Not a complete wave-cycle or original-executable comparison.'})
        print('PASS four native still comparisons and fresh repeats; no production changes', flush=True)
    except Exception:
        save(args.output / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
