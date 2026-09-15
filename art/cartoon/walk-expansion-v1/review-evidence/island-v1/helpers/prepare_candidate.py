"""Prepare a private six-path overlay; preserve every current archive member."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import zipfile
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
from art_common import check_duplicates, inspect_png

FRAMES = [11, 19, 20, 21, 22, 23]
CANVASES = [[64, 156], [64, 152], [48, 150], [64, 150], [64, 148], [64, 156]]
PREFIX = 'data/styles/cartoon/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exports', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print('WITNESS prepare_candidate.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    base = REPO / 'assets/scrantic_data.zip'
    baseline = REPO / 'build/rear-native-capture/baseline-v2'
    expected = json.loads((baseline / 'full/report.json').read_bytes())
    build = json.loads((baseline / 'build.json').read_bytes())
    recipe_raw = (args.exports / 'recipe.json').read_bytes()
    report_raw = (args.exports / 'export-report.json').read_bytes()
    recipe, report = json.loads(recipe_raw), json.loads(report_raw)
    require(not args.output.exists(), 'candidate-output-exists')
    require(sha(base.read_bytes()) == expected['archive_sha256'], 'production-archive-identity')
    require(sha((baseline / 'rear_route_probe').read_bytes()) == build['executable_sha256'], 'baseline-executable-identity')
    require(report['preview_only'] is False and report['runtime_sprites_written'] is True
            and report['runtime_fit_all_source_centers'] is True, 'runtime-export-required')
    require([r['frame'] for r in report['frames']] == FRAMES
            and [r['frame'] for r in recipe['frames']] == FRAMES, 'candidate-six-frames')
    require(recipe['scale_exact'] == {'numerator': 1, 'denominator': 10}
            and recipe['normalization'] == 'none', 'candidate-fixed-scale')
    payload, selections = {}, []
    for frame, canvas, row, recipe_row in zip(FRAMES, CANVASES, report['frames'], recipe['frames']):
        path = f'BMP/JOHNWALK.BMP/{frame:03}.png'
        raw = (args.exports / path).read_bytes()
        info = inspect_png(raw, path, tuple(canvas))
        require(info['color_type'] == 6 and row['runtime_canvas'] == canvas
                and row['source_centers_fit_runtime'] is True, f'candidate-canvas:{frame:03}')
        filtered = row['filtered_alpha8_bounds_hd_exclusive']
        require(filtered[0] >= 0 and filtered[1] >= 0 and filtered[2] <= canvas[0]
                and filtered[3] <= canvas[1], f'candidate-filtered-fit:{frame:03}')
        padded_raw = (args.exports / 'padded' / f'{frame:03}.png').read_bytes()
        require(sha(padded_raw) == row['padded_png_sha256'], f'candidate-padded-identity:{frame:03}')
        with Image.open(io.BytesIO(padded_raw)) as padded, Image.open(io.BytesIO(raw)) as runtime:
            pad = report['padding_hd']
            crop = padded.crop((pad, pad, pad + canvas[0], pad + canvas[1]))
            require(crop.convert('RGBA').tobytes() == runtime.convert('RGBA').tobytes(), f'candidate-runtime-crop:{frame:03}')
        source = REPO / 'art/cartoon/walk-expansion-v1' / recipe_row['source']
        require(sha(source.read_bytes()) == recipe_row['source_sha256'] == row['source_sha256'], f'candidate-source:{frame:03}')
        require(row['affine_forward'] == recipe_row['affine_forward'], f'candidate-affine:{frame:03}')
        payload[PREFIX + path] = raw
        selections.append({'frame': frame, 'path': PREFIX + path, 'png_sha256': sha(raw),
                           'source': recipe_row['source'], 'source_sha256': row['source_sha256'],
                           'canvas': canvas, 'affine_forward': row['affine_forward']})
    with zipfile.ZipFile(base) as source:
        check_duplicates(source)
        existing = {n: sha(source.read(n)) for n in source.namelist()}
        require(not (payload.keys() & existing.keys()), 'candidate-path-already-present')
    args.output.mkdir(parents=True)
    target = args.output / 'scrantic_data.zip'
    shutil.copyfile(base, target)
    with zipfile.ZipFile(target, 'a') as archive:
        for name, raw in sorted(payload.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(target) as candidate:
        check_duplicates(candidate)
        require(set(candidate.namelist()) == existing.keys() | payload.keys(), 'candidate-member-set')
        for name, digest in existing.items():
            require(sha(candidate.read(name)) == digest, 'preserved-member:' + name)
        for name, raw in payload.items():
            require(candidate.read(name) == raw, 'candidate-member:' + name)
    require(sha(base.read_bytes()) == expected['archive_sha256'], 'production-archive-preserved')
    evidence = {'scope': 'Private native review only. No production promotion or script overrides.',
                'base_archive_sha256': expected['archive_sha256'], 'archive_sha256': sha(target.read_bytes()),
                'baseline_executable_sha256': build['executable_sha256'], 'all_existing_members_preserved': len(existing),
                'new_paths': selections, 'recipe_sha256': sha(recipe_raw), 'export_report_sha256': sha(report_raw),
                'source_sha256': sha(Path(__file__).read_bytes())}
    (args.output / 'preparation.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\n')
    shutil.copyfile(args.exports / 'recipe.json', args.output / 'recipe.json')
    shutil.copyfile(args.exports / 'export-report.json', args.output / 'export-report.json')
    print(f'PASS private candidate: {len(existing)} unchanged members, exactly six additions', flush=True)


if __name__ == '__main__':
    main()
