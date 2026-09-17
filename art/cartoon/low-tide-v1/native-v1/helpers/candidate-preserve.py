"""One-time compact native evidence freeze; no source, archive or image changes."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'CMakeLists.txt').is_file())
BASE = ROOT / 'build/low-tide-v1/baseline-native'
DEST = ROOT / 'art/cartoon/low-tide-v1/native-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_bytes((json.dumps(obj, indent=2) + '\n').encode())


def main():
    if DEST.exists():
        raise ValueError('refusing existing durable native evidence')
    roots = {'baseline': BASE / 'captures-v1', 'candidate': HERE / 'captures-v1', 'prewave': HERE / 'prewave-v1'}
    for root in roots.values():
        if json.loads((root / 'summary.json').read_bytes())['status'] != 'PASS':
            raise ValueError('native summary not PASS: ' + str(root))
    copies = []
    def include(source, relative):
        copies.append((source, relative))
    include(HERE / 'bundle-README.md', 'README.md')
    for name in ('capture.py', 'run.py', 'prewave.py', 'run_prewave.py', 'preserve.py', 'README.md'):
        include(HERE / name, 'helpers/candidate-' + name)
    for name in ('capture.py', 'run.py', 'README.md'):
        include(BASE / name, 'helpers/baseline-' + name)
    inputs = json.loads((roots['candidate'] / 'inputs.json').read_bytes())
    for relative, digest in inputs['helper_sha256'].items():
        source = ROOT / relative
        if sha(source) != digest:
            raise ValueError('capture helper changed: ' + relative)
        if relative.startswith('art/'):
            include(source, 'dependencies/' + relative)
    include(roots['prewave'] / 'observer-source/driver.c', 'helpers/prewave-driver.c')
    for name in ('launch.json', 'launch.log'):
        include(BASE / name, 'baseline/' + name)
        include(HERE / name, 'candidate/' + name)
    for name in ('prewave-launch.json', 'prewave-launch.log'):
        include(HERE / name, 'prewave/' + name)
    for label, root in roots.items():
        for name in ('summary.json', 'inputs.json', 'build.json', 'build.stdout.txt', 'build.stderr.txt',
                     'smoke.json', 'smoke-progress.json', 'negative-controls.json'):
            if (root / name).is_file():
                include(root / name, label + '/' + name)
        cases = ('baseline', 'candidate') if label == 'prewave' else ('none/smoke', 'clover/smoke', 'none/repeat', 'clover/repeat')
        for case in cases:
            for name in ('report.json', 'capture.log'):
                include(root / case / name, label + '/' + case + '/' + name)
    for label, root in (('current', roots['baseline']), ('candidate', roots['candidate'])):
        for case in ('none', 'clover'):
            include(root / case / 'smoke/final.png', 'images/' + label + '-' + case + '.png')
    include(roots['prewave'] / 'baseline/prewave.png', 'images/prewave-current.png')
    include(roots['prewave'] / 'candidate/prewave.png', 'images/prewave-candidate.png')
    if len({rel for _, rel in copies}) != len(copies):
        raise ValueError('duplicate archival destination')
    for source, _ in copies:
        if not source.is_file():
            raise ValueError('missing archival input: ' + str(source))
    DEST.mkdir(parents=True)
    rows = []
    for source, relative in copies:
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = source.read_bytes()
        target.write_bytes(raw)
        rows.append({'path': relative, 'source': source.relative_to(ROOT).as_posix(),
                     'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    excluded = [ROOT / 'assets/scrantic_data.zip', ROOT / inputs['candidate_path'],
                roots['baseline'] / 'integrated_shore_probe', roots['candidate'] / 'integrated_shore_probe',
                roots['prewave'] / 'integrated_shore_probe']
    record = {'schema_version': 1, 'status': 'PASS', 'source_commit': commit, 'exact_copies': rows,
        'protected_source_sha256': inputs['protected_sha256'], 'capture_helper_sha256': inputs['helper_sha256'],
        'excluded_archives_executables': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in excluded],
        'bulk_frames': 'Omitted; retained case reports bind all actual displayed decoded RGB hashes and PNG hashes.',
        'scope': 'Technical low-tide static candidate and real native before-wave background comparison. No production promotion or human artwork approval inferred.'}
    save(DEST / 'evidence.json', record)
    for row in rows:
        if sha(DEST / row['path']) != row['sha256'] or sha(ROOT / row['source']) != row['sha256']:
            raise ValueError('archival readback mismatch: ' + row['path'])
    save(DEST / 'readback.json', {'status': 'PASS', 'evidence_sha256': sha(DEST / 'evidence.json'),
        'exact_copies_checked': len(rows), 'original_sources_checked': len(rows),
        'copied_bytes': sum(row['bytes'] for row in rows)})
    print(json.dumps({'evidence': str(DEST / 'evidence.json'), 'sha256': sha(DEST / 'evidence.json'),
                      'readback_sha256': sha(DEST / 'readback.json'), 'files': len(rows),
                      'bytes': sum(row['bytes'] for row in rows)}, indent=2))


if __name__ == '__main__':
    main()
