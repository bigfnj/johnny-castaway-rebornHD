"""Replay geometric screenshot identification without altering any image or artwork.

Requires the earlier connecting native candidate-v2 captures in ignored build/.
Writes only a new JSON report; the evidence directory is never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, __version__ as pillow_version


ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'assets/scrantic_data.zip').is_file())
BUNDLE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1'
NATIVE = ROOT / 'build/connecting-poses/native-motion-v1'
PINS = {
    'user-shot1.png': '87f2c0b5f04ccc127ac51cce88ad0dc585318dac496d9f42243400e757bca2f0',
    'user-shot2.png': '9efae44b05d928cb9d046f55616d9fb02eb844f80701cfff9d154d331c8e2a91',
}
SHOTS = [('user-shot1.png', (44, 46), 24), ('user-shot2.png', (40, 44), 29)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def metrics(a, b):
    return {'rgb_mean_absolute_error_0_255': float(np.abs(a.astype(float) - b.astype(float)).mean()),
            'exact_rgb_pixel_fraction': float((a == b).all(axis=2).mean())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing existing screenshot-match result: ' + str(args.output))
    review_path = NATIVE / 'review-v1/review-record.json'
    review = json.loads(review_path.read_text())
    results = []
    for name, (sx, sy), expected_frame in SHOTS:
        shot_path = BUNDLE / 'review-evidence/skin-color-audit-v1' / name
        assert sha(shot_path.read_bytes()) == PINS[name], 'exact user screenshot:' + name
        with Image.open(shot_path) as im:
            shot = np.array(im.convert('RGB'))
        scene = shot[sy:sy + 350, sx:min(sx + 475, shot.shape[1])]
        ranked, excluded = [], []
        for clip, (x, y, w, h) in review['cameras_hd_xywh'].items():
            displayed_width = round(w * 350 / h)
            if displayed_width < scene.shape[1]:
                excluded.append({'clip': clip, 'natural_width_at_350px_height': displayed_width,
                                 'reason': 'Too narrow to cover the observed scene width without distorting the fixed camera.'})
                continue
            folder = NATIVE / 'candidate-v2' / clip / 'full'
            report_path = folder / 'report.json'
            assert sha(report_path.read_bytes()) == review['reports_sha256'][clip]['candidate'], 'bound capture report:' + clip
            report = json.loads(report_path.read_text())
            for display in report['displays']:
                native_path = folder / display['png']
                assert sha(native_path.read_bytes()) == display['png_sha256'], 'bound native PNG:' + str(native_path)
                with Image.open(native_path) as im:
                    scaled = np.array(im.convert('RGB').crop((x, y, x + w, y + h)).resize((displayed_width, 350), Image.Resampling.NEAREST))
                observed = scaled[:, :scene.shape[1]]
                ranked.append(dict(metrics(observed, scene), clip=clip, display_index=display['index'],
                                   logical_ms=display['logical_ms'], actual_draw=display['actual_draw'],
                                   pose_index_zero_based=display['draw_ordinal'], png=record(native_path),
                                   report=record(report_path)))
        ranked.sort(key=lambda item: item['rgb_mean_absolute_error_0_255'])
        best = ranked[0]
        assert best['clip'] == 'waypoint_front' and best['actual_draw'][3] == expected_frame, 'matched scene and pose:' + name
        assert best['rgb_mean_absolute_error_0_255'] < 0.03 and best['exact_rgb_pixel_fraction'] > 0.996, 'near-exact scene match:' + name
        ties = [v for v in ranked if v['rgb_mean_absolute_error_0_255'] == best['rgb_mean_absolute_error_0_255']]
        next_distinct = next(v for v in ranked if v['actual_draw'] != best['actual_draw'])
        assert next_distinct['rgb_mean_absolute_error_0_255'] > 5, 'distinct-pose separation:' + name
        x, y, w, h = review['cameras_hd_xywh'][best['clip']]
        with Image.open(ROOT / best['png']['path']) as im:
            scaled = np.array(im.convert('RGB').crop((x, y, x + w, y + h)).resize((475, 350), Image.Resampling.NEAREST))
        _, px, py, _ = best['actual_draw']
        box = [int((px * 2 - x) * 475 / w), int((py * 2 - y) * 350 / h),
               int((px * 2 + 64 - x) * 475 / w), int((py * 2 + 150 - y) * 350 / h)]
        a = scaled[box[1]:box[3], box[0]:box[2]]
        b = scene[box[1]:box[3], box[0]:box[2]]
        sprite_metrics = metrics(a, b)
        assert sprite_metrics['exact_rgb_pixel_fraction'] > 0.996, 'sprite silhouette and interior match:' + name
        results.append({'screenshot': record(shot_path), 'screenshot_scene_origin_xy': [sx, sy],
                        'visible_scene_size': [scene.shape[1], scene.shape[0]],
                        'matching_camera_hd_xywh': [x, y, w, h], 'nearest_preview_size': [475, 350],
                        'matching_displays': ties, 'next_distinct_pose': next_distinct,
                        'full_sprite_canvas_region_in_preview_xyxy': box, 'sprite_region_metrics': sprite_metrics,
                        'native_displays_compared': len(ranked), 'excluded_by_scene_width': excluded})
    first = Image.open(NATIVE / 'candidate-v2/waypoint_front/full/display-005.png')
    second = Image.open(NATIVE / 'candidate-v2/waypoint_front/full/display-006.png')
    try:
        crop_equal = np.array_equal(np.array(first.crop((850, 420, 1138, 632))), np.array(second.crop((850, 420, 1138, 632))))
    finally:
        first.close()
        second.close()
    assert crop_equal, '029 repeated display camera crop identity'
    result = {'status': 'PASS', 'method': 'Compare whole scene and sprite-canvas RGB pixels after the recorded fixed native camera and nearest-neighbor display scaling; not a palette-median inference.',
              'script': record(Path(__file__)), 'review_record': record(review_path),
              'pillow_version': pillow_version, 'numpy_version': np.__version__, 'matches': results,
              'limits': ['Screenshot1 identifies frame024 at360ms in Front waypoint.',
                         'Screenshot2 identifies frame029 at240ms or320ms in Front waypoint. Those camera crops are identical; the full1280x960 captures differ elsewhere.',
                         'The screenshot crops exclude UI timing labels. This establishes the source pose and scene, not the exact wall-clock moment.',
                         'Small screenshot/render rounding differences remain; this is a near-exact comparison, not byte identity.',
                         'No image, color, alpha, geometry, production archive or existing evidence was modified.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS screenshot1 = mirrored024, Front waypoint, display007 at360ms')
    print('PASS screenshot2 = mirrored029, Front waypoint, displays005/006 at240/320ms')
    print('PASS whole-scene and full-sprite-canvas matches; raw source and runtime identities are separate from color statistics')


if __name__ == '__main__':
    main()
