"""Low-wave native captures over the separately approved static beach/rock."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import traceback

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
CONTRACT = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/native-final/contract.py'
spec = importlib.util.spec_from_file_location('retained_contract', CONTRACT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
BASE_SHA = 'f46e5cac5508b00cc7a675be4eaf843029cebfeabe80c849c8fa5f311813b92b'
PRODUCTION_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
FRAMES = tuple(range(30, 42))
# holiday, night, native x/y offset, low tide, public route mode, waits, raft
CASES = {
    'none': [0, 0, 0, 0, 1, 0, 32, 0],
    'clover': [2, 0, 0, 0, 1, 0, 32, 0],
    'night_shift': [2, 1, -80, 20, 1, 0, 32, 0],
    'raft1': [0, 0, 0, 0, 1, 0, 32, 1],
    'raft5': [0, 0, 0, 0, 1, 0, 32, 5],
    'high_control': [0, 0, 0, 0, 0, 0, 32, 0],
    'johnny_front': [0, 0, 0, 0, 1, 1, 32, 0],
    'johnny_rear': [0, 0, 0, 0, 1, 2, 32, 0],
}
GROUPS = {'initial': ('none', 'clover'),
          'extended': tuple(k for k in CASES if k not in ('none', 'clover')),
          'all': tuple(CASES)}


def hd(frame, resource='BACKGRND.BMP'):
    return f'data/hd/BMP/{resource}/{frame:03}.png'


def package(baseline, candidate=None):
    c.require(c.sha(baseline.read_bytes()) == BASE_SHA, 'approved static baseline archive')
    before = c.archive(baseline)
    production = c.archive(ROOT / 'assets/scrantic_data.zip')
    c.require(c.sha((ROOT / 'assets/scrantic_data.zip').read_bytes()) == PRODUCTION_SHA, 'production unchanged')
    c.require(set(before) - set(production) == {c.member(1), c.member(2)} and set(production) <= set(before), 'static baseline additions')
    c.require(all(before[n] == row for n, row in production.items()), 'static baseline retains production')
    after = c.archive(candidate) if candidate else before
    if candidate:
        c.require(set(after) - set(before) == {c.member(f) for f in FRAMES} and set(before) <= set(after), 'only twelve low-wave additions')
        c.require(all(after[n] == row for n, row in before.items()), 'candidate retains static baseline payloads')
        for f in FRAMES:
            c.require(after[c.member(f)]['canvas'] == before[hd(f)]['canvas'], f'{f:03} original low-wave canvas')
    return before, after


def verify(text, args, candidate, canvases):
    h, night, ox, oy, low, mode, waits, raft = args
    actual_state = f'STATE: seed=11 holiday={h} night={night} offset={ox},{oy} low={low} raft={raft} render=1280x960'
    c.require(text.count(actual_state) == 1, 'actual requested raft/state')
    # The retained parser assumes raft0. Validate the actual state above before
    # adapting only its parser input; the original capture log stays untouched.
    parsed = c.verify_log(text.replace(actual_state, actual_state.replace(f'raft={raft}', 'raft=0')),
                          args[:7], True, canvases)
    wave_rows = [r for r in parsed['background_draws'] if 30 <= r[0] <= 41]
    surfaces = [list(map(int, r)) for r in re.findall(r'LOW SURFACE: frame=(\d+) x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)', text)]
    c.require(len(wave_rows) == len(surfaces), 'every low-wave surface observed')
    for row, surface in zip(wave_rows, surfaces):
        f, x, y, dx, dy, scale, w, hh = row
        expected = ((233, 323), (367, 356), (558, 323), (129, 340))[(f - 30) // 3]
        c.require((x, y) == expected and [dx, dy, scale, w, hh] == [ox, oy, 2, *canvases[str(f)]], f'{f:03} low-wave logical origin/canvas')
        c.require(surface == [f, (x + ox) * 2, (y + oy) * 2, w, hh], f'{f:03} low-wave actual placement')
    raft_rows = [list(map(int, r)) for r in re.findall(r'RAFT DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)', text)]
    expected_raft = [[raft - 1, 529 if low else 512, 281 if low else 266, ox, oy, 2, *canvases['raft']]] if raft else []
    c.require(raft_rows == expected_raft, 'actual raft draw')
    if mode == 0:
        c.require(parsed['duration_ms'] >= 3840, 'complete 3840ms native wait cycle')
    parsed.update(low_surface_placements=surfaces, raft_draws=raft_rows, requested_raft=raft)
    return parsed


def pixel_scope(before, after, args, sizes):
    c.require(len(before) == len(after) == 1280 * 960 * 3, 'native RGB canvas')
    if not args[4]:
        c.require(before == after, 'high-tide exact pixels')
        return 0
    dx, dy = args[2] * 2, args[3] * 2
    rects = []
    for f in FRAMES:
        x, y = ((466, 646), (734, 712), (1116, 646), (258, 680))[(f - 30) // 3]
        w, h = sizes[str(f)]
        rects.append((max(0, x + dx), max(0, y + dy), min(1280, x + dx + w), min(960, y + dy + h)))
    changed = 0
    for y in range(960):
        start = y * 3840
        merged = []
        for l, r in sorted((l, r) for l, t, r, b in rects if t <= y < b):
            if merged and l <= merged[-1][1]:
                merged[-1][1] = max(r, merged[-1][1])
            else:
                merged.append([l, r])
        cursor = 0
        for l, r in merged:
            c.require(before[start + cursor * 3:start + l * 3] == after[start + cursor * 3:start + l * 3], 'pixel outside low-wave rectangles')
            changed += sum(before[start + x * 3:start + x * 3 + 3] != after[start + x * 3:start + x * 3 + 3] for x in range(l, r))
            cursor = r
        c.require(before[start + cursor * 3:start + 3840] == after[start + cursor * 3:start + 3840], 'pixel outside low-wave rectangles')
    return changed


def compare(observer, old_folder, folder, actual, args, sizes):
    old = json.loads((old_folder / 'report.json').read_bytes())
    c.require([[r[k] for k in c.TIMING] for r in old['displays']] == [[r[k] for k in c.TIMING] for r in actual['displays']], 'paired timing/phases/Johnny')
    for key in ('native_calls', 'native_returns', 'holiday_draws', 'ground_surface_placement', 'raft_draws'):
        c.require(old[key] == actual[key], 'paired ' + key)
    static = lambda rows: [r for r in rows if not 30 <= r[0] <= 41]
    c.require(static(old['background_draws']) == static(actual['background_draws']), 'paired non-low-wave draw records')
    counts = []
    for l, r in zip(old['displays'], actual['displays']):
        lp = observer.codec.ppm(old_folder / f"display-{l['ordinal']:03}.ppm")
        rp = observer.codec.ppm(folder / f"display-{r['ordinal']:03}.ppm")
        c.require(c.sha(lp) == l['pixels_sha256'] and c.sha(rp) == r['pixels_sha256'], 'recorded raw display identity')
        counts.append(pixel_scope(lp, rp, args, sizes))
    return counts


def controls(observer, output, name, args, sizes):
    folder = output / name / 'smoke'
    log = (folder / 'capture.log').read_text()
    pixels = observer.codec.ppm(folder / 'final.ppm')
    damaged = bytearray(pixels)
    damaged[0] ^= 1
    tests = [('raft_state', lambda: verify(log.replace('raft=0 render=', 'raft=1 render='), args, True, sizes), 'actual requested raft/state'),
             ('low_surface', lambda: verify(log.replace('LOW SURFACE: frame=30 x=466 ', 'LOW SURFACE: frame=30 x=467 ', 1), args, True, sizes), '030 low-wave actual placement'),
             ('outside_pixel', lambda: pixel_scope(pixels, bytes(damaged), args, sizes), 'pixel outside low-wave rectangles')]
    rows = []
    for name, call, label in tests:
        try:
            call()
        except ValueError as exc:
            c.require(str(exc) == 'final native: ' + label, 'named negative ' + name)
            rows.append({'name': name, 'status': 'FIRED', 'failure': str(exc)})
        else:
            raise ValueError('control survived: ' + name)
    verify(log, args, True, sizes)
    pixel_scope(pixels, pixels, args, sizes)
    c.save(output / 'negative-controls.json', {'status': 'PASS', 'controls': rows, 'adapter_sha256': c.sha(Path(__file__).read_bytes()),
        'method': 'Actual captured log/pixels copied and damaged in memory; restored positives rerun; no capture edits.'})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path)
    p.add_argument('--candidate-sha256')
    p.add_argument('--baseline-captures', type=Path)
    p.add_argument('--group', choices=GROUPS, default='initial')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    c.require(not a.output.exists(), 'fresh wave output')
    if a.candidate:
        c.require(a.candidate_sha256 and c.sha(a.candidate.read_bytes()) == a.candidate_sha256, 'explicit wave candidate hash')
        c.require(a.baseline_captures is not None, 'matching baseline capture root')
    a.output.mkdir(parents=True)
    try:
        before, after = package(a.baseline, a.candidate)
        observer = c.load_observer()
        observer.HERE = HERE
        observer.verify_log = verify
        protected = observer.legacy.protected()
        helper_paths = (Path(__file__), HERE / 'driver.c', HERE / 'run.py', CONTRACT, c.OBSERVER,
                        c.OBSERVER.parent / 'driver.c', observer.LEGACY, observer.legacy.CODEC)
        helpers = {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helper_paths}
        selected = {str(f): after[c.member(f) if c.member(f) in after else hd(f)]['canvas'] for f in (*c.FRAMES, *FRAMES)}
        archive = a.candidate or a.baseline
        c.save(a.output / 'inputs.json', {'baseline_sha256': BASE_SHA, 'archive_sha256': c.sha(archive.read_bytes()),
            'candidate': bool(a.candidate), 'cases': {n: CASES[n] for n in GROUPS[a.group]},
            'protected_sha256': protected, 'helpers_sha256': helpers,
            'members': {n: row['sha256'] for n, row in after.items() if n not in before},
            'scope': 'Explicit native state, unchanged engine, requested tick timing. Candidate true-alpha waves activate existing restore/redraw logic; low-wave draw row counts can differ from fallback stamping. No calendar or original-executable claim.'})
        exe = observer.build(a.output)
        results = {}
        for name in GROUPS[a.group]:
            args = CASES[name]
            sizes = dict(selected, raft=after[hd(args[7] - 1, 'MRAFT.BMP')]['canvas'] if args[7] else [0, 0])
            report = observer.one(exe, archive, a.output / name / 'smoke', args, True, sizes)
            c.require({c.member(1), c.member(2)} <= set(report['loaded_art']), 'approved static selected paths')
            if a.candidate:
                c.require({c.member(f) for f in FRAMES} <= set(report['loaded_art']), 'twelve selected low-wave paths')
            row = {'smoke': 'PASS', 'display_count': len(report['displays']), 'duration_ms': report['duration_ms'], 'displayed_phases': report['displayed_phases']}
            if a.candidate:
                row['changed_pixels'] = compare(observer, a.baseline_captures / name / 'smoke', a.output / name / 'smoke', report, args, sizes)
            results[name] = row
            c.save(a.output / 'smoke-progress.json', results)
        c.save(a.output / 'smoke.json', {'status': 'PASS', 'cases': results})
        print('PASS all selected smoke cases before repeats', flush=True)
        for name in GROUPS[a.group]:
            args = CASES[name]
            sizes = dict(selected, raft=after[hd(args[7] - 1, 'MRAFT.BMP')]['canvas'] if args[7] else [0, 0])
            old = json.loads((a.output / name / 'smoke/report.json').read_bytes())
            fresh = observer.one(exe, archive, a.output / name / 'repeat', args, True, sizes)
            fields = ('displays', 'native_calls', 'native_returns', 'background_draws', 'low_surface_placements', 'raft_draws', 'holiday_draws', 'png_sha256')
            c.require(all(old[k] == fresh[k] for k in fields), 'fresh native repeat ' + name)
            results[name]['fresh_repeat'] = 'PASS'
        if 'none' in GROUPS[a.group]:
            controls(observer, a.output, 'none', CASES['none'], dict(selected, raft=[0, 0]))
        c.require(protected == observer.legacy.protected(), 'protected runtime/production stable')
        c.require(helpers == {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helper_paths}, 'observer inputs stable')
        c.require(c.sha(archive.read_bytes()) == (a.candidate_sha256 if a.candidate else BASE_SHA), 'selected archive stable')
        c.save(a.output / 'summary.json', {'status': 'PASS', 'archive_sha256': c.sha(archive.read_bytes()), 'candidate': bool(a.candidate),
            'group': a.group, 'cases': results, 'pending_cases': [n for n in CASES if n not in results],
            'inputs_sha256': c.sha((a.output / 'inputs.json').read_bytes()), 'build_sha256': c.sha((a.output / 'build.json').read_bytes()),
            'scope': 'Native technical captures only. Artwork approval and unexecuted case groups remain separate.'})
    except Exception:
        c.save(a.output / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
