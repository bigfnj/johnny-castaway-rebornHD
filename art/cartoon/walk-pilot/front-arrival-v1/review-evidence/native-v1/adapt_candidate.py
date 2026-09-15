"""Adapt the preserved native comparison for one new Cartoon017 member."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'art/cartoon/walk-pilot/front-refresh-v1/review-evidence/native-island-v1/helpers/capture_candidate.py'


def main():
    target = OUT / 'capture_candidate.py'
    if target.exists():
        raise ValueError('preserve existing candidate capture helper')
    text = PRIOR.read_text(encoding='utf-8')
    changes = [
        ('"""Capture a private028/029 candidate with the already-bound native observer."""', '"""Capture a future private017 candidate with the current-main native observer."""'),
        ('capture.parse(destination, phase, capture.contract())', 'capture.parse(destination, phase, capture.contract(), candidate017=True)'),
        ("'native_delay_returns_ticks', 'native_completed_waits', 'display_count', 'duration_ms', 'loaded_art'):", "'native_delay_returns_ticks', 'native_completed_waits', 'display_count', 'duration_ms'):"),
        ("    canvases = {item['frame']: item['canvas'] for item in preparation['replaced_members']}", "    dependencies = sorted('data/styles/cartoon/BMP/JOHNWALK.BMP/017.png' if name == 'data/hd/BMP/JOHNWALK.BMP/017.png' else name for name in expected['loaded_art'])\n    capture.require(report['loaded_art'] == dependencies, phase + ': only standing017 dependency changed')\n    canvases = {item['frame']: item['canvas'] for item in preparation['added_members']}\n    capture.require(set(canvases) == {17}, 'exactly one added017 mask')"),
        ("different only inside placed028/029 canvas", "different only inside placed017 canvas"),
        ("Private028/029 native candidate, same observer and route as production28. All other frames, including mirrored HD017 arrival, remain unchanged.", "Private017 native candidate, same observer and route as current production28. Every travel display must remain identical; only the mirrored017 canvas may change."),
        ("differ only inside placed028/029 canvases", "differ only inside placed017 canvas"),
        ("HD017 mirrored at (293,243), every arrival display identical to baseline", "Cartoon017 mirrored at (293,243), only arrival canvas differs; all travel displays identical"),
    ]
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('unique candidate adaptation anchor:' + old)
        text = text.replace(old, new)
    target.write_text(text, encoding='utf-8', newline='\n')
    report = {'source': PRIOR.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
              'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'scope': 'Prepared for a future hash-bound017 PNG. Native candidate execution has not occurred.'}
    (OUT / 'candidate-adaptation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS future017 capture helper prepared; no candidate art selected or packed')


if __name__ == '__main__':
    main()
