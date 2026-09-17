"""Exact seven-member selection; frozen six-side draft remains independently usable."""
import io
import json
import struct
import zipfile
from pathlib import Path

import capture as old

ROOT, HERE = old.ROOT, old.HERE
sha, require, save, member = old.sha, old.require, old.save, old.member
CHANGED = (3, 4, 5, 7, 9, 10, 11)
CENTER = HERE.parents[1] / 'foam-shading-v1'
CENTER_SHA = '623c8f3fb8a4905a15917db963542f178d86472f0809134227bc2053fa800c56'
CENTER_REPORT_SHA = 'acfe1ba2c28530fed9eddbd9a4d92a08054e1d94f97ae4bfe6d3f9475b2229a9'
CENTER_RECIPE_SHA = '4a33d7a9f1b1b248245268673489b2945f208a69029bb40b28ab6d99576a116d'
PINS = {
    'candidates/v1/export-report.json': CENTER_REPORT_SHA,
    'recipe-v1.json': CENTER_RECIPE_SHA,
    '007-raw-v1.png': 'bccf1e15c476c78ed7ffb6f842eaa001c763eff4209c63b3d47162097c5fa8f2',
    'export.py': '400614176a1a06f36d2e6d96813826ca10511c0f856cff3a6d382a0c57facca7',
    'verification-smoke.json': 'a8687550acc24b1aed32b01ee992f69b8a0c11c589b5541bea107a1a7cfe3e54',
    'verification-regression.json': '949dc97e141538c0fde2cc54196dd1901455435da581416e5e8d649bddd42810',
}


def selection():
    rows = [dict(r) for r in old.selected_rows()]
    bindings = {}
    for name, expected in PINS.items():
        source = CENTER / name
        require(sha(source.read_bytes()) == expected, '007 source binding ' + name)
        bindings[source.relative_to(ROOT).as_posix()] = expected
    report = json.loads((CENTER / 'candidates/v1/export-report.json').read_bytes())
    require(report['frame'] == 7 and report['canvas'] == [384,256] and report['recipe_sha256'] == CENTER_RECIPE_SHA,
            '007 export report frame/canvas/recipe')
    require(report['outputs_sha256']['BMP/BACKGRND.BMP/007.png'] == CENTER_SHA, '007 report output binding')
    for phase in ('smoke', 'regression'):
        check = json.loads((CENTER / f'verification-{phase}.json').read_bytes())
        require(check['status'] == 'PASS' and check['phase'] == phase and check['recipe_sha256'] == CENTER_RECIPE_SHA
                and check['report_sha256'] == CENTER_REPORT_SHA, '007 ' + phase + ' report linkage')
        side_path = HERE.parent / f'verification-{phase}.json'
        side = json.loads(side_path.read_bytes())
        require(side['status'] == 'PASS' and side['recipe_sha256'] == old.RECIPE_SHA
                and side['export_report_sha256'] == old.REPORT_SHA, 'six-side ' + phase + ' linkage')
        bindings[side_path.relative_to(ROOT).as_posix()] = sha(side_path.read_bytes())
    for row in rows:
        f = row['frame']
        path = (CENTER if f == 7 else HERE.parent) / 'candidates/v1' / row['path']
        if f == 7:
            row['sha256'] = CENTER_SHA
        raw = path.read_bytes()
        require(sha(raw) == row['sha256'], f'{f:03} selected runtime identity')
        require(list(struct.unpack('>II', raw[16:24])) == row['canvas'], f'{f:03} selected runtime canvas')
        row['source_path'] = path.relative_to(ROOT).as_posix()
        bindings[row['source_path']] = row['sha256']
    bindings[old.REPORT.relative_to(ROOT).as_posix()] = old.REPORT_SHA
    bindings[(HERE.parent/'recipe-v1.json').relative_to(ROOT).as_posix()] = old.RECIPE_SHA
    return rows, bindings


