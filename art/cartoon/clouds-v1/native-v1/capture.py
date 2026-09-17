"""Paired cloud-only native review. No rendering or engine replacement."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import traceback

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
CONTRACT = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/native-final/contract.py'
spec = importlib.util.spec_from_file_location('cloud_retained_contract', CONTRACT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
BASE_SHA = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
SIZES = {15: [256, 72], 16: [384, 114], 17: [528, 152]}
INITIAL = {15: [40, 25, 1], 16: [230, 55, 2], 17: [375, 30, 1]}
# holiday, night, x/y offset, low tide, walk mode, waits, wind, cloud count
CASES = {'day_left': [0, 0, 0, 0, 0, 0, 20, 1, 3],
         'day_right': [0, 0, 0, 0, 0, 0, 20, 0, 3],
         'night_shift_right': [0, 1, -80, 20, 0, 0, 20, 0, 3],
         'no_clouds': [0, 0, 0, 0, 0, 0, 1, 0, 0]}
CLOUD = re.compile(r'CLOUD DRAW: frame=(\d+) flip=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+) blits=(\d+) bounds=(-?\d+),(-?\d+),(-?\d+),(-?\d+)')


def require(ok, label):
    if not ok:
        raise ValueError('cloud native: ' + label)


def validate_members(before, after):
    additions = {c.member(16), c.member(17)}
    require(len(before) == 2612 and len(after) == 2614, 'baseline/candidate member counts')
    require(before.keys() <= after.keys() and after.keys() - before.keys() == additions,
            'only cloud016/017 additions')
    require(all(after[n] == row for n, row in before.items()), 'all baseline payloads retained')
    for f in (16, 17):
        require(after[c.member(f)]['canvas'] == SIZES[f], f'{f:03} original scaled canvas')
    return {n: after[n] for n in sorted(additions)}


def verify(text, args, candidate, canvases):
    facts = c.verify_log(text, args[:7], True, canvases)
    wind, count = args[7:]
    require(text.count(f'CLOUD FIXTURE: wind={wind} count={count} source=explicit-native-state') == 1,
            'explicit cloud fixture')
    initial = [list(map(int, r)) for r in re.findall(r'CLOUD INITIAL: frame=(\d+) x=(-?\d+) y=(-?\d+) speed=(\d+)', text)]
    require(initial == [[f, *row] for f, row in INITIAL.items()][:count], 'cloud initial positions/speeds')
    positions = {f: row[0] for f, row in INITIAL.items()}
    latest, draws, seen_displays = {}, [], []
    for line in text.splitlines():
        match = CLOUD.fullmatch(line)
        if match:
            row = list(map(int, match.groups()))
            f, flip, x, y, dx, dy, scale, w, h, blits, l, t, r, b = row
            require(count == 3 and f == 15 + len(draws) % 3, 'native cloud draw order')
            previous = positions[f]
            expected = -264 if previous > 904 else 904 if previous < -264 else previous + (-1 if wind else 1) * INITIAL[f][2]
            require(x == expected and y == INITIAL[f][1], f'{f:03} native cloud movement')
            require([flip, dx, dy, scale, w, h] == [1 - wind, *args[2:4], 2, *SIZES[f]], f'{f:03} cloud flip/offset/canvas')
            require([l, t, r, b] == [(x + dx) * 2, (y + dy) * 2, (x + dx) * 2 + w, (y + dy) * 2 + h]
                    and blits == (w if flip else 1), f'{f:03} actual cloud blit bounds')
            positions[f] = x
            latest[f] = row
            draws.append(row)
        if line.startswith('DISPLAY: '):
            require(len(latest) == count, 'cloud layer populated before display')
            seen_displays.append([latest[f] for f in sorted(latest)])
    require(len(seen_displays) == len(facts['displays']), 'every displayed cloud state')
    require(len(draws) >= 6 if count else not draws, 'moving versus empty cloud state')
    if count:
        require(len(draws) % count == 0, 'complete native cloud updates')
    for display, state in zip(facts['displays'], seen_displays):
        display['clouds'] = state
    expected = {c.member(15), *[f'data/{"styles/cartoon" if candidate else "hd"}/BMP/BACKGRND.BMP/{f:03}.png' for f in (16, 17)]}
    require(expected <= set(facts['loaded_art']), 'selected cloud asset paths')
    facts.update(cloud_draws=draws, initial_clouds=initial, wind=wind, cloud_count=count)
    return facts


def pixel_scope(before, after, clouds):
    require(len(before) == len(after) == 1280 * 960 * 3, 'native RGB dimensions')
    rects = [(max(0, r[10]), max(0, r[11]), min(1280, r[12]), min(960, r[13]))
             for r in clouds if r[0] in (16, 17)]
    changed = 0
    for y in range(960):
        start = y * 3840
        merged = []
        for l, r in sorted((l, r) for l, t, r, b in rects if t <= y < b and l < r):
            if merged and l <= merged[-1][1]:
                merged[-1][1] = max(r, merged[-1][1])
            else:
                merged.append([l, r])
        cursor = 0
        for l, r in merged:
            require(before[start + cursor * 3:start + l * 3] == after[start + cursor * 3:start + l * 3], 'pixel outside displayed016/017')
            changed += sum(before[start + x * 3:start + x * 3 + 3] != after[start + x * 3:start + x * 3 + 3] for x in range(l, r))
            cursor = r
        require(before[start + cursor * 3:start + 3840] == after[start + cursor * 3:start + 3840], 'pixel outside displayed016/017')
    return changed


def compare(observer, folder, before, after):
    c.compare_facts(before, after)
    require(before['cloud_draws'] == after['cloud_draws'], 'paired cloud movement/flip/blits')
    require(before['background_draws'] == after['background_draws'], 'paired background draw records')
    counts = []
    for left, right in zip(before['displays'], after['displays']):
        require(left['clouds'] == right['clouds'], 'paired displayed cloud state')
        old = observer.codec.ppm(folder / 'baseline/smoke' / f"display-{left['ordinal']:03}.ppm")
        new = observer.codec.ppm(folder / 'candidate/smoke' / f"display-{right['ordinal']:03}.ppm")
        require(c.sha(old) == left['pixels_sha256'] and c.sha(new) == right['pixels_sha256'], 'actual display pixel identity')
        counts.append(pixel_scope(old, new, right['clouds']))
    require(any(counts) if after['cloud_count'] else not any(counts), 'visible cloud change or empty exact control')
    return counts


def controls(observer, output, before_members, after_members, canvases):
    folder = output / 'day_left/candidate/smoke'
    text = (folder / 'capture.log').read_text()
    args = CASES['day_left']
    report = verify(text, args, True, canvases)
    cloud = report['displays'][0]['clouds'][1]
    pixels = observer.codec.ppm(folder / 'display-001.ppm')
    damaged = bytearray(pixels)
    damaged[0] ^= 1
    wrong = json.loads(json.dumps(after_members))
    wrong[c.member(16)]['canvas'][0] += 1
    original = f'bounds={cloud[10]},{cloud[11]},{cloud[12]},{cloud[13]}'
    changed = f'bounds={cloud[10]+1},{cloud[11]},{cloud[12]},{cloud[13]}'
    require(original in text, 'negative actual-blit witness exists')
    tests = [('actual016placement', lambda: verify(text.replace(original, changed, 1), args, True, canvases), '016 actual cloud blit bounds'),
             ('outside_pixel', lambda: pixel_scope(pixels, bytes(damaged), report['displays'][0]['clouds']), 'pixel outside displayed016/017'),
             ('wrong016canvas', lambda: validate_members(before_members, wrong), '016 original scaled canvas')]
    rows = []
    for name, call, label in tests:
        try:
            call()
        except ValueError as exc:
            require(str(exc) == 'cloud native: ' + label, 'named control ' + name)
            rows.append({'name': name, 'status': 'FIRED', 'failure': str(exc)})
        else:
            raise ValueError('cloud control survived: ' + name)
    verify(text, args, True, canvases)
    pixel_scope(pixels, pixels, report['displays'][0]['clouds'])
    validate_members(before_members, after_members)
    c.save(output / 'negative-controls.json', {'status': 'PASS', 'controls': rows,
        'method': 'Actual log/pixels and selected member metadata damaged in memory; each expected named failure and restored positive executed.',
        'checker_sha256': c.sha(Path(__file__).read_bytes())})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--candidate-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'fresh output')
    a.output.mkdir(parents=True)
    try:
        require(c.sha(a.baseline.read_bytes()) == BASE_SHA, 'current61 baseline archive')
        require(c.sha(a.candidate.read_bytes()) == a.candidate_sha256, 'explicit candidate identity')
        before, after = c.archive(a.baseline), c.archive(a.candidate)
        added = validate_members(before, after)
        observer = c.load_observer()
        observer.HERE, observer.verify_log = HERE, verify
        protected = observer.legacy.protected()
        require(protected['assets/scrantic_data.zip'] == BASE_SHA, 'live production remains current61')
        paths = (Path(__file__), HERE / 'run.py', HERE / 'driver.c', CONTRACT, c.OBSERVER,
                 c.OBSERVER.parent / 'driver.c', observer.LEGACY, observer.legacy.CODEC)
        helpers = {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in paths}
        canvases = {str(f): before[c.member(f)]['canvas'] for f in c.FRAMES}
        c.save(a.output / 'inputs.json', {'baseline_sha256': BASE_SHA, 'candidate_sha256': a.candidate_sha256,
            'added_members': added, 'unchanged_prior_members': len(before), 'cases': CASES,
            'protected_sha256': protected, 'helpers_sha256': helpers,
            'scope': 'Explicit native cloud fixtures, real movement/timers/compositing; no natural story or original-executable claim.'})
        exe = observer.build(a.output)
        results = {}
        for name, args in CASES.items():
            rows = {label: observer.one(exe, archive, a.output / name / label / 'smoke', args, label == 'candidate', canvases)
                    for label, archive in (('baseline', a.baseline), ('candidate', a.candidate))}
            counts = compare(observer, a.output / name, rows['baseline'], rows['candidate'])
            results[name] = {'smoke': 'PASS', 'display_count': len(counts),
                             'duration_ms': rows['candidate']['duration_ms'], 'changed_pixels': counts}
            c.save(a.output / 'smoke-progress.json', results)
        c.save(a.output / 'smoke.json', {'status': 'PASS', 'cases': results})
        print('PASS all cloud smokes before fresh repeats', flush=True)
        for name, args in CASES.items():
            for label, archive in (('baseline', a.baseline), ('candidate', a.candidate)):
                old = json.loads((a.output / name / label / 'smoke/report.json').read_bytes())
                fresh = observer.one(exe, archive, a.output / name / label / 'repeat', args, label == 'candidate', canvases)
                keys = ('displays', 'cloud_draws', 'background_draws', 'wave_surface_placements', 'native_calls', 'native_returns', 'png_sha256')
                require(all(old[k] == fresh[k] for k in keys), 'fresh exact native repeat ' + name + '/' + label)
            results[name]['fresh_repeat'] = 'PASS'
        controls(observer, a.output, before, after, canvases)
        require(protected == observer.legacy.protected(), 'protected source/production stable')
        require(helpers == {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in paths}, 'helper inputs stable')
        require(c.sha(a.baseline.read_bytes()) == BASE_SHA and c.sha(a.candidate.read_bytes()) == a.candidate_sha256, 'private archives stable')
        c.save(a.output / 'summary.json', {'status': 'PASS', 'baseline_sha256': BASE_SHA,
            'candidate_sha256': a.candidate_sha256, 'cases': results,
            'inputs_sha256': c.sha((a.output / 'inputs.json').read_bytes()),
            'build_sha256': c.sha((a.output / 'build.json').read_bytes()),
            'scope': 'Paired actual cloud motion and fresh repeats. Human appearance approval remains separate; no complete traversal/wrap claim.'})
    except Exception:
        c.save(a.output / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
