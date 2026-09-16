"""Explicit profile routes; source-table contracts are separate from captured events."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = Path('/source') if Path('/source/CMakeLists.txt').exists() else next(p for p in HERE.parents if (p / 'assets/scrantic_data.zip').is_file())
OUT = Path('/out') if ROOT == Path('/source') else ROOT / 'build/profile-walk/native-motion-v1'
PRODUCTION_SHA = '096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6'
IMAGE = 'johnny-platform-cleanup:latest'
IMAGE_ID = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
CANDIDATE_FRAMES = tuple(range(1, 9))
DEFAULT_CLIP = 'left'
CLIPS = {
    'right': {'label': 'Right: F to C', 'prime': [5, 6, 5, 6], 'travel': [5, 6, 2, 6], 'path': 'FC', 'bookmark': 443, 'count': 13, 'ordinary': False},
    'left': {'label': 'Left: C to A', 'prime': [2, 2, 2, 2], 'travel': [2, 2, 0, 2], 'path': 'CA', 'bookmark': 163, 'count': 32, 'ordinary': False},
    'right_boundary': {'label': 'Right: ordinary 003 departure', 'prime': [5, 7, 5, 7], 'travel': [5, 7, 2, 6], 'path': 'FC', 'bookmark': 443, 'count': 13, 'ordinary': True},
    'left_boundary': {'label': 'Left: ordinary 003 departure', 'prime': [2, 3, 2, 3], 'travel': [2, 3, 0, 2], 'path': 'CA', 'bookmark': 163, 'count': 32, 'ordinary': True},
}
TURN_BOOKMARKS = (91, 145, 260, 314, 405, 471)
EXPECTED_FRAMES = {
    'FC': [3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 6, 7, 8],
    'CA': [4, 5, 6, 7, 8, 1, 2, 3] * 3 + [4, 5, 5, 6, 7, 8, 1, 2],
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def contract():
    table = ROOT / 'src/data/walk_data.h'
    rows = [list(map(int, match.groups())) for match in re.finditer(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', table.read_text())]
    assert len(rows) == 489, 'complete original-derived walk table'
    clips = {}
    for name, clip in CLIPS.items():
        start, heading, end, arrival = clip['travel']
        priming = rows[TURN_BOOKMARKS[start] + 9 + clip['prime'][1]]
        travel = rows[clip['bookmark']:clip['bookmark'] + clip['count']]
        assert [row[3] for row in travel] == EXPECTED_FRAMES[clip['path']], 'profile sequence:' + name
        assert {row[0] for row in travel} == ({0} if end == 2 else {1}), 'profile flip:' + name
        assert rows[clip['bookmark'] + clip['count']] == [0, 0, 0, 0], 'route sentinel:' + name
        prefix = [rows[TURN_BOOKMARKS[start] + arrival]] if clip['ordinary'] else []
        standing = rows[TURN_BOOKMARKS[end] + 9 + arrival]
        stages = {}
        for stage, api, selected, roles, chosen in (
            ('prime', clip['prime'], [priming], ['standing'], chr(65 + start)),
            ('travel', clip['travel'], prefix + travel + [standing], ['ordinary turn'] * len(prefix) + ['travel'] * len(travel) + ['arrival'], clip['path']),
        ):
            draws = [dict(frame=row[3], flip_x=row[0], x=row[1] - 1, y=row[2], delay_ticks=80 if i == len(selected) - 1 else 6, role=roles[i]) for i, row in enumerate(selected)]
            stages[stage] = {'api_arguments': api, 'chosen_path': chosen, 'draws': draws,
                             'expected_native_duration_ms': 120 + sum(row['delay_ticks'] * 20 for row in draws[1:])}
        clips[name] = stages
    return {'method': 'Exact source-table rows and specified public call boundaries; independently checked against compiled walk.c. First timer is 6 ticks. Display events are separately observed. No original-binary timing claim.',
            'source_table': table.relative_to(ROOT).as_posix(), 'source_sha256': sha(table.read_bytes()), 'clips': clips}


def load_json(path):
    return json.loads(Path(path).read_bytes())
