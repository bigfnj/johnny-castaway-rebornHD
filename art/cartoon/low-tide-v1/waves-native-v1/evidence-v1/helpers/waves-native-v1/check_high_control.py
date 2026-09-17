"""Focused damaged-input witness for the high-tide exact-pixel branch."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('wave_native_adapter', HERE / 'capture.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
c = a.c


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--candidate-sha256', required=True)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    c.require(not args.report.exists(), 'fresh high-control witness')
    observer = c.load_observer()
    rows = []
    for folder, archive_sha in ((args.baseline, a.BASE_SHA), (args.candidate, args.candidate_sha256)):
        report = json.loads((folder / 'report.json').read_bytes())
        c.require(report['status'] == 'PASS' and report['archive_sha256'] == archive_sha, 'high-control archive identity')
        c.require(report['args'] == a.CASES['high_control'], 'high-control actual arguments')
        c.require(c.sha((folder / 'final.png').read_bytes()) == report['png_sha256'], 'high-control final PNG identity')
        pixels = observer.codec.ppm(folder / 'final.ppm')
        c.require(c.sha(pixels) == report['displays'][-1]['pixels_sha256'], 'high-control final RGB identity')
        rows.append((report, pixels))
    before, after = rows[0][1], rows[1][1]
    members = c.archive(a.ROOT / 'build/low-tide-v1/static-candidate-v2.zip')
    sizes = {str(f): members[a.hd(f)]['canvas'] for f in a.FRAMES}
    c.require(a.pixel_scope(before, after, a.CASES['high_control'], sizes) == 0, 'actual unchanged high-tide positive')
    altered = bytearray(after)
    altered[(700 * 1280 + 500) * 3] ^= 1
    # This point is inside a low-wave rectangle. It must be allowed in low mode
    # yet refused in high mode, so the branch distinction is non-degenerate.
    c.require(a.pixel_scope(before, bytes(altered), a.CASES['none'], sizes) == 1, 'low-mode counterexample accepted')
    try:
        a.pixel_scope(before, bytes(altered), a.CASES['high_control'], sizes)
    except ValueError as exc:
        c.require(str(exc) == 'final native: high-tide exact pixels', 'named high-mode pixel failure')
        failure = str(exc)
    else:
        raise ValueError('high-tide pixel mutation survived')
    c.require(a.pixel_scope(before, after, a.CASES['high_control'], sizes) == 0, 'restored high-tide positive')
    c.save(args.report, {'status': 'PASS', 'failure': failure, 'mutated_pixel_hd': [500, 700],
        'low_mode_changed_pixels': 1, 'high_mode': 'FIRED', 'restored_positive': 'PASS',
        'adapter_sha256': c.sha((HERE / 'capture.py').read_bytes()), 'checker_sha256': c.sha(Path(__file__).read_bytes()),
        'baseline_report_sha256': c.sha((args.baseline / 'report.json').read_bytes()),
        'candidate_report_sha256': c.sha((args.candidate / 'report.json').read_bytes()),
        'method': 'Actual native high-tide pixels damaged only in memory; originals untouched. Same mutation accepted by low scope and rejected by high exact scope.'})
    print('PASS executed high-tide pixel witness: exactly one named failure, restored positive')


if __name__ == '__main__':
    main()
