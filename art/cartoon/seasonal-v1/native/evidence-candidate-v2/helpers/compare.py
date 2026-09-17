"""Compare immutable baseline/candidate seasonal stills using native coordinates."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import capture as c


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    require = c.require
    require(not args.report.exists(), 'preserve comparison report')
    spec = importlib.util.spec_from_file_location('seasonal_codec', c.CODEC)
    codec = importlib.util.module_from_spec(spec)
    require(c.sha(c.CODEC.read_bytes()) == c.CODEC_SHA, 'comparison codec identity')
    spec.loader.exec_module(codec)
    load = lambda p: json.loads(p.read_bytes())
    a, b = load(args.baseline / 'summary.json'), load(args.candidate / 'summary.json')
    require(a['status'] == b['status'] == 'PASS', 'completed native inputs')
    require(a['helper_sha256'] == b['helper_sha256'] == c.sha(Path(c.__file__).read_bytes()), 'comparison capture source identity')
    require(a['driver_sha256'] == b['driver_sha256'] == c.sha((c.HERE / 'driver.c').read_bytes()), 'comparison driver identity')
    ap, bp = load(args.baseline / 'inputs.json'), load(args.candidate / 'inputs.json')
    require(ap['protected_sha256'] == bp['protected_sha256'], 'same production inputs')
    require(a['selected_archive']['archive_sha256'] == c.PRODUCTION_SHA, 'comparison pinned baseline')
    require(set(a['groups']) == set(b['groups']), 'same native diagnostic groups')
    expected = [f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png' for i in range(4)]
    require(b['selected_archive']['new_cartoon_members'] == expected, 'all four selected seasonal additions')
    results = []
    witnesses = {}
    for group in a['groups']:
        for holiday, (name, _) in c.HOLIDAYS.items():
            for phase in ('smoke', 'repeat'):
                relative = Path(group) / name / phase
                old, new = args.baseline / relative, args.candidate / relative
                ar, br = load(old / 'report.json'), load(new / 'report.json')
                for field in ('holiday', 'night', 'offset', 'actual_holiday_draws', 'backdrop'):
                    require(ar[field] == br[field], 'same observed state:' + relative.as_posix() + ':' + field)
                retained = lambda report: [p for p in report['loaded_art'] if '/HOLIDAY.BMP/' not in p]
                require(retained(ar) == retained(br), 'same nonholiday dependencies:' + relative.as_posix())
                old_pixels, new_pixels = codec.ppm(old / 'final.ppm'), codec.ppm(new / 'final.ppm')
                for folder, report, pixels in [(old, ar, old_pixels), (new, br, new_pixels)]:
                    require(c.sha(pixels) == report['pixels_sha256'] and c.sha((folder / 'final.png').read_bytes()) == report['png_sha256'], 'comparison image identity:' + relative.as_posix())
                compared = c.compare_pixels(old_pixels, new_pixels, holiday, ar['offset'])
                results.append({'capture': relative.as_posix(), **compared,
                                'baseline_png_sha256': ar['png_sha256'], 'candidate_png_sha256': br['png_sha256']})
                if group == 'day' and phase == 'smoke' and holiday in (0, 1):
                    witnesses[holiday] = (old_pixels, new_pixels)
    controls = []
    for holiday, label in [(0, 'no-holiday exact scene identity'), (1, 'pixels outside holiday canvas')]:
        old_pixels, new_pixels = witnesses[holiday]
        wrong = bytearray(new_pixels)
        wrong[0] ^= 1
        try:
            c.compare_pixels(old_pixels, bytes(wrong), holiday, [0, 0])
        except ValueError as error:
            require(str(error) == 'seasonal: ' + label, 'comparison negative named failure')
            controls.append({'holiday': holiday, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('comparison negative survived')
        c.compare_pixels(old_pixels, new_pixels, holiday, [0, 0])
    report = {'status': 'PASS', 'baseline_summary_sha256': c.sha((args.baseline / 'summary.json').read_bytes()),
              'candidate_summary_sha256': c.sha((args.candidate / 'summary.json').read_bytes()),
              'baseline_archive_sha256': a['selected_archive']['archive_sha256'],
              'candidate_archive_sha256': b['selected_archive']['archive_sha256'],
              'capture_helper_sha256': c.sha(Path(c.__file__).read_bytes()),
              'comparison_helper_sha256': c.sha(Path(__file__).read_bytes()),
              'comparisons': results, 'negative_controls': controls,
              'scope': 'Exact matched native stills, both processes already smoke/repeat verified. No-holiday scenes are byte-identical; every other change lies within its actual seasonal canvas. Does not infer artistic or semantic alpha approval.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    c.save(args.report, report)
    print('PASS ' + str(len(results)) + ' native baseline/candidate image comparisons and two restored-positive negative controls')


if __name__ == '__main__':
    main()
