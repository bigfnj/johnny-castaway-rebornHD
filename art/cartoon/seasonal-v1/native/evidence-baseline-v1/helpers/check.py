"""Scoped actual-data negative controls for seasonal package and capture contracts."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import zipfile
import capture as c


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require = c.require
    require(not args.output.exists(), 'fresh control output')
    args.output.mkdir(parents=True)
    source = c.ROOT / 'assets/scrantic_data.zip'
    before = c.sha(source.read_bytes())
    require(before == c.PRODUCTION_SHA, 'control production identity')
    baseline = c.selected_archive(source)
    summary = json.loads((args.captures / 'summary.json').read_bytes())
    require(summary['status'] == 'PASS' and summary['helper_sha256'] == c.sha(Path(c.__file__).read_bytes()), 'completed capture and exact helper')
    text = (args.captures / 'day/halloween/smoke/capture.log').read_text()
    c.verify_log(text, 1, 0, [0, 0], baseline['holiday_dependencies'])
    results = []

    def fired(name, operation, label):
        try:
            operation()
        except ValueError as error:
            require(str(error) == 'seasonal: ' + label, 'correct control failure:' + name)
            results.append({'name': name, 'status': 'FIRED', 'failure': str(error)})
        else:
            raise ValueError('control survived:' + name)

    with zipfile.ZipFile(source) as original:
        entries = [(copy.copy(item), original.read(item.filename)) for item in original.infolist()]

    def package(name, rows):
        target = args.output / (name + '.zip')
        with zipfile.ZipFile(target, 'w') as archive:
            for info, raw in rows:
                archive.writestr(info, raw)
        return target

    wrong = package('retained-payload', [(info, raw + b' ' if i == 0 else raw) for i, (info, raw) in enumerate(entries)])
    fired('changed_existing_payload', lambda: c.selected_archive(wrong), 'retained production payload identity')
    missing = package('missing-member', entries[1:])
    fired('removed_existing_member', lambda: c.selected_archive(missing), 'retained production members')
    duplicate = package('duplicate-member', entries + entries[:1])
    fired('duplicate_member', lambda: c.selected_archive(duplicate), 'archive duplicate members')
    extra = package('unrelated-member', entries + [('unrelated.bin', b'not seasonal')])
    fired('unrelated_addition', lambda: c.selected_archive(extra), 'only seasonal additions')
    member = 'data/styles/cartoon/BMP/HOLIDAY.BMP/000.png'
    raw = next(raw for info, raw in entries if info.filename == baseline['holiday_dependencies'][0])
    added = package('technical-addition-control', entries + [(member, raw)])
    positive = c.selected_archive(added)
    require(positive['new_cartoon_members'] == [member] and positive['holiday_dependencies'][0] == member, 'nondegenerate candidate-addition control')
    damaged = bytearray(raw)
    damaged[16:20] = struct.pack('>I', 81)
    wrong_canvas = package('wrong-canvas', entries + [(member, bytes(damaged))])
    fired('wrong_candidate_canvas', lambda: c.selected_archive(wrong_canvas), 'holiday fixed canvas:0')
    fired('wrong_observed_state', lambda: c.verify_log(text.replace('holiday=1 night=0', 'holiday=0 night=0'), 1, 0, [0, 0], baseline['holiday_dependencies']), 'actual island state')
    fired('wrong_observed_backdrop', lambda: c.verify_log(text.replace('island backdrop: OCEAN02.SCR', 'island backdrop: OCEAN01.SCR'), 1, 0, [0, 0], baseline['holiday_dependencies']), 'actual backdrop')
    fired('missing_cleanup_witness', lambda: c.verify_log(text.replace('SEASONAL DONE:', 'REMOVED DONE:'), 1, 0, [0, 0], baseline['holiday_dependencies']), 'finite capture and cleanup')
    no_holiday = (args.captures / 'day/none/smoke/capture.log').read_text()
    injected = no_holiday + '\nSEASONAL DRAW: frame=0 x=410 y=298 dx=0 dy=0 scale=2 canvas=80x68\n'
    fired('draw_when_holiday_none', lambda: c.verify_log(injected, 0, 0, [0, 0], baseline['holiday_dependencies']), 'no-holiday draw absent')
    c.verify_log(text, 1, 0, [0, 0], baseline['holiday_dependencies'])
    require(c.selected_archive(source) == baseline and c.sha(source.read_bytes()) == before, 'restored positive and untouched production')
    report = {'status': 'PASS', 'helper_sha256': c.sha(Path(c.__file__).read_bytes()),
              'test_sha256': c.sha(Path(__file__).read_bytes()), 'production_archive_sha256': before,
              'smoke': 'completed baseline captures and baseline package checked first',
              'controls': results, 'nondegenerate_candidate_addition': 'PASS', 'restored_positive': 'PASS',
              'scope': 'Actual copied ZIP payloads and captured logs altered; no native rendering, image edits or production mutations. Technical addition control uses existing HD bytes only as a package-routing fixture, not proposed artwork.'}
    c.save(args.output / 'report.json', report)
    print('PASS nine supplemental input/log controls and restored positives')


if __name__ == '__main__':
    main()
