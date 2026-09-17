"""Focused full-source placement proof, replay and executed registration mutant."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
HELPER = HERE / 'export.py'
SELECTED = HERE.parent / 'foam-refresh-v1/candidates/v2'
OUTPUT = HERE / 'candidates/v1'
RECIPE = HERE / 'recipe-v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    a = p.parse_args()
    report_path = HERE / ('verification-' + a.phase + '.json')
    assert not report_path.exists(), 'fresh verification report required'
    helper = HELPER.read_bytes()
    recipe = json.loads(RECIPE.read_bytes())
    selected = json.loads((OUTPUT / 'export-report.json').read_bytes())
    runs = []

    def run(name, args, error=None, script=HELPER, witness=None):
        proc = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                              capture_output=True, text=True, timeout=60)
        assert proc.returncode == (1 if error else 0), (name, proc.stdout, proc.stderr)
        assert 'WITNESS side-fit ' + sha(helper) in proc.stdout
        assert proc.stderr.strip() == ('FAIL ' + error if error else ''), (name, proc.stderr)
        assert not witness or witness in proc.stdout, (name, 'executed mutant witness absent')
        runs.append({'name': name, 'exit_code': proc.returncode,
                     'command': ['python', '-B', script.relative_to(ROOT).as_posix(), *[str(x).replace(str(ROOT), '.') for x in args]],
                     'stdout': proc.stdout, 'stderr': proc.stderr})

    run('ten_frame_export_readback', ['--check'])
    assert [r['frame'] for r in selected['frames']] == [0, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert selected['resample_count'] == 0
    for frame in (0, 6, 7, 8):
        name = f'BMP/BACKGRND.BMP/{frame:03}.png'
        assert (OUTPUT / name).read_bytes() == (SELECTED / name).read_bytes(), name
    result = {'schema_version': 1, 'status': 'PASS', 'phase': a.phase,
              'exporter_sha256': sha(helper), 'test_sha256': sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(RECIPE.read_bytes()),
              'export_report_sha256': sha((OUTPUT / 'export-report.json').read_bytes()),
              'unchanged_frames': [0, 6, 7, 8],
              'scope': 'Technical source retention and selected integer placement. Native geometry and human appearance remain separate checks.'}
    if a.phase == 'regression':
        smoke = json.loads((HERE / 'verification-smoke.json').read_bytes())
        assert smoke['status'] == 'PASS' and smoke['exporter_sha256'] == sha(helper)
        protected_paths = [ROOT / 'assets/scrantic_data.zip', ROOT / recipe['mask_helper'],
                           ROOT / recipe['selected_recipe'], ROOT / recipe['selected_report'],
                           *[SELECTED / r['path'] for r in recipe['frames']]]
        before = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected_paths}
        work = ROOT / 'build/shoreline-repair-v1/side-fit-verification-v1'
        assert not work.exists(), 'fresh regression work required'
        work.mkdir(parents=True)
        run('fresh_exact_export_replay', ['--output', work / 'replay'])
        for name, digest in selected['outputs_sha256'].items():
            assert sha((work / 'replay' / name).read_bytes()) == digest, name
        assert (work / 'replay/export-report.json').read_bytes() == (OUTPUT / 'export-report.json').read_bytes()
        ground = Image.open(SELECTED / 'BMP/BACKGRND.BMP/000.png').convert('RGBA')
        proof = []
        with zipfile.ZipFile(ROOT / 'assets/scrantic_data.zip') as archive:
            for row in selected['frames']:
                frame = row['frame']
                if frame not in (3, 4, 5, 9, 10, 11):
                    continue
                source_raw = archive.read(row['source_member'])
                assert sha(source_raw) == row['source_member_sha256']
                assert sha(source_raw) != row['previous_selected_png_sha256'], 'source must be unmasked original'
                source = Image.open(io.BytesIO(source_raw)).convert('RGBA')
                unmasked = Image.open(OUTPUT / f'unmasked/{frame:03}.png').convert('RGBA')
                runtime = Image.open(OUTPUT / row['path']).convert('RGBA')
                left = frame < 6
                expected_canvas, paste, origin = ((150, 66), (0, 8), (534, 612)) if left else ((154, 74), (10, 10), (1036, 606))
                assert unmasked.size == runtime.size == expected_canvas
                assert row['footprint'] == {'id': 'cartoon-island-left-foam-v1' if left else 'cartoon-island-right-foam-v1',
                                            'canvas': list(expected_canvas), 'offset_hd': [-6, 0] if left else [0, 0]}
                x, y = paste
                cropback = unmasked.crop((x, y, x+source.width, y+source.height))
                assert cropback.tobytes() == source.tobytes(), f'{frame:03}: independent full RGBA cropback'
                unaffected = affected = padding = 0
                for py in range(runtime.height):
                    for px in range(runtime.width):
                        value = unmasked.getpixel((px, py))
                        actual = runtime.getpixel((px, py))
                        if not (x <= px < x+source.width and y <= py < y+source.height):
                            assert value == actual == (0, 0, 0, 0), f'{frame:03}: blank nonsource padding'
                            padding += 1
                        gx, gy = px+origin[0]-540, py+origin[1]-548
                        ga = ground.getpixel((gx, gy))[3] if 0 <= gx < 640 and 0 <= gy < 180 else 0
                        expected = (*value[:3], (value[3]*(255-ga)+127)//255)
                        assert actual == expected, (frame, px, py, 'world-aligned mask')
                        unaffected += value[3] > 0 and actual[3] == value[3]
                        affected += actual[3] != value[3]
                assert unaffected > 0 and affected > 0, f'{frame:03}: nondegenerate visibility cases'
                proof.append({'frame': frame, 'source_cropback_exact_rgba_sha256': sha(cropback.tobytes()),
                              'source_pixels_cropped': 0, 'blank_padding_pixels': padding,
                              'nonzero_foam_alpha_unchanged_pixels': unaffected,
                              'visibility_changed_alpha_pixels': affected,
                              'all_output_rgb_exact_to_integer_paste': True})
        bad = json.loads(RECIPE.read_bytes())
        row = next(r for r in bad['frames'] if r['frame'] == 3)
        row['source_paste_hd'][0] = 1
        row['source_translation_hd'][0] = -5
        wrong = work / 'wrong-003-placement.json'
        wrong.write_text(json.dumps(bad), encoding='utf-8')
        failure = '003: original source or placement contract differs'
        run('003_wrong_placement_refused', ['--recipe', wrong, '--output', work / 'refused'], failure)
        masked = json.loads(RECIPE.read_bytes())
        row = next(r for r in masked['frames'] if r['frame'] == 3)
        row['source_member_sha256'] = row['previous_selected_png_sha256']
        masked_recipe = work / 'wrong-003-masked-source.json'
        masked_recipe.write_text(json.dumps(masked), encoding='utf-8')
        run('003_already_masked_source_identity_refused', ['--recipe', masked_recipe, '--output', work / 'refused-masked'], failure)
        statement = '        require(row == selected, f"{row[\'frame\']:03}: original source or placement contract differs")'
        text = helper.decode('utf-8')
        assert text.count(statement) == 1
        mutant = text.replace(statement, '        pass  # executed control: placement/source binding removed', 1)
        mutant_path = work / 'mutant_export.py'
        mutant_path.write_text(mutant, encoding='utf-8', newline='\n')
        driver = work / 'execute_mutant.py'
        driver.write_text('from pathlib import Path\nimport hashlib\n'
                          'root=next(p for p in Path(__file__).resolve().parents if (p/"CMakeLists.txt").is_file())\n'
                          f'helper=root/{HELPER.relative_to(ROOT).as_posix()!r}\n'
                          'raw=(Path(__file__).parent/"mutant_export.py").read_bytes()\n'
                          'print("EXECUTED_MUTANT_SHA256="+hashlib.sha256(raw).hexdigest())\n'
                          'exec(compile(raw,str(helper),"exec"),{"__name__":"__main__","__file__":str(helper)})\n',
                          encoding='utf-8', newline='\n')
        run('003_wrong_placement_accepted_only_after_guard_removal', ['--recipe', wrong, '--output', work / 'mutant-output'],
            script=driver, witness='EXECUTED_MUTANT_SHA256=' + sha(mutant_path.read_bytes()))
        wrong_png = (work / 'mutant-output/BMP/BACKGRND.BMP/003.png').read_bytes()
        assert wrong_png != (OUTPUT / 'BMP/BACKGRND.BMP/003.png').read_bytes()
        run('restored_export_positive', ['--check'])
        assert HELPER.read_bytes() == helper
        assert before == {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in protected_paths}
        evidence = HERE / 'verification-v1'
        evidence.mkdir()
        for path in (mutant_path, driver, wrong, masked_recipe):
            (evidence / path.name).write_bytes(path.read_bytes())
        result.update(independent_frame_proof=proof, protected_files_sha256=before,
                      fresh_replay_files=len(selected['outputs_sha256'])+1,
                      guard_removal={'statement': statement, 'mutant_sha256': sha(mutant_path.read_bytes()),
                                     'driver_sha256': sha(driver.read_bytes()),
                                     'wrong_placement_recipe_sha256': sha(wrong.read_bytes()),
                                     'actual_wrong_003_png_sha256': sha(wrong_png),
                                     'restored_positive': 'PASS',
                                     'replay_note': 'Stage preserved control files together below repository root. Execute driver with --recipe wrong-003-placement.json and a fresh scratch --output only.'})
    result['runs'] = runs
    report_path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS side-fit ' + a.phase + ' ' + sha(report_path.read_bytes()))


if __name__ == '__main__':
    main()
