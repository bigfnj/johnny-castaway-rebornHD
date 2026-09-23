import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
manifest_path = HERE / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
generated = {
    '037': 'exec-566300e6-013d-434d-bc6a-c58b0c7c08b9.png',
    '038': 'exec-01d4e192-3aaf-43fd-81ab-c2e7e3f1a6ae.png',
    '039': 'exec-222fca4e-bc12-46e9-a238-c558ca307480.png',
    '041': 'exec-27fac05f-a619-42bf-ae03-38c969bedd24.png',
    '043': 'exec-686823da-d21c-48e1-8c8f-05f8937d09bc.png',
}
center_samples = {'037': (1260, 265), '038': (1170, 225), '041': (1040, 350), '043': (1000, 340)}

def pin(path):
    p = Path(path)
    return {'path': p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

for entry in manifest['entries']:
    frame = entry['frame']
    target = HERE / frame / 'candidate-v1.png'
    if not target.exists():
        continue
    im = Image.open(target)
    assert im.mode == 'RGBA', (frame, im.mode)
    alpha = im.getchannel('A')
    assert alpha.getextrema() == (0, 255)
    checks = {'mode': im.mode, 'canvas': list(im.size), 'alpha_range': list(alpha.getextrema()), 'visual_inspection': 'Viewed built-in output against previous drawing and original sprite. Requested object correction is present.'}
    if frame in center_samples:
        xy = center_samples[frame]
        checks['hole_alpha_sample'] = {'xy': list(xy), 'alpha': alpha.getpixel(xy)}
        assert checks['hole_alpha_sample']['alpha'] == 0, (frame, checks['hole_alpha_sample'])
    if frame == '039':
        checks['visible_character_parts'] = 'One gripping hand only; hair, cyan hairband, head and body removed.'
    request = json.loads((HERE / frame / 'request.json').read_text(encoding='utf-8'))
    record = {
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'resource': 'SMGIFT.BMP', 'frame': frame, 'version': 1,
        'mode': 'built-in-imagegen', 'status': 'awaiting_review',
        'requested_change': entry['requested_change'], 'design': manifest['design'],
        'request': pin(HERE / frame / 'request.json'),
        'reference_images': [pin(p) for p in request['referenced_image_paths']],
        'original': pin(ROOT / entry['original']), 'previous': pin(ROOT / entry['previous']),
        'output': pin(target),
        'generated_source': 'C:/Users/Admin/.codex/generated_images/01a0ca94-b9f4-7ab0-ab7e-e930bc4af061/' + generated[frame],
        'verification': checks, 'appearance_approval': None,
        'production_integrated': False, 'native_motion_checked': False,
    }
    (HERE / frame / 'record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    entry['output'] = target.relative_to(ROOT).as_posix()
    entry['status'] = 'awaiting_review'
    entry['sha256'] = record['output']['sha256']
    print(frame, checks)
manifest['built_at_utc'] = datetime.now(timezone.utc).isoformat()
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
