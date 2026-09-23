"""Create a local editing trial page from saved result records."""
import html
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def link(path):
    return html.escape(os.path.relpath(path, HERE).replace(os.sep, "/"), quote=True)


def main():
    cards = []
    for file in sorted(HERE.glob("*/record.json")):
        record = json.loads(file.read_text(encoding="utf-8"))
        if not record.get("output"):
            continue
        source = record["references"][0]["source"]["path"]
        output = record["output"]["path"]
        name = file.parent.name
        qa_file = file.parent / "visual-review.json"
        qa = json.loads(qa_file.read_text(encoding="utf-8")) if qa_file.exists() else {}
        assessment = qa.get("assessment", "Awaiting visual assessment. Technical generation success does not establish pose accuracy.")
        figures = []
        for title, path in [("Reference", source), ("Local raw result", output)]:
            figures.append(f'<figure><figcaption>{title}</figcaption><a href="{link(path)}"><img src="{link(path)}" alt="{title} {name}"></a></figure>')
        prompt = (file.parent / "prompt.txt").read_text(encoding="utf-8")
        cards.append(f'<article id="{html.escape(name)}"><h2>{html.escape(name)}</h2><p>{html.escape(assessment)}</p>'
                     f'<div class="row">{"".join(figures)}</div>'
                     f'<p>{record["output"]["mode"]}, {record["settings"]["width"]} × {record["settings"]["height"]}; '
                     f'inference {record.get("inference_seconds", "unknown")} seconds; '
                     f'peak PyTorch allocation {record.get("peak_allocated_gib", "unknown")} GiB.</p>'
                     f'<p><a href="{link(file)}">Run record</a> · '
                     f'<a href="{link(record["references"][0]["input"]["path"])}">Actual prepared RGB input</a></p>'
                     f'<details><summary>Exact local prompt</summary><pre>{html.escape(prompt)}</pre></details></article>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local FLUX editing trial</title><style>
*{box-sizing:border-box}body{font:16px system-ui;margin:0;background:#152731;color:#edf4f7;padding:24px;line-height:1.5}main{max-width:1500px;margin:auto}a{color:#afe0ff}h1{font-size:30px}article{background:#243e4c;padding:20px;border-radius:10px;margin:24px 0}.row{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}figcaption{font-weight:700;margin:10px 0}img{display:block;width:100%;height:360px;object-fit:contain;background:#eee9df repeating-conic-gradient(#ded9cf 0% 25%,transparent 0% 50%);background-size:24px 24px}pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer}@media(max-width:800px){.row{grid-template-columns:1fr}img{height:auto}body{padding:12px}}
</style><main><h1>Local FLUX.2 [klein] 4B editing trial</h1>
<p>Tests on the RTX4090 using the existing character as an image reference. Raw local results are RGB; the original transparent artwork is unchanged.</p>
<p><a href="../local-generation-handoff/index.html">Exact earlier prompts and references</a> · <a href="../review.html">Built-in attempt review</a></p>
'''
    (HERE / "review.html").write_text(page + "\n".join(cards) + "</main></html>\n", encoding="utf-8")
    print(f"Created review with {len(cards)} local results.")


if __name__ == "__main__":
    main()
