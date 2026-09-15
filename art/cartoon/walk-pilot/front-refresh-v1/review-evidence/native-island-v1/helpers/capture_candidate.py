"""Capture a private028/029 candidate with the already-bound native observer."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import capture

OUT = Path('/out')
SOURCE = Path('/source')
BASE = OUT / 'baseline-v1'


def outside_equal(a, b, box):
    x0, y0, x1, y1 = box
    capture.require(0 <= x0 < x1 <= 1280 and 0 <= y0 < y1 <= 960, 'candidate valid placed canvas')
    for y in range(960):
        row = y * 3840
        if y0 <= y < y1:
            if a[row:row + x0 * 3] != b[row:row + x0 * 3] or a[row + x1 * 3:row + 3840] != b[row + x1 * 3:row + 3840]:
                return False
        elif a[row:row + 3840] != b[row:row + 3840]:
            return False
    return True


def compare(folder, phase, preparation, binding):
    exe = BASE / 'front_route_probe'
    destination = folder / phase
    capture.require(not destination.exists(), 'preserve candidate captures:' + phase)
    destination.mkdir()
    shutil.copyfile(folder / 'scrantic_data.zip', destination / 'scrantic_data.zip')
    (destination / 'profile').mkdir()
    command = [str(exe), 'cartoon', phase]
    with (destination / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=destination,
                                env=dict(os.environ, HOME=str(destination / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    capture.require(result.returncode == 0, phase + ': candidate native exit; retained capture.log')
    expected = json.loads((BASE / phase / 'report.json').read_bytes())
    report = capture.parse(destination, phase, capture.contract())
    for field in ('path_seed', 'api', 'actual_path', 'observed_rows', 'actual_draws',
                  'native_delay_returns_ticks', 'native_completed_waits', 'display_count', 'duration_ms', 'loaded_art'):
        capture.require(report[field] == expected[field], phase + ': exact baseline ' + field)
    canvases = {item['frame']: item['canvas'] for item in preparation['replaced_members']}
    changed = 0
    for observed, prior in zip(report['displays'], expected['displays']):
        for field in ('index', 'logical_ms', 'stored_walk_row', 'actual_draw', 'duration_ms'):
            capture.require(observed[field] == prior[field], phase + ': identical display ' + field)
        previous = capture.codec.ppm(BASE / phase / prior['ppm'])
        pixels = capture.codec.ppm(destination / observed['ppm'])
        capture.require(capture.sha(previous) == prior['pixels_sha256'], phase + ': baseline pixels identity')
        flip, x, y, frame = observed['actual_draw']
        if frame in canvases:
            width, height = canvases[frame]
            box = [x * 2, y * 2, x * 2 + width, y * 2 + height]
            capture.require(outside_equal(previous, pixels, box),
                            f'{phase}: unchanged outside placed frame{frame:03} canvas:{observed["index"]}')
            capture.require(previous != pixels, f'{phase}: candidate visible in frame{frame:03}:{observed["index"]}')
            observed['allowed_change_box'] = box
            observed['comparison'] = 'different only inside placed028/029 canvas'
            changed += 1
        else:
            capture.require(previous == pixels, f'{phase}: unchanged full display frame{frame:03}:{observed["index"]}')
            observed['allowed_change_box'] = None
            observed['comparison'] = 'full display identical'
        observed['baseline_pixels_sha256'] = prior['pixels_sha256']
    report.update({'control': False, 'changed_displays': changed, 'unchanged_displays': len(report['displays']) - changed,
                   'archive_sha256': preparation['archive_sha256'], 'base_archive_sha256': preparation['base_archive_sha256'],
                   'executable_sha256': binding['executable_sha256'], 'exit_code': result.returncode,
                   'command': command, 'scope': 'Private028/029 native candidate, same observer and route as production28. All other frames, including mirrored HD017 arrival, remain unchanged.'})
    capture.save(destination / 'report.json', report)
    print(f'PASS candidate {phase}: {len(report["displays"])} displays; {changed} differ only inside placed028/029 canvases', flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=OUT / 'candidate-v1')
    args = parser.parse_args()
    folder = args.candidate
    print('WITNESS front capture_candidate.py SHA256=' + capture.sha(Path(__file__).read_bytes()), flush=True)
    binding = json.loads((BASE / 'build.json').read_bytes())
    preparation = json.loads((folder / 'preparation.json').read_bytes())
    capture.require(capture.protected() == binding['protected_sha256'], 'unchanged protected production inputs')
    capture.require(capture.sha((BASE / 'front_route_probe').read_bytes()) == binding['executable_sha256']
                    == preparation['baseline_executable_sha256'], 'same native observer')
    capture.require(capture.sha((folder / 'scrantic_data.zip').read_bytes()) == preparation['archive_sha256'],
                    'private candidate ZIP identity')
    capture.require(capture.sha((SOURCE / 'assets/scrantic_data.zip').read_bytes()) == preparation['base_archive_sha256'],
                    'unchanged baseline production ZIP identity')
    smoke = compare(folder, 'smoke', preparation, binding)
    full = compare(folder, 'full', preparation, binding)
    capture.require(capture.protected() == binding['protected_sha256'], 'preserved production inputs after capture')
    capture.save(folder / 'summary.json', {'status': 'PASS', 'phases': ['smoke', 'full'],
                 'same_observer_sha256': binding['executable_sha256'], 'archive_sha256': preparation['archive_sha256'],
                 'base_archive_sha256': preparation['base_archive_sha256'], 'display_count': full['display_count'],
                 'duration_ms': full['duration_ms'], 'path_seed': full['path_seed'],
                 'changed_displays': full['changed_displays'], 'unchanged_displays': full['unchanged_displays'],
                 'fixed_closeup_hd': [560, 400, 400, 280],
                 'final_arrival': 'HD017 mirrored at (293,243), every arrival display identical to baseline',
                 'capture_helper_sha256': capture.sha(Path(__file__).read_bytes()),
                 'scope': 'Technical native comparison only; no human approval, publishing or production promotion.'})


if __name__ == '__main__':
    main()
