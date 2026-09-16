"""Bounded fresh-process negative controls for the original-only exporter."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SMOKE_PATHS = ['BMP/JOHNWALK.BMP/018.png', 'BMP/SA_DEMO.BMP/000.png',
               'BMP/ENDCRDTS.BMP/000.png', 'SCR/INTRO.SCR.png']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dump-root', type=Path, required=True)
    parser.add_argument('--original-root', type=Path, required=True)
    parser.add_argument('--extraction', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('controls output must be fresh')
    args.output.mkdir(parents=True)
    helper = HERE / 'prepare.py'
    helper_bytes = helper.read_bytes()
    index_bytes = (args.extraction / 'index.json').read_bytes()
    runs = []

    def fixture(label):
        dest = args.output / label
        dest.mkdir()
        (dest / 'index.json').write_bytes(index_bytes)
        for relative in SMOKE_PATHS:
            target = dest / 'native' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.extraction / 'native' / relative, target)
        return dest

    def invoke(label, extraction, expected=None, dump_root=None, original_root=None,
               phase='smoke', execute=None, witness=None):
        command = [sys.executable, '-B', str(execute or helper), '--dump-root', str(dump_root or args.dump_root),
                   '--original-root', str(original_root or args.original_root), '--output', str(extraction), '--phase', phase]
        result = subprocess.run(command, cwd=ROOT, text=True, encoding='utf-8', capture_output=True, timeout=90)
        expected_code = 1 if expected else 0
        assert result.returncode == expected_code, (label, result.returncode, result.stdout, result.stderr)
        assert 'WITNESS original-inventory ' in result.stdout, label + ': actual helper witness missing'
        if expected:
            assert result.stderr.strip() == 'FAIL ' + expected, (label, result.stderr)
        else:
            assert 'PASS ' in result.stdout and result.stderr == '', (label, result.stderr)
        if witness:
            assert 'EXECUTED_MUTANT_BYTES_SHA256=' + witness in result.stdout, label + ': mutant execution witness missing'
        runs.append({'name': label, 'returncode': result.returncode, 'expected_failure': expected,
                     'result': 'FIRED' if expected else 'PASS', 'stdout': result.stdout, 'stderr': result.stderr})

    positive = fixture('positive')
    invoke('positive_before', positive)

    # Self-consistent PNG/file hashes must not override the independently
    # retained original RGBA pixels. This is the meaningful guard-removal case.
    changed = fixture('changed-pixel')
    image_path = changed / 'native/BMP/JOHNWALK.BMP/018.png'
    with Image.open(image_path) as opened:
        im = opened.copy()
    r, g, b, a = im.getpixel((8, 0))
    im.putpixel((8, 0), (r ^ 1, g, b, a))
    im.save(image_path)
    index = json.loads(index_bytes)
    next(row for row in index['frames'] if row['id'] == 'BMP/JOHNWALK.BMP/018')['png_sha256'] = sha(image_path.read_bytes())
    write_json(changed / 'index.json', index)
    label = 'native/BMP/JOHNWALK.BMP/018.png: original RGBA pixel identity differs'
    invoke('changed_pixel_with_refreshed_png_hash', changed, label)

    missing = fixture('missing-frame-row')
    index = json.loads(index_bytes)
    index['frames'] = [row for row in index['frames'] if row['id'] != 'BMP/JOHNWALK.BMP/018']
    write_json(missing / 'index.json', index)
    invoke('missing_frame_row', missing, 'index.json: missing or duplicate frame rows')

    mapping = fixture('wrong-frame-mapping')
    index = json.loads(index_bytes)
    next(row for row in index['frames'] if row['id'] == 'BMP/JOHNWALK.BMP/018')['frame'] = 19
    write_json(mapping / 'index.json', index)
    invoke('wrong_frame_mapping', mapping, 'BMP/JOHNWALK.BMP/018: frame/source mapping differs')

    palette = fixture('false-palette-parity')
    index = json.loads(index_bytes)
    index['original_executable_color_parity'] = True
    write_json(palette / 'index.json', index)
    invoke('false_original_palette_parity', palette, 'index.json: palette scope differs')

    report_copy = args.output / 'damaged-dump-report'
    report_copy.mkdir()
    (report_copy / 'report.json').write_bytes((args.dump_root / 'report.json').read_bytes() + b' ')
    invoke('changed_dump_report', positive, 'report.json: original dump report identity', dump_root=report_copy)

    pair_copy = args.output / 'damaged-resource-pair'
    pair_copy.mkdir()
    shutil.copyfile(args.original_root / 'RESOURCE.MAP', pair_copy / 'RESOURCE.MAP')
    raw = bytearray((args.original_root / 'RESOURCE.001').read_bytes())
    raw[-1] ^= 1
    (pair_copy / 'RESOURCE.001').write_bytes(raw)
    invoke('changed_original_volume', positive, 'RESOURCE.001: supplied-original input identity', original_root=pair_copy)
    invoke('existing_output_refused', positive, str(positive) + ': refusing to overwrite existing extraction', phase='prepare')

    statement = "            require(sha(opened.tobytes()) == facts['rgba_sha256'], row['path'] + ': original RGBA pixel identity differs')"
    source = helper_bytes.decode('utf-8')
    assert source.count(statement) == 1
    mutant = source.replace(statement, "            pass  # executed negative control: original RGBA guard removed", 1).encode('utf-8')
    mutant_path = args.output / 'prepare-rgba-guard-removed.py'
    mutant_path.write_bytes(mutant)
    # Keep __file__ at the real helper so imports/repository lookup are unchanged.
    # The driver records the exact bytes it compiles and executes before main.
    driver = args.output / 'execute_mutant.py'
    driver.write_text("from pathlib import Path\nimport hashlib\n"
                      + 'raw = Path(' + repr(str(mutant_path.resolve())) + ').read_bytes()\n'
                      + "print('EXECUTED_MUTANT_BYTES_SHA256=' + hashlib.sha256(raw).hexdigest(), flush=True)\n"
                      + 'scope = {"__name__": "__main__", "__file__": ' + repr(str(helper.resolve())) + '}\n'
                      + 'exec(compile(raw, ' + repr(str(helper.resolve())) + ', "exec"), scope)\n', encoding='utf-8', newline='\n')
    invoke('same_corruption_accepted_only_after_rgba_guard_removal', changed, execute=driver, witness=sha(mutant))
    invoke('positive_after', positive)
    assert helper.read_bytes() == helper_bytes
    assert (args.extraction / 'index.json').read_bytes() == index_bytes
    report = {'schema_version': 1, 'status': 'PASS', 'helper_sha256': sha(helper_bytes),
              'test_sha256': sha(Path(__file__).read_bytes()), 'extraction_index_sha256': sha(index_bytes),
              'negative_controls_fired': sum(run['result'] == 'FIRED' for run in runs), 'runs': runs,
              'guard_removal': {'artifact': mutant_path.name, 'sha256': sha(mutant),
                               'witness': 'EXECUTED_MUTANT_BYTES_SHA256',
                               'change': 'Exactly the original RGBA comparison removed; unchanged wrong PNG plus refreshed PNG hash then passes.'},
              'source_and_extraction_unchanged': True,
              'scope': 'Fresh processes exercise actual prepare/check entrypoints using isolated copied fixtures. No original, production or frozen reference bytes modified.'}
    write_json(args.output / 'verification.json', report)
    print('PASS ' + json.dumps({'negative_controls_fired': report['negative_controls_fired'], 'guard_removal_executed': True}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
