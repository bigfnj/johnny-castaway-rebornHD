"""Headless Linux seasonal stills using the unchanged native island/wait renderer."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCTION_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
CODEC = ROOT / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
CODEC_SHA = '1a956d08ef659cd537e1530bcf13cc9da153a1bf34a1730fd344e91a107c4195'
HOLIDAYS = {
    0: ('none', None),
    1: ('halloween', [0, 410, 298, 80, 68]),
    2: ('stpatricks', [1, 333, 286, 240, 94]),
    3: ('christmas', [2, 404, 267, 112, 130]),
    4: ('newyear', [3, 361, 155, 304, 94]),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError('seasonal: ' + message)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def protected():
    result = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
              for folder in ('src', 'platform', 'third_party/miniz')
              for p in (ROOT / folder).rglob('*')
              if p.is_file() and p.suffix in ('.c', '.h')}
    for p in (ROOT / 'CMakeLists.txt', ROOT / 'assets/scrantic_data.zip', CODEC):
        result[p.relative_to(ROOT).as_posix()] = sha(p.read_bytes())
    return result


def selected_archive(path):
    """Allow only exact current production plus zero to four holiday additions."""
    with zipfile.ZipFile(ROOT / 'assets/scrantic_data.zip') as z:
        base = {name: sha(z.read(name)) for name in z.namelist()}
    allowed = {f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png' for i in range(4)}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'archive duplicate members')
        selected = {name: sha(z.read(name)) for name in names}
        require(set(base) <= set(selected), 'retained production members')
        require(set(selected) - set(base) <= allowed, 'only seasonal additions')
        require(all(selected[name] == digest for name, digest in base.items()), 'retained production payload identity')
        art = []
        for holiday, (_, row) in HOLIDAYS.items():
            if not holiday:
                continue
            frame, _, _, width, height = row
            member = f'data/styles/cartoon/BMP/HOLIDAY.BMP/{frame:03}.png'
            if member not in selected:
                member = f'data/hd/BMP/HOLIDAY.BMP/{frame:03}.png'
            raw = z.read(member)
            require(raw[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', raw[16:24]) == (width, height), 'holiday fixed canvas:' + str(frame))
            art.append(member)
    return {'archive_sha256': sha(path.read_bytes()), 'member_count': len(selected),
            'unchanged_production_member_count': len(base), 'holiday_dependencies': art,
            'holiday_members_sha256': {p: selected[p] for p in art},
            'new_cartoon_members': sorted(set(selected) - set(base))}


def verify_log(text, holiday, night, offset, dependencies):
    dx, dy = offset
    require(f'SEASONAL STATE: seed=11 holiday={holiday} night={night} offset={dx},{dy} lowTide=0 raft=0 render=1280x960' in text, 'actual island state')
    backdrop = 'NIGHT.SCR' if night else 'OCEAN02.SCR'
    require('island backdrop: ' + backdrop in text, 'actual backdrop')
    require('Captured frame: final.ppm (1280x960)' in text and 'SEASONAL DONE: finite native wait returned; cleanup complete' in text, 'finite capture and cleanup')
    found = [list(map(int, match)) for match in re.findall(r'SEASONAL DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)', text)]
    if holiday:
        frame, x, y, width, height = HOLIDAYS[holiday][1]
        require(found == [[frame, x, y, dx, dy, 2, width, height]], 'actual holiday draw mapping')
    else:
        require(found == [], 'no-holiday draw absent')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    holiday_loaded = [name for name in loaded if '/HOLIDAY.BMP/' in name]
    require(holiday_loaded == sorted(dependencies) if holiday else not holiday_loaded, 'selected holiday dependency')
    return {'actual_holiday_draws': found, 'loaded_art': loaded, 'backdrop': backdrop}


def compare_pixels(clean, decorated, holiday, offset):
    require(len(clean) == len(decorated) == 1280 * 960 * 3, 'pixel dimensions')
    if not holiday:
        require(clean == decorated, 'no-holiday exact scene identity')
        return {'changed_pixels': 0, 'allowed_rect': None}
    _, x, y, width, height = HOLIDAYS[holiday][1]
    left, top = (x + offset[0]) * 2, (y + offset[1]) * 2
    right, bottom = left + width, top + height
    changed = 0
    for yy in range(960):
        start = yy * 1280 * 3
        if yy < top or yy >= bottom:
            require(clean[start:start+3840] == decorated[start:start+3840], 'pixels outside holiday canvas')
            continue
        # All selected diagnostic positions keep the holiday canvas onscreen.
        require(clean[start:start+left*3] == decorated[start:start+left*3] and
                clean[start+right*3:start+3840] == decorated[start+right*3:start+3840], 'pixels outside holiday canvas')
        changed += sum(clean[start+xx*3:start+xx*3+3] != decorated[start+xx*3:start+xx*3+3] for xx in range(left, right))
    require(changed > 0, 'holiday visibly drawn')
    return {'changed_pixels': changed, 'allowed_rect': [left, top, right, bottom]}


def build(output):
    text = (ROOT / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    exe = output / 'seasonal_probe'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX',
               '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz',
               str(HERE / 'driver.c'), *[str(ROOT / name) for name in sources],
               '-Wl,--wrap=grDrawSprite', '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, timeout=180)
    (output / 'build.stdout.txt').write_bytes(result.stdout)
    (output / 'build.stderr.txt').write_bytes(result.stderr)
    require(result.returncode == 0 and exe.is_file() and exe.stat().st_mtime_ns >= started, 'fresh observer build')
    save(output / 'build.json', {'command': command, 'started_ns': started, 'executable_mtime_ns': exe.stat().st_mtime_ns,
                                'executable_sha256': sha(exe.read_bytes()), 'driver_sha256': sha((HERE / 'driver.c').read_bytes()),
                                'capture_sha256': sha(Path(__file__).read_bytes()), 'compiler': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0]})
    return exe


def capture(exe, archive, metadata, folder, holiday, night, offset, codec):
    folder.mkdir(parents=True)
    shutil.copyfile(archive, folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), str(holiday), str(night), *map(str, offset)]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=30)
    require(result.returncode == 0, 'native exit:' + str(folder))
    facts = verify_log((folder / 'capture.log').read_text(), holiday, night, offset, metadata['holiday_dependencies'])
    pixels = codec.ppm(folder / 'final.ppm')
    png = codec.png_bytes(pixels)
    (folder / 'final.png').write_bytes(png)
    report = {'status': 'PASS', 'holiday': holiday, 'night': night, 'offset': offset, 'command': command,
              'archive_sha256': metadata['archive_sha256'], 'executable_sha256': sha(exe.read_bytes()),
              'pixels_sha256': sha(pixels), 'png_sha256': sha(png), 'log_sha256': sha((folder / 'capture.log').read_bytes()), **facts}
    save(folder / 'report.json', report)
    print('PASS captured ' + folder.relative_to(exe.parent).as_posix(), flush=True)
    return pixels, report


def negative_controls(output, codec, dependencies):
    folder = output / 'day/halloween/smoke'
    text = (folder / 'capture.log').read_text()
    clean = codec.ppm(output / 'day/none/smoke/final.ppm')
    actual = codec.ppm(folder / 'final.ppm')
    verify_log(text, 1, 0, [0, 0], dependencies)
    compare_pixels(clean, actual, 1, [0, 0])
    damaged = bytearray(actual)
    damaged[0] ^= 1
    variants = [
        ('draw_origin', lambda: verify_log(text.replace('frame=0 x=410', 'frame=0 x=411'), 1, 0, [0, 0], dependencies), 'actual holiday draw mapping'),
        ('outside_canvas', lambda: compare_pixels(clean, bytes(damaged), 1, [0, 0]), 'pixels outside holiday canvas'),
        ('wrong_dependency', lambda: verify_log(text.replace('Art asset: ' + dependencies[0], 'Art asset: data/incorrect/000.png'), 1, 0, [0, 0], dependencies), 'selected holiday dependency'),
    ]
    results = []
    for name, run, expected in variants:
        try:
            run()
        except ValueError as error:
            require(str(error) == 'seasonal: ' + expected, 'named negative-control failure:' + name)
            results.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('negative control survived:' + name)
    verify_log(text, 1, 0, [0, 0], dependencies)
    compare_pixels(clean, actual, 1, [0, 0])
    save(output / 'negative-controls.json', {'status': 'PASS', 'helper_sha256': sha(Path(__file__).read_bytes()),
         'method': 'Actual retained native log/pixels copied and altered in memory, then executed through the same verification functions. Original capture files untouched; positive readback before and after.', 'results': results})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--archive-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--diagnostics', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.exists(), 'fresh output directory required')
    output.mkdir(parents=True)
    try:
        inputs = protected()
        require(inputs['assets/scrantic_data.zip'] == PRODUCTION_SHA, 'pinned production baseline')
        require(sha(args.archive.read_bytes()) == args.archive_sha256, 'explicit archive identity')
        require(sha(CODEC.read_bytes()) == CODEC_SHA, 'reused capture codec identity')
        spec = importlib.util.spec_from_file_location('seasonal_codec', CODEC)
        codec = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(codec)
        metadata = selected_archive(args.archive)
        save(output / 'inputs.json', {'protected_sha256': inputs, 'selected_archive': metadata,
             'source_scope': 'Production island/graphics/walk functions compiled unchanged. Driver selects high tide, no raft, fixed island position and actual native same-heading A wait. Story scheduler and cargo suppression policy are outside this still capture.'})
        exe = build(output)
        groups = [('day', 0, [0, 0])]
        if args.diagnostics:
            groups += [('night', 1, [0, 0]), ('offset', 0, [-80, 20])]
        summaries = {}
        # Primary day scenes all smoke before regression/repeat.
        day = {}
        for holiday, (name, _) in HOLIDAYS.items():
            day[holiday] = capture(exe, args.archive, metadata, output / 'day' / name / 'smoke', holiday, 0, [0, 0], codec)
        print('PASS all five day smoke captures before regression', flush=True)
        for group, night, offset in groups:
            cases = {}
            if group == 'day':
                cases = day
            else:
                for holiday, (name, _) in HOLIDAYS.items():
                    cases[holiday] = capture(exe, args.archive, metadata, output / group / name / 'smoke', holiday, night, offset, codec)
            summaries[group] = {}
            for holiday, (name, _) in HOLIDAYS.items():
                pixels, record = cases[holiday]
                comparison = compare_pixels(cases[0][0], pixels, holiday, offset)
                repeated, repeat_record = capture(exe, args.archive, metadata, output / group / name / 'repeat', holiday, night, offset, codec)
                require(pixels == repeated and record['actual_holiday_draws'] == repeat_record['actual_holiday_draws'], 'exact fresh-process repeat:' + group + '/' + name)
                summaries[group][name] = {'smoke': 'PASS', 'regression_repeat': 'PASS', 'png_sha256': record['png_sha256'], **comparison}
        negative_controls(output, codec, metadata['holiday_dependencies'])
        require(protected() == inputs, 'protected production inputs unchanged')
        require(sha(args.archive.read_bytes()) == args.archive_sha256, 'selected archive unchanged')
        save(output / 'summary.json', {'status': 'PASS', 'selected_archive': metadata, 'groups': summaries,
             'helper_sha256': sha(Path(__file__).read_bytes()), 'driver_sha256': sha((HERE / 'driver.c').read_bytes()),
             'protected_inputs_unchanged': len(inputs), 'negative_controls': 3,
             'scope': 'Still capture of actual native holiday layer over current Cartoon island and approved standing016. No original-executable timing/palette claim; cargo scene suppression and randomized tide/offset selection are not exercised.'})
        print('PASS seasonal captures, exact repeats, scoped pixels, three negatives and unchanged production', flush=True)
    except Exception:
        save(output / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
