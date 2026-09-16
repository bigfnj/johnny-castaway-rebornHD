"""Six explicit native connecting-pose contracts, independent of capture logs."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = Path('/source') if Path('/source/CMakeLists.txt').exists() else next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
OUT = Path('/out') if ROOT == Path('/source') else ROOT/'build/connecting-poses/native-motion-v1'
PRODUCTION_SHA = '1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db'
TABLE_LF_SHA = '3b387634d62a915cdf308c1e370eea7a70aa07bc361eb19de70ff4931aa2ad70'
IMAGE = 'johnny-platform-cleanup:latest'
IMAGE_ID = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'
CANDIDATE_FRAMES = (9, 10, 12)
DEFAULT_CLIP = 'front_arc'
TURN_BOOKMARKS = (91, 145, 260, 314, 405, 471)

# A block is (role, exact walk-table row indices). Waypoint calls keep the
# actual intermediate turn, without a fabricated stop at that spot.
CLIPS = {
    'front_arc': {'label': 'Front turn: D to C', 'prime': [3,3,3,3], 'travel': [3,3,2,7], 'path': 'DC',
                  'blocks': [('ordinary turn', [316,315,314,321]), ('travel', list(range(278,288))), ('arrival', [276])],
                  'frames': [3,9,10,9,28,29,24,25,26,27,28,29,24,25,17], 'duration_ms': 3400},
    'rear_arc': {'label': 'Rear turn: D to E', 'prime': [3,6,3,6], 'travel': [3,6,4,2], 'path': 'DE',
                 'blocks': [('ordinary turn', [319,318,317,316]), ('travel', list(range(289,301))), ('arrival', [416])],
                 'frames': [23,12,23,3,4,5,6,7,8,1,2,3,4,6,7,8,0], 'duration_ms': 3640},
    'travel_cb': {'label': 'Front walk entry and exit: C to B', 'prime': [2,1,2,1], 'travel': [2,1,1,1], 'path': 'CB',
                  'blocks': [('travel', list(range(196,210))), ('arrival', [155])],
                  'frames': [9,28,29,24,25,26,27,28,29,24,25,26,27,9,17], 'duration_ms': 3400},
    'travel_ec': {'label': 'Front walk to profile: E to C', 'prime': [4,7,4,7], 'travel': [4,7,2,6], 'path': 'EC',
                  'blocks': [('travel', list(range(356,380))), ('arrival', [275])],
                  'frames': [28,29,24,25,26,27,28,29,24,25,9,3,4,5,6,7,8,1,2,3,4,6,7,8,0], 'duration_ms': 4600},
    'waypoint_front': {'label': 'Front waypoint: D via C to F', 'prime': [3,7,3,7], 'travel': [3,7,5,3], 'path': 'DCF',
                       'blocks': [('travel', list(range(278,288))), ('waypoint turn', [260,261]), ('travel', list(range(245,259))), ('arrival', [483])],
                       'frames': [28,29,24,25,26,27,28,29,24,25,10,9,4,6,7,8,1,2,3,4,5,6,7,21,22,23,18], 'duration_ms': 4840},
    'waypoint_rear': {'label': 'Rear waypoint: B via A to E', 'prime': [1,3,1,3], 'travel': [1,3,4,5], 'path': 'BAE',
                      'blocks': [('travel', list(range(109,132))), ('waypoint turn', [95]), ('travel', list(range(0,16))), ('arrival', [419])],
                      'frames': [11,19,20,21,22,23]*3+[11,19,20,21,22,12]+[19,20,21,22,23,11]*2+[19,20,21,22,18], 'duration_ms': 6520},
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_bytes())


def contract():
    table = ROOT/'src/data/walk_data.h'
    raw = table.read_bytes()
    normalized = raw.decode().replace('\r\n','\n').replace('\r','\n').encode()
    assert sha(normalized) == TABLE_LF_SHA, 'original-derived table identity'
    rows = [list(map(int,m.groups())) for m in re.finditer(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', table.read_text())]
    assert len(rows)==489, 'complete original-derived walk table'
    result={}
    for name, clip in CLIPS.items():
        selected = [(role,index) for role,indices in clip['blocks'] for index in indices]
        assert [rows[i][3] for role,i in selected] == clip['frames'], 'connecting sequence:'+name
        assert selected[-1][0]=='arrival' and all(rows[i][1] for role,i in selected), 'valid final arrival and non-sentinel rows:'+name
        prime_index=TURN_BOOKMARKS[clip['prime'][0]]+9+clip['prime'][1]
        stages={}
        for stage, api, chosen, selections in (
            ('prime',clip['prime'],chr(65+clip['prime'][0]),[('standing',prime_index)]),
            ('travel',clip['travel'],clip['path'],selected),
        ):
            draws=[]
            for ordinal,(role,index) in enumerate(selections):
                flip,x,y,frame=rows[index]
                draws.append(dict(frame=frame,flip_x=flip,x=x-1,y=y,delay_ticks=80 if ordinal==len(selections)-1 else 6,role=role,table_row=index))
            stages[stage]={'api_arguments':api,'chosen_path':chosen,'draws':draws,
                           'expected_native_duration_ms':120+20*sum(r['delay_ticks'] for r in draws[1:])}
        assert sum(stage['expected_native_duration_ms'] for stage in stages.values())==clip['duration_ms'], 'connecting timing budget:'+name
        result[name]=stages
    return {'method':'Explicit original-derived table rows and native API boundaries, independently checked against compiled unchanged walk/calcpath before rendering. All display times are observed separately.',
            'source_table':table.relative_to(ROOT).as_posix(),'source_sha256':sha(raw),'source_lf_sha256':sha(normalized),'clips':result}
