"""Seven-payload wave comparison with unchanged native pixels and recorded clocks."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
PACKER = HERE.parents[1] / 'offshore-scene-review-v1/build_review.py'
PACKER_SHA = 'b68c38f0e5cb0a25fecebcd2db966865707721db33be57f8a42ff3f705f71d21'
BASE_SHA = 'ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac'
CANDIDATE_SHA = '862d70fc93d1ed26020e15e8b04627dd56e97b47df8d86b99b8312c6cc88c3d0'
SELECTION_PINS = {
    'build/shoreline-repair-v1/side-clean-selected-v2/export-report.json': '5a3310203e73355ab18fb84736cca47aa1aae2d9e43a1b86c60c1eb3ce2ab99c',
    'art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/native/verification-v2/corrected-selection-v2.json': '0e24fc59fe7aea76c5b03d1c90ceac52aaf07cfcd622f72435950ad76c91b29e',
    'art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/native/verification-v2/metadata-clarification.json': 'df53ac8fa0122f6e97bbc630a54128e3e75d8ce404d3bdd15dfe416619d20638',
}
CASES = {
    'high_clover': ('Waves with clovers', [2,0,0,0,0,0,20]),
    'night_shift_clover': ('Night, shifted island', [2,1,-80,20,0,0,20]),
    'low_clover': ('Low tide: unchanged reference', [2,0,0,0,1,0,24]),
    'johnny_front': ('Johnny: front route', [0,0,0,0,0,1,1]),
    'johnny_rear': ('Johnny: rear route', [0,0,0,0,0,2,1]),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_bytes((json.dumps(value, indent=2)+'\n').encode())

def validate_inputs(captures):
    for path, digest in SELECTION_PINS.items():
        assert sha(ROOT / path) == digest, 'selected provenance identity: ' + path
    inputs = json.loads((captures / 'inputs.json').read_bytes())
    summary = json.loads((captures / 'summary.json').read_bytes())
    pair = inputs['pair']
    assert summary['status'] == 'PASS' and summary['phase'] == 'full', 'completed native matrix'
    assert pair == summary['package_pair'], 'summary package identity'
    assert pair['baseline_sha256'] == BASE_SHA and pair['candidate_sha256'] == CANDIDATE_SHA, 'selected comparison archives'
    expected = {f'data/styles/cartoon/BMP/BACKGRND.BMP/{f:03}.png' for f in (3,4,5,7,9,10,11)}
    assert set(pair['changed_members']) == expected and pair['unchanged_members'] == 2591, 'seven changed payloads'
    assert pair['changed_members']['data/styles/cartoon/BMP/BACKGRND.BMP/007.png']['after'] == '623c8f3fb8a4905a15917db963542f178d86472f0809134227bc2053fa800c56', 'clean007 selected source'
    loops = {}
    for key in ('high_clover', 'night_shift_clover'):
        for side in ('baseline', 'candidate'):
            report = json.loads((captures / key / side / 'smoke/report.json').read_bytes())
            first = report['displays'][0]
            endpoint = [r for r in report['displays'] if r['time_ms'] == 1440]
            assert first['time_ms'] == 0 and first['phases'] == [3,7,9,-1], key + ': initial007 phase'
            assert endpoint and endpoint[-1]['phases'] == first['phases'], key + ': observed1440 phase closure'
            loops[key + '/' + side] = {'start_phases': first['phases'], 'end_phases': endpoint[-1]['phases'],
                                      'native_duration_ms': report['duration_ms'], 'loop_ms': 1440}
    return loops

def build(captures, output):
    assert not output.exists(), 'fresh review output required'
    assert sha(PACKER) == PACKER_SHA, 'frozen atlas packer'
    loops = validate_inputs(captures)
    spec = importlib.util.spec_from_file_location('wave_native_atlas', PACKER)
    packer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packer)
    packer.CASES = CASES
    packer.HERE = HERE
    packer.build(captures, output)
    manifest = json.loads((output / 'manifest.json').read_bytes())
    manifest.update(default_case='high_clover', labels=['Earlier placement', 'Repositioned, clean waves'],
                    source_phase_loops=loops,
                    scope='Six whole side-wave placements plus the cleaned center007. Same ground, full-size clovers, other center phases and native timing. Human appearance review pending.')
    for key, clip in manifest['cases'].items():
        clip['recorded_duration_ms'] = clip['duration_ms']
        clip['recorded_display_count'] = len(clip['frames'])
        clip['loop'] = key in ('high_clover', 'night_shift_clover')
        if key in ('high_clover', 'night_shift_clover'):
            clip['frames'] = [r for r in clip['frames'] if r['time_ms'] <= 1440]
            clip['duration_ms'] = 1440
        if key == 'low_clover':
            assert {f for r in clip['frames'] for f in r['phases'] if f >= 0} == set(range(30,42)), 'all12 low-tide phases retained'
            assert clip['duration_ms'] == clip['recorded_duration_ms'] > 1440, 'full low-tide clock retained'
        dx, dy = clip['args'][2]*2, clip['args'][3]*2
        clip['views'] = {'waves': [510+dx,510+dy,700,270], 'center': [660+dx,550+dy,430,185],
                         'island': [510+dx,220+dy,700,610], 'full': [0,0,1280,960]}
    save(output / 'manifest.json', manifest)
    record = json.loads((output / 'build.json').read_bytes())
    record.update(builder_sha256=sha(Path(__file__)), packer_sha256=PACKER_SHA,
                  manifest_sha256=sha(output / 'manifest.json'), scope=manifest['scope'],
                  selection_provenance_sha256=SELECTION_PINS)
    save(output / 'build.json', record)
    print('PASS wave review', record['html_sha256'], record['manifest_sha256'])

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--captures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    build(a.captures.resolve(), a.output.resolve())
