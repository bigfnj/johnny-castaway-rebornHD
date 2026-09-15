"""Check the actual review in Chromium: smoke before exact timed pixel playback."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import functools
import http.server
import threading

from PIL import Image
from playwright.sync_api import sync_playwright


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


HASH_CANVAS = """async id=>{const c=document.getElementById(id),bytes=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    path = args.review / 'review.html'
    raw = path.read_bytes()
    data = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    expected = {}
    for row in data['frames']:
        for kind in ('baseline', 'candidate'):
            with Image.open(args.review / row[kind]) as image:
                expected[row[kind]] = sha(image.convert('RGBA').tobytes())
    checks = []
    mutations = []
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(args.review.resolve())))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base_url = f'http://127.0.0.1:{server.server_port}/'
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1600, 'height': 1100})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(base_url + 'review.html')
        page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
        assert page.locator('#speed').input_value() == '1' and page.locator('#view').input_value() == 'island'
        assert page.evaluate('images.baseline.length===47&&images.candidate.length===47')
        page.locator('#play').click()
        page.evaluate('select(0)')
        assert page.evaluate(HASH_CANVAS, 'candidate') == expected[data['frames'][0]['candidate']]
        print('SMOKE PASS 94 native PNGs loaded; default full island; exact first candidate pixels', flush=True)
        page.locator('#next').click()
        assert page.evaluate('nativeReviewState.index') == 1
        page.locator('#prev').click()
        assert page.evaluate('nativeReviewState.index') == 0
        page.locator('#play').click()
        page.wait_for_timeout(260)
        page.locator('#play').click()
        assert 1 <= page.evaluate('nativeReviewState.index') <= 8
        assert not errors
        print('SMOKE PASS previous/next/play/pause; actual browser timer progresses; no errors', flush=True)
        page.close()

        # Drive the real browser callback at exact independently recorded times.
        page = browser.new_page(viewport={'width': 1600, 'height': 1100})
        page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
        page.goto(base_url + 'review.html')
        page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
        page.locator('#repeat').uncheck()
        page.evaluate('reviewCallback(0)')
        for i, row in enumerate(data['frames']):
            page.evaluate('t=>reviewCallback(t)', row['logical_ms'])
            state = page.evaluate('nativeReviewState')
            assert state['index'] == i and state['frame'] == row['frame'], f'exact-timed-display:{i + 1}'
            for kind in ('baseline', 'candidate'):
                assert page.evaluate(HASH_CANVAS, kind) == expected[row[kind]], f'exact-native-pixels:{kind}:{i + 1}'
        assert not page.evaluate('nativeReviewState.playing')
        assert 'Arrival pose' in page.locator('#status').inner_text()
        checks.append('47 exact logical times and94 full-canvas native pixel hashes; final endpoint stops')
        page.locator('#view').select_option('walk')
        assert page.locator('#candidate').evaluate('c=>[c.width,c.height]') == [400, 280]
        for kind in ('baseline', 'candidate'):
            row = data['frames'][-1]
            x, y = 560, 400
            with Image.open(args.review / row[kind]) as im:
                expected_crop = sha(im.convert('RGBA').crop((x, y, x + 400, y + 280)).tobytes())
            assert page.evaluate(HASH_CANVAS, kind) == expected_crop, 'exact-closeup:' + kind
        page.locator('#view').select_option('island')
        page.locator('#repeat').check()
        page.evaluate('select(0);play(true);reviewCallback(0);reviewCallback(4360)')
        assert page.evaluate('nativeReviewState.index') == 0
        page.evaluate('select(0);play(false)')
        for _ in range(22): page.locator('#next').click()
        assert page.evaluate('nativeReviewState.frame') == 27
        page.locator('#next').click()
        assert page.evaluate('nativeReviewState.frame') == 17
        page.locator('#prev').click()
        assert page.evaluate('nativeReviewState.frame') == 27
        checks.append('close-up/full-island controls, last-walk-to-arrival stepping and recorded-route repeat')
        for width in (1280, 1600):
            page.set_viewport_size({'width': width, 'height': 1100})
            for kind in ('baseline', 'candidate'):
                fit = page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&Math.abs(r.width/c.width-r.height/c.height)<0.001;}')
                assert fit, f'full-scene-fit:{width}:{kind}'
            page.screenshot(path=str(args.review / f'preview-{width}.png'), full_page=True)
        checks.append('both full-scene canvases retain aspect and fit1280/1600')
        page.close()
        broken = raw.decode().replace('images/candidate/display-001.png', 'images/candidate/absent.png', 1)
        broken_path = args.review / 'missing-image-control.html'
        broken_path.write_text(broken, encoding='utf-8', newline='\n')
        page = browser.new_page()
        page.goto(base_url + broken_path.name)
        page.wait_for_function('window.nativeReviewError')
        assert page.locator('#failure').inner_text() == 'Cannot load candidate capture 1'
        page.close()
        checks.append('missing-image negative control reports exact candidate capture')
        for label, old, new in [('timed-display', "position+=(time-lastTime)*Number($('speed').value)", 'position+=0'),
                                ('candidate-pixel-identity', 'ctx.drawImage(images[kind][index],0,0)', 'ctx.drawImage(images.baseline[index],0,0)')]:
            text = raw.decode()
            assert text.count(old) == 1
            changed = text.replace(old, new)
            mutant_path = args.review / (label + '-mutant.html')
            mutant_path.write_text(changed, encoding='utf-8', newline='\n')
            page = browser.new_page()
            page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
            response = page.goto(base_url + mutant_path.name)
            assert response.body() == mutant_path.read_bytes(), 'served-mutant-byte-identity'
            script = re.findall(r'<script>(.*?)</script>', changed, re.S)[-1]
            assert sha(page.locator('script').last.text_content().encode()) == sha(script.encode()), 'loaded-mutant-script-identity'
            page.wait_for_function('window.nativeReviewState&&nativeReviewState.ready')
            page.evaluate('reviewCallback(0)')
            if label == 'timed-display':
                page.evaluate('reviewCallback(120)')
                failed = page.evaluate('nativeReviewState.index') != 1
            else:
                arrival = next(i for i, row in enumerate(data['frames']) if row['frame'] == 28)
                page.evaluate('i=>select(i)', arrival)
                failed = page.evaluate(HASH_CANVAS, 'candidate') != expected[data['frames'][arrival]['candidate']]
            assert failed, label + ': mutant survived'
            mutations.append({'label': 'review.html:' + label, 'result': 'FIRED', 'failure_count': 1,
                              'html_sha256': sha(mutant_path.read_bytes()),
                              'witness': 'Actual served bytes and loaded browser script digest match; executed timer or canvas pixels fail one named oracle.'})
            page.close()
        browser.close()
    server.shutdown()
    server.server_close()
    evidence = {'html_sha256': sha(raw), 'test_sha256': sha(Path(__file__).read_bytes()),
                'smoke_passed': 2, 'regressions': checks, 'mutations': mutations,
                'scope': 'Actual Chromium rendering and timer callback, exact native pixels. Browser wall-clock smoke uses a bounded interval; no physical timing claim.'}
    (args.review / 'browser-validation.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS native browser review: ' + str(len(checks)) + ' grouped regressions', flush=True)


if __name__ == '__main__':
    main()
