"""Bounded browser pixel, native-timing and scene-control verification."""
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
    assert sha(review / 'review.html') == build['html_sha256'], 'review.html identity'
    assert sha(review / 'manifest.json') == build['manifest_sha256'], 'manifest.json identity'
    manifest = json.loads((review / 'manifest.json').read_bytes())
    if phase == 'regression':
        smoke = json.loads((review / 'browser-smoke.json').read_bytes())
        assert smoke['status'] == 'PASS' and smoke['html_sha256'] == build['html_sha256'] and smoke['manifest_sha256'] == build['manifest_sha256'], 'matching browser smoke first'
    server = None
    if url is None:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(review)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/review.html'
    errors, checks, shots = [], [], {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={'width':1400,'height':1100})
            page.on('pageerror', lambda error: errors.append(str(error)))
            if phase == 'regression':
                page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewTick=fn;return 1}')
            response = page.goto(url)
            assert response.status == 200 and response.body() == (review / 'review.html').read_bytes(), 'exact served HTML'
            page.wait_for_function('window.sceneReviewState?.ready||window.sceneReviewError', timeout=90000, polling=50)
            assert not page.evaluate('window.sceneReviewError'), 'initial scene load: ' + str(page.evaluate('window.sceneReviewError'))
            assert page.locator('#scene').input_value() == 'day/pumpkin' and page.locator('#speed').input_value() == '1', 'Pumpkin and Normal defaults'
            assert page.locator('#play').is_disabled() and not page.evaluate('sceneReviewState.playing'), 'still view is not animated'
            checks.append('Pumpkin still default; playback disabled; Normal speed')
            for side in ('baseline','candidate'):
                image = manifest['cases']['day/pumpkin']['frames'][0][side]
                with Image.open(ROOT / manifest['images'][image]['source']) as native:
                    x,y,w,h = manifest['cases']['day/pumpkin']['camera']
                    expected = hashlib.sha256(native.convert('RGBA').crop((x,y,x+w,y+h)).tobytes()).hexdigest()
                assert page.evaluate(HASH, side) == expected, 'exact default native pixels: ' + side
            checks.append('Exact default native pixels on both panels')
            shot = review / ('browser-' + phase + '-pumpkin.png')
            page.screenshot(path=str(shot), full_page=True)
            shots[shot.name] = sha(shot)
            if phase == 'smoke':
                page.locator('#scene').select_option('motion/high_clover')
                page.wait_for_function('sceneReviewState.ready&&sceneReviewState.key==="motion/high_clover"', timeout=90000, polling=50)
                page.wait_for_timeout(320)
                page.locator('#play').click()
                state = page.evaluate('sceneReviewState')
                assert state['index'] > 0 and not state['playing'], 'Normal timer and pause'
                old = state['index']
                page.locator('#next').click()
                assert page.evaluate('sceneReviewState.index') == old+1, 'next recorded frame'
                page.locator('#previous').click()
                assert page.evaluate('sceneReviewState.index') == old, 'previous recorded frame'
                page.locator('#speed').select_option('0.5')
                assert page.locator('#speed').input_value() == '0.5', 'Slow speed selection'
                checks.append('Normal timer, pause, next/previous and Slow controls')
            else:
                for key, clip in manifest['cases'].items():
                    page.locator('#scene').select_option(key)
                    page.wait_for_function('key=>(sceneReviewState.ready&&sceneReviewState.key===key)||window.sceneReviewError', arg=key, timeout=90000, polling=50)
                    assert not page.evaluate('window.sceneReviewError'), key+' load'
                    unique = {manifest['tiles'][tile]['atlas'] for row in clip['frames'] for side in ('baseline','candidate') for tile in manifest['images'][row[side]]['tiles']}
                    assert page.evaluate('sceneReviewState.cacheSize') == len(unique), key+' selected scene cache only'
                    if clip['kind'] == 'still':
                        assert page.locator('#play').is_disabled(), key+' held still'
                    else:
                        page.evaluate('setPlaying(false)')
                    page.locator('#view').select_option('full')
                    # Each displayed ordinal is checked, including zero-duration transitions.
                    for i,row in enumerate(clip['frames']):
                        page.evaluate('i=>selectFrame(i)', i)
                        for side in ('baseline','candidate'):
                            data = manifest['images'][row[side]]
                            native = ROOT / data['source']
                            assert sha(native) == data['sha256'], 'source PNG unchanged: '+data['source']
                            with Image.open(native) as image:
                                expected = hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
                            assert page.evaluate(HASH, side) == expected, f'{key} frame {i} {side} full native pixels'
                            assert page.locator('#'+side).get_attribute('data-time') == str(row['time_ms']), key+' recorded timestamp'
                    if clip['kind'] == 'motion':
                        for ms in sorted({r['time_ms'] for r in clip['frames']}):
                            expected = max(i for i,r in enumerate(clip['frames']) if r['time_ms']<=ms)
                            page.evaluate('ms=>sceneReviewSeek(ms)', ms)
                            assert page.evaluate('sceneReviewState.index') == expected, key+' native timestamp boundary'
                        page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);reviewTick(300)')
                        assert page.evaluate('sceneReviewState.time_ms') == 200, key+' Normal 200ms clock'
                        page.locator('#speed').select_option('0.5')
                        page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);reviewTick(300)')
                        assert page.evaluate('sceneReviewState.time_ms') == 100, key+' Slow 100ms clock'
                        page.locator('#speed').select_option('1')
                        page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);document.dispatchEvent(new Event("visibilitychange"));reviewTick(9000)')
                        assert page.evaluate('sceneReviewState.time_ms') == 0, key+' hidden-tab clock reset'
                        draws = page.evaluate('''()=>{sceneReviewSeek(0);let count=0;const previous=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(...args){count++;return previous.apply(this,args)};try{sceneReviewSeek(1)}finally{CanvasRenderingContext2D.prototype.drawImage=previous}return count}''')
                        assert draws == 0, key+' unchanged native frame does not redraw'
                        page.evaluate('sceneReviewSeek(clip.duration_ms);setPlaying(true);reviewTick(100);reviewTick(300)')
                        assert not page.evaluate('sceneReviewState.playing'), key+' stops on recorded endpoint'
                        assert page.get_by_role('button',name='Replay',exact=True).count() == 1 and page.locator('#play').inner_text() == 'Play', key+' endpoint has distinct Play and Replay buttons'
                    page.evaluate('selectFrame(0)')
                    page.locator('#view').select_option('island')
                    for side in ('baseline','candidate'):
                        data = manifest['images'][clip['frames'][0][side]]
                        with Image.open(ROOT / data['source']) as image:
                            x,y,w,h = clip['camera']
                            expected = hashlib.sha256(image.convert('RGBA').crop((x,y,x+w,y+h)).tobytes()).hexdigest()
                        assert page.evaluate(HASH, side) == expected, key+' shared island camera'
                    if key in ('day/tree','day/banner','motion/night_shift_clover'):
                        shot = review / ('browser-' + key.replace('/','-') + '.png')
                        page.screenshot(path=str(shot), full_page=True)
                        shots[shot.name] = sha(shot)
                    checks.append(key+': all native pixels, ordinals, timing, cameras and controls')
            assert not errors, errors
            record = {'status':'PASS','phase':phase,'html_sha256':build['html_sha256'],'manifest_sha256':build['manifest_sha256'],
                      'checker_sha256':sha(Path(__file__)),'checks':checks,'screenshots_sha256':shots,
                      'scope':'Exact native capture pixels reconstructed from unchanged crop tiles; actual timing and UI controls. No artwork approval.'}
            report.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
            print('PASS',phase,len(checks),'checks',sha(report))
        finally:
            browser.close()
            if server:
                server.shutdown()


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--review',type=Path,required=True)
    p.add_argument('--phase',choices=('smoke','regression'),required=True)
    p.add_argument('--report',type=Path)
    p.add_argument('--url')
    a=p.parse_args()
    check(a.review.resolve(),a.phase,a.report or a.review/('browser-'+a.phase+'.json'),a.url)
