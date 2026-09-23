import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('frame')
parser.add_argument('source')
parser.add_argument('--notes', required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[3]
out = here / f'{args.frame}-candidate-v1.png'
assert not out.exists(), out
shutil.copy2(args.source, out)
im = Image.open(out)
request = here / f'{args.frame}-request.json'
req = json.loads(request.read_text(encoding='utf-8'))
record = {
    'frame': req['frame'], 'created_at_utc': datetime.now(timezone.utc).isoformat(),
    'tool': 'built-in image_gen', 'source_output': args.source,
    'request': {'path': request.relative_to(root).as_posix(), 'sha256': hashlib.sha256(request.read_bytes()).hexdigest()},
    'output': {'path': out.relative_to(root).as_posix(), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'canvas': list(im.size), 'mode': im.mode, 'alpha_range': im.getchannel('A').getextrema() if 'A' in im.getbands() else None},
    'visual_review': args.notes, 'status': 'awaiting_review', 'appearance_approval': None,
    'production_integrated': False, 'native_motion_checked': False,
}
record_path = here / f'{args.frame}-record.json'
record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
manifest_path = here / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
row = next(e for e in manifest['entries'] if e['frame'] == args.frame)
row.update({'output': out.relative_to(root).as_posix(), 'status': 'awaiting_review', 'record': record_path.relative_to(root).as_posix(), 'visual_review': args.notes})
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, indent=2))
