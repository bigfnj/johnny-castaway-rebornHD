"""Headless compiled loader/placement checks; run with a GNU-compatible C toolchain.

Uses copied production sources for mutations. No windows, artwork or production
archive writes. Actual platform decoding/native scene evidence is separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SMOKE = ['new-ground', 'new-center', 'legacy-ground', 'new-left', 'new-right']
REGRESSION = ['legacy-center', 'hd-fallback', 'bad-hd-fallback', 'original-fallback',
              'hd-style', 'draw-normal', 'draw-flip', 'draw-atop', 'draw-legacy',
              'draw-offset', 'wrong-ground-height', 'wrong-ground-width', 'wrong-source',
              'wrong-frame', 'wrong-resource', 'wrong-center-frame', 'wrong-center-height', 'wave-restore',
              'legacy-left', 'legacy-right', 'side-hd-fallback', 'side-wave-restore',
              'draw-left-normal', 'draw-left-flip', 'draw-left-atop', 'draw-left-offset',
              'draw-right-normal', 'draw-right-flip', 'draw-right-atop', 'draw-right-offset']
REGRESSION += [f'wrong-{side}-{axis}' for side in ('left', 'right')
               for axis in ('frame', 'other-end', 'width', 'height', 'source', 'resource', 'scale')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root, directory):
    directory.mkdir(parents=True, exist_ok=True)
    exe = directory / 'footprint-probe'
    exe.write_bytes(b'unbuilt')
    os.utime(exe, (1, 1))
    before = exe.stat().st_mtime_ns
    command = ['cc', '-std=gnu11', '-O1', '-g', '-ffunction-sections', '-fdata-sections',
               '-I' + str(root / 'platform'), '-I' + str(root / 'src/engine'),
               str(root / 'tests/test_art_footprint.c'), str(root / 'src/engine/graphics.c'),
               '-Wl,--gc-sections', '-o', str(exe)]
    run = subprocess.run(command, capture_output=True, text=True)
    (directory / 'build.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stdout + run.stderr
    assert exe.stat().st_mtime_ns > before, 'rebuilt artifact timestamp did not advance'
    return exe, {'command': command, 'sha256': sha(exe), 'rebuilt_timestamp_advanced': True}


def run_case(exe, case):
    run = subprocess.run([str(exe), case], capture_output=True, text=True, timeout=20)
    output = run.stdout + run.stderr
    assert f'WITNESS art footprint {case} BEGIN' in output, output
    if case.startswith('wrong-'):
        ok = run.returncode == 1 and output.count('REFUSED src/engine/art_style.c:') == 1 and 'data/styles/cartoon/BMP/' in output
    else:
        ok = run.returncode == 0 and f'WITNESS art footprint {case} PASS' in output
    return ok, {'case': case, 'exit_code': run.returncode, 'output': output, 'status': 'PASS' if ok else 'FAIL'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    root, out = args.source.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    exe, built = build(root, out)
    results = []
    for case in SMOKE if args.phase == 'smoke' else REGRESSION:
        ok, record = run_case(exe, case)
        results.append(record)
        assert ok, f'FAIL tests/test_art_footprint.py: {case}\n{record["output"]}'
        print('PASS footprint ' + case, flush=True)
    mutants = []
    if args.mutations:
        definitions = [
            ('wrong-frame', 'art_style.c', 'image == 0 &&', 'image >= 0 &&'),
            ('bad-hd-fallback', 'art_style.c', 'registeredFootprint = strict &&', 'registeredFootprint ='),
            ('draw-normal', 'graphics.c', 'x += assetDx; y += assetDy;\n    PlatformRect dest', 'x += 0; y += 0;\n    PlatformRect dest'),
            ('draw-flip', 'art_style.c', '560 - 640 - (-36)', '-36'),
            ('wrong-center-frame', 'art_style.c', 'image >= 6 && image <= 8', 'image >= 6 && image <= 9'),
            ('wave-restore', 'island.c', 'spriteLeft = x + dx', 'spriteLeft = x'),
            ('wrong-left-frame', 'art_style.c', 'image >= 3 && image <= 5', 'image >= 2 && image <= 5'),
            ('wrong-right-frame', 'art_style.c', 'image >= 9 && image <= 11', 'image >= 9 && image <= 12'),
            ('wrong-left-source', 'art_style.c', 'width == 72 && height == 29 && extendedLeftFoam', 'width >= 72 && height == 29 && extendedLeftFoam'),
            ('wrong-right-height', 'art_style.c', 'width == 154 && height == 74', 'width == 154 && height >= 74'),
            ('draw-left-flip', 'art_style.c', '144 - 150 - (-6)', '-6'),
            ('draw-right-flip', 'art_style.c', '144 - 154 : 0', '0 : 0'),
            ('side-wave-restore', 'island.c', 'spriteLeft = x + dx', 'spriteLeft = x'),
        ]
        for case, filename, old, new in definitions:
            directory = out / ('mutant-' + case)
            source = directory / 'source'
            for folder in ('src/engine', 'platform', 'tests'):
                (source / folder).mkdir(parents=True, exist_ok=True)
                for path in (root / folder).glob('*'):
                    if path.suffix in ('.c', '.h'):
                        shutil.copyfile(path, source / folder / path.name)
            changed = source / 'src/engine' / filename
            text = changed.read_text()
            assert text.count(old) == 1, (filename, old)
            changed.write_text(text.replace(old, new))
            binary, witness = build(source, directory)
            ok, result = run_case(binary, case)
            assert not ok, f'SURVIVED {filename}: {case}'
            result.update(status='FIRED', source='src/engine/' + filename,
                          executed_source_sha256=sha(changed), build=witness)
            mutants.append(result)
            print('FIRED rebuilt footprint ' + case, flush=True)
        for case, *_ in definitions:
            ok, record = run_case(exe, case)
            assert ok, record
    report = {'phase': args.phase, 'status': 'PASS', 'build': built, 'cases': results,
              'mutations': mutants, 'source_sha256': {name: sha(root / name) for name in
              ['src/engine/art_style.c', 'src/engine/art_style.h', 'src/engine/graphics.c', 'src/engine/island.c',
               'tests/test_art_footprint.c', 'tests/test_art_footprint.py']},
              'limits': 'Headless loader/draw unit probe uses a surface decoder fixture. No native island or PNG decoder parity claim.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
