"""Prepare the authorized next 72-drawing appearance batch."""
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'mermaid-gifts-and-glimpses-batch-v1'
selection = {
    'SLEVEJM1.BMP': list(range(11)),
    'SLEVEJM2.BMP': list(range(6)) + list(range(9, 21)),
    'SLEVEJM3.BMP': list(range(8)),
    'SMDATE1.BMP': list(range(17)),
    'SMDATE10.BMP': [4, 5, 6],
    'SMDATE11.BMP': [4],
    'SMDATE6.BMP': list(range(7)) + list(range(18, 22)) + [27, 28, 31],
}
assert sum(map(len, selection.values())) == 72
(HERE / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
for name in ['prepare_references.py', 'record_output.py', 'build_review.py', 'review-template.html', 'review.js']:
    destination = HERE / name
    assert not destination.exists(), destination
    shutil.copyfile(PREVIOUS / name, destination)
path = HERE / 'prepare_references.py'
text = path.read_text(encoding='utf-8')
text = text.replace('exact mermaid gift and glimpse drawings', 'exact mermaid departure and date drawings')
text = text.replace('No exclusions. All 70 selected original drawings are distinct; source alpha-bbox and mirrored-bbox comparison found no matches within this batch or against earlier generated resource/frame pairs.', 'Selected 72 distinct originals after cropped RGBA and mirrored comparison against 613 previously generated resource/frame pairs. Excluded SLEVEJM2 006-008 placeholder markers and SMDATE11 000-003,005-008 tails already represented by SMGFTWAV.')
path.write_text(text, encoding='utf-8')
path = HERE / 'build_review.py'
text = path.read_text(encoding='utf-8').replace('70-frame', '72-frame')
start = text.index('GROUPS = [')
end = text.index('\n\n\ndef pin', start)
text = text[:start] + 'GROUPS = [(r.lower().replace(".bmp", ""), r.replace(".BMP", ""), r, frames) for r, frames in json.loads((HERE / "selection.json").read_text(encoding="utf-8")).items()]' + text[end:]
path.write_text(text, encoding='utf-8')
path = HERE / 'review-template.html'
text = path.read_text(encoding='utf-8').replace('70 mermaid gift and glimpse drawings', '72 mermaid departure and date drawings')
path.write_text(text, encoding='utf-8')
(HERE / 'README.md').write_text('# Mermaid departure and date drawings\n\nThe user authorized the next several dozen drawings after approving the previous corrections. This batch contains 72 distinct source drawings. Each new drawing uses one built-in image generation request with its exact original as the pose reference and established cartoon artwork as the style reference.\n\nOpen review.html through the local review server. Generation requests and byte-exact returned PNGs are saved per frame under generation/. Appearance approval is pending.\n', encoding='utf-8')
print('Created 72-frame selection and reusable review helpers.')
