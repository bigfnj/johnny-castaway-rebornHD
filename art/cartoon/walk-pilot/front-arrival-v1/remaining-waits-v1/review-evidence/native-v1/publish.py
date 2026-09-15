"""Publish the checked ring page after root visual clearance, with fresh served checks."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright
import config

OUT = Path(__file__).resolve().parent
REVIEW = OUT / 'review-v1'
DEST = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review/standing-ring-v1')
URL = 'http://127.0.0.1:8932/standing-ring-v1/review.html'
HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw, digest, name):
    assert sha(raw) == digest, 'served identity:' + name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    record = json.loads((REVIEW / 'review-record.json').read_bytes())
    checked = json.loads((REVIEW / 'browser-validation.json').read_bytes())
    assert checked['status'] == 'PASS' and checked['smoke_passed'] == 1 and len(checked['regressions_after_smoke']) == 2
    assert checked['html_sha256'] == record['html_sha256'] and checked['checker_sha256'] == sha((OUT / 'check_review.py').read_bytes())
    files = {'review.html': record['html_sha256'], **record['image_files']}
    for name, digest in files.items():
        identity((REVIEW / name).read_bytes(), digest, name)
    if not args.verify_only:
        assert not DEST.exists(), 'preserve existing published slug'
        DEST.mkdir()
        for name in files:
            target = DEST / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REVIEW / name).read_bytes())
    for name, digest in files.items():
        with urlopen(URL.removesuffix('review.html') + name, timeout=30) as response:
            assert response.status == 200
            identity(response.read(), digest, name)
    print(f'SMOKE PASS {len(files)} served HTML/native image identities', flush=True)
    raw = (REVIEW / 'review.html').read_bytes()
    try:
        identity(raw + b' ', files['review.html'], 'review.html')
    except AssertionError as error:
        assert str(error) == 'served identity:review.html'
    else:
        raise AssertionError('changed served HTML negative control survived')
    bundle = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    checks, screenshots = [], {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors, requests = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('requestfailed', lambda request: requests.append(request.failure))
        page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
        response = page.goto(URL)
        identity(response.body(), files['review.html'], 'browser review.html')
        page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=60000)
        assert not page.evaluate('window.nativeReviewError||null')
        assert page.locator('#direction').input_value() == config.DEFAULT_CLIP and page.locator('#speed').input_value() == '1'
        for name, clip in bundle['clips'].items():
            page.locator('#direction').select_option(name)
            for heading in range(8):
                page.locator('#heading').select_option(str(heading))
                state = page.evaluate('nativeReviewState')
                assert state['clip'] == name and state['heading'] == heading and not state['playing']
                row = clip['frames'][state['index']]
                for kind in ('baseline', 'candidate'):
                    with Image.open(REVIEW / row[kind]) as image:
                        digest = sha(image.convert('RGBA').crop((560, 400, 960, 680)).tobytes())
                    assert page.evaluate(HASH, kind) == digest, 'published exact heading crop:' + name + ':' + str(heading)
                    assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}')
                if name == config.DEFAULT_CLIP and heading in (2, 4, 6):
                    path = OUT / f'published-heading{heading}-frame{row["frame"]:03}-1280.png'
                    page.screenshot(path=str(path), full_page=True)
                    screenshots[path.name] = sha(path.read_bytes())
            page.locator('#side').click()
            assert page.evaluate('nativeReviewState.heading') == 6 and page.evaluate('nativeReviewState.frame') == 0
            page.locator('#back').click()
            assert page.evaluate('nativeReviewState.heading') == 4 and page.evaluate('nativeReviewState.frame') == 15
            page.locator('#repeat').uncheck()
            page.locator('#replay').click()
            page.evaluate('reviewCallback(0)')
            for when in sorted({row['logical_ms'] for row in clip['frames']}):
                page.evaluate('t=>reviewCallback(t)', when)
                expected = max(i for i, row in enumerate(clip['frames']) if row['logical_ms'] <= when)
                assert page.evaluate('nativeReviewState.index') == expected, 'published native timestamp boundary'
            assert not page.evaluate('nativeReviewState.playing')
            checks.append(name + ': all8 exact heading crops, new-pose controls, every native timestamp boundary and endpoint,1280 visibility')
        assert not errors and not requests
        browser.close()
    result = {'status': 'PASS', 'url': URL, 'html_sha256': files['review.html'], 'served_file_count': len(files),
              'smoke_passed': True, 'regressions_after_smoke': checks, 'browser_errors': errors, 'request_failures': requests,
              'screenshots_sha256': screenshots, 'negative_control': 'changed HTML causes one named served identity failure',
              'publisher_sha256': sha(Path(__file__).read_bytes()),
              'scope': 'Published native complete-ring000015 comparison with all prior approved art retained; human approval separate, production unchanged.'}
    (OUT / 'publication.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
