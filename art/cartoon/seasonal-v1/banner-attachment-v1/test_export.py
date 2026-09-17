"""Focused banner fit, frozen-filter replay, and registration refusal witness."""
import argparse
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
HELPER = HERE / 'export_v2.py'
RECIPE = HERE / 'recipe-v3.json'
OUTPUT = HERE / 'candidates/v3'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    a = p.parse_args()
    report_path = HERE / ('verification-v3-' + a.phase + '.json')
    assert not report_path.exists(), 'fresh verification report required'
    selected = json.loads((OUTPUT / 'export-report.json').read_bytes())
    runs = []

    def run(name, args, error=None, script=HELPER, witness=None):
        command = [sys.executable, '-B', str(script), *map(str, args)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        assert result.returncode == (1 if error else 0), (name, result.stdout, result.stderr)
        assert 'WITNESS banner-registration ' + sha(HELPER.read_bytes()) in result.stdout or script.name == 'export.py'
        assert result.stderr.strip() == ('FAIL ' + error if error else ''), (name, result.stderr)
        assert not witness or witness in result.stdout, (name, 'executed mutation witness absent')
        runs.append({'name': name, 'exit_code': result.returncode,
                     'command': ['python', '-B', script.relative_to(ROOT).as_posix(), *[str(x).replace(str(ROOT), '.') for x in args]],
                     'stdout': result.stdout, 'stderr': result.stderr})

    run('selected_export_readback', ['--recipe', RECIPE, '--output', OUTPUT, '--check'])
    assert selected['runtime_ready'] and selected['outside_runtime_alpha8_pixels'] == 0
    assert selected['outside_runtime_max_alpha'] == 4
    assert selected['alpha8_source_centers_hd'] == [0.3150000000000084, 0.355000000000004, 302.53499999999997, 93.965]
    for frame in range(3):
        name = f'BMP/HOLIDAY.BMP/{frame:03}.png'
        assert (OUTPUT / name).read_bytes() == (HERE.parent / 'candidates/v5' / name).read_bytes(), name
    result = {'schema_version': 1, 'status': 'PASS', 'phase': a.phase,
              'exporter_sha256': sha(HELPER.read_bytes()), 'test_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(RECIPE.read_bytes()),
              'export_report_sha256': sha((OUTPUT / 'export-report.json').read_bytes()),
              'runtime_sha256': sha((OUTPUT / 'BMP/HOLIDAY.BMP/003.png').read_bytes()),
              'unchanged_v5_frames': [0, 1, 2], 'outside_alpha8_pixels': 0,
              'outside_max_alpha': 4, 'outside_nonzero_pixels': 106,
              'scope': 'Technical export only. Small deliberate registration change; no human scene acceptance.'}
    if a.phase == 'regression':
        smoke = json.loads((HERE / 'verification-v3-smoke.json').read_bytes())
        assert smoke['status'] == 'PASS' and smoke['exporter_sha256'] == result['exporter_sha256']
        protected = [HERE.parent / 'export.py', HERE.parent / 'recipe-v5.json',
                     HERE / 'export.py', HERE / 'raw-v1.png', HERE / 'raw-v2.png',
                     *[p for name in ('diagnostic-v1', 'diagnostic-v2') for p in (HERE / name).rglob('*') if p.is_file()],
                     *[p for p in (HERE.parent / 'candidates/v5').rglob('*.png')]]
        before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
        work = ROOT / 'build/seasonal-v1/banner-attachment-verification-v3'
        assert not work.exists(), 'fresh regression work required'
        work.mkdir(parents=True)
        run('fresh_process_exact_replay', ['--recipe', RECIPE, '--output', work / 'replay'])
        for name, digest in selected['outputs_sha256'].items():
            assert sha((work / 'replay' / name).read_bytes()) == digest, name
        assert (work / 'replay/export-report.json').read_bytes() == (OUTPUT / 'export-report.json').read_bytes()
        spec = importlib.util.spec_from_file_location('selected_banner', HELPER)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        base = adapter.trial.load_base()
        prior = json.loads((HERE.parent / 'recipe-v5.json').read_bytes())['frames'][3]
        with Image.open(HERE.parent / prior['source']) as original:
            padded = base.resample(original, prior['runtime_canvas'], prior['affine_forward'])
        assert base.png(padded) == (HERE.parent / 'candidates/v1/padded/003.png').read_bytes(), 'original registered padded ancestor'
        assert base.png(padded.crop((32, 32, 336, 126))) == (HERE.parent / 'candidates/v5/BMP/HOLIDAY.BMP/003.png').read_bytes(), 'frozen V5 banner reproduction'
        result['original_registered_ancestor'] = {
            'raw_sha256': sha((HERE.parent / prior['source']).read_bytes()),
            'padded_sha256': sha(base.png(padded)),
            'runtime_sha256': sha(base.png(padded.crop((32,32,336,126)))),
            'meaningful_bounds_hd': [v-32 for v in padded.getchannel('A').point(lambda v:255 if v>=8 else 0).getbbox()]}
        for version in (1, 2):
            run(f'rejected_raw_v{version}_fixed_placement', ['--recipe', HERE / f'recipe-v{version}.json', '--output', work / f'refused-v{version}'],
                '003: meaningful source or filtered alpha overhang', HERE / 'export.py')
            assert not (work / f'refused-v{version}').exists()
        wrong = json.loads(RECIPE.read_bytes())
        wrong['frames'][0]['affine_forward'][2] += .1
        wrong['frames'][0]['target_anchor'][0] += .1
        bad = work / 'wrong-registration.json'
        bad.write_text(json.dumps(wrong), encoding='utf-8')
        run('003_wrong_registration_refused', ['--recipe', bad, '--output', work / 'refused-registration'],
            '003: source or fixed V5 recipe differs')
        source = inspect.getsource(adapter.original_render)
        guard = "    base.require(recipe == prepare(source_path), '003: source or fixed V5 recipe differs')"
        assert source.count(guard) == 1
        mutant = source.replace(guard, '    pass  # executed control: registration binding removed', 1)
        mutation = work / 'mutant_render.py'
        mutation.write_text(mutant, encoding='utf-8', newline='\n')
        driver = work / 'execute_mutant.py'
        helper_relative = HELPER.relative_to(ROOT).as_posix()
        driver.write_text(
            'import hashlib,importlib.util\nfrom pathlib import Path\n'
            'root=next(p for p in Path(__file__).resolve().parents if (p/"CMakeLists.txt").is_file())\n'
            f'path=root/{helper_relative!r}\n'
            's=importlib.util.spec_from_file_location("selected",path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\n'
            'raw=(Path(__file__).parent/"mutant_render.py").read_bytes()\n'
            'print("EXECUTED_MUTANT_SHA256="+hashlib.sha256(raw).hexdigest())\n'
            'exec(compile(raw,"mutant_render.py","exec"),m.trial.__dict__)\n'
            'm.original_render=m.trial.render; m.trial.render=m.render\n'
            'print("WITNESS banner-registration "+m.trial.sha(path.read_bytes()))\n'
            'raise SystemExit(m.trial.main())\n', encoding='utf-8', newline='\n')
        run('003_wrong_registration_accepted_only_after_guard_removal', ['--recipe', bad, '--output', work / 'mutant-output'],
            script=driver, witness='EXECUTED_MUTANT_SHA256=' + sha(mutation.read_bytes()))
        bad_png = (work / 'mutant-output/BMP/HOLIDAY.BMP/003.png').read_bytes()
        assert bad_png != (OUTPUT / 'BMP/HOLIDAY.BMP/003.png').read_bytes()
        run('restored_selected_positive', ['--recipe', RECIPE, '--output', OUTPUT, '--check'])
        after = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected}
        assert before == after, 'frozen ancestor changed'
        result['protected_files_sha256'] = before
        evidence = HERE / 'verification-v3'
        evidence.mkdir()
        for path in (mutation, driver, bad):
            (evidence / path.name).write_bytes(path.read_bytes())
        result['guard_removal'] = {'removed_guard': guard, 'mutant_sha256': sha(mutation.read_bytes()),
                                   'driver_sha256': sha(driver.read_bytes()), 'wrong_recipe_sha256': sha(bad.read_bytes()),
                                   'actual_wrong_runtime_sha256': sha(bad_png),
                                   'replay_note': 'Stage the three preserved files together anywhere below the repository and run execute_mutant.py with --recipe and a fresh --output. Scratch only.'}
    result['runs'] = runs
    report_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS banner-attachment ' + a.phase + ' ' + sha(report_path.read_bytes()))


if __name__ == '__main__':
    main()
