"""One explicit configuration shared by native ring capture and later review."""
import hashlib
import json
from pathlib import Path

ROOT = Path('/source') if Path('/source/CMakeLists.txt').exists() else Path(__file__).resolve().parent.parents[2]
PRODUCTION_SHA = '1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63'
APPROVED = {
    17: {'path': 'build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png', 'sha256': '60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1'},
    16: {'path': 'build/front-arrival/export016-v2/BMP/JOHNWALK.BMP/016.png', 'sha256': '1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92'},
}
CANDIDATE_FRAMES = (0, 15)
DEFAULT_CLIP = 'decreasing'
CLIPS = {
    'decreasing': {'step': -1, 'label': 'Front → right → back → left', 'headings': [0, 7, 6, 5, 4, 3, 2, 1, 0]},
    'increasing': {'step': 1, 'label': 'Front → left → back → right', 'headings': [0, 1, 2, 3, 4, 5, 6, 7, 0]},
}
HEADING_LABELS = ['Front', 'Front-left', 'Left side', 'Back-left', 'Back', 'Back-right', 'Right side', 'Front-right']
FIXED_CAMERA_HD = [560, 400, 400, 280]


def stages(clip):
    values = CLIPS[clip]['headings']
    return [{'id': 'prime', 'from': 0, 'to': 0}] + [
        {'id': f'turn{i:02}', 'from': values[i - 1], 'to': values[i]} for i in range(1, len(values))]


def contract():
    path = ROOT / 'art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json'
    cases = json.loads(path.read_bytes())['native_trace']['cases']
    result = {}
    for clip in CLIPS:
        result[clip] = {}
        for stage in stages(clip):
            key = f'A-turn-{stage["from"]}-{stage["to"]}'
            row = dict(cases[key])
            row['destination_heading'] = stage['to']
            # adsPlayWalk sets the first timer to6 before accepting the initial
            # returned delay. Later walkAnimate returns replace the timer.
            row['expected_native_duration_ms'] = 120 + sum(d['delay_ticks'] * 20 for d in row['draws'][1:])
            result[clip][stage['id']] = row
    return {'trace_source': path.relative_to(ROOT).as_posix(),
            'trace_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'clips': result,
            'scope': 'Independent original port draw/delay trace plus actual adsPlayWalk first6-tick timer. Native display timestamps are separately observed; no original-binary timing claim.'}
