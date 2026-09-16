"""Build a config-driven full-ring review using exact native image bytes."""
import hashlib
import json
from pathlib import Path
import struct
import zipfile

from PIL import Image
import config

OUT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    destination = OUT / 'review-v1'
    assert not destination.exists(), 'preserve existing ring review'
    clips, copies, reports, rectangles = {}, {}, {}, []
    with zipfile.ZipFile(OUT / 'candidate-v1/scrantic_data.zip') as archive:
        for clip, configured in config.CLIPS.items():
            folders = {'baseline': OUT / 'baseline-v1' / clip / 'full', 'candidate': OUT / 'candidate-v1' / clip / 'full'}
            raw = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
            records = {kind: json.loads(value) for kind, value in raw.items()}
            left, right = records['baseline'], records['candidate']
            assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS' and right['control'] is False
            assert len(left['displays']) == len(right['displays'])
            frames = []
            for a, b in zip(left['displays'], right['displays']):
                assert all(a[key] == b[key] for key in ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'heading', 'actual_draw', 'draw_ordinal'))
                row = {key: b[key] for key in ('logical_ms', 'duration_ms', 'segment', 'segment_ms', 'heading', 'actual_draw', 'draw_ordinal', 'comparison')}
                row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'])
                flip, x, y, frame = b['actual_draw']
                png = archive.read(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png')
                width, height = struct.unpack('>II', png[16:24])
                rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
                for kind, record in (('baseline', a), ('candidate', b)):
                    path = folders[kind] / record['png']
                    png = path.read_bytes()
                    assert sha(png) == record['png_sha256']
                    with Image.open(path) as image:
                        assert image.size == (1280, 960) and sha(image.convert('RGB').tobytes()) == record['pixels_sha256']
                    relative = f'images/{record["png_sha256"]}.png'
                    if relative in copies:
                        assert copies[relative] == png, 'shared image exact bytes'
                    copies[relative] = png
                    row[kind] = relative
                frames.append(row)
            clips[clip] = {'label': configured['label'], 'frames': frames, 'duration_ms': right['duration_ms'],
                           'pose_count': max(row['pose_index'] for row in frames) + 1, 'segments': right['segments'],
                           'reports_sha256': {kind: sha(value) for kind, value in raw.items()}}
            reports[clip] = clips[clip]['reports_sha256']
    union = [min(r[0] for r in rectangles), min(r[1] for r in rectangles), max(r[2] for r in rectangles), max(r[3] for r in rectangles)]
    cx, cy, cw, ch = config.FIXED_CAMERA_HD
    assert cx <= union[0] < union[2] <= cx + cw and cy <= union[1] < union[3] <= cy + ch, 'fixed camera contains every full sprite canvas'
    bundle = {'default_clip': config.DEFAULT_CLIP, 'heading_labels': config.HEADING_LABELS, 'clips': clips}
    template = (OUT / 'review-template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1
    html = template.replace('__DATA__', json.dumps(bundle, separators=(',', ':')))
    destination.mkdir()
    for name, png in copies.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png)
    (destination / 'review.html').write_text(html, encoding='utf-8', newline='\n')
    record = {'status': 'local technical review; unpublished', 'html_sha256': sha((destination / 'review.html').read_bytes()),
              'image_files': {name: sha(png) for name, png in copies.items()}, 'reports_sha256': reports,
              'fixed_camera_hd_xywh': config.FIXED_CAMERA_HD, 'all_canvas_union_hd_xyxy': union,
              'builder_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha((OUT / 'review-template.html').read_bytes()),
              'config_sha256': sha((OUT / 'config.py').read_bytes()),
              'scope': 'Exact native two-direction rings; only000015 are new. Shared identical PNGs reference the same bytes; no frames/times omitted.'}
    (destination / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS full-ring review: {len(copies)} unique exact PNGs; all260 panel-display references retained; camera {union}')


if __name__ == '__main__':
    main()
