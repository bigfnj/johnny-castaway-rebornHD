"""Add only the recorded arrival sprite to a private copy of the production ZIP."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import check_duplicates, inspect_png

PATH = 'BMP/JOHNWALK.BMP/018.png'
TARGET = 'data/styles/cartoon/' + PATH


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def read_candidate(exports):
    recipe_raw = (exports / 'recipe.json').read_bytes()
    report_raw = (exports / 'export-report.json').read_bytes()
    recipe, report = json.loads(recipe_raw), json.loads(report_raw)
    require(report['preview_only'] is False and report['runtime_sprites_written'] is True
            and report['runtime_fit_all_source_centers'] is True, 'runtime-export-required')
    require([r['frame'] for r in recipe['frames']] == [18]
            and [r['frame'] for r in report['frames']] == [18], 'arrival-only-frame-set')
    require(sha(recipe_raw) == report['recipe_sha256'], 'recipe-report-identity')
    require(recipe['scale_exact'] == {'numerator': 1, 'denominator': 10}
            and recipe['normalization'] == 'none', 'fixed-family-scale')
    entry, observed = recipe['frames'][0], report['frames'][0]
    raw = (exports / PATH).read_bytes()
    info = inspect_png(raw, PATH, (64, 154))
    require(info['color_type'] == 6 and observed['runtime_canvas'] == entry['runtime_canvas'] == [64, 154], 'arrival-rgba-canvas')
    require(sha(raw) == report['outputs_sha256'][PATH], 'runtime-png-identity')
    source = ROOT / 'art/cartoon/arrival-pilot-v1' / entry['source']
    require(sha(source.read_bytes()) == entry['source_sha256'] == observed['source_sha256'], 'raw-source-identity')
    require(observed['affine_forward'] == entry['affine_forward'], 'recipe-export-affine')
    filtered = observed['filtered_alpha8_bounds_hd_exclusive']
    require(filtered[0] >= 0 and filtered[1] >= 0 and filtered[2] <= 64 and filtered[3] <= 154, 'filtered-arrival-fit')
    padded_raw = (exports / 'padded/018.png').read_bytes()
    require(sha(padded_raw) == report['outputs_sha256']['padded/018.png'], 'padded-png-identity')
    with Image.open(io.BytesIO(padded_raw)) as image, Image.open(io.BytesIO(raw)) as runtime:
        pad = report['padding_hd']
        require(pad == recipe['padding_hd'] == 64, 'recorded-padding')
        require(image.crop((pad, pad, pad + 64, pad + 154)).convert('RGBA').tobytes() == runtime.convert('RGBA').tobytes(), 'runtime-is-padded-crop')
        actual = image.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
        require([actual[0] - pad, actual[1] - pad, actual[2] - pad, actual[3] - pad] == filtered, 'actual-filtered-bounds')
    return raw, recipe_raw, report_raw, {'frame': 18, 'path': TARGET, 'canvas': [64, 154],
        'png_sha256': sha(raw), 'source': entry['source'], 'source_sha256': entry['source_sha256'],
        'affine_forward': entry['affine_forward']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exports', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print('WITNESS arrival prepare_candidate.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    require(not a.output.exists(), 'preserve-candidate-output')
    binding = json.loads((OUT / 'source-reuse.json').read_bytes())
    source_zip = ROOT / 'assets/scrantic_data.zip'
    require(sha(source_zip.read_bytes()) == binding['current_archive_sha256'], 'production-archive-identity')
    exe = OUT / 'baseline/rear_route_probe'
    require(sha(exe.read_bytes()) == binding['executable_sha256'], 'baseline-executable-identity')
    raw, recipe, report, selection = read_candidate(a.exports)
    with zipfile.ZipFile(source_zip) as original:
        check_duplicates(original)
        members = {name: sha(original.read(name)) for name in original.namelist()}
        require(members == binding['archive_members'], 'all-production-members-identity')
        require(TARGET not in members, 'arrival-path-absent-in-production')
    a.output.mkdir(parents=True)
    target = a.output / 'scrantic_data.zip'
    shutil.copyfile(source_zip, target)
    with zipfile.ZipFile(target, 'a') as archive:
        info = zipfile.ZipInfo(TARGET, (1980, 1, 1, 0, 0, 0))
        archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        check_duplicates(archive)
        require(set(archive.namelist()) == set(members) | {TARGET}, 'private-member-set')
        for name, digest in members.items():
            require(sha(archive.read(name)) == digest, 'preserved-production-member:' + name)
        require(archive.read(TARGET) == raw, 'candidate-member-bytes')
    require(sha(source_zip.read_bytes()) == binding['current_archive_sha256'], 'production-archive-preserved')
    (a.output / 'recipe.json').write_bytes(recipe)
    (a.output / 'export-report.json').write_bytes(report)
    record = {'scope': 'Technical private native review only; no production or human acceptance.',
        'base_archive_sha256': binding['current_archive_sha256'], 'archive_sha256': sha(target.read_bytes()),
        'baseline_executable_sha256': binding['executable_sha256'], 'new_paths': [selection],
        'all_existing_members_preserved': len(members), 'only_added_path': TARGET,
        'recipe_sha256': sha(recipe), 'export_report_sha256': sha(report),
        'source_sha256': sha(Path(__file__).read_bytes())}
    (a.output / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'PASS private candidate: {len(members)} preserved members; only frame018 added', flush=True)


if __name__ == '__main__':
    main()
