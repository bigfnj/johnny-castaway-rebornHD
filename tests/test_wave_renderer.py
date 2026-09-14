"""Real native captures for true-alpha shore waves. Uses only the standard library.

Run with --exe path/to/jc_reborn --archive assets/scrantic_data.zip.
Optional --baseline-exe compares complete HD/fallback captures against a saved
pre-change executable; ordinary runs still assert legacy pixels independently.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zipfile
import zlib


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)


def png(width, height, pixels):
    stride = width * 4
    assert len(pixels) == stride * height
    rows = b''.join(b'\0' + pixels[y*stride:(y+1)*stride] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def make_fixture(source, directory, active):
    directory.mkdir(parents=True, exist_ok=True)
    replacements = {'data/styles/cartoon/manifest.json': json.dumps(
        {'id': 'cartoon', 'scale': 2, 'alpha': 'straight', 'coverage': 'partial'}).encode()}
    with zipfile.ZipFile(source) as archive:
        inventory = json.loads(archive.read('data/hd/manifest.json'))
        for name, item in inventory['SCR'].items():
            width, height = item['width'] * 2, item['height'] * 2
            data = png(width, height, bytes((0, 0, 0, 255)) * width * height)
            replacements['data/hd/SCR/' + name + '.png'] = data
            if active:
                replacements['data/styles/cartoon/SCR/' + name + '.png'] = data
        for item in inventory['BMP']['BACKGRND.BMP']['images']:
            index, width, height = item['index'], item['width'] * 2, item['height'] * 2
            pixels = bytearray(width * height * 4)

            def patch(x, y, color):
                assert 0 <= x < width-1 and 0 <= y < height-1
                for dy in range(2):
                    for dx in range(2):
                        offset = ((y + dy) * width + x + dx) * 4
                        pixels[offset:offset+4] = bytes(color)

            if index in (3, 4, 5):
                patch(0, 0, (255, 0, 0, 128))
                patch(4, 0, (255, 0, 0, 128) if index == 3 else (0, 0, 0, 0))
                patch(8, 0, (255, 0, 0, 255))
                patch(12, 0, (255, 0, 0, 255) if index == 3 else (0, 0, 0, 0))
                patch(16, 0, ((255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255))[index-3])
            # The actual center/right canvases overlap at world HD (1038,640).
            # Their differing colors independently identify composition order.
            if index in (6, 7, 8):
                patch(310, 2, (255, 0, 0, 128))
            if index in (9, 10, 11):
                patch(2, 34, (0, 0, 255, 128))
                patch(24, 40, (0, 255, 0, 255))
            data = png(width, height, bytes(pixels))
            replacements[f'data/hd/BMP/BACKGRND.BMP/{index:03d}.png'] = data
            if active or index == 30:
                # The inactive pack has only a low-tide replacement. High-tide
                # animation must retain its existing HD fallback behavior.
                replacements[f'data/styles/cartoon/BMP/BACKGRND.BMP/{index:03d}.png'] = data
        path = directory / 'scrantic_data.zip'
        with zipfile.ZipFile(path, 'w') as target:
            for info in archive.infolist():
                if info.filename not in replacements and not info.filename.startswith('data/styles/cartoon/'):
                    target.writestr(copy.copy(info), archive.read(info.filename))
            for name, data in replacements.items():
                target.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)


def read_ppm(path):
    data = path.read_bytes()
    match = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n', data)
    if not match:
        raise RuntimeError(f'Invalid native capture: {path}')
    width, height = map(int, match.groups())
    pixels = data[match.end():]
    if (width, height) != (1280, 960) or len(pixels) != width * height * 3:
        raise RuntimeError(f'Invalid native capture dimensions: {path}')
    return pixels


def pixel(pixels, x, y):
    offset = (y * 1280 + x) * 3
    return list(pixels[offset:offset+3])


def capture(exe, directory, style, budget, label='current'):
    profile = directory / 'profile'
    profile.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['HOME'] = env['USERPROFILE'] = str(profile)
    output = directory / f'{label}-{style}-{budget:02d}.ppm'
    args = [str(exe), 'window', 'nosound', 'hotkeys', 'maxspeed', 'debug', 'day', 'holiday', 'none',
            'seed', '9', 'island', 'ads', 'ACTIVITY.ADS', '7', 'style', style,
            'frames', str(budget), 'capture', str(output)]
    result = subprocess.run(args, cwd=directory, env=env, capture_output=True, timeout=40,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
    output.with_suffix('.log').write_text(text, encoding='utf-8')
    if (result.returncode != 0 or f'stopping after {budget} frame(s)' not in text
            or f'Captured frame: {output}' not in text):
        raise RuntimeError(f'Native wave capture failed: {output.with_suffix(".log")}\n{text[-1500:]}')
    return read_ppm(output)


CHECKS = ('smoke', 'half-alpha', 'transparent', 'opaque', 'overlap', 'hd-legacy', 'inactive-tide')


def run(options, work):
    before = hashlib.sha256(options.archive.read_bytes()).hexdigest()
    active, inactive = work / 'active', work / 'inactive'
    make_fixture(options.archive, active, True)
    make_fixture(options.archive, inactive, False)
    cache = {}
    results = []

    def shot(directory, style, budget, baseline=False):
        key = (str(directory), style, budget, baseline)
        if key not in cache:
            cache[key] = capture(options.baseline_exe if baseline else options.exe, directory, style, budget,
                                 'baseline' if baseline else 'current')
        return cache[key]

    def check(name, label, condition):
        if options.only and options.only != name:
            return
        ok = condition()
        print(('PASS' if ok else 'FAIL') + f' tests/test_wave_renderer.py: {label}', flush=True)
        print(f'WITNESS wave assertion executed: {name}', flush=True)
        results.append({'name': name, 'label': label, 'passed': ok})
        if not ok:
            raise AssertionError(label)

    # Smoke always precedes regression on a full run; mutation runs select one
    # assertion but still require exit/capture witnesses from the real engine.
    check('smoke', 'HD and Cartoon complete actual wave captures', lambda:
          len(shot(active, 'hd', 1)) == len(shot(active, 'cartoon', 1)) == 1280*960*3)
    if options.phase == 'smoke':
        return results
    check('half-alpha', 'repeated translucent waves remain at one source-over blend', lambda:
          [pixel(shot(active, 'cartoon', frame), 540, 612) for frame in (1, 5, 11)] == [[128, 0, 0]]*3
          and [pixel(shot(active, 'cartoon', frame), 556, 612) for frame in (1, 5, 11)]
          == [[255, 0, 0], [0, 255, 0], [0, 0, 255]])
    check('transparent', 'the next transparent frame clears old translucent and opaque pixels', lambda:
          all(pixel(shot(active, 'cartoon', frame), x, 612) == [0, 0, 0]
              for frame in (5, 11) for x in (544, 552)))
    check('opaque', 'opaque redraw and untouched black destination stay stable', lambda:
          all(pixel(shot(active, 'cartoon', frame), 548, 612) == [255, 0, 0]
              and pixel(shot(active, 'cartoon', frame), 539, 612) == [0, 0, 0] for frame in (1, 5, 11)))
    check('overlap', 'overlapping neighbors survive restoration in current draw order', lambda:
          [pixel(shot(active, 'cartoon', frame), 1038, 640) for frame in (1, 5, 7, 11)]
          == [[128, 0, 64], [64, 0, 128], [128, 0, 64], [64, 0, 128]]
          and all(pixel(shot(active, 'cartoon', frame), 1060, 646) == [0, 255, 0] for frame in (1, 5, 7, 11)))
    check('hd-legacy', 'HD retains its exact legacy wave pixels', lambda:
          [pixel(shot(active, 'hd', frame), 540, 612) for frame in (1, 5, 11)]
          == [[128, 0, 0], [192, 0, 0], [224, 0, 0]])
    check('inactive-tide', 'Cartoon without active tide replacements equals HD byte-for-byte', lambda:
          all(shot(inactive, 'cartoon', frame) == shot(inactive, 'hd', frame) for frame in (1, 5, 11)))
    if options.baseline_exe:
        for directory in (active, inactive):
            for style in ('hd', 'cartoon'):
                if directory == active and style == 'cartoon':
                    continue
                for frame in (1, 5, 11):
                    assert shot(directory, style, frame) == shot(directory, style, frame, True), (directory, style, frame)
        print('PASS: all 9 complete HD/fallback captures match the pre-change executable byte-for-byte')
    else:
        print('INFO: optional pre-change executable comparison was not requested; independent legacy/fallback pixel checks executed.')
    assert hashlib.sha256(options.archive.read_bytes()).hexdigest() == before, 'Production archive changed'
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--baseline-exe', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--only', choices=CHECKS)
    parser.add_argument('--phase', choices=('smoke', 'all'), default='all')
    options = parser.parse_args()
    options.exe, options.archive = options.exe.resolve(), options.archive.resolve()
    if options.baseline_exe:
        options.baseline_exe = options.baseline_exe.resolve()
    temporary = None
    if options.work:
        work = options.work.resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix='johnny-wave-test-')
        work = Path(temporary.name)
    try:
        results = run(options, work)
        report = {'exe_sha256': hashlib.sha256(options.exe.read_bytes()).hexdigest(), 'checks': results}
        (work / 'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(f'Wave renderer: {len(results)} checks passed')
        return 0
    except (AssertionError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'Wave renderer failed: {exc}')
        return 1
    finally:
        if temporary:
            temporary.cleanup()


if __name__ == '__main__':
    raise SystemExit(main())
