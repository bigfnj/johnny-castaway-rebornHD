"""Native pixel and actual-loop checks for the bounded banner viewer."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'CMakeLists.txt').is_file())
HASH="""async side=>{const c=document.getElementById(side),data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(v=>v.toString(16).padStart(2,'0')).join('')}"""
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check(review,phase,report,url=None):
    assert not report.exists(),'fresh browser report required'
    build=json.loads((review/'build.json').read_bytes());manifest=json.loads((review/'manifest.json').read_bytes())
    assert sha(review/'review.html')==build['html_sha256'] and sha(review/'manifest.json')==build['manifest_sha256'],'page identity'
    if phase=='regression':
        smoke=json.loads((review/'browser-smoke.json').read_bytes())
        assert smoke['status']=='PASS' and smoke['html_sha256']==build['html_sha256'] and smoke['manifest_sha256']==build['manifest_sha256'],'matching smoke first'
    server=None
    if url is None:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(review)))
        threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/review.html'
    checks=[];errors=[];shots={}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={'width':1400,'height':1000})
            page.on('pageerror',lambda error:errors.append(str(error)))
            if phase=='regression':page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewTick=fn;return 1}')
            response=page.goto(url)
            assert response.status==200 and response.body()==(review/'review.html').read_bytes(),'exact served HTML'
            page.wait_for_function('window.sceneReviewState?.ready||window.sceneReviewError',timeout=60000,polling=50)
            assert not page.evaluate('window.sceneReviewError'),'initial load error'
            assert page.locator('#scene').input_value()=='day_banner' and page.locator('#view').input_value()=='banner' and page.locator('#speed').input_value()=='1','day/banner/Normal defaults'
            checks.append('Day, both banner ends and Normal speed defaults')
            page.evaluate('selectFrame(0)')
            def exact(key,index,view):
                row=manifest['cases'][key]['frames'][index]
                crop=manifest['cases'][key]['views'][view]
                for side in ('baseline','candidate'):
                    source=manifest['images'][row[side]]
                    assert sha(ROOT/source['source'])==source['sha256'],'native source identity'
                    with Image.open(ROOT/source['source']) as im:
                        x,y,w,h=crop;digest=hashlib.sha256(im.convert('RGBA').crop((x,y,x+w,y+h)).tobytes()).hexdigest()
                    assert page.evaluate(HASH,side)==digest,f'{key}/{index}/{view}/{side}: exact native pixels'
                    assert page.locator('#'+side).get_attribute('data-time')==str(row['time_ms']),'actual native timestamp'
            exact('day_banner',0,'banner');checks.append('Both default panels reconstruct exact native pixels')
            screenshot=review/('browser-'+phase+'-banner.png');page.screenshot(path=str(screenshot),full_page=True);shots[screenshot.name]=sha(screenshot)
            if phase=='smoke':
                page.locator('#play').click();page.wait_for_timeout(320);page.locator('#play').click()
                old=page.evaluate('sceneReviewState.index');assert old>0 and not page.evaluate('sceneReviewState.playing'),'actual timer and pause'
                page.locator('#next').click();assert page.evaluate('sceneReviewState.index')==old+1,'next'
                page.locator('#previous').click();assert page.evaluate('sceneReviewState.index')==old,'previous'
                page.locator('#view').select_option('waves');exact('day_banner',old,'waves')
                page.locator('#view').select_option('island');exact('day_banner',old,'island')
                checks.append('Normal playback, pause, stepping, wave closeup and whole island')
            else:
                for key,clip in manifest['cases'].items():
                    page.locator('#scene').select_option(key)
                    page.wait_for_function('key=>(sceneReviewState.ready&&sceneReviewState.key===key)||window.sceneReviewError',arg=key,timeout=60000,polling=50)
                    assert not page.evaluate('window.sceneReviewError'),key+' load'
                    page.evaluate('setPlaying(false)');page.locator('#view').select_option('full')
                    for i,row in enumerate(clip['frames']):
                        page.evaluate('i=>selectFrame(i)',i);exact(key,i,'full')
                    for view in ('banner','island','waves'):
                        page.evaluate('selectFrame(0)');page.locator('#view').select_option(view);exact(key,0,view)
                    for ms in sorted({r['time_ms'] for r in clip['frames']}):
                        page.evaluate('ms=>sceneReviewSeek(ms)',ms)
                        assert page.evaluate('sceneReviewState.index')==max(i for i,r in enumerate(clip['frames']) if r['time_ms']<=ms),'native time boundary'
                    page.evaluate('sceneReviewSeek(1400);setPlaying(true);reviewTick(100);reviewTick(300)')
                    assert page.evaluate('sceneReviewState.time_ms')==160 and page.evaluate('sceneReviewState.playing'),'actual 1440 ms loop'
                    page.locator('#speed').select_option('0.5')
                    page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);reviewTick(300)')
                    assert page.evaluate('sceneReviewState.time_ms')==100,'Slow clock'
                    page.locator('#speed').select_option('1')
                    page.evaluate('sceneReviewSeek(0);setPlaying(true);reviewTick(100);document.dispatchEvent(new Event("visibilitychange"));reviewTick(9000)')
                    assert page.evaluate('sceneReviewState.time_ms')==0,'hidden-tab clock reset'
                    draws=page.evaluate('''()=>{sceneReviewSeek(0);let count=0;const old=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(...args){count++;return old.apply(this,args)};try{sceneReviewSeek(1)}finally{CanvasRenderingContext2D.prototype.drawImage=old}return count}''')
                    assert draws==0,'unchanged frame does not redraw'
                    page.evaluate('selectFrame(clip.frames.length-1)')
                    assert page.locator('#play').inner_text()=='Play' and page.get_by_role('button',name='Replay',exact=True).count()==1,'distinct endpoint buttons'
                    page.evaluate('selectFrame(0)');page.locator('#view').select_option('banner')
                    shot=review/('browser-'+key+'.png');page.screenshot(path=str(shot),full_page=True);shots[shot.name]=sha(shot)
                    checks.append(key+': all native frames/timestamps, four cameras, 1440 ms loop and controls')
            assert not errors,errors
            result={'status':'PASS','phase':phase,'html_sha256':build['html_sha256'],'manifest_sha256':build['manifest_sha256'],
                    'checker_sha256':sha(Path(__file__)),'checks':checks,'screenshots_sha256':shots,'scope':'Pixel/timing/UI verification, not human attachment approval.'}
            report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS',phase,len(checks),'checks',sha(report))
        finally:
            browser.close()
            if server:server.shutdown()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);p.add_argument('--phase',choices=('smoke','regression'),required=True);p.add_argument('--report',type=Path);p.add_argument('--url')
    a=p.parse_args();check(a.review.resolve(),a.phase,a.report or a.review/('browser-'+a.phase+'.json'),a.url)
