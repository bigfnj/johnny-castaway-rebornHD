"""One-time preservation of the executed first diagnostic; never needed for replay."""
from pathlib import Path
import json
import shutil

from capture import ROOT, HERE, require, save, sha


def main():
    destination = HERE / 'evidence-v1'
    require(not destination.exists(), 'historical evidence already exists')
    run = ROOT / 'build/shoreline-repair-v1/native-v1'
    phase = ROOT / 'build/shoreline-repair-v1/phase-probe-v1'
    preparation = ROOT / 'build/shoreline-repair-v1/selected-v1/preparation.json'
    summary = json.loads((run / 'captures/summary.json').read_text())
    require(summary['status'] == 'PASS', 'completed native comparison')
    for source in (run, phase):
        launch = json.loads((source / 'launch.json').read_text())
        require(launch['exit_code'] == 0 and launch['no_surviving_task_container'], 'completed isolated launch')
    files = [(preparation, 'preparation.json')]
    for source, label in ((run, 'native'), (phase, 'phase')):
        for path in sorted(source.rglob('*')):
            if path.is_file() and path.suffix in ('.json', '.log', '.txt'):
                files.append((path, label + '/' + path.relative_to(source).as_posix()))
    for path in sorted((ROOT / 'build/shoreline-repair-v1/toolchecks-v1').glob('*.json')):
        require(json.loads(path.read_text())['status'] == 'PASS', 'completed tool check')
        files.append((path, 'toolchecks/' + path.name))
    sources = {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in HERE.iterdir() if path.is_file()}
    for name in ('art/cartoon/seasonal-v1/native/capture.py',
                 'art/cartoon/seasonal-v1/native/driver.c',
                 'art/cartoon/shoreline-repair-v1/recipe-v1.json',
                 'art/cartoon/shoreline-repair-v1/candidates/v1/export-report.json'):
        sources[name] = sha((ROOT / name).read_bytes())
    for source in (run / 'captures/inputs.json', phase / 'captures/inputs.json', preparation):
        data = json.loads(source.read_text())
        for key in ('protected_sha256', 'dependencies_sha256', 'source_inputs_sha256'):
            for name, digest in data.get(key, {}).items():
                require(sha((ROOT / name).read_bytes()) == digest, 'current source binding:' + name)
                sources[name] = digest
    large = {}
    for source in (run, phase, ROOT / 'build/shoreline-repair-v1/selected-v1'):
        for path in sorted(source.rglob('*')):
            if path.is_file() and (path.suffix in ('.png', '.ppm', '.zip') or path.name == 'seasonal_probe'):
                large[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    destination.mkdir()
    manifest = {}
    for path, name in files:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        require(target.read_bytes() == path.read_bytes(), 'exact preserved copy:' + name)
        manifest[name] = {'sha256': sha(target.read_bytes()), 'source': path.relative_to(ROOT).as_posix()}
    binder = {'schema_version': 1, 'accepted': False, 'status': 'PASS',
              'scope': 'First three-wave static prototype, four still cases. Known clipped wave edges remain; no complete animation or human acceptance claim.',
              'files': manifest, 'source_sha256': sources, 'excluded_large_artifacts_sha256': large,
              'results': {'tool_smoke': 2, 'tool_regression_checks': 9, 'tool_named_refusals': 8,
                          'native_smoke': 8, 'native_fresh_repeats': 8, 'native_named_refusals': 2,
                          'production_only_phase_probe': 1, 'final_native_wave_frames': [3, 7, 9]},
              'replay': 'Follow native/README.md with fresh scratch directories. Do not rerun this one-time writer against historical evidence.'}
    save(destination / 'evidence.json', binder)
    reread = json.loads((destination / 'evidence.json').read_text())
    require(all(sha((destination / name).read_bytes()) == row['sha256'] for name, row in reread['files'].items()), 'manifest copied-file readback')
    require(all(sha((ROOT / name).read_bytes()) == digest for name, digest in reread['source_sha256'].items()), 'manifest source readback')
    print(f"PASS preserved/read back {len(manifest)} files and {len(sources)} source bindings; evidence {sha((destination / 'evidence.json').read_bytes())}")


if __name__ == '__main__':
    main()
