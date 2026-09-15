"""Copy only this versioned review into the existing local review server root."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'island-review-v1'
DESTINATION = HERE.parents[2] / 'johnny-art-metadata/build/art-review/arrival-cartoon-v1'
URL = 'http://127.0.0.1:8932/arrival-cartoon-v1/review.html'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    assert not DESTINATION.exists(), 'preserve-existing-served-version'
    evidence = json.loads((SOURCE / 'review-record.json').read_bytes())
    checks = json.loads((SOURCE / 'browser-validation.json').read_bytes())
    html = (SOURCE / 'review.html').read_bytes()
    assert sha(html) == evidence['html_sha256'] == checks['html_sha256']
    assert checks['smoke_passed'] == 2 and len(checks['regressions']) == 4
    DESTINATION.mkdir()
    shutil.copyfile(SOURCE / 'review.html', DESTINATION / 'review.html')
    shutil.copytree(SOURCE / 'images', DESTINATION / 'images')
    with urllib.request.urlopen(URL, timeout=10) as response:
        assert response.read() == html, 'actual-served-html-bytes'
    for path, digest in evidence['image_files'].items():
        with urllib.request.urlopen(URL.rsplit('/', 1)[0] + '/' + path, timeout=10) as response:
            assert sha(response.read()) == digest, 'actual-served-image:' + path
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1600, 'height': 1100})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(URL)
        page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
        assert page.title() == "Johnny's new arrival pose"
        assert page.locator('#speed').input_value() == '1' and page.locator('#view').input_value() == 'island'
        page.evaluate('select(0);play(false)')
        for _ in range(23):
            page.locator('#next').click()
        assert page.evaluate('nativeReviewState.frame') == 18
        assert page.locator('#status').inner_text() == 'Arrival pose'
        page.screenshot(path=str(SOURCE / 'served-arrival.png'), full_page=True)
        page.locator('#prev').click()
        assert page.evaluate('nativeReviewState.frame') == 22
        assert not errors
        browser.close()
    report = {'status': 'PASS', 'url': URL, 'html_sha256': sha(html), 'all_served_image_hashes_match': len(evidence['image_files']),
              'actual_served_page': 'Ready; Normal/Full island defaults; all 23 pose-step transitions reach arrival018; Previous returns022; no browser errors.',
              'source_sha256': sha(Path(__file__).read_bytes()), 'human_acceptance': 'Not evaluated by this technical check.'}
    (SOURCE / 'served-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
