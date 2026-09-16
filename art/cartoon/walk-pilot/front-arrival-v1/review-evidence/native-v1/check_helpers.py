"""Check the actual future017 mask helper against retained native pixels."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import py_compile
import subprocess
import sys
import time
import zipfile
import struct

OUT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check(module_path):
    spec = importlib.util.spec_from_file_location('candidate_mask_under_test', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('WITNESS executed mask helper SHA256=' + sha(module_path.read_bytes()), flush=True)
    report = json.loads((OUT / 'baseline-v1/full/report.json').read_bytes())
    last = report['displays'][-1]
    pixels = module.capture.codec.ppm(OUT / 'baseline-v1/full' / last['ppm'])
    assert sha(pixels) == last['pixels_sha256'], 'bound native fixture identity'
    flip, x, y, frame = last['actual_draw']
    assert [flip, x, y, frame] == [1, 293, 243, 17], 'actual mirrored017 fixture'
    with zipfile.ZipFile('/source/assets/scrantic_data.zip') as archive:
        w, h = struct.unpack('>II', archive.read('data/hd/BMP/JOHNWALK.BMP/017.png')[16:24])
    box = [x * 2, y * 2, x * 2 + w, y * 2 + h]
    assert module.outside_equal(pixels, pixels, box), 'smoke identical native pixels'
    print('PASS smoke identical native pixels', flush=True)
    tests = [('inside', box[0], box[1], True),
             ('left', box[0] - 1, box[1], False),
             ('right', box[2], box[1], False),
             ('above', box[0], box[1] - 1, False),
             ('below', box[0], box[3], False)]
    for label, px, py, expected in tests:
        changed = bytearray(pixels)
        changed[(py * 1280 + px) * 3] ^= 1
        assert module.outside_equal(pixels, bytes(changed), box) == expected, 'frame017 mask rejects outside change:' + label
        print('PASS regression ' + label, flush=True)
    return box


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path)
    args = parser.parse_args()
    if args.module:
        check(args.module)
        return
    helper = OUT / 'capture_candidate.py'
    folder = OUT / 'helper-checks-v1'
    if folder.exists():
        raise ValueError('preserve helper check evidence')
    folder.mkdir()
    bound = sha(helper.read_bytes())
    box = check(helper)
    text = helper.read_text()
    start, end = text.index('def outside_equal('), text.index('\n\ndef compare(')
    function = text[start:end]
    assert function.count('return False') == 2, 'unique outside-mask mutation anchors'
    variant = folder / 'capture_candidate_no_mask.py'
    variant.write_text(text[:start] + function.replace('return False', 'return True') + text[end:])
    began = time.time_ns()
    bytecode = folder / 'capture_candidate_no_mask.pyc'
    py_compile.compile(str(variant), cfile=str(bytecode), doraise=True)
    assert bytecode.stat().st_mtime_ns >= began, 'fresh mutation bytecode'
    command = [sys.executable, '-B', str(Path(__file__)), '--module', str(bytecode)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    (folder / 'mutation.stdout.txt').write_text(result.stdout)
    (folder / 'mutation.stderr.txt').write_text(result.stderr)
    assert result.returncode == 1, 'mask removal must fail exactly one assertion'
    assert result.stderr.count('AssertionError:') == 1 and 'frame017 mask rejects outside change:left' in result.stderr, 'precise mask failure witness'
    assert ('WITNESS executed mask helper SHA256=' + sha(bytecode.read_bytes())) in result.stdout, 'actual mutated bytecode execution witness'
    assert sha(helper.read_bytes()) == bound, 'real helper unchanged'
    record = {'status': 'PASS', 'smoke': 'exact bound native pixels',
              'regression_controls': ['inside accepted', 'left rejected', 'right rejected', 'above rejected', 'below rejected'],
              'placed_arrival_box_hd_xyxy': box, 'helper_sha256': bound,
              'mutation': {'result': 'FIRED', 'exit_code': result.returncode, 'source_sha256': sha(variant.read_bytes()),
                           'executed_bytecode_sha256': sha(bytecode.read_bytes()), 'compile_started_ns': began,
                           'bytecode_mtime_ns': bytecode.stat().st_mtime_ns,
                           'failure': 'frame017 mask rejects outside change:left'},
              'scope': 'Native-pixel mask helper validation only. Candidate017 packaging and native candidate execution await actual artwork.'}
    (folder / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS executed mask-removal mutation fired; production and baseline unchanged')


if __name__ == '__main__':
    main()
