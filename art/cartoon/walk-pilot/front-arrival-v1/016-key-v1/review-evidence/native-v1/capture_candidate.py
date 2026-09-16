"""Capture a hash-bound016 candidate in both actual native turn directions."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import capture

OUT = Path('/out')
BASE = OUT / 'baseline-v1'


def outside_equal(a, b, box):
    x0, y0, x1, y1 = box
    capture.require(0 <= x0 < x1 <= 1280 and 0 <= y0 < y1 <= 960, 'valid placed016 canvas')
    for y in range(960):
        row = y * 3840
        if y0 <= y < y1:
            if a[row:row + x0 * 3] != b[row:row + x0 * 3] or a[row + x1 * 3:row + 3840] != b[row + x1 * 3:row + 3840]:
                return False
        elif a[row:row + 3840] != b[row:row + 3840]:
            return False
    return True


def compare(folder, clip, phase, preparation, binding):
    exe = BASE / 'front_turn_probe'
    destination = folder / clip / phase
    capture.require(not destination.exists(), 'preserve candidate capture:' + clip + ':' + phase)
    destination.mkdir(parents=True)
    shutil.copyfile(folder / 'scrantic_data.zip', destination / 'scrantic_data.zip')
    (destination / 'profile').mkdir()
    command = [str(exe), 'cartoon', phase, clip]
    with (destination / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=destination, env=dict(os.environ, HOME=str(destination / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    capture.require(result.returncode == 0, 'candidate exit:' + clip + ':' + phase)
    expected_folder = BASE / clip / phase
    expected = json.loads((expected_folder / 'report.json').read_bytes())
    report = capture.parse(destination, phase, clip, capture.contract(), candidate016=True)
    for field in ('clip', 'segments', 'completed_waits', 'display_count', 'duration_ms'):
        capture.require(report[field] == expected[field], 'same native ' + field + ':' + clip)
    dependencies = sorted('data/styles/cartoon/BMP/JOHNWALK.BMP/016.png' if name == 'data/hd/BMP/JOHNWALK.BMP/016.png' else name for name in expected['loaded_art'])
    capture.require(report['loaded_art'] == dependencies, 'only016 dependency changed')
    changes = preparation['added_members']
    capture.require(len(changes) == 1 and changes[0]['frame'] == 16, 'only016 candidate canvas')
    width, height = changes[0]['canvas']
    changed = 0
    for observed, previous in zip(report['displays'], expected['displays']):
        for field in ('index', 'logical_ms', 'segment', 'segment_ms', 'stored_walk_row', 'actual_draw', 'draw_ordinal', 'duration_ms'):
            capture.require(observed[field] == previous[field], 'same display ' + field)
        before = capture.codec.ppm(expected_folder / previous['ppm'])
        after = capture.codec.ppm(destination / observed['ppm'])
        capture.require(capture.sha(before) == previous['pixels_sha256'], 'bound baseline pixels')
        flip, x, y, frame = observed['actual_draw']
        if frame == 16:
            box = [x * 2, y * 2, x * 2 + width, y * 2 + height]
            capture.require(outside_equal(before, after, box), 'unchanged outside016 canvas:' + str(observed['index']))
            capture.require(before != after, 'candidate016 visibly rendered')
            observed['allowed_change_box'] = box
            observed['comparison'] = 'different only inside placed016 canvas'
            changed += 1
        else:
            capture.require(before == after, 'approved017 and full background pixels unchanged:' + str(observed['index']))
            observed['allowed_change_box'] = None
            observed['comparison'] = 'full display identical; approved017 retained'
        observed['baseline_pixels_sha256'] = previous['pixels_sha256']
    report.update({'control': False, 'changed_displays': changed, 'unchanged_displays': len(report['displays']) - changed,
                   'archive_sha256': preparation['archive_sha256'], 'base_archive_sha256': preparation['base_archive_sha256'],
                   'executable_sha256': binding['executable_sha256'], 'command': command, 'exit_code': result.returncode})
    capture.save(destination / 'report.json', report)
    print(f'PASS candidate {clip} {phase}: {len(report["displays"])} displays, {changed} inside016 changes', flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=OUT / 'candidate-v1')
    args = parser.parse_args()
    print('WITNESS turn candidate SHA256=' + capture.sha(Path(__file__).read_bytes()), flush=True)
    folder = args.candidate
    binding = json.loads((BASE / 'build.json').read_bytes())
    prep = json.loads((folder / 'preparation.json').read_bytes())
    capture.require(capture.protected() == binding['protected_sha256'], 'unchanged protected production inputs')
    capture.require(capture.sha((BASE / 'front_turn_probe').read_bytes()) == binding['executable_sha256'] == prep['baseline_executable_sha256'], 'same bound native observer')
    capture.require(capture.sha((OUT / 'baseline-pack.zip').read_bytes()) == prep['base_archive_sha256'] == binding['baseline_pack_sha256'], 'approved017 baseline ZIP identity')
    capture.require(capture.sha((folder / 'scrantic_data.zip').read_bytes()) == prep['archive_sha256'], 'candidate ZIP identity')
    reports = {}
    for clip in capture.CLIPS:
        compare(folder, clip, 'smoke', prep, binding)
        full = compare(folder, clip, 'full', prep, binding)
        reports[clip] = {key: full[key] for key in ('display_count', 'duration_ms', 'changed_displays', 'unchanged_displays')}
    capture.require(capture.protected() == binding['protected_sha256'], 'preserved production inputs after capture')
    capture.save(folder / 'summary.json', {'status': 'PASS', 'clips': reports, 'archive_sha256': prep['archive_sha256'],
                 'baseline_pack_sha256': prep['base_archive_sha256'], 'executable_sha256': binding['executable_sha256'],
                 'capture_helper_sha256': capture.sha(Path(__file__).read_bytes()),
                 'scope': 'Two actual same-spot turn directions; new016 only, approved017 retained. No publication, human016 approval or production change.'})


if __name__ == '__main__':
    main()
