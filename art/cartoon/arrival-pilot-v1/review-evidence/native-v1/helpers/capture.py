"""Capture the current arrival baseline, or a private frame-018 candidate, smoke first."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from capture_format import ppm, png_bytes

SOURCE = Path('/source')
OUT = Path('/out')
PRIOR = Path('/prior')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def outside_equal(a, b, box):
    x0, y0, x1, y1 = box
    for y in range(960):
        row = y * 3840
        if y0 <= y < y1:
            if a[row:row + x0 * 3] != b[row:row + x0 * 3] or a[row + x1 * 3:row + 3840] != b[row + x1 * 3:row + 3840]:
                return False
        elif a[row:row + 3840] != b[row:row + 3840]:
            return False
    return True


def capture(exe, archive, folder, phase, candidate, binding):
    folder.mkdir()
    shutil.copyfile(archive, folder / 'scrantic_data.zip')
    (folder / 'profile').mkdir()
    with (folder / 'capture.log').open('wb') as log:
        result = subprocess.run([str(exe), 'cartoon', phase], cwd=folder,
                                env=dict(os.environ, HOME=str(folder / 'profile')),
                                stdout=log, stderr=subprocess.STDOUT, timeout=90)
    text = (folder / 'capture.log').read_text()
    require(result.returncode == 0, phase + ': native-exit')
    require('Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text, phase + ': capture-witness')
    require('path_seed=2 route=B,A,UNDEF api=adsPlayWalk(1,3,0,3)' in text
            and 'REAR ISLAND: highTide=1 offset=0,0 raft=0 night=0 holiday=0' in text, phase + ': route-island-witness')
    reference_folder = OUT / 'baseline' / phase if candidate else PRIOR / 'candidate-v1' / phase
    reference_file = reference_folder / 'report.json' if candidate else OUT / f'prior-{phase}-report.json'
    if not candidate:
        require(sha(reference_file.read_bytes()) == binding['prior_capture_reports'][phase], phase + ': prior-report-identity')
    expected = json.loads(reference_file.read_bytes())
    observed = [list(map(int, r)) for r in re.findall(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', text)]
    require(observed == expected['observed_rows'], phase + ': native-walk-rows')
    displays, last = [], None
    for line in text.splitlines():
        row = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
        if row:
            last = list(map(int, row.groups()))
        item = re.search(r'REAR DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
        if not item:
            continue
        index, when, name = item.groups()
        require(len(displays) < len(expected['displays']), phase + ': extra-display')
        before = expected['displays'][len(displays)]
        require(int(index) == before['index'] and int(when) == before['logical_ms']
                and last == before['stored_walk_row'], f'{phase}: exact-timeline:{index}')
        pixels, reference = ppm(folder / name), ppm(reference_folder / before['ppm'])
        require(sha(reference) == before['pixels_sha256'], f'{phase}: reference-pixels:{index}')
        box = None
        if candidate and last[3] == 18:
            width, height = candidate['new_paths'][0]['canvas']
            x, y = (last[1] - 1) * 2, last[2] * 2
            box = [x, y, x + width, y + height]
            require(outside_equal(reference, pixels, box), f'{phase}: unchanged-outside-arrival:{index}')
            require(pixels != reference, f'{phase}: visible-arrival-candidate:{index}')
        else:
            require(pixels == reference, f'{phase}: unchanged-full-frame:{index}')
        png = Path(name).with_suffix('.png').name
        png_raw = png_bytes(pixels)
        (folder / png).write_bytes(png_raw)
        displays.append({**before, 'pixels_sha256': sha(pixels), 'png_sha256': sha(png_raw),
                         'baseline_pixels_sha256': sha(reference), 'changed_region_allowed': box,
                         'comparison': 'different-only-inside-arrival-canvas' if box else 'full-frame-identical'})
    require(len(displays) == len(expected['displays']), phase + ': display-count')
    loaded = sorted(set(re.findall(r'Art asset: (\S+)', text)))
    wanted = set(expected['loaded_art'])
    if candidate:
        wanted.remove('data/hd/BMP/JOHNWALK.BMP/018.png')
        wanted.add('data/styles/cartoon/BMP/JOHNWALK.BMP/018.png')
    require(set(loaded) == wanted, phase + ': exact-art-dependencies')
    final = ppm(folder / 'final.ppm')
    (folder / 'final.png').write_bytes(png_bytes(final))
    if phase == 'smoke':
        require('stopping after 1 frame(s)' in text and len(displays) == 1, 'smoke: real-one-frame-stop')
    else:
        require(len(displays) == 47 and displays[-1]['logical_ms'] == 4360
                and observed[-1] == [0, 299, 240, 18], 'full: route-arrival-contract')
        require(final == ppm(folder / displays[-1]['ppm']), 'full: final-capture-equality')
        require('finite route returned; cleanup complete;' in text and 'WALKING: end walk' in text, 'full: real-completion')
    report = {'status': 'PASS', 'phase': phase, 'control': not bool(candidate), 'exit_code': result.returncode,
              'executable_sha256': sha(exe.read_bytes()), 'archive_sha256': sha(archive.read_bytes()),
              'island_seed': 11, 'path_seed': 2, 'observed_rows': observed, 'displays': displays,
              'loaded_art': loaded, 'log_sha256': sha((folder / 'capture.log').read_bytes()),
              'scope': 'Actual saved Linux API-driver captures. Current 27-asset Cartoon walk/island baseline; only arrival 018 may differ in the private candidate. Port logical timing, not original executable or physical wall-clock parity.'}
    (folder / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS {phase}: {len(displays)} real displays; exact route/timing/art dependencies and pixel bounds', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    args = parser.parse_args()
    print('WITNESS arrival capture.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    binding = json.loads((OUT / 'source-reuse.json').read_bytes())
    exe = OUT / 'baseline/rear_route_probe'
    require(sha(exe.read_bytes()) == binding['executable_sha256'], 'saved-executable-identity')
    for name, digest in binding['protected_sha256'].items():
        require(sha((SOURCE / name).read_bytes()) == digest, 'protected-input:' + name)
    candidate = None
    folder = args.candidate or OUT / 'baseline'
    archive = SOURCE / 'assets/scrantic_data.zip'
    if args.candidate:
        candidate = json.loads((folder / 'preparation.json').read_bytes())
        archive = folder / 'scrantic_data.zip'
        require(sha(archive.read_bytes()) == candidate['archive_sha256'], 'private-candidate-archive')
        require(candidate['base_archive_sha256'] == binding['current_archive_sha256'], 'candidate-base-identity')
        require(candidate['baseline_executable_sha256'] == binding['executable_sha256'], 'candidate-executable-identity')
    require(not (folder / 'smoke').exists() and not (folder / 'full').exists(), 'preserve-prior-captures')
    for phase in ('smoke', 'full'):
        capture(exe, archive, folder / phase, phase, candidate, binding)
    for name, digest in binding['protected_sha256'].items():
        require(sha((SOURCE / name).read_bytes()) == digest, 'preserved-input:' + name)
    require(sha(exe.read_bytes()) == binding['executable_sha256'], 'preserved-executable')
    (folder / 'summary.json').write_text(json.dumps({'status': 'PASS', 'phases': ['smoke', 'full'],
        'executable_sha256': binding['executable_sha256'], 'archive_sha256': sha(archive.read_bytes()),
        'source_sha256': sha(Path(__file__).read_bytes()), 'protected_inputs_unchanged': len(binding['protected_sha256']),
        'control': not bool(candidate)}, indent=2) + '\n')


if __name__ == '__main__':
    main()
