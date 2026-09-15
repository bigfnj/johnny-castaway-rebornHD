"""Build two native turn directions with exact pixels and observed timestamps."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers'
sys.path.insert(0, str(PRIOR))
spec = importlib.util.spec_from_file_location('saved_arrival_player', PRIOR / 'build_review.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace(text, old, new, count=1):
    assert text.count(old) == count, 'unique viewer adaptation:' + old
    return text.replace(old, new)


def main():
    destination = OUT / 'review-v1'
    assert not destination.exists(), 'preserve existing turn review'
    clips, copies, reports = {}, {}, {}
    for clip in ('A1-to-A7', 'A7-to-A1'):
        folders = {'baseline': OUT / 'baseline-v1' / clip / 'full', 'candidate': OUT / 'candidate-v2' / clip / 'full'}
        raw = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
        records = {kind: json.loads(value) for kind, value in raw.items()}
        left, right = records['baseline'], records['candidate']
        assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS' and right['control'] is False
        assert len(left['displays']) == len(right['displays'])
        frames = []
        for a, b in zip(left['displays'], right['displays']):
            assert all(a[key] == b[key] for key in ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'actual_draw', 'draw_ordinal'))
            row = {key: b[key] for key in ('logical_ms', 'duration_ms', 'segment', 'segment_ms', 'actual_draw', 'draw_ordinal', 'comparison')}
            row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'])
            for kind, record in (('baseline', a), ('candidate', b)):
                path = folders[kind] / record['png']
                png = path.read_bytes()
                assert sha(png) == record['png_sha256']
                with Image.open(path) as image:
                    assert image.size == (1280, 960) and sha(image.convert('RGB').tobytes()) == record['pixels_sha256']
                relative = f'images/{clip}/{kind}/{record["png"]}'
                row[kind] = relative
                copies[relative] = png
            frames.append(row)
        clips[clip] = {'frames': frames, 'duration_ms': right['duration_ms'], 'pose_count': max(row['pose_index'] for row in frames) + 1,
                       'turn_start_ms': right['segments']['turn']['start_ms'], 'segments': right['segments'],
                       'reports_sha256': {kind: sha(value) for kind, value in raw.items()}}
        reports[clip] = clips[clip]['reports_sha256']
    page = prior.PAGE
    page = replace(page, "Johnny's new arrival pose", "Johnny's front turning pose", 2)
    page = replace(page, 'Watch the same Cartoon walk settle into the arrival pose. The new standing artwork is on the right.', 'Watch Johnny turn through the new front-facing pose. Standing017 is already approved; only turning016 is new on the right.')
    page = replace(page, '<div class="controls">', '<div class="controls"><label>Direction<select id="direction"><option value="A1-to-A7">Left to right</option><option value="A7-to-A1">Right to left</option></select></label>')
    page = replace(page, '<button id="next">Next pose</button>', '<button id="next">Next pose</button><button id="turning">Show turning pose</button><button id="replay">Replay turn</button>')
    page = replace(page, 'Current arrival', 'Approved017 + current HD016')
    page = replace(page, 'New Cartoon arrival', 'Approved017 + new Cartoon016')
    page = replace(page, 'Walk close-up', 'Pose close-up')
    page = replace(page, 'Only the standing pose is new. Use Previous pose and Next pose to check the last step into the arrival.', 'Compare both directions at Normal speed, then use Show turning pose or step through the change in foot placement. Both sides retain approved017 exactly.')
    description = ('These are two separate native same-spot turns at A: heading1 to7 and heading7 to1. Each clip begins with a separate native wait call to show approved017, then executes the requested turn. The starting wait lasts120ms in the actual port; it is not extended for this review. The first direction repeats its final017 for120ms before the1600ms hold; the reverse direction enters its1600ms hold directly. Native positions, horizontal mirroring, background updates and all timestamps are preserved. The candidate adds only016 above the approved017 private baseline. There is no interpolated pose, synthetic hold, original-executable parity claim or016 approval.')
    page, count = re.subn(r'<p class="muted">Both views use.*?</p><p id="technical">', '<p class="muted">' + description + '</p><p id="technical">', page, count=1)
    assert count == 1
    page = replace(page, 'There are 47 observed displays, including a zero-duration completion witness. Repeating restarts the recorded route; it does not invent a return walk.', 'Every observed display is retained, including zero-duration completion witnesses at native call boundaries. Playback advances to the final display at a shared timestamp. Repeating restarts the selected native clip; it does not invent another turn.')
    page = replace(page, "const data=JSON.parse(document.getElementById('capture-data').textContent),$=id=>document.getElementById(id);const images={baseline:[],candidate:[]};", "const bundle=JSON.parse(document.getElementById('capture-data').textContent),$=id=>document.getElementById(id);let active='A1-to-A7',data=bundle.clips[active],images;const allImages=Object.fromEntries(Object.keys(bundle.clips).map(key=>[key,{baseline:[],candidate:[]}]));")
    page = replace(page, "ctx.drawImage(images[kind][index],580,440,400,280,0,0,400,280)", "ctx.drawImage(images[kind][index],560,400,400,280,0,0,400,280)")
    page = replace(page, "row.frame===18?'Arrival pose':`Walking pose ${row.pose_index+1} / 23`", "`${row.segment==='prime'?'Starting pose (approved017)':row.frame===16?'Turning pose (016)':'Settling pose (approved017)'} · JOHNWALK.BMP ${String(row.frame).padStart(3,'0')}`")
    page = replace(page, '${row.logical_ms} ms · next interval ${row.duration_ms} ms · ${row.comparison}', '${row.logical_ms} ms · ${row.segment} +${row.segment_ms} ms · origin(${row.actual_draw[1]},${row.actual_draw[2]}) · mirrored ${Boolean(row.actual_draw[0])} · next interval ${row.duration_ms} ms · ${row.comparison}')
    page = replace(page, "{ready,index,frame:row.frame,position,playing,view:$('view').value,routeLength:data.frames.length}", "{ready,index,frame:row.frame,position,playing,view:$('view').value,routeLength:data.frames.length,clip:active,segment:row.segment}")
    page = replace(page, '(data.frames[index].pose_index+delta+24)%24', '(data.frames[index].pose_index+delta+data.pose_count)%data.pose_count')
    page = replace(page, "$('play').onclick=()=>play(!playing);", "$('direction').onchange=()=>{active=$('direction').value;data=bundle.clips[active];images=allImages[active];select(0);play(true);};$('turning').onclick=()=>{play(false);$('view').value='walk';select(data.frames.findIndex(row=>row.segment==='turn'&&row.frame===16));};$('replay').onclick=()=>{select(0);play(true);};$('play').onclick=()=>play(!playing);")
    old = "Promise.all(['baseline','candidate'].flatMap(kind=>data.frames.map((row,i)=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{images[kind][i]=im;resolve();};im.onerror=()=>reject(Error(`Cannot load ${kind} capture ${i+1}`));im.src=row[kind];})))).then(()=>{ready=true;draw();requestAnimationFrame(tick);})"
    new = "Promise.all(Object.entries(bundle.clips).flatMap(([clip,record])=>['baseline','candidate'].flatMap(kind=>record.frames.map((row,i)=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{allImages[clip][kind][i]=im;resolve();};im.onerror=()=>reject(Error(`Cannot load ${clip} ${kind} capture ${i+1}`));im.src=row[kind];}))))).then(()=>{images=allImages[active];ready=true;draw();requestAnimationFrame(tick);})"
    page = replace(page, old, new)
    page = page.replace('__DATA__', json.dumps({'clips': clips}, separators=(',', ':')))
    destination.mkdir()
    for name, raw in copies.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (destination / 'review.html').write_text(page, encoding='utf-8', newline='\n')
    record = {'status': 'local technical review; unpublished', 'html_sha256': sha((destination / 'review.html').read_bytes()),
              'image_files': {name: sha(raw) for name, raw in copies.items()}, 'reports_sha256': reports,
              'fixed_camera_hd_xywh': [560, 400, 400, 280], 'builder_sha256': sha(Path(__file__).read_bytes()),
              'prior_player_sha256': sha((PRIOR / 'build_review.py').read_bytes()),
              'scope': 'Only016 is new;017 approved and retained. No production edit, publication or human016 approval.'}
    (destination / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS local two-direction review with {len(copies)} exact native images')


if __name__ == '__main__':
    main()
