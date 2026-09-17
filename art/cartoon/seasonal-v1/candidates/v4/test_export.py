"""Focused decay-source replay and recipe-selection guard evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parents[2]
HELPER = HERE / 'export_v4.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    helper = HELPER.read_bytes()
    recipe_raw = (HERE / 'recipe-v4.json').read_bytes()
    approval_raw = (HERE / 'pumpkin-appearance-v4.json').read_bytes()
    approval = json.loads(approval_raw)
    recipe = json.loads(recipe_raw)
    assert approval['appearance_approved'] is True
    assert approval['raw_sha256'] == recipe['frames'][0]['source_sha256']
    runs = []

    def run(label, options=(), failure=None, script=HELPER, mutant=None):
        result = subprocess.run([sys.executable, '-B', str(script), *map(str, options)],
                                capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert result.returncode == (1 if failure else 0), (label, result.stdout, result.stderr)
        assert 'WITNESS seasonal-v4 ' + sha(helper) in result.stdout
        assert result.stderr.strip() == ('FAIL ' + failure if failure else ''), (label, result.stderr)
        assert failure or 'PASS seasonal-v4 ' in result.stdout
        assert not mutant or 'EXECUTED_MUTANT_SHA256=' + mutant in result.stdout
        runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS',
                     'stdout': result.stdout, 'stderr': result.stderr})

    run('v4_smoke_readback', ['--check'])
    report = {'schema_version': 1, 'status': 'PASS', 'phase': args.phase,
              'exporter_sha256': sha(helper), 'test_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(recipe_raw), 'appearance_approval_sha256': sha(approval_raw),
              'scope': 'Slight decay appearance approved separately after generation/export; recipe retains historical pending status. Placement remains diagnostic during shoreline investigation.'}
    if args.phase == 'regression':
        frozen = {p: sha(p.read_bytes()) for p in [HERE / 'export_v3.py', HERE / 'export_v2.py',
                  HERE / 'recipe-v3.json', HERE / 'recipe-v2.json', HERE / 'raw/000-v3.png',
                  *[p for p in (HERE / 'candidates/v3').rglob('*.png')]]}
        for frame in (1, 2, 3):
            name = f'BMP/HOLIDAY.BMP/{frame:03}.png'
            assert (HERE / 'candidates/v2' / name).read_bytes() == (HERE / 'candidates/v4' / name).read_bytes()
            assert (HERE / 'candidates/v3' / name).read_bytes() == (HERE / 'candidates/v4' / name).read_bytes()
        alpha = Image.open(HERE / 'candidates/v4/padded/000.png').getchannel('A')
        outside = [value for i, value in enumerate(alpha.get_flattened_data())
                   if not (32 <= i % alpha.width < 112 and 32 <= i // alpha.width < 100)]
        assert max(outside) == 3 and sum(value >= 8 for value in outside) == 0
        with tempfile.TemporaryDirectory(prefix='v4-check-', dir=HERE / 'candidates') as temporary:
            work = Path(temporary).resolve()
            assert work.is_relative_to((HERE / 'candidates').resolve())
            replay = work / 'replay'
            run('fresh_v4_replay', ['--output', replay])
            selected = json.loads((HERE / 'candidates/v4/export-report.json').read_bytes())
            for name, checksum in selected['outputs_sha256'].items():
                assert sha((replay / name).read_bytes()) == checksum
            assert (replay / 'export-report.json').read_bytes() == (HERE / 'candidates/v4/export-report.json').read_bytes()
            bad = json.loads(recipe_raw)
            bad['frames'][0]['affine_forward'][2] += .1
            bad_path = work / 'wrong-placement.json'
            bad_path.write_text(json.dumps(bad), encoding='utf-8')
            failure = 'recipe-v4: selected inputs or placement differ'
            run('000_translation_change_rejected', ['--recipe', bad_path, '--output', work / 'bad'], failure)
            run('000_prior_source_recipe_rejected', ['--recipe', HERE / 'recipe-v3.json', '--output', work / 'old'], failure)
            statement = "    base.require(recipe == selected_recipe(), 'recipe-v4: selected inputs or placement differ')"
            text = helper.decode('utf-8')
            assert text.count(statement) == 1
            mutant = text.replace(statement, '    pass  # executed control: v4 selection guard removed', 1).encode('utf-8')
            changed = work / 'mutant.py'
            changed.write_bytes(mutant)
            driver = work / 'execute_mutant.py'
            driver.write_text('from pathlib import Path\nimport hashlib\nraw=Path(' + repr(str(changed)) + ').read_bytes()\n'
                              + "print('EXECUTED_MUTANT_SHA256='+hashlib.sha256(raw).hexdigest())\n"
                              + 'exec(compile(raw,' + repr(str(HELPER)) + ',"exec"),{"__name__":"__main__","__file__":' + repr(str(HELPER)) + '})\n', encoding='utf-8')
            destination = work / 'mutant-result'
            run('000_translation_change_accepted_only_without_guard', ['--recipe', bad_path, '--output', destination],
                script=driver, mutant=sha(mutant))
            assert (destination / 'BMP/HOLIDAY.BMP/000.png').read_bytes() != (HERE / 'candidates/v4/BMP/HOLIDAY.BMP/000.png').read_bytes()
            report['guard_removal'] = {'sha256': sha(mutant), 'removed_statement': statement, 'actual_wrong_png_written': True}
        run('restored_v4_positive', ['--check'])
        assert HELPER.read_bytes() == helper and (HERE / 'recipe-v4.json').read_bytes() == recipe_raw
        assert all(sha(path.read_bytes()) == digest for path, digest in frozen.items())
        report.update(unchanged_frames_verified=[1, 2, 3], unchanged_frozen_files=len(frozen),
                      outside_runtime_alpha8_pixels=0, outside_runtime_max_alpha=3,
                      raw_alpha8_bounds=selected['frames'][0]['source_alpha8_bounds'])
    report['runs'] = runs
    (HERE / ('export-verification-v4-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS seasonal-v4 ' + args.phase)


if __name__ == '__main__':
    main()
