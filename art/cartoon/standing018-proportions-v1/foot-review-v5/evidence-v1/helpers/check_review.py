"""Check the changed contact view and reuse the frozen three-clip checker."""
import argparse
import functools
import http.server
import importlib.util
import io
import json
from pathlib import Path
import re
import threading
from PIL import Image
from playwright.sync_api import sync_playwright
import build_review as build

SHARED_PATH = build.HERE / 'shared_motion_check.py'
SHARED_SHA = '5aa64a669a5a2cea5a7a2e50726e1990620d8a1a645a3134e1868deb61ce45d4'
assert build.sha(SHARED_PATH.read_bytes()) == SHARED_SHA, 'unchanged reused motion checker'
spec = importlib.util.spec_from_file_location('shared018_motion_check', SHARED_PATH)
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
# The existing checker exposes this module-level binding interface. Keep its
# playback/pixel/control implementation exact; provide the new source pins.
shared.config = build


def data(review):
    return json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', (review / 'review.html').read_text(), re.S)[1])


def validate_contact(review, values):
    record = build.load(review / 'review-record.json')
    assert record['baseline_archive_sha256'] == build.BASE_SHA and record['candidate_archive_sha256'] == build.CANDIDATE_SHA and record['runtime018_sha256'] == build.RUNTIME_SHA, 'contact current-v2/new source binding'
    assert values['display_index'] == 63 and values['draw'] == [1, 394, 209, 18] and values['logical_ms'] == 4920, 'contact mirrored arrival occurrence'
    assert values['pose'] == [784, 410, 80, 178] and values['feet'] == [792, 546, 60, 34], 'contact fixed source camera'
    assert [r['kind'] for r in values['panels']] == ['original', 'current', 'revised'], 'contact three source roles'
    for name, digest in record['files_sha256'].items():
        assert build.sha((review / name).read_bytes()) == digest, 'contact bound file:' + name
    expected_archives = ['d7797181cf2e30699709946f0983b6899f0c7428785f9c596dea8ac150619f20', build.BASE_SHA, build.CANDIDATE_SHA]
    for row, archive in zip(values['panels'], expected_archives):
        raw = (review / 'inputs' / (row['kind'] + '-report.json')).read_bytes()
        report = json.loads(raw)
        display = report['displays'][62]
        assert report['archive_sha256'] == archive == row['archive_sha256'] and build.sha(raw) == row['report_sha256'], 'contact selected capture source:' + row['kind']
        assert display['actual_draw'] == values['draw'] and display['logical_ms'] == values['logical_ms'], 'contact exact captured draw:' + row['kind']
        image_raw = (review / row['image']).read_bytes()
        assert build.sha(image_raw) == row['png_sha256'] == display['png_sha256'], 'contact image/source binding:' + row['kind']
        with Image.open(io.BytesIO(image_raw)) as im:
            assert im.size == (1280, 960) and build.sha(im.convert('RGB').tobytes()) == display['pixels_sha256'], 'contact captured pixels:' + row['kind']
    assert record['motion_record_sha256'] == build.sha((review / 'motion/review-record.json').read_bytes()), 'contact linked motion record'


def contact_check(review, record_name='contact-browser.json', base_url=None):
    assert not (review / record_name).exists(), 'preserve contact browser report'
    values = data(review)
    validate_contact(review, values)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = None
    if base_url is None:
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(review)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f'http://127.0.0.1:{server.server_port}/review.html'
    errors, checks = [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 900})
                page.on('pageerror', lambda e: errors.append(str(e)))
                response = page.goto(base_url)
                assert response.status == 200 and response.body() == (review / 'review.html').read_bytes(), 'contact exact served HTML'
                page.wait_for_function('window.reviewReady||window.reviewError', polling=50)
                assert page.evaluate('window.reviewReady') and not errors, 'contact images ready'
                assert page.locator('h1').inner_text() == 'Foot contact' and page.locator('article h2').all_text_contents() == ['Original pose', 'Previous version', 'Corrected foot'], 'default foot contact and source labels'
                print('SMOKE PASS three loaded contact sources; mirrored arrival default', flush=True)
                for row in values['panels']:
                    image = Image.open(review / row['image']).convert('RGBA')
                    for kind in ('pose', 'feet'):
                        x, y, w, h = values[kind]
                        expected = build.sha(image.crop((x, y, x+w, y+h)).tobytes())
                        assert page.evaluate(shared.HASH, row['kind'] + '-' + kind) == expected, 'exact contact crop:' + row['kind'] + ':' + kind
                        assert page.locator('#' + row['kind'] + '-' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}'), '1280x900 contact visible:' + row['kind'] + ':' + kind
                        checks.append(row['kind'] + ':' + kind)
                assert page.locator('#motion-link').get_attribute('href') == 'motion/review.html', 'contact motion link destination'
                linked = page.request.get(base_url.rsplit('/', 1)[0] + '/motion/review.html')
                assert linked.status == 200 and linked.body() == (review / 'motion/review.html').read_bytes(), 'exact linked motion page'
                shot = Path(record_name).stem + '-1280.png'
                page.screenshot(path=str(review / shot), full_page=True)
                page.locator('#motion-link').click()
                page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', polling=50, timeout=90000)
                assert not page.evaluate('window.nativeReviewError||null') and page.locator('#speed').input_value() == '1', 'linked native motion ready at Normal'
                page.wait_for_timeout(240)
                assert page.evaluate('nativeReviewState.index') > 0, 'linked real motion progresses'
                assert page.locator('a[href="../review.html"]').count() == 1, 'motion return link exists'
                page.locator('a[href="../review.html"]').click()
                page.wait_for_function('window.reviewReady', polling=50)
                assert page.locator('h1').inner_text() == 'Foot contact' and not errors, 'return to contact works'
            finally: browser.close()
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
    result = {'status': 'PASS', 'smoke_before_regression': True, 'six_exact_visible_crops': checks,
              'motion_link_and_return': 'PASS; real Normal playback progresses', 'html_sha256': build.sha((review / 'review.html').read_bytes()),
              'checker_sha256': build.sha(Path(__file__).read_bytes()), 'shared_motion_checker_sha256': SHARED_SHA,
              'screenshot': shot, 'screenshot_sha256': build.sha((review / shot).read_bytes()), 'browser_errors': errors}
    (review / record_name).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS six exact contact crops; motion link, Normal playback and return', flush=True)
    return result


def full_check(review):
    contact = contact_check(review)
    motion = shared.check(review / 'motion')
    result = {'status': 'PASS', 'contact_record_sha256': build.sha((review / 'contact-browser.json').read_bytes()),
              'motion_record_sha256': build.sha((review / 'motion/browser-validation.json').read_bytes()),
              'checker_sha256': build.sha(Path(__file__).read_bytes()), 'bindings_sha256': build.sha(Path(build.__file__).read_bytes()),
              'shared_checker_sha256': SHARED_SHA, 'motion_counts': motion['executed_counts'],
              'scope': 'Changed contact/source/link checks plus exact reuse of the frozen three-clip pixel/timing/control regression. No old mutation matrix rerun.'}
    (review / 'browser-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    full_check(p.parse_args().review)
