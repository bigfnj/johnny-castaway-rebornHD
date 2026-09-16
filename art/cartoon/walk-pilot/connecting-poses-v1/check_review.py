"""Static 009 viewer smoke, followed by pixel and control regression."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright


def require(ok, label):
    if not ok:
        raise ValueError(label)


def verify_pixels(page, data, feet, mirrored, which):
    actual = page.locator('#' + which).evaluate("c=>c.toDataURL('image/png').split(',')[1]")
    actual = Image.open(io.BytesIO(base64.b64decode(actual))).convert('RGB')
    source = Image.open(io.BytesIO(base64.b64decode(data[which].split(',')[1]))).convert('RGBA')
    zoom = 5 if feet else 4
    width, height = [n * zoom for n in data['canvas']]
    sprite = source.resize((width, height), Image.Resampling.NEAREST)
    if mirrored:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    x, y = (512 - width) // 2, -362 if feet else 16
    expected = Image.new('RGBA', (512, 640), (188, 200, 206, 255))
    expected.alpha_composite(sprite, (x, y))
    box = (x + 1, max(y + 1, 0), x + width - 1, min(y + height - 1, 640))
    diff = ImageChops.difference(actual.crop(box), expected.convert('RGB').crop(box))
    require(max(channel[1] for channel in diff.getextrema()) <= 2, 'canvas-' + which + '-009')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)
    parser.add_argument('--url')
    args = parser.parse_args()
    out = args.review.resolve()
    html = out / 'review.html'
    html_sha = hashlib.sha256(html.read_bytes()).hexdigest()
    data = json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>', html.read_text(encoding='utf-8'), re.S)[1])
    cases, errors = [], []
    print('WITNESS check_review.py SHA256=' + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), flush=True)
    if args.phase == 'regression':
        smoke = json.loads((out / 'browser-smoke.json').read_bytes())
        require(smoke['status'] == 'PASS' and smoke['html_sha256'] == html_sha, 'prior-smoke:' + str(html))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={'width': 1280, 'height': 1100}, device_scale_factor=1)
            page.on('pageerror', lambda error: errors.append(str(error)))
            response = page.goto(args.url or html.as_uri())
            require(response.body() == html.read_bytes(), 'exact-served-html:' + str(html))
            page.wait_for_function('window.reviewReady === true')
            require(not errors, 'page-errors:' + str(html))
            require(page.locator('#status').inner_text().startswith('Pose 009'), 'initial-pose:009:' + str(html))
            for name in ['identity017', 'identity003']:
                require(page.locator('#' + name).evaluate('img=>img.complete&&img.naturalHeight>0'), 'identity:' + name)
            cases.append({'smoke': 'exact HTML, image readiness, pose009, both approved references', 'status': 'PASS'})
            if args.phase == 'regression':
                for feet in [False, True]:
                    if page.locator('#feet').get_attribute('aria-pressed') != str(feet).lower():
                        page.click('#feet')
                    for mirrored in [False, True]:
                        if page.locator('#mirror').get_attribute('aria-pressed') != str(mirrored).lower():
                            page.click('#mirror')
                        for which in ['original', 'candidate']:
                            verify_pixels(page, data, feet, mirrored, which)
                        cases.append({'feet': feet, 'mirrored': mirrored, 'both_canvas_pixels': 'PASS'})
                page.click('#feet')
                page.click('#mirror')
                page.screenshot(path=str(out / 'whole-body009.png'), full_page=True)
                page.evaluate("images.candidate=document.getElementById('identity017');render();")
                failure = None
                try:
                    verify_pixels(page, data, False, False, 'candidate')
                except ValueError as error:
                    failure = str(error)
                require(failure == 'canvas-candidate-009', 'negative-control-wrong-pose:' + str(html))
                cases.append({'mutation': 'substitute approved017 for candidate009', 'status': 'FIRED', 'failure': failure})
            require(not errors, 'page-errors:' + str(html))
        finally:
            browser.close()
    result = {'status': 'PASS', 'phase': args.phase, 'url': args.url,
              'html_sha256': html_sha, 'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cases': cases, 'console_errors': errors,
              'scope': 'Static browser rendering only; no native capture or artistic approval.'}
    (out / ('browser-' + args.phase + '.json')).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
