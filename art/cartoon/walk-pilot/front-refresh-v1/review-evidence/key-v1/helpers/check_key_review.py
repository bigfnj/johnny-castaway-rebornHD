import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[7]
ART=ROOT/'art/cartoon/walk-pilot/front-refresh-v1/review-evidence/key-v1'
URL='http://127.0.0.1:8932/front-refresh-028-v1/review.html'
parser=argparse.ArgumentParser()
parser.add_argument('--phase',choices=['smoke','regression'],required=True)
args=parser.parse_args()
checks=[]
def check(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1280,'height':900})
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    response=page.goto(URL)
    page.evaluate('window.reviewReady')
    check(response.status==200,'served-page-200')
    check(response.body()==(ART/'review.html').read_bytes(),'served-html-exact-bytes')
    check(page.locator('canvas').count()==3 and not errors,'three-canvases-no-page-errors')
    if args.phase=='regression':
        for width in [1280,1600,700]:
            page.set_viewport_size({'width':width,'height':900})
            for key in ['original','approved','candidate']:
                visible=page.locator('#'+key).bounding_box()
                check(visible['x']>=0 and visible['x']+visible['width']<=width+.1,f'whole-pose-visible-{width}-{key}')
                check(abs(visible['width']/visible['height']-.5)<.002,f'whole-pose-aspect-{width}-{key}')
        page.set_viewport_size({'width':1280,'height':900})
        before={key:page.locator('#'+key).evaluate('(c)=>c.toDataURL()') for key in ['original','approved','candidate']}
        for key,data in before.items():
            actual=Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA')
            source=Image.open(ART/(key+'.png')).convert('RGBA')
            expected=source.resize((320,640),Image.Resampling.NEAREST)
            # Canvas roundtrips straight alpha through premultiplied bytes.
            for background in [(255,255,255,255),(40,100,160,255)]:
                a=Image.alpha_composite(Image.new('RGBA',actual.size,background),actual)
                b=Image.alpha_composite(Image.new('RGBA',expected.size,background),expected)
                extrema=Image.frombytes('RGBA',a.size,bytes(abs(x-y) for x,y in zip(a.tobytes(),b.tobytes()))).getextrema()
                check(max(v[1] for v in extrema)<=1,f'canvas-source-composition-{key}-{background[0]}')
        page.get_by_role('button',name='Shorts and feet',exact=True).click()
        check(page.locator('#feet').get_attribute('aria-pressed')=='true','closeup-button-state')
        for key in before:
            check(page.locator('#'+key).evaluate('(c)=>c.height')==348,f'closeup-no-stretch-{key}')
            check(page.locator('#'+key).evaluate('(c)=>c.toDataURL()')!=before[key],f'closeup-changes-view-{key}')
        page.get_by_role('button',name='Whole pose',exact=True).click()
        check(all(page.locator('#'+key).evaluate('(c)=>c.toDataURL()')==value for key,value in before.items()),'whole-pose-restores-exact')
        check(not errors,'no-browser-errors-after-controls')
        page.screenshot(path=str(ART/'review-1280.png'))
    browser.close()
report={'phase':args.phase,'url':URL,'passed':checks,'count':len(checks)}
(ART/('browser-'+args.phase+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))

