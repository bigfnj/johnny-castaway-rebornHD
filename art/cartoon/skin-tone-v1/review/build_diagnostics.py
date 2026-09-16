"""Build a fresh, hash-bound still-color review and old/new/mask contact sheets."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'assets/scrantic_data.zip').is_file())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bound(path, expected, label):
    data = path.read_bytes()
    assert sha(data) == expected, label + ':' + path.name
    return data


def load_inputs(export):
    index_path = BUNDLE / 'input-index.json'
    index = json.loads(index_path.read_bytes())
    recipe_path = export / 'recipe.json'
    recipe = json.loads(recipe_path.read_bytes())
    assert sha(index_path.read_bytes()) == recipe['input_index_sha256'], 'frozen input-index identity'
    assert recipe['reference_frame'] == index['canonical_reference_frame'] == 29, 'unchanged reference029'
    expected = {row['frame']: row for row in index['frames']}
    assert [r['frame'] for r in recipe['frames']] == list(expected), 'exact ordered28-frame coverage'
    assert len(expected) == 28, '28 reviewed poses'
    frames = []
    for row in recipe['frames']:
        frame = row['frame']
        old = expected[frame]
        assert row['input'] == old['input'] == f'inputs/{frame:03}.png', 'input frame binding'
        assert row['candidate_png'] == f'sprites/{frame:03}.png' and row['mask'] == f'masks/{frame:03}.png', 'output frame binding'
        source = bound(BUNDLE / old['input'], old['sha256'], 'source PNG')
        assert sha(source) == row['input_sha256'], 'recipe input identity'
        candidate = bound(export / row['candidate_png'], row['candidate_png_sha256'], 'corrected PNG')
        mask_bytes = bound(export / row['mask'], row['mask_sha256'], 'mask PNG')
        with Image.open(BUNDLE / old['input']) as image:
            assert image.mode == 'RGBA', 'source RGBA'
            before = np.array(image)
        with Image.open(export / row['candidate_png']) as image:
            assert image.mode == 'RGBA' and list(image.size) == row['runtime_canvas'] == old['canvas'], 'exact pose canvas'
            after = np.array(image)
        with Image.open(export / row['mask']) as image:
            assert image.mode == 'L' and list(image.size) == old['canvas'], 'mask grayscale/canvas'
            mask = np.array(image)
        assert np.array_equal(before[:, :, 3], after[:, :, 3]), f'unchanged alpha:{frame:03}'
        assert sha(after.tobytes()) == row['rgba_sha256'], 'corrected pixel identity'
        assert sha(after[:, :, 3].tobytes()) == row['alpha_sha256'] == old['alpha_sha256'], 'alpha identity'
        changed = np.any(before[:, :, :3] != after[:, :, :3], axis=2)
        assert int(changed.sum()) == row['changed_pixels'], 'actual changed-pixel count'
        assert not np.any(changed & (mask == 0)), 'no change outside declared mask'
        if frame == 29:
            assert source == candidate and not changed.any(), 'canonical029 exact unchanged bytes'
        overlay = before.copy()
        strength = (mask.astype(float) / 255 * .70)[:, :, None]
        overlay[:, :, :3] = np.rint(before[:, :, :3] * (1 - strength) + np.array([255, 40, 160]) * strength).astype(np.uint8)
        frames.append({'frame': frame, 'before': before, 'after': after, 'overlay': overlay,
                       'old_bytes': source, 'new_bytes': candidate, 'mask_bytes': mask_bytes,
                       'record': {'frame': frame, 'canvas': old['canvas'], 'before': f'images/before-{frame:03}.png',
                                  'after': f'images/after-{frame:03}.png', 'overlay': f'images/overlay-{frame:03}.png',
                                  'mask': f'images/mask-{frame:03}.png', 'input_sha256': sha(source),
                                  'candidate_sha256': sha(candidate), 'mask_sha256': sha(mask_bytes),
                                  'changed_pixels': row['changed_pixels'], 'reference_unchanged': frame == 29}})
    return recipe_path, frames


def checker(width, height):
    im = Image.new('RGBA', (width, height), '#263743')
    draw = ImageDraw.Draw(im)
    for y in range(0, height, 18):
        for x in range(0, width, 18):
            if ((x // 18) + (y // 18)) % 2:
                draw.rectangle((x, y, x + 17, y + 17), fill='#2c3e4b')
    return im


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve existing diagnostic output'
    export = args.export.resolve()
    recipe_path, frames = load_inputs(export)
    args.output.mkdir(parents=True)
    images = args.output / 'images'
    images.mkdir()
    font = ImageFont.load_default(size=19)
    small = ImageFont.load_default(size=15)
    files = {}
    sheets = []
    for item in frames:
        row = item['record']
        for kind, data in [('before', item['old_bytes']), ('after', item['new_bytes']), ('mask', item['mask_bytes'])]:
            (args.output / row[kind]).write_bytes(data)
        Image.fromarray(item['overlay']).save(args.output / row['overlay'])
    # A uniform3x scale retains full source canvases; no per-pose bounds fitting.
    for page, start in enumerate(range(0, len(frames), 4), 1):
        group = frames[start:start + 4]
        sheet = Image.new('RGBA', (996, 60 + 516 * len(group)), '#17242e')
        draw = ImageDraw.Draw(sheet)
        for col, label in enumerate(['Earlier colors', 'Matched colors', 'Mask highlight']):
            draw.text((col * 332 + 16, 15), label, font=font, fill='#f3f6f7')
        for row_number, item in enumerate(group):
            top = 60 + row_number * 516
            reference = '  Color reference: unchanged' if item['frame'] == 29 else ''
            draw.text((16, top + 7), f'Pose {item["frame"]:03}{reference}', font=small, fill='#d8e5ec')
            for col, key in enumerate(['before', 'after', 'overlay']):
                panel = checker(316, 474)
                sprite = Image.fromarray(item[key]).resize((item[key].shape[1] * 3, item[key].shape[0] * 3), Image.Resampling.NEAREST)
                panel.alpha_composite(sprite, ((316 - sprite.width) // 2, 0))
                sheet.alpha_composite(panel, (col * 332 + 8, top + 34))
        name = f'contact-sheet-{page:02}.png'
        sheet.convert('RGB').save(args.output / name)
        sheets.append(name)
    data = {'frames': [item['record'] for item in frames], 'reference_frame': 29, 'default_frame': 24, 'sheets': sheets}
    template = (HERE / 'still-template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1, 'single review data slot'
    (args.output / 'review.html').write_text(template.replace('__DATA__', json.dumps(data, separators=(',', ':'))), encoding='utf-8', newline='\n')
    for path in sorted(args.output.rglob('*')):
        if path.is_file():
            files[path.relative_to(args.output).as_posix()] = sha(path.read_bytes())
    record = {'status': 'local still-color diagnostic; unpublished; corrected-output human approval pending',
              'export_recipe': {'path': recipe_path.relative_to(ROOT).as_posix(), 'sha256': sha(recipe_path.read_bytes())},
              'input_index_sha256': sha((BUNDLE / 'input-index.json').read_bytes()),
              'builder_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha((HERE / 'still-template.html').read_bytes()),
              'pillow_version': pillow_version, 'frames': data['frames'], 'files_sha256': files,
              'scope': 'All28 frozen poses before/after and soft-mask overlays. Source and corrected PNGs copied byte-for-byte. Canonical029 unchanged. Contact sheets use one3x nearest scale and intact canvases. Magenta overlay is mask strength, not proof of semantic correctness or actual changed pixels. No native motion or production claim.'}
    (args.output / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS28 exact source/candidate/mask bindings; all alpha unchanged; canonical029 byte-identical')
    print('PASS7 contact sheets and local28-pose still review built; unpublished')


if __name__ == '__main__':
    main()
