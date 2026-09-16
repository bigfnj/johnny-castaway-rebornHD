"""Build a two-panel viewer from exact native captures, without retiming."""
import io
import json
from pathlib import Path
import zipfile
from PIL import Image
import config

OUT, sha = config.OUT, config.sha


def main():
    destination = OUT / 'review-v1'
    assert not destination.exists(), 'preserve existing native review'
    assert config.load_json(OUT / 'baseline-v1/summary.json')['status'] == 'PASS'
    assert config.load_json(OUT / 'candidate-v1/summary.json')['status'] == 'PASS'
    clips, copies, reports = {}, {}, {}
    with zipfile.ZipFile(OUT / 'candidate-v1/scrantic_data.zip') as archive:
        for clip, configured in config.CLIPS.items():
            folders = {kind: OUT / (kind + '-v1') / clip / 'full' for kind in ('baseline', 'candidate')}
            raw = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
            left, right = json.loads(raw['baseline']), json.loads(raw['candidate'])
            assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS' and right['control'] is False
            assert len(left['displays']) == len(right['displays'])
            frames, rectangles = [], []
            for a, b in zip(left['displays'], right['displays']):
                keys = ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'role', 'actual_draw', 'draw_ordinal', 'stage_draw_ordinal')
                assert all(a[key] == b[key] for key in keys), 'matching native panel timeline'
                row = {key: b[key] for key in keys if key != 'index'}
                row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'], comparison=b['comparison'])
                flip, x, y, frame = b['actual_draw']
                # Native canvas sizes are identical in both styles. For camera
                # containment use their full canvases, never a cropped pivot.
                with Image.open(io.BytesIO(archive.read(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'))) as sprite:
                    width, height = sprite.size
                rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
                for kind, record in (('baseline', a), ('candidate', b)):
                    path = folders[kind] / record['png']
                    png = path.read_bytes()
                    assert sha(png) == record['png_sha256'], 'bound native PNG'
                    with Image.open(path) as image:
                        assert image.size == (1280, 960) and sha(image.convert('RGB').tobytes()) == record['pixels_sha256'], 'bound native pixels'
                    relative = f'images/{record["png_sha256"]}.png'
                    if relative in copies:
                        assert copies[relative] == png, 'identical shared image'
                    copies[relative] = png
                    row[kind] = relative
                frames.append(row)
            union = [min(r[0] for r in rectangles), min(r[1] for r in rectangles), max(r[2] for r in rectangles), max(r[3] for r in rectangles)]
            box = [max(0, union[0] - 16), max(0, union[1] - 16), min(1280, union[2] + 16), min(960, union[3] + 16)]
            camera = [box[0], box[1], box[2] - box[0], box[3] - box[1]]
            assert box[0] <= union[0] < union[2] <= box[2] and box[1] <= union[1] < union[3] <= box[3]
            clips[clip] = {'label': configured['label'], 'frames': frames, 'duration_ms': right['duration_ms'],
                           'pose_count': max(row['pose_index'] for row in frames) + 1, 'segments': right['segments'],
                           'camera_hd_xywh': camera, 'all_canvas_union_hd_xyxy': union,
                           'reports_sha256': {kind: sha(value) for kind, value in raw.items()}}
            reports[clip] = clips[clip]['reports_sha256']
    bundle = {'default_clip': config.DEFAULT_CLIP, 'clips': clips, 'candidate_frames': list(config.CANDIDATE_FRAMES)}
    template = (config.HERE / 'review-template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1
    html = template.replace('__DATA__', json.dumps(bundle, separators=(',', ':')))
    destination.mkdir()
    for name, png in copies.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png)
    (destination / 'review.html').write_text(html, encoding='utf-8', newline='\n')
    record = {'status': 'local technical review; unpublished; human motion approval pending',
              'html_sha256': sha((destination / 'review.html').read_bytes()), 'image_files': {name: sha(png) for name, png in copies.items()},
              'reports_sha256': reports, 'cameras_hd_xywh': {name: clip['camera_hd_xywh'] for name, clip in clips.items()},
              'builder_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha((config.HERE / 'review-template.html').read_bytes()),
              'config_sha256': sha((config.HERE / 'config.py').read_bytes()),
              'scope': 'All exact native displays in two directions plus ordinary003 contexts. Shared images are deduplicated without changing pixels/timestamps. Only001-008 are candidates.'}
    (destination / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS native review: {len(copies)} exact unique PNGs, {sum(len(c["frames"]) for c in clips.values())} complete timeline displays')


if __name__ == '__main__':
    main()
