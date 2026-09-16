"""Browser smoke followed by complete native pixel, timing and control checks."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import re
import threading
import traceback
from PIL import Image
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'native-review'))
import config

HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def check(review, record_name='browser-validation.json', base_url=None, expected_html=None):
    assert not (review / record_name).exists(), 'preserve browser evidence'
    raw = (expected_html or review / 'review.html').read_bytes()
    bundle = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    assert list(bundle['clips']) == list(config.CLIPS) and bundle['reference_frames'] == [29] and bundle['target_frames'] == list(config.TARGET_FRAMES), 'eight clips and all28 corrected poses'
    urls = {row[kind] for clip in bundle['clips'].values() for row in clip['frames'] for kind in ('baseline', 'candidate')}
    expected, crops = {}, {}
    for name in urls:
        with Image.open(review / name) as im:
            image = im.convert('RGBA')
            expected[name] = config.sha(image.tobytes())
            for clip, values in bundle['clips'].items():
                x, y, w, h = values['camera_hd_xywh']
                crops[(clip, name)] = config.sha(image.crop((x, y, x + w, y + h)).tobytes())
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = None
    if base_url is None:
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(review)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f'http://127.0.0.1:{server.server_port}/review.html'
    errors, requests, checks, screenshots = [], [], [], {}
    counts = dict(display_panels=0, timestamp_boundaries=0, pose_crops=0, reference_choices=0)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 900})
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('requestfailed', lambda r: requests.append({'name': r.url.split('/')[-1], 'failure': r.failure}))
                response = page.goto(base_url)
                served = response.body()
                print('WITNESS served HTML SHA256=' + config.sha(served), flush=True)
                assert response.status == 200 and served == raw, 'exact served HTML'
                page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=90000, polling=50)
                assert not page.evaluate('window.nativeReviewError||null'), 'native image readiness'
                assert page.locator('#direction').input_value() == 'waypoint_front' and page.locator('#speed').input_value() == '1', 'default Front waypoint and Normal'
                page.wait_for_timeout(260)
                page.locator('#play').click()
                assert page.evaluate('nativeReviewState.index') > 0 and not errors, 'real Normal timer progresses'
                first_urls = {row[kind] for row in bundle['clips']['waypoint_front']['frames'] for kind in ('baseline', 'candidate')}
                assert set(page.evaluate('[...cache.keys()]')) == first_urls, 'only selected clip image references'
                assert page.evaluate('pendingLoads.size') == 0, 'initial image loads completed'
                print('SMOKE PASS exact native images loaded; default Front waypoint and Normal timer progress', flush=True)
                page.close()
                page = browser.new_page(viewport={'width': 1280, 'height': 900})
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('requestfailed', lambda r: requests.append({'name': r.url.split('/')[-1], 'failure': r.failure}))
                page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewCallback=fn;return 1;}')
                page.goto(base_url)
                page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=90000, polling=50)
                assert not page.evaluate('window.nativeReviewError||null'), 'deterministic review ready'
                for name, clip in bundle['clips'].items():
                    page.locator('#direction').select_option(name)
                    page.wait_for_function('(window.nativeReviewState&&nativeReviewState.ready)||window.nativeReviewError', timeout=90000, polling=50)
                    assert not page.evaluate('window.nativeReviewError||null'), 'clip image readiness:' + name
                    clip_urls = {row[kind] for row in clip['frames'] for kind in ('baseline', 'candidate')}
                    assert set(page.evaluate('[...cache.keys()]')) == clip_urls and page.evaluate('pendingLoads.size') == 0, 'exact selected clip cache; previous references released:' + name
                    page.evaluate('play(false)')
                    page.locator('#view').select_option('island')
                    for i, row in enumerate(clip['frames']):
                        page.evaluate('i=>select(i)', i)
                        for kind in ('baseline', 'candidate'):
                            assert page.evaluate(HASH, kind) == expected[row[kind]], 'exact native pixels:' + name + ':' + str(i)
                            counts['display_panels'] += 1
                    page.locator('#repeat').uncheck()
                    page.locator('#replay').click()
                    page.evaluate('reviewCallback(0)')
                    times = {row['logical_ms'] for row in clip['frames']}
                    times.update(max(0, row['logical_ms'] - 1) for row in clip['frames'])
                    for when in sorted(times):
                        page.evaluate('t=>reviewCallback(t)', when)
                        expected_index = max(i for i, row in enumerate(clip['frames']) if row['logical_ms'] <= when)
                        assert page.evaluate('nativeReviewState.index') == expected_index, 'actual timestamp boundary:' + name + ':' + str(when)
                        counts['timestamp_boundaries'] += 1
                    assert not page.evaluate('nativeReviewState.playing'), 'actual endpoint stops:' + name
                    page.locator('#view').select_option('close')
                    for pose in range(clip['pose_count']):
                        page.locator('#pose').select_option(str(pose))
                        state = page.evaluate('nativeReviewState')
                        assert state['pose'] == pose and not state['playing'], 'pose selector native ordinal:' + name + ':' + str(pose)
                        row = clip['frames'][state['index']]
                        for kind in ('baseline', 'candidate'):
                            assert page.evaluate(HASH, kind) == crops[(name, row[kind])], 'exact fixed route crop:' + name + ':' + str(pose)
                            assert page.locator('#' + kind).evaluate('c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight;}'), '1280x900 full visible route canvas'
                            counts['pose_crops'] += 1
                    references = {row['pose_index']: row for row in clip['frames'] if row['frame'] == 29}
                    options = page.locator('#reference option').evaluate_all('items=>items.map(x=>x.value)')
                    assert options == [''] + [str(pose) for pose in references], 'reference selector complete occurrences:' + name
                    for pose, row in references.items():
                        page.locator('#reference').select_option(str(pose))
                        state = page.evaluate('nativeReviewState')
                        assert state['pose'] == pose and state['frame'] == row['frame'] and not state['playing'], 'reference selector native ordinal:' + name + ':' + str(pose)
                        counts['reference_choices'] += 1
                    if references:
                        assert page.locator('#show-reference').is_enabled() and page.locator('#reference').is_enabled(), 'available029 controls:' + name
                        page.locator('#show-reference').click()
                        first = next(row for row in clip['frames'] if row['frame'] == 29)
                        assert page.evaluate('nativeReviewState.pose') == first['pose_index'], 'show first unchanged029:' + name
                    else:
                        assert page.locator('#show-reference').is_disabled() and page.locator('#reference').is_disabled(), 'absent029 controls disabled:' + name
                    page.locator('#arrival').click()
                    arrival = next(row for row in clip['frames'] if row['role'] == 'arrival')
                    assert page.evaluate('nativeReviewState.frame') == arrival['frame'] and page.evaluate('nativeReviewState.role') == 'arrival', 'arrival selects actual retained pose:' + name
                    page.locator('#departure').click()
                    departure = next(row for row in clip['frames'] if row['segment'] == 'travel')
                    assert page.evaluate('nativeReviewState.pose') == departure['pose_index'], 'departure matches first native route draw:' + name
                    ordinal = page.evaluate('nativeReviewState.pose')
                    page.locator('#next').click()
                    assert page.evaluate('nativeReviewState.pose') == (ordinal + 1) % clip['pose_count'], 'next pose preserves every draw'
                    page.locator('#prev').click()
                    assert page.evaluate('nativeReviewState.pose') == ordinal, 'previous pose reverses step'
                    for target in (24, 29, 15, 16):
                        row = next((r for r in clip['frames'] if r['frame'] == target), None)
                        if row is None:
                            continue
                        page.locator('#pose').select_option(str(row['pose_index']))
                        filename = f'{Path(record_name).stem}-{name}-frame{target:03}-1280.png'
                        page.screenshot(path=str(review / filename), full_page=True)
                        screenshots[filename] = config.sha((review / filename).read_bytes())
                    page.locator('#speed').select_option('0.5')
                    page.locator('#replay').click()
                    page.evaluate('reviewCallback(0);reviewCallback(240)')
                    assert page.evaluate('nativeReviewState.position') == 120, 'Slow timing scale'
                    page.locator('#speed').select_option('1')
                    page.locator('#repeat').check()
                    page.locator('#replay').click()
                    page.evaluate('reviewCallback(0)')
                    page.evaluate('t=>reviewCallback(t)', clip['duration_ms'])
                    assert page.evaluate('nativeReviewState.index') == 0 and page.evaluate('nativeReviewState.playing'), 'repeat returns to real priming'
                    checks.append(name + ': all display pixels/timestamps, all pose crops/selectors, reference choices, arrival/departure, pause/step/replay/Slow/repeat,1280 visibility')
                    print('PASS ' + checks[-1], flush=True)
                assert page.locator('#still-link').get_attribute('href') == 'stills/review.html', 'all28 still comparison link'
                still = page.request.get(base_url.rsplit('/', 1)[0] + '/stills/review.html')
                assert still.status == 200 and still.body() == (review / 'stills/review.html').read_bytes(), 'exact linked still review'
                assert not errors and not requests, 'no browser errors or failed images'
            finally:
                browser.close()
    except Exception:
        (review / (Path(record_name).stem + '-failure.json')).write_text(json.dumps({'traceback': traceback.format_exc(), 'page_errors': errors, 'request_failures': requests}, indent=2) + '\n', encoding='utf-8')
        raise
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
    result = {'status': 'PASS', 'html_sha256': config.sha(raw), 'checker_sha256': config.sha(Path(__file__).read_bytes()), 'smoke_passed': 1,
              'regressions_after_smoke': checks, 'unique_native_images': len(urls), 'executed_counts': counts,
              'display_references_checked': sum(len(c['frames']) * 2 for c in bundle['clips'].values()),
              'screenshots_sha256': screenshots, 'browser_errors': errors, 'request_failures': requests,
              'scope': 'Exact eight-clip native color pixel/timing/control validation, including exact active-clip cache membership after each switch. No memory-savings measurement or human color approval inferred.'}
    (review / record_name).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS eight-clip native color review and screenshots', flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--review', type=Path, default=config.OUT / 'review-v1')
    parser.add_argument('--expected-html', type=Path)
    parser.add_argument('--base-url')
    parser.add_argument('--record-name', default='browser-validation.json')
    args = parser.parse_args()
    check(args.review, record_name=args.record_name, base_url=args.base_url, expected_html=args.expected_html)
