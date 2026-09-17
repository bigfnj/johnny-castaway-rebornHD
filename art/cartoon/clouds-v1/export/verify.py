"""Focused fresh replay and invalid-binding controls for the private cloud export."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
ROOT = BUNDLE.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    helper = BUNDLE / 'export.py'
    helper_sha = sha(helper.read_bytes().replace(b'\r\n', b'\n'))
    recipe = json.loads((BUNDLE / 'recipe.json').read_bytes())
    scratch = ROOT / 'build/clouds-v1/export-controls'
    scratch.mkdir(parents=True, exist_ok=True)
    cases = [('fresh_replay', [], None)]
    for name, field, value in [('wrong_016_source_hash', 'source_sha256', '0' * 64),
                                ('wrong_017_registration', 'affine_forward', [.390625, 0, -36.28125, 0, .390625, -130.640625])]:
        changed = copy.deepcopy(recipe)
        changed['frames'][0 if '016' in name else 1][field] = value
        path = scratch / (name + '.json')
        path.write_text(json.dumps(changed, indent=2) + '\n', encoding='utf-8', newline='\n')
        cases.append((name, ['--recipe', str(path)], 'recipe: selected source, prompt or fixed registration binding differs'))
    cases.append(('wrong_baseline_archive', ['--baseline', str(ROOT / 'art/cartoon/character-inventory-v1/reference-originals.zip')], 'baseline archive: identity differs'))
    cases.append(('restored_positive', [], None))
    results = []
    for name, arguments, failure in cases:
        result = subprocess.run([sys.executable, '-B', str(helper), '--check'] + arguments,
                                cwd=ROOT, text=True, capture_output=True)
        lines = result.stdout.splitlines()
        assert lines[0] == 'WITNESS cloud-export ' + helper_sha, name
        assert not result.stderr, (name, result.stderr)
        if failure:
            assert result.returncode == 1 and lines == [lines[0], 'FAIL ' + failure], (name, result.stdout)
        else:
            assert result.returncode == 0 and lines[1].startswith('PASS cloud-export '), (name, result.stdout)
        results.append({'name': name, 'arguments': ['--check'] + arguments, 'exit_code': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
    # Replay the real CLI from a different miniature checkout. Historical JSON
    # retains the old absolute request paths; every referenced file is copied.
    relocated = Path(tempfile.mkdtemp(prefix='relocated-', dir=scratch))
    copied = set(recipe['inputs_sha256']) | {'art/cartoon/clouds-v1/export.py',
        'art/cartoon/clouds-v1/recipe.json', recipe['filter']['path'],
        'art/cartoon/clouds-v1/reference/backgrnd-016-original.png',
        'art/cartoon/clouds-v1/reference/backgrnd-017-original.png'}
    for name in sorted(copied):
        target = relocated / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    moved_bundle = relocated / 'art/cartoon/clouds-v1'
    result = subprocess.run([sys.executable, '-B', str(moved_bundle / 'export.py'),
        '--baseline', str(ROOT / 'assets/scrantic_data.zip'), '--candidate', str(relocated / 'candidate.zip')],
        cwd=relocated, text=True, capture_output=True)
    assert result.returncode == 0 and 'WITNESS cloud-export ' + helper_sha in result.stdout, result.stdout + result.stderr
    assert (relocated / 'candidate.zip').read_bytes() == (ROOT / 'build/clouds-v1/candidate.zip').read_bytes()
    for name in json.loads((HERE / 'export-report.json').read_bytes())['outputs_sha256']:
        assert (moved_bundle / 'export' / name).read_bytes() == (HERE / name).read_bytes(), name
    escape_probe = "import importlib.util,sys; from pathlib import Path; s=importlib.util.spec_from_file_location('export',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print('WITNESS cloud-export '+m.lf_sha(Path(sys.argv[1]).read_bytes())); m.resolve_reference('D:/old/art/cartoon/clouds-v1/../outside.png',Path(sys.argv[2]))"
    escaped = subprocess.run([sys.executable, '-B', '-c', escape_probe, str(moved_bundle / 'export.py'), str(relocated)],
                             cwd=relocated, text=True, capture_output=True)
    assert escaped.returncode == 1 and 'WITNESS cloud-export ' + helper_sha in escaped.stdout
    assert escaped.stderr.splitlines()[-1] == 'ValueError: recorded reference: escaping or invalid batch path', escaped.stderr
    foreign_probe = escape_probe.replace('D:/old/art/cartoon/clouds-v1/../outside.png', 'D:/old/art/cartoon/other-batch/input.png')
    foreign = subprocess.run([sys.executable, '-B', '-c', foreign_probe, str(moved_bundle / 'export.py'), str(relocated)],
                             cwd=relocated, text=True, capture_output=True)
    assert foreign.returncode == 1 and 'WITNESS cloud-export ' + helper_sha in foreign.stdout
    assert foreign.stderr.splitlines()[-1] == 'ValueError: recorded reference: missing or ambiguous batch suffix', foreign.stderr
    relocation = {'status': 'PASS', 'fresh_root': str(relocated), 'copied_files_sha256':
                  {name: sha((relocated / name).read_bytes()) for name in sorted(copied)},
                  'recipe_byte_identical': (moved_bundle / 'recipe.json').read_bytes() == (BUNDLE / 'recipe.json').read_bytes(),
                  'candidate_byte_identical': True, 'five_rendered_pngs_byte_identical': True,
                  'stdout': result.stdout, 'stderr': result.stderr,
                  'escaping_reference_control': {'input': 'D:/old/art/cartoon/clouds-v1/../outside.png',
                      'exit_code': escaped.returncode, 'stdout': escaped.stdout, 'stderr': escaped.stderr},
                  'foreign_batch_control': {'input': 'D:/old/art/cartoon/other-batch/input.png',
                      'exit_code': foreign.returncode, 'stdout': foreign.stdout, 'stderr': foreign.stderr}}
    # Visualization only: exact runtime pixels alpha-composited on a solid sky.
    sheet = Image.new('RGBA', (1100, 620), (91, 157, 203, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 12), 'Original diagnostic palette x2 | candidate true-alpha runtime x1', fill=(10, 25, 40))
    for i, frame in enumerate((16, 17)):
        native = Image.open(BUNDLE / f'reference/backgrnd-{frame:03}-original.png').convert('RGBA')
        native = native.resize((native.width * 2, native.height * 2), Image.Resampling.NEAREST)
        candidate = Image.open(HERE / f'BMP/BACKGRND.BMP/{frame:03}.png').convert('RGBA')
        for column, image in enumerate((native, candidate)):
            x, y = 16 + column * 550, 48 + i * 190
            draw.text((x, y), f'{frame:03} ' + ('Original diagnostic palette' if column == 0 else 'Fixed Cartoon candidate'), fill=(10, 25, 40))
            sheet.alpha_composite(image, (x, y + 24))
    archive_path = ROOT / 'assets/scrantic_data.zip'
    candidate_path = ROOT / 'build/clouds-v1/candidate.zip'
    with zipfile.ZipFile(archive_path) as baseline, zipfile.ZipFile(candidate_path) as candidate_zip:
        member = 'data/styles/cartoon/BMP/BACKGRND.BMP/015.png'
        raw = baseline.read(member)
        assert candidate_zip.read(member) == raw
    style = Image.open(io.BytesIO(raw)).convert('RGBA')
    draw.text((16, 456), '015 Exact unchanged accepted Cartoon runtime x1', fill=(10, 25, 40))
    sheet.alpha_composite(style, (16, 486))
    diagnostic = HERE / 'comparison-with-015.png'
    sheet.convert('RGB').save(diagnostic, compress_level=9)
    report = {'status': 'PASS', 'scope': 'Fixed-transform pixel/package replay and three invalid binding inputs; no native run or human approval.',
              'exporter_lf_sha256': helper_sha, 'verification_helper_lf_sha256': sha(Path(__file__).read_bytes().replace(b'\r\n', b'\n')),
              'recipe_sha256': sha((BUNDLE / 'recipe.json').read_bytes()),
              'export_report_sha256': sha((HERE / 'export-report.json').read_bytes()),
              'package_report_sha256': sha((HERE / 'package-report.json').read_bytes()),
              'candidate_sha256': sha(candidate_path.read_bytes()), 'baseline_readback_sha256': sha(archive_path.read_bytes()),
              'ordered_checks': results, 'relocated_cli_replay': relocation,
              'diagnostic': {'path': 'comparison-with-015.png', 'sha256': sha(diagnostic.read_bytes()),
                             'sky_rgb': [91, 157, 203], 'original_scale': 2, 'runtime_scale': 1,
                             'unchanged015_sha256': sha(raw), 'used_as_export_input': False},
              'limits': 'Controls execute fresh helper processes with bad recipe hashes/registration and a wrong archive. No source-removal mutant or renderer regression is claimed.'}
    (HERE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS cloud-export verification: fresh replay, three refused inputs, restored replay; unchanged015 diagnostic')


if __name__ == '__main__':
    main()
