"""Execute candidate-v2 comparison negatives on fresh native capture evidence."""
import copy
import io
from pathlib import Path
import sys
import zipfile

from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'assets/scrantic_data.zip').is_file())
HERE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
sys.path.insert(0, str(HERE))
import config
import capture_candidate
import native_core as core


def main():
    out = config.OUT / 'negative-controls'
    destination = out / 'native-v2.json'
    assert not destination.exists(), 'preserve candidate-v2 comparison controls'
    baseline = config.OUT / 'baseline-v1/front_arc/full'
    candidate = config.OUT / 'candidate-v2/front_arc/full'
    assert config.load_json(config.OUT / 'candidate-v2/summary.json')['status'] == 'PASS'
    left = config.load_json(baseline / 'report.json')
    right = config.load_json(candidate / 'report.json')
    prep = config.load_json(config.OUT / 'candidate-v2/preparation.json')
    executed = {Path(p).name: core.sha(Path(p).read_bytes()) for p in (capture_candidate.__file__, core.__file__, config.__file__)}
    print('WITNESS executing connecting comparison helpers ' + str(executed), flush=True)
    capture_candidate.compare_reports(copy.deepcopy(right), left, prep, candidate, baseline)
    print('CONTROL PASS actual candidate-v2 reports and pixels', flush=True)
    results = []

    def expect(name, label, call, detail):
        try:
            call()
        except ValueError as error:
            assert str(error) == 'connecting capture: ' + label, 'wrong failure:' + name + ':' + str(error)
            results.append({'name': name, 'status': 'FIRED', 'expected_failure': str(error), 'mutation': detail})
            print('FIRED ' + name + ': ' + str(error), flush=True)
        else:
            raise AssertionError('candidate comparison negative SURVIVED:' + name)

    changed_time = copy.deepcopy(right)
    changed_time['displays'][1]['logical_ms'] += 20
    expect('changed-display-time', 'identical native display logical_ms',
           lambda: capture_candidate.compare_reports(changed_time, left, prep, candidate, baseline),
           {'display_index': 1, 'delta_ms': 20})

    def pixel_control(name, frame, label, select_pixel):
        altered = copy.deepcopy(right)
        draw = next(row for row in altered['displays'] if row['actual_draw'][3] == frame)
        path = candidate / draw['ppm']
        original_read = core.codec.ppm
        original = original_read(path)
        x, y, reason = select_pixel(draw)
        pixels = bytearray(original)
        offset = (y * 1280 + x) * 3
        pixels[offset] ^= 1
        changed = bytes(pixels)
        assert len(changed) == len(original) and changed != original
        draw['pixels_sha256'] = core.sha(changed)
        core.codec.ppm = lambda p: changed if Path(p) == path else original_read(p)
        try:
            expect(name, label,
                   lambda: capture_candidate.compare_reports(altered, left, prep, candidate, baseline),
                   {'frame': frame, 'display_index': draw['index'], 'pixel': [x, y],
                    'component': 'red', 'xor': 1, 'report_hash_updated': True, 'location_basis': reason})
        finally:
            core.codec.ppm = original_read

    def outside(draw):
        _, x, y, _ = draw['actual_draw']
        assert x > 0 and y > 0
        return 0, 0, 'Outside the exact placed009 canvas.'

    pixel_control('changed-outside-candidate-canvas', 9, 'unchanged outside placed frame:9', outside)

    def opaque_standing(draw):
        flip, x, y, frame = draw['actual_draw']
        with zipfile.ZipFile(config.OUT / 'baseline-pack.zip') as archive:
            data = archive.read(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png')
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            alpha = image.getchannel('A')
            sx, sy = next((sx, sy) for sy in range(height) for sx in range(width) if alpha.getpixel((sx, sy)) == 255)
            return x * 2 + (width - 1 - sx if flip else sx), y * 2 + sy, 'An alpha255 pixel of the retained approved017 PNG, mirrored according to the actual draw.'

    pixel_control('changed-approved-standing-pixel', 17, 'all prior-approved pose/background pixels unchanged', opaque_standing)
    capture_candidate.compare_reports(copy.deepcopy(right), left, prep, candidate, baseline)
    print('CONTROL PASS restored original native capture comparisons', flush=True)
    binding = config.load_json(config.OUT / 'baseline-v1/build.json')
    core.require(core.protected() == binding['protected_sha256'], 'production inputs unchanged after candidate negatives')
    record = {'status': 'PASS', 'candidate_version': 2, 'positive_control_before_and_after': True,
        'executed_helper_sha256': executed, 'harness_sha256': core.sha(Path(__file__).read_bytes()),
        'candidate_archive_sha256': prep['archive_sha256'], 'selection_sha256': prep['selection_sha256'],
        'baseline_report_sha256': core.sha((baseline / 'report.json').read_bytes()),
        'candidate_report_sha256': core.sha((candidate / 'report.json').read_bytes()), 'mutations': results,
        'native_build_witness': {key: binding[key] for key in ('executable_sha256', 'build_started_ns', 'executable_mtime_ns')},
        'scope': 'Three executed input mutations through the real comparison on candidate-v2 front_arc. Capture files remain untouched; altered pixel readers and matching report hashes exist only in memory. No modified-engine replay claim.'}
    core.save(destination, record)
    print('PASS three exact candidate-v2 comparison failures with restored positive control')


if __name__ == '__main__':
    main()
