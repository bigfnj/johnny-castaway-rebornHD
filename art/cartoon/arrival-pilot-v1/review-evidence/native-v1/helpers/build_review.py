"""Pair exact native captures in a portable timed browser review."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from capture_format import ppm

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Johnny's new arrival pose</title><style>
*{box-sizing:border-box}body{margin:0;background:#17232d;color:#edf3f7;font:16px system-ui,sans-serif}main{max-width:1900px;margin:auto;padding:24px}h1{font-size:28px;margin:0 0 10px}p{line-height:1.45;margin:8px 0}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:14px 0}button,select{font:inherit;padding:8px 12px;background:#eaf2f6;color:#182c3a;border:0;border-radius:5px}button{cursor:pointer}label{display:flex;align-items:center;gap:6px}.panels{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.panel{background:#263746;border-radius:8px;overflow:hidden}.panel h2{margin:0;padding:12px;font-size:17px}canvas{display:block;width:100%;height:auto;image-rendering:pixelated;background:#263746}.muted{color:#b9c8d2}details{margin-top:16px}#failure{color:#ff9a9a}#status{min-height:1.5em}@media(max-width:700px){main{padding:10px}.panels{gap:8px}}
</style><main><h1>Johnny's new arrival pose</h1><p>Watch the same Cartoon walk settle into the arrival pose. The new standing artwork is on the right.</p>
<div class="controls"><button id="play">Pause</button><button id="prev">Previous pose</button><button id="next">Next pose</button><label>Speed<select id="speed"><option value="0.5">Slow</option><option value="1" selected>Normal</option></select></label><label>View<select id="view"><option value="island" selected>Full island</option><option value="walk">Walk close-up</option></select></label><label><input id="repeat" type="checkbox" checked>Repeat</label></div>
<p id="status">Loading native captures...</p><div class="panels"><section class="panel"><h2>Current arrival</h2><canvas id="baseline" width="1280" height="960"></canvas></section><section class="panel"><h2>New Cartoon arrival</h2><canvas id="candidate" width="1280" height="960"></canvas></section></div>
<p>Only the standing pose is new. Use Previous pose and Next pose to check the last step into the arrival.</p><details><summary>Technical details</summary><p class="muted">Both views use the approved Cartoon island and rear walk. The left arrival uses packaged HD frame 018; only the right arrival uses new Cartoon frame 018. These are paired native Linux captures from the same saved executable and unmodified B-to-A route. The private candidate adds one sprite and preserves every production member. The script moves the sprite origin from (302,244) on the last walking pose to (298,240) on arrival; the review preserves that shift. Recorded timing includes background updates and the 1.6-second arrival hold. This does not establish original executable rendering or physical wall-clock speed. No turn has been appended.</p><p id="technical"></p><p class="muted">There are 47 observed displays, including a zero-duration completion witness. Repeating restarts the recorded route; it does not invent a return walk. Close-up uses the same native pixels with a matching camera rectangle in both views. No interpolated poses or image repainting.</p></details><p id="failure" role="alert"></p></main>
<script id="capture-data" type="application/json">__DATA__</script><script>
'use strict';const data=JSON.parse(document.getElementById('capture-data').textContent),$=id=>document.getElementById(id);const images={baseline:[],candidate:[]};let ready=false,index=0,position=0,playing=true,lastTime=null;
function draw(){if(!ready)return;const row=data.frames[index];for(const kind of ['baseline','candidate']){const c=$(kind),ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;if($('view').value==='walk'){c.width=400;c.height=280;ctx.imageSmoothingEnabled=false;ctx.drawImage(images[kind][index],580,440,400,280,0,0,400,280);}else{c.width=1280;c.height=960;ctx.drawImage(images[kind][index],0,0);}}$('status').textContent=row.frame===18?'Arrival pose':`Walking pose ${row.pose_index+1} / 23`;$('technical').textContent=`Native display ${index+1} / ${data.frames.length} · JOHNWALK.BMP ${String(row.frame).padStart(3,'0')} · ${row.logical_ms} ms · next interval ${row.duration_ms} ms · ${row.comparison}`;window.nativeReviewState={ready,index,frame:row.frame,position,playing,view:$('view').value,routeLength:data.frames.length};}
function select(i){index=i;position=data.frames[i].logical_ms;lastTime=null;draw();}
function play(value){playing=value;lastTime=null;$('play').textContent=value?'Pause':'Play';draw();}
function stepPose(delta){play(false);const target=(data.frames[index].pose_index+delta+24)%24;select(data.frames.findIndex(row=>row.pose_index===target));}
$('play').onclick=()=>play(!playing);$('prev').onclick=()=>stepPose(-1);$('next').onclick=()=>stepPose(1);$('view').onchange=draw;$('speed').onchange=()=>{lastTime=null;};
function tick(time){if(ready&&playing){if(lastTime!==null){position+=(time-lastTime)*Number($('speed').value);if(position>=data.duration_ms){if($('repeat').checked)position%=data.duration_ms;else{position=data.duration_ms;play(false);}}index=0;while(index+1<data.frames.length&&data.frames[index+1].logical_ms<=position)index++;}draw();}lastTime=time;requestAnimationFrame(tick);}
Promise.all(['baseline','candidate'].flatMap(kind=>data.frames.map((row,i)=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{images[kind][i]=im;resolve();};im.onerror=()=>reject(Error(`Cannot load ${kind} capture ${i+1}`));im.src=row[kind];})))).then(()=>{ready=true;draw();requestAnimationFrame(tick);}).catch(error=>{$('failure').textContent=error.message;window.nativeReviewError=error.message;});
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print('WITNESS build_review.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    assert not args.output.exists(), 'preserve-prior-review'
    baseline = HERE / 'baseline/full'
    candidate = args.candidate / 'full'
    baseline_raw = (baseline / 'report.json').read_bytes()
    candidate_raw = (candidate / 'report.json').read_bytes()
    left, right = json.loads(baseline_raw), json.loads(candidate_raw)
    assert right['status'] == 'PASS' and not right['control'], 'real-candidate-required'
    assert left['executable_sha256'] == right['executable_sha256'], 'same-saved-executable'
    assert len(left['displays']) == len(right['displays']) == 47, '47-display-contract'
    frames, copies, pose_index, prior = [], [], -1, None
    for a, b in zip(left['displays'], right['displays']):
        assert all(a[k] == b[k] for k in ('index', 'logical_ms', 'duration_ms', 'stored_walk_row', 'draw_xy', 'frame')), 'paired-timeline'
        if b['stored_walk_row'] != prior:
            pose_index += 1
            prior = b['stored_walk_row']
        row = {k: b[k] for k in ('logical_ms', 'duration_ms', 'draw_xy', 'frame', 'comparison')}
        row['pose_index'] = pose_index
        for kind, folder, record in [('baseline', baseline, a), ('candidate', candidate, b)]:
            pixels = ppm(folder / record['ppm'])
            assert sha(pixels) == record['pixels_sha256'], f'{kind}-capture-pixels:{record["index"]}'
            png = (folder / record['png']).read_bytes()
            from capture_format import png_bytes
            assert png == png_bytes(pixels), f'{kind}-lossless-png:{record["index"]}'
            path = f'images/{kind}/{record["png"]}'
            row[kind] = path
            copies.append((path, png))
        frames.append(row)
    assert frames[-1]['logical_ms'] == 4360 and frames[-1]['duration_ms'] == 0
    args.output.mkdir(parents=True)
    for path, raw in copies:
        target = args.output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    data = {'duration_ms': 4360, 'frames': frames, 'baseline_report_sha256': sha(baseline_raw),
            'candidate_report_sha256': sha(candidate_raw)}
    html = PAGE.replace('__DATA__', json.dumps(data, separators=(',', ':')))
    (args.output / 'review.html').write_text(html, encoding='utf-8', newline='\n')
    evidence = {'status': 'built-for-human-review', 'html_sha256': sha((args.output / 'review.html').read_bytes()),
                'image_files': {p: sha(raw) for p, raw in copies}, 'baseline_report_sha256': sha(baseline_raw),
                'candidate_report_sha256': sha(candidate_raw), 'source_sha256': sha(Path(__file__).read_bytes()),
                'scope': 'Exact native PNG bytes; no production promotion or human acceptance assigned.'}
    (args.output / 'review-record.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS paired native review: 94 unchanged capture PNGs,47 display records', flush=True)


if __name__ == '__main__':
    main()
