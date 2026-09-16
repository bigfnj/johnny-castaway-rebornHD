"""Build a private three-pose package from an explicit technical export handoff."""
import argparse
import copy
import io
import json
from pathlib import Path
import zipfile
from PIL import Image
import config

ROOT, OUT, sha = config.ROOT, config.OUT, config.sha


def bound_files(value, result):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            relative = Path(value['path'])
            assert not relative.is_absolute() and '..' not in relative.parts, 'repo-relative handoff path'
            path = ROOT / relative
            assert sha(path.read_bytes()) == value['sha256'], 'handoff input identity:' + relative.as_posix()
            result[relative.as_posix()] = value['sha256']
        for child in value.values():
            bound_files(child, result)
    elif isinstance(value, list):
        for child in value:
            bound_files(child, result)


def validate_selection(selection):
    assert [row['frame'] for row in selection['frames']] == list(config.CANDIDATE_FRAMES), 'exact three connecting candidates'
    inputs = {}
    bound_files(selection, inputs)
    for row in selection['frames']:
        frame = row['frame']
        label = f'{frame:03}'
        recipe = config.load_json(ROOT / row['recipe']['path'])
        report = config.load_json(ROOT / row['export_report']['path'])
        assert len(recipe['frames']) == 1 and recipe['frames'][0]['frame'] == frame, 'selected recipe frame:' + label
        assert len(report['frames']) == 1 and report['frames'][0]['frame'] == frame, 'selected export-report frame:' + label
        rf, ef = recipe['frames'][0], report['frames'][0]
        assert report['recipe_sha256'] == row['recipe']['sha256'], 'selected report recipe binding:' + label
        assert rf['source_sha256'] == ef['source_sha256'] == row['source']['sha256'], 'selected source hash binding:' + label
        assert rf['source'] == ef['source'] == Path(row['source']['path']).name, 'selected source name binding:' + label
        assert report['outputs_sha256'][f'BMP/JOHNWALK.BMP/{label}.png'] == row['runtime']['sha256'], 'selected runtime output binding:' + label
        assert report['outputs_sha256'][f'padded/{label}.png'] == row['padded']['sha256'], 'selected padded output binding:' + label
        assert rf['runtime_canvas'] == ef['runtime_canvas'] == row['runtime']['canvas'], 'selected canvas binding:' + label
        assert rf['cap_raw'] == ef['cap_raw'] and rf['affine_forward'] == ef['affine_forward'], 'selected placement binding:' + label
        assert recipe['reference_hashes'] == report['reference_hashes'], 'selected original reference binding:' + label
        assert report['preview_only'] is False and report['runtime_sprites_written'] is True and report['runtime_fit_all_source_centers'] is True and ef['source_centers_fit_runtime'] is True, 'selected completed runtime export:' + label
    return inputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--candidate-version', type=int, default=1)
    args = parser.parse_args()
    assert args.candidate_version > 0, 'positive candidate version'
    selection_path = args.selection.resolve()
    selection = config.load_json(selection_path)
    inputs = validate_selection(selection)
    base = OUT / 'baseline-pack.zip'
    assert sha(base.read_bytes()) == config.PRODUCTION_SHA, 'exact current baseline'
    assert sha((ROOT / 'assets/scrantic_data.zip').read_bytes()) == config.PRODUCTION_SHA, 'production still unchanged'
    candidate = OUT / f'candidate-v{args.candidate_version}'
    assert not candidate.exists(), 'preserve private candidate evidence'
    added = []
    additions = {}
    for row in selection['frames']:
        frame, runtime = row['frame'], row['runtime']
        raw = (ROOT / runtime['path']).read_bytes()
        assert sha(raw) == runtime['sha256'], 'selected runtime identity:' + str(frame)
        with Image.open(io.BytesIO(raw)) as image:
            assert image.mode == 'RGBA' and list(image.size) == runtime['canvas'], 'runtime RGBA canvas:' + str(frame)
            assert image.getchannel('A').getbbox(), 'visible runtime:' + str(frame)
        member = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
        additions[member] = raw
        added.append({'frame': frame, 'member': member, 'sha256': runtime['sha256'], 'canvas': runtime['canvas']})
    candidate.mkdir()
    package = candidate / 'scrantic_data.zip'
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(package, 'x') as packed:
        names = original.namelist()
        assert len(names) == len(set(names)) and not set(additions).intersection(names), 'unique new candidate members'
        packed.comment = original.comment
        for info in original.infolist():
            packed.writestr(copy.copy(info), original.read(info.filename))
        for member, raw in additions.items():
            hd = 'data/hd/BMP/JOHNWALK.BMP/' + member.rsplit('/', 1)[1]
            with Image.open(io.BytesIO(original.read(hd))) as old, Image.open(io.BytesIO(raw)) as new:
                assert old.size == new.size, 'original-derived runtime canvas unchanged:' + member
            info = copy.copy(original.getinfo(hd))
            info.filename = info.orig_filename = member
            packed.writestr(info, raw)
    with zipfile.ZipFile(base) as original, zipfile.ZipFile(package) as packed:
        assert packed.namelist() == names + list(additions), 'only three named additions'
        assert all(original.read(name) == packed.read(name) for name in names), 'every prior production payload unchanged'
        assert all(packed.read(name) == raw for name, raw in additions.items()), 'exact selected candidate bytes'
    (candidate / 'candidate-selection.json').write_bytes(selection_path.read_bytes())
    record = {'status': 'PASS', 'scope': 'Private technical candidate only; no motion approval or production promotion.',
              'candidate_version': args.candidate_version,
              'selection_source': selection_path.relative_to(ROOT).as_posix(), 'selection_sha256': sha(selection_path.read_bytes()),
              'base_archive_sha256': config.PRODUCTION_SHA, 'archive_sha256': sha(package.read_bytes()),
              'base_member_count': len(names), 'unchanged_prior_payloads': len(names),
              'unchanged_prior_cartoon_pngs': sum(name.startswith('data/styles/cartoon/') and name.endswith('.png') for name in names),
              'added_members': added,
              'bound_handoff_files_sha256': inputs, 'helper_sha256': sha(Path(__file__).read_bytes())}
    (candidate / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS private candidate adds three poses; all {len(names)} prior members unchanged; SHA256={record["archive_sha256"]}')


if __name__ == '__main__':
    main()
