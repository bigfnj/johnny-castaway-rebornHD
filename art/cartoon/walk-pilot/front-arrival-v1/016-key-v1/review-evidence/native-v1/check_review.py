"""Bounded native turn viewer smoke, timing/pixel checks and root screenshots."""
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
REVIEW = OUT / 'review-v1'
HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    result_path = REVIEW / 'browser-validation.json'
    if result_path.exists():
        raise ValueError('preserve existing browser evidence')
    raw = (REVIEW / 'review.html').read_bytes()
    data = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    expected = {}
    for clip in data['clips'].values():
        for row in clip['frames']:
            for kind in ('baseline', 'candidate'):
                with Image.open(REVIEW / row[kind]) as image:
                    expected[row[kind]] = sha(image.convert('RGBA').tobytes())
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REVIEW)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/review.html'
    screenshots, checks = {}, []
    page = None
    request_failures = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('requestfailed', lambda r: request_failures.append({'url': r.url.split('/')[-1], 'failure': r.failure}))
            response = page.goto(url)
            assert response.body() == raw, 'served local HTML identity'
            page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError')
            assert not page.evaluate('window.nativeReviewError||null'), 'image-load diagnostic:' + str(page.evaluate('window.nativeReviewError||null'))
            assert page.locator('#speed').input_value() == '1' and page.locator('#view').input_value() == 'island'
            page.wait_for_timeout(260)
            page.locator('#play').click()
            assert page.evaluate('nativeReviewState.index') > 0 and not errors, 'actual normal timer advances'
            print('SMOKE PASS native images loaded, Normal timer advances, no errors', flush=True)
            page.close()
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('requestfailed', lambda r: request_failures.append({'url': r.url.split('/')[-1], 'failure': r.failure}))
            page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
            page.goto(url)
            page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError')
            assert not page.evaluate('window.nativeReviewError||null'), 'controlled page image-load diagnostic'
            for name, clip in data['clips'].items():
                page.locator('#direction').select_option(name)
                page.evaluate('play(false)')
                page.locator('#view').select_option('island')
                for i, row in enumerate(clip['frames']):
                    page.evaluate('i=>select(i)', i)
                    for kind in ('baseline', 'candidate'):
                        assert page.evaluate(HASH, kind) == expected[row[kind]], 'exact native pixels:' + name + ':' + str(i)
                page.locator('#repeat').uncheck()
                page.locator('#replay').click()
                page.evaluate('reviewCallback(0)')
                for when in sorted({r['logical_ms'] for r in clip['frames']}):
                    page.evaluate('t=>reviewCallback(t)', when)
                    last = max(i for i, row in enumerate(clip['frames']) if row['logical_ms'] <= when)
                    assert page.evaluate('nativeReviewState.index') == last, 'native timed boundary:' + name + ':' + str(when)
                assert not page.evaluate('nativeReviewState.playing'), 'native endpoint stops'
                page.locator('#turning').click()
                state = page.evaluate('nativeReviewState')
                assert state['clip'] == name and state['frame'] == 16 and state['segment'] == 'turn' and state['position'] == clip['turn_start_ms'] and not state['playing'] and state['view'] == 'walk'
                positions = [('turning016', page.evaluate('nativeReviewState.index'))]
                page.locator('#prev').click()
                assert page.evaluate('nativeReviewState.frame') == 17 and page.evaluate('nativeReviewState.segment') == 'prime'
                positions.append(('starting017', page.evaluate('nativeReviewState.index')))
                page.locator('#next').click()
                assert page.evaluate('nativeReviewState.frame') == 16
                page.locator('#next').click()
                assert page.evaluate('nativeReviewState.frame') == 17 and page.evaluate('nativeReviewState.segment') == 'turn'
                positions.append(('settling017', page.evaluate('nativeReviewState.index')))
                for label, index in positions:
                    page.evaluate('i=>select(i)', index)
                    row = clip['frames'][index]
                    for kind in ('baseline', 'candidate'):
                        with Image.open(REVIEW / row[kind]) as im:
                            cropped = sha(im.convert('RGBA').crop((560, 400, 960, 680)).tobytes())
                        assert page.evaluate(HASH, kind) == cropped, 'exact fixed crop:' + name + ':' + label
                        assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}'), 'visible fixed crop'
                    filename = name + '-' + label + '-1280.png'
                    page.screenshot(path=str(REVIEW / filename), full_page=True)
                    screenshots[filename] = sha((REVIEW / filename).read_bytes())
                page.locator('#speed').select_option('0.5')
                page.locator('#replay').click()
                page.evaluate('reviewCallback(0);reviewCallback(240)')
                assert page.evaluate('nativeReviewState.position') == 120 and page.evaluate('nativeReviewState.frame') == 16, 'half-speed actual turn'
                page.locator('#speed').select_option('1')
                checks.append(name + ': all raw display pixels, observed timestamp boundaries, fixed crops, priming/turn step controls, replay and Slow cadence')
                print('PASS ' + checks[-1], flush=True)
            assert not errors
            browser.close()
    except Exception as error:
        (REVIEW / 'browser-failure.json').write_text(json.dumps({'error': str(error), 'request_failures': request_failures, 'page_errors': errors}, indent=2) + '\n')
        raise
    finally:
        server.shutdown()
        server.server_close()
    record = {'status': 'PASS', 'html_sha256': sha(raw), 'checker_sha256': sha(Path(__file__).read_bytes()),
              'smoke_passed': 1, 'regressions_after_smoke': checks, 'browser_errors': errors,
              'screenshots_sha256': screenshots,
              'scope': 'Bounded local two-direction native pixel/timing/control checks. Root visual checkpoint required before publication; no human016 approval.'}
    result_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS local turn review and six native pose screenshots; unpublished', flush=True)


if __name__ == '__main__':
    main()
