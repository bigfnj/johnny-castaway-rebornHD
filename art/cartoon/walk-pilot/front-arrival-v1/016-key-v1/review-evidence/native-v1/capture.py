"""Capture both real same-spot turn directions, with native priming and smoke first."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

SOURCE = Path('/source')
OUT = Path('/out')
BASE = OUT / 'baseline-v1'
FORMAT = SOURCE / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec = importlib.util.spec_from_file_location('turn_codec', FORMAT)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
CLIPS = {'A1-to-A7': (1, 7), 'A7-to-A1': (7, 1)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('turn capture: ' + label)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def protected():
    result = {path.relative_to(SOURCE).as_posix(): sha(path.read_bytes())
              for folder in ('src', 'platform', 'third_party/miniz')
              for path in (SOURCE / folder).rglob('*') if path.is_file() and path.suffix in ('.c', '.h')}
    for name in ('CMakeLists.txt', 'assets/scrantic_data.zip', FORMAT.relative_to(SOURCE).as_posix()):
        result[name] = sha((SOURCE / name).read_bytes())
    return result


def contract():
    path = SOURCE / 'art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json'
    trace = json.loads(path.read_bytes())['native_trace']['cases']
    cases = {}
    for clip, (start, end) in CLIPS.items():
        cases[clip] = {segment: trace[f'A-turn-{a}-{b}'] for segment, a, b in [('prime', start, start), ('turn', start, end)]}
    require([d['frame'] for d in cases['A1-to-A7']['turn']['draws']] == [16, 17, 17], 'negative native repeated final017')
    require([d['frame'] for d in cases['A7-to-A1']['turn']['draws']] == [16, 17], 'positive native016 then017')
    return {'trace_source': path.relative_to(SOURCE).as_posix(), 'trace_sha256': sha(path.read_bytes()), 'clips': cases,
            'scope': 'Draw arguments and returned delays from independently compiled untouched walk.c. Display timestamps observed separately, including adsPlayWalk first-timer behavior.'}


def build():
    require(not BASE.exists(), 'preserve baseline build evidence')
    prep = json.loads((OUT / 'preparation.json').read_bytes())
    inputs = protected()
    require(inputs['assets/scrantic_data.zip'] == prep['production_archive_sha256'], 'production source archive identity')
    require(sha((OUT / 'route_driver.c').read_bytes()) == prep['adapted_driver_sha256'], 'prepared observer identity')
    require(sha((OUT / 'baseline-pack.zip').read_bytes()) == prep['baseline_pack_sha256'], 'approved017 private baseline identity')
    BASE.mkdir()
    text = (SOURCE / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    exe = BASE / 'front_turn_probe'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX',
               '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz',
               '/out/route_driver.c', *['/source/' + name for name in sources],
               '-Wl,--wrap=eventsWaitTick', '-Wl,--wrap=platformUpdateWindow', '-Wl,--wrap=grDrawSprite',
               '-Wl,--wrap=grDrawSpriteFlip', '-Wl,--wrap=walkAnimate', '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (BASE / 'build.stdout.txt').write_text(result.stdout)
    (BASE / 'build.stderr.txt').write_text(result.stderr)
    require(result.returncode == 0 and exe.stat().st_mtime_ns >= started, 'fresh successful native build')
    binding = {'command': command, 'source_commit': prep['source_commit'], 'executable_sha256': sha(exe.read_bytes()),
               'driver_sha256': prep['adapted_driver_sha256'], 'executable_mtime_ns': exe.stat().st_mtime_ns,
               'build_started_ns': started, 'image_id': prep['image_id'], 'protected_sha256': inputs,
               'compiler': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0],
               'libc': subprocess.check_output(['ldd', '--version'], text=True).splitlines()[0],
               'capture_helper_sha256': sha(Path(__file__).read_bytes()), 'codec_sha256': sha(FORMAT.read_bytes()),
               'baseline_pack_sha256': prep['baseline_pack_sha256']}
    save(BASE / 'build.json', binding)
    save(BASE / 'route-contract.json', contract())
    print('PASS fresh turn observer built; production sources untouched', flush=True)
    return exe, binding


def parse(folder, phase, clip, expected, candidate016=False):
    text = (folder / 'capture.log').read_text()
    require(f'TURN DRIVER: island_seed=11 path_seed=2 clip={clip} style=cartoon' in text, 'actual clip witness:' + clip)
    require('TURN ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text, 'deterministic island')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text, 'real native capture/decode')
    segments, displays, waits = {}, [], []
    segment = None
    row = draw = None
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
            segments[segment] = {'api_arguments': list(map(int, start[2].split(','))), 'start_ms': int(start[3]), 'rows': [], 'draws': [], 'delays': []}
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
            require(draw == [row[0], row[1] - 1, row[2], row[3]], 'real draw matches stored row:' + index)
            pixels = codec.ppm(folder / name)
            encoded = codec.png_bytes(pixels)
            png = Path(name).with_suffix('.png').name
            (folder / png).write_bytes(encoded)
            displays.append({'index': int(index), 'logical_ms': int(when), 'segment': segment,
                             'segment_ms': int(when) - segments[segment]['start_ms'], 'stored_walk_row': row,
                             'actual_draw': draw, 'draw_ordinal': ordinal, 'ppm': name, 'png': png,
                             'pixels_sha256': sha(pixels), 'png_sha256': sha(encoded)})
    require([d['index'] for d in displays] == list(range(1, len(displays) + 1)), 'contiguous native displays')
    require([w[1] for w in waits] == [d['logical_ms'] for d in displays], 'one display per completed wait')
    cumulative = 0
    for ticks, when in waits:
        cumulative += ticks * 20
        require(cumulative == when, 'observed timing accumulation')
    for name, observed in segments.items():
        reference = expected['clips'][clip][name]
        rows = reference['draws']
        require(observed['api_arguments'] == reference['api_arguments'], 'actual API:' + name)
        if phase == 'smoke':
            require(name == 'prime' and observed['draws'][0] == [rows[0]['flip_x'], rows[0]['x'], rows[0]['y'], rows[0]['frame']], 'initial approved017 smoke')
        else:
            require(observed['draws'] == [[r['flip_x'], r['x'], r['y'], r['frame']] for r in rows], 'trace actual draws:' + name)
            require(observed['delays'] == [r['delay_ticks'] for r in rows] + [0], 'trace returned delays:' + name)
            require(observed['end_ms'] >= observed['start_ms'], 'segment endpoint:' + name)
    if phase == 'smoke':
        require(len(displays) == 1 and displays[0]['logical_ms'] == 0 and 'stopping after 1 frame(s)' in text, 'one-display shutdown')
    else:
        require(set(segments) == {'prime', 'turn'} and 'finite clips returned; cleanup complete;' in text, 'finite native clip cleanup')
        require(segments['prime']['start_ms'] == 0 and segments['prime']['end_ms'] == segments['turn']['start_ms'], 'contiguous native segments')
        require(displays[-1]['logical_ms'] == segments['turn']['end_ms'], 'final endpoint observed')
    final_pixels = codec.ppm(folder / 'final.ppm')
    require(final_pixels == codec.ppm(folder / displays[-1]['ppm']), 'final pixels equal completion display')
    (folder / 'final.png').write_bytes(codec.png_bytes(final_pixels))
    for index, display in enumerate(displays):
        display['duration_ms'] = displays[index + 1]['logical_ms'] - display['logical_ms'] if index + 1 < len(displays) else 0
        require(display['duration_ms'] >= 0, 'monotonic observed display timeline')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    require('data/styles/cartoon/BMP/JOHNWALK.BMP/017.png' in loaded and 'data/hd/BMP/JOHNWALK.BMP/017.png' not in loaded, 'approved017 dependency')
    selected16 = 'data/styles/cartoon/BMP/JOHNWALK.BMP/016.png' if candidate016 else 'data/hd/BMP/JOHNWALK.BMP/016.png'
    excluded16 = 'data/hd/BMP/JOHNWALK.BMP/016.png' if candidate016 else 'data/styles/cartoon/BMP/JOHNWALK.BMP/016.png'
    require(selected16 in loaded and excluded16 not in loaded, 'selected016 dependency')
    for frame in range(24, 30):
        require(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' in loaded, 'approved walking asset dependency')
    return {'status': 'PASS', 'clip': clip, 'phase': phase, 'segments': segments, 'displays': displays,
            'completed_waits': waits, 'display_count': len(displays), 'duration_ms': displays[-1]['logical_ms'],
            'loaded_art': loaded, 'log_sha256': sha((folder / 'capture.log').read_bytes()),
            'scope': 'Two explicit native calls: starting017 wait then requested same-spot turn. Actual observed timing; no interpolated poses or fabricated holds. Candidate016.' if candidate016 else 'Approved017 private baseline plus existing HD016; two actual native calls and observed timing.'}


def capture(exe, binding, clip, phase, expected):
    folder = BASE / clip / phase
    require(not folder.exists(), 'preserve prior phase:' + clip + ':' + phase)
    folder.mkdir(parents=True)
    shutil.copyfile(OUT / 'baseline-pack.zip', folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full', clip]
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    require(result.returncode == 0, 'native exit; retained log:' + clip + ':' + phase)
    report = parse(folder, phase, clip, expected)
    report.update({'command': command, 'exit_code': result.returncode, 'archive_sha256': sha((folder / 'scrantic_data.zip').read_bytes()), 'executable_sha256': sha(exe.read_bytes())})
    require(report['archive_sha256'] == binding['baseline_pack_sha256'] and report['executable_sha256'] == binding['executable_sha256'], 'unchanged execution inputs')
    save(folder / 'report.json', report)
    print(f'PASS {clip} {phase}: {report["display_count"]} displays, {report["duration_ms"]}ms', flush=True)
    return report


def main():
    print('WITNESS turn capture SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    exe, binding = build()
    expected = contract()
    reports = {}
    for clip in CLIPS:
        capture(exe, binding, clip, 'smoke', expected)
        full = capture(exe, binding, clip, 'full', expected)
        repeat = capture(exe, binding, clip, 'repeat', expected)
        for field in ('displays', 'segments', 'loaded_art', 'completed_waits'):
            require(full[field] == repeat[field], 'fresh-process repeat:' + clip + ':' + field)
        reports[clip] = {key: full[key] for key in ('display_count', 'duration_ms', 'segments')}
    require(protected() == binding['protected_sha256'], 'all production build inputs unchanged')
    save(BASE / 'summary.json', {'status': 'PASS', 'clips': reports, 'baseline_pack_sha256': binding['baseline_pack_sha256'],
         'executable_sha256': binding['executable_sha256'], 'protected_inputs_unchanged': len(binding['protected_sha256']),
         'verification': 'Each direction smoke then full then exact fresh-process repeat', 'scope': 'Baseline only; no candidate016 art, publication or production changes.'})
    print('PASS both native directions and all unchanged protected inputs', flush=True)


if __name__ == '__main__':
    main()
