import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REVIEW = ROOT / 'art/cartoon/mermaid-expression-corrections-v1/review-data.json'
CHANGES = {
    '000': 'Show BOTH eyes, with her gaze directed more toward the viewer.',
    '010': 'Turn farther away from the viewer and show more of her back.',
    '012': 'Lean back more, as though watching something happening in the sky.',
    '013': 'Face slightly farther away from the viewer.',
    '014': 'Look up toward the sky.',
}
DETAILS = {
    '000': 'Change only the head orientation and eyes: turn the partially submerged face toward the viewer sufficiently that BOTH blue eyes are clearly visible above the water and looking toward the viewer. Keep the mouth submerged. Preserve the arched green tail in its exact position, the separate head at lower right, blonde hair, blue headband, and all water ripples.',
    '010': 'Rotate her head and upper torso away from the viewer toward the right, showing a rear three-quarter view with more of the back and back of the shoulder and less of the face. Preserve the original right-facing movement and waterline. Her long blonde hair falls behind her; green swimsuit straps remain in place. Do not turn her toward the camera.',
    '012': 'Make her lean back noticeably farther against the water, upper torso reclined about 25 degrees, chin raised and both gaze and face angled up toward activity overhead. Preserve the right-facing composition, relaxed smile, blonde hair and blue headband, green swimsuit with both straps in place, and the surrounding water ripples. Human anatomical proportions and a natural neck angle.',
    '013': 'Keep the upward gaze and head tipped back, but rotate the head slightly farther away from the viewer toward the right so the near-profile and rear of her head are more prominent and less of the front of her face is visible. Preserve the compact head, floating blonde hair trailing left, blue headband, waterline and detached splash at right.',
    '014': 'Lift the face and eyes to look UP at the sky with the head tipped back, as though floating on her back. The nose should point diagonally upward. Keep the compact mostly submerged head on the left, long blonde hair, blue headband, exactly one separate small hand emerging at right, and the same waterline and ripples. Do not add an exposed torso or extra limbs.',
}

def pin(path):
    return {'path': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

assets = json.loads(REVIEW.read_text(encoding='utf-8'))['assets']
entries = []
for frame, change in CHANGES.items():
    row = next(a for a in assets if a['key'] == f'SMGLIMSE.BMP-{frame}')
    original = ROOT / row['images']['original']['path']
    prior = ROOT / (row['images']['revised'] or row['images']['previous'])['path']
    nearest = ROOT / f'art/cartoon/mermaid-gifts-and-glimpses-batch-v1/reference/nearest8/SMGLIMSE.BMP/{frame}.png'
    prompt = ('Use case: precise-object-edit. Asset: a single transparent cartoon game sprite, SMGLIMSE frame ' + frame + '. '
              'Image 1 is the edit target and style authority. Image 2 is the original low-resolution pose/composition reference. '
              'Primary request: ' + DETAILS[frame] + ' '
              'Keep the established clean cel-shaded illustration, bold smooth black outlines, bright yellow hair, cyan accents, green costume/tail where present, adult character identity, proportions and sprite composition. '
              'Make only the requested pose/gaze correction. Preserve the exact canvas framing and all unrelated elements. '
              'Output the sprite on a genuinely transparent background with an alpha channel, no black or white background, no checkerboard, no labels, no text, no extra objects.')
    request = {'frame': f'SMGLIMSE.BMP-{frame}', 'created_at_utc': datetime.now(timezone.utc).isoformat(), 'tool': 'built-in image_gen', 'requested_change': change, 'prompt': prompt, 'inputs': [pin(prior), pin(nearest)], 'original': pin(original), 'appearance_approval': None}
    request_path = HERE / f'{frame}-request.json'
    request_path.write_text(json.dumps(request, indent=2) + '\n', encoding='utf-8')
    entries.append({'resource': 'SMGLIMSE.BMP', 'frame': frame, 'original': pin(original)['path'], 'previous': pin(prior)['path'], 'output': None, 'status': 'pending_generation', 'requested_change': change, 'request': pin(request_path)['path'], 'record': None})
(HERE / 'manifest.json').write_text(json.dumps({'schema_version': 1, 'appearance_approval': None, 'production_integrated': False, 'entries': entries}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'manifest': str(HERE / 'manifest.json'), 'requests': len(entries)}))
