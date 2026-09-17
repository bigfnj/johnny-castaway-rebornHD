"""Fixed cloud exports and a private two-member additive candidate archive."""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_SHA = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
FILTER_PATH = 'art/cartoon/seasonal-v1/export.py'
FILTER_SHA = '7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
CONFIG = {
    16: {'canvas': [384, 114], 'affine': [21 / 64, 0, -63.3125, 0, 21 / 64, -111.546875],
         'anchor': [196, 343], 'raw_sha256': 'f16bd7802c23c3dd6040e8d5ddd181ad880e87ecf23e071bb004b9690a52be4e'},
    17: {'canvas': [528, 152], 'affine': [25 / 64, 0, -37.28125, 0, 25 / 64, -130.640625],
         'anchor': [98, 337], 'raw_sha256': 'c9343aa097d1700cb736287e2e9af36ceaf6affec799913368171fb85c987a58'},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def lf_sha(data):
    return sha(data.replace(b'\r\n', b'\n'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(data):
    return (json.dumps(data, indent=2) + '\n').encode()


def rel(path):
    return path.resolve().relative_to(ROOT).as_posix()


def resolve_reference(recorded, root=None):
    """Keep exact historical request text; read its validated batch suffix here."""
    root = ROOT if root is None else Path(root)
    marker = 'art/cartoon/clouds-v1/'
    normalized = recorded.replace('\\', '/')
    require(normalized.count(marker) == 1, 'recorded reference: missing or ambiguous batch suffix')
    prefix, suffix = normalized.split(marker)
    require((not prefix or prefix.endswith('/')) and suffix and
            all(part not in ('', '.', '..') and ':' not in part for part in suffix.split('/')),
            'recorded reference: escaping or invalid batch path')
    path = (root / marker / suffix).resolve()
    path.relative_to((root / marker).resolve())
    return path


def filter_module():
    require(lf_sha((ROOT / FILTER_PATH).read_bytes()) == FILTER_SHA, FILTER_PATH + ': filter source identity differs')
    spec = importlib.util.spec_from_file_location('cloud_frozen_filter', ROOT / FILTER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare():
    reference = json.loads((HERE / 'reference/source.json').read_bytes())
    inputs = {rel(HERE / 'reference/source.json'): sha((HERE / 'reference/source.json').read_bytes())}
    frames = []
    initial = json.loads((HERE / 'generation/requests.json').read_bytes())
    for frame, config in CONFIG.items():
        source = HERE / f'generation/{frame:03}-generated-v2.png'
        request = HERE / f'generation/{frame:03}-v2-request.json'
        require(sha(source.read_bytes()) == config['raw_sha256'], f'{frame:03}: selected raw identity differs')
        document = json.loads(request.read_bytes())['request']
        refs = [resolve_reference(name) for name in document['referenced_image_paths']]
        first = next(row for row in initial['requests'] if int(row['slot']) == frame)
        ancestor_refs = [resolve_reference(name) for name in first['referenced_image_paths']]
        fallback = next(row for row in reference['frames'] if row['resource'] == 'BACKGRND.BMP' and row['frame'] == frame)
        for path in [source, request, HERE / 'generation/requests.json'] + refs + ancestor_refs:
            inputs[rel(path)] = sha(path.read_bytes())
        frames.append({'frame': frame, 'path': f'BMP/BACKGRND.BMP/{frame:03}.png',
                       'source': rel(source), 'source_sha256': config['raw_sha256'], 'generated_canvas': [1536, 1024],
                       'runtime_canvas': config['canvas'], 'affine_forward': config['affine'],
                       'raw_anchor': config['anchor'], 'target_anchor': [1, 1],
                       'request': rel(request), 'request_sha256': sha(request.read_bytes()),
                       'ordered_references': [{'path': rel(p), 'sha256': sha(p.read_bytes())} for p in refs],
                       'initial_request': rel(HERE / 'generation/requests.json'),
                       'ordered_initial_references': [{'path': rel(p), 'sha256': sha(p.read_bytes())} for p in ancestor_refs],
                       'fallback': {'native_canvas': fallback['canvas'], 'original_member': fallback['path'],
                                    'original_sha256': fallback['png_sha256'], 'hd_member': fallback['bundled']['hd_member'],
                                    'hd_sha256': fallback['bundled']['hd_png_sha256']}})
    module = filter_module()
    return {'schema_version': 1, 'accepted': False, 'scope': 'Technical cloud candidates pending human scene approval.',
            'normalization': 'none', 'pillow_version': PILLOW_VERSION, 'resampling': module.FILTERS,
            'filter': {'path': FILTER_PATH, 'lf_sha256': FILTER_SHA}, 'padding_hd': module.PAD,
            'baseline_archive_sha256': BASE_SHA, 'inputs_sha256': inputs, 'frames': frames}


def measure(source, padded, config, pad):
    a = np.array(source.getchannel('A'))
    y, x = np.nonzero(a >= 8)
    bounds = [int(x.min()), int(y.min()), int(x.max() + 1), int(y.max() + 1)]
    s, _, tx, _, _, ty = config['affine']
    width, height = config['canvas']
    xx = (np.arange(a.shape[1]) + .5) * s + tx
    yy = (np.arange(a.shape[0]) + .5) * s + ty
    def stats(mask):
        values = a[mask]
        return {'nonzero_source_pixels': int(np.count_nonzero(values)), 'alpha8_source_pixels': int(np.count_nonzero(values >= 8)),
                'max_alpha': int(values.max()) if len(values) else 0}
    runtime_outside = (xx[None, :] < 0) | (xx[None, :] >= width) | (yy[:, None] < 0) | (yy[:, None] >= height)
    padded_outside = (xx[None, :] < -pad) | (xx[None, :] >= width + pad) | (yy[:, None] < -pad) | (yy[:, None] >= height + pad)
    p = np.array(padded.getchannel('A'))
    outside = p.copy()
    outside[pad:pad + height, pad:pad + width] = 0
    fy, fx = np.nonzero(p >= 8)
    centers = [(bounds[0] + .5) * s + tx, (bounds[1] + .5) * s + ty,
               (bounds[2] - .5) * s + tx, (bounds[3] - .5) * s + ty]
    return {'source_alpha_extrema': [int(a.min()), int(a.max())], 'source_alpha8_bounds': bounds,
            'source_alpha8_centers_hd': centers,
            'source_alpha8_center_margins_hd': [centers[0], centers[1], width - centers[2], height - centers[3]],
            'source_centers_outside_runtime': stats(runtime_outside), 'source_centers_outside_padded': stats(padded_outside),
            'filtered_alpha8_bounds_hd': [int(fx.min()) - pad, int(fy.min()) - pad, int(fx.max() + 1) - pad, int(fy.max() + 1) - pad],
            'filtered_outside_runtime_nonzero_pixels': int(np.count_nonzero(outside)),
            'filtered_outside_runtime_alpha8_pixels': int(np.count_nonzero(outside >= 8)),
            'filtered_outside_runtime_max_alpha': int(outside.max()),
            'alpha8_source_fit': bool(centers[0] >= 0 and centers[1] >= 0 and centers[2] < width and centers[3] < height)}


def render(recipe):
    require(recipe == prepare(), 'recipe: selected source, prompt or fixed registration binding differs')
    module = filter_module()
    require(PILLOW_VERSION == '12.3.0', 'Pillow: expected12.3.0 for reproduction')
    outputs, rows = {}, []
    sheet = Image.new('RGB', (1100, 420), (72, 98, 118))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), 'Original x2 / fixed Cartoon runtime x1 | human approval pending', fill='white')
    for i, row in enumerate(recipe['frames']):
        frame = row['frame']
        source = Image.open(ROOT / row['source'])
        require(source.mode == 'RGBA' and list(source.size) == row['generated_canvas'], f'{frame:03}: source canvas or mode differs')
        padded = module.resample(source, row['runtime_canvas'], row['affine_forward'])
        width, height = row['runtime_canvas']
        runtime = padded.crop((module.PAD, module.PAD, module.PAD + width, module.PAD + height))
        outputs[row['path']] = module.png(runtime)
        outputs[f'padded/{frame:03}.png'] = module.png(padded)
        original = Image.open(HERE / f'reference/backgrnd-{frame:03}-original.png').convert('RGBA')
        original = original.resize((original.width * 2, original.height * 2), Image.Resampling.NEAREST)
        for column, image in enumerate((original, runtime)):
            x, y = 12 + column * 550, 42 + i * 180
            draw.text((x, y), f'{frame:03} ' + ('original x2' if column == 0 else 'Cartoon runtime x1'), fill='white')
            sheet.paste(image, (x, y + 20), image)
        rows.append({'frame': frame, 'path': row['path'], 'canvas': row['runtime_canvas'],
                     'sha256': sha(outputs[row['path']]), 'source_sha256': row['source_sha256'],
                     'affine_forward': row['affine_forward'], **measure(source, padded, CONFIG[frame], module.PAD)})
    outputs['comparison.png'] = module.png(sheet)
    report = {'schema_version': 1, 'accepted': False, 'exporter_lf_sha256': lf_sha(Path(__file__).read_bytes()),
              'recipe_sha256': sha(encode(recipe)), 'frames': rows,
              'scope': 'Alpha8 is diagnostic only. No threshold, keying, recolor, alpha painting or per-axis warp is applied.',
              'outputs_sha256': {name: sha(raw) for name, raw in outputs.items()}}
    outputs['export-report.json'] = encode(report)
    return outputs, report


def package(baseline, outputs):
    raw = baseline.read_bytes()
    require(sha(raw) == BASE_SHA, 'baseline archive: identity differs')
    extra = {'data/styles/cartoon/' + CONFIG_PATH: outputs[CONFIG_PATH] for CONFIG_PATH in [f'BMP/BACKGRND.BMP/{n:03}.png' for n in CONFIG]}
    result = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as before, zipfile.ZipFile(result, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as after:
        require(len(before.namelist()) == len(set(before.namelist())) == 2612, 'baseline archive: member count or uniqueness differs')
        require(not set(extra).intersection(before.namelist()), 'baseline archive: cloud members already exist')
        for info in before.infolist():
            after.writestr(copy.copy(info), before.read(info.filename))
        for name, data in sorted(extra.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            after.writestr(info, data, compresslevel=9)
    data = result.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as before, zipfile.ZipFile(io.BytesIO(data)) as after:
        require(len(after.namelist()) == 2614, 'candidate archive: member count differs')
        require(all(before.read(n) == after.read(n) for n in before.namelist()), 'candidate archive: prior payload changed')
        require(all(after.read(n) == p for n, p in extra.items()), 'candidate archive: selected cloud payload differs')
        count = sum(n.startswith('data/styles/cartoon/') and n.endswith('.png') for n in after.namelist())
        require(count == 63, 'candidate archive: Cartoon count differs')
    return data, {'baseline_sha256': BASE_SHA, 'candidate_sha256': sha(data), 'members': 2614,
                  'cartoon_png_members': count, 'unchanged_baseline_payloads': 2612,
                  'added_members_sha256': {n: sha(p) for n, p in extra.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe.json')
    parser.add_argument('--output', type=Path, default=HERE / 'export')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'assets/scrantic_data.zip')
    parser.add_argument('--candidate', type=Path, default=ROOT / 'build/clouds-v1/candidate.zip')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS cloud-export ' + lf_sha(Path(__file__).read_bytes()))
    try:
        recipe = prepare() if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        candidate, pack_report = package(args.baseline, outputs)
        outputs['package-report.json'] = encode({**pack_report, 'recipe_sha256': sha(encode(recipe)),
                                                'export_report_sha256': sha(outputs['export-report.json'])})
        if args.check:
            for name, raw in outputs.items():
                require((args.output / name).read_bytes() == raw, name + ': replay differs')
            require(args.candidate.read_bytes() == candidate, 'candidate archive: replay differs')
        else:
            require(not args.output.exists() and not args.candidate.exists(), 'output: refusing to overwrite')
            require(not args.prepare or not args.recipe.exists(), 'recipe: refusing to overwrite')
            for name, raw in outputs.items():
                target = args.output / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            args.candidate.parent.mkdir(parents=True, exist_ok=True)
            args.candidate.write_bytes(candidate)
            if args.prepare:
                args.recipe.write_bytes(encode(recipe))
        print('PASS cloud-export ' + json.dumps(pack_report))
        return 0
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print('FAIL ' + str(exc))
        return 1


if __name__ == '__main__':
    sys.exit(main())
