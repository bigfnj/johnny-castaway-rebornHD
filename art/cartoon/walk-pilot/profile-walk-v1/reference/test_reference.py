"""Original profile references: smoke first, then witnessed damaged-input controls."""
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
ROOT = HERE.parents[4]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    parser.add_argument('--dump-root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    helper = HERE / 'prepare.py'
    witness = 'WITNESS profile-reference SHA256=' + sha(helper.read_bytes())
    cases = []

    def run(label, argv, diagnostic=None):
        process = subprocess.run([sys.executable, '-B', str(helper), *map(str, argv)],
                                 cwd=ROOT, capture_output=True, text=True, timeout=30)
        assert witness in process.stdout, (label, 'missing executing source witness')
        if diagnostic:
            assert process.returncode == 1 and process.stderr.strip() == 'FAIL ' + diagnostic, (label, process.stdout, process.stderr)
        else:
            assert process.returncode == 0 and 'PASS ' in process.stdout and not process.stderr, (label, process.stdout, process.stderr)
        cases.append({'label': label, 'exit_code': process.returncode,
                      'stdout': process.stdout, 'stderr': process.stderr,
                      'expected_named_failure': diagnostic, 'status': 'FIRED' if diagnostic else 'PASS'})

    with tempfile.TemporaryDirectory(prefix='johnny-profile-reference-') as temporary:
        scratch = Path(temporary)
        generated = scratch / 'generated'
        if args.phase == 'smoke':
            run('prepare-eight-from-verified-original-dump', ['--dump-root', args.dump_root, '--output', generated])
            run('check-preserved-eight-references', ['--check', '--output', HERE])
            for path in generated.iterdir():
                assert path.read_bytes() == (HERE / path.name).read_bytes(), path.name + ': stored reproduction differs'
        else:
            index = json.loads((HERE / 'source-index.json').read_bytes())
            names = ['source-index.json', *index['record_sha256']]
            names += [f'{f:03}-original-{kind}.png' for f in range(1, 9) for kind in ('native', 'nearest8')]

            def fixture(label):
                output = scratch / label
                output.mkdir()
                for name in names:
                    shutil.copyfile(HERE / name, output / name)
                return output

            def rebind(output, record):
                # Re-sign disposable container hashes so semantic guards, not
                # merely stale file hashes, must reject these controls.
                save(output / '003-source.json', record)
                changed = json.loads((output / 'source-index.json').read_bytes())
                changed['record_sha256']['003-source.json'] = sha((output / '003-source.json').read_bytes())
                save(output / 'source-index.json', changed)

            for label, field, value, diagnostic in (
                ('original-facts', 'original_frame', {'frame': 3}, '003-source.json: original fact row differs'),
                ('cap-registration', 'registration', {'suggested_cap_target_hd': [55, .25]}, '003-source.json: registration differs'),
                ('source-provenance', 'historical_dump_engine_sha256', '0' * 64, '003-source.json: provenance/limit differs'),
            ):
                output = fixture(label)
                record = json.loads((output / '003-source.json').read_bytes())
                record[field] = value
                rebind(output, record)
                run(label, ['--check', '--output', output], diagnostic)

            for kind, diagnostic in (
                ('native', '003-original-native.png: original RGBA differs'),
                ('nearest8', '003-original-nearest8.png: exact8 pixel replication differs'),
            ):
                output = fixture('damaged-' + kind)
                path = output / ('003-original-' + kind + '.png')
                with Image.open(path) as opened:
                    im = opened.copy()
                pixel = im.getpixel((0, 0))
                im.putpixel((0, 0), (pixel[0] ^ 1, *pixel[1:]))
                im.save(path)
                record = json.loads((output / '003-source.json').read_bytes())
                record['files_sha256'][path.name] = sha(path.read_bytes())
                rebind(output, record)
                run('damaged-' + kind, ['--check', '--output', output], diagnostic)

            output = fixture('wrong-frame-scope')
            changed = json.loads((output / 'source-index.json').read_bytes())
            changed['frames'] = [1, 2, 3, 4, 5, 6, 7, 9]
            save(output / 'source-index.json', changed)
            run('wrong-frame-scope', ['--check', '--output', output], 'source-index.json: frame scope')

            output = fixture('existing-output')
            before = {p.name: sha(p.read_bytes()) for p in output.iterdir()}
            run('existing-output', ['--dump-root', args.dump_root, '--output', output], 'output: must be a fresh directory')
            assert before == {p.name: sha(p.read_bytes()) for p in output.iterdir()}, 'existing output changed'

            dump = scratch / 'damaged-dump'
            (dump / 'dump/BMP').mkdir(parents=True)
            shutil.copyfile(args.dump_root / 'report.json', dump / 'report.json')
            for frame in range(36):
                name = f'JOHNWALK.BMP.{frame:03}.xpm'
                shutil.copyfile(args.dump_root / 'dump/BMP' / name, dump / 'dump/BMP' / name)
            target = dump / 'dump/BMP/JOHNWALK.BMP.003.xpm'
            target.write_bytes(target.read_bytes() + b'\n')
            output = scratch / 'refused-output'
            run('original-xpm-raw-identity', ['--dump-root', dump, '--output', output], 'original-frame-identity:003')
            assert not output.exists(), 'damaged input wrote an output'
    args.report.parent.mkdir(parents=True, exist_ok=True)
    save(args.report, {'schema_version': 1, 'phase': args.phase, 'case_count': len(cases),
                       'helper_sha256': sha(helper.read_bytes()), 'test_sha256': sha(Path(__file__).read_bytes()),
                       'source_index_sha256': sha((HERE / 'source-index.json').read_bytes()),
                       'scope': 'Fresh Python subprocesses run the actual helper. Regression corrupts disposable inputs and rebinds container hashes for semantic controls. No production or reference pixels changed.',
                       'cases': cases})
    print('PASS ' + args.phase + ': ' + str(len(cases)) + ' witnessed cases')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
