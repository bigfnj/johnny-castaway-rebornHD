"""Publish one new checked color-review slug, then verify served bytes and controls."""
import argparse
import json
from pathlib import Path
import sys
from urllib.request import urlopen

import check_native

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'native-review'))
import config

SLUG = 'cartoon-skin-tone-v1'


def identity(raw, expected, label):
    assert config.sha(raw) == expected, 'identity:' + label


def checkpoint_identity(review):
    record = config.load_json(review / 'review-record.json')
    checked = config.load_json(review / 'browser-validation.json')
    assert checked['status'] == 'PASS' and checked['smoke_passed'] == 1 and len(checked['regressions_after_smoke']) == 8, 'complete local color browser checks'
    identity(Path(check_native.__file__).read_bytes(), checked['checker_sha256'], 'current browser checker')
    assert checked['html_sha256'] == record['files_sha256']['review.html'], 'same checked color HTML'
    candidate = config.OUT / record['candidate_directory']
    identity((candidate / 'preparation.json').read_bytes(), record['candidate_preparation_sha256'], 'captured preparation')
    prep = config.load_json(candidate / 'preparation.json')
    assert prep['archive_sha256'] == record['candidate_archive_sha256'] and prep['recipe_sha256'] == record['recipe_sha256'], 'same captured correction'
    identity((candidate / 'scrantic_data.zip').read_bytes(), record['candidate_archive_sha256'], 'captured private archive')
    identity((candidate / 'correction-recipe.json').read_bytes(), record['recipe_sha256'], 'captured correction recipe')
    identity((config.ROOT / 'assets/scrantic_data.zip').read_bytes(), config.PRODUCTION_SHA, 'unchanged production archive')
    for name, digest in record['files_sha256'].items():
        identity((review / name).read_bytes(), digest, 'review file:' + name)
    for clip, values in record['reports_sha256'].items():
        for kind, digest in values.items():
            root = config.OUT / 'baseline-v1' if kind == 'baseline' else candidate
            identity((root / clip / 'full/report.json').read_bytes(), digest, 'captured report:' + kind + ':' + clip)
    return record, checked, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--server-root', type=Path, required=True)
    parser.add_argument('--base-url', default='http://127.0.0.1:8932')
    parser.add_argument('--browser-guard', type=Path, required=True)
    parser.add_argument('--native-guard', type=Path, required=True)
    parser.add_argument('--input-guard', type=Path, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    review = args.review.resolve()
    publication = review / 'publication.json'
    assert not publication.exists(), 'preserve color publication record'
    record, checked, candidate = checkpoint_identity(review)
    browser = config.load_json(args.browser_guard)
    assert browser['status'] == 'PASS' and browser['original_html_sha256'] == checked['html_sha256'], 'browser controls bind reviewed HTML'
    assert [r['name'] for r in browser['controls']] == ['wrong-pose-selector', 'retained-previous-clip-cache', 'changed-served-html'], 'three executed browser controls'
    assert browser['executed_checker_sha256'] == checked['checker_sha256'], 'same controlled browser checker'
    native = config.load_json(args.native_guard)
    assert native['status'] == 'PASS' and native['candidate_archive_sha256'] == record['candidate_archive_sha256'] and native['recipe_sha256'] == record['recipe_sha256'], 'native controls bind displayed correction'
    assert native['candidate_version'] == int(record['candidate_directory'].removeprefix('candidate-v')), 'native controls candidate version'
    assert native['inputs']['candidate_report_sha256'] == record['reports_sha256']['front_arc']['candidate'] and native['inputs']['baseline_report_sha256'] == record['reports_sha256']['front_arc']['baseline'], 'native controls bind captured reports'
    assert [(row['case'], row['status']) for row in native['controls']] == [(name, 'FIRED') for name in ('changed-display-timestamp', 'outside-skin', 'outside-canvas', 'unchanged029')], 'four executed native controls'
    inputs = config.load_json(args.input_guard)
    assert inputs['status'] == 'PASS' and inputs['recipe_sha256'] == record['recipe_sha256'] and inputs['candidate_archive_sha256'] == record['candidate_archive_sha256'], 'input controls bind displayed correction'
    assert len(inputs['controls']) == 8 and all(row['status'] == 'FIRED' for row in inputs['controls']), 'eight executed input controls'
    assert inputs['decoded_masks_equal_png'] == 28, 'all28 native mask decodings verified'
    identity((config.HERE / 'prepare_candidate.py').read_bytes(), inputs['executed_helper_sha256'], 'input-controlled helper')
    identity((config.HERE / 'capture_candidate.py').read_bytes(), inputs['capture_helper_sha256'], 'input-controlled capture helper')
    identity((config.HERE / 'check_native.py').read_bytes(), native['checker_sha256'], 'native-controlled checker')
    identity((config.HERE / 'skin_compare.py').read_bytes(), native['comparison_helper_sha256'], 'native-controlled comparison')
    target = args.server_root / SLUG
    url = args.base_url.rstrip('/') + '/' + SLUG + '/review.html'
    files = record['files_sha256']
    if not args.verify_only:
        assert not target.exists(), 'preserve existing published color slug'
        target.mkdir()
        for name in files:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((review / name).read_bytes())
    for name, digest in files.items():
        with urlopen(url.removesuffix('review.html') + name, timeout=30) as response:
            assert response.status == 200, 'successful served response:' + name
            identity(response.read(), digest, 'served file:' + name)
    print(f'SMOKE PASS {len(files)} exact served color-review files', flush=True)
    served = check_native.check(review, 'publication-browser.json', url)
    # Recheck capture, HTML and recipe bindings after actual server/browser use.
    checkpoint_identity(review)
    guards = {p.resolve().relative_to(config.ROOT).as_posix(): config.sha(p.read_bytes()) for p in [args.browser_guard, args.native_guard, args.input_guard]}
    result = {'status': 'PASS', 'url': url, 'served_files': len(files), 'html_sha256': checked['html_sha256'],
              'review_record_sha256': config.sha((review / 'review-record.json').read_bytes()),
              'browser_validation_sha256': config.sha((review / 'browser-validation.json').read_bytes()),
              'candidate_preparation_sha256': config.sha((candidate / 'preparation.json').read_bytes()),
              'candidate_archive_sha256': record['candidate_archive_sha256'], 'recipe_sha256': record['recipe_sha256'],
              'review_directory': review.relative_to(config.OUT).as_posix(), 'candidate_directory': record['candidate_directory'],
              'guard_records_sha256': guards, 'browser_smoke_then_regression': served,
              'publisher_sha256': config.sha(Path(__file__).read_bytes()),
              'scope': 'Published eight native earlier/matched-color comparisons and28-pose still review; human color approval remains separate. Production unchanged.'}
    publication.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS published ' + url, flush=True)


if __name__ == '__main__':
    main()
