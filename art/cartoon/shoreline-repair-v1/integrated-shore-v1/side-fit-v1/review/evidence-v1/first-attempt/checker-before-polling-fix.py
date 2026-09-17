"""Exact native pixels, clocks and simple controls for the combined wave viewer."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
HASH = """async side=>{const c=document.getElementById(side),data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(v=>v.toString(16).padStart(2,'0')).join('')}"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(review, phase, report, url=None):
    assert not report.exists(), 'fresh browser report required'
    build = json.loads((review / 'build.json').read_bytes())
    manifest = json.loads((review / 'manifest.json').read_bytes())
    assert sha(review / 'review.html') == build['html_sha256'] and sha(review / 'manifest.json') == build['manifest_sha256'], 'page identity'
    if phase == 'regression':
        smoke = json.loads((review / 'browser-smoke.json').read_bytes())
        assert smoke['status'] == 'PASS' and smoke['html_sha256'] == build['html_sha256'] and smoke['manifest_sha256'] == build['manifest_sha256'], 'matching smoke first'
    server = None
    if url is None:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(review)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/review.html'
    checks, errors, shots = [], [], {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={'width':1280, 'height':900})
            page.on('pageerror', lambda error: errors.append(str(error)))
            if phase == 'regression':
                page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewTick=fn;return 1}')
            response = page.goto(url)
            assert response.status == 200 and response.body() == (review / 'review.html').read_bytes(), 'exact served HTML'
            page.wait_for_function('window.sceneReviewState?.ready||window.sceneReviewError', timeout=60000)
            assert not page.evaluate('window.sceneReviewError'), 'initial load error'
            assert page.locator('#scene').input_value() == 'high_clover' and page.locator('#view').input_value() == 'waves' and page.locator('#speed').input_value() == '1', 'high/shore/Normal defaults'
            assert page.evaluate('sceneReviewState.index===0&&!sceneReviewState.playing&&sceneReviewState.time_ms===0'), 'initial007 paused at0'
            assert manifest['cases']['high_clover']['frames'][0]['phases'] == [3,7,9,-1], 'corrected007 initial phase'
            checks.append('Defaults show old dark007 versus clean007 at time0, Normal speed')
            def exact(key, index, view):
                row = manifest['cases'][key]['frames'][index]
                x,y,w,h = manifest['cases'][key]['views'][view]
                for side in ('baseline','candidate'):
                    source = manifest['images'][row[side]]
                    assert sha(ROOT / source['source']) == source['sha256'], 'native source identity'
                    with Image.open(ROOT / source['source']) as im:
                        digest = hashlib.sha256(im.convert('RGBA').crop((x,y,x+w,y+h)).tobytes()).hexdigest()
                    assert page.evaluate(HASH, side) == digest, f'{key}/{index}/{view}/{side}: exact native pixels'
                    assert page.locator('#'+side).get_attribute('data-time') == str(row['time_ms']), 'recorded native timestamp'
            def screenshot(name):
                path = review / name
                page.screenshot(path=str(path), full_page=True)
                shots[name] = sha(path)
            exact('high_clover',0,'waves')
            screenshot('browser-'+phase+'-1280.png')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'no horizontal overflow at1280'
            for side in ('baseline','candidate'):
                box = page.locator('#'+side).bounding_box()
                assert box['y']+box['height'] <= 900 and box['width'] >= 550, 'both whole-shore panels visible at1280'
            checks.append('Exact default native crops and both panels visible at1280x900')
            if phase == 'smoke':
                page.locator('#play').click()
                page.wait_for_timeout(360)
                page.locator('#play').click()
                old = page.evaluate('sceneReviewState.index')
                assert old > 0 and not page.evaluate('sceneReviewState.playing'), 'real Normal playback and pause'
                page.locator('#next').click()
                assert page.evaluate('sceneReviewState.index') == old+1, 'next frame'
                page.locator('#previous').click()
                assert page.evaluate('sceneReviewState.index') == old, 'previous frame'
                page.locator('#first').click()
                assert page.evaluate('sceneReviewState.index') == 0, 'corrected phase shortcut'
                page.locator('#view').select_option('center')
                exact('high_clover',0,'center')
                screenshot('browser-center007-1280.png')
                checks.append('Real playback, pause, stepping and clean007 shortcut')
            else:
                for key, clip in manifest['cases'].items():
                    page.locator('#scene').select_option(key)
                    page.wait_for_function('key=>(sceneReviewState.ready&&sceneReviewState.key===key)||window.sceneReviewError', arg=key, timeout=60000)
                    assert not page.evaluate('window.sceneReviewError'), key+' load'
                    assert not page.evaluate('sceneReviewState.playing'), 'scene switch resets playback clock'
                    page.locator('#view').select_option('full')
                    for index, row in enumerate(clip['frames']):
                        page.evaluate('i=>selectFrame(i)', index)
                        exact(key,index,'full')
                    for view in ('waves','center','island'):
                        page.evaluate('selectFrame(0)')
                        page.locator('#view').select_option(view)
                        exact(key,0,view)
                    for ms in sorted({r['time_ms'] for r in clip['frames']}):
                        page.evaluate('ms=>sceneReviewSeek(ms)', ms)
                        assert page.evaluate('sceneReviewState.index') == max(i for i,r in enumerate(clip['frames']) if r['time_ms']<=ms), 'native time boundary'
                    duration = clip['duration_ms']
                    page.evaluate('ms=>{sceneReviewSeek(ms-40);setPlaying(true);reviewTick(100);reviewTick(300)}', duration)
                    if clip['loop']:
                        assert page.evaluate('sceneReviewState.time_ms') == 160 and page.evaluate('sceneReviewState.playing'), 'actual selected cycle clock'
                    else:
                        assert page.evaluate('sceneReviewState.time_ms') == duration and not page.evaluate('sceneReviewState.playing'), 'route stops at recorded endpoint'
                    if key == 'low_clover':
                        assert duration > 1440 and duration == clip['recorded_duration_ms'], 'low tide not truncated'
                        assert {f for r in clip['frames'] for f in r['phases'] if f>=0} == set(range(30,42)), 'all12 low phases'
                    page.locator('#speed').select_option('0.5')
                    page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);reviewTick(300)')
                    assert page.evaluate('sceneReviewState.time_ms') == 100, 'Slow clock'
                    page.locator('#speed').select_option('1')
                    page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);document.dispatchEvent(new Event("visibilitychange"));reviewTick(9000)')
                    assert page.evaluate('sceneReviewState.time_ms') == 0, 'hidden tab clock resets'
                    page.evaluate('selectFrame(clip.frames.length-1)')
                    page.locator('#replay').click()
                    assert page.evaluate('sceneReviewState.index===0&&sceneReviewState.playing'), 'replay starts at0'
                    page.evaluate('selectFrame(0)')
                    page.locator('#view').select_option('waves' if not key.startswith('johnny') else 'island')
                    screenshot('browser-'+key+'.png')
                    checks.append(key+': every native frame, timing boundary, cameras, cycle/end, Slow and replay')
                page.evaluate("choose('high_clover');choose('night_shift_clover')")
                page.wait_for_function("sceneReviewState.ready&&sceneReviewState.key==='night_shift_clover'")
                page.evaluate('selectFrame(0)')
                page.locator('#view').select_option('waves')
                exact('night_shift_clover',0,'waves')
                checks.append('Rapid selection discards obsolete load and displays final selected clip')
            assert not errors, errors
            result = {'status':'PASS','phase':phase,'html_sha256':build['html_sha256'],
                      'manifest_sha256':build['manifest_sha256'],'checker_sha256':sha(Path(__file__)),
                      'checks':checks,'screenshots_sha256':shots,
                      'scope':'Exact native pixel, timing and viewer controls; human artwork approval remains separate.'}
            report.write_bytes((json.dumps(result,indent=2)+'\n').encode())
            print('PASS',phase,len(checks),'checks',sha(report))
        finally:
            browser.close()
            if server:
                server.shutdown()
                server.server_close()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--review',type=Path,required=True)
    p.add_argument('--phase',choices=('smoke','regression'),required=True)
    p.add_argument('--report',type=Path)
    p.add_argument('--url')
    a = p.parse_args()
    check(a.review.resolve(),a.phase,a.report or a.review/('browser-'+a.phase+'.json'),a.url)
