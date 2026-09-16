"""One-time exact motion-evidence writer; never replay into a frozen checkpoint."""
import json
from pathlib import Path
import shutil
import config
import native_core as core


def checkpoint_identity(out, publication):
    candidate = out / publication['candidate_directory']
    review = out / publication['review_directory']
    assert config.sha((review / 'review.html').read_bytes()) == publication['html_sha256'], 'preserve published HTML identity'
    assert config.sha((review / 'review-record.json').read_bytes()) == publication['review_record_sha256'], 'preserve published review-record identity'
    assert config.sha((review / 'browser-validation.json').read_bytes()) == publication['browser_validation_sha256'], 'preserve browser validation identity'
    assert config.sha((candidate / 'preparation.json').read_bytes()) == publication['candidate_preparation_sha256'], 'preserve candidate preparation identity'
    selected = config.load_json(candidate / 'preparation.json')
    assert config.sha((candidate / 'candidate-selection.json').read_bytes()) == selected['selection_sha256'] == publication['candidate_selection_sha256'], 'preserve captured selection identity'
    record = config.load_json(review / 'review-record.json')
    assert record['html_sha256'] == publication['html_sha256'], 'preserve checked HTML binding'
    for clip, reports in record['reports_sha256'].items():
        assert clip in config.CLIPS, 'preserve configured report clip'
        for kind, digest in reports.items():
            base = out / 'baseline-v1' if kind == 'baseline' else candidate
            assert kind in ('baseline', 'candidate'), 'preserve known report panel'
            assert config.sha((base / clip / 'full/report.json').read_bytes()) == digest, 'preserve captured full report:' + kind + ':' + clip
    return selected


def main():
    out, here = config.OUT, config.HERE
    destination, binder = here / 'evidence/motion-v1', here / 'evidence.json'
    assert not destination.exists() and not binder.exists(), 'preserve previous motion checkpoint'
    publication = config.load_json(out / 'publication.json')
    assert publication['status'] == 'PASS', 'published checked motion review'
    selected = checkpoint_identity(out, publication)
    candidate_name = publication['candidate_directory']
    candidate = out / candidate_name
    review_name = publication['review_directory']
    review = out / review_name
    production = config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes())
    assert production == config.PRODUCTION_SHA, 'production remains exact baseline'
    build = config.load_json(out / 'baseline-v1/build.json')
    assert core.protected() == build['protected_sha256'], 'all protected source/archive inputs unchanged'
    for path in (candidate / 'summary.json', review / 'browser-validation.json', review / 'publication-browser.json'):
        assert config.load_json(path)['status'] == 'PASS', 'completed checkpoint:' + path.name
    assert config.sha((candidate / 'scrantic_data.zip').read_bytes()) == selected['archive_sha256'] == publication['candidate_archive_sha256'], 'exact reviewed private ZIP'
    assert selected['selection_sha256'] == publication['candidate_selection_sha256'], 'published selection identity'
    names = [f'{candidate_name}/preparation.json', f'{candidate_name}/candidate-selection.json', f'{candidate_name}/summary.json',
             f'{review_name}/review.html', f'{review_name}/review-record.json', f'{review_name}/browser-validation.json',
             f'{review_name}/publication-browser.json', 'publication.json']
    names += [f'{candidate_name}/{clip}/{phase}/{name}' for clip in config.CLIPS for phase in ('smoke', 'full', 'repeat') for name in ('capture.log', 'report.json')]
    files = {}

    def copy(source, relative):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
        assert path.read_bytes() == source.read_bytes(), 'exact motion evidence:' + relative
        files[path.relative_to(here).as_posix()] = config.sha(path.read_bytes())

    for name in names:
        copy(out / name, name)
    for stage in ('build', 'validation', 'negatives', 'publication'):
        for source in sorted((out / 'browser-execution' / stage).glob('*')):
            if source.is_file():
                copy(source, source.relative_to(out).as_posix())
    runner = config.ROOT / 'build/connecting-analysis/run_browser_stage.py'
    if runner.is_file():
        copy(runner, 'helpers/host-run_browser_stage.py')
    # Capture all small guard inputs and outputs, including executed helper
    # removals. Bulk images, private archives and executables stay local.
    for source in sorted((out / 'negative-controls').rglob('*')):
        if source.is_file() and source.suffix in ('.json', '.txt', '.log', '.py', '.c', '.html', '.md'):
            copy(source, source.relative_to(out).as_posix())
    for name, digest in publication['guard_records_sha256'].items():
        path = config.ROOT / name
        assert config.sha(path.read_bytes()) == digest, 'published guard still exact:' + name
        copied = destination / path.relative_to(out)
        assert copied.is_file() and config.sha(copied.read_bytes()) == digest, 'published guard preserved:' + name
    for original in sorted(here.glob('*')):
        if original.suffix in ('.py', '.html', '.md'):
            copy(original, 'helpers/' + original.name)
    baseline_path = here / 'baseline-checkpoint.json'
    baseline = config.load_json(baseline_path)
    files[baseline_path.relative_to(here).as_posix()] = config.sha(baseline_path.read_bytes())
    baseline_root = config.ROOT / baseline['evidence_root']
    for name, digest in baseline['files_sha256'].items():
        path = baseline_root / name
        assert config.sha(path.read_bytes()) == digest, 'frozen baseline evidence unchanged:' + name
        files[path.relative_to(here).as_posix()] = digest
    record = {'schema_version': 1, 'status': 'technical native motion checkpoint complete; human transition approval pending',
              'source_commit': build['source_commit'], 'baseline_archive_sha256': production, 'candidate_archive_sha256': selected['archive_sha256'],
              'candidate_directory': candidate_name, 'candidate_selection_sha256': selected['selection_sha256'], 'added_members': selected['added_members'],
              'url': publication['url'], 'html_sha256': publication['html_sha256'], 'files_sha256': files,
              'native_clips': config.load_json(candidate / 'summary.json')['clips'], 'guard_records_sha256': publication['guard_records_sha256'],
              'scope': 'Six native clips, smoke/full/fresh-repeat, scoped pixel equality, local and served browser checks, executed negative controls. Current40-asset Cartoon baseline with HD fallbacks; only009/010/012 added. No production changes or human approval inferred.',
              'omitted': 'Capture PNGs/PPMs, private ZIPs, native executables and screenshots remain local. Bound reports retain image/screenshot hashes; recreate in new scratch using pinned baseline and helpers. This evidence writer refuses frozen destinations.',
              'preserver_sha256': config.sha(Path(__file__).read_bytes())}
    binder.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    assert all(config.sha((here / name).read_bytes()) == digest for name, digest in files.items()), 'final immutable checkpoint readback'
    print(f'PASS preserved {len(files)} bound files; evidence SHA256={config.sha(binder.read_bytes())}')


if __name__ == '__main__':
    main()