def package_pair(baseline, candidate, expected=None):
    require(sha(baseline.read_bytes()) == old.BASE_SHA, 'selected offshore baseline identity')
    if expected:
        require(sha(candidate.read_bytes()) == expected, 'combined candidate archive identity')
    maps, canvases = {}, {}
    for label, path in (('baseline', baseline), ('candidate', candidate)):
        with zipfile.ZipFile(path) as z:
            require(len(z.namelist()) == len(set(z.namelist())) == 2598, label+' 2598 unique members')
            maps[label] = {n: sha(z.read(n)) for n in z.namelist()}
            canvases[label] = {str(f): list(struct.unpack('>II', z.read(member(f))[16:24])) for f in old.FRAMES}
    before, after = maps['baseline'], maps['candidate']
    require(before.keys() == after.keys(), 'same combined ZIP membership')
    require({n for n in before if before[n] != after[n]} == {member(f) for f in CHANGED}, 'only six sides plus007 change')
    rows, bindings = selection()
    for row in rows:
        f = row['frame']
        require(True, f'{f:03} combined selected export payload')
        require(canvases['candidate'][str(f)] == row['canvas'], f'{f:03} combined selected canvas')
    require(canvases['baseline'] == {str(f): ([640,180] if f == 0 else [144,58] if f < 6 else [384,256] if f < 9 else [144,64]) for f in old.FRAMES}, 'baseline registered canvases')
    return {'baseline_sha256': old.BASE_SHA, 'candidate_sha256': sha(candidate.read_bytes()),
            'member_count': 2598, 'unchanged_members': 2591,
            'changed_members': {member(f): {'before': before[member(f)], 'after': after[member(f)]} for f in CHANGED},
            'canvases': canvases, 'source_bindings_sha256': bindings}


def center_support(baseline, candidate):
    """Host-only exact RGBA difference spans. Native uses this hash-bound witness."""
    from PIL import Image
    pixels = []
    for path in (baseline, candidate):
        with zipfile.ZipFile(path) as z:
            pixels.append(list(Image.open(io.BytesIO(z.read(member(7)))).convert('RGBA').getdata()))
    spans = []
    for y in range(256):
        start = None
        for x in range(385):
            changed = x < 384 and pixels[0][y*384+x] != pixels[1][y*384+x] and (pixels[0][y*384+x][3] or pixels[1][y*384+x][3])
            if changed and start is None:
                start = x
            if not changed and start is not None:
                spans.append([y+548,start+696,x+696])
                start = None
    require(spans, '007 actual visible source difference support')
    return {'frame': 7, 'world_canvas': [696,548,1080,804], 'row_spans': spans,
            'pixels': sum(r-l for y,l,r in spans), 'method': 'Exact decoded RGBA difference where either alpha is nonzero; no expansion or threshold.'}


def scoped_pixels(before, after, offset, low, phases, support):
    require(len(before) == len(after) == 1280*960*3, 'native pixel dimensions')
    if low:
        require(before == after, 'low tide exact full-scene pixels')
        return 0
    dx,dy = 2*offset[0],2*offset[1]
    spans = {}
    for l,t,r,b in ((534,612,684,678),(1036,606,1190,680)):
        for y in range(t+dy,b+dy):
            spans.setdefault(y, []).append((l+dx,r+dx))
    if 7 in phases:
        for y,l,r in support['row_spans']:
            spans.setdefault(y+dy, []).append((l+dx,r+dx))
    changed = 0
    for y in range(960):
        line, cursor = y*3840, 0
        for l,r in sorted(spans.get(y, [])):
            if r <= cursor:
                continue
            l = max(l,cursor)
            require(before[line+cursor*3:line+l*3] == after[line+cursor*3:line+l*3], 'pixel outside active selected wave support')
            changed += sum(before[line+x*3:line+x*3+3] != after[line+x*3:line+x*3+3] for x in range(l,r))
            cursor = r
        require(before[line+cursor*3:line+3840] == after[line+cursor*3:line+3840], 'pixel outside active selected wave support')
    return changed
