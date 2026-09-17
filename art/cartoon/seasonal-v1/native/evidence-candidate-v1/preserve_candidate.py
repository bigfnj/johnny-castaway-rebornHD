from pathlib import Path
import copy
import hashlib
import json
import shutil
import zipfile

root = Path(__file__).resolve().parents[2]
source = root / 'build/seasonal-v1/native-candidate-v1'
target = root / 'art/cartoon/seasonal-v1/native/evidence-candidate-v1'
assert not target.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = json.loads((source / 'captures/summary.json').read_bytes())
expected = [f'data/styles/cartoon/BMP/HOLIDAY.BMP/{i:03}.png' for i in range(4)]
assert summary['status'] == 'PASS'
assert summary['selected_archive']['new_cartoon_members'] == expected
selected = {}
for frame, member in enumerate(expected):
    path = root / f'art/cartoon/seasonal-v1/candidates/v1/BMP/HOLIDAY.BMP/{frame:03}.png'
    selected[member] = {'path': path.relative_to(root).as_posix(), 'sha256': sha(path)}

def verify_runtime(mapping):
    for member, row in selected.items():
        if mapping[member] != row['sha256']:
            raise ValueError('selected candidate runtime identity:' + member)

verify_runtime(summary['selected_archive']['holiday_members_sha256'])
wrong = copy.deepcopy(summary['selected_archive']['holiday_members_sha256'])
wrong[expected[0]] = '0' * 64
try:
    verify_runtime(wrong)
except ValueError as error:
    assert str(error) == 'selected candidate runtime identity:' + expected[0]
    witness = str(error)
else:
    raise AssertionError('runtime binding negative survived')
verify_runtime(summary['selected_archive']['holiday_members_sha256'])
archive = root / 'build/seasonal-v1/cartoon-seasonal-draft-v1.zip'
assert sha(archive) == summary['selected_archive']['archive_sha256']
with zipfile.ZipFile(archive) as packed:
    assert {member: hashlib.sha256(packed.read(member)).hexdigest() for member in expected} == summary['selected_archive']['holiday_members_sha256']
target.mkdir(parents=True)
copied = {}

def retain(path, relative):
    dest = target / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dest)
    assert sha(path) == sha(dest)
    copied[relative] = sha(dest)

for relative in ['launch.json', 'launch.log', 'comparison.json', 'captures/build.json',
                 'captures/build.stdout.txt', 'captures/build.stderr.txt',
                 'captures/inputs.json', 'captures/summary.json', 'captures/negative-controls.json']:
    retain(source / relative, 'records/' + relative)
for path in sorted((source / 'captures').glob('*/*/*/report.json')):
    retain(path, 'records/' + path.relative_to(source).as_posix())
for path in sorted((source / 'captures/day').glob('*/smoke/capture.log')):
    retain(path, 'records/' + path.relative_to(source).as_posix())
for name in ['driver.c', 'capture.py', 'run.py', 'compare.py', 'README.md']:
    retain(target.parent / name, 'helpers/' + name)
retain(root / 'art/cartoon/seasonal-v1/candidates/v1/export-report.json', 'records/export-report.json')
retain(Path(__file__), 'preserve_candidate.py')
assert summary['helper_sha256'] == copied['helpers/capture.py']
assert summary['driver_sha256'] == copied['helpers/driver.c']
binding = {'status': 'PASS', 'selected_runtime': selected,
           'negative_control': {'status': 'FIRED', 'failure': witness,
                                'method': 'Altered copied selected-runtime SHA, exact named failure; restored positive. No PNG or archive modified.'},
           'scope': 'All four actual native-selected members equal the four candidates/v1 exported PNG bytes. Technical source identity, not human approval.'}
binding_path = target / 'records/export-binding.json'
binding_path.write_text(json.dumps(binding, indent=2) + '\n', encoding='utf-8', newline='\n')
copied['records/export-binding.json'] = sha(binding_path)
baseline = root / 'art/cartoon/seasonal-v1/native/evidence-baseline-v1/evidence.json'
report = {'schema_version': 1, 'status': 'PASS', 'human_art_approval': 'pending', 'files_sha256': copied,
          'selected_archive': summary['selected_archive'],
          'linked_baseline': {'path': baseline.relative_to(root).as_posix(), 'sha256': sha(baseline)},
          'local_capture_root': source.relative_to(root).as_posix(),
          'retained_logs': 'Five primary day smoke logs plus launcher/build logs. All30 capture reports retained; remaining logs and images stay in scratch.',
          'not_copied': ['PNG/PPM native images (hashes in each report)', 'native executable (hash in build.json)', 'repeated ZIP copies (selected archive hash recorded)'],
          'reproduction': 'Use live native/run.py with draft ZIP and a fresh output, then native/compare.py against reproduced baseline. Source397edf8 and exact helpers are pinned; frozen helper copies are evidence snapshots, not standalone launch paths.'}
(target / 'evidence.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
assert all(sha(target / rel) == digest for rel, digest in copied.items())
print(json.dumps({'status': 'PASS', 'files': len(copied), 'bytes': sum((target / rel).stat().st_size for rel in copied), 'evidence_sha256': sha(target / 'evidence.json'), 'selected_archive_sha256': sha(archive)}))
