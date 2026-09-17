"""Focused v3 replay and recipe guard evidence; the frozen filter is reused."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parents[2]
HELPER = HERE / 'export_v3.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    helper = HELPER.read_bytes()
    recipe_raw = (HERE / 'recipe-v3.json').read_bytes()
    runs = []

    def run(label, options=(), failure=None, script=HELPER, mutant=None):
        result = subprocess.run([sys.executable, '-B', str(script), *map(str, options)],
                                capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert result.returncode == (1 if failure else 0), (label, result.stdout, result.stderr)
        assert 'WITNESS seasonal-v3 ' + sha(helper) in result.stdout
        assert result.stderr.strip() == ('FAIL ' + failure if failure else ''), (label, result.stderr)
        assert failure or 'PASS seasonal-v3 ' in result.stdout
        assert not mutant or 'EXECUTED_MUTANT_SHA256=' + mutant in result.stdout
        runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS', 'stdout': result.stdout, 'stderr': result.stderr})

    run('v3_smoke_readback', ['--check'])
    report = {'schema_version': 1, 'status': 'PASS', 'phase': args.phase, 'exporter_sha256': sha(helper),
              'test_sha256': sha(Path(__file__).read_bytes()), 'recipe_sha256': sha(recipe_raw),
              'scope': 'Approved pumpkin face source technical export; composed batch/production approval remains separate.'}
    if args.phase == 'regression':
        for frame in (1, 2, 3):
            name = f'BMP/HOLIDAY.BMP/{frame:03}.png'
            assert (HERE / 'candidates/v2' / name).read_bytes() == (HERE / 'candidates/v3' / name).read_bytes()
        spec = importlib.util.spec_from_file_location('seasonal_v3_checked', HELPER)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        recipe = json.loads(recipe_raw)
        row = recipe['frames'][0]
        image = Image.open(HERE / row['source']).convert('RGBA')
        hidden = image.copy()
        hidden.putdata([(17, 211, 83, a) if a == 0 else (r, g, b, a) for r, g, b, a in image.get_flattened_data()])
        assert adapter.base.resample(image, row['runtime_canvas'], row['affine_forward']).tobytes() == adapter.base.resample(hidden, row['runtime_canvas'], row['affine_forward']).tobytes()
        with tempfile.TemporaryDirectory(prefix='v3-check-', dir=HERE / 'candidates') as temporary:
            work = Path(temporary).resolve()
            assert work.is_relative_to((HERE / 'candidates').resolve())
            replay = work / 'replay'
            run('fresh_v3_replay', ['--output', replay])
            selected = json.loads((HERE / 'candidates/v3/export-report.json').read_bytes())
            for name, checksum in selected['outputs_sha256'].items():
                assert sha((replay / name).read_bytes()) == checksum
            assert (replay / 'export-report.json').read_bytes() == (HERE / 'candidates/v3/export-report.json').read_bytes()
            bad = json.loads(recipe_raw)
            bad['frames'][0]['affine_forward'][0] = .1401
            bad['frames'][0]['affine_forward'][4] = .1401
            bad_path = work / 'wrong-placement.json'
            bad_path.write_text(json.dumps(bad), encoding='utf-8')
            run('changed_placement_rejected', ['--recipe', bad_path, '--output', work / 'bad'], 'recipe-v3: selected inputs or placement differ')
            run('prior_source_recipe_rejected', ['--recipe', HERE / 'recipe-v2.json', '--output', work / 'old'], 'recipe-v3: selected inputs or placement differ')
            statement = "    base.require(recipe == selected_recipe(), 'recipe-v3: selected inputs or placement differ')"
            text = helper.decode('utf-8')
            assert text.count(statement) == 1
            mutant = text.replace(statement, '    pass  # executed control: v3 selection guard removed', 1).encode('utf-8')
            changed = work / 'mutant.py'
            changed.write_bytes(mutant)
            driver = work / 'execute_mutant.py'
            driver.write_text('from pathlib import Path\nimport hashlib\nraw=Path(' + repr(str(changed)) + ').read_bytes()\n'
                              + "print('EXECUTED_MUTANT_SHA256='+hashlib.sha256(raw).hexdigest())\n"
                              + 'exec(compile(raw,' + repr(str(HELPER)) + ',"exec"),{"__name__":"__main__","__file__":' + repr(str(HELPER)) + '})\n', encoding='utf-8')
            destination = work / 'mutant-result'
            run('changed_placement_accepted_only_without_guard', ['--recipe', bad_path, '--output', destination], script=driver, mutant=sha(mutant))
            assert (destination / row['path']).read_bytes() != (HERE / 'candidates/v3' / row['path']).read_bytes()
            report['guard_removal'] = {'sha256': sha(mutant), 'removed_statement': statement, 'actual_wrong_png_written': True}
        run('restored_v3_positive', ['--check'])
        assert HELPER.read_bytes() == helper and (HERE / 'recipe-v3.json').read_bytes() == recipe_raw
        report.update(unchanged_frames_verified=[1,2,3], new_source_hidden_rgb_independence=True,
                      meaningful_filtered_alpha_outside_runtime=selected['frames'][0]['outside_runtime_alpha8_pixels'],
                      raw_alpha8_bounds=selected['frames'][0]['source_alpha8_bounds'])
    report['runs'] = runs
    (HERE / ('export-verification-v3-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS seasonal-v3 ' + args.phase)


if __name__ == '__main__':
    main()
