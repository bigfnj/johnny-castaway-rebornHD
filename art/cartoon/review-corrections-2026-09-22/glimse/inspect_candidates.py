import json
from pathlib import Path
from playwright.sync_api import sync_playwright

here = Path(__file__).resolve().parent
manifest = json.loads((here / 'manifest.json').read_text(encoding='utf-8'))
rows = [e for e in manifest['entries'] if e['output']]
cards = []
for e in rows:
    name = Path(e['output']).name
    cards.append(f'<section><h2>SMGLIMSE {e["frame"]}</h2><div class="pair"><div class="light"><img src="{name}"></div><div class="dark"><img src="{name}"></div></div></section>')
html = '<!doctype html><meta charset="utf-8"><title>Glimse light and dark inspection</title><style>body{margin:16px;background:#666;color:white;font:16px sans-serif}h2{margin:8px}section{margin-bottom:20px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pair>div{display:flex;align-items:center;justify-content:center;height:380px}.light{background:#f8f4ed}.dark{background:#233640}img{max-width:100%;max-height:100%;object-fit:contain}</style>' + ''.join(cards)
(here / 'inspection.html').write_text(html, encoding='utf-8')
url = 'http://127.0.0.1:8941/review-corrections-2026-09-22/glimse/inspection.html'
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page(viewport={'width': 1800, 'height': 1900}, device_scale_factor=1)
    page.goto(url)
    page.wait_for_function('Array.from(document.images).every(im=>im.complete && im.naturalWidth>0)')
    page.screenshot(path=str(here / 'light-dark-inspection.png'), full_page=True)
    print(json.dumps({'url': url, 'image_count': page.locator('img').count(), 'screenshot': str(here / 'light-dark-inspection.png')}))
    browser.close()
