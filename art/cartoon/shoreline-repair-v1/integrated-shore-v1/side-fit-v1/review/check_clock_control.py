"""Execute the previously wrong low-tide loop setting against the actual viewer."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import shutil
import threading
from playwright.sync_api import sync_playwright
import build_review as b

def endpoint(page, url):
    page.goto(url)
    page.wait_for_function('sceneReviewState.ready', polling=50)
    page.locator('#scene').select_option('low_clover')
    page.wait_for_function("sceneReviewState.ready&&sceneReviewState.key==='low_clover'",polling=50)
    page.evaluate('sceneReviewSeek(2840);setPlaying(true);reviewTick(100);reviewTick(300)')
    return page.evaluate('({time_ms:sceneReviewState.time_ms,playing:sceneReviewState.playing,index:sceneReviewState.index})')

def run(review, work):
    assert not work.exists(), 'fresh clock control output'
    work.mkdir(parents=True)
    original=json.loads((review/'manifest.json').read_bytes())
    assert original['cases']['low_clover']['duration_ms']==2880 and not original['cases']['low_clover']['loop']
    for label in ('positive','wrong-loop'):
        dest=work/label
        dest.mkdir()
        for name in ('review.html','manifest.json',*original['atlases']):
            shutil.copyfile(review/name,dest/name)
    changed=json.loads((work/'wrong-loop/manifest.json').read_bytes())
    changed['cases']['low_clover']['loop']=True
    b.save(work/'wrong-loop/manifest.json',changed)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(work)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                observed={}
                for label in ('positive','wrong-loop','positive'):
                    page=browser.new_page()
                    page.add_init_script('window.requestAnimationFrame=fn=>{window.reviewTick=fn;return 1}')
                    value=endpoint(page,f'http://127.0.0.1:{server.server_port}/{label}/review.html')
                    page.close()
                    if label=='wrong-loop':
                        try:
                            assert value['time_ms']==2880 and not value['playing'], 'low tide must stop at full captured endpoint'
                        except AssertionError as exc:
                            observed['mutation']={'status':'FIRED','failure':str(exc),'actual':value}
                        else:raise AssertionError('wrong low-tide loop survived')
                    else:
                        assert value['time_ms']==2880 and not value['playing'], 'restored low-tide endpoint'
                        observed['restored_positive' if 'mutation' in observed else 'positive']=value
            finally:browser.close()
    finally:
        server.shutdown()
        server.server_close()
    b.save(work/'result.json',{'status':'PASS','html_sha256':b.sha(review/'review.html'),
          'manifest_sha256':b.sha(review/'manifest.json'),'mutant_manifest_sha256':b.sha(work/'wrong-loop/manifest.json'),
          'checker_sha256':b.sha(Path(__file__)),'observed':observed,
          'method':'Actual headless page, fresh page per case, deterministic public animation clock. Only scratch manifest low-tide loop flag changes.'})
    print('PASS low-tide loop negative and restored control',b.sha(work/'result.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--review',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    run(a.review.resolve(),a.work.resolve())
