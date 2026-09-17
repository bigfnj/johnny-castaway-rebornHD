"""Two low-tide additions against the frozen current-production native baseline."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import traceback

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
BASE = ROOT / 'build/low-tide-v1/baseline-native/captures-v1'
PRODUCTION = ROOT / 'assets/scrantic_data.zip'
CONTRACT = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/native-final/contract.py'
spec = importlib.util.spec_from_file_location('retained_native_contract', CONTRACT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
BASE_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
BASE_PINS = {
    'summary.json': 'b35db16764e93362d6392e0f281bb90148cc21a9c4ff9e19408c3ab618239063',
    'inputs.json': '71e3bef729d6934835135bb8b1b6f3b30d0450a8e0191de82f47281a1b50e981',
    'build.json': '7c506bde8596d57113509955271927f703b5c652252e29dc2408dfec00995839',
    'none/smoke/report.json': '7603f2022db205caa737bd21732dfd16df48a6bcf530faddb641aa45f5778626',
    'clover/smoke/report.json': 'f21469d5e5a47b1e39d53f04c3e9024efca7c620e67855d8eb03faefd3ca897b',
}
CASES = {'none': [0, 0, 0, 0, 1, 0, 24], 'clover': [2, 0, 0, 0, 1, 0, 24]}
ADDITIONS = {c.member(1): [768, 138], c.member(2): [128, 60]}
RECTS = ((498, 606, 1266, 744), (300, 656, 428, 716))


def packages(before, after):
    c.require(len(before) == 2598 and set(after) - set(before) == set(ADDITIONS)
              and set(before) <= set(after), '001/002 additions only')
    for name, row in before.items():
        c.require(after[name] == row, 'unchanged prior member ' + name)
    for name, canvas in ADDITIONS.items():
        c.require(after[name]['canvas'] == canvas, 'selected canvas ' + name)
    return {name: after[name] for name in ADDITIONS}


def scoped_pixels(before, after):
    c.require(len(before) == len(after) == 1280 * 960 * 3, 'native RGB dimensions')
    changed = 0
    for y in range(960):
        start = y * 3840
        cursor = 0
        for left, right in sorted((l, r) for l, t, r, b in RECTS if t <= y < b):
            c.require(before[start + cursor * 3:start + left * 3] == after[start + cursor * 3:start + left * 3],
                      'pixel outside BACKGRND001/002 rectangles')
            changed += sum(before[start + x * 3:start + x * 3 + 3] != after[start + x * 3:start + x * 3 + 3]
                           for x in range(left, right))
            cursor = right
        c.require(before[start + cursor * 3:start + 3840] == after[start + cursor * 3:start + 3840],
                  'pixel outside BACKGRND001/002 rectangles')
    return changed


def compare(observer, folder, name, actual):
    original = json.loads((BASE / name / 'smoke/report.json').read_bytes())
    c.compare_facts(original, actual)
    for key in ('background_draws', 'ground_surface_placement', 'wave_surface_placements', 'holiday_draws'):
        c.require(original[key] == actual[key], 'paired draw records ' + name + '/' + key)
    c.require(set(actual['loaded_art']) - set(original['loaded_art']) == set(ADDITIONS), 'selected 001/002 paths')
    c.require(set(original['loaded_art']) - set(actual['loaded_art']) ==
              {'data/hd/BMP/BACKGRND.BMP/001.png', 'data/hd/BMP/BACKGRND.BMP/002.png'}, 'only 001/002 fallback paths replaced')
    counts = []
    for old, new in zip(original['displays'], actual['displays']):
        old_pixels = observer.codec.ppm(BASE / name / 'smoke' / f"display-{old['ordinal']:03}.ppm")
        new_pixels = observer.codec.ppm(folder / f"display-{new['ordinal']:03}.ppm")
        c.require(c.sha(old_pixels) == old['pixels_sha256'], 'baseline raw pixels ' + name)
        c.require(c.sha(new_pixels) == new['pixels_sha256'], 'candidate raw pixels ' + name)
        counts.append(scoped_pixels(old_pixels, new_pixels))
    c.require(any(counts), 'visible 001/002 change ' + name)
    return counts


def controls(observer, before, after, output):
    left = observer.codec.ppm(BASE / 'none/smoke/final.ppm')
    right = observer.codec.ppm(output / 'none/smoke/final.ppm')
    altered = dict(after)
    wave = 'data/hd/BMP/BACKGRND.BMP/030.png'
    altered[wave] = dict(after[wave], sha256='0' * 64)
    wrong_canvas = dict(after)
    wrong_canvas[c.member(1)] = dict(after[c.member(1)], canvas=[767, 138])
    pixel = bytearray(right)
    pixel[0] = left[0] ^ 1
    tests = [
        ('changed_old_wave', lambda: packages(before, altered), 'unchanged prior member ' + wave),
        ('wrong_001_canvas', lambda: packages(before, wrong_canvas), 'selected canvas ' + c.member(1)),
        ('outside_pixel', lambda: scoped_pixels(left, bytes(pixel)), 'pixel outside BACKGRND001/002 rectangles'),
    ]
    results = []
    for name, call, label in tests:
        try:
            call()
        except ValueError as exc:
            c.require(str(exc) == 'final native: ' + label, 'named control ' + name)
            results.append({'name': name, 'status': 'FIRED', 'failure': str(exc)})
        else:
            raise ValueError('control survived: ' + name)
    packages(before, after)
    scoped_pixels(left, right)
    c.save(output / 'negative-controls.json', {'status': 'PASS', 'results': results,
        'method': 'Actual member metadata and native pixel copies damaged in memory; original files untouched; restored positives executed.',
        'adapter_sha256': c.sha(Path(__file__).read_bytes())})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--output', type=Path, default=Path('/out/captures-v1'))
    args = parser.parse_args()
    c.require(c.sha(args.candidate.read_bytes()) == args.candidate_sha256, 'explicit candidate SHA256')
    c.require(not args.output.exists(), 'fresh candidate output')
    args.output.mkdir()
    try:
        c.require(c.sha(PRODUCTION.read_bytes()) == BASE_SHA, 'current approved production archive')
        for relative, digest in BASE_PINS.items():
            c.require(c.sha((BASE / relative).read_bytes()) == digest, 'baseline evidence ' + relative)
        observer = c.load_observer()
        observer.verify_log = c.verify_log
        protected = observer.legacy.protected()
        prior_inputs = json.loads((BASE / 'inputs.json').read_bytes())
        c.require(protected == prior_inputs['protected_sha256'], 'runtime/production same as baseline build')
        for relative, digest in prior_inputs['helper_sha256'].items():
            c.require(c.sha((ROOT / relative).read_bytes()) == digest, 'baseline helper ' + relative)
        before, after = c.archive(PRODUCTION), c.archive(args.candidate)
        added = packages(before, after)
        build = json.loads((BASE / 'build.json').read_bytes())
        exe = args.output / 'integrated_shore_probe'
        shutil.copyfile(BASE / exe.name, exe)
        exe.chmod(0o755)
        c.require(c.sha(exe.read_bytes()) == build['executable_sha256'], 'exact baseline executable reuse')
        helpers = [Path(__file__), Path(__file__).with_name('run.py'), CONTRACT, c.OBSERVER,
                   c.OBSERVER.parent / 'driver.c', observer.LEGACY, observer.legacy.CODEC]
        helper_pins = {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helpers}
        c.save(args.output / 'inputs.json', {'baseline_sha256': BASE_SHA, 'candidate_sha256': args.candidate_sha256,
            'candidate_path': args.candidate.relative_to(ROOT).as_posix(), 'added_members': added,
            'unchanged_prior_members': len(before), 'total_members': len(after), 'rectangles_hd': RECTS,
            'baseline_evidence_sha256': BASE_PINS, 'executable_sha256': build['executable_sha256'],
            'build_reuse': 'Exact executable from pinned baseline build.json; no new compile claimed.',
            'cases': CASES, 'protected_sha256': protected, 'helper_sha256': helper_pins,
            'scope': 'Native Cartoon low tide, explicit state, seed 11, real wait calls. Old low-wave pixels and stamping behavior preserved. No pre-wave image, calendar policy, original-executable or artwork approval claim.'})
        canvases = {str(f): after[c.member(f)]['canvas'] for f in c.FRAMES}
        results = {}
        for name, case in CASES.items():
            folder = args.output / name / 'smoke'
            report = observer.one(exe, args.candidate, folder, case, True, canvases)
            counts = compare(observer, folder, name, report)
            results[name] = {'smoke': 'PASS', 'display_count': len(counts), 'duration_ms': report['duration_ms'],
                             'displayed_phases': report['displayed_phases'], 'changed_pixels': counts}
            c.save(args.output / 'smoke-progress.json', results)
        c.save(args.output / 'smoke.json', {'status': 'PASS', 'captures': 2, 'cases': results})
        print('PASS both candidate smokes before fresh repeats', flush=True)
        fields = ('displays', 'native_calls', 'native_returns', 'background_draws', 'ground_surface_placement',
                  'wave_surface_placements', 'holiday_draws', 'loaded_art', 'png_sha256')
        for name, case in CASES.items():
            original = json.loads((args.output / name / 'smoke/report.json').read_bytes())
            repeat = observer.one(exe, args.candidate, args.output / name / 'repeat', case, True, canvases)
            c.require(all(original[key] == repeat[key] for key in fields), 'fresh exact native repeat ' + name)
            results[name]['fresh_repeat'] = 'PASS'
        controls(observer, before, after, args.output)
        c.require(protected == observer.legacy.protected(), 'protected inputs stable')
        c.require(helper_pins == {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helpers}, 'helpers stable')
        c.require(c.sha(args.candidate.read_bytes()) == args.candidate_sha256, 'candidate archive stable')
        c.save(args.output / 'summary.json', {'status': 'PASS', 'baseline_sha256': BASE_SHA,
            'candidate_sha256': args.candidate_sha256, 'cases': results, 'smoke_captures': 2,
            'fresh_repeat_captures': 2, 'outside_001_002_pixels': 'EXACT', 'negative_controls': 3,
            'protected_inputs_unchanged': len(protected), 'accepted': False,
            'limitation': 'Old low-wave art remains and may visibly stamp opaque sand over the new beach. These are real displayed native frames, not a reconstructed static composite.'})
    except Exception:
        c.save(args.output / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
