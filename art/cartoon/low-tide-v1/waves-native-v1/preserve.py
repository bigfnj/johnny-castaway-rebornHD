"""One-time compact freeze of the completed eight-case native wave comparison."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
SCRATCH = ROOT / 'build/low-tide-v1/waves-native-v1'
DEST = HERE / 'evidence-v1'
RUNS = ('baseline-initial-v1', 'baseline-extended-v1', 'candidate-initial-v1', 'candidate-extended-v1')
MANIFEST = ROOT / 'art/cartoon/low-tide-v1/motion-review-v1/manifest.json'
MANIFEST_SHA = '97d7177dccdc3d149fba0b518202c59d57d5f4add899344af3c503d885743e14'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_bytes((json.dumps(obj, indent=2) + '\n').encode())


def main():
    if DEST.exists():
        raise ValueError('refusing existing wave evidence')
    copies = []
    reports = []
    excluded = []
    summaries = {}
    common_sources = None
    common_helpers = None
    runtime_matches = []
    for run in RUNS:
        folder = SCRATCH / run
        out = folder / 'captures'
        summary = json.loads((out / 'summary.json').read_bytes())
        launch = json.loads((folder / 'launch.json').read_bytes())
        inputs = json.loads((out / 'inputs.json').read_bytes())
        if summary['status'] != 'PASS' or launch['exit_code'] != 0 or not launch['no_surviving_task_container']:
            raise ValueError('run not complete PASS: ' + run)
        if any(row.get('smoke') != 'PASS' or row.get('fresh_repeat') != 'PASS' for row in summary['cases'].values()):
            raise ValueError('missing smoke/repeat: ' + run)
        if (out / 'build.stderr.txt').read_bytes():
            raise ValueError('compiler stderr requires inspection: ' + run)
        if common_sources is None:
            common_sources, common_helpers = inputs['protected_sha256'], inputs['helpers_sha256']
        if inputs['protected_sha256'] != common_sources or inputs['helpers_sha256'] != common_helpers:
            raise ValueError('source/observer identity differs between runs: ' + run)
        summaries[run] = summary
        for name in ('launch.json', 'launch.log'):
            copies.append((folder / name, run + '/' + name))
        for name in ('summary.json', 'inputs.json', 'build.json', 'build.stdout.txt', 'build.stderr.txt',
                     'smoke.json', 'smoke-progress.json', 'negative-controls.json'):
            if (out / name).is_file():
                copies.append((out / name, run + '/' + name))
        for case in summary['cases']:
            for phase in ('smoke', 'repeat'):
                source = out / case / phase
                report = json.loads((source / 'report.json').read_bytes())
                if report['status'] != 'PASS' or report['archive_sha256'] != summary['archive_sha256']:
                    raise ValueError('case archive/status mismatch: ' + str(source))
                if sha(source / 'capture.log') != report['log_sha256'] or sha(source / 'final.png') != report['png_sha256']:
                    raise ValueError('case log/image identity mismatch: ' + str(source))
                matches = [line for line in (source / 'capture.log').read_text().splitlines()
                           if re.search(r'warning|error|failed|ALSA|segmentation', line, re.I)]
                runtime_matches.extend({'run': run, 'case': case, 'phase': phase, 'line': line} for line in matches)
                reports.append({'run': run, 'case': case, 'phase': phase, 'display_count': len(report['displays']),
                                'duration_ms': report['duration_ms'], 'png_sha256': report['png_sha256']})
                for name in ('report.json', 'capture.log'):
                    copies.append((source / name, run + '/' + case + '/' + phase + '/' + name))
        excluded.append({'path': (out / 'integrated_shore_probe').relative_to(ROOT).as_posix(),
                         'sha256': sha(out / 'integrated_shore_probe'), 'kind': 'executable'})
    # Both initial groups are covered by the root-owned lossless browser media.
    if sha(MANIFEST) != MANIFEST_SHA:
        raise ValueError('root-owned browser manifest changed')
    for case in ('night_shift', 'raft5', 'johnny_front', 'johnny_rear'):
        copies.append((SCRATCH / 'candidate-extended-v1/captures' / case / 'smoke/final.png', 'images/' + case + '.png'))
    for relative, digest in {**common_sources, **common_helpers}.items():
        if sha(ROOT / relative) != digest:
            raise ValueError('source changed after capture: ' + relative)
    for relative in common_helpers:
        copies.append((ROOT / relative, 'helpers/' + relative))
    for name in ('README.md', 'check_high_control.py', 'preserve.py'):
        copies.append((HERE / name, 'helpers/waves-native-v1/' + name))
    copies.append((SCRATCH / 'high-control-witness.json', 'high-control-witness.json'))
    high = summaries['candidate-extended-v1']['cases']['high_control']['changed_pixels']
    if not high or any(high):
        raise ValueError('high-tide whole-scene comparison not exact')
    for name in ('static-candidate-v2.zip', 'all-waves-candidate-v1.zip'):
        path = ROOT / 'build/low-tide-v1' / name
        excluded.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'kind': 'private archive'})
    if runtime_matches:
        raise ValueError('runtime diagnostic matches require inspection: ' + repr(runtime_matches))
    if len({name for _, name in copies}) != len(copies):
        raise ValueError('duplicate evidence destination')
    DEST.mkdir()
    rows = []
    for source, relative in copies:
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = source.read_bytes()
        target.write_bytes(raw)
        rows.append({'path': relative, 'source': source.relative_to(ROOT).as_posix(),
                     'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    record = {'schema_version': 1, 'status': 'PASS', 'copies': rows, 'case_reports': reports,
        'source_commit_at_preservation': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'protected_source_sha256': common_sources, 'capture_helper_sha256': common_helpers,
        'excluded_archives_executables': excluded,
        'initial_native_pixels': {'manifest': MANIFEST.relative_to(ROOT).as_posix(), 'sha256': MANIFEST_SHA,
            'scope': 'Root-owned lossless browser reconstruction for initial none/clover. Browser validation is separate.'},
        'smoke_captures': 16, 'fresh_repeat_captures': 16, 'high_tide_identical_displays': len(high),
        'compiler_stderr_empty': True, 'runtime_diagnostic_matches': runtime_matches,
        'bulk_frames': 'All raw sequences remain scratch. Each retained report binds every displayed PNG and decoded RGB hash.',
        'limits': 'Explicit state bypasses story/calendar selection. Night/cloud/raft fallback remains. Current port native execution only, not original executable or workstation display testing. No human motion acceptance inferred.'}
    save(DEST / 'evidence.json', record)
    for row in rows:
        if sha(DEST / row['path']) != row['sha256'] or sha(ROOT / row['source']) != row['sha256']:
            raise ValueError('copy readback mismatch: ' + row['path'])
    save(DEST / 'readback.json', {'status': 'PASS', 'evidence_sha256': sha(DEST / 'evidence.json'),
        'copies_checked': len(rows), 'original_sources_checked': len(rows), 'copied_bytes': sum(r['bytes'] for r in rows)})
    print(json.dumps({'evidence_sha256': sha(DEST / 'evidence.json'), 'readback_sha256': sha(DEST / 'readback.json'),
                      'copies': len(rows), 'bytes': sum(r['bytes'] for r in rows)}, indent=2))


if __name__ == '__main__':
    main()
