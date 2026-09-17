"""V5 source/placement checks, fresh reproduction and executed guard witness."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parents[2]
HELPER = HERE / 'export_v5.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    helper = HELPER.read_bytes()
    recipe_raw = (HERE / 'recipe-v5.json').read_bytes()
    selected = json.loads((HERE / 'candidates/v5/export-report.json').read_bytes())
    recipe = json.loads(recipe_raw)
    original = json.loads((HERE / 'recipe-v1.json').read_bytes())
    runs = []

    def run(label, options=(), failure=None, script=HELPER, mutant=None):
        result = subprocess.run([sys.executable, '-B', str(script), *map(str, options)],
                                capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert result.returncode == (1 if failure else 0), (label, result.stdout, result.stderr)
        assert 'WITNESS seasonal-v5 ' + sha(helper) in result.stdout
        assert result.stderr.strip() == ('FAIL ' + failure if failure else ''), (label, result.stderr)
        assert failure or 'PASS seasonal-v5 ' in result.stdout
        assert not mutant or 'EXECUTED_MUTANT_SHA256=' + mutant in result.stdout
        runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS',
                     'stdout': result.stdout, 'stderr': result.stderr})

    run('v5_smoke_readback', ['--check'])
    report = {'schema_version': 1, 'status': 'PASS', 'phase': args.phase,
              'exporter_sha256': sha(helper), 'test_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(recipe_raw), 'export_report_sha256': sha((HERE / 'candidates/v5/export-report.json').read_bytes()),
              'scope': 'Original V1 registration and retained001-003; approved decay source000. No native/island/tide compatibility claim.'}
    if args.phase == 'regression':
        frozen = {p: sha(p.read_bytes()) for p in [HERE / 'export.py', HERE / 'recipe-v1.json',
                  HERE / 'raw/000-v3.png', HERE / 'pumpkin-appearance-v4.json',
                  *[p for p in (HERE / 'candidates/v1').rglob('*.png')]]}
        for frame in (1, 2, 3):
            name = f'BMP/HOLIDAY.BMP/{frame:03}.png'
            assert (HERE / 'candidates/v1' / name).read_bytes() == (HERE / 'candidates/v5' / name).read_bytes()
        for current, prior in zip(recipe['frames'], original['frames']):
            for field in ('runtime_canvas', 'scale', 'raw_anchor', 'target_anchor', 'affine_forward'):
                assert current[field] == prior[field], (current['frame'], field)
        alpha = Image.open(HERE / 'candidates/v5/padded/000.png').getchannel('A')
        outside = [value for i, value in enumerate(alpha.get_flattened_data())
                   if not (32 <= i % alpha.width < 112 and 32 <= i // alpha.width < 100)]
        assert max(outside) == 4 and sum(value > 0 for value in outside) == 63
        assert sum(value >= 8 for value in outside) == 0
        with tempfile.TemporaryDirectory(prefix='v5-check-', dir=HERE / 'candidates/v5') as temporary:
            work = Path(temporary).resolve()
            assert work.is_relative_to((HERE / 'candidates/v5').resolve())
            replay = work / 'replay'
            run('fresh_v5_replay', ['--output', replay])
            for name, checksum in selected['outputs_sha256'].items():
                assert sha((replay / name).read_bytes()) == checksum
            assert (replay / 'export-report.json').read_bytes() == (HERE / 'candidates/v5/export-report.json').read_bytes()
            reduced = json.loads(recipe_raw)
            prior_reduced = json.loads((HERE / 'recipe-v4.json').read_bytes())['frames'][0]
            for field in ('scale', 'raw_anchor', 'target_anchor', 'affine_forward'):
                reduced['frames'][0][field] = prior_reduced[field]
            reduced_path = work / 'wrong-reduced-placement.json'
            reduced_path.write_text(json.dumps(reduced), encoding='utf-8')
            stale = json.loads(recipe_raw)
            for field in ('source', 'source_sha256'):
                stale['frames'][0][field] = original['frames'][0][field]
            stale_path = work / 'wrong-stale-source.json'
            stale_path.write_text(json.dumps(stale), encoding='utf-8')
            failure = 'recipe-v5: selected inputs or V1 registration differ'
            run('000_reduced_placement_rejected', ['--recipe', reduced_path, '--output', work / 'bad'], failure)
            run('000_stale_source_rejected', ['--recipe', stale_path, '--output', work / 'old'], failure)
            statement = "    base.require(recipe == selected_recipe(), 'recipe-v5: selected inputs or V1 registration differ')"
            text = helper.decode('utf-8')
            assert text.count(statement) == 1
            mutant = text.replace(statement, '    pass  # executed control: V5 selection guard removed', 1).encode('utf-8')
            changed = work / 'mutant.py'
            changed.write_bytes(mutant)
            driver = work / 'execute_mutant.py'
            driver.write_text('from pathlib import Path\nimport hashlib\nraw=Path(' + repr(str(changed)) + ').read_bytes()\n'
                              + "print('EXECUTED_MUTANT_SHA256='+hashlib.sha256(raw).hexdigest())\n"
                              + 'exec(compile(raw,' + repr(str(HELPER)) + ',"exec"),{"__name__":"__main__","__file__":' + repr(str(HELPER)) + '})\n', encoding='utf-8')
            destination = work / 'mutant-result'
            run('000_reduced_placement_accepted_only_without_guard', ['--recipe', reduced_path, '--output', destination],
                script=driver, mutant=sha(mutant))
            wrong_png = (destination / 'BMP/HOLIDAY.BMP/000.png').read_bytes()
            assert wrong_png != (HERE / 'candidates/v5/BMP/HOLIDAY.BMP/000.png').read_bytes()
            report['guard_removal'] = {'sha256': sha(mutant), 'removed_statement': statement,
                                       'actual_wrong_png_written': True, 'wrong_png_sha256': sha(wrong_png)}
        run('restored_v5_positive', ['--check'])
        assert HELPER.read_bytes() == helper and (HERE / 'recipe-v5.json').read_bytes() == recipe_raw
        assert all(sha(path.read_bytes()) == digest for path, digest in frozen.items())
        report.update(unchanged_v1_frames_verified=[1, 2, 3], unchanged_frozen_files=len(frozen),
                      all_four_original_transforms_equal=True, outside_runtime_alpha8_pixels=0,
                      outside_runtime_max_alpha=4, outside_runtime_nonzero_pixels=63)
    report['runs'] = runs
    (HERE / ('export-verification-v5-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS seasonal-v5 ' + args.phase)


if __name__ == '__main__':
    main()
