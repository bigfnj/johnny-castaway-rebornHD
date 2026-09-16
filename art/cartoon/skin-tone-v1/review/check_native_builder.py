"""Exercise clip/phase/source bindings and two real native-review input refusals."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

import build_native

config = build_native.config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--wrong-stills', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve native builder control evidence'
    args.output.mkdir(parents=True)
    contract = config.contract()['clips']
    reports = {name: config.load_json(config.OUT / 'baseline-v1' / name / 'full/report.json') for name in config.CLIPS}
    for name, report in reports.items():
        build_native.source_identity(report, 'baseline', name, contract)
    controls = []
    for name, value, clip, label in [
        ('swapped-equal-duration-route', copy.deepcopy(reports['travel_cb']), 'front_arc', 'capture clip/phase identity:baseline:front_arc'),
        ('spoofed-route-name', dict(copy.deepcopy(reports['travel_cb']), clip='front_arc'), 'front_arc', 'capture source contract:baseline:front_arc:prime'),
        ('wrong-capture-phase', dict(copy.deepcopy(reports['front_arc']), phase='smoke'), 'front_arc', 'capture clip/phase identity:baseline:front_arc'),
    ]:
        try:
            build_native.source_identity(value, 'baseline', clip, contract)
        except AssertionError as error:
            assert str(error) == label, 'intended source refusal:' + name
            controls.append({'case': name, 'status': 'FIRED', 'failure': label})
        else:
            raise AssertionError('source control survived:' + name)
    for name, report in reports.items():
        build_native.source_identity(report, 'baseline', name, contract)
    occupied = args.output / 'occupied'
    occupied.mkdir()
    sentinel = occupied / 'sentinel.txt'
    sentinel.write_text('preserve this existing review\n', encoding='utf-8')
    before = sentinel.read_bytes()
    cases = [
        ('mismatched-still-recipe', args.output / 'wrong-still-output', 'stills use exact captured correction recipe'),
        ('occupied-review', occupied, 'preserve existing native color review'),
    ]
    for name, destination, label in cases:
        command = [sys.executable, '-B', str(Path(build_native.__file__)), '--candidate', str(args.candidate),
                   '--stills', str(args.wrong_stills), '--output', str(destination)]
        result = subprocess.run(command, capture_output=True, text=True, cwd=config.ROOT)
        (args.output / (name + '.stdout.txt')).write_text(result.stdout, encoding='utf-8')
        (args.output / (name + '.stderr.txt')).write_text(result.stderr, encoding='utf-8')
        assert result.returncode != 0 and result.stderr.count('AssertionError:') == 1 and 'AssertionError: ' + label in result.stderr, 'one intended builder refusal:' + name
        controls.append({'case': name, 'status': 'FIRED', 'failure': label, 'exit_code': result.returncode})
    assert not (args.output / 'wrong-still-output').exists(), 'recipe mismatch creates no output'
    assert list(occupied.iterdir()) == [sentinel] and sentinel.read_bytes() == before, 'occupied review unchanged'
    output = {'status': 'PASS', 'executed_builder_sha256': config.sha(Path(build_native.__file__).read_bytes()),
              'checker_sha256': config.sha(Path(__file__).read_bytes()), 'baseline_source_positive_before_and_after': 8,
              'source_reports_sha256': {name: config.sha((config.OUT / 'baseline-v1' / name / 'full/report.json').read_bytes()) for name in reports},
              'candidate_preparation_sha256': config.sha((args.candidate / 'preparation.json').read_bytes()),
              'wrong_still_record_sha256': config.sha((args.wrong_stills / 'review-record.json').read_bytes()),
              'controls': controls,
              'scope': 'Source binding positives bracket three altered-report controls. Fresh builder processes refuse the actual earlier still recipe and an occupied output. No input, capture or existing review modified.'}
    (args.output / 'result.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print('PASS eight source-contract positives before/after; five intended native-builder refusals')


if __name__ == '__main__':
    main()
