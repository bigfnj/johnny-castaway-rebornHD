"""Bind the current native baseline and fixed camera, preserving all capture inputs."""
import hashlib
import json
from pathlib import Path
import struct
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    summary = json.loads((OUT / 'baseline-v1/summary.json').read_bytes())
    report = json.loads((OUT / 'baseline-v1/full/report.json').read_bytes())
    source = ROOT / 'assets/scrantic_data.zip'
    if sha(source.read_bytes()) != summary['archive_sha256']:
        raise ValueError('finish.py: current production archive identity')
    rectangles = []
    with zipfile.ZipFile(source) as archive:
        identities = {}
        for flip, x, y, frame in report['actual_draws']:
            name = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
            if name not in archive.namelist():
                name = f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png'
            raw = archive.read(name)
            identities[name] = sha(raw)
            width, height = struct.unpack('>II', raw[16:24])
            rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
    union = [min(row[0] for row in rectangles), min(row[1] for row in rectangles), max(row[2] for row in rectangles), max(row[3] for row in rectangles)]
    camera = [560, 400, 400, 280]
    if not (camera[0] <= union[0] < union[2] <= camera[0] + camera[2] and camera[1] <= union[1] < union[3] <= camera[1] + camera[3]):
        raise ValueError('finish.py: fixed camera clips placed canvas')
    names = ['prepare.py', 'capture.py', 'route_driver.c', 'preparation.json', 'finish.py',
             'prepare_candidate.py', 'adapt_candidate.py', 'capture_candidate.py', 'candidate-adaptation.json',
             'check_helpers.py', 'helper-checks-v1/report.json', 'README.md',
             'baseline-v1/build.json', 'baseline-v1/route-contract.json', 'baseline-v1/summary.json']
    names += [f'baseline-v1/{phase}/report.json' for phase in ('smoke', 'full', 'repeat')]
    result = {'status': 'PASS', 'label': 'Current Cartoon walk + HD standing017', 'summary': summary,
              'canvas_union_hd_xyxy': union, 'fixed_closeup_hd_xywh': camera, 'full_scene_hd_wh': [1280, 960],
              'frame_png_sha256': identities, 'files_sha256': {name: sha((OUT / name).read_bytes()) for name in names},
              'scope': 'Native current-main baseline only. Exact logical times and actual origins are in phase reports. Fixed camera contains full placed canvases. No candidate art, publication, original-executable parity or human approval.'}
    destination = OUT / 'evidence.json'
    if destination.exists():
        raise ValueError('finish.py: preserve existing evidence')
    destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'canvas_union_hd_xyxy': union, 'fixed_camera_hd_xywh': camera, 'files_bound': len(names)}))


if __name__ == '__main__':
    main()
