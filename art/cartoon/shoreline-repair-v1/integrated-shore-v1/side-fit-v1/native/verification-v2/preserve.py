"""Freeze compact completed combined native records; never copy bulk media or ZIPs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent
ROOT = next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
RUN = ROOT/'build/shoreline-repair-v1/native-side-clean-v2'
PACKAGE = ROOT/'build/shoreline-repair-v1/side-clean-selected-v2'
TARGET = NATIVE/'evidence-v2'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    captures = RUN/'captures'
    summary = json.loads((captures/'summary.json').read_bytes())
    inputs = json.loads((captures/'inputs.json').read_bytes())
    launch = json.loads((RUN/'launch.json').read_bytes())
    negatives = json.loads((captures/'negative-controls.json').read_bytes())
    checks = json.loads((HERE/'package-regression.json').read_bytes())
    assert summary['status'] == 'PASS' and summary['phase'] == 'full'
    assert summary['smoke_captures'] == summary['fresh_repeat_captures'] == 10
    assert len(summary['cases']) == 5
    assert all(r['smoke'] == r['fresh_repeat'] == 'PASS' for r in summary['cases'].values())
    assert inputs['pair'] == summary['package_pair']
    assert launch['exit_code'] == 0 and launch['no_surviving_task_container']
    assert negatives['status'] == 'PASS' and len(negatives['results']) == 6
    assert checks['status'] == 'PASS' and checks['package_pair'] == summary['package_pair']
    assert checks['source_sha256'] == sha(NATIVE/'combined.py')
    for name,digest in inputs['helpers_sha256'].items():
        assert sha(captures/'helper-snapshot'/name) == digest, name
        assert sha(ROOT/name) == digest, name
    for name,digest in inputs['protected_sha256'].items():
        assert sha(ROOT/name) == digest, name
    for row in launch['inputs'].values():
        assert sha(ROOT/row['path']) == row['sha256'], row['path']
    assert not TARGET.exists(), 'fresh immutable evidence folder required'
    TARGET.mkdir()
    copied,origins = {},{}

    def copy(source,relative):
        dest = TARGET/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(source.read_bytes())
        copied[relative] = sha(source)
        origins[relative] = source.relative_to(ROOT).as_posix()

    for name in ('launch.json','launch.log'):
        copy(RUN/name,name)
    for source in sorted(captures.rglob('*')):
        if source.is_file() and 'profile' not in source.parts and source.suffix in ('.json','.log','.txt','.py','.c','.h'):
            copy(source,'captures/'+source.relative_to(captures).as_posix())
    for name in ('preparation.json','export-report.json','center007-support.json'):
        copy(PACKAGE/name,'package/'+name)
    for name in ('check_package.py','package-regression.json','combined_guard_disabled.py','preserve.py',
                 'correct_metadata.py','corrected-selection-v2.json','metadata-clarification.json'):
        copy(HERE/name,'verification/'+name)
    readme = '''# Combined side placement and cleaned center wave

The private candidate replaces six side wave PNGs and center 007 in the selected offshore archive. All 2,591 remaining payloads, including ground 000, center 006/008 and all four holidays, are retained exactly. Production was not changed. Human appearance approval is separate.

Ten baseline/candidate smoke captures across five cases completed before ten fresh repeats. Cases are high clovers, shifted night clovers, unchanged low-tide clovers, and actual Johnny front D-C-F and rear B-A-E calls. Timelines, wave phases, logical draw origins, Johnny positions and call returns match. High loops cover all nine phases; low covers all twelve. Scene changes are restricted to the old/new side canvas unions and the exact visible RGBA difference support of 007 only while that phase is active. Low tide is identical across the entire frame. Six damaged-log/pixel controls fire, followed by restored positives.

Package verification ran in fresh processes: the selected package passed; an altered 007 pixel failed by name; a copy with only that payload guard disabled accepted the corrupt package; the unchanged original accepted the selected package again. The actual source digest witness and sole mutated source are retained. The host independently decoded and reproduced the exact 007 support spans. Host authoring used Pillow 12.3.0; the pinned native Docker image has no Pillow and reads the hash-bound support record.

This folder retains compact logs, reports, source/helper snapshots, input identities and actual Docker arguments. Every PNG and decoded frame digest remains in its capture report. Bulk PNG/PPM files, executable and private ZIPs remain local under the capture root; the separate browser atlas retains displayed pixels. The Docker image is locally available; this record makes no claim of remote image distribution. The source commit and fingerprints identify the compiled port. This does not establish original-executable timing, palette parity, calendar policy, every story route or human art approval.

Replay in an isolated checkout with the pinned source and production archive from captures/inputs.json. Restore selected offshore baseline ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac using its existing retained authoring/preparation records. Keep helpers at their original repository paths so imports resolve. Use fresh output folders:

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/native/prepare_v2.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --output build/shoreline-repair-v1/side-clean-replay-package
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/native/run_v2.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --candidate build/shoreline-repair-v1/side-clean-replay-package/candidate.zip --preparation build/shoreline-repair-v1/side-clean-replay-package/preparation.json --runtime-commit 1aad361fe78dde2c956e05dc451b8d5bab100af0 --output build/shoreline-repair-v1/side-clean-native-replay
```

The earlier six-side-only draft remains unchanged. The historical preparation sentence saying “and2591 other payloads” is imprecise; 2,591 is the total unchanged count, inclusive of the named ground, center and holiday members.

The captured combined selection inherited the previous 007 raw-source path/hash and true byte-identity annotation. Its actual runtime/source_path, export pins and ZIP payload were correctly bound to the new 007 throughout. verification/corrected-selection-v2.json supplies the corrected annotation for integration, with explicit false identity flags for the seven changed rows and true flags for 000/006/008. verification/metadata-clarification.json verifies all ten actual source ancestries and ZIP identities and pins both versions. Historical captured inputs remain unchanged; no pixel or package changed for this correction.
'''
    (TARGET/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    copied['README.md'] = sha(TARGET/'README.md')
    record = {'schema_version':1,'status':'PASS','kind':'combined-side-and007-native-evidence',
        'accepted':False,'files_sha256':copied,'copied_from':origins,
        'package_pair':summary['package_pair'],'source_commit':launch['source_commit'],
        'capture_root_local_only':RUN.relative_to(ROOT).as_posix(),'smoke_captures':10,'fresh_repeat_captures':10,
        'display_records_per_variant':sum(r['display_count'] for r in summary['cases'].values()),
        'native_negative_controls':6,'package_fresh_process_checks':4,
        'metadata_clarification':{'path':'verification/metadata-clarification.json','sha256':copied['verification/metadata-clarification.json']},
        'corrected_integration_selection':{'path':'verification/corrected-selection-v2.json','sha256':copied['verification/corrected-selection-v2.json']},
        'scope':'Five current-port cases; static state selection; human appearance and production promotion remain separate.'}
    save(TARGET/'evidence.json',record)
    assert all(sha(TARGET/name) == digest for name,digest in copied.items())
    assert {p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file()} == set(copied)|{'evidence.json'}
    print(json.dumps({'status':'PASS','retained_files':len(copied),'evidence_sha256':sha(TARGET/'evidence.json'),
                      'bytes':sum((TARGET/name).stat().st_size for name in copied)}))


if __name__ == '__main__':
    main()
