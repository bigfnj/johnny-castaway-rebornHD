"""Side-placement A/B with the frozen real native driver and capture/build APIs.

The local log validator follows the pinned observer's contracts, with expanded
ground/center on both sides and per-package side offsets. Logs are never rewritten.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import traceback
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
OBSERVER = HERE.parents[1] / 'native/capture.py'
OBSERVER_SHA = 'f2e0684f6726ce53951988b5d44c101d3efe44f07e6b3b66277499a9f12a1bae'
DRIVER_SHA = 'beb8beae0c3b54562fe51285d184d55ccd2b185fe34cf97b7801d2536abd1b59'
BASE_SHA = 'ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac'
REPORT = HERE.parent / 'candidates/v1/export-report.json'
REPORT_SHA = '8489c4449c6fbfe82f8bd4e66a3e4edfd4bec71c4e5d36c5c9999711c6786323'
RECIPE_SHA = '3002ca095bd647a2e513b92659d5943811ae1787aeacd5181191602670a1e50d'
SIDES = (3, 4, 5, 9, 10, 11)
FRAMES = (0, *range(3, 12))
CASES = {
    'high_clover': [2, 0, 0, 0, 0, 0, 20],
    'night_shift_clover': [2, 1, -80, 20, 0, 0, 20],
    'low_clover': [2, 0, 0, 0, 1, 0, 24],
    'johnny_front': [0, 0, 0, 0, 0, 1, 1],
    'johnny_rear': [0, 0, 0, 0, 0, 2, 1],
}
TIMING = ('ordinal', 'ticks', 'time_ms', 'segment', 'phases', 'johnny')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('side native: ' + label)


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def member(frame):
    return f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'


def selected_rows():
    require(sha(REPORT.read_bytes()) == REPORT_SHA, 'selected export report identity')
    require(sha((HERE.parent / 'recipe-v1.json').read_bytes()) == RECIPE_SHA, 'selected recipe identity')
    report = json.loads(REPORT.read_bytes())
    require([r['frame'] for r in report['frames']] == list(FRAMES), 'ordered ten selected frames')
    return report['frames']


def package_pair(baseline, candidate, candidate_sha=None):
    require(sha(baseline.read_bytes()) == BASE_SHA, 'selected offshore baseline identity')
    if candidate_sha:
        require(sha(candidate.read_bytes()) == candidate_sha, 'candidate archive identity')
    maps, canvases = {}, {}
    for label, path in (('baseline', baseline), ('candidate', candidate)):
        with zipfile.ZipFile(path) as archive:
            require(len(archive.namelist()) == len(set(archive.namelist())) == 2598, label+' 2598 unique members')
            maps[label] = {n: sha(archive.read(n)) for n in archive.namelist()}
            canvases[label] = {str(f): list(struct.unpack('>II', archive.read(member(f))[16:24])) for f in FRAMES}
    before, after = maps['baseline'], maps['candidate']
    require(before.keys() == after.keys(), 'same ZIP membership')
    require({n for n in before if before[n] != after[n]} == {member(f) for f in SIDES}, 'only six side PNG payloads change')
    for row in selected_rows():
        f = row['frame']
        require(after[member(f)] == row['sha256'], f'{f:03} selected export payload')
        require(canvases['candidate'][str(f)] == row['canvas'], f'{f:03} selected canvas')
    require(canvases['baseline'] == {str(f): ([640,180] if f == 0 else [144,58] if f < 6 else [384,256] if f < 9 else [144,64]) for f in FRAMES}, 'baseline registered canvases')
    return {'baseline_sha256': BASE_SHA, 'candidate_sha256': sha(candidate.read_bytes()),
            'member_count': 2598, 'unchanged_members': 2592,
            'changed_members': {member(f): {'before': before[member(f)], 'after': after[member(f)]} for f in SIDES},
            'canvases': canvases, 'selected_export_report_sha256': REPORT_SHA}


def load_observer():
    require(sha(OBSERVER.read_bytes()) == OBSERVER_SHA, 'frozen observer identity')
    require(sha((OBSERVER.parent / 'driver.c').read_bytes()) == DRIVER_SHA, 'frozen driver identity')
    spec = importlib.util.spec_from_file_location('side_fit_native_observer', OBSERVER)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    return observer


def verify_log(text, args, candidate, canvases):
    """Validate actual log coordinates directly; both variants have expanded ground."""
    holiday, night, ox, oy, low, mode, waits = args
    require(f'STATE: seed=11 holiday={holiday} night={night} offset={ox},{oy} low={low} raft=0 render=1280x960' in text, 'actual native state')
    require('DONE: native calls returned; cleanup complete' in text, 'native cleanup returned')
    backdrop = 'NIGHT.SCR' if night else 'OCEAN02.SCR'
    require('island backdrop: '+backdrop in text, 'selected native backdrop')
    bg = [list(map(int, r)) for r in re.findall(r'BG DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)', text)]
    require([r for r in bg if r[0] == 0] == [[0,288,279,ox,oy,2,640,180]], 'logical expanded ground origin/canvas')
    ground = [list(map(int, r)) for r in re.findall(r'GROUND SURFACE: x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)', text)]
    require(ground == [[540+ox*2,548+oy*2,640,180]], 'actual expanded ground surface')
    props = [list(map(int, r)) for r in re.findall(r'PROP DRAW: frame=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) scale=(\d+) canvas=(\d+)x(\d+)', text)]
    require(props == ([[1,333,286,ox,oy,2,240,94]] if holiday == 2 else []), 'unchanged clover origin/canvas')
    wave_rows = [r for r in bg if 3 <= r[0] <= 11]
    surfaces = [list(map(int, r)) for r in re.findall(r'WAVE SURFACE: frame=(\d+) x=(-?\d+) y=(-?\d+) canvas=(\d+)x(\d+)', text)]
    require(len(surfaces) == len(wave_rows), 'every high-wave surface observed')
    for actual, row in zip(surfaces, wave_rows):
        f, x, y, dx, dy, scale, w, h = row
        expected_xy = ((270,306),(364,319),(518,303))[(f-3)//3]
        require((x,y) == expected_xy and [dx,dy,scale,w,h] == [ox,oy,2,*canvases[str(f)]], f'{f:03} logical wave origin/canvas')
        offset = (-32,-90) if 6 <= f <= 8 else (-6,0) if candidate and 3 <= f <= 5 else (0,0)
        require(actual == [f,(x+dx)*2+offset[0],(y+dy)*2+offset[1],w,h], f'{f:03} actual registered wave surface')
    displays = []
    for row in re.findall(r'DISPLAY: n=(\d+) ticks=(\d+) segment=(\d+) phases=(-?\d+),(-?\d+),(-?\d+),(-?\d+) johnny=(-?\d+),(\d+),(-?\d+),(-?\d+)', text):
        n, t, segment, *tail = map(int, row)
        displays.append({'ordinal': n, 'ticks': t, 'time_ms': t*20, 'segment': segment, 'phases': tail[:4], 'johnny': tail[4:]})
    require(displays and [r['ordinal'] for r in displays] == list(range(1,len(displays)+1)), 'contiguous displays')
    require(displays[0]['ticks'] == 0 and all(a['ticks'] <= b['ticks'] for a,b in zip(displays,displays[1:])), 'actual native timing')
    calls = [list(map(int,r)) for r in re.findall(r'NATIVE CALL: segment=(\d+) args=(\d+),(\d+),(\d+),(\d+)',text)]
    expected = [[i+1,0,0,0,0] for i in range(waits)] if mode == 0 else ([[1,3,7,3,7],[2,3,7,5,3]] if mode == 1 else [[1,1,3,1,3],[2,1,3,4,5]])
    require(calls == expected, 'exact public native calls')
    returns = [list(map(int,r)) for r in re.findall(r'NATIVE RETURN: segment=(\d+) ticks=(\d+)',text)]
    require([r[0] for r in returns] == [r[0] for r in calls], 'every native call returned')
    seen = {f for row in displays for f in row['phases'] if f >= 0}
    if not low:
        require(displays[0]['phases'] == [3,7,9,-1], 'initial high phases')
    if mode == 0:
        require(seen == set(range(30,42) if low else range(3,12)), 'complete low/high phase coverage')
    if low:
        require(not wave_rows and not surfaces, 'no high-wave drawing at low tide')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)',text)))
    require({member(f) for f in FRAMES} <= set(loaded), 'selected ten background dependencies')
    if holiday:
        require({f'data/styles/cartoon/BMP/HOLIDAY.BMP/{f:03}.png' for f in range(4)} <= set(loaded), 'four unchanged holiday dependencies')
    return {'displays': displays, 'native_calls': calls, 'native_returns': returns,
            'background_draws': bg, 'ground_surface_placement': ground, 'wave_surface_placements': surfaces,
            'holiday_draws': props, 'displayed_phases': sorted(seen), 'backdrop': backdrop,
            'loaded_art': loaded, 'duration_ms': displays[-1]['time_ms']}


def scoped_pixels(before, after, offset, low=False):
    require(len(before) == len(after) == 1280*960*3, 'native pixel dimensions')
    if low:
        require(before == after, 'low tide exact full-scene pixels')
        return 0
    dx, dy = 2*offset[0], 2*offset[1]
    # Union of old and new side CANVASES. No middle/ground-wide permission.
    rectangles = [(534+dx,612+dy,684+dx,678+dy), (1036+dx,606+dy,1190+dx,680+dy)]
    changed = 0
    for y in range(960):
        line = y*1280*3
        spans = sorted((l,r) for l,t,r,b in rectangles if t <= y < b)
        cursor = 0
        for left, right in spans:
            require(before[line+cursor*3:line+left*3] == after[line+cursor*3:line+left*3], 'pixel outside old/new side rectangles')
            changed += sum(before[line+x*3:line+x*3+3] != after[line+x*3:line+x*3+3] for x in range(left,right))
            cursor = right
        require(before[line+cursor*3:line+3840] == after[line+cursor*3:line+3840], 'pixel outside old/new side rectangles')
    return changed


def compare_facts(before, after):
    require([[r[k] for k in TIMING] for r in before['displays']] == [[r[k] for k in TIMING] for r in after['displays']], 'paired timelines/phases/Johnny positions')
    require(before['native_calls'] == after['native_calls'] and before['native_returns'] == after['native_returns'], 'paired public calls and returns')
    require([r[:6] for r in before['background_draws']] == [r[:6] for r in after['background_draws']], 'paired logical background draws')


def controls(observer, output, pair):
    folder = output / 'high_clover'
    text = (folder / 'candidate/smoke/capture.log').read_text()
    canvases = pair['canvases']['candidate']
    before = observer.codec.ppm(folder / 'baseline/smoke/final.ppm')
    after = observer.codec.ppm(folder / 'candidate/smoke/final.ppm')
    damaged = bytearray(after)
    # The gap between side rectangles must remain protected, despite expanded ground.
    at = (650*1280+800)*3
    damaged[at] = before[at] ^ 1
    low = observer.codec.ppm(output / 'low_clover/candidate/smoke/final.ppm')
    low_bad = bytearray(low); low_bad[0] ^= 1
    altered = re.sub(r'(phases=\d+,)8(,)', r'\g<1>7\2', text)
    require(altered != text, 'phase mutation changed actual log')
    tests = [
        ('actual_left_offset', lambda: verify_log(text.replace('WAVE SURFACE: frame=3 x=534 ', 'WAVE SURFACE: frame=3 x=535 '), CASES['high_clover'], True, canvases), '003 actual registered wave surface'),
        ('native_timestamp', lambda: verify_log(text.replace('DISPLAY: n=1 ticks=0 ', 'DISPLAY: n=1 ticks=1 '), CASES['high_clover'], True, canvases), 'actual native timing'),
        ('phase_omission', lambda: verify_log(altered, CASES['high_clover'], True, canvases), 'complete low/high phase coverage'),
        ('middle_gap_pixel', lambda: scoped_pixels(before, bytes(damaged), [0,0]), 'pixel outside old/new side rectangles'),
        ('low_tide_changed_pixel', lambda: scoped_pixels(low, bytes(low_bad), [0,0], True), 'low tide exact full-scene pixels'),
    ]
    results = []
    for name, call, label in tests:
        try:
            call()
        except ValueError as error:
            require(str(error) == 'side native: '+label, 'named negative '+name)
            results.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('side native: negative survived '+name)
    verify_log(text, CASES['high_clover'], True, canvases)
    scoped_pixels(before, after, [0,0])
    scoped_pixels(low, low, [0,0], True)
    save(output / 'negative-controls.json', {'status': 'PASS', 'adapter_sha256': sha(Path(__file__).read_bytes()),
                                            'package_pair': pair, 'results': results, 'restored_positive': 'PASS',
                                            'method': 'Actual immutable native logs and pixels damaged only in memory; no renderer or captured file changes.'})


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--candidate-sha256', required=True)
    p.add_argument('--runtime-commit', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'fresh output')
    a.output.mkdir(parents=True)
    try:
        observer = load_observer()
        observer.verify_log = verify_log
        pair = package_pair(a.baseline, a.candidate, a.candidate_sha256)
        protected = observer.legacy.protected()
        require(protected['assets/scrantic_data.zip'] == observer.legacy.PRODUCTION_SHA, 'production archive unchanged')
        snapshot = a.output / 'source-snapshot'
        for name, digest in protected.items():
            if name == 'assets/scrantic_data.zip':
                continue
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
            require(sha(target.read_bytes()) == digest, 'source snapshot '+name)
        helper_paths = [*HERE.glob('*.py'), OBSERVER, OBSERVER.parent/'driver.c', observer.LEGACY, observer.legacy.CODEC]
        helpers = {q.relative_to(ROOT).as_posix(): sha(q.read_bytes()) for q in helper_paths}
        for q in helper_paths:
            target = a.output/'helper-snapshot'/q.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(q.read_bytes())
        save(a.output/'inputs.json', {'pair': pair, 'cases': CASES, 'protected_sha256': protected,
                                     'helpers_sha256': helpers, 'runtime_commit_authorized_by_root': a.runtime_commit,
                                     'scope': 'Both variants have selected expanded ground and center waves. Actual port timing and public calls, not original-executable or calendar parity.'})
        exe = observer.build(a.output)
        results = {}
        for name, args in CASES.items():
            rows = {}
            for side, archive in (('baseline', a.baseline), ('candidate', a.candidate)):
                rows[side] = observer.one(exe, archive, a.output/name/side/'smoke', args, side == 'candidate', pair['canvases'][side])
            compare_facts(rows['baseline'], rows['candidate'])
            counts = []
            for left, right in zip(rows['baseline']['displays'], rows['candidate']['displays']):
                before = observer.codec.ppm(a.output/name/'baseline/smoke'/f"display-{left['ordinal']:03}.ppm")
                after = observer.codec.ppm(a.output/name/'candidate/smoke'/f"display-{right['ordinal']:03}.ppm")
                counts.append(scoped_pixels(before, after, args[2:4], bool(args[4])))
            require(bool(args[4]) or any(counts), name+' side changes visible')
            results[name] = {'args': args, 'smoke': 'PASS', 'display_count': len(counts),
                             'changed_pixel_counts': counts, 'displayed_phases': rows['baseline']['displayed_phases'],
                             'duration_ms': rows['baseline']['duration_ms']}
        save(a.output/'smoke.json', {'status': 'PASS', 'variant_case_captures': 10, 'cases': results})
        for name, args in CASES.items():
            for side, archive in (('baseline', a.baseline), ('candidate', a.candidate)):
                prior = json.loads((a.output/name/side/'smoke/report.json').read_bytes())
                fresh = observer.one(exe, archive, a.output/name/side/'repeat', args, side == 'candidate', pair['canvases'][side])
                require(all(prior[k] == fresh[k] for k in ('displays', 'native_calls', 'native_returns', 'background_draws', 'wave_surface_placements', 'png_sha256')), name+'/'+side+' fresh native repeat')
            results[name]['fresh_repeat'] = 'PASS'
        controls(observer, a.output, pair)
        require(protected == observer.legacy.protected(), 'compiled sources and production stable during run')
        require(helpers == {q.relative_to(ROOT).as_posix(): sha(q.read_bytes()) for q in helper_paths}, 'capture helpers stable during run')
        require(package_pair(a.baseline, a.candidate, a.candidate_sha256) == pair, 'private package pair stable')
        save(a.output/'summary.json', {'status': 'PASS', 'phase': 'full', 'package_pair': pair, 'cases': results,
                                      'smoke_captures': 10, 'fresh_repeat_captures': 10,
                                      'protected_inputs_unchanged': len(protected), 'accepted': False,
                                      'scope': 'Tentative side placement A/B; no production promotion or human approval.'})
    except Exception:
        save(a.output/'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
