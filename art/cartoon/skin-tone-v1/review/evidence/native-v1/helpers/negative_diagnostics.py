"""Execute focused altered-input controls against the still-review builder."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'assets/scrantic_data.zip').is_file())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert not output.exists(), 'preserve diagnostic negative evidence'
    output.mkdir(parents=True)
    copied = output / 'copied-export'
    shutil.copytree(args.export, copied)
    builder = HERE / 'build_diagnostics.py'
    rows = []

    def run(name, destination, expected=None):
        argv = [sys.executable, '-B', str(builder), '--export', str(copied), '--output', str(destination)]
        result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
        (output / (name + '.stdout.txt')).write_text(result.stdout, encoding='utf-8')
        (output / (name + '.stderr.txt')).write_text(result.stderr, encoding='utf-8')
        if expected is None:
            assert result.returncode == 0 and 'PASS28 exact' in result.stdout, 'executed restored positive control'
        else:
            assert result.returncode != 0 and result.stderr.count('AssertionError:') == 1 and expected in result.stderr, 'one intended refusal:' + name
        rows.append({'control': name, 'exit_code': result.returncode, 'expected_failure': expected,
                     'stdout_sha256': sha(result.stdout.encode()), 'stderr_sha256': sha(result.stderr.encode()),
                     'executed_builder_sha256': sha(builder.read_bytes())})
        print(('PASS positive:' if expected is None else 'FIRED:') + name)

    run('positive-before', output / 'positive-before')
    for name, relative, expected in [('stale-corrected-png', 'sprites/024.png', 'corrected PNG:024.png'),
                                     ('stale-mask-png', 'masks/024.png', 'mask PNG:024.png')]:
        path = copied / relative
        original = path.read_bytes()
        with Image.open(path) as image:
            image.load()
            if image.mode == 'RGBA':
                values = list(image.getpixel((25, 50)))
                values[0] ^= 1
                image.putpixel((25, 50), tuple(values))
            else:
                image.putpixel((25, 50), image.getpixel((25, 50)) ^ 1)
            image.save(path)
        assert sha(path.read_bytes()) != sha(original), 'actual changed valid PNG bytes'
        destination = output / name
        run(name, destination, expected)
        assert not destination.exists(), 'failure before review output creation'
        path.write_bytes(original)
    occupied = output / 'occupied'
    occupied.mkdir()
    sentinel = occupied / 'sentinel.txt'
    sentinel.write_text('existing diagnostic must stay intact\n', encoding='utf-8')
    sentinel_hash = sha(sentinel.read_bytes())
    run('existing-output', occupied, 'preserve existing diagnostic output')
    assert list(occupied.iterdir()) == [sentinel] and sha(sentinel.read_bytes()) == sentinel_hash, 'existing output unchanged'
    run('positive-after', output / 'positive-after')
    report = {'status': 'PASS', 'controls': rows, 'script_sha256': sha(Path(__file__).read_bytes()),
              'export_recipe_sha256': sha((args.export / 'recipe.json').read_bytes()),
              'scope': 'Executed builder in fresh Python processes; two actual validPNG mutations with stale recipe hashes, then occupied-output refusal. Original export and diagnostic checkpoints remain untouched.'}
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
