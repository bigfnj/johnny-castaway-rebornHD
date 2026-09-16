"""Bounded native ring browser checks and root pose screenshots."""
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading

from PIL import Image
from playwright.sync_api import sync_playwright
import config

OUT = Path(__file__).resolve().parent
REVIEW = OUT / 'review-v1'
HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    assert not (REVIEW / 'browser-validation.json').exists(), 'preserve existing validation'
    raw = (REVIEW / 'review.html').read_bytes()
    bundle = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    urls = {row[kind] for clip in bundle['clips'].values() for row in clip['frames'] for kind in ('baseline', 'candidate')}
    expected, crops = {}, {}
    for name in urls:
        with Image.open(REVIEW / name) as im:
            image = im.convert('RGBA')
            expected[name] = sha(image.tobytes())
            crops[name] = sha(image.crop((560, 400, 960, 680)).tobytes())
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REVIEW)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/review.html'
    errors, requests, checks, screenshots = [], [], [], {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('requestfailed', lambda r: requests.append({'name': r.url.split('/')[-1], 'failure': r.failure}))
            response = page.goto(url)
            assert response.body() == raw
            page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=60000)
            assert not page.evaluate('window.nativeReviewError||null'), 'native image readiness'
            assert page.locator('#direction').input_value() == config.DEFAULT_CLIP and page.locator('#speed').input_value() == '1'
            page.wait_for_timeout(260)
            page.locator('#play').click()
            assert page.evaluate('nativeReviewState.index') > 0 and not errors
            assert page.evaluate('cache.size') == len(urls)
            print('SMOKE PASS exact native image set loaded; longer default direction and Normal timer progress', flush=True)
            page.close()
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('requestfailed', lambda r: requests.append({'name': r.url.split('/')[-1], 'failure': r.failure}))
            page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
            page.goto(url)
            page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=60000)
            assert not page.evaluate('window.nativeReviewError||null')
            for name, clip in bundle['clips'].items():
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
                for when in sorted({row['logical_ms'] for row in clip['frames']}):
                    page.evaluate('t=>reviewCallback(t)', when)
                    expected_index = max(i for i, row in enumerate(clip['frames']) if row['logical_ms'] <= when)
                    assert page.evaluate('nativeReviewState.index') == expected_index, 'actual timestamp boundary:' + name + ':' + str(when)
                assert not page.evaluate('nativeReviewState.playing'), 'actual endpoint stops'
                for heading in range(8):
                    page.locator('#heading').select_option(str(heading))
                    state = page.evaluate('nativeReviewState')
                    assert state['heading'] == heading and not state['playing'] and state['view'] == 'walk'
                    row = clip['frames'][state['index']]
                    for kind in ('baseline', 'candidate'):
                        assert page.evaluate(HASH, kind) == crops[row[kind]], 'exact heading crop:' + name + ':' + str(heading)
                        assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}'), 'full visible heading canvas'
                    if heading in (2, 4, 6):
                        filename = f'{name}-heading{heading}-frame{row["frame"]:03}-1280.png'
                        page.screenshot(path=str(REVIEW / filename), full_page=True)
                        screenshots[filename] = sha((REVIEW / filename).read_bytes())
                page.locator('#side').click()
                assert page.evaluate('nativeReviewState.heading') == 6 and page.evaluate('nativeReviewState.frame') == 0
                page.locator('#back').click()
                assert page.evaluate('nativeReviewState.heading') == 4 and page.evaluate('nativeReviewState.frame') == 15
                ordinal = page.evaluate('data.frames[index].pose_index')
                page.locator('#next').click()
                assert page.evaluate('data.frames[index].pose_index') == (ordinal + 1) % clip['pose_count']
                page.locator('#prev').click()
                assert page.evaluate('data.frames[index].pose_index') == ordinal
                page.locator('#speed').select_option('0.5')
                page.locator('#replay').click()
                page.evaluate('reviewCallback(0);reviewCallback(240)')
                assert page.evaluate('nativeReviewState.position') == 120
                page.locator('#speed').select_option('1')
                page.locator('#repeat').check()
                page.locator('#replay').click()
                page.evaluate('reviewCallback(0)')
                page.evaluate('t=>reviewCallback(t)', clip['duration_ms'])
                assert page.evaluate('nativeReviewState.index') == 0 and page.evaluate('nativeReviewState.playing')
                checks.append(name + ': every native display pixel/timestamp, all8 heading crops, exact call boundaries, pause/step/replay/Slow/repeat,1280 visibility')
                print('PASS ' + checks[-1], flush=True)
            assert not errors and not requests, 'no browser errors or failed image requests'
            browser.close()
    except Exception as error:
        (REVIEW / 'browser-failure.json').write_text(json.dumps({'error': str(error), 'page_errors': errors, 'request_failures': requests}, indent=2) + '\n')
        raise
    finally:
        server.shutdown()
        server.server_close()
    result = {'status': 'PASS', 'html_sha256': sha(raw), 'checker_sha256': sha(Path(__file__).read_bytes()),
              'smoke_passed': 1, 'regressions_after_smoke': checks, 'unique_native_images': len(urls),
              'display_references_checked': sum(len(c['frames']) * 2 for c in bundle['clips'].values()),
              'screenshots_sha256': screenshots, 'browser_errors': errors, 'request_failures': requests,
              'scope': 'Bounded local complete-ring native pixel/timing/control validation. Root visual checkpoint required before publication.'}
    (REVIEW / 'browser-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS local full-ring review and six new-pose screenshots; unpublished', flush=True)


if __name__ == '__main__':
    main()
