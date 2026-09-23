import json
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
rows = json.loads((ROOT / 'art/cartoon/mermaid-expression-corrections-v1/review-data.json').read_text(encoding='utf-8'))['assets']
changes = {
    '037': 'Show a life preserver with a yellow rope and a transparent open center; preserve the mermaid pose and her grip.',
    '038': 'Use the same white life preserver with yellow rope and open center, preserving its overhead angle and the mermaid pose.',
    '039': 'Show the life preserver and rope at the waterline with JUST her hand gripping it. Remove all hair, head and body.',
    '041': 'Use the same white life preserver, continuous yellow perimeter rope, and transparent open center.',
    '043': 'Use the same white life preserver, continuous yellow perimeter rope, and transparent open center.',
}
entries = []
for frame, change in changes.items():
    row = next(r for r in rows if r['resource'] == 'SMGIFT.BMP' and r['frame'] == frame)
    target = HERE / frame
    target.mkdir(parents=True, exist_ok=True)
    entries.append({
        'resource': 'SMGIFT.BMP', 'frame': frame,
        'original': row['images']['original']['path'],
        'previous': (row['images']['revised'] or row['images']['previous'])['path'],
        'output': None, 'status': 'pending_generation', 'requested_change': change,
        'request': (target / 'request.json').relative_to(ROOT).as_posix(),
        'record': (target / 'record.json').relative_to(ROOT).as_posix(),
    })
manifest = {'built_at_utc': datetime.now(timezone.utc).isoformat(), 'design': 'White padded flotation ring, soft gray underside, fully open transparent center, continuous golden-yellow rope around the outer rim, bold black cartoon linework.', 'appearance_approved': False, 'production_integrated': False, 'entries': entries}
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(HERE / 'manifest.json')
