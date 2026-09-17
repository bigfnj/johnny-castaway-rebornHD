"""Prepare a matched shoreline close-up from actual native scene captures."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
CASES = ('none', 'clover', 'pumpkin', 'tree')
CROP = (536, 460, 1192, 700)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    args = parser.parse_args()
    output = HERE / 'review-images'
    output.mkdir(exist_ok=False)
    files = {}
    for case in CASES:
        for captures, label in ((args.before, 'before'), (args.after, 'after')):
            source = captures / 'candidate' / case / 'smoke' / 'final.png'
            target = output / f'{case}-{label}.png'
            with Image.open(source) as image:
                image.convert('RGB').crop(CROP).save(target)
            files[target.name] = {
                'source': source.as_posix(),
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            }
    record = {'scope': 'Unapproved static contact refinement; full-size V5 props unchanged.',
              'crop_xyxy': CROP, 'files': files}
    (output / 'source.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
