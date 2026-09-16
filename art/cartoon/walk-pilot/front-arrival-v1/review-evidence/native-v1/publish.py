"""Publish the already-tested native review and verify its served identity."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.request import urlopen

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / 'island-review-v1'
FROZEN = SOURCE
DESTINATION = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review/front-arrival017-v1')
URL = 'http://127.0.0.1:8932/front-arrival017-v1/'
HASH_CANVAS = """async id=>{const c=document.getElementById(id),bytes=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw, expected, name):
    if sha(raw) != expected:
        raise AssertionError('served-identity:' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    record = json.loads((FROZEN / 'review-record.json').read_bytes())
    validation = json.loads((SOURCE / 'browser-validation.json').read_bytes())
    assert validation['html_sha256'] == record['html_sha256'], 'browser-tested-html-identity'
    assert validation['test_sha256'] == sha((HERE / 'check_review.py').read_bytes()), 'browser-checker-identity'
    assert validation['smoke_passed'] == 2 and len(validation['regressions']) == 4 and len(validation['mutations']) == 3, 'required-local-browser-validation'
    assert all(row['result'] == 'FIRED' and row['failure_count'] == 1 for row in validation['mutations']), 'executed-browser-mutations'
    expected = {'review.html': record['html_sha256'], **record['image_files']}
    if not args.verify_only:
        assert not DESTINATION.exists(), 'published-directory-already-exists'
        for name, digest in expected.items():
            identity((SOURCE / name).read_bytes(), digest, name)
        DESTINATION.mkdir()
        for name in expected:
            target = DESTINATION / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((SOURCE / name).read_bytes())
    for name, digest in expected.items():
        with urlopen(URL + name, timeout=30) as response:
            assert response.status == 200, 'served-status:' + name
            identity(response.read(), digest, name)
    raw = (DESTINATION / 'review.html').read_bytes()
    data = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    # One changed byte must fail this exact artifact identity check.
    try:
        identity(raw + b' ', expected['review.html'], 'review.html')
    except AssertionError as error:
        assert str(error) == 'served-identity:review.html'
    else:
        raise AssertionError('changed-served-html-control-survived')
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
        page.goto(URL + 'review.html')
        page.wait_for_function('window.nativeReviewState && nativeReviewState.ready')
        assert page.locator('#speed').input_value() == '1'
        assert page.locator('#view').input_value() == 'island'
        assert page.evaluate('images.baseline.length===47 && images.candidate.length===47')
        assert not errors
        print('SMOKE PASS: 95 served identities and 94 loaded native images', flush=True)
        page.locator('#repeat').uncheck()
        page.evaluate('reviewCallback(0)')
        for index, row in enumerate(data['frames']):
            page.evaluate('t=>reviewCallback(t)', row['logical_ms'])
            state = page.evaluate('nativeReviewState')
            assert state['index'] == index and state['frame'] == row['frame']
            for kind in ('baseline', 'candidate'):
                with Image.open(DESTINATION / row[kind]) as image:
                    digest = sha(image.convert('RGBA').tobytes())
                assert page.evaluate(HASH_CANVAS, kind) == digest, 'served-native-pixels:' + row[kind]
        assert not page.evaluate('nativeReviewState.playing')
        assert 'Arrival pose' in page.locator('#status').inner_text()
        checks.append('47 native display times and 94 rendered RGBA identities; final arrival stops')
        page.locator('#view').select_option('walk')
        assert page.locator('#candidate').evaluate('c=>[c.width,c.height]') == [400, 280]
        for kind in ('baseline', 'candidate'):
            with Image.open(DESTINATION / data['frames'][-1][kind]) as image:
                digest = sha(image.convert('RGBA').crop((560,400,960,680)).tobytes())
            assert page.evaluate(HASH_CANVAS, kind) == digest, 'served-closeup:' + kind
        page.locator('#arrival').click()
        state = page.evaluate('nativeReviewState')
        assert state['frame'] == 17 and state['position'] == 2760 and not state['playing'] and state['view'] == 'walk', 'published-show-arrival'
        page.locator('#prev').click()
        assert page.evaluate('nativeReviewState.frame') == 27, 'published-previous-last-step'
        page.locator('#next').click()
        assert page.evaluate('nativeReviewState.frame') == 17, 'published-next-arrival'
        page.locator('#replay').click()
        assert page.evaluate('nativeReviewState.index') == 0 and page.evaluate('nativeReviewState.playing'), 'published-replay'
        page.locator('#speed').select_option('0.5')
        page.evaluate('reviewCallback(0);reviewCallback(240)')
        assert page.evaluate('nativeReviewState.position') == 120, 'published-slow-speed'
        page.locator('#speed').select_option('1')
        checks.append('fixed close-up preserves exact arrival pixels')
        page.locator('#view').select_option('island')
        page.evaluate('select(0);play(false)')
        for kind in ('baseline', 'candidate'):
            assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight&&Math.abs(r.width/c.width-r.height/c.height)<0.001;}')
        assert not errors
        page.screenshot(path=str(HERE / 'published-1280.png'), full_page=True)
        checks.append('full-island aspect and 1280px layout; no JavaScript errors')
        browser.close()
    report = {'url': URL + 'review.html', 'html_sha256': sha(raw),
              'publisher_sha256': sha(Path(__file__).read_bytes()),
              'served_file_count': len(expected), 'smoke_passed': True,
              'regressions_after_smoke': checks,
              'negative_control': 'changed served HTML produces one named identity failure',
              'scope': 'Publication of native current Cartoon walk and proposed017 comparison. Human approval pending; production archive unchanged.'}
    (HERE / 'publication.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
