from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[2]
source = root / 'build/seasonal-v1/native-baseline-v2'
target = root / 'art/cartoon/seasonal-v1/native/evidence-baseline-v1'
assert not target.exists()
target.mkdir(parents=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
copied = {}

def retain(path, relative):
    dest = target / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dest)
    assert sha(path) == sha(dest)
    copied[relative] = sha(dest)

for relative in ['launch.json', 'launch.log', 'captures/build.json',
                 'captures/build.stdout.txt', 'captures/build.stderr.txt',
                 'captures/inputs.json', 'captures/summary.json', 'captures/negative-controls.json']:
    retain(source / relative, 'records/' + relative)
for path in sorted((source / 'captures').glob('*/*/*/report.json')):
    retain(path, 'records/' + path.relative_to(source).as_posix())
for path in sorted((source / 'captures/day').glob('*/smoke/capture.log')):
    retain(path, 'records/' + path.relative_to(source).as_posix())
retain(root / 'build/seasonal-v1/native-controls-v1/report.json', 'records/supplemental-controls.json')
for relative in ['launch.json', 'launch.log']:
    retain(root / 'build/seasonal-v1/native-baseline-v1' / relative, 'initial-failure/' + relative)
for name in ['driver.c', 'capture.py', 'run.py', 'check.py', 'README.md']:
    retain(target.parent / name, 'helpers/' + name)
retain(Path(__file__), 'preserve_baseline.py')
summary = json.loads((source / 'captures/summary.json').read_bytes())
assert summary['helper_sha256'] == copied['helpers/capture.py']
assert summary['driver_sha256'] == copied['helpers/driver.c']
report = {'schema_version': 1, 'status': 'PASS', 'files_sha256': copied,
          'selected_archive': summary['selected_archive'],
          'local_capture_root': source.relative_to(root).as_posix(),
          'not_copied': ['PNG/PPM native images (hashes in each report)', 'native executable (hash in build.json)', 'repeated ZIP copies (selected archive hash recorded)'],
          'reproduction': 'Use live native/run.py and README commands from source checkout397edf8 plus these added helper files; frozen copies have repository-relative imports and are evidence snapshots, not standalone launch locations.'}
(target / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
assert all(sha(target / rel) == digest for rel, digest in copied.items())
print(json.dumps({'status': 'PASS', 'files': len(copied), 'bytes': sum((target / rel).stat().st_size for rel in copied), 'evidence_sha256': sha(target / 'evidence.json')}))
