"""Small reference readback and executed damaged-output controls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / 'prepare_references.py'
ROOT = HERE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    original = HELPER.read_bytes()
    runs = []

    def invoke(label, options=(), failure=None, script=HELPER, mutant_hash=None):
        run = subprocess.run([sys.executable, '-B', str(script), '--check', *map(str, options)],
                             cwd=ROOT, text=True, encoding='utf-8', capture_output=True, timeout=60)
        assert run.returncode == (1 if failure else 0), (label, run.stdout, run.stderr)
        assert 'WITNESS seasonal-reference ' + sha(original) in run.stdout
        assert not run.stderr, (label, run.stderr)
        if failure:
            assert run.stdout.splitlines()[-1] == 'FAIL ' + failure, (label, run.stdout)
        else:
            assert 'PASS seasonal-reference ' in run.stdout, (label, run.stdout)
        if mutant_hash:
            assert 'EXECUTED_MUTANT_SHA256=' + mutant_hash in run.stdout
        runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS',
                     'stdout': run.stdout, 'stderr': run.stderr, 'returncode': run.returncode})

    invoke('exact_reference_readback')
    report = {'schema_version': 1, 'phase': args.phase, 'status': 'PASS',
              'helper_sha256': sha(original), 'test_sha256': sha(Path(__file__).read_bytes()),
              'source_sha256': sha((HERE / 'source.json').read_bytes())}
    if args.phase == 'regression':
        manifest = json.loads((HERE / 'source.json').read_bytes())
        checked = []
        for row in manifest['frames']:
            name = f"{row['frame']:03}"
            native = Image.open(HERE / (name + '-original-native.png')).convert('RGBA')
            enlarged = Image.open(HERE / (name + '-original-nearest8.png')).convert('RGBA')
            guide = Image.open(HERE / (name + '-original-guide.png')).convert('RGBA')
            assert enlarged.size == (native.width * 8, native.height * 8)
            for y in range(enlarged.height):
                for x in range(enlarged.width):
                    assert enlarged.getpixel((x, y)) == native.getpixel((x // 8, y // 8)), name
            dx, dy = row['guide']['offset']
            assert guide.crop((dx, dy, dx + enlarged.width, dy + enlarged.height)).tobytes() == enlarged.tobytes()
            assert guide.getbbox() == tuple(v + (dx if i % 2 == 0 else dy) for i, v in enumerate(enlarged.getbbox()))
            checked.append({'frame': row['frame'], 'nearest8_pixels_checked': enlarged.width * enlarged.height,
                            'guide_offset': [dx, dy], 'guide_padding_alpha_zero': True})
        invoke('wrong_original_archive_rejected', ['--originals', HERE / 'source.json'],
               'art/cartoon/character-inventory-v1/reference-originals.zip: source identity differs')
        # Temp artifacts are strictly below this owned reference folder.
        with tempfile.TemporaryDirectory(prefix='verification-', dir=HERE) as directory:
            work = Path(directory).resolve()
            assert work.is_relative_to(HERE.resolve())
            for path in HERE.iterdir():
                if path.is_file() and (path.suffix == '.png' or path.name == 'source.json'):
                    shutil.copyfile(path, work / path.name)
            damaged = work / '000-original-guide.png'
            raw = bytearray(damaged.read_bytes())
            raw[-1] ^= 1
            damaged.write_bytes(raw)
            invoke('altered_guide_rejected', ['--output', work], '000-original-guide.png: reproduced bytes differ')
            statement = "                require(target.read_bytes() == data, name + ': reproduced bytes differ')"
            text = original.decode('utf-8')
            assert text.count(statement) == 1
            mutant = text.replace(statement, '                pass  # executed control: output identity guard removed', 1).encode('utf-8')
            mutant_path = work / 'guard_removed.py'
            mutant_path.write_bytes(mutant)
            driver = work / 'execute_mutant.py'
            driver.write_text('from pathlib import Path\nimport hashlib\n'
                              + 'raw = Path(' + repr(str(mutant_path)) + ').read_bytes()\n'
                              + "print('EXECUTED_MUTANT_SHA256=' + hashlib.sha256(raw).hexdigest())\n"
                              + 'scope = {"__name__": "__main__", "__file__": ' + repr(str(HELPER)) + '}\n'
                              + 'exec(compile(raw, ' + repr(str(HELPER)) + ', "exec"), scope)\n', encoding='utf-8')
            invoke('same_bad_guide_accepted_only_without_guard', ['--output', work], script=driver, mutant_hash=sha(mutant))
            report['mutation'] = {'sha256': sha(mutant), 'removed_statement': statement,
                                  'corrupt_guide_sha256': sha(raw), 'executed': True}
        invoke('restored_real_references_pass')
        assert HELPER.read_bytes() == original
        report['independent_pixels'] = checked
    report['runs'] = runs
    report['scope'] = 'Source/reference reproduction only; no generation, geometry export or human art acceptance.'
    (HERE / ('verification-' + args.phase + '.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS seasonal reference ' + args.phase)


if __name__ == '__main__':
    main()
