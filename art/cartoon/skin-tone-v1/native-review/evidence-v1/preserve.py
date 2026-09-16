"""One-shot snapshot of already completed native evidence; no capture/test rerun."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = ROOT / 'build/skin-tone/native-review'
TOOLS = HERE.parent


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def save(path, value):
    assert not path.exists(), 'preserve existing evidence:' + str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'size': path.stat().st_size}


def main():
    assert not (HERE / 'evidence.json').exists(), 'preserve frozen evidence'
    copied = []

    def copy(source, relative):
        target = HERE / relative
        assert not target.exists(), 'preserve copied evidence:' + relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        assert sha(target) == sha(source), 'byte-exact evidence copy:' + relative
        copied.append({'path': relative, 'source': source.relative_to(ROOT).as_posix(),
                       'sha256': sha(target), 'size': target.stat().st_size})

    candidate = load(OUT / 'candidate-v2/summary.json')
    baseline = load(OUT / 'baseline-v1/summary.json')
    build = load(OUT / 'baseline-v1/build.json')
    assert candidate['status'] == baseline['status'] == 'PASS'
    assert sum(row['display_count'] for row in candidate['clips'].values()) == 298
    assert sum(row['changed_displays'] for row in candidate['clips'].values()) == 286
    assert len(candidate['frames_seen']) == 28 and len(candidate['frames_with_visible_color_changes']) == 27
    for relative, wanted in build['protected_sha256'].items():
        assert sha(ROOT / relative) == wanted, 'unchanged captured source:' + relative

    for name in ('preparation.json', 'route_driver.c', 'trace_driver.c', 'candidate-v1-launch-failure.json'):
        copy(OUT / name, 'records/native/' + name)
    for version in ('baseline-v1', 'candidate-v1', 'candidate-v2'):
        for source in sorted((OUT / version).rglob('*')):
            if source.is_file() and source.suffix in ('.json', '.txt', '.log'):
                copy(source, 'records/native/' + source.relative_to(OUT).as_posix())
    copy(OUT / 'negative-controls/native-v2.json', 'records/native/negative-controls/native-v2.json')
    checks = ROOT / 'build/skin-tone/native-review-toolchecks-v3'
    for name in ('smoke.json', 'regression.json', 'inputs-v2.json'):
        copy(checks / name, 'records/toolchecks-v3/' + name)
    for source in sorted(TOOLS.glob('*.py')):
        copy(source, 'helpers/' + source.name)
    copy(TOOLS / 'README.md', 'helpers/README.md')
    prior = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
    dependencies = [prior / 'native_core.py', prior / 'capture.py',
                    ROOT / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py',
                    ROOT / 'art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/review-evidence/native-v1/route_driver.c',
                    ROOT / 'art/cartoon/walk-pilot/front-arrival-v1/trace/trace.py']
    for source in dependencies:
        copy(source, 'dependencies/' + source.relative_to(ROOT).as_posix())

    capture_rows = []
    for version in ('baseline-v1', 'candidate-v2'):
        for clip in candidate['clips']:
            for phase in ('smoke', 'full', 'repeat'):
                location = OUT / version / clip / phase
                report = load(location / 'report.json')
                for display in report['displays']:
                    row = pin(location / display['ppm'])
                    row.update(pixels_sha256=display['pixels_sha256'], index=display['index'],
                               logical_ms=display['logical_ms'], actual_draw=display['actual_draw'])
                    capture_rows.append(row)
                capture_rows.append(pin(location / 'final.ppm'))
    save(HERE / 'capture-payloads.json', {'scope': 'Hash-only original PPM files; no image copies.', 'files': capture_rows})
    excluded = []
    for relative in ('baseline-pack.zip', 'candidate-v1/scrantic_data.zip', 'candidate-v2/scrantic_data.zip',
                     'baseline-v1/connecting_walk_probe', 'baseline-v1/connecting_trace'):
        excluded.append(pin(OUT / relative))
    for source in sorted((OUT / 'candidate-v2/masks').glob('*')):
        if source.is_file():
            excluded.append(pin(source))
    save(HERE / 'excluded-payloads.json', {'scope': 'No duplicate archives, binaries or masks; identities only.', 'files': excluded})

    source_pins = dict(build['protected_sha256'])
    for source in sorted(TOOLS.glob('*.py')):
        source_pins[source.relative_to(ROOT).as_posix()] = sha(source)
    for source in dependencies:
        source_pins[source.relative_to(ROOT).as_posix()] = sha(source)
    for relative in ('art/cartoon/skin-tone-v1/correct.py', 'art/cartoon/skin-tone-v1/input-index.json',
                     'art/cartoon/skin-tone-v1/calibration-v1.json', 'art/cartoon/skin-tone-v1/protected-cap-polygons-v1.json',
                     'art/cartoon/skin-tone-v1/protected-landmarks-v2.json', 'art/cartoon/skin-tone-v1/ancestry.json',
                     'art/cartoon/skin-tone-v1/exports-v2/recipe.json',
                     'art/cartoon/walk-pilot/connecting-poses-v1/candidate-selection-v2.json',
                     'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/README.md'):
        source_pins[relative] = sha(ROOT / relative)
    save(HERE / 'source-pins.json', {'source_commit': build['source_commit'], 'files_sha256': source_pins,
                                   'note': 'Source is retained at original repo-relative paths; snapshots only for helper dependencies.'})

    mount = ['docker', 'run', '--rm', '--init', '--network', 'none', '--mount',
             'type=bind,source=D:/.ai-work/worktrees/johnny-cartoon-connecting-poses,target=/source,readonly',
             '--mount', 'type=bind,source=D:/.ai-work/worktrees/johnny-cartoon-connecting-poses/build/skin-tone/native-review,target=/out',
             build['image_id'], 'xvfb-run', '-a', '-s', '-screen 0 1280x960x24', 'python3', '-B']
    entry = '/source/art/cartoon/skin-tone-v1/native-review/'
    save(HERE / 'commands.json', {
        'provenance': 'Actual native launch argv transcribed from execution tool calls; phases and native child commands are separately retained in reports.',
        'host_working_directory': 'D:/.ai-work/worktrees/johnny-cartoon-connecting-poses',
        'host_python': 'TOOLBOX_PYTHON (Python3.11.15, Pillow12.3.0)',
        'host_preparation': ['python -B art/cartoon/skin-tone-v1/native-review/prepare.py --baseline build/connecting-poses/native-motion-v1/candidate-v2/scrantic_data.zip',
                             'python -B art/cartoon/skin-tone-v1/native-review/prepare_candidate.py --export build/skin-tone/export-v2 --candidate-version 1',
                             'python -B art/cartoon/skin-tone-v1/native-review/prepare_candidate.py --export build/skin-tone/export-v2 --candidate-version 2'],
        'native_launches': [
            {'label': 'baseline', 'argv': mount + [entry + 'capture.py'], 'exit_code': 0},
            {'label': 'candidate1-failed-before-native', 'argv': mount + [entry + 'capture_candidate.py', '--candidate-version', '1'], 'exit_code': 1},
            {'label': 'candidate2', 'argv': mount + [entry + 'capture_candidate.py', '--candidate-version', '2'], 'exit_code': 0}],
        'replay': 'Use a fresh isolated checkout/output root and substitute host bind paths only; see REPRODUCE.md.'})

    files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.name not in ('evidence.json', 'readback.json'):
            files.append({'path': path.relative_to(HERE).as_posix(), 'sha256': sha(path), 'size': path.stat().st_size})
    save(HERE / 'evidence.json', {
        'schema_version': 1, 'status': 'PASS', 'scope': 'Native skin-tone evidence preservation only; human color review and production promotion remain separate.',
        'source_commit': build['source_commit'], 'candidate_version': 2,
        'baseline_archive_sha256': candidate['baseline_sha256'], 'candidate_archive_sha256': candidate['archive_sha256'],
        'recipe_sha256': candidate['recipe_sha256'], 'image_id': build['image_id'],
        'native_executable_sha256': candidate['executable_sha256'],
        'coverage': {'clips': 8, 'full_displays_per_package': 298, 'changed_displays': 286,
                     'unchanged_displays': 12, 'poses': 28, 'visibly_changed_poses': 27,
                     'all_smokes_before_full': True, 'fresh_repeats_exact': True},
        'checks': {'smoke': 2, 'regression': 6, 'source_mutations_fired': 4,
                   'handoff_controls_fired': 8, 'native_controls_fired': 4},
        'retained_failure': 'records/native/candidate-v1-launch-failure.json',
        'copy_records': copied, 'files': files,
        'omissions': 'PPM/PNG captures, ZIPs, raw artwork and native binaries are not copied. Hash manifests, original reports, source pins and replay instructions are retained.'})
    print(json.dumps({'status': 'PRESERVED', 'files': len(files), 'byte_exact_copies': len(copied),
                      'bytes': sum(item['size'] for item in files), 'ppm_hashes': len(capture_rows),
                      'evidence_sha256': sha(HERE / 'evidence.json')}))


if __name__ == '__main__':
    main()
