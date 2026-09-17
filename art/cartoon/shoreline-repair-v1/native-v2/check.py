"""Focused positive/damaged-input controls for the extended ground contract."""
import argparse
from pathlib import Path
import tempfile
import zipfile

from capture import CANVASES, ROOT, ground_log, member, native, outside_ground, package_pair, require, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--phase-probe', type=Path, required=True)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    require(not args.report.exists(), 'fresh check report required')
    log = (args.phase_probe / 'capture.log').read_text()
    ground_log(log)
    with zipfile.ZipFile(args.baseline) as source:
        baseline = {name: source.read(name) for name in source.namelist()}
    selected = dict(baseline)
    for frame in CANVASES:
        selected[member(frame)] = baseline[f'data/hd/BMP/BACKGRND.BMP/{frame:03}.png']
    rows = []
    def refuses(name, call, expected):
        try:
            call()
        except ValueError as error:
            require(str(error) == 'seasonal: ' + expected, 'named refusal:' + name)
            rows.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('control survived:' + name)
    with tempfile.TemporaryDirectory(prefix='shore-v2-check-') as scratch:
        def archive(name, payloads):
            path = Path(scratch) / (name + '.zip')
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as target:
                for key, value in payloads.items():
                    target.writestr(key, value)
            return path
        positive = archive('positive', selected)
        package_pair(args.baseline, positive)
        rows.append({'name': 'ten_valid_same_canvas_replacements', 'status': 'PASS', 'scope': 'Temporary HD-byte package fixture, not proposed artwork.'})
        # This pixel is inside base000 and outside every wave canvas. It proves
        # the expanded allowance is exercised, rather than only its old subset.
        before = bytes(1280 * 960 * 3)
        after = bytearray(before)
        after[(580*1280+600)*3] = 1
        outside_ground(before, bytes(after))
        rows.append({'name': 'base_only_pixel_change', 'status': 'PASS'})
        if args.phase == 'regression':
            bad = dict(selected, **{member(4): baseline[member(4)]})
            path = archive('missing-replacement', bad)
            refuses('missing_required_phase004', lambda: package_pair(args.baseline, path), 'only ten selected ground/wave payloads changed')
            bad = dict(selected, **{member(12): baseline[member(12)] + b'damage'})
            path = archive('extra-replacement', bad)
            refuses('unrelated_palm_changed', lambda: package_pair(args.baseline, path), 'only ten selected ground/wave payloads changed')
            bad = dict(selected, **{member(0): selected[member(7)]})
            path = archive('wrong-base-canvas', bad)
            refuses('wrong_base000_canvas', lambda: package_pair(args.baseline, path), 'ground/wave fixed canvas:' + member(0))
            bad = dict(baseline)
            bad['data/styles/cartoon/BMP/HOLIDAY.BMP/000.png'] = baseline['data/hd/BMP/HOLIDAY.BMP/000.png']
            bad_base = archive('wrong-prop', bad)
            refuses('wrong_V5_prop', lambda: package_pair(bad_base, positive), 'exact V5 prop payloads')
            refuses('wrong_base_origin', lambda: ground_log(log.replace('SHORE DRAW: frame=0 x=288 ', 'SHORE DRAW: frame=0 x=289 ')), 'actual base island origin/canvas')
            after[0] = 1
            refuses('outside_ground_pixel', lambda: outside_ground(before, bytes(after)), 'changed pixel outside drawn ground canvases')
            package_pair(args.baseline, positive)
            ground_log(log)
    report = {'status': 'PASS', 'phase': args.phase, 'checks': rows,
              'adapter_sha256': sha((Path(__file__).parent / 'capture.py').read_bytes()),
              'checker_sha256': sha(Path(__file__).read_bytes()), 'baseline_sha256': sha(args.baseline.read_bytes()),
              'actual_native_log_sha256': sha((args.phase_probe / 'capture.log').read_bytes()),
              'scope': 'Copied-input helper contract only; no new native capture or artwork approval.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    save(args.report, report)
    print(f"PASS {args.phase}: {len(rows)} checks; adapter {report['adapter_sha256']}")


if __name__ == '__main__':
    main()
