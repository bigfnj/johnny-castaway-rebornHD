"""Publish an immutable checked profile page, then check the served copy."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen
import check_review
import config

SERVER_ROOT = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review')
SLUG = 'profile-walk-motion-v1'
URL = f'http://127.0.0.1:8932/{SLUG}/review.html'


def identity(raw, expected, name):
    assert config.sha(raw) == expected, 'served identity:' + name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    review = config.OUT / 'review-v1'
    target = SERVER_ROOT / SLUG
    report_path = config.OUT / 'publication.json'
    assert not report_path.exists(), 'preserve publication evidence'
    record = config.load_json(review / 'review-record.json')
    checked = config.load_json(review / 'browser-validation.json')
    assert checked['status'] == 'PASS' and checked['smoke_passed'] == 1 and len(checked['regressions_after_smoke']) == 4, 'complete local browser checks'
    assert checked['checker_sha256'] == config.sha(Path(check_review.__file__).read_bytes()), 'same browser checker'
    assert checked['html_sha256'] == record['html_sha256'], 'same checked HTML'
    for name in ('selection', 'native', 'browser'):
        assert config.load_json(config.OUT / 'negative-controls' / (name + '.json'))['status'] == 'PASS', 'executed negative controls:' + name
    files = {'review.html': record['html_sha256'], **record['image_files']}
    for name, digest in files.items():
        identity((review / name).read_bytes(), digest, name)
    if not args.verify_only:
        assert not target.exists(), 'preserve existing published profile slug'
        target.mkdir()
        for name in files:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((review / name).read_bytes())
    for name, digest in files.items():
        with urlopen(URL.removesuffix('review.html') + name, timeout=30) as response:
            assert response.status == 200, 'successful served response:' + name
            identity(response.read(), digest, name)
    print(f'SMOKE PASS {len(files)} exact served HTML/native image identities', flush=True)
    try:
        identity((review / 'review.html').read_bytes() + b' ', files['review.html'], 'review.html')
    except AssertionError as error:
        assert str(error) == 'served identity:review.html', 'specific served-identity negative'
    else:
        raise AssertionError('changed served HTML identity mutation SURVIVED')
    checked_served = check_review.check(review, 'publication-browser.json', URL)
    result = {'status': 'PASS', 'url': URL, 'html_sha256': files['review.html'], 'served_file_count': len(files),
              'served_smoke_passed': True, 'browser_smoke_then_regression': checked_served,
              'negative_control': 'Appended HTML byte causes exactly one named served identity failure.',
              'publisher_sha256': config.sha(Path(__file__).read_bytes()),
              'scope': 'Published complete native profile comparison; user approval of whole gait remains separate. Production unchanged.'}
    report_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS published ' + URL, flush=True)


if __name__ == '__main__':
    main()
