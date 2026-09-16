"""Capture exact native waiting rings from the shared stage configuration."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import config
import native_core as core

OUT = Path('/out')
BASE = OUT / 'baseline-v1'
sha, require, save, codec = core.sha, core.require, core.save, core.codec


def parse(folder, phase, clip, candidate=False):
    text = (folder / 'capture.log').read_text()
    require(f'TURN DRIVER: island_seed=11 path_seed=2 clip={clip} style=cartoon' in text, 'actual configured ring witness')
    require('TURN ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text, 'fixed island state')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text, 'native capture/decode witness')
    expected = config.contract()['clips'][clip]
    segments, displays, waits = {}, [], []
    segment = row = draw = None
    ordinal = -1
    for line in text.splitlines():
        start = re.search(r'TURN SEGMENT: (\w+) api=adsPlayWalk\(([^)]+)\) start_ms=(\d+)', line)
        end = re.search(r'TURN SEGMENT END: (\w+) end_ms=(\d+)', line)
        stored = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
        actual = re.search(r'TURN DRAW: flip=(\d+) x=(\d+) y=(\d+) frame=(\d+)', line)
        delay = re.search(r'TURN ANIMATE: delay_ticks=(\d+)', line)
        wait = re.search(r'TURN WAIT: ticks=(\d+) logical_ms=(\d+)', line)
        display = re.search(r'TURN DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
        if start:
            segment = start[1]
            require(segment in expected and segment not in segments, 'unique configured stage:' + segment)
            segments[segment] = {'api_arguments': list(map(int, start[2].split(','))), 'start_ms': int(start[3]), 'rows': [], 'draws': [], 'delays': [], 'heading': expected[segment]['destination_heading']}
        if end:
            segments[end[1]]['end_ms'] = int(end[2])
        if stored:
            row = list(map(int, stored.groups()))
            ordinal += 1
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
            pixels = codec.ppm(folder / name)
            encoded = codec.png_bytes(pixels)
            png = Path(name).with_suffix('.png').name
            (folder / png).write_bytes(encoded)
            displays.append({'index': int(index), 'logical_ms': int(when), 'segment': segment,
                             'segment_ms': int(when) - segments[segment]['start_ms'], 'heading': segments[segment]['heading'],
                             'stored_walk_row': row, 'actual_draw': draw, 'draw_ordinal': ordinal,
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
        reference_draws = [[r['flip_x'], r['x'], r['y'], r['frame']] for r in reference['draws']]
        if phase == 'smoke':
            require(name == 'prime' and observed['draws'] == reference_draws, 'initial approved016 smoke')
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
        require({d['heading'] for d in displays} == set(range(8)), 'all eight headings observed')
    final = codec.ppm(folder / 'final.ppm')
    require(final == codec.ppm(folder / displays[-1]['ppm']), 'final native image identity')
    (folder / 'final.png').write_bytes(codec.png_bytes(final))
    for i, display in enumerate(displays):
        display['duration_ms'] = displays[i + 1]['logical_ms'] - display['logical_ms'] if i + 1 < len(displays) else 0
        require(display['duration_ms'] >= 0, 'nondecreasing native display time')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    for frame in (16, 17, 18, 24, 25, 26, 27, 28, 29):
        require(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' in loaded, 'retained approved dependency:' + str(frame))
    for frame in config.CANDIDATE_FRAMES:
        selected = f'data/{"styles/cartoon" if candidate else "hd"}/BMP/JOHNWALK.BMP/{frame:03}.png'
        absent = f'data/{"hd" if candidate else "styles/cartoon"}/BMP/JOHNWALK.BMP/{frame:03}.png'
        require(selected in loaded and absent not in loaded, 'selected000015 dependency:' + str(frame))
    return {'status': 'PASS', 'clip': clip, 'phase': phase, 'segments': segments, 'displays': displays,
            'completed_waits': waits, 'display_count': len(displays), 'duration_ms': displays[-1]['logical_ms'],
            'loaded_art': loaded, 'log_sha256': sha((folder / 'capture.log').read_bytes()),
            'scope': 'Actual native eight-heading adjacent turns plus priming; all actual delays/mirrors/origins. New000015 candidate.' if candidate else 'Approved016017 private baseline and existing018, with current HD000015. Native timing only.'}


def capture(exe, binding, clip, phase):
    folder = BASE / clip / phase
    require(not folder.exists(), 'preserve capture:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(OUT / 'baseline-pack.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=120)
    require(result.returncode == 0, 'native exit; retained log:' + clip + ':' + phase)
    report = parse(folder, phase, clip)
    report.update({'command': command, 'exit_code': result.returncode, 'archive_sha256': sha((folder / 'scrantic_data.zip').read_bytes()), 'executable_sha256': sha(exe.read_bytes())})
    require(report['archive_sha256'] == binding['baseline_pack_sha256'] and report['executable_sha256'] == binding['executable_sha256'], 'execution identity')
    save(folder / 'report.json', report)
    print(f'PASS {clip} {phase}: {report["display_count"]} displays, {report["duration_ms"]}ms', flush=True)
    return report


def main():
    print('WITNESS ring capture SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    exe, binding = core.build()
    reports = {}
    for clip in config.CLIPS:
        capture(exe, binding, clip, 'smoke')
        full = capture(exe, binding, clip, 'full')
        repeat = capture(exe, binding, clip, 'repeat')
        for field in ('displays', 'segments', 'completed_waits', 'loaded_art'):
            require(full[field] == repeat[field], 'exact fresh native repeat:' + clip + ':' + field)
        reports[clip] = {key: full[key] for key in ('display_count', 'duration_ms', 'segments')}
    require(core.protected() == binding['protected_sha256'], 'all protected production inputs unchanged')
    save(BASE / 'summary.json', {'status': 'PASS', 'clips': reports, 'baseline_pack_sha256': binding['baseline_pack_sha256'],
         'executable_sha256': binding['executable_sha256'], 'capture_helper_sha256': sha(Path(__file__).read_bytes()),
         'config_sha256': sha((OUT / 'config.py').read_bytes()), 'protected_inputs_unchanged': len(binding['protected_sha256']),
         'verification': 'Each direction smoke then full then exact fresh-process repeat',
         'scope': 'Baseline actual adjacent-heading rings only. No candidate000015, publication or production changes.'})
    print('PASS both full waiting rings and unchanged protected inputs', flush=True)


if __name__ == '__main__':
    main()
