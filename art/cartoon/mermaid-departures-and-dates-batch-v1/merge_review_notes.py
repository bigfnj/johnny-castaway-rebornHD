"""Collect frame inspection notes and explicitly selected corrections."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
notes = {}
versions = json.loads((HERE / 'selected-versions.json').read_text(encoding='utf-8'))
for name in ['SLEVEJM1-SLEVEJM3-notes.json', 'SLEVEJM2-notes.json', 'SMDATE1-notes.json', 'SMDATE10-SMDATE11-notes.json', 'SMDATE6-notes.json']:
    path = HERE / name
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding='utf-8'))
    if 'assets' in data:
        for row in data['assets']:
            resource = row.get('resource', data.get('resource'))
            key = f"{resource}-{int(row['frame']):03}"
            notes[key] = row.get('visual_review', row.get('review_note', ''))
            if row.get('selected_version', 1) > 1:
                versions[key] = row['selected_version']
    else:
        assert all(isinstance(value, str) for value in data.values()), name
        notes.update(data)
overrides_path = HERE / 'shark-correction-overrides.json'
if overrides_path.exists():
    overrides = json.loads(overrides_path.read_text(encoding='utf-8'))
    for key, row in overrides['assets'].items():
        versions[key] = row['version']
        notes[key] = row['review_note']
selected = json.loads((HERE / 'selection.json').read_text(encoding='utf-8'))
expected = {f'{resource}-{frame:03}' for resource, frames in selected.items() for frame in frames}
assert set(notes) == expected, (sorted(expected - set(notes)), sorted(set(notes) - expected))
(HERE / 'review-notes.json').write_text(json.dumps(notes, indent=2) + '\n', encoding='utf-8')
(HERE / 'selected-versions.json').write_text(json.dumps(versions, indent=2) + '\n', encoding='utf-8')
print(f'Collected {len(notes)} frame notes and {len(versions)} explicitly selected revisions.')
