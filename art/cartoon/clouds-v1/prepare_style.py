"""Extract exact approved style references; no image transformation."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'style-reference'
OUT.mkdir(parents=True, exist_ok=True)
specs = [
    ('art/cartoon/island-pilot-v1/palm-sand-cloud/source-images.zip', 'cloud-generated-v1.png', 'approved-cloud-raw.png', 'b50454479c9f08d2eebf381d0d110aab4f3fde6c2d046161da4c22a77b1e21ca'),
    ('assets/scrantic_data.zip', 'data/styles/cartoon/BMP/BACKGRND.BMP/015.png', 'approved-cloud015-runtime.png', 'd7f6f6608cb18ac169b6e4378cb5c12c30a9139d7925c36e8a02f1c8eea41649'),
]
records = []
for path, member, name, expected in specs:
    with zipfile.ZipFile(ROOT/path) as z:
        data = z.read(member)
    actual = hashlib.sha256(data).hexdigest()
    assert actual == expected, name
    (OUT/name).write_bytes(data)
    records.append({'archive':path,'archive_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                    'member':member,'output':name,'sha256':actual})
(OUT/'source.json').write_bytes((json.dumps({'scope':'Exact approved cloud style references. No artistic or pixel edits.', 'files':records},indent=2)+'\n').encode())
print(json.dumps(records))
