"""Retain pre-publication evidence while correcting the inherited view label."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
REVIEW = OUT / 'review-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    history = OUT / 'pre-label-review'
    assert not history.exists(), 'preserve label history'
    raw = (REVIEW / 'review.html').read_bytes()
    assert raw.count(b'Walk close-up') == 1, 'unique inherited view label'
    history.mkdir()
    names = ['review.html', 'review-record.json', 'browser-validation.json']
    names += [path.name for path in REVIEW.glob('*-1280.png')]
    for name in names:
        (history / name).write_bytes((REVIEW / name).read_bytes())
    changed = raw.replace(b'Walk close-up', b'Pose close-up')
    (REVIEW / 'review.html').write_bytes(changed)
    record = json.loads((REVIEW / 'review-record.json').read_bytes())
    record['html_sha256'] = sha(changed)
    record['builder_sha256'] = sha((OUT / 'build_review.py').read_bytes())
    (REVIEW / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    (REVIEW / 'browser-validation.json').unlink()
    report = {'old_html_sha256': sha(raw), 'new_html_sha256': sha(changed), 'change': 'Walk close-up -> Pose close-up',
              'preserved_pre_label_files_sha256': {name: sha((history / name).read_bytes()) for name in names}}
    (OUT / 'view-label-correction.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS label corrected; pre-label evidence retained; browser recheck required')


if __name__ == '__main__':
    main()
