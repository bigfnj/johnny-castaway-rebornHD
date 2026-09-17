"""Recompute source-alpha overlap measurements without changing any image."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
HERE = Path(__file__).resolve().parent.parent
SELECTED = HERE.parent / 'foam-refresh-v1/candidates/v2'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive = ROOT / 'assets/scrantic_data.zip'
    assert sha(archive.read_bytes()) == '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
    with Image.open(SELECTED / 'BMP/BACKGRND.BMP/000.png') as image:
        ground = image.convert('RGBA')
    with zipfile.ZipFile(archive) as z:
        old_ground_raw = z.read('data/styles/cartoon/BMP/BACKGRND.BMP/000.png')
        old_ground = Image.open(io.BytesIO(old_ground_raw)).convert('RGBA')
        rows = []
        for frame in range(3, 12):
            center = 6 <= frame <= 8
            member = f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
            source_path = SELECTED / f'audit/{frame:03}-unmasked.png'
            raw = source_path.read_bytes() if center else z.read(member)
            source = Image.open(io.BytesIO(raw)).convert('RGBA')
            origin = (696, 548) if center else (540, 612) if frame < 6 else (1036, 606)
            a = source.getchannel('A')
            values = list(a.get_flattened_data())

            def measured(g, go, shift=(0, 0)):
                mass = retained = meaningful = removed = 0
                pixels = []
                for y in range(source.height):
                    for x in range(source.width):
                        before = values[y*source.width+x]
                        gx, gy = x+origin[0]+shift[0]-go[0], y+origin[1]+shift[1]-go[1]
                        ga = g.getpixel((gx, gy))[3] if 0 <= gx < g.width and 0 <= gy < g.height else 0
                        after = (before*(255-ga)+127)//255
                        mass += before; retained += after
                        meaningful += after >= 8; removed += before >= 8 and after < 8
                        pixels.append(after)
                return {'alpha_mass_retained_percent': round(100*retained/mass, 2),
                        'alpha8_retained_pixels': meaningful, 'alpha8_removed_pixels': removed}, pixels

            old, _ = measured(old_ground, (576, 558))
            current, expected = measured(ground, (540, 548))
            with Image.open(SELECTED / f'BMP/BACKGRND.BMP/{frame:03}.png') as actual:
                assert list(actual.getchannel('A').get_flattened_data()) == expected, frame
            shift = (-6, 8) if frame < 6 else (10, 10) if frame >= 9 else (0, 0)
            proposed, _ = measured(ground, (540, 548), shift)
            clipped = sum(values[y*source.width+x] >= 8 for y in range(source.height) for x in range(source.width)
                          if not (0 <= x+shift[0] < source.width and 0 <= y+shift[1] < source.height))
            rows.append({'frame': frame, 'source': source_path.relative_to(ROOT).as_posix() if center else member,
                         'source_sha256': sha(raw), 'source_container': None if center else 'assets/scrantic_data.zip',
                         'source_canvas': list(source.size), 'world_origin_hd': list(origin),
                         'alpha8_pixels': sum(v >= 8 for v in values), 'alpha8_bounds_local': a.point(lambda v: 255 if v >= 8 else 0).getbbox(),
                         'nonzero_bounds_local': a.getbbox(), 'old_ground_hypothetical_mask': old,
                         'selected_ground_mask': current, 'proposed_translation_hd': list(shift),
                         'proposed_ground_mask': proposed, 'alpha8_pixels_clipped_if_shifted_inside_old_canvas': clipped})
    coast = []
    for x in (580, 620, 660, 720, 760, 800, 880, 960, 1040, 1080, 1120):
        bottoms = []
        for g, ox, oy in ((old_ground, 576, 558), (ground, 540, 548)):
            yy = [y+oy for y in range(g.height) if 0 <= x-ox < g.width and g.getpixel((x-ox, y))[3] >= 128]
            bottoms.append(max(yy) if yy else None)
        coast.append({'world_x_hd': x, 'old_bottom_hd': bottoms[0], 'new_bottom_hd': bottoms[1]})
    report = {'schema_version': 1, 'scope': 'Read-only source geometry. Translation values are comparison candidates, not visual approval.',
              'method': 'Sum source alpha before/after the recorded integer ground visibility mask. Alpha>=8 denotes meaningful coverage. Alpha mass includes translucent glow/shadow and is not a count of literal wave lines.',
              'archive_sha256': sha(archive.read_bytes()), 'old_ground_member_sha256': sha(old_ground_raw),
              'selected_ground_sha256': sha((SELECTED / 'BMP/BACKGRND.BMP/000.png').read_bytes()),
              'measurement_source_sha256': sha(Path(__file__).read_bytes()), 'frames': rows, 'coast_alpha128_bottoms': coast,
              'source_scope': 'Side sources are the earlier production drawings. Center sources were generated for the enlarged island; old-ground overlap for them is a geometric counterfactual, not a claim that they were shown on the older island.',
              'recommendation': {'left': {'frames': [3,4,5], 'translation_hd': [-6,8], 'canvas': [150,66], 'offset_hd': [-6,0], 'source_paste_xy': [0,8]},
                                 'right': {'frames': [9,10,11], 'translation_hd': [10,10], 'canvas': [154,74], 'offset_hd': [0,0], 'source_paste_xy': [10,10]},
                                 'unchanged': 'Keep approved ground and selected center006-008 byte-exact. Recompute mask after family translation; moving already-masked outputs cannot recover omitted strokes.'}}
    (HERE / 'geometry.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS measured all nine high-wave phases; no image files changed')


if __name__ == '__main__':
    main()
