"""Build a standalone original/current/revised walk review from frozen inputs.

This is a composed diagnostic, not a native engine capture or arrival animation.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("front_review_export", HERE / "export.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
require, sha, encode = exporter.require, exporter.sha, exporter.encode


def route(source):
    rows, active = [], False
    for line in source.decode("utf-8").splitlines():
        match = re.search(r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", line)
        if not match:
            continue
        if "// E to A" in line:
            active = True
        if not active:
            continue
        flip, x, y, frame = map(int, match.groups())
        if not x:
            break
        rows.append({"flip": flip, "frame": frame, "x": x - 1, "y": y, "duration_ms": 120})
    expected = [28, 29, 24, 25, 26, 27] * 3 + [28, 29, 24, 25, 27]
    require([row["frame"] for row in rows] == expected and all(row["flip"] == 0 for row in rows), "original-e-to-a-travel-contract")
    return rows


PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Johnny front walk review</title><style>
*{box-sizing:border-box}body{margin:0;background:#15222b;color:#eef4f6;font:16px system-ui,sans-serif}main{max-width:1800px;margin:auto;padding:22px}h1{font-size:27px;margin:0 0 12px}p{line-height:1.5}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:18px 0}button,select{font:inherit;border:0;border-radius:5px;padding:9px;background:#edf4f6;color:#14232a}button{cursor:pointer}label{display:flex;gap:7px;align-items:center}.panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.panel{background:#263942;border-radius:8px;overflow:hidden}h2{font-size:17px;padding:12px;margin:0}canvas{width:100%;height:auto;display:block;image-rendering:pixelated}.muted{color:#c0d0d7}#status{min-height:1.6em}#failure{color:#ff9999}details{margin-top:18px}@media(max-width:800px){main{padding:10px}.panels{grid-template-columns:1fr}}
</style><main><h1>Front walk: original, current and revised</h1><p>Watch the feet and the turn of Johnny's body. Frames 024–027 retain the approved Cartoon artwork; revised frames are listed below.</p>
<div class="controls"><button id="play">Pause</button><button id="previous">Previous pose</button><button id="next">Next pose</button><label>Speed<select id="speed"><option value="0.5">Slow</option><option value="1" selected>Normal</option></select></label><label><input id="repeat" type="checkbox" checked>Repeat</label></div>
<p id="status">Loading images...</p><div class="panels"><section class="panel"><h2>Original pose reference</h2><canvas id="original"></canvas></section><section class="panel"><h2>Current approved Cartoon</h2><canvas id="current"></canvas></section><section class="panel"><h2>Revised Cartoon candidate</h2><canvas id="revised"></canvas></section></div>
<p id="changes"></p><p class="muted">The final one-second pause holds the last walking pose for review. It is not Johnny's native standing arrival.</p><details><summary>Reference and preview details</summary><p>This standalone comparison uses the 23 stored E-to-A positions, their recorded horizontal orientation, and 120 ms per travel pose. Original colors are the decoder's diagnostic palette. Both Cartoon views use the same placement and scale. Revised artwork includes transparent padding so an overhanging toe stays visible. No in-between poses are generated, and no island, native arrival, or original-executable playback is simulated.</p><p id="technical"></p></details><p id="failure" role="alert"></p></main>
<script id="review-data" type="application/json">__DATA__</script><script>
'use strict';const data=JSON.parse(document.getElementById('review-data').textContent),$=id=>document.getElementById(id);const images={};let ready=false,index=0,position=0,playing=true,last=null;
function background(ctx,w,h){for(let y=0;y<h;y+=12)for(let x=0;x<w;x+=12){ctx.fillStyle=((x/12+y/12)%2)?'#34464e':'#2e4048';ctx.fillRect(x,y,12,12);}}
function draw(){if(!ready)return;const row=data.timeline[index],frame=data.assets[String(row.frame)],box=data.viewport;for(const kind of ['original','current','revised']){const c=$(kind);c.width=box[2];c.height=box[3];const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;background(ctx,c.width,c.height);const entry=frame[kind],x=row.x*2-box[0]-entry.padding,y=row.y*2-box[1]-entry.padding;ctx.drawImage(images[entry.path],x,y,entry.width,entry.height);}const label=row.hold?'Diagnostic endpoint hold':`Pose ${index+1} / 23`;$('status').textContent=`${label} | JOHNWALK.BMP ${String(row.frame).padStart(3,'0')} | x ${row.x}, y ${row.y}`;$('technical').textContent=`${row.start_ms} ms; ${row.duration_ms} ms interval. ${data.preview_only?'Preview only: runtime export is withheld.':'Runtime canvases fit the recorded alpha-8 source centers; visual approval is pending.'}`;window.frontReviewState={ready,index,frame:row.frame,position,playing,hold:row.hold,duration:data.duration_ms};}
function select(i){index=i;position=data.timeline[i].start_ms;last=null;draw();}
function play(value){playing=value;last=null;$('play').textContent=value?'Pause':'Play';draw();}
$('play').onclick=()=>play(!playing);$('previous').onclick=()=>{play(false);select((index+data.timeline.length-1)%data.timeline.length);};$('next').onclick=()=>{play(false);select((index+1)%data.timeline.length);};$('speed').onchange=()=>{last=null;};
function tick(time){if(ready&&playing){if(last!==null){position+=(time-last)*Number($('speed').value);if(position>=data.duration_ms){if($('repeat').checked)position%=data.duration_ms;else{position=data.duration_ms;play(false);}}index=0;while(index+1<data.timeline.length&&data.timeline[index+1].start_ms<=position)index++;}draw();}last=time;requestAnimationFrame(tick);}
const paths=[...new Set(Object.values(data.assets).flatMap(frame=>Object.values(frame).map(entry=>entry.path)))];Promise.all(paths.map(path=>new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{images[path]=image;resolve();};image.onerror=()=>reject(Error(`Cannot load ${path}`));image.src=path;}))).then(()=>{ready=true;$('changes').textContent=`Revised frames: ${data.revised_frames.map(n=>String(n).padStart(3,'0')).join(', ')||'none (unchanged control)'}.`;draw();requestAnimationFrame(tick);}).catch(error=>{$('failure').textContent=error.message;window.frontReviewError=error.message;});
</script></html>'''


def build(export_directory, output):
    require(not output.exists(), "review-output-already-exists")
    recipe, inputs, rendered, report = exporter.reproduce(export_directory / "recipe.json")
    rows = route(inputs["inputs/walk-data.h"])
    timeline = [dict(row, start_ms=i * 120, hold=False) for i, row in enumerate(rows)]
    timeline.append(dict(rows[-1], start_ms=2760, duration_ms=1000, hold=True))
    assets, copies = {}, {}
    for row in recipe["frames"]:
        frame, width, height = row["frame"], *row["runtime_canvas"]
        entries = {"original": (inputs[row["original"]], width, height, 0),
                   "current": (inputs[row["baseline"]], width, height, 0),
                   "revised": (rendered[f"padded/{frame:03}.png"], width + exporter.PAD * 2, height + exporter.PAD * 2, exporter.PAD)}
        assets[str(frame)] = {}
        for kind, (raw, w, h, padding) in entries.items():
            path = f"images/{kind}/{frame:03}.png"
            copies[path] = raw
            visible = exporter.decoded(raw, "review-image-canvas").getchannel("A").getbbox()
            require(visible is not None, f"empty-review-image:{frame:03}:{kind}")
            visible = [n * (2 if kind == "original" else 1) for n in visible]
            assets[str(frame)][kind] = {"path": path, "width": w, "height": h, "padding": padding,
                                        "visible_bounds": visible, "sha256": sha(raw)}
    boxes = [[row["x"] * 2 - entry["padding"] + entry["visible_bounds"][0],
              row["y"] * 2 - entry["padding"] + entry["visible_bounds"][1],
              row["x"] * 2 - entry["padding"] + entry["visible_bounds"][2],
              row["y"] * 2 - entry["padding"] + entry["visible_bounds"][3]]
             for row in rows for entry in assets[str(row["frame"])].values()]
    left, top = min(box[0] for box in boxes) - 8, min(box[1] for box in boxes) - 8
    right, bottom = max(box[2] for box in boxes) + 8, max(box[3] for box in boxes) + 8
    data = {"schema_version": 1, "timeline": timeline, "duration_ms": 3760,
            "viewport": [left, top, right - left, bottom - top], "assets": assets,
            "preview_only": recipe["preview_only"], "revised_frames": [row["frame"] for row in recipe["frames"] if row["mode"] == "generated"],
            "scope": "Composed technical review; exact stored travel rows plus diagnostic hold. No native arrival or artistic approval."}
    html = PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    output.mkdir(parents=True)
    exporter.write_output(output / "export", recipe, inputs, rendered, report)
    copies["review.html"] = html.encode("utf-8")
    copies["review-data.json"] = encode(data)
    for name, raw in copies.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    evidence = {"status": "technical-review-built", "human_accepted": False, "native_capture": False,
                "files": {name: sha(raw) for name, raw in sorted(copies.items())},
                "recipe_sha256": sha(encode(recipe)), "exporter_sha256": sha((HERE / "export.py").read_bytes()),
                "review_builder_sha256": sha(Path(__file__).read_bytes()), "timing_source_sha256": sha(inputs["inputs/walk-data.h"]),
                "travel_poses": 23, "travel_ms": 2760, "diagnostic_hold_ms": 1000}
    (output / "review-record.json").write_bytes(encode(evidence))
    return data, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print("WITNESS front-review " + sha(Path(__file__).read_bytes()), flush=True)
    try:
        build(args.export, args.output)
    except (ValueError, KeyError, OSError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    print("PASS standalone 23-pose review with labeled diagnostic hold; unpublished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
