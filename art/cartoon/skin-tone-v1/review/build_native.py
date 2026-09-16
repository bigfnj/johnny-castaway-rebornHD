"""Build an unpublished eight-clip color review from complete native captures."""
import argparse
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'native-review'))
import config

LABELS = dict(front_arc='Front turn', rear_arc='Rear turn', travel_cb='Front walk connection',
              travel_ec='Profile connection', waypoint_front='Front waypoint', waypoint_rear='Rear waypoint',
              wait015='Rear standing pose', wait016='Front standing pose')
DEFAULT_CLIP = 'waypoint_front'


def canvas(archive, frame):
    name = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
    with Image.open(io.BytesIO(archive.read(name))) as image:
        return image.size


def source_identity(report, kind, clip, contract):
    assert report['clip'] == clip and report['phase'] == 'full', 'capture clip/phase identity:' + kind + ':' + clip
    for stage, expected in contract[clip].items():
        observed = report['segments'][stage]
        draws = [[row[k] for k in ('flip_x', 'x', 'y', 'frame')] for row in expected['draws']]
        assert observed['api_arguments'] == expected['api_arguments'] and observed['chosen_path'] == expected['chosen_path'] and observed['draws'] == draws, 'capture source contract:' + kind + ':' + clip + ':' + stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--stills', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve existing native color review'
    candidate_dir = args.candidate.resolve()
    candidate_relative = candidate_dir.relative_to(config.OUT.resolve()).as_posix()
    assert '/' not in candidate_relative and candidate_relative.startswith('candidate-'), 'explicit local color candidate'
    preparation_path = candidate_dir / 'preparation.json'
    prep = config.load_json(preparation_path)
    assert prep['status'] == 'PASS' and prep['base_archive_sha256'] == config.BASELINE_SHA, 'prepared color candidate baseline'
    assert config.sha((candidate_dir / 'correction-recipe.json').read_bytes()) == prep['recipe_sha256'], 'prepared color recipe'
    assert config.sha((candidate_dir / 'input-index.json').read_bytes()) == prep['input_index_sha256'], 'prepared color inputs'
    assert [row['frame'] for row in prep['replaced_members']] == list(config.TARGET_FRAMES), 'exact28 native color scope'
    still_record = config.load_json(args.stills / 'review-record.json')
    still_checks = config.load_json(args.stills / 'browser-validation.json')
    assert still_record['export_recipe']['sha256'] == prep['recipe_sha256'], 'stills use exact captured correction recipe'
    assert still_checks['status'] == 'PASS' and still_checks['review_record_sha256'] == config.sha((args.stills / 'review-record.json').read_bytes()), 'completed bound still browser checks'
    assert still_checks['html_sha256'] == still_record['files_sha256']['review.html'], 'tested still HTML identity'
    copies = {}
    for name, digest in still_record['files_sha256'].items():
        raw = (args.stills / name).read_bytes()
        assert config.sha(raw) == digest, 'bound still file:' + name
        copies['stills/' + name] = raw
    roots = {'baseline': config.OUT / 'baseline-v1', 'candidate': candidate_dir}
    summaries = {kind: config.load_json(path / 'summary.json') for kind, path in roots.items()}
    assert all(row['status'] == 'PASS' and list(row['clips']) == list(config.CLIPS) for row in summaries.values()), 'eight complete color clips'
    assert summaries['candidate']['frames_seen'] == list(config.TARGET_FRAMES), 'all28 frames captured'
    assert summaries['candidate']['archive_sha256'] == prep['archive_sha256'] and summaries['candidate']['recipe_sha256'] == prep['recipe_sha256'], 'summary candidate identity'
    baseline_path, candidate_path = config.OUT / 'baseline-pack.zip', candidate_dir / 'scrantic_data.zip'
    assert config.sha(baseline_path.read_bytes()) == config.BASELINE_SHA, 'pinned earlier-color archive'
    assert config.sha(candidate_path.read_bytes()) == prep['archive_sha256'], 'pinned corrected-color archive'
    contract = config.contract()['clips']
    clips, reports, seen = {}, {}, set()
    with zipfile.ZipFile(baseline_path) as baseline, zipfile.ZipFile(candidate_path) as candidate:
        for row in prep['replaced_members']:
            assert config.sha(baseline.read(row['member'])) == row['input_sha256'], 'baseline sprite:' + str(row['frame'])
            assert config.sha(candidate.read(row['member'])) == row['sha256'], 'corrected sprite:' + str(row['frame'])
        assert baseline.read('data/styles/cartoon/BMP/JOHNWALK.BMP/029.png') == candidate.read('data/styles/cartoon/BMP/JOHNWALK.BMP/029.png'), 'unchanged canonical029 member'
        for name, configured in config.CLIPS.items():
            folders = {kind: root / name / 'full' for kind, root in roots.items()}
            raw = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
            left, right = json.loads(raw['baseline']), json.loads(raw['candidate'])
            for kind, report in [('baseline', left), ('candidate', right)]:
                source_identity(report, kind, name, contract)
            assert left['status'] == right['status'] == 'PASS', 'positive native report:' + name
            assert left['executable_sha256'] == right['executable_sha256'] == summaries['candidate']['executable_sha256'], 'same executable:' + name
            assert left['archive_sha256'] == config.BASELINE_SHA and right['archive_sha256'] == prep['archive_sha256'], 'capture archive identity:' + name
            assert len(left['displays']) == len(right['displays']) and left['duration_ms'] == right['duration_ms'] == configured['duration_ms'], 'matching full timeline:' + name
            frames, rectangles = [], []
            for a, b in zip(left['displays'], right['displays']):
                keys = ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'role', 'actual_draw', 'draw_ordinal', 'stage_draw_ordinal')
                assert all(a[key] == b[key] for key in keys), 'matching native panel timeline:' + name
                row = {key: b[key] for key in keys if key != 'index'}
                row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'], comparison=b['comparison'])
                flip, x, y, frame = b['actual_draw']
                seen.add(frame)
                width, height = canvas(candidate, frame)
                assert (width, height) == canvas(baseline, frame), 'unchanged full sprite canvas:' + str(frame)
                rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
                for kind, display in [('baseline', a), ('candidate', b)]:
                    path = folders[kind] / display['png']
                    png = path.read_bytes()
                    assert config.sha(png) == display['png_sha256'], 'bound native PNG:' + str(path)
                    with Image.open(path) as image:
                        assert image.size == (1280, 960) and config.sha(image.convert('RGB').tobytes()) == display['pixels_sha256'], 'bound native pixels:' + str(path)
                    relative = f'images/{display["png_sha256"]}.png'
                    assert relative not in copies or copies[relative] == png, 'shared native image identity'
                    copies[relative] = png
                    row[kind] = relative
                frames.append(row)
            union = [min(r[0] for r in rectangles), min(r[1] for r in rectangles), max(r[2] for r in rectangles), max(r[3] for r in rectangles)]
            box = [max(0, union[0] - 16), max(0, union[1] - 16), min(1280, union[2] + 16), min(960, union[3] + 16)]
            camera = [box[0], box[1], box[2] - box[0], box[3] - box[1]]
            clips[name] = {'label': LABELS[name], 'route_label': configured['label'], 'frames': frames,
                           'duration_ms': right['duration_ms'], 'pose_count': max(row['pose_index'] for row in frames) + 1,
                           'segments': right['segments'], 'camera_hd_xywh': camera, 'all_canvas_union_hd_xyxy': union,
                           'reports_sha256': {kind: config.sha(value) for kind, value in raw.items()}}
            reports[name] = clips[name]['reports_sha256']
    assert seen == set(config.TARGET_FRAMES), 'all28 frames in displayed review'
    bundle = {'default_clip': DEFAULT_CLIP, 'clips': clips, 'reference_frames': [29], 'target_frames': list(config.TARGET_FRAMES)}
    template_path = HERE / 'native-template.html'
    template = template_path.read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1, 'single native review data slot'
    args.output.mkdir(parents=True)
    for name, raw in copies.items():
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    (args.output / 'review.html').write_text(template.replace('__DATA__', json.dumps(bundle, separators=(',', ':'))), encoding='utf-8', newline='\n')
    outputs = {name: config.sha(raw) for name, raw in copies.items()}
    outputs['review.html'] = config.sha((args.output / 'review.html').read_bytes())
    record = {'status': 'local native color review; unpublished; human color approval pending',
              'files_sha256': outputs, 'reports_sha256': reports,
              'builder_sha256': config.sha(Path(__file__).read_bytes()), 'template_sha256': config.sha(template_path.read_bytes()),
              'config_sha256': config.sha((config.HERE / 'config.py').read_bytes()),
              'candidate_directory': candidate_relative, 'candidate_preparation_sha256': config.sha(preparation_path.read_bytes()),
              'recipe_sha256': prep['recipe_sha256'], 'baseline_archive_sha256': config.BASELINE_SHA,
              'candidate_archive_sha256': prep['archive_sha256'], 'still_record_sha256': config.sha((args.stills / 'review-record.json').read_bytes()),
              'still_browser_validation_sha256': config.sha((args.stills / 'browser-validation.json').read_bytes()),
              'scope': 'Eight complete native clips: six routes and015/016 waits covering all28 selected poses. Earlier and corrected colors use identical geometry and observed timestamps. Both already contain009/010/012. Fixed cameras and full canvases; reference029 is unchanged. No human approval or production promotion.'}
    (args.output / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'PASS eight native color clips, {sum(len(c["frames"]) for c in clips.values())} displays, all28 poses and bound still review; unpublished')


if __name__ == '__main__':
    main()
