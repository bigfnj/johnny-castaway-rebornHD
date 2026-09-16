"""Observe native connecting routes, preserving all display events and timing."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import traceback
import config
import native_core as core

OUT, BASE = config.OUT, core.BASE
sha, require, save, codec = core.sha, core.require, core.save, core.codec


def parse(folder, phase, clip, candidate=False):
    text = (folder / 'capture.log').read_text()
    require(f'TURN DRIVER: island_seed=11 path_seed=2 clip={clip} style=cartoon' in text, 'actual configured connecting witness')
    require('TURN ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text, 'fixed island state')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text, 'native capture/decode witness')
    expected = config.contract()['clips'][clip]
    segments, displays, waits = {}, [], []
    segment = row = draw = None
    ordinal = stage_ordinal = -1
    for line in text.splitlines():
        start = re.search(r'TURN SEGMENT: (\w+) api=adsPlayWalk\(([^)]+)\) start_ms=(\d+)', line)
        end = re.search(r'TURN SEGMENT END: (\w+) end_ms=(\d+)', line)
        chosen = re.search(r'\. chosen path:\s+([A-F]+)', line)
        stored = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
        actual = re.search(r'TURN DRAW: flip=(\d+) x=(\d+) y=(\d+) frame=(\d+)', line)
        delay = re.search(r'TURN ANIMATE: delay_ticks=(\d+)', line)
        wait = re.search(r'TURN WAIT: ticks=(\d+) logical_ms=(\d+)', line)
        display = re.search(r'TURN DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
        if start:
            segment, stage_ordinal = start[1], -1
            require(segment in expected and segment not in segments, 'unique configured stage:' + segment)
            segments[segment] = {'api_arguments': list(map(int, start[2].split(','))), 'start_ms': int(start[3]), 'rows': [], 'draws': [], 'delays': [], 'chosen_path': None}
        if chosen:
            require(segment is not None and segments[segment]['chosen_path'] is None, 'one selected path per stage')
            segments[segment]['chosen_path'] = chosen[1]
        if end:
            require(end[1] == segment, 'matching stage end')
            segments[segment]['end_ms'] = int(end[2])
        if stored:
            row = list(map(int, stored.groups()))
            ordinal += 1
            stage_ordinal += 1
            segments[segment]['rows'].append(row)
        if actual:
            draw = list(map(int, actual.groups()))
            segments[segment]['draws'].append(draw)
        if delay:
            segments[segment]['delays'].append(int(delay[1]))
        if wait:
            waits.append(list(map(int, wait.groups())))
        if display:
            index, when, name = display.groups()
            require(draw == [row[0], row[1] - 1, row[2], row[3]], 'actual draw and stored row:' + index)
            require(0 <= stage_ordinal < len(expected[segment]['draws']), 'draw ordinal within source contract')
            role = expected[segment]['draws'][stage_ordinal]['role']
            pixels = codec.ppm(folder / name)
            encoded = codec.png_bytes(pixels)
            png = Path(name).with_suffix('.png').name
            (folder / png).write_bytes(encoded)
            displays.append({'index': int(index), 'logical_ms': int(when), 'segment': segment,
                             'segment_ms': int(when) - segments[segment]['start_ms'], 'role': role,
                             'stored_walk_row': row, 'actual_draw': draw, 'draw_ordinal': ordinal, 'stage_draw_ordinal': stage_ordinal,
                             'ppm': name, 'png': png, 'pixels_sha256': sha(pixels), 'png_sha256': sha(encoded)})
    require([d['index'] for d in displays] == list(range(1, len(displays) + 1)), 'contiguous native displays')
    require([w[1] for w in waits] == [d['logical_ms'] for d in displays], 'one display per completed native wait')
    accumulated = 0
    for ticks, when in waits:
        accumulated += ticks * 20
        require(accumulated == when, 'native accumulated timing')
    end_ms = 0
    for name, observed in segments.items():
        reference = expected[name]
        require(observed['api_arguments'] == reference['api_arguments'], 'actual source API:' + name)
        require(observed['chosen_path'] == reference['chosen_path'], 'actual selected configured path:' + name)
        reference_draws = [[r['flip_x'], r['x'], r['y'], r['frame']] for r in reference['draws']]
        if phase == 'smoke':
            require(name == 'prime' and observed['draws'] == reference_draws, 'initial approved standing smoke')
        else:
            require(observed['draws'] == reference_draws, 'source draw sequence:' + name)
            require(observed['delays'] == [r['delay_ticks'] for r in reference['draws']] + [0], 'source delay returns:' + name)
            require(observed['start_ms'] == end_ms, 'sequential native stage boundary:' + name)
            require(observed['end_ms'] - observed['start_ms'] == reference['expected_native_duration_ms'], 'observed first-timer stage duration:' + name)
            end_ms = observed['end_ms']
    if phase == 'smoke':
        require(len(displays) == 1 and displays[0]['logical_ms'] == 0 and 'stopping after 1 frame(s)' in text, 'one-frame smoke shutdown')
    else:
        require(list(segments) == list(expected), 'all configured native stages in order')
        require('finite clips returned; cleanup complete;' in text and displays[-1]['logical_ms'] == end_ms, 'finite native cleanup and endpoint')
        expected_arrival = expected['travel']['draws'][-1]
        require(displays[-1]['actual_draw'] == [expected_arrival[k] for k in ('flip_x','x','y','frame')]
                and displays[-1]['role'] == 'arrival', 'actual configured approved arrival')
    final = codec.ppm(folder / 'final.ppm')
    require(final == codec.ppm(folder / displays[-1]['ppm']), 'final native image identity')
    (folder / 'final.png').write_bytes(codec.png_bytes(final))
    for i, display in enumerate(displays):
        display['duration_ms'] = displays[i + 1]['logical_ms'] - display['logical_ms'] if i + 1 < len(displays) else 0
        require(display['duration_ms'] >= 0, 'nondecreasing native display time')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    for frame in (0,1,2,3,4,5,6,7,8,11,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29):
        require(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' in loaded, 'retained approved dependency:' + str(frame))
    for frame in config.CANDIDATE_FRAMES:
        selected = f'data/{"styles/cartoon" if candidate else "hd"}/BMP/JOHNWALK.BMP/{frame:03}.png'
        absent = f'data/{"hd" if candidate else "styles/cartoon"}/BMP/JOHNWALK.BMP/{frame:03}.png'
        require(selected in loaded and absent not in loaded, 'selected connecting dependency:' + str(frame))
    return {'status': 'PASS', 'clip': clip, 'phase': phase, 'segments': segments, 'displays': displays,
            'completed_waits': waits, 'display_count': len(displays), 'duration_ms': displays[-1]['logical_ms'],
            'loaded_art': loaded, 'log_sha256': sha((folder / 'capture.log').read_bytes()),
            'scope': 'Native port connecting route, actual API prime/departure/travel/waypoint/arrival; all observed timestamps and origins. No original-binary timing claim.', 'candidate': candidate}


def capture(exe, binding, clip, phase):
    folder = BASE / clip / phase
    require(not folder.exists(), 'preserve capture:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(OUT / 'baseline-pack.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')), stdout=log, stderr=subprocess.STDOUT, timeout=120)
    require(result.returncode == 0, 'native exit; retained log:' + clip + ':' + phase)
    report = parse(folder, phase, clip)
    report.update(command=command, exit_code=result.returncode, archive_sha256=sha((folder / 'scrantic_data.zip').read_bytes()), executable_sha256=sha(exe.read_bytes()))
    require(report['archive_sha256'] == binding['baseline_pack_sha256'] and report['executable_sha256'] == binding['executable_sha256'], 'execution identity')
    save(folder / 'report.json', report)
    print(f'PASS {clip} {phase}: {report["display_count"]} displays, {report["duration_ms"]}ms', flush=True)
    return report


def main():
    print('WITNESS connecting capture SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    exe, binding = core.build()
    reports = {}
    for clip in config.CLIPS:
        capture(exe, binding, clip, 'smoke')
    print('PASS all six native smoke checks before regression', flush=True)
    for clip in config.CLIPS:
        full = capture(exe, binding, clip, 'full')
        repeat = capture(exe, binding, clip, 'repeat')
        for field in ('displays', 'segments', 'completed_waits', 'loaded_art'):
            require(full[field] == repeat[field], 'exact fresh native repeat:' + clip + ':' + field)
        reports[clip] = {key: full[key] for key in ('display_count', 'duration_ms', 'segments')}
    require(core.protected() == binding['protected_sha256'], 'all protected production inputs unchanged')
    save(BASE / 'summary.json', {'status': 'PASS', 'clips': reports, 'baseline_pack_sha256': binding['baseline_pack_sha256'], 'executable_sha256': binding['executable_sha256'],
         'capture_helper_sha256': sha(Path(__file__).read_bytes()), 'config_sha256': sha((config.HERE / 'config.py').read_bytes()), 'protected_inputs_unchanged': len(binding['protected_sha256']),
         'verification': 'All six smoke captures pass before six full and exact fresh-process repeats. Independent compiled C trace checked before native rendering.',
         'scope': 'Current40-asset baseline, HD009/010/012; no candidates, publication or production changes.'})
    print('PASS six native connecting clips and unchanged protected inputs', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        save(OUT / 'baseline-failure.json', {'traceback': traceback.format_exc(), 'helper_sha256': sha(Path(__file__).read_bytes())})
        raise
