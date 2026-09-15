"""Exercise the actual candidate mask helper against hash-bound native pixels."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile

import capture

OUT = Path('/out')
HELPER = OUT / 'capture_candidate.py'


def module(path):
    spec = importlib.util.spec_from_file_location('candidate_under_test', path)
    item = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item


def pixels():
    before_report = json.loads((OUT / 'baseline-v1/full/report.json').read_bytes())
    after_report = json.loads((OUT / 'candidate-v1/full/report.json').read_bytes())
    before, after = before_report['displays'][0], after_report['displays'][0]
    a = capture.codec.ppm(OUT / 'baseline-v1/full' / before['ppm'])
    b = capture.codec.ppm(OUT / 'candidate-v1/full' / after['ppm'])
    capture.require(capture.sha(a) == before['pixels_sha256'] and capture.sha(b) == after['pixels_sha256'],
                    'mask verification native pixel identities')
    return a, b, after['allowed_change_box']


def changed(raw, x, y):
    result = bytearray(raw)
    result[(y * 1280 + x) * 3] ^= 1
    return bytes(result)


def negative_case(under_test, a, b, box):
    x0, y0, _, _ = box
    if under_test.outside_equal(a, changed(b, x0 - 1, y0), box):
        raise AssertionError('capture_candidate.py: changed pixel outside placed frame028 was allowed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path)
    args = parser.parse_args()
    a, b, box = pixels()
    if args.module:
        try:
            negative_case(module(args.module), a, b, box)
        except AssertionError as error:
            print('FAIL ' + str(error))
            return 1
        return 0
    under_test = module(HELPER)
    x0, y0, x1, y1 = box
    assert under_test.outside_equal(a, b, box), 'actual native candidate obeys placed-frame mask'
    assert under_test.outside_equal(a, changed(b, x0, y0), box), 'inside-canvas change remains allowed'
    for x, y in ((x0 - 1, y0), (x1, y0), (x0, y0 - 1), (x0, y1)):
        assert not under_test.outside_equal(a, changed(b, x, y), box), 'outside-canvas change must be rejected'
    source = HELPER.read_text()
    anchor = 'def outside_equal(a, b, box):\n'
    assert source.count(anchor) == 1, 'unique actual mask helper anchor'
    witness = 'WITNESS removed-native-candidate-mask'
    with tempfile.TemporaryDirectory(prefix='front-mask-mutant-') as name:
        folder = Path(name)
        mutant, bytecode = folder / 'mutant.py', folder / 'mutant.pyc'
        mutant.write_text(source.replace(anchor, anchor + f'    print({witness!r})\n    return True\n'))
        bytecode.write_bytes(b'not bytecode')
        os.utime(bytecode, ns=(1_000_000_000, 1_000_000_000))
        previous = bytecode.stat().st_mtime_ns
        py_compile.compile(str(mutant), cfile=str(bytecode), doraise=True)
        assert bytecode.stat().st_mtime_ns > previous, 'mask mutant rebuilt timestamp'
        result = subprocess.run([sys.executable, '-B', str(Path(__file__)), '--module', str(bytecode)],
                                capture_output=True, text=True, timeout=30)
        expected = 'FAIL capture_candidate.py: changed pixel outside placed frame028 was allowed'
        assert result.returncode == 1 and result.stdout.splitlines() == [witness, expected] and not result.stderr, (
            'one witnessed actual mask-helper failure required', result.stdout, result.stderr)
    report = {'status': 'PASS', 'controls': 6, 'native_baseline_pixels_sha256': capture.sha(a),
              'native_candidate_pixels_sha256': capture.sha(b), 'placed_canvas': box,
              'helper_sha256': capture.sha(HELPER.read_bytes()), 'mutation': 'FIRED',
              'rebuilt': True, 'witness': witness, 'failure': expected,
              'scope': 'Recorded native pixels and actual comparison helper; no new native execution or changed capture files.'}
    capture.save(OUT / 'candidate-v1/mask-guard-verification.json', report)
    print(json.dumps(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
