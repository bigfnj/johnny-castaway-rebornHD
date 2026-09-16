"""Capture the same native calls; changes are limited to placed profile canvases."""
import os
from pathlib import Path
import shutil
import subprocess
import traceback
import capture
import config
import native_core as core

OUT, BASE = config.OUT, core.BASE
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


def compare_reports(report, expected, prep, folder, prior_folder):
    for key in ('clip', 'segments', 'completed_waits', 'display_count', 'duration_ms'):
        core.require(report[key] == expected[key], 'unchanged native ' + key)
    replacements = {f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png': f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' for frame in config.CANDIDATE_FRAMES}
    core.require(report['loaded_art'] == sorted(replacements.get(name, name) for name in expected['loaded_art']), 'only profile dependencies change')
    canvases = {row['frame']: row['canvas'] for row in prep['added_members']}
    core.require(set(canvases) == set(config.CANDIDATE_FRAMES), 'only configured candidate canvases')
    changed = 0
    for observed, prior in zip(report['displays'], expected['displays']):
        for key in ('index', 'logical_ms', 'segment', 'segment_ms', 'role', 'actual_draw', 'stored_walk_row', 'draw_ordinal', 'stage_draw_ordinal', 'duration_ms'):
            core.require(observed[key] == prior[key], 'identical native display ' + key)
        before = core.codec.ppm(prior_folder / prior['ppm'])
        after = core.codec.ppm(folder / observed['ppm'])
        core.require(core.sha(before) == prior['pixels_sha256'], 'bound baseline image')
        core.require(core.sha(after) == observed['pixels_sha256'], 'bound candidate image')
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
    return changed


def compare(clip, phase, prep, binding):
    folder = CANDIDATE / clip / phase
    core.require(not folder.exists(), 'preserve candidate phase:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(CANDIDATE / 'scrantic_data.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    exe = BASE / 'profile_walk_probe'
    core.require(core.sha(exe.read_bytes()) == binding['executable_sha256'], 'same baseline native executable')
    core.require(core.sha((folder / 'scrantic_data.zip').read_bytes()) == prep['archive_sha256'], 'selected private package identity')
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')), stdout=log, stderr=subprocess.STDOUT, timeout=120)
    core.require(result.returncode == 0, 'candidate native exit; retained log')
    prior_folder = BASE / clip / phase
    expected = config.load_json(prior_folder / 'report.json')
    report = capture.parse(folder, phase, clip, candidate=True)
    changed = compare_reports(report, expected, prep, folder, prior_folder)
    report.update(control=False, changed_displays=changed, unchanged_displays=len(report['displays']) - changed, archive_sha256=prep['archive_sha256'],
                  base_archive_sha256=prep['base_archive_sha256'], executable_sha256=binding['executable_sha256'], command=command, exit_code=result.returncode)
    core.save(folder / 'report.json', report)
    print(f'PASS candidate {clip} {phase}: {len(report["displays"])} displays; {changed} inside-profile changes', flush=True)
    return report


def main():
    print('WITNESS profile candidate SHA256=' + core.sha(Path(__file__).read_bytes()), flush=True)
    prep = config.load_json(CANDIDATE / 'preparation.json')
    binding = config.load_json(BASE / 'build.json')
    core.require(config.load_json(BASE / 'summary.json')['status'] == 'PASS', 'completed baseline smoke and regressions')
    core.require(core.protected() == binding['protected_sha256'], 'unchanged protected inputs before candidate')
    results = {}
    for clip in config.CLIPS:
        compare(clip, 'smoke', prep, binding)
        report = compare(clip, 'full', prep, binding)
        repeat = compare(clip, 'repeat', prep, binding)
        for field in ('displays', 'segments', 'completed_waits', 'loaded_art'):
            core.require(report[field] == repeat[field], 'exact fresh candidate repeat:' + clip + ':' + field)
        results[clip] = {key: report[key] for key in ('display_count', 'duration_ms', 'changed_displays', 'unchanged_displays')}
    core.require(core.protected() == binding['protected_sha256'], 'all protected production inputs unchanged')
    core.save(CANDIDATE / 'summary.json', {'status': 'PASS', 'clips': results, 'archive_sha256': prep['archive_sha256'], 'baseline_sha256': prep['base_archive_sha256'],
              'executable_sha256': binding['executable_sha256'], 'helper_sha256': core.sha(Path(__file__).read_bytes()), 'parser_sha256': core.sha(Path(capture.__file__).read_bytes()),
              'scope': 'Each of four candidate clips smoke then full exact baseline comparison then fresh-process repeat. Eight profile canvases only; all prior-approved poses and backgrounds unchanged.'})
    print('PASS four candidate clips; exact timing and scoped pixels; production unchanged', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        core.save(OUT / 'candidate-failure.json', {'traceback': traceback.format_exc(), 'helper_sha256': core.sha(Path(__file__).read_bytes())})
        raise
