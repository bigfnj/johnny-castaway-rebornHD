"""Use the saved Linux executable, smoke then full route, with private CWD ZIPs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from run_baseline import ppm, png_bytes

BASE = Path('/out')
SOURCE = Path('/source')
FRAMES = [11, 19, 20, 21, 22, 23]
CANVASES = {11: (64, 156), 19: (64, 152), 20: (48, 150), 21: (64, 150), 22: (64, 148), 23: (64, 156)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def outside_equal(left, right, box):
    x0, y0, x1, y1 = box
    pitch = 1280 * 3
    for y in range(960):
        start = y * pitch
        if y0 <= y < y1:
            if left[start:start + x0 * 3] != right[start:start + x0 * 3] or left[start + x1 * 3:start + pitch] != right[start + x1 * 3:start + pitch]:
                return False
        elif left[start:start + pitch] != right[start:start + pitch]:
            return False
    return True


def capture(exe, archive, folder, phase, baseline, control):
    folder.mkdir()
    shutil.copyfile(archive, folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run([str(exe), 'cartoon', phase], cwd=folder,
                                env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    text = (folder / 'capture.log').read_text()
    require(result.returncode == 0, f'{phase}: native-exit')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text,
            f'{phase}: real-capture-witness')
    require('path_seed=2 route=B,A,UNDEF api=adsPlayWalk(1,3,0,3)' in text
            and 'REAR ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text,
            f'{phase}: actual-route-and-island')
    expected = json.loads((baseline / phase / 'report.json').read_bytes())
    observed = [list(map(int, r)) for r in re.findall(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', text)]
    require(observed == expected['observed_rows'], f'{phase}: all-walk-rows')
    displays, last_row = [], None
    for line in text.splitlines():
        row = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
        if row:
            last_row = list(map(int, row.groups()))
        found = re.search(r'REAR DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
        if not found:
            continue
        index, when, name = found.groups()
        require(len(displays) < len(expected['displays']), f'{phase}: extra-display')
        reference = expected['displays'][len(displays)]
        require(int(index) == reference['index'] and int(when) == reference['logical_ms']
                and last_row == reference['stored_walk_row'], f'{phase}: exact-display:{index}')
        pixels = ppm(folder / name)
        original = ppm(baseline / phase / reference['ppm'])
        require(sha(original) == reference['pixels_sha256'], f'{phase}: baseline-pixels:{index}')
        frame = last_row[3]
        if control or frame == 18:
            require(pixels == original, f'{phase}: unchanged-full-frame:{index}')
            rectangle = None
        else:
            width, height = CANVASES[frame]
            x, y = (last_row[1] - 1) * 2, last_row[2] * 2
            rectangle = [x, y, x + width, y + height]
            require(outside_equal(original, pixels, rectangle), f'{phase}: unchanged-outside-Johnny:{index}')
            require(pixels != original, f'{phase}: visible-candidate:{index}')
        png = Path(name).with_suffix('.png').name
        png_raw = png_bytes(pixels)
        (folder / png).write_bytes(png_raw)
        displays.append({**reference, 'pixels_sha256': sha(pixels), 'png_sha256': sha(png_raw),
                         'baseline_pixels_sha256': sha(original), 'changed_region_allowed': rectangle,
                         'comparison': 'full-frame-identical' if rectangle is None else 'different-only-inside-Johnny-canvas'})
    require(len(displays) == len(expected['displays']), f'{phase}: display-count')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    wanted = set(expected['loaded_art'])
    if not control:
        for frame in FRAMES:
            suffix = f'BMP/JOHNWALK.BMP/{frame:03}.png'
            wanted.remove('data/hd/' + suffix)
            wanted.add('data/styles/cartoon/' + suffix)
    require(set(loaded) == wanted, f'{phase}: exact-loaded-art')
    final = ppm(folder / 'final.ppm')
    if phase == 'smoke':
        require('stopping after 1 frame(s)' in text, 'smoke: one-frame-stop')
    else:
        require(final == ppm(folder / displays[-1]['ppm']), f'{phase}: final-capture-equality')
        require('finite route returned; cleanup complete;' in text and 'WALKING: end walk' in text,
                'full: real-route-completion')
    record = {'status': 'PASS', 'phase': phase, 'control': control, 'exit_code': result.returncode,
              'executable_sha256': sha(exe.read_bytes()), 'archive_sha256': sha(archive.read_bytes()),
              'island_seed': 11, 'path_seed': 2, 'observed_rows': observed, 'displays': displays,
              'loaded_art': loaded, 'log_sha256': sha((folder / 'capture.log').read_bytes()),
              'scope': 'Actual saved Linux API-driver captures; port logical timing; no Windows or original EXE rendering claim.'}
    (folder / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'PASS {phase}: {len(displays)} real displays; placement/timing/dependencies/background verified', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, help='Prepared private candidate directory inside /out')
    parser.add_argument('--control-output', type=Path, help='Optional unchanged-archive proof directory')
    args = parser.parse_args()
    require(bool(args.candidate) != bool(args.control_output), 'choose-candidate-or-control')
    print('WITNESS run_candidate.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    baseline = BASE / 'baseline-v2'
    build = json.loads((baseline / 'build.json').read_bytes())
    exe = baseline / 'rear_route_probe'
    require(sha(exe.read_bytes()) == build['executable_sha256'], 'saved-executable-identity')
    protected = build['protected_sha256']
    require(all(sha((SOURCE / n).read_bytes()) == h for n, h in protected.items()), 'baseline-production-inputs')
    output = args.candidate or args.control_output
    if args.candidate:
        archive = output / 'scrantic_data.zip'
        record = json.loads((output / 'preparation.json').read_bytes())
        require(sha(archive.read_bytes()) == record['archive_sha256'], 'private-archive-identity')
        require(record['baseline_executable_sha256'] == build['executable_sha256'], 'prepared-executable-identity')
    else:
        archive = SOURCE / 'assets/scrantic_data.zip'
        output.mkdir()
    require(not (output / 'smoke').exists() and not (output / 'full').exists(), 'preserve-prior-captures')
    capture(exe, archive, output / 'smoke', 'smoke', baseline, bool(args.control_output))
    capture(exe, archive, output / 'full', 'full', baseline, bool(args.control_output))
    require(all(sha((SOURCE / n).read_bytes()) == h for n, h in protected.items())
            and sha(exe.read_bytes()) == build['executable_sha256'], 'all-protected-inputs-preserved')
    (output / 'summary.json').write_text(json.dumps({'status': 'PASS', 'phases': ['smoke', 'full'],
            'executable_sha256': build['executable_sha256'], 'protected_inputs_unchanged': len(protected),
            'source_sha256': sha(Path(__file__).read_bytes()), 'control': bool(args.control_output)}, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        raise SystemExit(1)
