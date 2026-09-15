"""Headless decoder controls plus actual RESOURCE archive execution."""
import argparse
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile


def fixture(folder, method, packed):
    u16 = lambda x: struct.pack('<H', x)
    u32 = lambda x: struct.pack('<I', x)
    fixed = lambda s: s.encode('ascii').ljust(13, b'\0')
    palette = b'PAL:' + u16(780) + b'\0\0VGA:' + u32(768) + bytes(range(64)) * 12
    bmp = (b'BMP:' + u16(8) + u16(2) + b'INF:' + u32(0) + u16(1)
           + u16(8) + u16(2) + b'BIN:' + u32(len(packed) + 5)
           + bytes([method]) + u32(8) + packed)
    data, entries = b'', b''
    for name, payload in [('DEFAULT.PAL', palette), ('SHORT.BMP', bmp)]:
        record = fixed(name) + u32(len(payload)) + payload
        entries += u32(len(record)) + u32(len(data))
        data += record
    mapping = b'\0' * 6 + fixed('RESOURCE.001') + u16(2) + entries
    with zipfile.ZipFile(folder / 'scrantic_data.zip', 'w') as archive:
        archive.writestr('data/RESOURCE.MAP', mapping)
        archive.writestr('data/RESOURCE.001', data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--engine', required=True, type=Path)
    parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
    parser.add_argument('--only')
    options = parser.parse_args()
    probe, engine = options.probe.resolve(), options.engine.resolve()
    checks = []

    def decoded(name, method, packed, size, expected=None, error=None, consumed=None):
        def check():
            run = subprocess.run([str(probe), str(method), packed, str(size)], capture_output=True, timeout=15)
            text = (run.stdout + run.stderr).decode('utf-8', 'replace')
            assert 'WITNESS production uncompress ' in text, text
            if error:
                assert run.returncode == 1 and error in text and 'RESULT ' not in text, text
            else:
                assert run.returncode == 0 and f'RESULT {expected} consumed=' in text, text
                if consumed is not None:
                    assert f'RESULT {expected} consumed={consumed}' in text.splitlines(), text
        checks.append((name, check))

    decoded('rle-complete', 1, '88aa', 8, 'aa' * 8)
    decoded('lzw-complete', 2, 'aa00', 1, 'aa')
    if options.phase == 'regression' or options.only:
        decoded('rle-short-output', 1, '81aa', 8, error='RLE decode incomplete: produced 1 of 8 output bytes')
        decoded('lzw-short-output', 2, 'aa00', 8, error='LZW decode incomplete: produced 1 of 8 output bytes')
        decoded('rle-literal', 1, '03010203', 3, '010203')
        decoded('rle-mixed', 1, '02aabb82cc01dd', 5, 'aabbccccdd')
        decoded('lzw-dictionary', 2, '410202', 3, '414141')
        # Full-buffer return keeps the existing behavior even with a residual
        # dictionary string and another encoded code not yet consumed.
        decoded('lzw-full-buffer-early', 2, '41020a01', 2, '4141', consumed=3)

        def resource(name, method, packed, error=None):
            def check():
                with tempfile.TemporaryDirectory(prefix='jcr-decode-') as temp:
                    folder = Path(temp)
                    fixture(folder, method, bytes.fromhex(packed))
                    run = subprocess.run([str(engine), 'debug', 'dump'], cwd=folder,
                                         capture_output=True, timeout=20)
                    text = (run.stdout + run.stderr).decode('utf-8', 'replace')
                    assert 'zipvfs: opened archive' in text, text
                    dumped = folder / 'dump/BMP/SHORT.BMP.000.xpm'
                    if error:
                        assert run.returncode != 0 and error in text and not dumped.exists(), text
                    else:
                        assert run.returncode == 0 and 'Dumping BMP : SHORT.BMP' in text, text
                        assert dumped.read_text().splitlines()[-2:] == ['"aaaaaaaa",', '"aaaaaaaa"}']
            checks.append((name, check))
        resource('resource-rle-complete', 1, '88aa')
        resource('resource-rle-short', 1, '81aa', 'RLE decode incomplete: produced 1 of 8 output bytes')
        resource('resource-lzw-short', 2, 'aa00', 'LZW decode incomplete: produced 1 of 8 output bytes')
    if options.only:
        checks = [(name, check) for name, check in checks if name == options.only]
        if not checks:
            parser.error(f'unknown check: {options.only}')
    failures = 0
    for name, check in checks:
        print(f'WITNESS decoder assertion executed: {name}', flush=True)
        try:
            check()
            print(f'PASS {name}')
        except (AssertionError, OSError, subprocess.SubprocessError) as error:
            failures += 1
            print(f'FAIL tests/test_uncompress.py:{name}: {error}')
    print(f'Decoder {options.phase}: {len(checks) - failures}/{len(checks)} passed')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
