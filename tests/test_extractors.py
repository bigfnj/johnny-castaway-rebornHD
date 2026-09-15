"""Headless legacy extractor controls; synthetic bytes are not original-source parity.

All output is isolated. Smoke must pass before running the regression phase.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OFFSETS = [0x1DC00, 0x20800, 0x20E00, 0x22C00, 0x24000, 0x24C00,
           0x28A00, 0x2C600, 0x2D000, 0x2DE00, 0x34400, 0x32E00,
           0x39C00, 0x43400, 0x37200, 0x37E00, 0x45A00, 0x3AE00,
           0x3E600, 0x3F400, 0x41200, 0x42600, 0x42C00, 0x43400]
WALK_START = 0x188EA
WALK_COUNT = 489


def sound_fixture(maximum=False):
    data = bytearray(0x45A00 + (65543 if maximum else 400))
    for index, offset in enumerate(sorted(set(OFFSETS))):
        size = (0, 1, 255, 256, 291)[index % 5]
        if maximum and offset == 0x45A00: size = 65535
        data[offset:offset + size + 8] = bytes((index * 17 + n * 7) % 256 for n in range(size + 8))
        struct.pack_into('<H', data, offset, size)
    expected = {f'sound{i + 1}.wav': bytes(data[offset:offset + struct.unpack_from('<H', data, offset)[0] + 8]) for i, offset in enumerate(OFFSETS)}
    return bytes(data), expected


def walk_fixture(table=False):
    if table:
        source = (ROOT / 'src/data/walk_data.h').read_text(encoding='utf-8')
        rows = [tuple(map(int, match)) for match in re.findall(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', source)]
        assert len(rows) == WALK_COUNT, 'tests/test_extractors.py: compiled walk table shape changed'
    else:
        rows = [(i % 2, (i * 257) % 65536, 65535 - (i * 131) % 65536, (0, 32767, 291, 256)[i % 4]) for i in range(WALK_COUNT)]
    data = bytearray(WALK_START)
    for flip, x, y, sprite in rows:
        data.extend(struct.pack('<HHH', flip * 32768 + sprite, x, y))
    expected = ''.join(f'    {{ {flip}, {x:3d}, {y:3d}, {sprite:2d} }},\n' for flip, x, y, sprite in rows).encode()
    return bytes(data), expected


def execute(exe, args, case, *, env=None):
    result = subprocess.run([str(exe), *map(str, args)], cwd=case, capture_output=True, env=env, timeout=20)
    (case / 'stdout.bin').write_bytes(result.stdout)
    (case / 'stderr.txt').write_bytes(result.stderr)
    return result


def oracle(label, condition, detail):
    print(f'WITNESS {label}: assertion executed', flush=True)
    assert condition, f'{label}: {detail}'


def success(result, tool, label):
    text = result.stderr.decode('utf-8', 'replace')
    oracle(label, result.returncode == 0 and 'PASS ' + tool in text and 'parity is unverified' in text and 'FAIL ' not in text,
           f'expected successful legacy extraction: {result.returncode}: {text}')


def failure(result, tool, path, label, fragment=None):
    text = result.stderr.decode('utf-8', 'replace')
    failures = [line for line in text.splitlines() if line.startswith('FAIL ')]
    oracle(label, result.returncode != 0 and len(failures) == 1 and failures[0].startswith('FAIL ' + tool + ':')
           and str(path).replace('\\', '/') in failures[0].replace('\\', '/')
           and (fragment is None or fragment in failures[0]) and 'PASS ' not in text and not result.stdout,
           f'expected one path-naming failure for {path}: exit={result.returncode}; {text}')


def check_case(name, sound, walk, work, env=None):
    case = work / name; case.mkdir()
    is_sound = name.startswith('sound')
    exe = sound if is_sound else walk
    tool = 'tools/extract_sound.c' if is_sound else 'tools/extract_walk_data.c'
    label = tool + ' ' + name
    source = case / 'source with spaces.scr'
    output = case / ('output directory' if is_sound else 'walk table.txt')
    if is_sound: output.mkdir()
    data, expected = sound_fixture(name == 'sound-max') if is_sound else walk_fixture(name == 'walk-table')
    source.write_bytes(data)
    args = ['--layout', 'legacy-fixed-offsets', '--input', source, '--output-dir', output] if is_sound else ['--input', source, '--output', output]
    if name.endswith('-arguments'):
        invalid = [([], 'arguments'), (['--input'], '--input'), (['--unknown'], '--unknown'),
                   (args + ['--input', source], '--input')]
        if is_sound: invalid.append((['--layout', 'riff', '--input', source, '--output-dir', output], 'arguments'))
        for index, (arguments, token) in enumerate(invalid):
            check = case / str(index); check.mkdir()
            failure(execute(exe, arguments, check), tool, token, label)
        oracle(label, not list(output.iterdir()) if is_sound else not output.exists(), 'bad arguments created output')
        return
    if name.endswith('-help'):
        result = execute(exe, ['--help'], case)
        oracle(label, result.returncode == 0 and b'Usage:' in result.stdout and b'parity is unverified' in result.stdout, 'help failed')
        return
    if name.endswith('-missing'):
        source.unlink()
        failure(execute(exe, args, case, env=env), tool, source, label, 'cannot open input')
    elif name.endswith('-truncated') or name.endswith('-header'):
        truncated = data[:0x1DC01] if name.endswith('-header') else data[:-1] if not is_sound else data[:0x45A02]
        source.write_bytes(truncated)
        failure(execute(exe, args, case, env=env), tool, source, label, 'truncated input')
    elif name.endswith('-existing'):
        sentinel = output / 'sound24.wav' if is_sound else output
        sentinel.write_bytes(b'KEEP USER FILE')
        failure(execute(exe, args, case, env=env), tool, sentinel, label, 'already exists')
        oracle(label, sentinel.read_bytes() == b'KEEP USER FILE', 'existing output was changed')
        if is_sound:
            oracle(label, list(output.iterdir()) == [sentinel], 'earlier files were not rolled back')
        return
    elif name.endswith('-bad-output'):
        destination = output / 'sound24.wav' if is_sound else output
        destination.mkdir()
        failure(execute(exe, args, case, env=env), tool, destination, label)
        if is_sound: oracle(label, list(output.iterdir()) == [destination], 'created files survived output failure')
        return
    elif name.endswith('-fault'):
        kind = env['JCR_EXTRACT_FAULT']
        target = source if kind in ('read', 'seek', 'tell', 'input-close', 'allocate') else output / 'sound1.wav' if is_sound else output
        fragments = {'read': 'short read', 'seek': 'seek failed', 'tell': 'cannot determine input length',
                     'input-close': 'input close failed', 'allocate': 'allocation failed', 'write': 'output write failed',
                     'close': 'output close failed', 'stdout': 'output write failed'}
        if kind == 'stdout': args[-1] = '-'; target = 'stdout'
        failure(execute(exe, args, case, env=env), tool, target, label, fragments[kind])
    else:
        if name.endswith('-stdout'): args[-1] = '-'
        result = execute(exe, args, case, env=env)
        success(result, tool, label)
        if is_sound:
            actual = {p.name: p.read_bytes() for p in output.iterdir()}
            oracle(label, actual == expected, 'legacy block bytes or names differ')
        else:
            actual = result.stdout.replace(b'\r\n', b'\n') if name.endswith('-stdout') else output.read_bytes()
            oracle(label, actual == expected, '489-row byte/flag/order/format contract differs')
        return
    oracle(label, not list(output.iterdir()) if is_sound else not output.exists(), 'failure left partial output')


SMOKE = ['sound-help', 'walk-help', 'sound-valid', 'walk-valid']
REGRESSION = ['sound-max', 'walk-table', 'walk-stdout', 'sound-missing', 'walk-missing',
              'sound-truncated', 'sound-header', 'walk-truncated', 'sound-existing',
              'walk-existing', 'sound-bad-output', 'walk-bad-output', 'sound-arguments', 'walk-arguments']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sound', type=Path, required=True); parser.add_argument('--walk', type=Path, required=True)
    parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
    parser.add_argument('--work', type=Path); parser.add_argument('--only')
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve(); work.mkdir(parents=True, exist_ok=False)
    else:
        work = Path(tempfile.mkdtemp(prefix='jcr-extractors-'))
    sound, walk = args.sound.resolve(), args.walk.resolve()
    cases = [args.only] if args.only else SMOKE if args.phase == 'smoke' else REGRESSION
    try:
        for name in cases: check_case(name, sound, walk, work)
        report = {'phase': args.phase, 'passed': cases, 'sound_sha256': hashlib.sha256(sound.read_bytes()).hexdigest(),
                  'walk_sha256': hashlib.sha256(walk.read_bytes()).hexdigest(), 'original_source_parity': 'unverified; synthetic fixtures only'}
        (work / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(f'INFO original SCRANTIC.SCR is unavailable; synthetic layout coverage only. Evidence: {work}')
        print(f'PASS extractors {args.phase}: {len(cases)}/{len(cases)}'); return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}; evidence: {work}'); return 1


if __name__ == '__main__': raise SystemExit(main())
