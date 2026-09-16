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
import build_review as config
import io
import zipfile

HASH = """async id=>{const c=document.getElementById(id),b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('')}"""


def validate_model(bundle, review):
    assert list(bundle['clips']) == list(config.CLIPS) and bundle['reference_frames'] == [18] and bundle['target_frames'] == [18], 'three clips and selected018'
    record = json.loads((review / 'review-record.json').read_bytes())
    assert record['baseline_archive_sha256'] == config.BASE_SHA and record['candidate_archive_sha256'] == config.CANDIDATE_SHA and record['runtime018_sha256'] == config.RUNTIME_SHA, 'review selected source identity'
    for name, digest in record['files_sha256'].items():
        if name != 'review.html':
            assert config.sha((review / name).read_bytes()) == digest, 'review bound artifact:' + name
    with zipfile.ZipFile(config.REVISED / 'scrantic_data.zip') as archive:
        for clip, values in bundle['clips'].items():
            left = config.load(review / 'inputs' / clip / 'baseline-full.json')
            right = config.load(review / 'inputs' / clip / 'candidate-full.json')
            config.validate_pair(left, right, clip, record['executable_sha256'])
            assert values['duration_ms'] == right['duration_ms'] and len(values['frames']) == len(right['displays']), 'review full native timeline:' + clip
            rectangles = []
            for row, a, b in zip(values['frames'], left['displays'], right['displays']):
                assert all(row[k] == b[k] for k in config.TIMELINE_KEYS if k != 'index') and row['pose_index'] == b['draw_ordinal'] and row['frame'] == b['actual_draw'][3], 'review native time/draw binding:' + clip
                assert row['baseline'] == 'images/' + a['png_sha256'] + '.png' and row['candidate'] == 'images/' + b['png_sha256'] + '.png', 'review native image binding:' + clip
                flip, x, y, frame = b['actual_draw']
                with Image.open(io.BytesIO(archive.read(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'))) as im:
                    w, h = im.size
                rectangles.append((x * 2, y * 2, x * 2 + w, y * 2 + h))
            union = [min(v[0] for v in rectangles), min(v[1] for v in rectangles), max(v[2] for v in rectangles), max(v[3] for v in rectangles)]
            box = [max(0, union[0]-16), max(0, union[1]-16), min(1280, union[2]+16), min(960, union[3]+16)]
            camera = [box[0], box[1], box[2]-box[0], box[3]-box[1]]
            assert values['all_canvas_union_hd_xyxy'] == union and values['camera_hd_xywh'] == camera, 'review fixed full-canvas camera:' + clip
            assert values['pose_count'] == max(b['draw_ordinal'] for b in right['displays'])+1, 'review native pose count:' + clip
    print('PASS source-bound three-clip model, timelines, images and fixed cameras', flush=True)


def check(review, record_name='browser-validation.json', base_url=None, expected_html=None):
    assert not (review / record_name).exists(), 'preserve browser evidence'
    raw = (expected_html or review / 'review.html').read_bytes()
    assert config.sha(raw) == config.load(review / 'review-record.json')['files_sha256']['review.html'], 'bound review HTML identity'
    bundle = json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', raw.decode(), re.S)[1])
    validate_model(bundle, review)
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
                assert page.locator('.panel h2').all_text_contents() == ['Previous version', 'Corrected foot'], 'earlier/revised panel labels'
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
                    references = {row['pose_index']: row for row in clip['frames'] if row['frame'] == 18}
                    options = page.locator('#reference option').evaluate_all('items=>items.map(x=>x.value)')
                    assert options == [''] + [str(pose) for pose in references], 'reference selector complete occurrences:' + name
                    for pose, row in references.items():
                        page.locator('#reference').select_option(str(pose))
                        state = page.evaluate('nativeReviewState')
                        assert state['pose'] == pose and state['frame'] == row['frame'] and not state['playing'], 'reference selector native ordinal:' + name + ':' + str(pose)
                        counts['reference_choices'] += 1
                    if references:
                        assert page.locator('#show-reference').is_enabled() and page.locator('#reference').is_enabled(), 'available018 controls:' + name
                        page.locator('#show-reference').click()
                        first = next(row for row in clip['frames'] if row['frame'] == 18)
                        assert page.evaluate('nativeReviewState.pose') == first['pose_index'], 'show first018:' + name
                    else:
                        assert page.locator('#show-reference').is_disabled() and page.locator('#reference').is_disabled(), 'absent018 controls disabled:' + name
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
                    for target in (18, 23, 22, 3):
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
              'scope': 'Exact three-clip018 native pixel/timing/control validation, including active-clip cache membership after each switch. No performance-saving measurement or human motion approval inferred.'}
    (review / record_name).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS three-clip018 native motion review and screenshots', flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--expected-html', type=Path)
    parser.add_argument('--base-url')
    parser.add_argument('--record-name', default='browser-validation.json')
    args = parser.parse_args()
    check(args.review, record_name=args.record_name, base_url=args.base_url, expected_html=args.expected_html)

