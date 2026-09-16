"""Publish this verified018 preview once, then check its served bytes and controls."""
import argparse
import copy
import json
from pathlib import Path
import urllib.request
from playwright.sync_api import sync_playwright
import build_review as build
import check_review as check

SERVER = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review')
SLUG = 'standing018-motion-v1'
URL = 'http://127.0.0.1:8932/' + SLUG + '/review.html'


def binding(record, browser, negatives, record_hash):
    assert browser['status'] == 'PASS' and browser['html_sha256'] == record['files_sha256']['review.html'], 'publication tested HTML binding'
    assert browser['checker_sha256'] == build.sha(Path(check.__file__).read_bytes()), 'publication tested checker binding'
    assert negatives['status'] == 'PASS' and negatives['executed_negative_count'] == 7 and negatives['review_record_sha256'] == record_hash, 'publication negative review binding'
    assert negatives['builder_sha256'] == record['builder_sha256'] and negatives['checker_sha256'] == browser['checker_sha256'], 'publication tested helper bindings'


def publish(review, negatives_path):
    target = SERVER / SLUG
    assert not target.exists(), 'preserve previous published018 motion review'
    record_path = review / 'review-record.json'
    record, browser, negatives = build.load(record_path), build.load(review / 'browser-validation.json'), build.load(negatives_path)
    digest = build.sha(record_path.read_bytes())
    binding(record, browser, negatives, digest)
    controls = []
    for name, expected in [('stale-html', 'publication tested HTML binding'), ('stale-checker', 'publication tested checker binding'), ('stale-review', 'publication negative review binding')]:
        b, n = copy.deepcopy(browser), copy.deepcopy(negatives)
        if name == 'stale-html': b['html_sha256'] = '0' * 64
        elif name == 'stale-checker': b['checker_sha256'] = '0' * 64
        else: n['review_record_sha256'] = '0' * 64
        try: binding(record, b, n, digest)
        except AssertionError as error:
            assert str(error) == expected, 'specific publication control:' + name
            controls.append({'case': name, 'failure': str(error)})
        else: raise AssertionError('publication mutation survived:' + name)
    binding(record, browser, negatives, digest)
    files = {}
    for name, expected in record['files_sha256'].items():
        raw = (review / name).read_bytes()
        assert build.sha(raw) == expected, 'published input identity:' + name
        files[name] = raw
    files['review-record.json'] = record_path.read_bytes()
    target.mkdir()
    for name, raw in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    for name, raw in files.items():
        with urllib.request.urlopen(URL.rsplit('/', 1)[0] + '/' + name) as response:
            assert response.status == 200 and response.read() == raw, 'served published file identity:' + name
    check.check(review, record_name='publication-browser.json', base_url=URL)
    shots = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.add_init_script('window.requestAnimationFrame=fn=>0')
            page.goto(URL)
            for clip in build.CLIPS:
                page.locator('#direction').select_option(clip)
                page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready', timeout=90000)
                # Last018 selects mirrored arrival rather than that clip's
                # unmirrored priming occurrence. No camera or pixels change.
                ordinal = page.evaluate('data.frames.filter(r=>r.frame===18).at(-1).pose_index')
                page.locator('#reference').select_option(str(ordinal))
                name = 'published-' + clip + '-last018-1280.png'
                page.screenshot(path=str(review / name), full_page=True)
                shots[name] = build.sha((review / name).read_bytes())
        finally: browser.close()
    result = {'status': 'PASS', 'url': URL, 'slug': SLUG, 'html_sha256': record['files_sha256']['review.html'],
              'review_record_sha256': digest, 'served_files_checked': len(files),
              'publication_binding_controls': controls, 'positive_before_and_restored_after': True,
              'publisher_sha256': build.sha(Path(__file__).read_bytes()), 'negative_result_sha256': build.sha(negatives_path.read_bytes()),
              'served_browser_sha256': build.sha((review / 'publication-browser.json').read_bytes()),
              'screenshots_sha256': shots, 'scope': 'Verified local review published unchanged; human motion approval pending.'}
    (review / 'publication.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS published ' + URL, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--negatives', type=Path, required=True)
    a = p.parse_args()
    publish(a.review, a.negatives)

