"""Focused018 static browser smoke then exact crop, scene and served-byte regression."""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading
from PIL import Image
from playwright.sync_api import sync_playwright

sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);p.add_argument('--url');p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    assert not a.report.exists(), 'preserve browser check evidence'
    record=json.loads((a.review/'review-record.json').read_bytes());data=record['bundle']
    server=None
    if not a.url:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*_):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(a.review.resolve())))
        threading.Thread(target=server.serve_forever,daemon=True).start()
    url=a.url or f'http://127.0.0.1:{server.server_port}/review.html'
    errors=[];counts={'pixel_crops':0,'served_files':0,'detail_controls':0}
    try:
        with sync_playwright() as play:
            browser=play.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
                response=page.goto(url);assert response.status==200 and sha(response.body())==record['files_sha256']['review.html'], 'served018 HTML identity'
                page.wait_for_function('window.reviewReady===true')
                assert page.locator('article').count()==3 and page.evaluate('reviewData.draw')==[0,478,216,18], 'three initial018 panels'
                assert 'diagnostic palette' in page.locator('.intro').inner_text() and not errors, 'visible geometry-only palette scope'
                print('SMOKE PASS three loaded018 panels, fixed placement, explicit palette limitation',flush=True)
                for row in data['panels']:
                    with Image.open(a.review/row['image']) as im:
                        for kind in ('pose','feet'):
                            x,y,w,h=data[kind]
                            expected=im.convert('RGBA').crop((x,y,x+w,y+h)).tobytes()
                            got=page.locator('#'+row['kind']+'-'+kind).evaluate('(c)=>Array.from(c.getContext("2d").getImageData(0,0,c.width,c.height).data)')
                            assert bytes(got)==expected, 'exact fixed camera pixels:'+row['kind']+':'+kind
                            assert page.locator('#'+row['kind']+'-'+kind).evaluate('(c)=>getComputedStyle(c).imageRendering')=='pixelated', 'nearest-neighbor display'
                            counts['pixel_crops']+=1
                for name,digest in record['files_sha256'].items():
                    r=page.request.get(url.rsplit('/',1)[0]+'/'+name)
                    assert r.status==200 and sha(r.body())==digest, 'exact served018 file:'+name
                    counts['served_files']+=1
                page.screenshot(path=str(a.report.with_suffix('.png')),full_page=True)
                detail=page.locator('details').nth(1);detail.locator('summary').click()
                assert page.locator('.scene').count()==3 and all(page.locator('.scene').nth(i).is_visible() for i in range(3)), 'full scene expansion'
                for i,row in enumerate(data['panels']):
                    assert page.locator('.scene').nth(i).get_attribute('src')==row['image'], 'full scene source identity'
                detail.locator('summary').click();assert not page.locator('.scene').first.is_visible(), 'full scene collapse'
                counts['detail_controls']=2
                assert not errors, 'browser clean'
                print('REGRESSION PASS six exact camera crops, four served identities and full-scene expand/collapse',flush=True)
            finally:browser.close()
    finally:
        if server:server.shutdown();server.server_close()
    result={'status':'PASS','ordered_phases':['smoke','regression'],'url':url if a.url else 'ephemeral local HTTP server',
            'counts':counts,'html_sha256':record['files_sha256']['review.html'],'record_sha256':sha((a.review/'review-record.json').read_bytes()),
            'checker_sha256':sha(Path(__file__).read_bytes()),'screenshot_sha256':sha(a.report.with_suffix('.png').read_bytes()),'browser_errors':errors}
    a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
