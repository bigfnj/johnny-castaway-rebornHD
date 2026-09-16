"""Executed connecting-contract and native parser negatives on disposable inputs."""
import copy
import os
from pathlib import Path
import re
import time
import config
import capture
import native_core as core


def main():
    out = config.OUT / 'negative-controls' / 'baseline'
    core.require(not out.exists(), 'preserve baseline negative evidence')
    out.mkdir(parents=True)
    binding = config.load_json(core.BASE / 'build.json')
    core.require(config.load_json(core.BASE / 'summary.json')['status'] == 'PASS', 'baseline complete before negatives')
    helpers = {Path(p).name: core.sha(Path(p).read_bytes()) for p in (config.__file__, capture.__file__, core.__file__, __file__)}
    print('WITNESS executing connecting baseline guards ' + str(helpers), flush=True)
    original_contract = config.contract
    original_clips = copy.deepcopy(config.CLIPS)
    original_root, original_table_hash = config.ROOT, config.TABLE_LF_SHA
    original_base = core.BASE
    reference = original_contract()
    original_table = (original_root / 'src/data/walk_data.h').read_text()
    results = []

    def expect(name, label, call):
        try:
            call()
        except (ValueError, AssertionError) as error:
            assert str(error) == label, 'wrong negative failure:' + name + ':' + str(error)
            results.append({'name': name, 'status': 'FIRED', 'expected_failure': str(error)})
            print('FIRED ' + name + ': ' + str(error), flush=True)
        else:
            raise AssertionError('negative SURVIVED:' + name)

    def restore():
        config.CLIPS = copy.deepcopy(original_clips)
        config.ROOT = original_root
        config.TABLE_LF_SHA = original_table_hash
        config.contract = original_contract
        core.BASE = original_base

    def table_control(name, text, label):
        scratch = out / name
        path = scratch / 'src/data/walk_data.h'
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding='utf-8', newline='\n')
        config.ROOT = scratch
        config.TABLE_LF_SHA = config.sha(text.encode())
        try:
            expect(name, label, original_contract)
        finally:
            restore()

    print('CONTROL PASS original table contracts', flush=True)
    config.TABLE_LF_SHA = '0' * 64
    expect('wrong-table-fingerprint', 'original-derived table identity', original_contract)
    restore()

    row_pattern = r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}'
    matches = list(re.finditer(row_pattern, original_table))
    assert len(matches) == 489
    first = matches[0]
    table_control('missing-table-row', original_table[:first.start()] + original_table[first.end():], 'complete original-derived walk table')

    config.CLIPS['front_arc']['frames'][0] = 12
    expect('wrong-explicit-pose-sequence', 'connecting sequence:front_arc', original_contract)
    restore()
    config.CLIPS['front_arc']['blocks'][-1] = ('travel', [276])
    expect('missing-arrival-role', 'valid final arrival and non-sentinel rows:front_arc', original_contract)
    restore()

    match = matches[314]
    fields = list(map(int, match.groups()))
    fields[1] = 0
    table_control('sentinel-in-selected-turn', original_table[:match.start()] + '{' + ','.join(map(str, fields)) + '}' + original_table[match.end():], 'valid final arrival and non-sentinel rows:front_arc')
    config.CLIPS['front_arc']['duration_ms'] += 20
    expect('changed-configured-duration', 'connecting timing budget:front_arc', original_contract)
    restore()

    # A fresh compiled unchanged C trace must disagree with an incorrect
    # waypoint prediction. This changes expected input, not engine code.
    modified = copy.deepcopy(reference)
    waypoint = next(r for r in modified['clips']['waypoint_front']['travel']['draws'] if r['role'] == 'waypoint turn')
    assert waypoint['frame'] == 10
    waypoint['frame'] = 12
    config.contract = lambda: copy.deepcopy(modified)
    core.BASE = out / 'wrong-waypoint-prediction'
    started = time.time_ns()
    try:
        expect('wrong-waypoint-prediction', 'connecting capture: independent compiled C trace agrees with source contract:waypoint_front:travel', core.build)
        executable = core.BASE / 'connecting_trace'
        assert executable.is_file() and executable.stat().st_mtime_ns >= started, 'fresh trace executable witness'
        trace_witness = {'executable_sha256': config.sha(executable.read_bytes()), 'build_started_ns': started, 'executable_mtime_ns': executable.stat().st_mtime_ns,
                         'case': 'waypoint_front:travel', 'expected_frame_mutation': [10, 12], 'engine_source_mutated': False}
    finally:
        restore()

    baseline = original_base / 'waypoint_front/full'
    altered = out / 'wrong-selected-waypoint-path'
    altered.mkdir()
    for path in baseline.glob('*.ppm'):
        os.link(path, altered / path.name)
    text = (baseline / 'capture.log').read_text()
    target = 'chosen path: DCF'
    assert text.count(target) == 1, 'unique waypoint route witness'
    (altered / 'capture.log').write_text(text.replace(target, 'chosen path: DF', 1), encoding='utf-8')
    expect('wrong-selected-waypoint-path', 'connecting capture: actual selected configured path:travel', lambda: capture.parse(altered, 'full', 'waypoint_front'))

    # A malformed role annotation must not label the terminal display as
    # approved arrival; the original expected draw geometry remains exact.
    modified = copy.deepcopy(reference)
    modified['clips']['waypoint_front']['travel']['draws'][-1]['role'] = 'travel'
    config.contract = lambda: copy.deepcopy(modified)
    unchanged = out / 'wrong-terminal-role'
    unchanged.mkdir()
    for path in baseline.glob('*.ppm'):
        os.link(path, unchanged / path.name)
    (unchanged / 'capture.log').write_text(text, encoding='utf-8')
    try:
        expect('wrong-terminal-role', 'connecting capture: actual configured approved arrival', lambda: capture.parse(unchanged, 'full', 'waypoint_front'))
    finally:
        restore()

    assert original_contract() == reference, 'restored positive contract'
    positive = out / 'positive-restored'
    positive.mkdir()
    for path in baseline.glob('*.ppm'):
        os.link(path, positive / path.name)
    (positive / 'capture.log').write_text(text, encoding='utf-8')
    parsed = capture.parse(positive, 'full', 'waypoint_front')
    expected = config.load_json(baseline / 'report.json')
    assert all(parsed[key] == expected[key] for key in ('displays', 'segments', 'completed_waits', 'loaded_art')), 'restored native parse agrees'
    core.require(core.protected() == binding['protected_sha256'], 'protected inputs unchanged after baseline negatives')
    record = {'status': 'PASS', 'executed_helper_sha256': helpers, 'mutations': results, 'count': len(results),
              'positive_original_contract_and_restored_native_parse': True, 'fresh_trace_witness': trace_witness,
              'baseline_build_sha256': config.sha((original_base / 'build.json').read_bytes()),
              'baseline_waypoint_report_sha256': config.sha((baseline / 'report.json').read_bytes()),
              'protected_inputs_unchanged': len(binding['protected_sha256']),
              'scope': 'Six contract-input negatives, one incorrect prediction checked against a freshly compiled unchanged C observer, one actual captured selected-path mutation, and one terminal role annotation mutation. No altered engine or original binary timing claim.'}
    core.save(out / 'report.json', record)
    print('PASS nine executed baseline negatives and restored native positive control', flush=True)


if __name__ == '__main__':
    main()
