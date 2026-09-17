"""Package unchanged native capture crops for the three-way wave review."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CROP = (520, 470, 1200, 750)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def prepare(sources):
    panels = {}
    schedule = None
    for key, folder in sources.items():
        folder = folder.resolve()
        raw = (folder / 'report.json').read_bytes()
        report = json.loads(raw)
        if report['status'] != 'PASS':
            raise ValueError(key + ': native capture did not pass')
        rows = report['displays']
        current = [(r['time_ms'], r['phases'], r['johnny']) for r in rows]
        if schedule is None:
            schedule = current
        elif schedule != current:
            raise ValueError(key + ': native timing or poses differ')
        if {f for r in rows for f in r['phases'] if f >= 0} != set(range(3, 12)):
            raise ValueError(key + ': wave phases missing')
        repeated = folder.parent / 'repeat' / 'report.json'
        repeat_report = json.loads(repeated.read_bytes())
        if repeat_report['status'] != 'PASS':
            raise ValueError(key + ': fresh native repeat did not pass')
        if rows != repeat_report['displays']:
            raise ValueError(key + ': fresh native repeat differs')
        target = HERE / key
        target.mkdir(exist_ok=True)
        hashes = {}
        for row in rows:
            name = row['file']
            if name in hashes:
                continue
            image_raw = (folder / name).read_bytes()
            if sha(image_raw) != row['png_sha256']:
                raise ValueError(key + '/' + name + ': source PNG hash differs')
            with Image.open(folder / name) as source:
                if source.size != (1280, 960):
                    raise ValueError(key + '/' + name + ': source dimensions differ')
                cropped = source.crop(CROP)
                cropped.save(target / name)
            hashes[name] = {'source_sha256': row['png_sha256'],
                            'crop_sha256': sha((target / name).read_bytes())}
        (target / 'native-report.json').write_bytes(raw)
        panels[key] = {
            'native_report': (folder / 'report.json').relative_to(ROOT).as_posix(),
            'native_report_sha256': sha(raw),
            'fresh_repeat_report_sha256': sha(repeated.read_bytes()),
            'archive_sha256': report['archive_sha256'],
            'executable_sha256': report['executable_sha256'],
            'duration_ms': report['duration_ms'], 'images': hashes,
            'displays': [{k: row[k] for k in ('ordinal', 'time_ms', 'ticks', 'phases', 'johnny', 'file')}
                         for row in rows],
        }
    original = panels['original']['displays']
    initial = original[0]['phases']
    at_loop = [row for row in original if row['time_ms'] == 1440]
    if not at_loop or at_loop[-1]['phases'] != initial:
        raise ValueError('original: 1440 ms does not close the observed wave cycle')
    manifest = {
        'schema_version': 1, 'accepted': False, 'loop_ms': 1440,
        'stored_crop': [CROP[0], CROP[1], CROP[2] - CROP[0], CROP[3] - CROP[1]],
        'method': 'Unchanged pixel crops from native port captures. No invented frames or interpolation.',
        'scope': 'Center wave study with St Patrick clovers. Both Cartoon side families and approved ground are identical.',
        'original_limit': 'Authentic source sprites rendered by port with diagnostic colors; not original executable footage.',
        'builder_sha256': sha(Path(__file__).read_bytes()), 'panels': panels,
    }
    save(HERE / 'manifest.json', manifest)
    print('PASS three native clips; exact shared timing; all nine wave phases; fresh repeat matches')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'offshore', 'wash'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    prepare(vars(args))
