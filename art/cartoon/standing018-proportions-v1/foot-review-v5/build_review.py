"""Build foot-v5 motion from checked current-v2 and new native captures."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'assets/scrantic_data.zip').is_file())
sys.path.insert(0, str(ROOT / 'art/cartoon/skin-tone-v1/native-review'))
import config

CLIPS = ('waypoint_front', 'front_arc', 'waypoint_rear')
LABELS = {'waypoint_front': 'Same-position arrival: 023 to 018',
          'front_arc': 'Departure from 018', 'waypoint_rear': 'Mirrored arrival: 022 to 018'}
BASE = ROOT / 'build/standing018-proportions/native-review/color-v2'
REVISED = ROOT / 'build/standing018-proportions/foot-v5-motion'
MOTION = REVISED
BASE_SHA = '7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52'
CANDIDATE_SHA = '561edb2c9b4b4857b723af1505ce8d2654616aae2942325389604a4d88804521'
RUNTIME_SHA = '5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f'
MEMBER = 'data/styles/cartoon/BMP/JOHNWALK.BMP/018.png'
TIMELINE_KEYS = ('index', 'logical_ms', 'duration_ms', 'segment', 'segment_ms', 'role',
                 'actual_draw', 'draw_ordinal', 'stage_draw_ordinal')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda p: json.loads(p.read_bytes())


def folder(clip):
    return REVISED / clip


def baseline_folder(clip):
    return (BASE if clip == 'front_arc' else ROOT / 'build/standing018-proportions/motion-v1') / clip


def validate_pair(left, right, clip, executable):
    """Validate identities before consuming reports as a viewer timeline."""
    contract = config.contract()['clips'][clip]
    for kind, report, digest in [('baseline', left, BASE_SHA), ('candidate', right, CANDIDATE_SHA)]:
        assert report['status'] == 'PASS' and report['clip'] == clip and report['phase'] == 'full', 'capture clip/phase identity:' + kind + ':' + clip
        assert report['archive_sha256'] == digest and report['executable_sha256'] == executable, 'capture archive/executable identity:' + kind + ':' + clip
        for stage, expected in contract.items():
            actual = report['segments'][stage]
            draws = [[r[k] for k in ('flip_x', 'x', 'y', 'frame')] for r in expected['draws']]
            assert actual['api_arguments'] == expected['api_arguments'] and actual['chosen_path'] == expected['chosen_path'] and actual['draws'] == draws, 'capture route contract:' + kind + ':' + clip + ':' + stage
        assert report['duration_ms'] == config.CLIPS[clip]['duration_ms'], 'native clip duration:' + kind + ':' + clip
        assert report['display_count'] == len(report['displays']), 'native display count:' + kind + ':' + clip
    assert right['runtime018_sha256'] == RUNTIME_SHA, 'capture selected018 identity:' + clip
    assert len(left['displays']) == len(right['displays']), 'matching display count:' + clip
    assert left['completed_waits'] == right['completed_waits'] and left['segments'] == right['segments'], 'matching native waits and stages:' + clip
    for a, b in zip(left['displays'], right['displays']):
        assert all(a[k] == b[k] for k in TIMELINE_KEYS), 'matching native panel timeline:' + clip + ':' + str(a['index'])
    return right['displays']


def build(output):
    assert not output.exists(), 'preserve existing018 motion review'
    prep_path = REVISED / 'preparation.json'
    prep = load(prep_path)
    assert prep['status'] == 'PASS' and prep['base_archive_sha256'] == BASE_SHA and prep['archive_sha256'] == CANDIDATE_SHA and prep['runtime018_sha256'] == RUNTIME_SHA, 'pinned prepared018 candidate'
    files, records, clips = {}, {}, {}
    summary = load(MOTION / 'summary.json')
    assert summary['status'] == 'PASS' and set(summary['clips']) == set(CLIPS) and summary['archive_sha256'] == CANDIDATE_SHA and summary['runtime018_sha256'] == RUNTIME_SHA, 'complete selected018 native family'
    assert summary['ordered_phases_per_clip'] == ['smoke', 'full', 'repeat'], 'ordered native smoke before regressions'
    for name in ('preparation.json', 'summary.json'):
        files['inputs/native-motion-' + name] = (MOTION / name).read_bytes()
    for path in (prep_path, REVISED / 'color-recipe.json'):
        files['inputs/' + path.name] = path.read_bytes()
    assert sha(files['inputs/color-recipe.json']) == prep['color_recipe_sha256'], 'prepared018 color record identity'
    paths = {'baseline': BASE / 'scrantic_data.zip', 'candidate': REVISED / 'scrantic_data.zip'}
    assert sha(paths['baseline'].read_bytes()) == BASE_SHA and sha(paths['candidate'].read_bytes()) == CANDIDATE_SHA, 'pinned comparison archives'
    with zipfile.ZipFile(paths['baseline']) as old, zipfile.ZipFile(paths['candidate']) as new:
        names = old.namelist()
        assert len(names) == len(set(names)) == 2594 and new.namelist() == names, 'same2594 archive members'
        assert sha(new.read(MEMBER)) == RUNTIME_SHA and old.read(MEMBER) != new.read(MEMBER), 'exact revised018 member'
        assert all(old.read(n) == new.read(n) for n in names if n != MEMBER), '2593 unchanged member payloads'
        for clip in CLIPS:
            sources = {'baseline': baseline_folder(clip) / 'full', 'candidate': folder(clip) / 'full'}
            reports = {kind: load(p / 'report.json') for kind, p in sources.items()}
            left, right = reports['baseline'], reports['candidate']
            validate_pair(left, right, clip, prep['executable_sha256'])
            # Smoke must have completed before the full pass; the fresh repeat
            # must preserve every native display and timeline.
            smoke = load(folder(clip) / 'smoke/report.json')
            repeat = load(folder(clip) / 'repeat/report.json')
            assert smoke['status'] == repeat['status'] == 'PASS' and smoke['phase'] == 'smoke' and repeat['phase'] == 'repeat', 'native smoke/full/repeat completion:' + clip
            for report in (smoke, repeat):
                assert report['clip'] == clip and report['archive_sha256'] == CANDIDATE_SHA and report['runtime018_sha256'] == RUNTIME_SHA, 'native phase identity:' + clip
            assert all(right[k] == repeat[k] for k in ('displays', 'segments', 'completed_waits', 'loaded_art')), 'fresh native repeat identity:' + clip
            for kind, p in sources.items():
                relative = 'inputs/' + clip + '/' + kind + '-full.json'
                files[relative] = (p / 'report.json').read_bytes()
                records[relative] = {'path': (p / 'report.json').relative_to(ROOT).as_posix(), 'sha256': sha(files[relative])}
            for phase in ('smoke', 'repeat'):
                p = folder(clip) / phase / 'report.json'
                relative = 'inputs/' + clip + '/candidate-' + phase + '.json'
                files[relative] = p.read_bytes()
                records[relative] = {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(files[relative])}
            frames, rectangles = [], []
            for a, b in zip(left['displays'], right['displays']):
                row = {k: b[k] for k in TIMELINE_KEYS if k != 'index'}
                row.update(frame=b['actual_draw'][3], pose_index=b['draw_ordinal'])
                flip, x, y, frame = b['actual_draw']
                member = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
                with Image.open(io.BytesIO(new.read(member))) as sprite:
                    w, h = sprite.size
                with Image.open(io.BytesIO(old.read(member))) as sprite:
                    assert sprite.size == (w, h), 'unchanged full sprite canvas:' + str(frame)
                rectangles.append([x * 2, y * 2, x * 2 + w, y * 2 + h])
                for kind, display in [('baseline', a), ('candidate', b)]:
                    path = sources[kind] / display['png']
                    raw = path.read_bytes()
                    assert sha(raw) == display['png_sha256'], 'bound native PNG:' + clip + ':' + kind + ':' + display['png']
                    with Image.open(io.BytesIO(raw)) as im:
                        assert im.size == (1280, 960) and sha(im.convert('RGB').tobytes()) == display['pixels_sha256'], 'bound native pixels:' + clip + ':' + kind
                    relative = 'images/' + sha(raw) + '.png'
                    assert relative not in files or files[relative] == raw, 'shared image identity'
                    files[relative] = raw
                    row[kind] = relative
                frames.append(row)
            union = [min(v[0] for v in rectangles), min(v[1] for v in rectangles), max(v[2] for v in rectangles), max(v[3] for v in rectangles)]
            box = [max(0, union[0] - 16), max(0, union[1] - 16), min(1280, union[2] + 16), min(960, union[3] + 16)]
            camera = [box[0], box[1], box[2] - box[0], box[3] - box[1]]
            clips[clip] = {'label': LABELS[clip], 'route_label': config.CLIPS[clip]['label'], 'frames': frames,
                           'duration_ms': right['duration_ms'], 'pose_count': max(r['pose_index'] for r in frames) + 1,
                           'segments': right['segments'], 'camera_hd_xywh': camera, 'all_canvas_union_hd_xyxy': union}
    bundle = {'default_clip': 'waypoint_front', 'clips': clips, 'reference_frames': [18], 'target_frames': [18]}
    template = (HERE / 'template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1, 'single review data slot'
    files['review.html'] = template.replace('__DATA__', json.dumps(bundle, separators=(',', ':'))).encode()
    output.mkdir(parents=True)
    for name, raw in files.items():
        p = output / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
    record = {'status': 'native motion comparison; human motion review pending', 'files_sha256': {n: sha(b) for n, b in files.items()},
              'source_reports': records, 'baseline_archive_sha256': BASE_SHA, 'candidate_archive_sha256': CANDIDATE_SHA,
              'runtime018_sha256': RUNTIME_SHA, 'executable_sha256': prep['executable_sha256'],
              'builder_sha256': sha(Path(__file__).read_bytes()), 'template_sha256': sha((HERE / 'template.html').read_bytes()),
              'config_sha256': sha(Path(config.__file__).read_bytes()), 'clips': list(CLIPS),
              'scope': 'Three native clips, fixed shared cameras, all actual displays/timestamps and018 occurrences. Same approved lighter skin target; only018 proportions changed. No invented hold, position adjustment, production promotion or original-executable timing claim.'}
    (output / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS three018 native clips; ' + str(sum(len(c['frames']) for c in clips.values())) + ' actual displays; all other archive members retained', flush=True)


def build_contact(output):
    original = ROOT / 'build/standing018-proportions/original-mirror-v1/full'
    sources = {'original': original, 'current': baseline_folder('waypoint_rear') / 'full',
               'revised': folder('waypoint_rear') / 'full'}
    archives = {'original': 'd7797181cf2e30699709946f0983b6899f0c7428785f9c596dea8ac150619f20',
                'current': BASE_SHA, 'revised': CANDIDATE_SHA}
    labels = {'original': 'Original pose', 'current': 'Previous version', 'revised': 'Corrected foot'}
    notes = {'original': 'Original pose at this exact arrival.', 'current': 'Accepted shorts; smaller foot still high.', 'revised': 'The smaller foot has been lowered.'}
    records, files, panels = {}, {}, []
    for kind, folder_path in sources.items():
        raw = (folder_path / 'report.json').read_bytes()
        report = json.loads(raw)
        assert report['status'] == 'PASS' and report['phase'] == 'full' and report['clip'] == 'waypoint_rear' and report['archive_sha256'] == archives[kind], 'contact exact source report:' + kind
        row = report['displays'][62]
        assert row['index'] == 63 and row['logical_ms'] == 4920 and row['actual_draw'] == [1, 394, 209, 18], 'contact actual mirrored arrival:' + kind
        png = (folder_path / row['png']).read_bytes()
        assert sha(png) == row['png_sha256'], 'contact selected PNG:' + kind
        with Image.open(io.BytesIO(png)) as im:
            assert im.size == (1280, 960) and sha(im.convert('RGB').tobytes()) == row['pixels_sha256'], 'contact selected native pixels:' + kind
        files[kind + '.png'] = png
        files['inputs/' + kind + '-report.json'] = raw
        records[kind] = report
        panels.append({'kind': kind, 'label': labels[kind], 'note': notes[kind], 'image': kind + '.png',
                       'png_sha256': sha(png), 'report_sha256': sha(raw), 'archive_sha256': archives[kind]})
    assert records['original']['reference_report_sha256'] == sha(files['inputs/current-report.json']), 'original contact binds this exact current report'
    for kind in ('original', 'revised'):
        assert records[kind]['executable_sha256'] == records['current']['executable_sha256'] and records[kind]['duration_ms'] == records['current']['duration_ms'], 'contact same observer and duration:' + kind
        common_keys = ('index', 'logical_ms', 'duration_ms', 'role', 'actual_draw')
        assert len(records[kind]['displays']) == len(records['current']['displays']) and all(all(a[k] == b[k] for k in common_keys) for a,b in zip(records[kind]['displays'], records['current']['displays'])), 'contact same observed display timeline:' + kind
    bundle = {'panels': panels, 'pose': [784, 410, 80, 178], 'feet': [792, 546, 60, 34],
              'frame': 18, 'draw': [1, 394, 209, 18], 'logical_ms': 4920, 'display_index': 63,
              'motion': 'motion/review.html'}
    template = (HERE / 'contact-template.html').read_text(encoding='utf-8')
    assert template.count('__DATA__') == 1, 'single contact data slot'
    files['review.html'] = template.replace('__DATA__', json.dumps(bundle, separators=(',', ':'))).encode()
    assert not (output / 'review.html').exists(), 'preserve prior contact landing'
    for name, raw in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    record = {'status': 'PASS; human foot-contact review pending', 'bundle': bundle,
              'files_sha256': {name: sha(raw) for name, raw in files.items()},
              'motion_record_sha256': sha((output / 'motion/review-record.json').read_bytes()),
              'builder_sha256': sha(Path(__file__).read_bytes()), 'contact_template_sha256': sha((HERE / 'contact-template.html').read_bytes()),
              'baseline_archive_sha256': BASE_SHA, 'candidate_archive_sha256': CANDIDATE_SHA, 'runtime018_sha256': RUNTIME_SHA,
              'scope': 'Original/current-v2/new mirrored018 still, separate two-panel actual motion. Diagnostic source palette explained in About; no original synchronized walking claim.'}
    (output / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS original/current-v2/new contact landing at exact mirrored display063', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    output = p.parse_args().output
    build(output / 'motion')
    build_contact(output)
