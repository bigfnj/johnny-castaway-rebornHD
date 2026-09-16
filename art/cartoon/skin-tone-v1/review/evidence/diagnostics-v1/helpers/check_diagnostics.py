"""Smoke first, then all-pose browser checks for the local still-color review."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading

from playwright.sync_api import sync_playwright


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    review = args.review.resolve()
    output = review / 'browser-validation.json'
    assert not output.exists(), 'preserve browser validation'
    html = (review / 'review.html').read_bytes()
    data = json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>', html.decode(), re.S)[1])
    record = json.loads((review / 'review-record.json').read_bytes())
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(review)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors, failed, counts = [], [], {'pose_selections': 0, 'served_image_hashes': 0, 'control_checks': 0}
    screenshots = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 900})
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('requestfailed', lambda request: failed.append(request.url))
                response = page.goto(f'http://127.0.0.1:{server.server_port}/review.html')
                assert response.status == 200 and response.body() == html, 'exact served diagnostic HTML'
                page.wait_for_function("[...document.querySelectorAll('.stage img')].every(im=>im.complete&&im.naturalWidth)")
                assert page.locator('#pose').input_value() == '24', 'default screenshot1 pose024'
                assert page.locator('#pose option').count() == 28, 'all28 pose choices'
                assert page.locator('#reference').get_attribute('src') == 'images/before-029.png', 'unchanged canonical029 reference'
                assert not errors and not failed, 'browser smoke clean'
                print('SMOKE PASS exact local page, default024, all28 choices and unchanged029 reference', flush=True)
                for row in data['frames']:
                    page.locator('#pose').select_option(str(row['frame']))
                    page.wait_for_function("[...document.querySelectorAll('.stage img')].every(im=>im.complete&&im.naturalWidth)")
                    assert page.locator('body').get_attribute('data-frame') == str(row['frame']), 'selected pose identity'
                    for kind in ('before', 'after', 'overlay'):
                        observed = page.locator('#' + kind).evaluate('(im)=>({src:im.getAttribute("src"),w:im.naturalWidth,h:im.naturalHeight,width:im.getBoundingClientRect().width,height:im.getBoundingClientRect().height})')
                        assert observed == {'src': row[kind], 'w': row['canvas'][0], 'h': row['canvas'][1], 'width': row['canvas'][0] * 3 if kind != 'overlay' else 0, 'height': row['canvas'][1] * 3 if kind != 'overlay' else 0}, 'same intact3x pose canvas:' + kind + ':' + str(row['frame'])
                    counts['pose_selections'] += 1
                # Fetch and hash exact served bytes independently of image element IDs.
                for name, digest in record['files_sha256'].items():
                    if not name.startswith('images/'):
                        continue
                    actual = page.evaluate("async name=>{const b=await(await fetch(name)).arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('')}", name)
                    assert actual == digest, 'exact served image:' + name
                    counts['served_image_hashes'] += 1
                page.locator('#pose').select_option('24')
                page.locator('#next').click()
                assert page.locator('#pose').input_value() == '25', 'next pose'
                page.locator('#prev').click()
                assert page.locator('#pose').input_value() == '24', 'previous pose'
                page.locator('#pose').select_option('0')
                page.locator('#prev').click()
                assert page.locator('#pose').input_value() == '29', 'previous wraps to029'
                assert 'unchanged' in page.locator('#pose-note').inner_text(), 'canonical unchanged label'
                page.locator('#next').click()
                assert page.locator('#pose').input_value() == '0', 'next wraps to000'
                page.locator('#pose').select_option('24')
                page.wait_for_function("document.getElementById('after').complete")
                page.screenshot(path=str(review / 'browser-colors-024.png'), full_page=True)
                page.locator('#mask-toggle').check()
                assert page.locator('.mask-panel').is_visible() and not page.locator('.reference').is_visible(), 'mask display toggle'
                assert page.locator('#overlay').evaluate('(im)=>im.getBoundingClientRect().width') == 192, 'mask fixed3x canvas'
                page.screenshot(path=str(review / 'browser-mask-024.png'), full_page=True)
                page.locator('#mask-toggle').uncheck()
                assert page.locator('.reference').is_visible() and not page.locator('.mask-panel').is_visible(), 'return to unchanged reference'
                counts['control_checks'] = 8
                assert not errors and not failed, 'browser regression clean'
                for name in ('browser-colors-024.png', 'browser-mask-024.png'):
                    screenshots[name] = sha((review / name).read_bytes())
                print('REGRESSION PASS28 pose selections,112 exact served image hashes and8 controls', flush=True)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result = {'status': 'PASS', 'ordered_phases': ['smoke', 'regression'], 'counts': counts,
              'html_sha256': sha(html), 'review_record_sha256': sha((review / 'review-record.json').read_bytes()),
              'checker_sha256': sha(Path(__file__).read_bytes()), 'screenshots_sha256': screenshots,
              'browser_errors': errors, 'request_failures': failed,
              'scope': 'Local still-color diagnostic only; no publication, native motion or human approval.'}
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
