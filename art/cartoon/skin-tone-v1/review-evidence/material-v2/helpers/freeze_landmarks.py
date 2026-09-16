"""Freeze independently reviewed input landmarks before examining corrections."""
from pathlib import Path
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'art/cartoon/skin-tone-v1'
OUT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
index_path = HERE / 'input-index.json'
index = json.loads(index_path.read_bytes())
rows = json.loads((OUT / 'proposals.json').read_bytes())
assert [r['frame'] for r in rows] == [r['frame'] for r in index['frames']]
regions = 0
for row in rows:
    path = HERE / row['input']
    assert sha(path.read_bytes()) == row['input_sha256']
    with Image.open(path) as opened:
        im = opened.convert('RGBA')
    assert list(im.size) == row['canvas']
    for point in row['landmarks']:
        x, y = point['xy']
        assert list(im.getpixel((x, y))) == point['rgba']
        if point['role'] in ('hat-white', 'hair-or-beard', 'shorts-white'):
            patch = im.crop((x-1, y-1, x+2, y+2))
            assert min(patch.getchannel('A').getdata()) >= 240
            point['region_xywh'] = [x-1, y-1, 3, 3]
            point['region_rgba_sha256'] = sha(patch.tobytes())
            regions += 1
document = dict(
    schema_version=1,
    scope='Independent protected material landmarks; expected RGBA comes only from frozen source sprites.',
    source_index='input-index.json',
    source_index_sha256=sha(index_path.read_bytes()),
    coordinate_convention='Zero-based x,y in each unmirrored runtime PNG full canvas. Region hashes cover row-major decoded RGBA bytes.',
    selection_method='Appearance-based coordinate proposals followed by visual review of all 28 original sprites. No correction implementation, correction masks, or corrected exports were inspected before freezing this file.',
    proposed_script_sha256=sha((OUT/'select_landmarks.py').read_bytes()),
    limitations='Sparse protected-material samples, not an exhaustive segmentation. Hidden rear-view eyes are explicitly excluded. Regions cover only interior hat white, hair/beard and shorts white.',
    frame_count=len(rows),
    landmark_count=sum(len(r['landmarks']) for r in rows),
    region_count=regions,
    frames=rows,
)
destination = HERE / 'protected-landmarks-v1.json'
assert not destination.exists(), 'Do not overwrite the independently frozen manifest.'
destination.write_text(json.dumps(document, indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(path=destination.relative_to(ROOT).as_posix(), sha256=sha(destination.read_bytes()), frames=len(rows), landmarks=document['landmark_count'], regions=regions)))
