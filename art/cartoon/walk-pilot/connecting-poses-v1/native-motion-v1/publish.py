"""Publish a new checked connecting page and verify its served bytes and controls."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
import check_review
import config

SLUG = 'connecting-turns-motion-v1'


def identity(raw, expected, name):
    assert config.sha(raw) == expected, 'served identity:' + name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root', type=Path, required=True)
    parser.add_argument('--base-url', default='http://127.0.0.1:8932')
    parser.add_argument('--review', type=Path, default=config.OUT / 'review-v1')
    parser.add_argument('--guard', type=Path, action='append', required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    review = args.review.resolve()
    target = args.server_root / SLUG
    url = args.base_url.rstrip('/') + '/' + SLUG + '/review.html'
    report_path = config.OUT / 'publication.json'
    assert not report_path.exists(), 'preserve publication evidence'
    record = config.load_json(review / 'review-record.json')
    checked = config.load_json(review / 'browser-validation.json')
    assert checked['status'] == 'PASS' and checked['smoke_passed'] == 1 and len(checked['regressions_after_smoke']) == len(config.CLIPS), 'complete local browser checks'
    assert checked['checker_sha256'] == config.sha(Path(check_review.__file__).read_bytes()), 'same browser checker'
    assert checked['html_sha256'] == record['html_sha256'], 'same checked HTML'
    review_name = review.relative_to(config.OUT.resolve()).as_posix()
    assert '/' not in review_name and review_name.startswith('review-'), 'explicit local review directory'
    browser_control_path = config.OUT / 'negative-controls' / ('browser.json' if review_name == 'review-v1' else 'browser-' + review_name + '.json')
    browser_control = config.load_json(browser_control_path)
    assert browser_control['status'] == 'PASS' and [r['name'] for r in browser_control['controls']] == ['wrong-pose-selector', 'changed-served-html'], 'two executed browser controls'
    assert browser_control['original_html_sha256'] == record['html_sha256'], 'controls bind this review'
    guards, bound_candidate_checks = {}, set()
    for path in [browser_control_path, *args.guard]:
        path = path.resolve()
        guard = config.load_json(path)
        assert guard['status'] == 'PASS', 'executed guard passed:' + path.name
        if path.name.startswith('selection'):
            assert guard['selection_sha256'] == record['candidate_selection_sha256'], 'selection guard binds displayed candidate'
            bound_candidate_checks.add('selection')
        if path.name.startswith('native'):
            assert guard['selection_sha256'] == record['candidate_selection_sha256'] and guard['candidate_archive_sha256'] == record['candidate_archive_sha256'], 'native guard binds displayed candidate'
            bound_candidate_checks.add('native')
        guards[path.relative_to(config.ROOT).as_posix()] = config.sha(path.read_bytes())
    assert bound_candidate_checks == {'selection', 'native'}, 'selection and native candidate controls required'
    candidate = config.OUT / record['candidate_directory']
    preparation = config.load_json(candidate / 'preparation.json')
    assert preparation['archive_sha256'] == record['candidate_archive_sha256'] and preparation['selection_sha256'] == record['candidate_selection_sha256'], 'same captured candidate'
    assert config.sha((candidate / 'scrantic_data.zip').read_bytes()) == record['candidate_archive_sha256'], 'candidate unchanged'
    assert config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes()) == record['baseline_archive_sha256'], 'production remains baseline'
    files = {'review.html': record['html_sha256'], **record['image_files']}
    for name, digest in files.items():
        identity((review / name).read_bytes(), digest, name)
    if not args.verify_only:
        assert not target.exists(), 'preserve existing published connecting slug'
        target.mkdir()
        for name in files:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((review / name).read_bytes())
    for name, digest in files.items():
        with urlopen(url.removesuffix('review.html') + name, timeout=30) as response:
            assert response.status == 200, 'successful served response:' + name
            identity(response.read(), digest, name)
    print(f'SMOKE PASS {len(files)} exact served HTML/native image identities', flush=True)
    checked_served = check_review.check(review, 'publication-browser.json', url)
    result = {'status': 'PASS', 'url': url, 'html_sha256': files['review.html'], 'served_file_count': len(files),
              'review_record_sha256': config.sha((review / 'review-record.json').read_bytes()),
              'browser_validation_sha256': config.sha((review / 'browser-validation.json').read_bytes()),
              'candidate_preparation_sha256': config.sha((candidate / 'preparation.json').read_bytes()),
              'review_directory': review.relative_to(config.OUT).as_posix(), 'candidate_directory': record['candidate_directory'],
              'candidate_archive_sha256': record['candidate_archive_sha256'], 'candidate_selection_sha256': record['candidate_selection_sha256'],
              'served_smoke_passed': True, 'browser_smoke_then_regression': checked_served, 'guard_records_sha256': guards,
              'publisher_sha256': config.sha(Path(__file__).read_bytes()),
              'scope': 'Published six complete native connecting comparisons; human transition approval remains separate. Production unchanged.'}
    report_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS published ' + url, flush=True)


if __name__ == '__main__':
    main()
