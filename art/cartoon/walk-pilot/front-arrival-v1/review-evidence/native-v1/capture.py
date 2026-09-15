"""Build/capture the unchanged production front route under Linux/Xvfb, smoke first.

This is a baseline evidence recorder, not a golden corpus or an art acceptance.
It imports unchanged PPM/PNG encoding helpers from the preserved arrival review.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile

SOURCE = Path('/source')
OUT = Path('/out')
BASE = OUT / 'baseline-v1'
FORMAT = SOURCE / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec = importlib.util.spec_from_file_location('arrival_capture_format', FORMAT)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
EXPECTED_ZIP = '1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError('capture.py: ' + label)


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def protected():
    result = {str(path.relative_to(SOURCE)): sha(path.read_bytes())
              for folder in ('src', 'platform', 'third_party/miniz')
              for path in (SOURCE / folder).rglob('*') if path.is_file() and path.suffix in ('.c', '.h')}
    for name in ('CMakeLists.txt', 'assets/scrantic_data.zip', str(FORMAT.relative_to(SOURCE))):
        result[name] = sha((SOURCE / name).read_bytes())
    return result


def contract():
    text = (SOURCE / 'src/data/walk_data.h').read_text()
    body = text.split('static uint16 walkData[][4] = {', 1)[1].split('\n};', 1)[0]
    rows = [list(map(int, row)) for row in re.findall(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', body)]
    block = text.split('static int walkDataBookmarks[6][6] = {', 1)[1].split('\n};', 1)[0]
    bookmarks = [list(map(int, re.findall(r'-?\d+', row))) for row in re.findall(r'\{([^}]+)\}', block)]
    turn_block = text.split('static int walkDataBookmarksTurns[NUM_OF_NODES] = {', 1)[1].split('};', 1)[0]
    turns = list(map(int, re.findall(r'\d+', turn_block)))
    travel = []
    for row in rows[bookmarks[4][0]:]:
        if row[1] == 0:
            break
        travel.append(row)
    arrival = rows[turns[0] + 1 + 9]
    require(len(travel) == 23 and travel[-1] == [0, 301, 242, 27], 'known front travel endpoint')
    require(arrival == [1, 294, 243, 17], 'known mirrored HD017 arrival endpoint')
    return {'source': 'src/data/walk_data.h', 'bookmark': bookmarks[4][0],
            'travel_rows': travel, 'arrival_row': arrival, 'api': 'adsPlayWalk(4,1,0,1)',
            'arrival_note': 'HD frame017 remains mirrored at logical draw origin (293,243).'}


def build():
    require(not BASE.exists(), 'preserve existing baseline evidence')
    inputs = protected()
    require(inputs['assets/scrantic_data.zip'] == EXPECTED_ZIP, 'unchanged production28 ZIP')
    preparation = json.loads((OUT / 'preparation.json').read_bytes())
    require(sha((OUT / 'route_driver.c').read_bytes()) == preparation['adapted_driver_sha256'], 'prepared driver identity')
    BASE.mkdir()
    text = (SOURCE / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    exe = BASE / 'front_route_probe'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX',
               '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz',
               '/out/route_driver.c', *['/source/' + name for name in sources],
               '-Wl,--wrap=eventsWaitTick', '-Wl,--wrap=platformUpdateWindow',
               '-Wl,--wrap=grDrawSprite', '-Wl,--wrap=grDrawSpriteFlip', '-Wl,--wrap=walkAnimate',
               '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (BASE / 'build.stdout.txt').write_text(result.stdout)
    (BASE / 'build.stderr.txt').write_text(result.stderr)
    require(result.returncode == 0, 'native build failed: ' + result.stderr)
    require(exe.stat().st_mtime_ns >= started, 'fresh native executable timestamp')
    record = {'command': command, 'exit_code': result.returncode, 'source_commit': preparation['source_commit'],
              'executable_sha256': sha(exe.read_bytes()), 'driver_sha256': sha((OUT / 'route_driver.c').read_bytes()),
              'executable_mtime_ns': exe.stat().st_mtime_ns, 'build_started_ns': started,
              'image_id': preparation['image_id'], 'protected_sha256': inputs,
              'compiler': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0],
              'libc': subprocess.check_output(['ldd', '--version'], text=True).splitlines()[0],
              'capture_script_sha256': sha(Path(__file__).read_bytes()),
              'codec_sha256': sha(FORMAT.read_bytes())}
    save(BASE / 'build.json', record)
    save(BASE / 'route-contract.json', contract())
    print('PASS fresh native observer built with unchanged production sources', flush=True)
    return exe, record


def parse(folder, phase, expected, candidate017=False):
    text = (folder / 'capture.log').read_text()
    route = re.search(r'FRONT DRIVER: island_seed=11 path_seed=(\d+) route=E,A,UNDEF api=adsPlayWalk\(4,1,0,1\) style=cartoon', text)
    require(route and 'chosen path: EA' in text, phase + ': actual direct route witness')
    require('FRONT ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text,
            phase + ': deterministic island state')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text,
            phase + ': real final capture and art decode witnesses')
    rows, draws, delays, waits, displays = [], [], [], [], []
    last_row = last_draw = None
    for line in text.splitlines():
        row = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
        draw = re.search(r'FRONT DRAW: flip=(\d+) x=(\d+) y=(\d+) frame=(\d+)', line)
        delay = re.search(r'FRONT ANIMATE: delay_ticks=(\d+)', line)
        wait = re.search(r'FRONT WAIT: ticks=(\d+) logical_ms=(\d+)', line)
        display = re.search(r'FRONT DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
        if row:
            last_row = list(map(int, row.groups()))
            rows.append(last_row)
        if draw:
            last_draw = list(map(int, draw.groups()))
            draws.append(last_draw)
        if delay:
            delays.append(int(delay[1]))
        if wait:
            waits.append(list(map(int, wait.groups())))
        if display:
            index, when, name = display.groups()
            pixels = codec.ppm(folder / name)
            png = Path(name).with_suffix('.png').name
            encoded = codec.png_bytes(pixels)
            (folder / png).write_bytes(encoded)
            require(last_row is not None and last_draw == [last_row[0], last_row[1] - 1, last_row[2], last_row[3]],
                    phase + ': actual draw dispatch matches current walk row:' + index)
            displays.append({'index': int(index), 'logical_ms': int(when), 'stored_walk_row': last_row,
                             'actual_draw': last_draw, 'ppm': name, 'png': png,
                             'pixels_sha256': sha(pixels), 'png_sha256': sha(encoded)})
    require([item['index'] for item in displays] == list(range(1, len(displays) + 1)), phase + ': contiguous displays')
    require(len(waits) == len(displays) and [w[1] for w in waits] == [d['logical_ms'] for d in displays],
            phase + ': every completed native wait has one observed display')
    cumulative = 0
    for ticks, when in waits:
        cumulative += ticks * 20
        require(cumulative == when, phase + ': observed wait timestamp accumulation')
    final_pixels = codec.ppm(folder / 'final.ppm')
    (folder / 'final.png').write_bytes(codec.png_bytes(final_pixels))
    travel = expected['travel_rows']
    if phase == 'smoke':
        require('stopping after 1 frame(s)' in text and len(displays) == 1, 'smoke: native one-frame shutdown')
        require(rows[0] == travel[0] and displays[0]['logical_ms'] == 0, 'smoke: initial pose and time')
    else:
        require(rows == travel + [expected['arrival_row']], phase + ': exact source-table travel and arrival')
        require(draws == [[r[0], r[1] - 1, r[2], r[3]] for r in rows], phase + ': actual draw/flip sequence')
        require(delays == [6] * len(travel) + [80, 0], phase + ': native 120ms travel and 1600ms arrival delay returns')
        require('finite route returned; cleanup complete;' in text and 'WALKING: end walk' in text,
                phase + ': finite route completion and cleanup')
        duration = sum(delays) * 20
        require(displays[-1]['logical_ms'] == duration and displays[0]['logical_ms'] == 0,
                phase + ': full native duration endpoints')
        for index, row in enumerate(rows):
            appearances = [d for d in displays if d['stored_walk_row'] == row]
            require(appearances and appearances[0]['logical_ms'] == index * 120,
                    phase + ': first presentation time for pose:' + str(index + 1))
        require(final_pixels == codec.ppm(folder / displays[-1]['ppm']), phase + ': final native pixels equal last display')
    for index, display in enumerate(displays):
        display['duration_ms'] = displays[index + 1]['logical_ms'] - display['logical_ms'] if index + 1 < len(displays) else 0
        require(display['duration_ms'] >= 0, phase + ': monotonic presentation time')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    for frame in range(24, 30):
        require(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png' in loaded, phase + ': production front-family load')
    standing = 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png' if candidate017 else 'data/hd/BMP/JOHNWALK.BMP/017.png'
    excluded = 'data/hd/BMP/JOHNWALK.BMP/017.png' if candidate017 else 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png'
    require(standing in loaded and excluded not in loaded, phase + ': selected standing017 dependency')
    return {'status': 'PASS', 'phase': phase, 'island_seed': 11, 'path_seed': int(route[1]),
            'api': expected['api'], 'actual_path': [4, 0, 6], 'observed_rows': rows, 'actual_draws': draws,
            'native_delay_returns_ticks': delays, 'native_completed_waits': waits, 'displays': displays,
            'display_count': len(displays), 'duration_ms': displays[-1]['logical_ms'], 'loaded_art': loaded,
            'log_sha256': sha((folder / 'capture.log').read_bytes()), 'final_pixels_sha256': sha(final_pixels),
            'scope': ('Actual Linux current approved Cartoon walk/island and private Cartoon017 arrival.' if candidate017 else 'Current Cartoon walk + HD standing017.') + ' Native logical timing under maxspeed; no original-executable or wall-clock parity claim.'}


def capture(exe, binding, phase, expected):
    folder = BASE / phase
    require(not folder.exists(), 'preserve prior phase:' + phase)
    folder.mkdir()
    archive = SOURCE / 'assets/scrantic_data.zip'
    shutil.copyfile(archive, folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    command = [str(exe), 'cartoon', 'smoke' if phase == 'smoke' else 'full']
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run(command, cwd=folder, env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    require(result.returncode == 0, phase + ': native process exit; inspect retained capture.log')
    report = parse(folder, phase, expected)
    report.update({'command': command, 'exit_code': result.returncode,
                   'archive_sha256': sha((folder / 'scrantic_data.zip').read_bytes()),
                   'executable_sha256': sha(exe.read_bytes())})
    require(report['archive_sha256'] == EXPECTED_ZIP and report['executable_sha256'] == binding['executable_sha256'],
            phase + ': unchanged execution inputs')
    save(folder / 'report.json', report)
    print(f"PASS {phase}: {report['display_count']} observed displays, {report['duration_ms']}ms, direct path seed {report['path_seed']}", flush=True)
    return report


def main():
    print('WITNESS front capture.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    exe, binding = build()
    expected = contract()
    smoke = capture(exe, binding, 'smoke', expected)
    full = capture(exe, binding, 'full', expected)
    repeat = capture(exe, binding, 'repeat', expected)
    require(full['displays'] == repeat['displays'] and full['observed_rows'] == repeat['observed_rows']
            and full['actual_draws'] == repeat['actual_draws'] and full['loaded_art'] == repeat['loaded_art'],
            'fresh-process native replay matches every display and dependency')
    require(protected() == binding['protected_sha256'], 'all production build and helper inputs unchanged')
    with zipfile.ZipFile(SOURCE / 'assets/scrantic_data.zip') as archive:
        members = archive.namelist()
        require(len(members) == len(set(members)), 'unique production ZIP members')
        cartoon = [name for name in members if name.startswith('data/styles/cartoon/') and name.endswith('.png')]
        require(len(cartoon) == 28, 'unchanged 28-asset production pack')
    save(BASE / 'summary.json', {'status': 'PASS', 'phases': ['smoke', 'full', 'repeat'],
         'production_assets': len(cartoon), 'archive_sha256': EXPECTED_ZIP, 'archive_members': len(members),
         'executable_sha256': binding['executable_sha256'], 'protected_inputs_unchanged': len(binding['protected_sha256']),
         'path_seed': full['path_seed'], 'display_count': full['display_count'], 'duration_ms': full['duration_ms'],
         'first_walk': full['actual_draws'][0], 'last_walk': full['actual_draws'][-2], 'arrival': full['actual_draws'][-1],
         'repeat': 'fresh native process, exact per-display RGB and PNG hashes, timing, draw dispatch and art dependencies',
         'scope': 'Baseline only. No candidate ZIP, publishing, production source edit or original-executable claim.'})
    print('PASS full replay and unchanged protected sources/production28 archive', flush=True)


if __name__ == '__main__':
    main()
