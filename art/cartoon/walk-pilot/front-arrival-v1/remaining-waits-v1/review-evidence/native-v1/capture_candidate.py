"""Compare complete native rings, permitting changes only in configured new art."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import capture
import config
import native_core as core

OUT = Path('/out')
BASE = OUT / 'baseline-v1'
CANDIDATE = OUT / 'candidate-v1'


def outside_equal(a, b, box):
    x0, y0, x1, y1 = box
    core.require(0 <= x0 < x1 <= 1280 and 0 <= y0 < y1 <= 960, 'valid placed candidate canvas')
    for y in range(960):
        row = y * 3840
        if y0 <= y < y1:
            if a[row:row + x0 * 3] != b[row:row + x0 * 3] or a[row + x1 * 3:row + 3840] != b[row + x1 * 3:row + 3840]:
                return False
        elif a[row:row + 3840] != b[row:row + 3840]:
            return False
    return True


def compare(clip, phase, prep, binding):
    folder = CANDIDATE / clip / phase
    core.require(not folder.exists(), 'preserve candidate phase:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(CANDIDATE / 'scrantic_data.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    exe = BASE / 'waiting_ring_probe'
    command = [str(exe), 'cartoon', phase, clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=120)
    core.require(result.returncode == 0, 'candidate native exit; retained log')
    prior_folder = BASE / clip / phase
    expected = json.loads((prior_folder / 'report.json').read_bytes())
    report = capture.parse(folder, phase, clip, candidate=True)
    for key in ('clip', 'segments', 'completed_waits', 'display_count', 'duration_ms'):
        core.require(report[key] == expected[key], 'unchanged native ' + key)
    replacements = {f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png': f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' for frame in config.CANDIDATE_FRAMES}
    core.require(report['loaded_art'] == sorted(replacements.get(name, name) for name in expected['loaded_art']), 'only000015 dependencies change')
    canvases = {row['frame']: row['canvas'] for row in prep['added_members']}
    core.require(set(canvases) == set(config.CANDIDATE_FRAMES), 'only configured candidate canvases')
    changed = 0
    for observed, prior in zip(report['displays'], expected['displays']):
        for key in ('index', 'logical_ms', 'segment', 'segment_ms', 'heading', 'actual_draw', 'stored_walk_row', 'draw_ordinal', 'duration_ms'):
            core.require(observed[key] == prior[key], 'identical native display ' + key)
        before = core.codec.ppm(prior_folder / prior['ppm'])
        after = core.codec.ppm(folder / observed['ppm'])
        core.require(core.sha(before) == prior['pixels_sha256'], 'bound baseline image')
        flip, x, y, frame = observed['actual_draw']
        if frame in canvases:
            width, height = canvases[frame]
            box = [x * 2, y * 2, x * 2 + width, y * 2 + height]
            core.require(outside_equal(before, after, box), 'unchanged outside placed frame:' + str(frame))
            core.require(before != after, 'new candidate visible:' + str(frame))
            observed['allowed_change_box'] = box
            observed['comparison'] = f'different only inside placed{frame:03} canvas'
            changed += 1
        else:
            core.require(before == after, 'all prior-approved pose/background pixels unchanged')
            observed['allowed_change_box'] = None
            observed['comparison'] = 'full display identical; approved pose retained'
        observed['baseline_pixels_sha256'] = prior['pixels_sha256']
    report.update({'control': False, 'changed_displays': changed, 'unchanged_displays': len(report['displays']) - changed,
                   'archive_sha256': prep['archive_sha256'], 'base_archive_sha256': prep['base_archive_sha256'],
                   'executable_sha256': binding['executable_sha256'], 'command': command, 'exit_code': result.returncode})
    core.save(folder / 'report.json', report)
    print(f'PASS candidate {clip} {phase}: {len(report["displays"])} displays; {changed} inside000015 changes', flush=True)
    return report


def main():
    print('WITNESS ring candidate SHA256=' + core.sha(Path(__file__).read_bytes()), flush=True)
    binding = json.loads((BASE / 'build.json').read_bytes())
    prep = json.loads((CANDIDATE / 'preparation.json').read_bytes())
    core.require(core.protected() == binding['protected_sha256'], 'unchanged protected production inputs')
    core.require(core.sha((BASE / 'waiting_ring_probe').read_bytes()) == binding['executable_sha256'] == prep['baseline_executable_sha256'], 'same native observer')
    core.require(core.sha((OUT / 'baseline-pack.zip').read_bytes()) == prep['base_archive_sha256'], 'approved baseline ZIP identity')
    core.require(core.sha((CANDIDATE / 'scrantic_data.zip').read_bytes()) == prep['archive_sha256'], 'candidate ZIP identity')
    results = {}
    for clip in config.CLIPS:
        compare(clip, 'smoke', prep, binding)
        report = compare(clip, 'full', prep, binding)
        results[clip] = {key: report[key] for key in ('display_count', 'duration_ms', 'changed_displays', 'unchanged_displays')}
    core.require(core.protected() == binding['protected_sha256'], 'protected production inputs after both clips')
    core.save(CANDIDATE / 'summary.json', {'status': 'PASS', 'clips': results, 'archive_sha256': prep['archive_sha256'],
         'baseline_pack_sha256': prep['base_archive_sha256'], 'executable_sha256': binding['executable_sha256'],
         'capture_helper_sha256': core.sha(Path(__file__).read_bytes()), 'scope': 'Native complete rings; only000015 new. Prior approved artwork exact; no human approval/publication/production writes.'})


if __name__ == '__main__':
    main()
