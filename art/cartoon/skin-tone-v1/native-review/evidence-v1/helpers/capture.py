"""Capture eight native clips against the uncorrected connecting package."""
import os
from pathlib import Path
import shutil
import subprocess
import traceback
import config
import native_core as core
from legacy import load_previous

_previous = load_previous('capture')
OUT, BASE = config.OUT, core.BASE


def parse(folder, phase, clip, candidate=False):
    # Both packages contain009/010/012. The old flag selects these dependencies.
    report = _previous.parse(folder, phase, clip, candidate=True)
    report['candidate'] = candidate
    report['scope'] = 'Actual port route/wait timing and drawing; no original-binary parity claim.'
    return report


def capture(exe, binding, clip, phase):
    folder = BASE / clip / phase
    core.require(not folder.exists(), 'preserve skin baseline:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(OUT / 'baseline-pack.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=120)
    core.require(result.returncode == 0, 'baseline native exit; retained log:' + clip + ':' + phase)
    report = parse(folder, phase, clip)
    report.update(command=command, exit_code=result.returncode,
                  archive_sha256=core.sha((folder / 'scrantic_data.zip').read_bytes()),
                  executable_sha256=core.sha(exe.read_bytes()))
    core.require(report['archive_sha256'] == binding['baseline_pack_sha256'] == config.BASELINE_SHA,
                 'exact connecting baseline execution')
    core.save(folder / 'report.json', report)
    print(f'PASS baseline {clip} {phase}: {report["display_count"]} displays, {report["duration_ms"]}ms', flush=True)
    return report


def main():
    print('WITNESS skin baseline SHA256=' + core.sha(Path(__file__).read_bytes()), flush=True)
    exe, binding = core.build()
    results, seen = {}, set()
    for clip in config.CLIPS:
        capture(exe, binding, clip, 'smoke')
    print('PASS all eight native smoke checks before regression', flush=True)
    for clip in config.CLIPS:
        report = capture(exe, binding, clip, 'full')
        repeat = capture(exe, binding, clip, 'repeat')
        for key in ('displays', 'segments', 'completed_waits', 'loaded_art'):
            core.require(report[key] == repeat[key], 'exact fresh baseline repeat:' + clip + ':' + key)
        seen.update(d['actual_draw'][3] for d in report['displays'])
        results[clip] = {key: report[key] for key in ('display_count', 'duration_ms', 'segments')}
    core.require(seen == set(config.TARGET_FRAMES), 'all28 actual Johnny frames covered')
    core.require(core.protected() == binding['protected_sha256'], 'protected production inputs unchanged')
    core.save(BASE / 'summary.json', {
        'status': 'PASS', 'clips': results, 'frames_seen': sorted(seen),
        'baseline_pack_sha256': binding['baseline_pack_sha256'],
        'executable_sha256': binding['executable_sha256'],
        'capture_helper_sha256': core.sha(Path(__file__).read_bytes()),
        'scope': 'Eight smoke checks before full and fresh repeats; uncorrected connecting baseline.'})
    print('PASS eight baseline clips cover all28 frames; production unchanged', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        core.save(OUT / 'baseline-failure.json', {'traceback': traceback.format_exc()})
        raise
