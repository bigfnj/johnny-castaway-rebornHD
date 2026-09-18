"""Build a 28-drawing appearance review with isolated source-phase playback.

Raw PNGs are never rewritten. Browser fitting is provisional, uniform and
bottom-centered within each original sprite's occupied bounds.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERSIONS = {0: 3, 1: 2, 13: 2, 15: 2, 23: 2}
GROUPS = [
    ("wood", "Wood and embers", [0, 21, 22, 23, 24, 25, 26]),
    ("smoke", "Smoke wisps", list(range(1, 5))),
    ("small", "Small flames", list(range(5, 9))),
    ("medium", "Medium flames", list(range(9, 13))),
    ("large", "Large flames", list(range(13, 17))),
    ("very-large", "Very large flames", list(range(17, 21))),
    ("burst", "Fire-pop graphic", [27]),
]


def ident(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def measure(path):
    result = ident(path)
    with Image.open(path) as im:
        alpha = im.convert("RGBA").getchannel("A")
        result.update(canvas=list(im.size), mode=im.mode,
                      alpha_range=list(alpha.getextrema()), alpha_bounds=alpha.getbbox(),
                      alpha8_bounds=alpha.point(lambda a: 255 if a >= 8 else 0).getbbox())
    return result


def main():
    assets = []
    cards = []
    nav = []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        figures = []
        for n in frames:
            raw = HERE / f"generation/{n:03}-generated-v{VERSIONS.get(n, 1)}.png"
            original = HERE / f"reference/original/{n:03}.png"
            a = dict(frame=n, group=group, selected_raw=measure(raw), original=measure(original),
                     raw_url=raw.relative_to(HERE).as_posix(), original_url=original.relative_to(HERE).as_posix(),
                     requests=[ident(p) for p in sorted((HERE / "generation").glob(f"{n:03}-*request*.json"))],
                     records=[ident(p) for p in sorted((HERE / "generation").glob(f"{n:03}-record*.json"))])
            assets.append(a)
            figures.append(f'<figure id="frame-{n:03}"><figcaption>FIRE1 / {n:03}</figcaption>'
                           f'<a href="{a["raw_url"]}" target="_blank" rel="noopener" aria-label="Open full drawing {n:03}">'
                           f'<canvas class="thumb check" width="540" height="360" data-frame="{n}" aria-label="Cartoon drawing {n:03}"></canvas></a>'
                           f'<details><summary>Compare original {n:03}</summary><div class="original check"><img src="{a["original_url"]}" alt="Original FIRE1 frame {n:03}"></div></details></figure>')
        note = '<p>Frame 025 is retained even though its draw site is not identified in the saved scene map.</p>' if group == "wood" else ""
        cards.append(f'<section><h2 id="{group}">{title}</h2>{note}<div class="grid">{"".join(figures)}</div></section>')
    sequences = json.loads((HERE / "reference/phase-sequences.json").read_text(encoding="utf-8"))
    cycles = [s for s in sequences["sequences"] if s["id"] in ["smoke", "small_flames", "medium_flames", "large_flames", "very_large_flames"]]
    options = "".join(f'<option value="{s["id"]}"'+(' selected' if s["id"] == "large_flames" else '')+f'>{s["description"].capitalize()}</option>' for s in cycles)
    data = dict(assets=sorted(assets, key=lambda a: a["frame"]), cycles=cycles,
                fitting="Uniform contain into original alpha bounds, bottom centered; provisional review fitting only.",
                crop=[288, 253, 50, 72])
    (HERE / "review-data.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    page = template.replace("{{NAV}}", "".join(nav)).replace("{{OPTIONS}}", options).replace("{{CARDS}}", "\n".join(cards))
    (HERE / "review.html").write_text(page, encoding="utf-8")
    record = dict(schema_version=1, date="2026-09-18", status="awaiting_batch_appearance_review",
                  generated_drawing_count=28, resource="FIRE1.BMP", page=ident(HERE / "review.html"),
                  browser_script=ident(HERE / "review.js"), data=ident(HERE / "review-data.json"), assets=data["assets"],
                  source=ident(HERE / "reference/source.json"), phase_source=ident(HERE / "reference/phase-sequences.json"),
                  production_archive=ident(ROOT / "assets/scrantic_data.zip"), visual_approval=None,
                  production_acceptance=False, export_executed=False, raw_pixel_processing=False,
                  review_url="http://127.0.0.1:8941/fire-v1/review.html",
                  timing="Isolated source-derived phase order, positions and nominal 140 ms timing; editorial repetition.",
                  fit=data["fitting"], deferred_work=["Native registration and visual size", "Johnny/fire interactions and story timing", "Dying-fire and clipped ember scenes", "Bulk smoke and regression tests"])
    (HERE / "review-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Built 28-drawing review with five source-derived phase comparisons.")


if __name__ == "__main__":
    main()
