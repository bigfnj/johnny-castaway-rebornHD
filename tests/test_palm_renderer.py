"""Windows native walk.c palm tests; fixtures/captures remain isolated.

Uses the standard library. Smoke completes before regression. The separate API
driver exercises real D/E routes, including HD Johnny directions outside24-29.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from test_wave_renderer import png, read_ppm, pixel

PREFIX = 'data/styles/cartoon/'
CHECKS = ('smoke', 'outside-alpha', 'overlap', 'opaque', 'transparent', 'clipping', 'hd-legacy', 'partial-fallback')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(base, folder, alpha=128, active=True, original=False):
    folder.mkdir(parents=True)
    replacements = {PREFIX + 'manifest.json': json.dumps(
        {'id': 'cartoon', 'scale': 2, 'alpha': 'straight', 'coverage': 'partial'}).encode()}
    with zipfile.ZipFile(base) as source:
        inventory = json.loads(source.read('data/hd/manifest.json'))
        if original:
            # Inactive high-tide replacement provides a valid partial pack.
            item = inventory['BMP']['BACKGRND.BMP']['images'][30]
            w, h = item['width']*2, item['height']*2
            replacements[PREFIX + 'BMP/BACKGRND.BMP/030.png'] = png(w, h, bytes(w*h*4))
        else:
            for name, item in inventory['SCR'].items():
                w, h = item['width']*2, item['height']*2
                data = png(w, h, bytes((0, 0, 0, 255))*w*h)
                replacements['data/hd/SCR/' + name + '.png'] = data
                replacements[PREFIX + 'SCR/' + name + '.png'] = data
            for resource in ('BACKGRND.BMP', 'JOHNWALK.BMP'):
                for item in inventory['BMP'][resource]['images']:
                    index, w, h = item['index'], item['width']*2, item['height']*2
                    pixels = bytearray(bytes((0, 0, 255, 128))*w*h if resource == 'JOHNWALK.BMP' else bytes(w*h*4))
                    if resource == 'BACKGRND.BMP' and index == 13:
                        # Away from Johnny and over Johnny, at HD900,350/450.
                        for y in (54, 154):
                            for dy in (0, 1):
                                for dx in (0, 1):
                                    pos = ((y+dy)*w + 16+dx)*4
                                    pixels[pos:pos+4] = bytes((255, 0, 0, alpha))
                    data = png(w, h, bytes(pixels))
                    relative = f'BMP/{resource}/{index:03d}.png'
                    replacements['data/hd/' + relative] = data
                    if resource == 'JOHNWALK.BMP' or active:
                        replacements[PREFIX + relative] = data
        with zipfile.ZipFile(folder / 'scrantic_data.zip', 'x') as target:
            for info in source.infolist():
                if info.filename not in replacements and not info.filename.startswith(PREFIX):
                    target.writestr(copy.copy(info), source.read(info.filename))
            for name, data in replacements.items():
                target.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)


def capture(driver, folder, style, route, label):
    profile = folder / 'profile'
    profile.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['HOME'] = env['USERPROFILE'] = str(profile)
    # Copy the driver beside this fixture so ZIP resolution cannot find a
    # production archive beside the source driver in preference to the fixture.
    exe = folder / (label + '.exe')
    shutil.copyfile(driver, exe)
    output = folder / f'{label}-{style}-{route}.ppm'
    budget = 0 if route == 'none' else 4
    command = [str(exe), style, route, str(budget), str(output)]
    result = subprocess.run(command, cwd=folder, env=env, capture_output=True, timeout=30,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
    output.with_suffix('.log').write_text(text, encoding='utf-8')
    assert result.returncode == 0 and f'Captured frame: {output}' in text, (
        f'Capture failed (exit {result.returncode}): {output.with_suffix(".log")}\n{text[-1500:]}'
    )
    if route != 'none':
        assert f'chosen path: {route.upper()}' in text and 'next=-1' in text, f'Real direct walk witness missing: {output}'
        assert 'stopping after 4 frame(s)' in text, f'Bounded exit missing: {output}'
    return read_ppm(output)


def run(options, work):
    protected = {str(p): digest(p) for p in (options.archive, options.driver)}
    fixtures = {}
    shots = {}
    results = []

    def case(alpha=128, active=True, original=False):
        key = (alpha, active, original)
        if key not in fixtures:
            folder = work / f'alpha{alpha}-active{int(active)}-original{int(original)}'
            fixture(options.archive, folder, alpha, active, original)
            fixtures[key] = folder
        return fixtures[key]

    def shot(route, alpha=128, style='cartoon', active=True, original=False, baseline=False):
        key = (route, alpha, style, active, original, baseline)
        if key not in shots:
            shots[key] = capture(options.baseline_driver if baseline else options.driver,
                                 case(alpha, active, original), style, route,
                                 'baseline' if baseline else 'current')
        return shots[key]

    def check(name, label, fn):
        if options.only and options.only != name:
            return
        try:
            ok = bool(fn())
        except Exception as exc:
            ok = False
            label += ': ' + str(exc)
        print(('PASS' if ok else 'FAIL') + f' tests/test_palm_renderer.py: {label}', flush=True)
        print(f'WITNESS palm assertion executed: {name}', flush=True)
        results.append({'name': name, 'passed': ok, 'label': label})
        if not ok:
            raise AssertionError(label)

    # Source-over arithmetic oracle is independent of the implementation helper.
    # Half red tree over half blue Johnny over black = RGB128,0,64.
    check('smoke', 'HD and Cartoon finish actual D/E captures', lambda:
          all(len(shot(route, style=style)) == 1280*960*3 for route in ('de', 'ed') for style in ('hd', 'cartoon')))
    if options.phase != 'smoke':
        check('outside-alpha', 'palm alpha128 remains128 away from Johnny on both routes', lambda:
              all(pixel(shot(route), 900, 350) == [128, 0, 0] for route in ('none', 'de', 'ed')))
        check('overlap', 'palm-over-partial-Johnny preserves tree color and Johnny coverage', lambda:
              all(pixel(shot(route), 900, 450) == [128, 0, 64] for route in ('de', 'ed')))
        check('opaque', 'opaque palm still occludes Johnny', lambda:
              all(pixel(shot(route, alpha=255), 900, y) == [255, 0, 0] for route in ('de', 'ed') for y in (350, 450)))
        check('transparent', 'transparent palm preserves Johnny and empty background', lambda:
              all(pixel(shot(route, alpha=0), 900, 350) == [0, 0, 0] and
                  pixel(shot(route, alpha=0), 900, 450) == [0, 0, 128] for route in ('de', 'ed')))

        def clipping():
            proc = subprocess.run([str(options.driver), 'atop-clipping'], capture_output=True, timeout=10)
            text = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
            (work / 'atop-clipping.log').write_text(text, encoding='utf-8')
            return proc.returncode == 0 and 'ATOP clipped scaled offset and negative origin: PASS' in text
        check('clipping', 'source-atop respects scaled offset, clip and negative origin', clipping)
        check('hd-legacy', 'HD retains its original source-over pixels', lambda:
              all(pixel(shot(route, style='hd'), 900, 350) == [192, 0, 0] and
                  pixel(shot(route, style='hd'), 900, 450) == [160, 0, 64] for route in ('de', 'ed')))
        check('partial-fallback', 'partial Cartoon without palm replacements retains HD behavior', lambda:
              all(shot(route, active=False) == shot(route, style='hd', active=False) for route in ('de', 'ed')))
        if options.baseline_driver and not options.only:
            for route in ('de', 'ed'):
                for style in ('hd', 'cartoon'):
                    assert shot(route, style=style, original=True) == shot(route, style=style, original=True, baseline=True), f'Historical full-frame {style}/{route} differs'
            print('PASS historical full-frame HD and partial-fallback parity: 4/4', flush=True)
        elif not options.only:
            print('INFO historical pre-change driver unavailable; independent HD pixels and current full-frame fallback parity run above', flush=True)
    assert all(digest(p) == h for p, h in protected.items()), 'Protected driver/archive changed'
    report = {'status': 'PASS', 'checks': results, 'protected_inputs': protected,
              'scope': 'Actual walk.c API routes. Test-only synthetic art; shipped CLI scheduling is not claimed.',
              'historical_full_frames': 4 if options.baseline_driver and not options.only and options.phase != 'smoke' else 0}
    (work / 'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--driver', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--baseline-driver', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--only', choices=CHECKS)
    parser.add_argument('--phase', choices=('smoke', 'all'), default='all')
    options = parser.parse_args()
    options.driver = options.driver.resolve()
    options.archive = options.archive.resolve()
    if options.baseline_driver:
        options.baseline_driver = options.baseline_driver.resolve()
    try:
        if options.work:
            options.work = options.work.resolve()
            options.work.mkdir(parents=True, exist_ok=True)
            return run(options, options.work)
        with tempfile.TemporaryDirectory(prefix='jc-palm-') as temp:
            return run(options, Path(temp))
    except AssertionError:
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
