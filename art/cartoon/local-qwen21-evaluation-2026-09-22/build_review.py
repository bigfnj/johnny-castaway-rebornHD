"""Build the isolated Qwen 2.1 evaluation review without changing image assets."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_json(filename: str) -> tuple[dict, str | None]:
    path = ROOT / filename
    if not path.exists():
        return {}, None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        return data, None
    except (OSError, ValueError) as exc:
        return {}, f"Could not read {filename}: {exc}"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def image_card(title: str, filename: str, description: str, pixelated: bool = False) -> str:
    path = ROOT / filename
    if path.is_file():
        body = (
            f'<a class="canvas" href="{escape(filename)}" target="_blank" '
            f'rel="noopener" aria-label="Open {escape(title)} PNG">'
            f'<img class="{"pixelated" if pixelated else ""}" '
            f'src="{escape(filename)}" alt="{escape(title)}"></a>'
            f'<div class="image-footer"><a href="{escape(filename)}" '
            f'target="_blank" rel="noopener">Open PNG</a>'
            '<span class="dimensions">Loading dimensions</span></div>'
        )
    else:
        message = "No generated output is available yet." if filename == "output-raw.png" else "Input file is not available yet."
        body = f'<div class="canvas empty">{message}</div>'
    return (
        f'<article class="card"><h2>{escape(title)}</h2>'
        f'<p>{escape(description)}</p>{body}</article>'
    )


def measured_fields(data: object, prefix: str = "") -> list[tuple[str, object]]:
    """Expose recorded measurements; never calculate or supply missing results."""
    result = []
    if not isinstance(data, dict):
        return result
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            result.extend(measured_fields(value, name))
            continue
        if value is None or isinstance(value, (list, tuple)):
            continue
        terms = ("gpu", "vram", "cuda", "elapsed", "duration", "seconds", "allocated", "reserved", "wall_time", "peak_memory")
        if any(term in name.lower() for term in terms):
            result.append((name, value))
    return result


def main() -> None:
    request, request_error = read_json("request.json")
    record, record_error = read_json("record.json")
    arguments = request.get("arguments", {})
    if not isinstance(arguments, dict):
        arguments = {}
    prompt = request.get("prompt", arguments.get("prompt", "No prompt has been recorded yet."))
    status = record.get("status", "No run status has been recorded yet.")
    if isinstance(status, (dict, list)):
        status = json.dumps(status, ensure_ascii=False)
    status = {
        "image_returned_needs_visual_review": "Render complete; awaiting your review",
    }.get(status, status)
    measurements = measured_fields(record)
    rows = "".join(f"<tr><th>{escape(name)}</th><td>{escape(value)}</td></tr>" for name, value in measurements)
    measurement_html = f'<table><tbody>{rows}</tbody></table>' if rows else '<p class="muted">GPU and timing measurements have not been recorded yet.</p>'
    problems = [error for error in (request_error, record_error) if error]
    if record.get("error"):
        error = record["error"]
        problems.append(error if isinstance(error, str) else json.dumps(error, ensure_ascii=False, indent=2))
    problems_html = "".join(f'<pre class="error">{escape(error)}</pre>' for error in problems)
    assessment = record.get('visual_review', {}).get('summary', '')
    links = " · ".join(
        f'<a href="{name}" target="_blank" rel="noopener">{label}</a>'
        for name, label in (("request.json", "Exact request"), ("record.json", "Run record"))
        if (ROOT / name).is_file()
    )
    cards = "".join((
        image_card("Original SMGIFT 039", "inputs/reference-01.png", "Reference 1: original pixel drawing and composition.", True),
        image_card("Approved SMGIFT 041 reference", "inputs/reference-02.png", "Reference 2: approved cartoon life preserver, white ring, and rope."),
        image_card("Approved SMGIFT 039", "inputs/approved-comparison.png", "The approved drawing remains the baseline for comparison."),
        image_card("Qwen-Image-2.1 evaluation output", "output-raw.png", "Raw model output for review. File availability does not imply approval."),
    ))
    document = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Qwen-Image-2.1 model evaluation | SMGIFT 039</title>
<style>
:root { color-scheme: dark; font: 16px/1.5 system-ui, sans-serif; background: #112936; color: #edf5f8; }
* { box-sizing: border-box; }
body { margin: 0; }
main { max-width: 1640px; margin: auto; padding: 24px; }
h1 { font-size: clamp(1.5rem, 3vw, 2.1rem); margin: 0 0 8px; }
h2 { font-size: 1.1rem; margin: 0 0 6px; }
p { margin: 6px 0 12px; }
a { color: #a7e5ff; text-underline-offset: 3px; }
a:focus-visible, button:focus-visible { outline: 3px solid #ffcc66; outline-offset: 4px; }
.notice { color: #ffcc66; font-weight: 650; }
.muted, .dimensions { color: #bdd0d9; }
.status { padding: 14px 18px; margin: 18px 0; border: 1px solid #426374; border-radius: 10px; background: #1b3948; }
.toolbar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 20px 0 14px; }
button { border: 1px solid #6c8998; border-radius: 6px; color: #edf5f8; background: #244858; padding: 7px 12px; font: inherit; cursor: pointer; }
button[aria-pressed="true"] { color: #102632; background: #b9e8fa; border-color: #b9e8fa; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.card { min-width: 0; padding: 16px; border-radius: 10px; background: #203f4e; }
.card p { min-height: 3em; color: #d4e2e9; }
.canvas { height: 400px; width: 100%; display: flex; align-items: center; justify-content: center; border: 1px solid #6b7c80; border-radius: 4px; overflow: hidden; background-color: #eeeae0; background-image: conic-gradient(#d4d1c7 25%, #eeeae0 0 50%, #d4d1c7 0 75%, #eeeae0 0); background-size: 24px 24px; }
body[data-background="dark"] .canvas { background: #162329; }
body[data-background="white"] .canvas { background: #fff; }
.canvas img { display: block; width: 100%; height: 100%; object-fit: contain; }
.canvas img.pixelated { image-rendering: pixelated; }
.canvas.empty { color: #152d38; text-align: center; padding: 24px; }
body[data-background="dark"] .canvas.empty { color: #edf5f8; }
.image-footer { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding-top: 10px; font-size: .9rem; }
.details { margin-top: 20px; padding: 18px; background: #1b3948; border-radius: 10px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font: .9rem/1.5 ui-monospace, monospace; margin: 12px 0; }
.prompt { font-family: inherit; }
.error { color: #ffd1c8; border-left: 3px solid #ffab96; padding: 10px; background: #492f33; }
summary { cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: .9rem; }
th, td { text-align: left; vertical-align: top; padding: 8px; border-bottom: 1px solid #426374; overflow-wrap: anywhere; }
th { font-weight: 500; width: 52%; }
@media (max-width: 760px) { main { padding: 14px; } .grid { grid-template-columns: 1fr; } .canvas { height: 330px; } .card p { min-height: 0; } }
</style>
</head>
<body data-background="checkerboard">
<main>
<h1>Qwen-Image-2.1 model evaluation</h1>
<p class="notice">Model evaluation only. Approved drawings remain selected.</p>
<p>SMGIFT 039: evaluate a written instruction with two reference images, life preserver consistency, and transparent output.</p>
<section class="status" aria-label="Run status">
<div>Recorded status: <strong>__STATUS__</strong></div>
<p>__ASSESSMENT__</p>
<p class="muted">This review reports the saved run record. Refresh after the review is rebuilt to see new results.</p>
__PROBLEMS__
<div>__LINKS__</div>
</section>
<div class="toolbar" aria-label="Preview background">
<span>Preview background:</span>
<button type="button" data-bg="checkerboard" aria-pressed="true">Checkerboard</button>
<button type="button" data-bg="dark" aria-pressed="false">Dark</button>
<button type="button" data-bg="white" aria-pressed="false">White</button>
</div>
<section class="grid" aria-label="Image comparison">__CARDS__</section>
<section class="details"><h2>Written instruction</h2><pre class="prompt">__PROMPT__</pre></section>
<section class="details"><h2>Recorded GPU and timing data</h2>__MEASUREMENTS__
<details><summary>Full run record</summary><pre>__RECORD__</pre></details></section>
</main>
<script>
for (const button of document.querySelectorAll('[data-bg]')) {
  button.addEventListener('click', () => {
    document.body.dataset.background = button.dataset.bg;
    for (const option of document.querySelectorAll('[data-bg]')) {
      option.setAttribute('aria-pressed', String(option === button));
    }
  });
}
for (const image of document.querySelectorAll('.canvas img')) {
  const label = image.closest('.card').querySelector('.dimensions');
  const showDimensions = () => { label.textContent = image.naturalWidth + ' x ' + image.naturalHeight + ' pixels'; };
  image.addEventListener('load', showDimensions);
  image.addEventListener('error', () => { label.textContent = 'Image could not be loaded'; });
  if (image.complete && image.naturalWidth) showDimensions();
}
</script>
</body>
</html>
"""
    substitutions = {
        "__STATUS__": escape(status),
        "__ASSESSMENT__": escape(assessment),
        "__PROBLEMS__": problems_html,
        "__LINKS__": links,
        "__CARDS__": cards,
        "__PROMPT__": escape(prompt),
        "__MEASUREMENTS__": measurement_html,
        "__RECORD__": escape(json.dumps(record, ensure_ascii=False, indent=2)) if record else "No run record is available.",
    }
    for marker, value in substitutions.items():
        document = document.replace(marker, value)
    output = ROOT / "review.html"
    output.write_text(document, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
