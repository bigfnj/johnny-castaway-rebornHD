"""Freeze small motion evidence; keep local native images and binaries out of Git."""
import json
from pathlib import Path
import shutil
import config
import native_core as core


def main():
    out, here = config.OUT, config.HERE
    destination = here / 'evidence/motion-v1'
    binder = here / 'evidence.json'
    assert not destination.exists() and not binder.exists(), 'preserve previous motion checkpoint'
    production = config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes())
    assert production == config.PRODUCTION_SHA, 'production remains exact baseline'
    build = config.load_json(out / 'baseline-v1/build.json')
    assert core.protected() == build['protected_sha256'], 'all protected source/archive inputs remain unchanged'
    for path in ('candidate-v1/summary.json', 'review-v1/browser-validation.json', 'publication.json', 'negative-controls/selection.json', 'negative-controls/native.json', 'negative-controls/browser.json'):
        assert config.load_json(out / path)['status'] == 'PASS', 'completed checkpoint:' + path
    publication = config.load_json(out / 'publication.json')
    selected = config.load_json(out / 'candidate-v1/preparation.json')
    assert config.sha((out / 'candidate-v1/scrantic_data.zip').read_bytes()) == selected['archive_sha256'], 'reviewed private candidate ZIP still exact'
    names = ['candidate-v1/preparation.json', 'candidate-v1/candidate-selection.json', 'candidate-v1/summary.json', 'review-v1/review.html', 'review-v1/review-record.json',
             'review-v1/browser-validation.json', 'review-v1/publication-browser.json', 'publication.json', 'negative-controls/selection.json', 'negative-controls/native.json', 'negative-controls/browser.json',
             'negative-controls/wrong-selected-path/capture.log', 'negative-controls/wrong-pose-selector/review.html', 'negative-controls/wrong-pose-selector/browser-failure.json',
             'negative-controls/wrong-pose-selector/checker.stdout.txt', 'negative-controls/wrong-pose-selector/checker.stderr.txt']
    names += [f'candidate-v1/{clip}/{phase}/{name}' for clip in config.CLIPS for phase in ('smoke', 'full', 'repeat') for name in ('capture.log', 'report.json')]
    files = {}
    for name in names:
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out / name, path)
        assert path.read_bytes() == (out / name).read_bytes(), 'exact preserved motion evidence:' + name
        files[path.relative_to(here).as_posix()] = config.sha(path.read_bytes())
    for original in sorted(here.glob('*')):
        if original.suffix not in ('.py', '.html', '.md'):
            continue
        path = destination / 'helpers' / original.name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)
        files[path.relative_to(here).as_posix()] = config.sha(path.read_bytes())
    baseline_path = here / 'baseline-checkpoint.json'
    baseline = config.load_json(baseline_path)
    files[baseline_path.relative_to(here).as_posix()] = config.sha(baseline_path.read_bytes())
    baseline_root = config.ROOT / baseline['evidence_root']
    for name, digest in baseline['files_sha256'].items():
        path = baseline_root / name
        assert config.sha(path.read_bytes()) == digest, 'frozen baseline evidence unchanged:' + name
        files[path.relative_to(here).as_posix()] = digest
    record = {'schema_version': 1, 'status': 'technical native motion checkpoint complete; human gait approval pending',
              'source_commit': build['source_commit'], 'baseline_archive_sha256': production, 'candidate_archive_sha256': selected['archive_sha256'],
              'candidate_selection_sha256': selected['selection_sha256'], 'added_members': selected['added_members'],
              'url': publication['url'], 'html_sha256': publication['html_sha256'], 'files_sha256': files,
              'native_clips': config.load_json(out / 'candidate-v1/summary.json')['clips'],
              'guard_results': {name: config.load_json(out / 'negative-controls' / (name + '.json')) for name in ('selection', 'native', 'browser')},
              'scope': 'All four native clips, smoke/full/fresh-repeat, scoped pixel equality, local+served browser regressions, executed meaningful negative controls. No production writes or human approval inferred.',
              'omitted': 'Capture PNGs/PPMs, private ZIPs, native executables and screenshots remain local. Native image and screenshot hashes are retained in bound reports; recreate via the frozen helpers and pinned baseline.',
              'preserver_sha256': config.sha(Path(__file__).read_bytes())}
    binder.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert all(config.sha((here / name).read_bytes()) == digest for name, digest in files.items()), 'final immutable checkpoint readback'
    print(f'PASS preserved {len(files)} bound files; evidence SHA256={config.sha(binder.read_bytes())}')


if __name__ == '__main__':
    main()
