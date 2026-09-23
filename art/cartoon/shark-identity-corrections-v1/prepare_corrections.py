"""Freeze the superseded drawings and plan the user's shark identity correction."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BATCH = HERE.parent / 'mermaid-departures-and-dates-batch-v1'
selection = {'SLEVEJM1.BMP': list(range(10)), 'SLEVEJM2.BMP': list(range(6)) + [9, 10, 11], 'SLEVEJM3.BMP': list(range(8))}
versions = json.loads((BATCH / 'selected-versions.json').read_text(encoding='utf-8'))
def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
entries = []
for resource, frames in selection.items():
    for frame in frames:
        key = f'{resource}-{frame:03}'
        old_version = versions.get(key, 1)
        version = old_version + 1
        folder = BATCH / 'generation' / resource
        assert not (folder / f'{frame:03}-v{version}-request.json').exists(), key
        entries.append({'key': key, 'resource': resource, 'frame': f'{frame:03}',
                        'previous_version': old_version, 'version': version,
                        'original': pin(BATCH / 'reference/original' / resource / f'{frame:03}.png'),
                        'nearest8': pin(BATCH / 'reference/nearest8' / resource / f'{frame:03}.png'),
                        'previous': pin(folder / f'{frame:03}-generated-v{old_version}.png'),
                        'previous_record': pin(folder / f'{frame:03}-record-v{old_version}.json'),
                        'output_path': (folder / f'{frame:03}-generated-v{version}.png').relative_to(ROOT).as_posix(),
                        'request_path': (folder / f'{frame:03}-v{version}-request.json').relative_to(ROOT).as_posix(),
                        'record_path': (folder / f'{frame:03}-record-v{version}.json').relative_to(ROOT).as_posix()})
assert len(entries) == 27
data = {'schema_version': 1, 'status': 'corrections_in_progress',
        'user_request': 'while we go through everything for approval, can you start on this massive overhaul. the "dolphin" you drew is a shark,  there are other references of the shark that have already been converted so i would start there, but it is a gray shark with razor teeth and a sneaky demeanor.',
        'direction': 'Restore the established neutral-gray shark, pale ivory underside, razor triangular teeth, gill slits and sly half-lidded brows. Exact original anatomy and gestures govern pose; the old dolphin interpretation is superseded.',
        'selection': selection, 'count': len(entries), 'entries': entries,
        'style_references': [pin(HERE.parent / p) for p in ['sharks-batch-v1/generation/GJFFFOOD.BMP/019-generated-v1.png', 'sharks-batch-v1/generation/SHARK.BMP/025-generated-v1.png']],
        'appearance_approval': None, 'production_integrated': False, 'native_motion_checked': False}
(HERE / 'correction-plan.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
(HERE / 'previous-selected-versions.json').write_text(json.dumps(versions, indent=2) + '\n', encoding='utf-8')
(HERE / 'README.md').write_text('# Shark identity corrections\n\nThe user identified the animal in the departure scenes as the established gray shark with razor teeth and a sneaky demeanor. The earlier dolphin interpretation is superseded. This pass covers 27 drawings, including partial bodies and exposed fins.\n\ncorrection-plan.json freezes the previous drawing per frame and assigns each new version. The exact original governs anatomy and gesture; GJFFFOOD019 and SHARK025 supply established shark identity and tooth design. The other 45 drawings keep their current selections.\n\nNew requests and byte-exact built-in ImageGen outputs are stored as versioned siblings in mermaid-departures-and-dates-batch-v1/generation/. The focused HTML review compares the original, previous interpretation and new shark correction. Appearance approval remains pending.\n', encoding='utf-8')
print('Prepared 27 shark identity corrections; previous candidates pinned.')
