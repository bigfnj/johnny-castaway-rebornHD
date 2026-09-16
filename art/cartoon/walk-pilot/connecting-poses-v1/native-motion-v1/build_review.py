"""Build a new two-panel connecting review from exact native capture records."""
import argparse
import io
import json
from pathlib import Path
import zipfile
from PIL import Image
import config

LABELS = dict(front_arc='Front turn', rear_arc='Rear turn',
              travel_cb='Front walk connection', travel_ec='Profile connection',
              waypoint_front='Front waypoint', waypoint_rear='Rear waypoint')


def canvas(archive, frame):
    member = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
    if member not in archive.namelist():
        member = f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png'
    with Image.open(io.BytesIO(archive.read(member))) as image:
        return image.size


def source_identity(report, kind, clip, contract):
    assert report['clip'] == clip and report['phase'] == 'full', 'capture clip/phase identity:' + kind + ':' + clip
    for stage, expected in contract[clip].items():
        observed = report['segments'][stage]
        expected_draws = [[row[k] for k in ('flip_x', 'x', 'y', 'frame')] for row in expected['draws']]
        assert observed['api_arguments'] == expected['api_arguments'] and observed['chosen_path'] == expected['chosen_path'] and observed['draws'] == expected_draws, 'capture source contract:' + kind + ':' + clip + ':' + stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=config.OUT / 'review-v1')
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    args = parser.parse_args()
    destination = args.output
    assert not destination.exists(), 'preserve existing native review'
    candidate_dir = args.candidate.resolve()
    candidate_relative = candidate_dir.relative_to(config.OUT.resolve()).as_posix()
    assert '/' not in candidate_relative and candidate_relative.startswith('candidate-'), 'explicit local candidate directory'
    roots = {'baseline': config.OUT / 'baseline-v1', 'candidate': candidate_dir}
    summaries = {kind: config.load_json(path / 'summary.json') for kind, path in roots.items()}
    assert all(s['status'] == 'PASS' and list(s['clips']) == list(config.CLIPS) for s in summaries.values()), 'six complete captured clips'
    prep = config.load_json(candidate_dir / 'preparation.json')
    selected_path = args.selection.resolve()
    selected = config.load_json(selected_path)
    assert config.sha(selected_path.read_bytes()) == prep['selection_sha256'], 'canonical captured selection'
    assert (candidate_dir / 'candidate-selection.json').read_bytes() == selected_path.read_bytes(), 'private selection copy'
    assert [row['frame'] for row in selected['frames']] == list(config.CANDIDATE_FRAMES), 'three connecting candidates'
    base_path, candidate_path = config.OUT / 'baseline-pack.zip', candidate_dir / 'scrantic_data.zip'
    assert config.sha(base_path.read_bytes()) == prep['base_archive_sha256'] == config.PRODUCTION_SHA, 'pinned baseline archive'
    assert config.sha(candidate_path.read_bytes()) == prep['archive_sha256'], 'pinned candidate archive'
    contract = config.contract()['clips']
    clips, copies, reports = {}, {}, {}
    with zipfile.ZipFile(base_path) as baseline, zipfile.ZipFile(candidate_path) as archive:
        for clip, configured in config.CLIPS.items():
            folders = {kind: path / clip / 'full' for kind, path in roots.items()}
            raw = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
            left, right = json.loads(raw['baseline']), json.loads(raw['candidate'])
            for kind, report in (('baseline', left), ('candidate', right)):
                source_identity(report, kind, clip, contract)
            assert left['status'] == right['status'] == 'PASS' and right['control'] is False, 'positive capture:' + clip
            assert left['executable_sha256'] == right['executable_sha256'] == summaries['candidate']['executable_sha256'], 'same native executable:' + clip
            assert left['archive_sha256'] == config.PRODUCTION_SHA and right['archive_sha256'] == prep['archive_sha256'], 'captured archive:' + clip
            assert len(left['displays']) == len(right['displays']) and left['duration_ms'] == right['duration_ms'] == configured['duration_ms'], 'matching complete timeline:' + clip
            frames, rectangles = [], []
            for a, b in zip(left['displays'], right['displays']):
                keys = ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'role', 'actual_draw', 'draw_ordinal', 'stage_draw_ordinal')
                assert all(a[key] == b[key] for key in keys), 'matching native panel timeline:' + clip
                row = {key: b[key] for key in keys if key != 'index'}
                row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'], comparison=b['comparison'])
                flip, x, y, frame = b['actual_draw']
                width, height = canvas(archive, frame)
                assert (width, height) == canvas(baseline, frame), 'unchanged full sprite canvas:' + str(frame)
                rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
                for kind, record in (('baseline', a), ('candidate', b)):
                    path = folders[kind] / record['png']
                    png = path.read_bytes()
                    assert config.sha(png) == record['png_sha256'], 'bound native PNG:' + str(path)
                    with Image.open(path) as image:
                        assert image.size == (1280, 960) and config.sha(image.convert('RGB').tobytes()) == record['pixels_sha256'], 'bound native pixels:' + str(path)
                    relative = f'images/{record["png_sha256"]}.png'
                    assert relative not in copies or copies[relative] == png, 'identical shared image'
                    copies[relative] = png
                    row[kind] = relative
                frames.append(row)
            union = [min(r[0] for r in rectangles), min(r[1] for r in rectangles), max(r[2] for r in rectangles), max(r[3] for r in rectangles)]
            box = [max(0, union[0] - 16), max(0, union[1] - 16), min(1280, union[2] + 16), min(960, union[3] + 16)]
            camera = [box[0], box[1], box[2] - box[0], box[3] - box[1]]
            assert box[0] <= union[0] < union[2] <= box[2] and box[1] <= union[1] < union[3] <= box[3], 'full canvas containment:' + clip
            clips[clip] = {'label': LABELS[clip], 'route_label': configured['label'], 'frames': frames,
                           'duration_ms': right['duration_ms'], 'pose_count': max(row['pose_index'] for row in frames) + 1,
                           'segments': right['segments'], 'camera_hd_xywh': camera, 'all_canvas_union_hd_xyxy': union,
                           'reports_sha256': {kind: config.sha(value) for kind, value in raw.items()}}
            reports[clip] = clips[clip]['reports_sha256']
    bundle = {'default_clip': config.DEFAULT_CLIP, 'clips': clips, 'candidate_frames': list(config.CANDIDATE_FRAMES)}
    template_path = config.HERE / 'review-template.html'
    template = template_path.read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1, 'single data placeholder'
    html = template.replace('__DATA__', json.dumps(bundle, separators=(',', ':')))
    destination.mkdir(parents=True)
    for name, png in copies.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png)
    (destination / 'review.html').write_text(html, encoding='utf-8', newline='\n')
    record = {'status': 'local technical review; unpublished; human motion approval pending',
              'html_sha256': config.sha((destination / 'review.html').read_bytes()), 'image_files': {name: config.sha(png) for name, png in copies.items()},
              'reports_sha256': reports, 'cameras_hd_xywh': {name: clip['camera_hd_xywh'] for name, clip in clips.items()},
              'builder_sha256': config.sha(Path(__file__).read_bytes()), 'template_sha256': config.sha(template_path.read_bytes()),
              'config_sha256': config.sha((config.HERE / 'config.py').read_bytes()), 'candidate_selection_sha256': prep['selection_sha256'],
              'candidate_directory': candidate_relative, 'candidate_selection_source': selected_path.relative_to(config.ROOT).as_posix(),
              'baseline_archive_sha256': config.PRODUCTION_SHA, 'candidate_archive_sha256': prep['archive_sha256'],
              'scope': 'Six complete native connecting clips. Left: current40-asset Cartoon with HD fallbacks. Right: same pack with009/010/012 only. Exact timestamps and full scene pixels; fixed camera per clip. No original-executable or human approval claim.'}
    (destination / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS native connecting review: {len(copies)} exact unique PNGs, {sum(len(c["frames"]) for c in clips.values())} complete timeline displays')


if __name__ == '__main__':
    main()
