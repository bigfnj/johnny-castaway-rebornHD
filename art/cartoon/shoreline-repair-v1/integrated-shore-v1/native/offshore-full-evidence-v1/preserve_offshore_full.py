"""Copy only compact completed full-matrix records into a new evidence bundle."""
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
NATIVE = ROOT / 'art/cartoon/shoreline-repair-v1/integrated-shore-v1/native'
RUN = ROOT / 'build/shoreline-repair-v1/offshore-full-v1'
TARGET = NATIVE / 'offshore-full-evidence-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    summary = json.loads((RUN / 'captures/summary.json').read_bytes())
    launch = json.loads((RUN / 'launch.json').read_bytes())
    inputs = json.loads((RUN / 'captures/inputs.json').read_bytes())
    negatives = json.loads((RUN / 'captures/negative-controls.json').read_bytes())
    assert summary['status'] == 'PASS' and summary['phase'] == 'full'
    assert len(summary['cases']) == 12
    assert all(row['smoke'] == row['fresh_repeat'] == 'PASS' for row in summary['cases'].values())
    assert launch['exit_code'] == 0 and launch['no_surviving_task_container']
    assert negatives['status'] == 'PASS' and len(negatives['results']) == 6
    for name, digest in inputs['helpers_sha256'].items():
        assert sha(RUN / 'captures/helper-snapshot' / name) == digest, name
    for row in launch['inputs'].values():
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    assert not TARGET.exists(), 'new immutable destination required'
    TARGET.mkdir()
    copied, origins = {}, {}

    def copy(source, relative):
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        copied[relative] = sha(source)
        origins[relative] = source.relative_to(ROOT).as_posix()

    for name in ('launch.json', 'launch.log'):
        copy(RUN / name, name)
    for path in sorted((RUN / 'captures').rglob('*')):
        if path.is_file() and path.suffix in ('.json', '.log', '.txt', '.py', '.c'):
            copy(path, 'captures/' + path.relative_to(RUN / 'captures').as_posix())
    copy(ROOT / 'build/shoreline-repair-v1/offshore-selected-v1/preparation.json', 'preparation.json')
    for name in ('src/engine/art_style.c', 'src/engine/art_style.h', 'src/engine/graphics.c', 'src/engine/island.c'):
        assert sha(ROOT / name) == inputs['protected_sha256'][name], name
        copy(ROOT / name, 'runtime-source/' + name)
    copy(Path(__file__), 'preserve_offshore_full.py')

    selected = {
        'day_pumpkin': 'day/pumpkin/candidate/smoke/final.png',
        'day_clover': 'day/clover/candidate/smoke/final.png',
        'day_tree': 'day/tree/candidate/smoke/final.png',
        'day_banner': 'day/banner/candidate/smoke/final.png',
        'low_clover': 'motion/low_clover/candidate/smoke/final.png',
        'night_shift_clover': 'motion/night_shift_clover/candidate/smoke/final.png',
        'front_arrival': 'motion/johnny_front/candidate/smoke/display-044.png',
        'rear_initial': 'motion/johnny_rear/candidate/smoke/display-001.png',
        'rear_arrival': 'motion/johnny_rear/candidate/smoke/display-064.png',
    }
    visual = {
        'method': 'Direct visual inspection of actual 1280x960 native PNGs. No pixel changes, crop recentering or retiming.',
        'new_blocking_contact_findings': [],
        'observations': [
            'Full-size pumpkin, clovers and tree rest on visible sand. Banner remains attached across the palm canopy.',
            'Front arrival 018 at native (433,225), rear initial 018 at (452,254), and mirrored rear arrival 018 at (394,209) appear grounded without a new visible gap.',
            'Low tide retains the existing HD/pixel beach, rock and low-wave layers. Those layers cover part of the new top-ground contour as before; this is unchanged fallback coverage, not new style approval.',
            'Night retains the existing fallback sky/ocean and clouds. The shifted ground, palm, clovers and Johnny move together at the requested scene offset.',
        ],
        'limits': 'Static visual review covers the named images, not every animated display or every engine route. Native timing/phase and pixel-scope checks cover all recorded displays. Human offshore choice is recorded separately.',
        'images_local_only': {key: {'path': (RUN / 'captures' / value).relative_to(ROOT).as_posix(), 'sha256': sha(RUN / 'captures' / value)} for key, value in selected.items()},
    }
    save(TARGET / 'visual-review.json', visual)
    copied['visual-review.json'] = sha(TARGET / 'visual-review.json')
    totals = sum(row['display_count'] for row in summary['cases'].values())
    README = f'''# Selected offshore scene: full native verification

The exact selected offshore archive ab5c8094 was tested against the same full-size V5 seasonal baseline 3d619201. Their 2,598 named members differ only at ground 000 and high-wave frames 003 through 011; all four holiday PNGs and the other 2,588 members are unchanged. Production data 4c8085be was not modified.

The run completed 24 baseline/candidate smoke captures across 12 cases before starting 24 fresh-process exact repeats. Cases comprise five initial day states (no decoration and each of four decorations), high-tide motion with and without clovers, low-tide motion with and without clovers, a shifted night scene with clovers, and Johnny's actual D-C-F and B-A-E routes. One side of the matrix contains {totals} display records; all four baseline/candidate smoke/repeat sides retain their actual records. Day states last one native wait; only clovers and no-decoration cases receive the long wave loops. This is not an all-decoration-by-all-state cross product.

Every capture verifies actual ground and wave surface placement, sprite canvas dimensions, real logical tick times, native phase progression and returned calls. All high-wave phases 003-011 and low-wave phases 030-041 are observed in their long clips. Baseline and candidate timelines, phases and Johnny positions match exactly. Pixel differences stay inside the changed ground/foam rectangles, adjusted for the scene offset. Fresh repeats reproduce exact display bytes. The 60 protected source/data inputs and both private archives are unchanged after execution. Six executed damaged-data controls fail with their expected labels, followed by restored positive checks: ground offset, center offset, first phase tuple, timestamp, out-of-scope pixel and missing phase 008. These reuse the existing captured-data guards; no new runtime or authoring mutation was introduced for this run.

The reviewed seasonal props and sampled front/rear Johnny contacts show no new visible grounding problem. Low-tide shore/rock/waves and the night backdrop remain existing fallback artwork. Their visibility is technical compatibility coverage, not approval of newly generated low-tide or night art. See visual-review.json for exact inspected image hashes and the limits of static visual inspection. Actual browser playback and human approval remain separate records.

## Retained records and reproduction

evidence.json binds files physically inside this folder. Reports retain every image filename, digest, time, phase and Johnny draw. Full PNG/PPM collections, ZIPs and the executable remain local under build/shoreline-repair-v1/offshore-full-v1; no missing scratch image is claimed as a durable member. The browser review separately preserves its displayed media. Captured helper snapshots, four changed runtime source snapshots, compiler command and all source fingerprints are retained here. This preservation script copies exact bytes and refuses an existing output folder; it is not a command to replay over historical evidence.

Use an isolated scratch checkout with the source commit from launch.json plus the exact source hashes from captures/inputs.json and captures/build.json. Restore pinned production archive 4c8085be and the exact baseline archive 3d619201 before replay, since the helper deliberately refuses later production packages. Reconstruct the selected private archive using the retained preparation.json and its pinned exporter inputs, or restore exact archive ab5c8094. The earlier native/evidence/README.md documents baseline dependencies. Run the helper from the original native directory depth so its maintained helper imports resolve:

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/run.py --baseline build/shoreline-repair-v1/selected-v1/baseline.zip --candidate build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --output build/shoreline-repair-v1/offshore-full-replay --phase full
```

The pinned Docker image and Xvfb keep the application off the workstation desktop. launch.json records the exact image, arguments, successful exit and absence of the task container after cleanup. This observer renders the current port with selected scene state; it does not validate original-executable timing or palette parity. Explicit state selection bypasses calendar and cargo-suppression policy. No production package was promoted by these tests.
'''
    (TARGET / 'README.md').write_text(README, encoding='utf-8', newline='\n')
    copied['README.md'] = sha(TARGET / 'README.md')
    save(TARGET / 'evidence.json', {
        'schema_version': 1, 'status': 'PASS', 'kind': 'technical-full-native-matrix',
        'art_approval_recorded_separately': True, 'files_sha256': copied, 'copied_from': origins,
        'source_commit': launch['source_commit'], 'package_pair': summary['package_pair'],
        'capture_root_local_only': RUN.relative_to(ROOT).as_posix(),
        'smoke_captures': 24, 'fresh_repeat_captures': 24, 'cases': 12,
        'display_records_per_matrix_side': totals, 'executed_native_negative_controls': 6,
        'limits': 'Current-port selected-state verification. Calendar/cargo policy, original executable parity and all engine routes are outside scope.',
    })
    assert all(sha(TARGET / name) == digest for name, digest in copied.items())
    result = {'status': 'PASS', 'file_count': len(copied), 'bytes': sum((TARGET / name).stat().st_size for name in copied),
              'evidence_sha256': sha(TARGET / 'evidence.json'),
              'method': 'Every retained file rehashed after copy. Only physically retained files appear in files_sha256; images/executables/ZIPs remain explicitly local.'}
    save(TARGET / 'readback.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
