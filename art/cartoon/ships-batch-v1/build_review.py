"""Build the static combined art gallery and bind its selected raw files."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = HERE.parent
VERSIONS = {**{("SHIPS.BMP", n): 2 for n in (4, 5, 15)}, **{("TANKER.BMP", n): 2 for n in (3, 4, 5, 6, 10, 11, 12)}}
GROUPS = [
    ("tanker", "Tanker views", "TANKER.BMP", range(14), "tanker-v1"),
    ("prow", "Close-up hull pieces", "GJPROW.BMP", range(2), "tanker-v1"),
    ("ships", "Sailing ships and separate hull sections", "SHIPS.BMP", range(10), "ships-v1"),
    ("effects", "Cannon flashes, smoke and projectiles", "SHIPS.BMP", range(14, 21), "ships-v1"),
]
SHIP_NAMES = ["Small source shape (role unconfirmed)", "Small source shape (role unconfirmed)", "Small source shape (role unconfirmed)", "Lower hull and water", "Lower hull and water", "Lower hull and water", "Lower hull and water", "Upper ship section", "Complete sailing ship", "Complete sailing ship"]
EFFECT_NAMES = {14: "Cannon flash", 15: "Cannon flash", 16: "Cannon flash", 17: "Smoke puff", 18: "Tiny projectile", 19: "Cannonball", 20: "Small cannonball"}

def ident(path):
    result = dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    if path.suffix == ".png":
        with Image.open(path) as im:
            result.update(canvas=list(im.size), mode=im.mode)
            if im.mode == "RGBA":
                result["alpha_range"] = list(im.getchannel("A").getextrema())
    return result

def url(path):
    return html.escape(os.path.relpath(path, HERE).replace(os.sep, "/"), quote=True)

def card(resource, n, name, raw, original, preserved=False):
    frame = f"{n:03}"
    label = f"{resource}{frame}"
    detail = "Exact original, retained unchanged" if preserved else "Open full drawing"
    return f'''<figure id="{resource.lower()}-{frame}"><figcaption>{html.escape(name)} <span>{label}</span></figcaption>
<a class="art{' preserved' if preserved else ''}" href="{url(raw)}" target="_blank" rel="noopener" aria-label="{detail}: {label}"><img src="{url(raw)}" alt="{html.escape(name)} {label}"></a>
<small>{detail}</small><details><summary>Compare original</summary><div class="original"><img src="{url(original)}" alt="Original {label}"></div></details></figure>'''

def main():
    assets, sections, nav = [], [], []
    for anchor, title, resource, numbers, family in GROUPS:
        cards = []
        nav.append(f'<a href="#{anchor}">{title} ({len(numbers)})</a>')
        for n in numbers:
            frame = f"{n:03}"
            folder = ART / family
            generation = folder / "generation" / resource if family == "tanker-v1" else folder / "generation"
            version = VERSIONS.get((resource, n), 1)
            raw = generation / f"{frame}-generated-v{version}.png"
            original = folder / "reference/original" / resource / f"{frame}.png" if family == "tanker-v1" else folder / f"reference/original/{frame}.png"
            name = f"View {frame}" if resource == "TANKER.BMP" else ("Anchor hull panel" if n == 0 else "Tapered hull continuation") if resource == "GJPROW.BMP" else SHIP_NAMES[n] if n < 10 else EFFECT_NAMES[n]
            requests = sorted(generation.glob(f"{frame}-*request*.json"))
            assets.append(dict(resource=resource, frame=frame, kind="generated_draft", selected_raw=ident(raw), original_reference=ident(original), requests=[ident(p) for p in requests]))
            cards.append(card(resource, n, name, raw, original))
        extra = '<p>The upper and lower sections join in the application. Their fit will be checked during bulk integration.</p>' if anchor == "ships" else ""
        sections.append(f'<section><h2 id="{anchor}">{title}</h2>{extra}<div class="grid {anchor}">{chr(10).join(cards)}</div></section>')
    cards = []
    for n in range(10, 14):
        raw = ART / f"ships-v1/source-preserved/{n:03}.png"
        original = ART / f"ships-v1/reference/original/{n:03}.png"
        assets.append(dict(resource="SHIPS.BMP", frame=f"{n:03}", kind="source_preserved", selected_raw=ident(raw), original_reference=ident(original), requests=[]))
        cards.append(card("SHIPS.BMP", n, "One-pixel source slot", raw, original, True))
    sections.append('<section><h2 id="preserved">Four source slots kept unchanged</h2><p>These original files each contain one black pixel. Their role is still unconfirmed, so they are retained as supplied.</p><div class="grid preserved-grid">'+"\n".join(cards)+"</div></section>")
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>33 Cartoon ship drawings</title><style>
*{box-sizing:border-box}body{margin:0;padding:24px;background:#152731;color:#edf4f7;font:16px system-ui,sans-serif}main{max-width:1500px;margin:auto}h1{margin:0 0 12px;font-size:30px}h2{margin:36px 0 16px;scroll-margin-top:18px}p{line-height:1.55;color:#c9dce5;max-width:1080px}nav,.controls{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}nav a,button{padding:10px 15px;border:0;border-radius:6px;background:#d8eaf3;color:#142c3a;font:inherit;text-decoration:none;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.tanker,.prow{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;background:#243e4c;padding:15px;border-radius:10px}figcaption{font-size:19px;font-weight:650;margin-bottom:12px}figcaption span{display:block;margin-top:5px;font-size:14px;font-weight:450;color:#c9dce5}.art{display:block;height:310px;background-color:#f6f2e8;background-image:repeating-conic-gradient(#e4dfd4 0% 25%,transparent 0% 50%);background-size:24px 24px}.tanker .art{height:245px}.prow .art{height:360px}.art img{display:block;width:100%;height:100%;object-fit:contain}.art.preserved{height:70px}.art.preserved img{width:128px;height:16px;position:relative;top:27px;margin:auto;image-rendering:pixelated}.dark .art{background-color:#17232a;background-image:repeating-conic-gradient(#233540 0% 25%,transparent 0% 50%)}small{display:block;color:#c9dce5;margin-top:8px}details{margin-top:12px}summary{cursor:pointer}.original{margin-top:12px;background:#e8e8de;padding:14px;display:flex;justify-content:center;align-items:center;height:160px}.original img{width:100%;height:100%;object-fit:contain;image-rendering:pixelated}.preserved-grid .original{height:60px}.preserved-grid .original img{width:128px;height:16px}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){body{padding:14px}.grid{grid-template-columns:1fr}}
</style></head><body><main><h1>33 Cartoon ship drawings in one review</h1><p>Review the tanker directions, hull pieces, sailing ships and small effects. Use the frame numbers to flag exceptions. Click any drawing for its full image.</p><p>This is an artwork review. Final size, joined parts and motion will be checked during bulk integration. Original colors below are diagnostic; their shapes guide the redraws.</p>
<nav aria-label="Artwork groups">'''+"".join(nav)+'''</nav><div class="controls"><button id="originals" aria-pressed="false">Show all originals</button><button id="background" aria-pressed="false">Use dark checkerboard</button></div>'''+"\n".join(sections)+'''</main><script>
const originals=document.getElementById('originals');originals.addEventListener('click',()=>{const open=originals.getAttribute('aria-pressed')!=='true';document.querySelectorAll('details').forEach(d=>{d.open=open});originals.setAttribute('aria-pressed',String(open));originals.textContent=open?'Hide all originals':'Show all originals'});
const background=document.getElementById('background');background.addEventListener('click',()=>{const dark=document.body.classList.toggle('dark');background.setAttribute('aria-pressed',String(dark));background.textContent=dark?'Use light checkerboard':'Use dark checkerboard'});
</script></body></html>'''
    output = HERE / "review.html"
    output.write_text(page, encoding="utf-8")
    record = dict(schema_version=1, status="awaiting_batch_appearance_review", date="2026-09-17", generated_drawing_count=33, preserved_source_slot_count=4, total_slots=37,
                  reviewed_url="http://127.0.0.1:8941/ships-batch-v1/review.html", page=ident(output), assets=assets,
                  source_records=[ident(ART / f"{f}/reference/source.json") for f in ["ships-v1", "tanker-v1"]],
                  production_archive=ident(ROOT / "assets/scrantic_data.zip"), visual_approval=None, production_acceptance=False,
                  human_question="The 33-drawing ship review is open at http://127.0.0.1:8941/ships-batch-v1/review.html. Does the artwork look right? You can approve the group or list exceptions by resource and frame number. Final size and motion remain part of bulk integration.",
                  production_package_changed=False, export_executed=False,
                  deferred_work=["Original-canvas fitting and registration", "Joined upper/lower ship sections", "Native yaw/water/effect timing", "Bulk smoke and regressions"])
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(f"Wrote gallery: {len(assets)} slots, 33 new drawings, 4 source-preserved")

if __name__ == "__main__":
    main()
