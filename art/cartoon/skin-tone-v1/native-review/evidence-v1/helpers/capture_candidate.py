"""Capture corrected colors with unchanged routes, timing and skin-only pixels."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import traceback
import zipfile
from mask_data import LMask
import capture
import config
import native_core as core
import skin_compare
from skin_compare import compare_reports


def verify_prepared(target):
    prep = config.load_json(target / 'preparation.json')
    core.require(core.sha((target / 'scrantic_data.zip').read_bytes()) == prep['archive_sha256'], 'prepared package identity')
    core.require(prep['base_archive_sha256'] == config.BASELINE_SHA, 'selected uncorrected baseline')
    core.require(core.sha((target / 'correction-recipe.json').read_bytes()) == prep['recipe_sha256'], 'prepared correction recipe')
    core.require(core.sha((target / 'input-index.json').read_bytes()) == prep['input_index_sha256'], 'prepared frozen index')
    core.require([r['frame'] for r in prep['replaced_members']] == list(config.TARGET_FRAMES), 'prepared28 frame scope')
    masks = {}
    with zipfile.ZipFile(target / 'scrantic_data.zip') as archive:
        for row in prep['replaced_members']:
            path = target / row['mask']
            core.require(core.sha(path.read_bytes()) == row['mask_sha256'], 'prepared mask:' + str(row['frame']))
            core.require(core.sha(archive.read(row['member'])) == row['sha256'], 'prepared sprite:' + str(row['frame']))
            decoded = (target / row['mask_l']).read_bytes()
            core.require(core.sha(decoded) == row['mask_l_sha256'], 'prepared decoded mask:' + str(row['frame']))
            masks[row['frame']] = LMask(row['canvas'], decoded)
    return prep, masks


def compare(target, clip, phase, prep, binding, masks):
    folder = target / clip / phase
    core.require(not folder.exists(), 'preserve color capture:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(target / 'scrantic_data.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    exe = core.BASE / 'connecting_walk_probe'
    core.require(core.sha(exe.read_bytes()) == binding['executable_sha256'], 'same baseline executable')
    core.require(core.sha((folder / 'scrantic_data.zip').read_bytes()) == prep['archive_sha256'], 'corrected execution package')
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=120)
    core.require(result.returncode == 0, 'corrected native exit; log retained')
    prior_folder = core.BASE / clip / phase
    expected = config.load_json(prior_folder / 'report.json')
    report = capture.parse(folder, phase, clip, candidate=True)
    count, frames = compare_reports(report, expected, prep, folder, prior_folder, masks)
    report.update(changed_displays=count, unchanged_displays=len(report['displays'])-count,
                  frames_with_visible_color_changes=sorted(frames),
                  archive_sha256=prep['archive_sha256'], base_archive_sha256=config.BASELINE_SHA,
                  executable_sha256=binding['executable_sha256'], command=command, exit_code=result.returncode)
    core.save(folder / 'report.json', report)
    print(f'PASS corrected {clip} {phase}: {len(report["displays"])} displays; {count} skin-only changes', flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-version', type=int, default=1)
    args = parser.parse_args()
    core.require(args.candidate_version > 0, 'positive candidate version')
    target = config.OUT / f'candidate-v{args.candidate_version}'
    print('WITNESS skin capture SHA256=' + core.sha(Path(__file__).read_bytes()), flush=True)
    prep, masks = verify_prepared(target)
    binding = config.load_json(core.BASE / 'build.json')
    core.require(config.load_json(core.BASE / 'summary.json')['status'] == 'PASS', 'complete baseline checks')
    core.require(core.protected() == binding['protected_sha256'], 'protected inputs before corrected capture')
    results, seen, changed_frames = {}, set(), set()
    for clip in config.CLIPS:
        compare(target, clip, 'smoke', prep, binding, masks)
    print('PASS all eight corrected smoke checks before regression', flush=True)
    for clip in config.CLIPS:
        full = compare(target, clip, 'full', prep, binding, masks)
        repeat = compare(target, clip, 'repeat', prep, binding, masks)
        for field in ('displays', 'segments', 'completed_waits', 'loaded_art'):
            core.require(full[field] == repeat[field], 'exact fresh corrected repeat:' + clip + ':' + field)
        seen.update(d['actual_draw'][3] for d in full['displays'])
        changed_frames.update(full['frames_with_visible_color_changes'])
        results[clip] = {k: full[k] for k in ('display_count', 'duration_ms', 'changed_displays', 'unchanged_displays')}
    core.require(seen == set(config.TARGET_FRAMES), 'all28 frames observed')
    expected_changed = {r['frame'] for r in prep['replaced_members'] if r['changed_pixels']}
    core.require(changed_frames == expected_changed, 'all corrected poses visibly covered; unchanged reference preserved')
    core.require(core.protected() == binding['protected_sha256'], 'protected inputs after corrected capture')
    verify_prepared(target)
    core.save(target / 'summary.json', {
        'status': 'PASS', 'clips': results, 'frames_seen': sorted(seen),
        'frames_with_visible_color_changes': sorted(changed_frames),
        'archive_sha256': prep['archive_sha256'], 'baseline_sha256': config.BASELINE_SHA,
        'recipe_sha256': prep['recipe_sha256'], 'executable_sha256': binding['executable_sha256'],
        'helper_sha256': core.sha(Path(__file__).read_bytes()),
        'comparison_helper_sha256': core.sha(Path(skin_compare.__file__).read_bytes()),
        'scope': 'Eight actual native clips: smoke, full exact timing/placement and transformed skin-mask comparison, fresh repeats. No production promotion.'})


if __name__ == '__main__':
    try:
        main()
    except Exception:
        core.save(config.OUT / 'corrected-failure.json', {'traceback': traceback.format_exc()})
        raise
