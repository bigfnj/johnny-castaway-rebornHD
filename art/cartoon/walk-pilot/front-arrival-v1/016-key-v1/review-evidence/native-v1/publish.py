"""Publish only the tested two-direction HTML/native images into a fresh slug."""
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
REVIEW = OUT / 'review-v1'
DEST = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review/front-turn016-v1')
URL = 'http://127.0.0.1:8932/front-turn016-v1/review.html'
HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw, digest, name):
    assert sha(raw) == digest, 'served identity:' + name


def main():
    assert not DEST.exists(), 'preserve existing published slug'
    record = json.loads((REVIEW / 'review-record.json').read_bytes())
    checked = json.loads((REVIEW / 'browser-validation.json').read_bytes())
    assert checked['status'] == 'PASS' and checked['smoke_passed'] == 1 and len(checked['regressions_after_smoke']) == 2
    assert checked['html_sha256'] == record['html_sha256'] and checked['checker_sha256'] == sha((OUT / 'check_review.py').read_bytes())
    files = {'review.html': record['html_sha256'], **record['image_files']}
    for name, digest in files.items():
        identity((REVIEW / name).read_bytes(), digest, name)
    DEST.mkdir()
    for name in files:
        destination = DEST / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((REVIEW / name).read_bytes())
    for name, digest in files.items():
        with urlopen(URL.removesuffix('review.html') + name, timeout=30) as response:
            assert response.status == 200
            identity(response.read(), digest, name)
    print(f'SMOKE PASS {len(files)} served HTML/native image identities', flush=True)
    try:
        identity((REVIEW / 'review.html').read_bytes() + b' ', files['review.html'], 'review.html')
    except AssertionError as error:
        assert str(error) == 'served identity:review.html'
    else:
        raise AssertionError('changed served HTML negative control survived')
    raw = (REVIEW / 'review.html').read_bytes()
    data = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
        response = page.goto(URL)
        identity(response.body(), files['review.html'], 'browser review.html')
        page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
        assert page.locator('#speed').input_value() == '1' and page.locator('#view option[value="walk"]').inner_text() == 'Pose close-up'
        for name, clip in data['clips'].items():
            page.locator('#direction').select_option(name)
            page.locator('#turning').click()
            state = page.evaluate('nativeReviewState')
            assert state['clip'] == name and state['frame'] == 16 and state['position'] == 120 and not state['playing']
            row = clip['frames'][state['index']]
            for kind in ('baseline', 'candidate'):
                with Image.open(REVIEW / row[kind]) as image:
                    expected = sha(image.convert('RGBA').crop((560, 400, 960, 680)).tobytes())
                assert page.evaluate(HASH, kind) == expected, 'published exact016 crop:' + name + ':' + kind
                assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}')
            page.screenshot(path=str(OUT / ('published-' + name + '-turning016-1280.png')), full_page=True)
            page.locator('#prev').click()
            assert page.evaluate('nativeReviewState.frame') == 17 and page.evaluate('nativeReviewState.segment') == 'prime'
            page.locator('#next').click()
            assert page.evaluate('nativeReviewState.frame') == 16
            page.locator('#next').click()
            assert page.evaluate('nativeReviewState.frame') == 17 and page.evaluate('nativeReviewState.segment') == 'turn'
            page.locator('#replay').click()
            page.locator('#repeat').uncheck()
            page.evaluate('reviewCallback(0);reviewCallback(120)')
            assert page.evaluate('nativeReviewState.frame') == 16
            page.evaluate('t=>reviewCallback(t)', clip['duration_ms'])
            assert not page.evaluate('nativeReviewState.playing') and page.evaluate('nativeReviewState.frame') == 17
            checks.append(name + ': exact016 native crops, initial/turn/settled stepping, Normal native boundary and endpoint,1280 layout')
        assert not errors
        browser.close()
    report = {'status': 'PASS', 'url': URL, 'html_sha256': files['review.html'], 'served_file_count': len(files),
              'smoke_passed': True, 'regressions_after_smoke': checks, 'browser_errors': errors,
              'negative_control': 'changed HTML causes one named served identity failure',
              'publisher_sha256': sha(Path(__file__).read_bytes()),
              'scope': 'Proposed016 and approved017 native turn comparison. No016 human approval or production change.'}
    (OUT / 'publication.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
