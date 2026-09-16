"""Executed parser/comparison negatives, not mutated-engine replay claims."""
import copy
import os
from pathlib import Path
import capture
import capture_candidate
import config
import native_core as core


def main():
    out = config.OUT / 'negative-controls'
    out.mkdir(exist_ok=True)
    assert not (out / 'native.json').exists(), 'preserve native negative evidence'
    baseline = config.OUT / 'baseline-v1/right/full'
    candidate = config.OUT / 'candidate-v1/right/full'
    left = config.load_json(baseline / 'report.json')
    right = config.load_json(candidate / 'report.json')
    prep = config.load_json(config.OUT / 'candidate-v1/preparation.json')
    executed = {Path(p).name: core.sha(Path(p).read_bytes()) for p in (capture.__file__, capture_candidate.__file__, core.__file__, config.__file__)}
    print('WITNESS executing profile parser/comparison helpers ' + str(executed), flush=True)
    capture_candidate.compare_reports(copy.deepcopy(right), left, prep, candidate, baseline)
    print('CONTROL PASS unchanged actual native reports and pixels', flush=True)
    results = []

    def expect(name, label, call):
        try:
            call()
        except ValueError as error:
            assert str(error) == 'profile capture: ' + label, 'negative reached wrong failure:' + name + ':' + str(error)
            results.append({'name': name, 'status': 'FIRED', 'expected_failure': str(error)})
            print('FIRED ' + name + ': ' + str(error), flush=True)
        else:
            raise AssertionError('negative SURVIVED:' + name)

    # Reparse one disposable captured log with the selected direct path changed.
    # Only PPM inputs are hard-linked; the parser writes new PNGs in this folder.
    altered = out / 'wrong-selected-path'
    altered.mkdir()
    for path in baseline.glob('*.ppm'):
        os.link(path, altered / path.name)
    log = (baseline / 'capture.log').read_text()
    target = 'chosen path: FC'
    assert log.count(target) == 1, 'unique direct path mutation site'
    (altered / 'capture.log').write_text(log.replace(target, 'chosen path: FDC', 1), encoding='utf-8')
    expect('wrong-selected-path', 'actual selected direct path:travel', lambda: capture.parse(altered, 'full', 'right'))

    changed_time = copy.deepcopy(right)
    changed_time['displays'][1]['logical_ms'] += 20
    expect('changed-display-time', 'identical native display logical_ms', lambda: capture_candidate.compare_reports(changed_time, left, prep, candidate, baseline))

    # Change one byte of a standing000 capture in memory. Update that report's
    # own hash, so the meaningful unchanged-pixel check must reject it.
    changed_pixel = copy.deepcopy(right)
    draw = next(row for row in changed_pixel['displays'] if row['actual_draw'][3] == 0)
    path = candidate / draw['ppm']
    original_read = core.codec.ppm
    pixels = bytearray(original_read(path))
    pixels[0] ^= 1
    changed = bytes(pixels)
    draw['pixels_sha256'] = core.sha(changed)
    core.codec.ppm = lambda p: changed if Path(p) == path else original_read(p)
    try:
        expect('changed-approved-standing-pixel', 'all prior-approved pose/background pixels unchanged', lambda: capture_candidate.compare_reports(changed_pixel, left, prep, candidate, baseline))
    finally:
        core.codec.ppm = original_read
    capture_candidate.compare_reports(copy.deepcopy(right), left, prep, candidate, baseline)
    print('CONTROL PASS restored comparison on original captured inputs', flush=True)
    binding = config.load_json(config.OUT / 'baseline-v1/build.json')
    core.require(core.protected() == binding['protected_sha256'], 'protected inputs unchanged after negatives')
    record = {'status': 'PASS', 'positive_control_before_and_after': True, 'executed_helper_sha256': executed,
              'harness_sha256': core.sha(Path(__file__).read_bytes()), 'mutations': results,
              'native_build_witness': {'executable_sha256': binding['executable_sha256'], 'build_started_ns': binding['build_started_ns'], 'executable_mtime_ns': binding['executable_mtime_ns']},
              'scope': 'Three executed input mutations through current Python parser/comparison guards. The original freshly built native observer produced the bound baseline/candidate; no mutated engine was built or claimed.'}
    core.save(out / 'native.json', record)


if __name__ == '__main__':
    main()
