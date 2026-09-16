"""Exact native scene comparison against the transformed per-sprite skin mask."""
import config
import native_core as core

WIDTH, HEIGHT = 1280, 960


def compare_pixels(before, after, draw, mask):
    flip, x, y, frame = draw
    label = f'{frame:03}'
    width, height = mask.size
    core.require(mask.mode == 'L' and flip in (0, 1), 'skin mask mode/flip:' + label)
    x0, y0 = x * 2, y * 2
    core.require(0 <= x0 < x0 + width <= WIDTH and 0 <= y0 < y0 + height <= HEIGHT,
                 'skin mask placement:' + label)
    core.require(len(before) == len(after) == WIDTH * HEIGHT * 3, 'scene byte count:' + label)
    weights = mask.tobytes()
    changed = 0
    for sy in range(HEIGHT):
        row = sy * WIDTH * 3
        if not y0 <= sy < y0 + height:
            core.require(before[row:row+WIDTH*3] == after[row:row+WIDTH*3], 'outside skin canvas:' + label)
            continue
        first, last = row + x0 * 3, row + (x0 + width) * 3
        core.require(before[row:first] == after[row:first] and
                     before[last:row+WIDTH*3] == after[last:row+WIDTH*3], 'outside skin canvas:' + label)
        for sx in range(width):
            pixel = first + sx * 3
            if before[pixel:pixel+3] == after[pixel:pixel+3]:
                continue
            source_x = width - 1 - sx if flip else sx
            core.require(weights[(sy-y0)*width+source_x] > 0, 'outside transformed skin mask:' + label)
            changed += 1
    return changed


def compare_reports(report, expected, prep, folder, prior_folder, masks):
    for key in ('clip', 'segments', 'completed_waits', 'display_count', 'duration_ms', 'loaded_art'):
        core.require(report[key] == expected[key], 'unchanged native ' + key)
    core.require(len(report['displays']) == len(expected['displays']), 'same native display count')
    unchanged_frames = {row['frame'] for row in prep['replaced_members'] if row['changed_pixels'] == 0}
    changes, frames = 0, set()
    for observed, prior in zip(report['displays'], expected['displays']):
        for key in ('index', 'logical_ms', 'segment', 'segment_ms', 'role', 'actual_draw',
                    'stored_walk_row', 'draw_ordinal', 'stage_draw_ordinal', 'duration_ms'):
            core.require(observed[key] == prior[key], 'identical native display ' + key)
        before = core.codec.ppm(prior_folder / prior['ppm'])
        after = core.codec.ppm(folder / observed['ppm'])
        core.require(core.sha(before) == prior['pixels_sha256'], 'bound baseline image')
        core.require(core.sha(after) == observed['pixels_sha256'], 'bound corrected image')
        frame = observed['actual_draw'][3]
        core.require(frame in masks, 'covered current Johnny frame:' + str(frame))
        if frame in unchanged_frames:
            core.require(before == after, 'unchanged reference pixels:' + f'{frame:03}')
        changed = compare_pixels(before, after, observed['actual_draw'], masks[frame])
        if changed:
            changes += 1
            frames.add(frame)
        observed.update(baseline_pixels_sha256=prior['pixels_sha256'],
                        changed_scene_pixels=changed,
                        comparison='different only at transformed actual skin-mask support' if changed else 'full display identical')
    return changes, frames
