"""Save an attributable error, or the known uncertain concurrent-group failure."""
import hashlib
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[2]
frame, error, attribution = sys.argv[1:]
folder = here / 'generation' / 'SBREAKUP.BMP'
request = folder / f'{frame}-v1-request.json'
dest = folder / f'{frame}-v1-failure.json'
record = {
    'schema_version': 1, 'resource': 'SBREAKUP.BMP', 'frame': frame, 'version': 1,
    'tool': 'image_gen.imagegen', 'mode': 'built-in', 'status': 'no_image_returned',
    'request': {'path': request.relative_to(root).as_posix(), 'sha256': hashlib.sha256(request.read_bytes()).hexdigest()},
    'error': error, 'attribution': attribution, 'output': None,
    'appearance_approval': None, 'production_integrated': False, 'native_motion_checked': False
}
assert not dest.exists(), dest
dest.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(dest)
