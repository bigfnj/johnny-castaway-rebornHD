"""Fixed family transforms of approved white foam into native low-tide canvases."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

import PIL
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HIGH = 'art/cartoon/shoreline-repair-v1/integrated-shore-v1'
LOW = 'art/cartoon/low-tide-v1'
FILTER = 'art/cartoon/seasonal-v1/export.py'
FILTER_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
MASK = 'art/cartoon/shoreline-repair-v1/foam-contact-v2/export.py'
MASK_SHA = 'fae28aba1181761777ae4ed43e088fb6a1cc51b08f20db39135ac81fe4ae1445'
ARCHIVE = 'assets/scrantic_data.zip'
ARCHIVE_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
GROUND_MEMBER = 'data/styles/cartoon/BMP/BACKGRND.BMP/000.png'
GROUND_SHA = '22b426952abb1877e7c77111da0f4f0826dc86ff7a993c4390156c0f55166d9d'
BACKGROUND = LOW + '/native-v1/images/prewave-candidate.png'
BACKGROUND_SHA = '3f39d67fff987f6d7ed8c99cdf138694a3da4ef34be3c954392366ddec512dd4'
AUDIT_MARGIN = 128
FAMILIES = {
    'left': {'frames': [30,31,32], 'sources': [3,4,5], 'scale': 1.5,
             'translation': [6,-6], 'world_origin': [466,646],
             'basis': 'Uniform enlargement of the approved left curve across the longer low beach; a shared upward translation retains phase030 bottom fringe.'},
    'center': {'frames': [33,34,35], 'sources': [6,7,8], 'scale': .23,
               'translation': [0,-90], 'world_origin': [734,712],
               'basis': 'One direct raw-source resample at92% of former displayed scale fits all three phases in the fixed56HD height; translation aligns the crescent with the new beach front.'},
    'right': {'frames': [36,37,38], 'sources': [9,10,11], 'scale': 1.1,
              'translation': [-4,8], 'world_origin': [1116,646],
              'basis': 'Uniform enlargement and shared placement wrap the right low-shore tip without cropping any phase.'},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def encode(obj):
    return (json.dumps(obj, indent=2) + '\n').encode('utf-8')


def png(im):
    b = io.BytesIO()
    im.save(b, format='PNG', compress_level=9)
    return b.getvalue()


def image(data):
    with Image.open(io.BytesIO(data)) as im:
        require(im.mode == 'RGBA', 'input image: expected RGBA')
        return im.copy()


def load_tool(path, digest, name):
    require(sha((ROOT/path).read_bytes()) == digest, path + ': helper hash differs')
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_path(frame):
    if frame == 7:
        return HIGH + '/foam-shading-v1/007-raw-v1.png'
    if frame in (6,8):
        return HIGH + f'/foam-refresh-v1/{frame:03}-raw.png'
    return HIGH + f'/side-fit-v1/candidates/v1/unmasked/{frame:03}.png'


def rows():
    result = []
    for name, family in FAMILIES.items():
        s = family['scale']
        tx,ty = family['translation']
        for frame, source in zip(family['frames'], family['sources']):
            canvas = [256 if frame == 31 else 240,96] if name == 'left' else ([352,56] if name == 'center' else [176,96])
            result.append({'frame':frame, 'family':name, 'source_frame':source,
                'source':source_path(source), 'path':f'BMP/BACKGRND.BMP/{frame:03}.png',
                'runtime_canvas':canvas, 'world_origin':family['world_origin'],
                'affine_forward':[s,0,tx,0,s,ty]})
    return result


def prepared():
    files = [FILTER, MASK, BACKGROUND, LOW+'/native-v1/prewave/summary.json',
        LOW+'/native-v1/prewave/candidate/report.json', LOW+'/static-v2/export.json',
        LOW+'/static-v2/BMP/BACKGRND.BMP/001.png', LOW+'/static-v2/BMP/BACKGRND.BMP/002.png',
        LOW+'/reference/source.json', HIGH+'/side-fit-v1/recipe-v1.json',
        HIGH+'/side-fit-v1/candidates/v1/export-report.json', HIGH+'/foam-refresh-v1/recipe-v2.json',
        HIGH+'/foam-shading-v1/recipe-v1.json']
    files += [r['source'] for r in rows()]
    return {'schema_version':1, 'accepted':False,
        'scope':'Technical reuse proposal. Native motion and human acceptance pending.',
        'pillow_version':PIL.__version__, 'families':FAMILIES, 'frames':rows(),
        'source_bindings':{p:sha((ROOT/p).read_bytes()) for p in files},
        'archive':ARCHIVE, 'archive_sha256':ARCHIVE_SHA,
        'ground_member':GROUND_MEMBER, 'ground_member_sha256':GROUND_SHA,
        'ground_layers':[{'path':GROUND_MEMBER, 'world_origin':[540,548]},
            {'path':LOW+'/static-v2/BMP/BACKGRND.BMP/001.png','world_origin':[498,606]},
            {'path':LOW+'/static-v2/BMP/BACKGRND.BMP/002.png','world_origin':[300,656]}],
        'resampling':'One uniform premultiplied RGBa bicubic8x/Lanczos pass per source. No phase-specific fitting, source crop, color painting or thresholds.',
        'visibility':'Frozen ground-alpha visibility mask, with RGB exactly unchanged after resampling. This offshore interpretation does not replicate original sand-bearing wash.',
        'audit_margin_hd':AUDIT_MARGIN,
        'preview':'Exact world-coordinate software overlay on the native pre-wave background. Three aligned family-phase combinations are static studies, not the engine update sequence or native motion proof.'}


def validate(recipe):
    require(recipe['frames'] == rows() and recipe['families'] == FAMILIES, 'recipe: fixed family transform or frame mapping differs')
    require(recipe['accepted'] is False and recipe['pillow_version'] == PIL.__version__, 'recipe: proposal/version contract differs')
    for path,digest in recipe['source_bindings'].items():
        require(sha((ROOT/path).read_bytes()) == digest, path + ': source binding differs')
    require(recipe == prepared(), 'recipe: source/placement contract differs')
    require(sha((ROOT/ARCHIVE).read_bytes()) == ARCHIVE_SHA, 'archive: current47-asset baseline differs')
    require(recipe['source_bindings'][BACKGROUND] == BACKGROUND_SHA, 'background: native pre-wave identity differs')
    summary = json.loads((ROOT/(LOW+'/native-v1/prewave/summary.json')).read_bytes())
    require(summary['cases']['candidate']['prewave_png_sha256'] == BACKGROUND_SHA, 'background: native summary differs')


def bounds(alpha, minimum):
    b = alpha.point(lambda v:255 if v >= minimum else 0).getbbox()
    return list(b) if b else None


def render(recipe, selected=None):
    validate(recipe)
    filt = load_tool(FILTER,FILTER_SHA,'low_wave_filter')
    mask = load_tool(MASK,MASK_SHA,'low_wave_mask')
    ground = Image.new('RGBA',(1280,960))
    with zipfile.ZipFile(ROOT/ARCHIVE) as archive:
        raw = archive.read(GROUND_MEMBER)
    require(sha(raw) == GROUND_SHA, 'ground000: member hash differs')
    ground.alpha_composite(image(raw),(540,548))
    for frame,origin in ((1,(498,606)),(2,(300,656))):
        ground.alpha_composite(image((ROOT/(LOW+f'/static-v2/BMP/BACKGRND.BMP/{frame:03}.png')).read_bytes()),origin)
    outputs, records, sprites = {}, [], {}
    selected = set(selected or range(30,39))
    for row in recipe['frames']:
        frame = row['frame']
        if frame not in selected:
            continue
        source = image((ROOT/row['source']).read_bytes())
        w,h = row['runtime_canvas']
        s,_,tx,_,_,ty = row['affine_forward']
        # The audit surrounds the entire transformed source, not merely the runtime crop.
        m = AUDIT_MARGIN
        require(tx >= -m and ty >= -m and tx+s*source.width <= w+m and ty+s*source.height <= h+m,
                f'{frame:03}: full source exceeds audit coverage')
        padded = filt.resample(source,[w+2*m,h+2*m],[s,0,tx+m,0,s,ty+m])
        crop = (filt.PAD+m,filt.PAD+m,filt.PAD+m+w,filt.PAD+m+h)
        outside = padded.getchannel('A')
        outside.paste(0,crop)
        histogram = outside.histogram()
        require(outside.getextrema()[1] == 0, f'{frame:03}: filtered alpha outside runtime canvas')
        unmasked = padded.crop(crop)
        retained, details = mask.occlude(unmasked,ground,row['world_origin'],[0,0,1280,960])
        require(retained.convert('RGB').tobytes() == unmasked.convert('RGB').tobytes(), f'{frame:03}: visibility mask changed RGB')
        require(any(retained.getchannel('A').histogram()[8:]), f'{frame:03}: visible foam vanished')
        sprites[frame] = retained
        outputs[row['path']] = png(retained)
        outputs[f'unmasked/{frame:03}.png'] = png(unmasked)
        outputs[f'audit/{frame:03}.png'] = png(padded)
        alpha_before = unmasked.getchannel('A'); alpha_after = retained.getchannel('A')
        records.append({**row, 'source_sha256':recipe['source_bindings'][row['source']],
            'candidate_png_sha256':sha(outputs[row['path']]), 'source_canvas':list(source.size),
            'unmasked_alpha1_bounds':bounds(alpha_before,1), 'runtime_alpha1_bounds':bounds(alpha_after,1),
            'runtime_alpha8_bounds':bounds(alpha_after,8), 'outside_runtime_max_alpha':outside.getextrema()[1],
            'outside_runtime_nonzero_pixels':sum(histogram[1:]), 'outside_runtime_alpha8_pixels':sum(histogram[8:]),
            'unmasked_alpha_sum':sum(v*n for v,n in enumerate(alpha_before.histogram())),
            'runtime_alpha_sum':sum(v*n for v,n in enumerate(alpha_after.histogram())),
            'post_resample_rgb_unchanged':True, 'visibility':details})
    if selected == set(range(30,39)):
        background = Image.open(ROOT/BACKGROUND).convert('RGBA')
        sheet = Image.new('RGB',(840,690),(238,238,230))
        draw = ImageDraw.Draw(sheet)
        for phase in range(3):
            preview = background.copy()
            for name,family in FAMILIES.items():
                preview.alpha_composite(sprites[family['frames'][phase]],family['world_origin'])
            outputs[f'preview/phase-{phase}.png'] = png(preview)
            draw.text((8,phase*230+3),f'Family phase {phase+1}: static placement study, no timing claim',fill=(0,0,0))
            sheet.paste(preview.crop((440,580,1280,790)),(0,phase*230+20))
        outputs['preview/phases.png'] = png(sheet)
    report = {'schema_version':1,'status':'TECHNICAL_EXPORTED','accepted':False,
        'scope':recipe['scope'], 'preview_scope':recipe['preview'], 'exporter_sha256':sha(Path(__file__).read_bytes()),
        'recipe_sha256':sha(encode(recipe)), 'resample_count_per_frame':1, 'frames':records,
        'ground_union_rgba_sha256':sha(ground.tobytes()),
        'outputs_sha256':{p:sha(raw) for p,raw in outputs.items()}}
    return outputs,report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare',action='store_true')
    p.add_argument('--recipe',type=Path,default=HERE/'recipe-v1.json')
    p.add_argument('--output',type=Path,default=HERE/'candidates/v1')
    p.add_argument('--phase',choices=['smoke','full'],default='full')
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    print('WITNESS low-wave-reuse '+sha(Path(__file__).read_bytes()))
    try:
        if a.prepare:
            require(not a.recipe.exists(),'recipe: refusing overwrite')
        recipe=prepared() if a.prepare else json.loads(a.recipe.read_bytes())
        outputs,report=render(recipe,[30,33,36] if a.phase=='smoke' else None)
        outputs['export-report.json']=encode(report)
        if not a.check:
            require(not a.output.exists(),'output: refusing overwrite')
        for path,raw in outputs.items():
            dest=a.output/path
            if a.check:
                require(dest.read_bytes()==raw,path+': replay differs')
            else:
                dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw)
        if a.prepare:
            a.recipe.write_bytes(encode(recipe))
        print('PASS '+a.phase+' '+json.dumps({'frames':len(report['frames']), 'recipe_sha256':report['recipe_sha256']}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print('FAIL '+str(e),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
