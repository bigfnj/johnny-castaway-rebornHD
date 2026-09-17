"""Bounded v2 placement smoke/replay; previous filter controls remain frozen."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
HELPER = HERE / 'export_v2.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    helper_hash = sha(HELPER.read_bytes())
    runs = []

    def invoke(name, options, failure=None):
        run = subprocess.run([sys.executable, '-B', str(HELPER), *map(str, options)], cwd=ROOT,
                             capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert run.returncode == (1 if failure else 0), (name, run.stdout, run.stderr)
        assert 'WITNESS seasonal-export ' + helper_hash in run.stdout
        assert run.stderr.strip() == ('FAIL ' + failure if failure else ''), (name, run.stderr)
        assert failure or 'PASS seasonal-export ' in run.stdout
        runs.append({'name': name, 'result': 'FIRED' if failure else 'PASS', 'stdout': run.stdout,
                     'stderr': run.stderr, 'returncode': run.returncode})

    invoke('v2_smoke_exact_readback', ['--check'])
    report = {'schema_version': 1, 'phase': args.phase, 'status': 'PASS', 'exporter_sha256': helper_hash,
              'test_sha256': sha(Path(__file__).read_bytes()), 'recipe_sha256': sha((HERE / 'recipe-v2.json').read_bytes()),
              'scope': 'Current Cartoon shoreline technical placement only; native contact and human approval pending.'}
    if args.phase == 'regression':
        old_recipe = (HERE / 'recipe.json').read_bytes()
        assert sha(old_recipe) == '13a3363b72338c07bdb5d75d242a98a547bf688cf5daa676cc0a0ce0f3761d83'
        assert (HERE / 'recipe-v1.json').read_bytes() == old_recipe
        assert sha((HERE / 'export.py').read_bytes()) == '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
        previous = json.loads((HERE / 'candidates/v1/export-report.json').read_bytes())
        assert all(sha((HERE / 'candidates/v1' / path).read_bytes()) == checksum
                   for path, checksum in previous['outputs_sha256'].items())
        old_functions = {n.name: ast.dump(n) for n in ast.parse((HERE / 'export.py').read_text()).body if isinstance(n, ast.FunctionDef)}
        new_functions = {n.name: ast.dump(n) for n in ast.parse(HELPER.read_text()).body if isinstance(n, ast.FunctionDef)}
        for name in ('prepare', 'render', 'resample'):
            assert old_functions[name] == new_functions[name], name + ': filter/render implementation changed'
        measurements = []
        for frame in range(4):
            name = f'BMP/HOLIDAY.BMP/{frame:03}.png'
            before = (HERE / 'candidates/v1' / name).read_bytes()
            after = (HERE / 'candidates/v2' / name).read_bytes()
            assert (before == after) == (frame == 3), name + ': changed/unchanged scope differs'
            image = Image.open(HERE / 'candidates/v2' / name).convert('RGBA')
            padded = Image.open(HERE / f'candidates/v2/padded/{frame:03}.png').convert('RGBA')
            width, height = image.size
            assert image.tobytes() == padded.crop((32, 32, 32+width, 32+height)).tobytes()
            outside = [padded.getpixel((x,y))[3] for y in range(padded.height) for x in range(padded.width)
                       if not (32 <= x < 32+width and 32 <= y < 32+height)]
            assert max(outside) < 8
            measurements.append({'frame': frame, 'png_sha256': sha(after), 'canvas': list(image.size),
                                 'changed_from_v1': before != after, 'outside_max_alpha': max(outside),
                                 'outside_alpha8_pixels': sum(a>=8 for a in outside)})
        with tempfile.TemporaryDirectory(prefix='v2-check-', dir=HERE / 'candidates') as directory:
            work = Path(directory).resolve()
            assert work.is_relative_to((HERE / 'candidates').resolve())
            replay = work / 'replay'
            invoke('v2_fresh_export_replay', ['--output', replay])
            for path in (HERE / 'candidates/v2').rglob('*'):
                if path.is_file():
                    assert path.read_bytes() == (replay / path.relative_to(HERE / 'candidates/v2')).read_bytes()
            invoke('v1_placement_recipe_rejected_by_v2', ['--recipe', HERE / 'recipe-v1.json', '--output', work / 'wrong'],
                   '000: fixed uniform registration differs')
        invoke('v2_positive_after_control', ['--check'])
        report.update(measurements=measurements, v1_recipe_and_outputs_preserved=True,
                      resample_prepare_render_function_bodies_unchanged=True,
                      previous_controls='export-verification-regression.json retains ten negatives, alpha0/visible RGB axes and executed fixed-registration guard removal for the unchanged guard/filter implementation. This run separately executes the old-placement rejection against v2.')
    report['runs'] = runs
    (HERE / ('export-verification-v2-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS seasonal-v2 ' + args.phase)


if __name__ == '__main__':
    main()
