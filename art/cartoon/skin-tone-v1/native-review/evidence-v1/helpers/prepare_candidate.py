"""Stage a private color-only package against the selected connecting baseline."""
import argparse
import copy
import io
from pathlib import Path
import shutil
import zipfile
from PIL import Image
import config
import native_core as core

BUNDLE = config.ROOT / 'art/cartoon/skin-tone-v1'


def relative_file(root, name):
    relative = Path(name)
    core.require(not relative.is_absolute() and '..' not in relative.parts, 'relative export path:' + str(name))
    result = (root / relative).resolve()
    core.require(result.is_relative_to(root.resolve()), 'contained export path:' + str(name))
    return result


def validate_export(export):
    export = export.resolve()
    recipe = config.load_json(export / 'recipe.json')
    index = config.load_json(BUNDLE / 'input-index.json')
    core.require(recipe['schema_version'] == 1 and recipe['operation'] == 'post-export-color-correction',
                 'explicit color-only recipe')
    for key, name in (('algorithm_sha256', 'correct.py'), ('input_index_sha256', 'input-index.json'),
                      ('calibration_sha256', 'calibration-v1.json'),
                      ('cap_exclusions_sha256', 'protected-cap-polygons-v1.json')):
        core.require(config.sha((BUNDLE / name).read_bytes()) == recipe[key], 'correction binding:' + name)
    cap_rows = {row['frame']: row for row in config.load_json(BUNDLE / 'protected-cap-polygons-v1.json')['frames']}
    core.require([r['frame'] for r in recipe['frames']] == list(config.TARGET_FRAMES), 'exact28 corrected frame scope')
    core.require([r['frame'] for r in index['frames']] == list(config.TARGET_FRAMES), 'exact28 frozen input scope')
    core.require(index['candidate_archive_sha256'] == config.BASELINE_SHA, 'frozen connecting baseline')
    corrected, masks, records = {}, {}, []
    for row, original in zip(recipe['frames'], index['frames']):
        frame = row['frame']
        label = f'{frame:03}'
        member = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{label}.png'
        core.require(row['member'] == original['member'] == member and
                     row['path'] == f'BMP/JOHNWALK.BMP/{label}.png', 'canonical frame mapping:' + label)
        source = relative_file(BUNDLE, row['input']).read_bytes()
        data = relative_file(export, row['candidate_png']).read_bytes()
        mask_bytes = relative_file(export, row['mask']).read_bytes()
        core.require(config.sha(source) == row['input_sha256'] == original['sha256'], 'exact input:' + label)
        core.require(config.sha(data) == row['candidate_png_sha256'], 'corrected output hash:' + label)
        core.require(config.sha(mask_bytes) == row['mask_sha256'], 'skin mask hash:' + label)
        core.require(row['protected_cap_mask_l_sha256'] == cap_rows[frame]['mask_l_sha256'] and
                     row['input_sha256'] == cap_rows[frame]['input_sha256'], 'cap exclusion binding:' + label)
        with Image.open(io.BytesIO(source)) as old, Image.open(io.BytesIO(data)) as new, Image.open(io.BytesIO(mask_bytes)) as mask:
            core.require(old.mode == new.mode == 'RGBA' and mask.mode == 'L', 'RGBA and soft L mask:' + label)
            core.require(old.size == new.size == mask.size and list(new.size) == row['runtime_canvas'] == original['canvas'],
                         'unchanged canvas:' + label)
            a, b, weights = old.tobytes(), new.tobytes(), mask.tobytes()
            core.require(a[3::4] == b[3::4], 'unchanged alpha:' + label)
            core.require(config.sha(b[3::4]) == row['alpha_sha256'] == original['alpha_sha256'], 'alpha identity:' + label)
            core.require(config.sha(b) == row['rgba_sha256'], 'corrected RGBA identity:' + label)
            changed = [p for p in range(len(weights)) if a[p*4:p*4+3] != b[p*4:p*4+3]]
            core.require(all(weights[p] > 0 for p in changed), 'only skin-mask RGB changes:' + label)
            core.require(len(changed) == row['changed_pixels'], 'measured changed pixels:' + label)
            if frame == recipe['reference_frame']:
                core.require(data == source and not changed, 'reference frame is byte-identical:' + label)
        corrected[member], masks[frame] = data, mask_bytes
        records.append({'frame': frame, 'member': member, 'input_sha256': original['sha256'],
                        'sha256': row['candidate_png_sha256'], 'canvas': row['runtime_canvas'],
                        'mask': f'masks/{label}.png', 'mask_sha256': row['mask_sha256'],
                        'mask_l': f'masks/{label}.l', 'mask_l_sha256': config.sha(weights),
                        'protected_cap_mask_l_sha256': row['protected_cap_mask_l_sha256'],
                        'changed_pixels': len(changed)})
    core.require(recipe['reference_frame'] == 29 and any(r['changed_pixels'] for r in records),
                 'reference029 plus actual color changes')
    return recipe, corrected, masks, records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--candidate-version', type=int, default=1)
    args = parser.parse_args()
    core.require(args.candidate_version > 0, 'positive candidate version')
    print('WITNESS skin package SHA256=' + config.sha(Path(__file__).read_bytes()), flush=True)
    recipe, corrected, masks, records = validate_export(args.export)
    base = config.OUT / 'baseline-pack.zip'
    core.require(config.sha(base.read_bytes()) == config.BASELINE_SHA, 'exact connecting baseline')
    core.require(config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes()) == config.PRODUCTION_SHA,
                 'production unchanged')
    target = config.OUT / f'candidate-v{args.candidate_version}'
    core.require(not target.exists(), 'preserve color candidate evidence')
    with zipfile.ZipFile(base) as src:
        names = src.namelist()
        core.require(len(names) == len(set(names)) == 2594, 'unique2594 baseline members')
        core.require(set(corrected) <= set(names), 'replacements only, no additions')
        for row in records:
            core.require(config.sha(src.read(row['member'])) == row['input_sha256'],
                         'candidate baseline input:' + str(row['frame']))
        target.mkdir()
        package = target / 'scrantic_data.zip'
        with zipfile.ZipFile(package, 'x') as dst:
            dst.comment = src.comment
            for info in src.infolist():
                dst.writestr(copy.copy(info), corrected.get(info.filename, src.read(info.filename)))
        with zipfile.ZipFile(package) as dst:
            core.require(dst.namelist() == names, 'same member order and coverage')
            for name in names:
                expected = corrected[name] if name in corrected else src.read(name)
                core.require(dst.read(name) == expected, 'exact member payload:' + name)
    (target / 'masks').mkdir()
    for frame, raw in masks.items():
        (target / 'masks' / f'{frame:03}.png').write_bytes(raw)
        with Image.open(io.BytesIO(raw)) as image:
            (target / 'masks' / f'{frame:03}.l').write_bytes(image.tobytes())
    shutil.copyfile(args.export / 'recipe.json', target / 'correction-recipe.json')
    shutil.copyfile(BUNDLE / 'input-index.json', target / 'input-index.json')
    record = {'status': 'PASS', 'scope': 'Private color-only candidate; no human approval or production promotion.',
              'candidate_version': args.candidate_version,
              'base_archive_sha256': config.BASELINE_SHA, 'archive_sha256': config.sha(package.read_bytes()),
              'recipe_sha256': config.sha((target / 'correction-recipe.json').read_bytes()),
              'input_index_sha256': config.sha((target / 'input-index.json').read_bytes()),
              'algorithm_sha256': recipe['algorithm_sha256'], 'calibration_sha256': recipe['calibration_sha256'],
              'cap_exclusions_sha256': recipe['cap_exclusions_sha256'],
              'member_count': len(names), 'unchanged_other_payloads': len(names)-len(records),
              'replaced_members': records, 'added_members': [], 'removed_members': [],
              'helper_sha256': config.sha(Path(__file__).read_bytes())}
    core.save(target / 'preparation.json', record)
    print(f'PASS28 frame inputs, alpha and mask support; {record["unchanged_other_payloads"]} other payloads unchanged; SHA256={record["archive_sha256"]}')


if __name__ == '__main__':
    main()
