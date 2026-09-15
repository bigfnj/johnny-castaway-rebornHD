"""Bind the existing Linux route observer to unchanged current production sources."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / 'johnny-cartoon-production/build/rear-native-capture'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'duplicate-archive-member:' + str(path))
        return {name: sha(archive.read(name)) for name in names}


def main():
    print('WITNESS arrival setup.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    old = json.loads((PRIOR / 'baseline-v2/build.json').read_bytes())
    source_hashes = {name: digest for name, digest in old['protected_sha256'].items()
                     if name != 'assets/scrantic_data.zip'}
    for name, digest in source_hashes.items():
        require(sha((ROOT / name).read_bytes()) == digest, 'unchanged-production-source:' + name)
    exe = PRIOR / 'baseline-v2/rear_route_probe'
    require(sha(exe.read_bytes()) == old['executable_sha256'], 'saved-linux-executable')
    require(sha((PRIOR / 'route_driver.c').read_bytes()) == old['driver_sha256'], 'saved-observer-source')
    archive = ROOT / 'assets/scrantic_data.zip'
    require(sha(archive.read_bytes()) == '1daf8f95614fde8efd85745a8baac02a41d88c2775a91374d66959174220aa7e', 'current-production-archive')
    current_members = members(archive)
    require(current_members == members(PRIOR / 'candidate-v1/scrantic_data.zip'), 'prior-reviewed-member-equality')
    require('data/styles/cartoon/BMP/JOHNWALK.BMP/018.png' not in current_members, 'arrival-still-hd-fallback')
    target = OUT / 'baseline'
    require(not target.exists(), 'preserve-existing-baseline')
    target.mkdir()
    shutil.copyfile(exe, target / 'rear_route_probe')
    shutil.copyfile(PRIOR / 'route_driver.c', OUT / 'route_driver.c')
    shutil.copyfile(PRIOR / 'run_baseline.py', OUT / 'capture_format.py')
    shutil.copyfile(PRIOR / 'baseline-v2/build.json', OUT / 'historical-build.json')
    for phase in ('smoke', 'full'):
        shutil.copyfile(PRIOR / f'candidate-v1/{phase}/report.json', OUT / f'prior-{phase}-report.json')
    evidence = {
        'scope': 'Fresh current 27-asset baseline with an unchanged saved Linux observer. No compilation or production archive modification.',
        'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'setup_sha256': sha(Path(__file__).read_bytes()),
        'executable_sha256': old['executable_sha256'],
        'driver_sha256': old['driver_sha256'],
        'historical_build_sha256': sha((OUT / 'historical-build.json').read_bytes()),
        'protected_sha256': {**source_hashes, 'assets/scrantic_data.zip': sha(archive.read_bytes())},
        'prior_capture_reports': {p: sha((OUT / f'prior-{p}-report.json').read_bytes()) for p in ('smoke', 'full')},
        'all_prior_reviewed_members_equal': len(current_members),
        'archive_members': current_members,
        'original_build_archive_sha256': old['protected_sha256']['assets/scrantic_data.zip'],
        'current_archive_sha256': sha(archive.read_bytes()),
        'source_identity_policy': 'Exact bytes for every recorded source/header/CMake/test-driver input; only archive identity is updated after full uncompressed-member equality to the previously reviewed candidate.'
    }
    save(OUT / 'source-reuse.json', evidence)
    print(f'PASS saved executable and {len(source_hashes)} unchanged build/source inputs; {len(current_members)} current members equal prior reviewed candidate', flush=True)


if __name__ == '__main__':
    main()
