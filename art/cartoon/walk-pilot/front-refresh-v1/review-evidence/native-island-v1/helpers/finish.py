"""Record baseline file identities and camera bounds; never modify capture inputs."""
import hashlib
import json
from pathlib import Path
import struct
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = OUT / 'baseline-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    summary = json.loads((BASE / 'summary.json').read_bytes())
    report = json.loads((BASE / 'full/report.json').read_bytes())
    rectangles = []
    with zipfile.ZipFile(ROOT / 'assets/scrantic_data.zip') as archive:
        for flip, x, y, frame in report['actual_draws']:
            name = f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'
            if name not in archive.namelist():
                name = f'data/hd/BMP/JOHNWALK.BMP/{frame:03}.png'
            raw = archive.read(name)
            width, height = struct.unpack('>II', raw[16:24])
            rectangles.append([x * 2, y * 2, x * 2 + width, y * 2 + height])
    union = [min(row[0] for row in rectangles), min(row[1] for row in rectangles),
             max(row[2] for row in rectangles), max(row[3] for row in rectangles)]
    paths = ['prepare.py', 'capture.py', 'route_driver.c', 'preparation.json',
             'baseline-v1/build.json', 'baseline-v1/route-contract.json', 'baseline-v1/summary.json']
    paths += [f'baseline-v1/{phase}/report.json' for phase in ('smoke', 'full', 'repeat')]
    evidence = {'status': 'PASS', 'summary': summary, 'canvas_union_hd_xyxy': union,
                'files_sha256': {name: sha((OUT / name).read_bytes()) for name in paths},
                'scope': 'Scratch baseline only. Captures are native composited pixels; bounds are full canvases, not silhouette fits.'}
    destination = OUT / 'evidence.json'
    if destination.exists():
        raise ValueError('finish.py: preserve existing evidence')
    destination.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'full_canvas_union_hd': union, 'files_bound': len(paths)}))


if __name__ == '__main__':
    main()
