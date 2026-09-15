"""Reuse the proven arrival review player with exact front-route capture bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PRIOR = ROOT / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers'
sys.path.insert(0, str(PRIOR))
spec = importlib.util.spec_from_file_location('prior_arrival_viewer', PRIOR / 'build_review.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    destination = OUT / 'island-review-v1'
    assert not destination.exists(), 'preserve prior review'
    folders = {'baseline': OUT / 'baseline-v1/full', 'candidate': OUT / 'candidate-v1/full'}
    raw_reports = {kind: (folder / 'report.json').read_bytes() for kind, folder in folders.items()}
    reports = {kind: json.loads(raw) for kind, raw in raw_reports.items()}
    left, right = reports['baseline'], reports['candidate']
    assert left['executable_sha256'] == right['executable_sha256'] and right['status'] == 'PASS'
    assert len(left['displays']) == len(right['displays'])
    frames, copies, pose_index, previous = [], [], -1, None
    for a, b in zip(left['displays'], right['displays']):
        assert all(a[key] == b[key] for key in ('index', 'logical_ms', 'duration_ms', 'stored_walk_row', 'actual_draw'))
        if b['stored_walk_row'] != previous:
            pose_index += 1
            previous = b['stored_walk_row']
        row = {key: b[key] for key in ('logical_ms', 'duration_ms', 'comparison')}
        row.update({'draw_xy': b['actual_draw'][1:3], 'frame': b['actual_draw'][3], 'pose_index': pose_index})
        for kind, record in (('baseline', a), ('candidate', b)):
            pixels = prior.ppm(folders[kind] / record['ppm'])
            png_path = folders[kind] / record['png']
            png = png_path.read_bytes()
            assert sha(pixels) == record['pixels_sha256'] and sha(png) == record['png_sha256']
            with Image.open(png_path) as image:
                assert image.size == (1280, 960) and image.convert('RGB').tobytes() == pixels
            relative = f'images/{kind}/{record["png"]}'
            row[kind] = relative
            copies.append((relative, png))
        frames.append(row)
    data = {'duration_ms': right['duration_ms'], 'frames': frames, 'pose_count': pose_index + 1,
            'travel_pose_count': len(right['observed_rows']) - 1, 'arrival_frame': 17,
            'baseline_report_sha256': sha(raw_reports['baseline']), 'candidate_report_sha256': sha(raw_reports['candidate'])}
    page = prior.PAGE
    replacements = [
        ("Johnny's new arrival pose", "Johnny's front walk refresh", 2),
        ('Watch the same Cartoon walk settle into the arrival pose. The new standing artwork is on the right.',
         'Watch the current Cartoon front walk beside the proposed refresh. The new footwork is on the right.', 1),
        ('Current arrival', 'Current Cartoon', 1),
        ('New Cartoon arrival', 'Provisional front walk', 1),
        ('Only the standing pose is new. Use Previous pose and Next pose to check the last step into the arrival.',
         'Only walking frames 028 and 029 are revised. Watch the whole gait at Normal speed, then use the pose controls to inspect individual steps. The standing arrival is unchanged HD artwork.', 1),
        ('ctx.drawImage(images[kind][index],580,440,400,280,0,0,400,280)',
         'ctx.drawImage(images[kind][index],560,400,400,280,0,0,400,280)', 1),
        ("row.frame===18?'Arrival pose':`Walking pose ${row.pose_index+1} / 23`",
         "row.frame===data.arrival_frame?'Arrival pose (existing HD)':`Walking pose ${row.pose_index+1} / ${data.travel_pose_count}`", 1),
        ('(data.frames[index].pose_index+delta+24)%24', '(data.frames[index].pose_index+delta+data.pose_count)%data.pose_count', 1),
    ]
    for old, new, count in replacements:
        assert page.count(old) == count, 'unique player adaptation:' + old
        page = page.replace(old, new)
    description = ('Both panels use the approved Cartoon island and the same actual E-to-A route. The private candidate replaces only frames 028 and 029; frames 024-027 remain byte-identical. The last walking frame 027 is drawn at (300,242), then the existing mirrored HD017 arrival at (293,243) holds for 1.6 seconds. All timing, draw positions and background updates come from the same native Linux observer. This is port rendering and logical timing, not an original-executable or physical wall-clock comparison.')
    page, count = re.subn(r'<p class="muted">Both views use.*?</p><p id="technical">',
                         '<p class="muted">' + description + '</p><p id="technical">', page, count=1)
    assert count == 1
    page = page.replace('There are 47 observed displays', f'There are {len(frames)} observed displays')
    page = page.replace('__DATA__', json.dumps(data, separators=(',', ':')))
    destination.mkdir()
    for relative, raw in copies:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (destination / 'review.html').write_text(page, encoding='utf-8', newline='\n')
    evidence = {'status': 'unpublished technical review', 'html_sha256': sha((destination / 'review.html').read_bytes()),
                'image_files': {name: sha(raw) for name, raw in copies}, 'fixed_closeup_hd': [560, 400, 400, 280],
                'baseline_report_sha256': sha(raw_reports['baseline']), 'candidate_report_sha256': sha(raw_reports['candidate']),
                'builder_sha256': sha(Path(__file__).read_bytes()),
                'prior_player_sha256': sha((PRIOR / 'build_review.py').read_bytes()),
                'scope': 'Exact native PNGs and reused player; no publishing, production promotion or human acceptance.'}
    (destination / 'review-record.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    checker = (PRIOR / 'check_review.py').read_text(encoding='utf-8')
    for old, new, count in [
        ('x, y = 580, 440', 'x, y = 560, 400', 1),
        ("nativeReviewState.frame') == 22", "nativeReviewState.frame') == 27", 2),
        ("nativeReviewState.frame') == 18", "nativeReviewState.frame') == 17", 1),
        ("row['frame'] == 18", "row['frame'] == 28", 1),
    ]:
        assert checker.count(old) == count, 'unique browser checker adaptation:' + old
        checker = checker.replace(old, new)
    checker_path = OUT / 'check_review.py'
    assert not checker_path.exists(), 'preserve prior checker'
    checker_path.write_text(checker, encoding='utf-8', newline='\n')
    print(f'PASS unpublished front native review: {len(copies)} exact native PNGs, {len(frames)} displays')


if __name__ == '__main__':
    main()
