"""Exact source-only composite and nearest scaling; no painted pixels."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()
PRODUCTION_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
ORIGINS = {0: (576, 558), 3: (540, 612), 7: (728, 638), 9: (1036, 606)}
ORDER = [0, 9, 3, 7]
CROP = (540, 558, 1180, 686)
OFFSET = (128, 384)

def main():
    production = ROOT / 'assets/scrantic_data.zip'
    reference = ROOT / 'art/cartoon/character-inventory-v1/reference-originals.zip'
    assert sha(production.read_bytes()) == PRODUCTION_SHA
    rows = []
    with zipfile.ZipFile(reference) as originals, zipfile.ZipFile(production) as cartoon:
        for label, archive, prefix, scale in [
            ('original', originals, 'native/BMP/BACKGRND.BMP/', 2),
            ('cartoon', cartoon, 'data/styles/cartoon/BMP/BACKGRND.BMP/', 1),
        ]:
            # Full render-size transparent canvas retains the original origins.
            world = Image.new('RGBA', (1280, 960))
            sources = []
            for frame in ORDER:
                member = prefix + f'{frame:03}.png'
                raw = archive.read(member)
                im = Image.open(io.BytesIO(raw)).convert('RGBA')
                source_size = list(im.size)
                if scale != 1:
                    im = im.resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
                origin = ORIGINS[frame]
                world.alpha_composite(im, origin)
                sources.append({'frame': frame, 'member': member, 'sha256': sha(raw),
                                'source_canvas': source_size, 'source_to_runtime_nearest_scale': scale,
                                'runtime_canvas': list(im.size), 'world_origin_hd': list(origin)})
            cut = world.crop(CROP)
            omitted = [(x, y, world.getpixel((x, y))[3]) for y in range(558, 690) for x in range(536, 1184)
                       if not (CROP[0] <= x < CROP[2] and CROP[1] <= y < CROP[3]) and world.getpixel((x, y))[3] > 0]
            expanded = cut.resize((1280, 256), Image.Resampling.NEAREST)
            guide = Image.new('RGBA', (1536, 1024))
            guide.paste(expanded, OFFSET)
            assert guide.crop((128, 384, 1408, 640)).tobytes() == expanded.tobytes()
            padding = guide.getchannel('A')
            padding.paste(0, (128, 384, 1408, 640))
            assert padding.getbbox() is None
            target = HERE / f'{label}-ground-master.png'
            assert not target.exists(), str(target)
            guide.save(target, compress_level=9)
            rows.append({'label': label, 'file': target.name, 'sha256': sha(target.read_bytes()),
                         'sources_in_draw_order': sources,
                         'cropped_composite_rgba_sha256': sha(cut.tobytes()),
                         'omitted_nonzero_alpha_pixels': len(omitted),
                         'omitted_alpha8_pixels': sum(a >= 8 for x, y, a in omitted),
                         'omitted_world_bounds_xyxy': [min(x for x,y,a in omitted), min(y for x,y,a in omitted),
                                                       max(x for x,y,a in omitted)+1, max(y for x,y,a in omitted)+1] if omitted else None})
    record = {
        'schema_version': 1,
        'role': 'Generation geometry/style references only; no approved replacement or native capture.',
        'helper_sha256': sha(Path(__file__).read_bytes()),
        'source_archives': {'art/cartoon/character-inventory-v1/reference-originals.zip': sha(reference.read_bytes()),
                            'assets/scrantic_data.zip': PRODUCTION_SHA},
        'world_hd_crop_xyxy': list(CROP), 'cropped_runtime_canvas': [640, 128],
        'guide_canvas': [1536, 1024], 'nearest_runtime_to_guide_scale': 2, 'guide_offset_xy': list(OFFSET),
        'guide_to_crop_runtime_affine': [0.5, 0, -64, 0, 0.5, -192],
        'draw_order': ORDER,
        'phase_note': '009,003,007 follows the final three observed grDrawSprite calls in the unchanged finite-wait native phase probe. This is a fresh direct source composite, not emulation of prior opaque stamping history.',
        'guides': rows,
        'checks': {'exact_nearest_embedding_and_transparent_padding': 'PASS', 'guide_count': 2},
        'limits': 'Only000/003/007/009 included. No palm, shadow, Johnny, ocean, props, new rejected shoreline drafts, masks or recoloring. Original diagnostic colors retained, including blue wave water. Requested crop omits two lowerHDrows of007 wave fringe; original yellow/olive ground is wholly above this boundary. This reference is not a native executable screenshot.'
    }
    observation = ROOT / 'build/shoreline-repair-v1/phase-probe-v1/phase-observation.json'
    if observation.is_file():
        record['phase_observation'] = {'path': observation.relative_to(ROOT).as_posix(), 'sha256': sha(observation.read_bytes())}
    (HERE / 'source.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'source_json_sha256': sha((HERE / 'source.json').read_bytes()),
                      'outputs': [{k: row[k] for k in ['file', 'sha256', 'omitted_nonzero_alpha_pixels', 'omitted_alpha8_pixels']} for row in rows]}))

if __name__ == '__main__':
    main()
