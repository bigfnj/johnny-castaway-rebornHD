"""Actual seasonal export replay, alpha checks and named damaged-input controls."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parents[1]
HELPER = HERE / 'export.py'
ROOT = HERE.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    source = HELPER.read_bytes()
    recipe_bytes = (HERE / 'recipe.json').read_bytes()
    recipe = json.loads(recipe_bytes)
    raw_hashes = {row['source']: sha((HERE / row['source']).read_bytes()) for row in recipe['frames']}
    runs = []

    def invoke(label, options, failure=None, script=HELPER, mutant=None):
        result = subprocess.run([sys.executable, '-B', str(script), *map(str, options)],
                                cwd=ROOT, text=True, encoding='utf-8', capture_output=True, timeout=90)
        assert result.returncode == (1 if failure else 0), (label, result.stdout, result.stderr)
        assert 'WITNESS seasonal-export ' + sha(source) in result.stdout, label
        if failure:
            assert result.stderr.strip() == 'FAIL ' + failure, (label, result.stderr)
        else:
            assert 'PASS seasonal-export ' in result.stdout and not result.stderr, label
        if mutant:
            assert 'EXECUTED_MUTANT_SHA256=' + mutant in result.stdout, label
        runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS', 'returncode': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})

    invoke('current_candidate_reproduces', ['--check'])
    report = {'schema_version': 1, 'phase': args.phase, 'status': 'PASS',
              'exporter_sha256': sha(source), 'test_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(recipe_bytes), 'source_sha256': raw_hashes,
              'scope': 'Technical export and reproducibility; no human scene acceptance.'}
    if args.phase == 'regression':
        spec = importlib.util.spec_from_file_location('seasonal_export_under_test', HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reference = json.loads((HERE / 'reference/source.json').read_bytes())
        measured = []
        for row, original in zip(recipe['frames'], reference['frames']):
            frame = row['frame']
            assert row['runtime_canvas'] == [2 * n for n in original['native_canvas']]
            fixed = Image.open(HERE / 'candidates/v1' / row['path']).convert('RGBA')
            padded = Image.open(HERE / f'candidates/v1/padded/{frame:03}.png').convert('RGBA')
            w, h = fixed.size
            assert list(fixed.size) == row['runtime_canvas']
            assert fixed.tobytes() == padded.crop((32, 32, 32 + w, 32 + h)).tobytes()
            outside = [padded.getpixel((x, y))[3] for y in range(padded.height) for x in range(padded.width)
                       if not (32 <= x < 32 + w and 32 <= y < 32 + h)]
            assert max(outside) < 8, f'{frame:03}: meaningful filtered alpha outside runtime'
            measured.append({'frame': frame, 'canvas': list(fixed.size), 'outside_max_alpha': max(outside),
                             'outside_alpha8_pixels': sum(a >= 8 for a in outside)})
        # The wide clover source contains hidden RGB haze. Change every alpha0
        # RGB value: premultiplication must make that entire axis invisible.
        row = recipe['frames'][1]
        im = Image.open(HERE / row['source']).convert('RGBA')
        changed_hidden = im.copy()
        changed_hidden.putdata([(255, 0, 255, a) if a == 0 else (r, g, b, a)
                                for r, g, b, a in im.get_flattened_data()])
        a = module.resample(im, row['runtime_canvas'], row['affine_forward'])
        b = module.resample(changed_hidden, row['runtime_canvas'], row['affine_forward'])
        assert a.tobytes() == b.tobytes(), 'hidden alpha0 RGB changed the export'
        # A nondegenerate visible-color control must still affect the result.
        changed_visible = im.copy()
        changed_visible.putdata([(255-r, 255-g, 255-b, alpha) if alpha >= 128 else (r, g, b, alpha)
                                 for r, g, b, alpha in im.get_flattened_data()])
        c = module.resample(changed_visible, row['runtime_canvas'], row['affine_forward'])
        assert a.tobytes() != c.tobytes() and a.getchannel('A').tobytes() == c.getchannel('A').tobytes()
        report['independent_measurements'] = measured
        report['alpha0_hidden_rgb_control'] = 'PASS: all hidden RGB replaced, identical full padded output'
        report['visible_rgb_control'] = 'PASS: visible colors changed output while alpha stayed exact'
        with tempfile.TemporaryDirectory(prefix='verify-', dir=HERE / 'candidates') as directory:
            work = Path(directory).resolve()
            assert work.is_relative_to((HERE / 'candidates').resolve())
            replay = work / 'replay'
            invoke('fresh_full_export', ['--output', replay])
            for path in (HERE / 'candidates/v1').rglob('*'):
                if path.is_file():
                    assert path.read_bytes() == (replay / path.relative_to(HERE / 'candidates/v1')).read_bytes()

            def bad(label, edit, expected):
                value = json.loads(recipe_bytes)
                edit(value)
                path = work / (label + '.json')
                path.write_text(json.dumps(value), encoding='utf-8')
                invoke(label, ['--recipe', path, '--output', work / (label + '-out')], expected)
                return path

            bad('wrong_source_hash', lambda r: r['frames'][0].update(source_sha256='0'*64), '000: source hash differs')
            bad('wrong_slot_source', lambda r: r['frames'][0].update(source='raw/003-v1.png'), '000: slot/source identity differs')
            bad('missing_frame', lambda r: r['frames'].pop(), 'recipe: frame coverage differs')
            bad('wrong_runtime_canvas', lambda r: r['frames'][0].update(runtime_canvas=[81, 68]), '000: runtime canvas differs')
            bad('wrong_filter', lambda r: r['resampling'].update(oversample=4), 'recipe: render contract differs')
            bad('false_acceptance', lambda r: r.update(accepted=True), 'recipe: render contract differs')
            bad('stale_reference', lambda r: r.update(reference_sha256='0'*64), 'recipe: reference identity differs')

            def scale_change(r):
                r['frames'][0]['scale'] = .1621
                r['frames'][0]['affine_forward'][0] = .1621
                r['frames'][0]['affine_forward'][4] = .1621
            bad_scale = bad('changed_uniform_scale', scale_change, '000: fixed uniform registration differs')
            png_path = replay / 'BMP/HOLIDAY.BMP/000.png'
            altered = bytearray(png_path.read_bytes())
            altered[-1] ^= 1
            png_path.write_bytes(altered)
            invoke('changed_output_png', ['--check', '--output', replay], 'BMP/HOLIDAY.BMP/000.png: reproduced bytes differ')
            invoke('existing_output_refused', ['--output', replay], 'output: refusing to overwrite')

            statement = "        require(row['scale'] == config['scale'] and row['affine_forward'] == expected_affine(frame) and row['raw_anchor'] == config['raw_anchor'] and row['target_anchor'] == config['target_anchor'], label + ': fixed uniform registration differs')"
            text = source.decode('utf-8')
            assert text.count(statement) == 1
            mutant = text.replace(statement, '        pass  # executed control: fixed registration guard removed', 1).encode('utf-8')
            mutant_path = work / 'guard_removed.py'
            mutant_path.write_bytes(mutant)
            driver = work / 'execute_mutant.py'
            driver.write_text('from pathlib import Path\nimport hashlib\n'
                              + 'raw = Path(' + repr(str(mutant_path)) + ').read_bytes()\n'
                              + "print('EXECUTED_MUTANT_SHA256=' + hashlib.sha256(raw).hexdigest())\n"
                              + 'scope = {"__name__": "__main__", "__file__": ' + repr(str(HELPER)) + '}\n'
                              + 'exec(compile(raw, ' + repr(str(HELPER)) + ', "exec"), scope)\n', encoding='utf-8')
            mutant_output = work / 'mutant-output'
            invoke('wrong_scale_accepted_only_after_guard_removal', ['--recipe', bad_scale, '--output', mutant_output], script=driver, mutant=sha(mutant))
            assert (mutant_output / 'BMP/HOLIDAY.BMP/000.png').read_bytes() != (HERE / 'candidates/v1/BMP/HOLIDAY.BMP/000.png').read_bytes()
            report['guard_removal'] = {'sha256': sha(mutant), 'removed_statement': statement,
                                      'witness': 'EXECUTED_MUTANT_SHA256=' + sha(mutant),
                                      'result': 'Same changed scale is rejected by original, accepted and changes real PNG bytes only after guard removal.'}
        invoke('restored_positive', ['--check'])
        assert HELPER.read_bytes() == source and (HERE / 'recipe.json').read_bytes() == recipe_bytes
        assert all(sha((HERE / path).read_bytes()) == checksum for path, checksum in raw_hashes.items())
    report['runs'] = runs
    report['negative_controls_fired'] = sum(r['result'] == 'FIRED' for r in runs)
    (HERE / ('export-verification-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS seasonal export ' + args.phase + ': ' + str(report['negative_controls_fired']) + ' named negatives')


if __name__ == '__main__':
    main()
