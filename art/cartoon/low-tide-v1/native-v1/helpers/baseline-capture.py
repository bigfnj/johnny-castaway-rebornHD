"""Current-production low-tide baseline only, using the frozen native observer."""
import importlib.util
import json
from pathlib import Path
import traceback

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
CONTRACT = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1/native-final/contract.py'
spec = importlib.util.spec_from_file_location('retained_native_contract', CONTRACT)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
ARCHIVE = ROOT / 'assets/scrantic_data.zip'
EXPECTED = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
OUT = Path('/out/captures-v1')
CASES = {'none': [0, 0, 0, 0, 1, 0, 24], 'clover': [2, 0, 0, 0, 1, 0, 24]}


def main():
    c.require(not OUT.exists(), 'fresh low-tide baseline output')
    OUT.mkdir()
    try:
        c.require(c.sha(ARCHIVE.read_bytes()) == EXPECTED, 'current approved production archive')
        observer = c.load_observer()
        observer.verify_log = c.verify_log
        protected = observer.legacy.protected()
        members = c.archive(ARCHIVE)
        canvases = {str(f): members[c.member(f)]['canvas'] for f in c.FRAMES}
        helpers = [Path(__file__), CONTRACT, c.OBSERVER, c.OBSERVER.parent / 'driver.c', observer.LEGACY, observer.legacy.CODEC]
        helper_hashes = {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helpers}
        c.save(OUT / 'inputs.json', {
            'archive': {'path': 'assets/scrantic_data.zip', 'sha256': EXPECTED, 'members': len(members)},
            'cases': CASES, 'protected_sha256': protected, 'helper_sha256': helper_hashes,
            'scope': 'Fresh current Cartoon production baseline only. Explicit low-tide/holiday state, seed 11, daytime OCEAN02, no scene offset, no Johnny route. Real native repeated wait calls; requested tick timings, not wall-clock playback. No package comparison or original-executable claim.',
            'adapter_note': 'The reused verifier candidate=True selects the already-approved current footprint/Cartoon holiday rules. No prior-production baseline or 14-change package contract is invoked.'
        })
        exe = observer.build(OUT)
        results = {}
        for name, args in CASES.items():
            report = observer.one(exe, ARCHIVE, OUT / name / 'smoke', args, True, canvases)
            results[name] = {'smoke': 'PASS', 'display_count': len(report['displays']),
                             'duration_ms': report['duration_ms'], 'displayed_phases': report['displayed_phases']}
            c.save(OUT / 'smoke-progress.json', results)
        c.save(OUT / 'smoke.json', {'status': 'PASS', 'captures': 2, 'cases': results})
        print('PASS both smoke captures before fresh-process repeats', flush=True)
        fields = ('displays', 'native_calls', 'native_returns', 'background_draws',
                  'ground_surface_placement', 'wave_surface_placements', 'holiday_draws', 'png_sha256')
        for name, args in CASES.items():
            prior = json.loads((OUT / name / 'smoke/report.json').read_bytes())
            fresh = observer.one(exe, ARCHIVE, OUT / name / 'repeat', args, True, canvases)
            c.require(all(prior[k] == fresh[k] for k in fields), 'fresh exact native repeat ' + name)
            results[name]['fresh_repeat'] = 'PASS'
        c.require(protected == observer.legacy.protected(), 'protected runtime/production stable')
        c.require(helper_hashes == {p.relative_to(ROOT).as_posix(): c.sha(p.read_bytes()) for p in helpers}, 'capture helpers stable')
        c.save(OUT / 'summary.json', {'status': 'PASS', 'archive_sha256': EXPECTED,
            'cases': results, 'smoke_captures': 2, 'fresh_repeat_captures': 2,
            'protected_inputs_unchanged': len(protected), 'scope': 'Current approved production low-tide baseline. No new artwork, native code edits or comparative claims.'})
    except Exception:
        c.save(OUT / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
