"""Integer placement of complete original side foam, then the frozen alpha mask.

Ground and selected center PNGs are copied exactly. Only six side sprites change;
there is no resampling, paint, scale change, or relocation of already-masked foam.
"""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
SELECTED = HERE.parent / 'foam-refresh-v1/candidates/v2'
PRIOR_RECIPE = HERE.parent / 'foam-refresh-v1/recipe-v2.json'
MASK = HERE.parents[1] / 'foam-contact-v2/export.py'
ARCHIVE = ROOT / 'assets/scrantic_data.zip'
ARCHIVE_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
MASK_SHA = 'fae28aba1181761777ae4ed43e088fb6a1cc51b08f20db39135ac81fe4ae1445'
RECIPE_SHA = '53a6ba750c90c9c0b721864d103bd565ae332c6e5a40b00ae98cdc6eb171f4b4'
REPORT_SHA = 'ceb1dd987098c6f5ee36a77988009b1f290e44f421bfd7f08cd275c34bca999d'
SIDES = (3, 4, 5, 9, 10, 11)
UNCHANGED = (0, 6, 7, 8)
GROUND_BOX = [540, 548, 1180, 728]
PLACEMENTS = {
    3: {'canvas': [150, 66], 'offset_hd': [-6, 0], 'paste': [0, 8],
        'shift': [-6, 8], 'id': 'cartoon-island-left-foam-v1'},
    9: {'canvas': [154, 74], 'offset_hd': [0, 0], 'paste': [10, 10],
        'shift': [10, 10], 'id': 'cartoon-island-right-foam-v1'},
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def encode(value):
    return (json.dumps(value, indent=2) + '\n').encode('utf-8')


def png(image):
    out = io.BytesIO()
    image.save(out, format='PNG', compress_level=9)
    return out.getvalue()


def load_mask():
    require(sha(MASK.read_bytes()) == MASK_SHA, 'mask: frozen helper differs')
    spec = importlib.util.spec_from_file_location('side_fit_frozen_visibility', MASK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stats(image):
    alpha = image.getchannel('A')
    histogram = alpha.histogram()
    return {'nonzero_pixels': sum(histogram[1:]), 'alpha8_pixels': sum(histogram[8:]),
            'alpha_sum': sum(i*n for i, n in enumerate(histogram)),
            'maximum_alpha': alpha.getextrema()[1], 'nonzero_bounds': alpha.getbbox(),
            'alpha8_bounds': alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()}


def prepared():
    load_mask()
    require(sha(ARCHIVE.read_bytes()) == ARCHIVE_SHA, 'archive: original unmasked source differs')
    require(sha(PRIOR_RECIPE.read_bytes()) == RECIPE_SHA, 'selected recipe identity differs')
    require(sha((SELECTED / 'export-report.json').read_bytes()) == REPORT_SHA, 'selected report identity differs')
    prior = json.loads(PRIOR_RECIPE.read_bytes())
    report = json.loads((SELECTED / 'export-report.json').read_bytes())
    pins = report['outputs_sha256']
    rows = []
    for original in prior['frames']:
        row = copy.deepcopy(original)
        frame, path = row['frame'], row['path']
        require(sha((SELECTED / path).read_bytes()) == pins[path], f'{frame:03}: selected PNG differs')
        row['previous_selected_png_sha256'] = pins[path]
        if frame in SIDES:
            family = 3 if frame < 6 else 9
            place = PLACEMENTS[family]
            source_canvas = list(row['canvas'])
            logical = row['logical_origin_hd']
            origin = [a+b for a, b in zip(logical, place['offset_hd'])]
            row.update(source_canvas=source_canvas, canvas=place['canvas'],
                       asset_offset_hd=place['offset_hd'], source_paste_hd=place['paste'],
                       source_translation_hd=place['shift'],
                       world_box=[*origin, origin[0]+place['canvas'][0], origin[1]+place['canvas'][1]],
                       footprint={'id': place['id'], 'canvas': place['canvas'], 'offset_hd': place['offset_hd']},
                       role='original unmasked foam, integer placed then visibility masked')
            row.pop('sha256', None)
        else:
            row['sha256'] = pins[path]
        rows.append(row)
    return {'schema_version': 1, 'accepted': False,
            'scope': 'Side-wave placement comparison only; human native review pending.',
            'pillow_version': PIL.__version__, 'resample_count': 0, 'scale': 1,
            'archive': 'assets/scrantic_data.zip', 'archive_sha256': ARCHIVE_SHA,
            'selected_recipe': PRIOR_RECIPE.relative_to(ROOT).as_posix(), 'selected_recipe_sha256': RECIPE_SHA,
            'selected_report': (SELECTED / 'export-report.json').relative_to(ROOT).as_posix(), 'selected_report_sha256': REPORT_SHA,
            'mask_helper': MASK.relative_to(ROOT).as_posix(), 'mask_helper_sha256': MASK_SHA,
            'static_ground_world_box': GROUND_BOX, 'unchanged_frames': list(UNCHANGED),
            'operation': 'Exact unmasked source RGBA pasted at integer coordinates into transparent padding; frozen ground-alpha visibility mask recomputed at the new world position.',
            'limits': 'The visibility mask changes only foam alpha. It is not exact global translucent ground-over-foam compositing. Source cropback exactness is before this deliberate mask.',
            'frames': rows}


def render(recipe):
    expected = prepared()
    require({k:v for k,v in recipe.items() if k != 'frames'} == {k:v for k,v in expected.items() if k != 'frames'}, 'recipe: source and visibility contract differs')
    require([r['frame'] for r in recipe['frames']] == [r['frame'] for r in expected['frames']], 'recipe: frame coverage differs')
    for row, selected in zip(recipe['frames'], expected['frames']):
        pass  # executed control: placement/source binding removed
    mask = load_mask()
    ground = Image.open(SELECTED / 'BMP/BACKGRND.BMP/000.png').convert('RGBA')
    outputs, rows = {}, []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in recipe['frames']:
            frame, path = row['frame'], row['path']
            if frame in UNCHANGED:
                raw = (SELECTED / path).read_bytes()
                outputs[path] = raw
                rows.append({**row, 'sha256': sha(raw), 'byte_identical_to_selected': True})
                continue
            source_raw = archive.read(row['source_member'])
            require(sha(source_raw) == row['source_member_sha256'], f'{frame:03}: unmasked archive member differs')
            source = Image.open(io.BytesIO(source_raw)).convert('RGBA')
            require(list(source.size) == row['source_canvas'], f'{frame:03}: unmasked source canvas differs')
            x, y = row['source_paste_hd']
            canvas = Image.new('RGBA', row['canvas'], (0, 0, 0, 0))
            canvas.paste(source, (x, y))
            cropback = canvas.crop((x, y, x+source.width, y+source.height))
            require(cropback.tobytes() == source.tobytes(), f'{frame:03}: full source cropback differs')
            outside = canvas.copy()
            outside.paste((0, 0, 0, 0), (x, y, x+source.width, y+source.height))
            require(not any(outside.tobytes()), f'{frame:03}: padding is not transparent zero RGBA')
            retained, visibility = mask.occlude(canvas, ground, row['world_box'][:2], GROUND_BOX)
            require(all(a[:3] == b[:3] and b[3] <= a[3] for a, b in zip(canvas.get_flattened_data(), retained.get_flattened_data())), f'{frame:03}: visibility changed RGB or introduced alpha')
            old, _ = mask.occlude(source, ground, row['logical_origin_hd'], GROUND_BOX)
            require(png(old) == (SELECTED / path).read_bytes(), f'{frame:03}: prior selected visibility reproduction differs')
            raw = png(retained)
            outputs[path] = raw
            outputs[f'unmasked/{frame:03}.png'] = png(canvas)
            rows.append({**row, 'sha256': sha(raw), 'source_rgba_sha256': sha(source.tobytes()),
                         'source_cropback_rgba_sha256': sha(cropback.tobytes()),
                         'source_cropback_exact': True, 'source_pixels_cropped': 0,
                         'source_rectangle_in_canvas': [x, y, x+source.width, y+source.height],
                         'source_world_origin_hd': [row['world_box'][0]+x, row['world_box'][1]+y],
                         'source_coverage': stats(source), 'padded_source_coverage': stats(canvas),
                         'padding_coverage': stats(outside), 'previous_retained_coverage': stats(old),
                         'retained_coverage': stats(retained), 'visibility_measurements': visibility,
                         'previous_selected_reproduced': True})
    report = {'schema_version': 1, 'status': 'TECHNICAL_EXPORTED_PENDING_NATIVE_REVIEW', 'accepted': False,
              'exporter_sha256': sha(Path(__file__).read_bytes()), 'recipe_sha256': sha(encode(recipe)),
              'archive_sha256': ARCHIVE_SHA, 'mask_helper_sha256': MASK_SHA,
              'selected_recipe_sha256': RECIPE_SHA, 'selected_report_sha256': REPORT_SHA,
              'pillow_version': PIL.__version__, 'resample_count': 0,
              'unchanged_frames': list(UNCHANGED), 'source_pixels_cropped': 0,
              'limits': recipe['limits'], 'frames': rows,
              'outputs_sha256': {name: sha(raw) for name, raw in outputs.items()}}
    return outputs, report


def main():
    global ARCHIVE
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare', action='store_true')
    p.add_argument('--recipe', type=Path, default=HERE / 'recipe-v1.json')
    p.add_argument('--output', type=Path, default=HERE / 'candidates/v1')
    p.add_argument('--archive', type=Path, help='Optional recovered byte-identical original archive for later replay.')
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    if a.archive:
        ARCHIVE = a.archive.resolve()
    print('WITNESS side-fit ' + sha(Path(__file__).read_bytes()))
    try:
        if a.prepare:
            require(not a.recipe.exists(), 'recipe: refusing overwrite')
        recipe = prepared() if a.prepare else json.loads(a.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = encode(report)
        if not a.check:
            require(not a.output.exists(), 'output: refusing overwrite')
        for name, raw in outputs.items():
            target = a.output / name
            if a.check:
                require(target.read_bytes() == raw, name + ': exact replay differs')
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        if a.prepare:
            a.recipe.write_bytes(encode(recipe))
        print('PASS side-fit ' + json.dumps({'frames': 10, 'source_pixels_cropped': 0, 'unchanged_frames': list(UNCHANGED)}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
