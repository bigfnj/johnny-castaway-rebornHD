"""Copy matched native stills for a provisional shoreline-size review."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
CASES = ('none', 'clover', 'pumpkin', 'tree')
CROP = (536, 236, 1192, 700)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures', type=Path, required=True)
    args = parser.parse_args()
    output = HERE / 'review-images'
    output.mkdir(exist_ok=False)
    files = {}
    for case in CASES:
        for package, label in (('baseline', 'before'), ('candidate', 'after')):
            source = args.captures / package / case / 'smoke' / 'final.png'
            image = Image.open(source).convert('RGB')
            target = output / f'{case}-{label}.png'
            image.crop(CROP).save(target)
            files[target.name] = {
                'source': source.as_posix(),
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            }
    record = {'scope': 'Unapproved static shoreline draft; same full-size V5 props on both sides.',
              'crop_xyxy': CROP, 'files': files}
    (output / 'source.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
