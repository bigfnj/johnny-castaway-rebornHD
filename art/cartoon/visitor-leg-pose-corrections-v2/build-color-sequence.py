"""Read-only source trace and comparison metadata. No PNG mutations."""
import hashlib
import base64
import io
import importlib.util
import json
import os
import struct
import zipfile
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('inventory', ROOT / 'tools/inventory_scenes.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def decode_bytes(r):
    data, size = r['_compressed'], r['script_bytes']
    if r['compression_method'] == 1:
        out, pos = bytearray(), 0
        while pos < len(data):
            code = data[pos]
            pos += 1
            if code & 128:
                out.extend([data[pos]] * (code & 127))
                pos += 1
            else:
                out.extend(data[pos:pos + code])
                pos += code
        assert pos == len(data) and len(out) == size
        return bytes(out)
    # Equivalent LSB-first dictionary decoding to src/engine/uncompress.c.
    # Exact resulting bytes must match the prior production-probe SHA-256.
    cursor = 0
    def bits(n):
        nonlocal cursor
        result = sum(((data[(cursor+i)//8] >> ((cursor+i)%8)) & 1) << i for i in range(n))
        cursor += n
        return result
    nbits, free, bitpos = 9, 257, 0
    table = [(0,0)] * 4096
    old = last = bits(nbits)
    out = bytearray([old & 255])
    while len(out) < size:
        new = bits(nbits)
        bitpos += nbits
        if new == 256:
            width = nbits * 8
            cursor += (width - ((bitpos - 1) % width)) - 1
            nbits, free, bitpos = 9, 256, 0
            continue
        code, stack = new, []
        if code >= free:
            stack.append(last)
            code = old
        while code > 255:
            assert code < 4096 and len(stack) < 4096
            prefix, append = table[code]
            stack.append(append)
            code = prefix
        stack.append(code)
        last = code
        out.extend(reversed(stack))
        if free < 4096:
            table[free] = (old, last)
            free += 1
            if free >= (1 << nbits) and nbits < 12:
                nbits += 1
                bitpos = 0
        old = new
    assert len(out) == size
    return bytes(out)

def commands(r, data):
    result, pos, tag = [], 0, 0
    while pos < len(data):
        start, code = pos, inventory.u16(data, pos)
        pos += 2
        if r['type'] == 'ADS':
            name, nargs = inventory.ADS_OPS.get(code, ('TAG', 0))
            if name == 'TAG':
                tag = code
            args = [inventory.u16(data, pos + i*2) for i in range(nargs)]
            pos += nargs*2
        else:
            name, nargs = inventory.TTM_OPS.get(code, f'UNKNOWN_{code:04X}'), code & 15
            if nargs == 15:
                argument, end = inventory.cstring(data, pos, 256)
                pos = end + ((end-pos) & 1)
                args = [argument]
            else:
                args = [inventory.u16(data, pos + i*2) for i in range(nargs)]
                pos += nargs*2
            if name == 'TAG':
                tag = args[0]
        assert pos <= len(data)
        result.append(dict(offset=start, opcode=f'{code:04X}', command=name, tag=tag, args=args))
    return result

def load_trace():
    archive = ROOT / 'assets/scrantic_data.zip'
    with zipfile.ZipFile(archive) as z:
        files = {Path(n).name.upper(): n for n in z.namelist()}
        _, resources = inventory.resource_catalog(z.read(files['RESOURCE.MAP']), z.read(files['RESOURCE.001']))
    baseline = json.loads((ROOT / 'docs/knowledge-base/port-inventory.json').read_text(encoding='utf-8'))
    known = {r['name']: r for r in baseline['port_resources']}
    scripts = {}
    for name in ['SUZY.ADS', 'SUZYCITY.TTM']:
        r = resources[name]
        inventory.metadata(r)
        data = decode_bytes(r)
        assert r['payload_sha256'] == known[name]['payload_sha256']
        assert sha(data) == known[name]['decoded_sha256']
        scripts[name] = dict(payload_sha256=r['payload_sha256'], decoded_sha256=sha(data), tags=r['tags'], bindings=r.get('bindings',[]), commands=commands(r,data))
    return scripts

def image_info(relative, expected=None):
    path = ROOT / relative
    digest = sha(path.read_bytes())
    if expected:
        assert digest == expected, relative
    with Image.open(path) as im:
        assert im.mode == 'RGBA'
        bounds = im.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
        return dict(path=relative, url=os.path.relpath(path, HERE).replace(os.sep, '/'), sha256=digest, canvas=list(im.size), bounds=list(bounds))

def file_info(relative, expected=None):
    path = ROOT / relative
    digest = sha(path.read_bytes())
    if expected:
        assert digest == expected, relative
    return dict(path=relative, url=os.path.relpath(path, HERE).replace(os.sep, '/'), sha256=digest)

def build():
    trace = load_trace()
    (HERE / 'color-sequence-source-commands.json').write_text(json.dumps(trace, indent=2)+'\n', encoding='utf-8')
    older = json.loads((HERE.parent / 'worker-visitor-mermaid-fixes-v1/review-data.json').read_text(encoding='utf-8'))
    latest = json.loads((HERE / 'selected-versions.json').read_text(encoding='utf-8'))
    oldrows = {int(r['frame']):r for r in older['assets'] if r['resource']=='SSUZY1.BMP'}
    sprites = {}
    for frame in range(11):
        key = f'SSUZY1.BMP-{frame:03d}'
        row = oldrows[frame]
        selected = latest['frames'][key]['appearance_approval']['output'] if key in latest['frames'] else row['selected_raw']
        original = row['original_reference']
        sprites[str(frame)] = dict(frame=frame, label=f'{frame:03d}', color_pending=frame in [4,5],
            original=image_info(original['path'], original['sha256']), cartoon=image_info(selected['path'], selected['sha256']))
        if frame in [3,4,5]:
            relative = (f'art/cartoon/visitor-leg-pose-corrections-v2/generation/SSUZY1.BMP/003-record-v3.json' if frame == 3 else
                f'art/cartoon/mermaid-expression-corrections-v1/generation/SSUZY1.BMP/{frame:03d}-record-v2.json')
            record = json.loads((ROOT / relative).read_text(encoding='utf-8'))
            candidate = image_info(record['output']['path'], record['output']['sha256'])
            candidate.update(record=file_info(relative), request=file_info(record['request']['path'], record['request']['sha256']),
                version=record['version'], appearance_approval=None, review_status='awaiting_review',
                review_label='Regenerated bottle candidate: awaiting review' if frame == 3 else 'Regenerated color candidate: awaiting review')
            sprites[str(frame)]['candidate'] = candidate
    tagsteps = {}
    for tag in [2,3,5]:
        delay, timing_offset, draw, extra, terminal = 4, None, None, [], None
        rows = []
        for c in trace['SUZYCITY.TTM']['commands']:
            if c['tag'] != tag:
                continue
            op, args = c['command'], c['args']
            if op == 'CLEAR_SCREEN':
                draw, extra = None, []
            elif op == 'DRAW_SPRITE':
                if args[3] == 0:
                    assert draw is None
                    draw = dict(frame=args[2], x=args[0], y=args[1], draw_offset=c['offset'], flip=False)
                else:
                    extra.append(c)
            elif op == 'SET_DELAY':
                delay, timing_offset = max(4,args[0]), c['offset']
                timing_kind = 'SET_DELAY'
            elif op == 'TIMER':
                delay, timing_offset = sum(args)//2, c['offset']
                timing_kind = 'TIMER_port_approximation'
            elif op == 'PURGE':
                terminal = c['offset']
            elif op == 'UPDATE':
                assert draw is not None
                rows.append(dict(**draw, tag=tag, update_offset=c['offset'], delay_ticks=delay, duration_ms=delay*20,
                    timing_offset=timing_offset, timing_kind=timing_kind, supplementary_draws=extra.copy(), purge_offset=terminal))
        assert not any(c['command'] in ['GOTO_TAG','LOCAL_TAG'] for c in trace['SUZYCITY.TTM']['commands'] if c['tag']==tag)
        tagsteps[tag] = rows
    assert [x['frame'] for x in tagsteps[2]] == list(range(10))
    assert [x['frame'] for x in tagsteps[3]] == [10,9,10,9]
    assert [x['frame'] for x in tagsteps[5]] == [9,8,6,4,3,2,1,0]
    ads = trace['SUZY.ADS']['commands']
    calls = [c for c in ads if c['tag']==1 and c['command']=='ADD_SCENE' and c['args'][:2] in [[1,2],[1,3],[1,5]]]
    assert [c['args'] for c in calls] == [[1,2,0,1],[1,3,2,1],[1,5,0,1]]
    steps = []
    for call in calls:
        tag, count = call['args'][1], max(1,call['args'][2])
        for repeat in range(count):
            for step in tagsteps[tag]:
                steps.append(dict(**step, repeat=repeat+1, ads_call_offset=call['offset']))
    elapsed = 0
    for i, step in enumerate(steps):
        step.update(index=i, start_ms=elapsed)
        elapsed += step['duration_ms']
    assert len(steps)==26 and elapsed==5840
    # Frame008 includes its bottle. Frames009/010 use a separate source prop.
    # Keep the original bytes in metadata and reuse the already drawn cartoon
    # bottle in canvas only. No raster file is created or changed.
    inv = HERE.parent / 'character-inventory-v1'
    index = json.loads((inv / 'source/frame-index.json').read_text(encoding='utf-8'))
    prop_entry = next(r for r in index['frames'] if r['resource']=='SSUZY2.BMP' and r['frame']==1)
    with zipfile.ZipFile(inv / 'reference-originals.zip') as archive:
        prop_bytes = archive.read(prop_entry['path'])
    assert sha(prop_bytes) == prop_entry['png_sha256']
    with Image.open(io.BytesIO(prop_bytes)) as prop, Image.open(ROOT / sprites['8']['original']['path']) as original8:
        patch = original8.crop((0,43,16,59))
        visible = [(x,y) for y in range(16) for x in range(16) if prop.getpixel((x,y))[3] != 0]
        assert all(prop.getpixel(p) == patch.getpixel(p) for p in visible)
        prop_original = dict(url='data:image/png;base64,'+base64.b64encode(prop_bytes).decode('ascii'),
            archive=file_info((inv / 'reference-originals.zip').relative_to(ROOT).as_posix()), archive_member=prop_entry['path'],
            sha256=sha(prop_bytes), canvas=list(prop.size), bounds=list(prop.getchannel('A').getbbox()),
            baked_frame8_matching_visible_pixels=len(visible))
    source8 = next(s for s in steps if s['frame']==8)
    src = sprites['8']['cartoon']['bounds']
    target = sprites['8']['original']['bounds']
    fit = min((target[2]-target[0])/(src[2]-src[0]),(target[3]-target[1])/(src[3]-src[1]))
    x = source8['x']+target[0]+((target[2]-target[0])-(src[2]-src[0])*fit)/2
    y = source8['y']+target[3]-(src[3]-src[1])*fit
    bottle_crop = [58,700,142,881]
    cartoon_rect = [x+(bottle_crop[0]-src[0])*fit,y+(bottle_crop[1]-src[1])*fit,
        (bottle_crop[2]-bottle_crop[0])*fit,(bottle_crop[3]-bottle_crop[1])*fit]
    prop_steps = [s for s in steps if s['frame'] in [9,10]]
    assert all(any(c['args']==[173,297,1,1] for c in s['supplementary_draws']) for s in prop_steps)
    ground_bottle = dict(resource='SSUZY2.BMP',frame=1,original=prop_original,source_position=[173,297],
        display_on_frames=[9,10],already_baked_in_frame=8,cartoon_source_frame=8,cartoon_source_crop=bottle_crop,
        cartoon_logical_rect=cartoon_rect,source_draw_offsets=[c['offset'] for s in prop_steps for c in s['supplementary_draws'] if c['args']==[173,297,1,1]],
        note='008 contains the bottle. For009/010 the original prop uses source(173,297); the existing008 cartoon bottle is shown at its unchanged008 display position. No PNG changes.')
    boxes = []
    for s in steps:
        b = sprites[str(s['frame'])]['original']['bounds']
        boxes.append([s['x']+b[0],s['y']+b[1],s['x']+b[2],s['y']+b[3]])
    viewport = [min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8]
    paths = ['assets/scrantic_data.zip','tools/inventory_scenes.py','src/engine/uncompress.c','src/engine/ttm.c','src/engine/ads.c','src/engine/events.c','docs/knowledge-base/port-inventory.json',
        'art/cartoon/worker-visitor-mermaid-fixes-v1/review-data.json','art/cartoon/visitor-leg-pose-corrections-v2/selected-versions.json']
    data = dict(schema_version=3,resource='SSUZY1.BMP',status='source_order_with_current_port_timing_comparison_not_native_capture',
        default_drawing_mode='candidate',
        color_correction_status='Regenerated003 bottle and004/005 color candidates await review. Approved selections remain unchanged;009/010 ground bottle is displayed as a scene prop.',
        timing_label='Source order with current-port timing. Most updates 180 ms; final pause 1340 ms uses the port approximation for TIMER 45, 90.',
        tick_ms=20, nominal_excerpt_ms=elapsed, viewport=viewport, sprites=sprites, steps=steps, ground_bottle=ground_bottle,
        clips=[dict(id='full',label='Source excerpt: tanning oil, apply twice, lie back',indices=list(range(26))),
            dict(id='tanning',label='Tanning oil (tag 2)',indices=list(range(10))),
            dict(id='apply',label='Apply oil twice (tag 3)',indices=list(range(10,18))),
            dict(id='lieback',label='Lie back down (tag 5)',indices=list(range(18,26)))],
        control_flow=dict(ads='SUZY.ADS#1',ttm='SUZYCITY.TTM',calls=calls,normal_order=[2,3,3,5],
            preceding='MEANWHIL.TTM tag1 completes; SUZYCITY.TTM tag1 has loaded SSUZY1.BMP into slot0.',
            following='SUZYCITY.TTM tag6 floating bottle follows; deliberately outside this pose/color excerpt.'),
        display_notes=[
            'New candidate mode uses regenerated 003, 004 and 005 drawings awaiting review. Approved selection mode restores their previous selected drawings, including the imported 004 and 005 PNGs.',
            'No PNG pixels, approval records, selectors, or runtime assets are changed. Links open the exact displayed PNGs and saved generation requests.',
            'Original uses unmodified DRAW_SPRITE coordinates and canvas dimensions, enlarged together in a shared crop.',
            'For this color comparison only, each cartoon visible alpha box is uniformly fitted within the corresponding original visible box, bottom-centered. This is display normalization, not native registration.',
            'The ground bottle remains visible at a fixed position through 008, 009 and 010. It is already inside 008;009/010 use the separate SSUZY2.BMP frame001 at source(173,297). Cartoon playback reuses the bottle from008 without editing any PNG.',
            'Background SUZBEACH.SCR and other separate prop layers remain omitted. Supplementary draw commands are preserved in metadata.',
            'The 26 updates and tag 3 repeat count follow decoded source commands. Original executable timing has not been measured. Browser scheduling and concurrent native layers are not modeled.',
            'Final TIMER 45, 90 is 67 ticks in current C integer arithmetic. The port source explicitly labels that formula uncertain.',
            'Playback stops at the excerpt end by default. Optional repeat is a review control, not an asserted source loop.'],
        source_pins=[dict(path=p,sha256=sha((ROOT/p).read_bytes())) for p in paths],
        scripts={k:{a:v for a,v in r.items() if a!='commands'} for k,r in trace.items()})
    (HERE / 'color-sequence.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    template = (HERE / 'color-sequence-template.html').read_text(encoding='utf-8')
    (HERE / 'color-sequence-review.html').write_text(template.replace('__SEQUENCE_DATA__',json.dumps(data).replace('</','<\\/')),encoding='utf-8')
    print(json.dumps(dict(steps=len(steps),duration_ms=elapsed,frame_order=[s['frame'] for s in steps],sprites=len(sprites),pngs_unchanged=True)))

if __name__ == '__main__':
    build()
