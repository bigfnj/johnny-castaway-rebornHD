"""Adapt the proven isolated packer to add016 above the approved017 baseline."""
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'build/front-arrival/native/prepare_candidate.py'


def main():
    target = OUT / 'prepare_candidate.py'
    if target.exists():
        raise ValueError('preserve candidate packer')
    text = PRIOR.read_text().replace('017', '016')
    for old, new, count in [
        ("source = ROOT / 'assets/scrantic_data.zip'", "source = OUT / 'baseline-pack.zip'", 1),
        ("baseline['archive_sha256']", "baseline['baseline_pack_sha256']", 3),
        ('production archive unchanged', 'approved017 baseline archive unchanged', 1),
        ('no production edit or human approval', 'no production edit or approval of016', 1),
    ]:
        if text.count(old) != count:
            raise ValueError('unique packer adaptation:' + old)
        text = text.replace(old, new)
    target.write_text(text, encoding='utf-8', newline='\n')
    (OUT / 'candidate-packer-adaptation.json').write_text(json.dumps({
        'source': PRIOR.relative_to(ROOT).as_posix(),
        'source_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'scope': 'Prepared only; candidate016 artwork not selected by this helper generation.'}, indent=2) + '\n')
    print('PASS candidate016 private packer prepared')


if __name__ == '__main__':
    main()
