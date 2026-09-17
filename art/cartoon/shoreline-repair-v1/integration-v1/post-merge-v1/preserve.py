"""Copy the completed main audit records without changing their bytes."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = next(path for path in Path(__file__).resolve().parents
            if (path / 'CMakeLists.txt').is_file() and (path / 'src/engine').is_dir())
SOURCE = ROOT / 'build/seasonal-post-merge'
BASE = ROOT / 'art/cartoon/shoreline-repair-v1/integration-v1'
DEST = BASE / 'post-merge-v1'
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def write_json(path, data):
    path.write_bytes((json.dumps(data, indent=2) + '\n').encode())

head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip()
assert head == '9b0a4ed1fb5920faf426c4d3aa89e45afadebf07', head
DEST.mkdir(exist_ok=True)
assert not (DEST / 'evidence.json').exists(), 'Completed record already exists'
copies = {
    'core-review.md': 'core-review.md',
    'platform-review.md': 'platform-review.md',
    'authoring-review.md': 'authoring-review.md',
    'package.json': 'package.json',
    'main-ci.json': 'main-ci.json',
    'index-v1/result.json': 'index-main.json',
}
for source, target in copies.items():
    if (DEST / target).exists():
        assert (SOURCE / source).read_bytes() == (DEST / target).read_bytes()
    else:
        shutil.copyfile(SOURCE / source, DEST / target)
    assert (SOURCE / source).read_bytes() == (DEST / target).read_bytes()
ci = json.loads((DEST / 'main-ci.json').read_bytes())
assert ci['headSha'] == head and ci['conclusion'] == 'success'
assert len(ci['jobs']) == 4 and all(job['conclusion'] == 'success' for job in ci['jobs'])
archive_sha = json.loads((DEST / 'package.json').read_bytes())['archive_sha256']
paths = ['build/Release/jc_reborn.exe', 'build/Release/jc_reborn.scr',
         'build/Release/scrantic_data.zip', 'assets/scrantic_data.zip']
deployment = {name: {'sha256': sha((ROOT / name).read_bytes()),
                     'bytes': (ROOT / name).stat().st_size} for name in paths}
assert deployment[paths[2]]['sha256'] == deployment[paths[3]]['sha256'] == archive_sha
write_json(DEST / 'deployment.json', {'main_commit': head, 'files': deployment,
           'scope': 'Built main outputs. Binaries remain untracked build artifacts. '
                    'The executable and screensaver are separate console/Windows-subsystem targets; '
                    'an initial collection-only equality assertion was removed after checking CMake. '
                    'No build or runtime failure occurred.'})
shutil.copyfile(__file__, DEST / 'preserve.py')
files = {path.name: sha(path.read_bytes()) for path in sorted(DEST.iterdir())}
write_json(DEST / 'evidence.json', {'main_commit': head, 'files_sha256': files,
           'scope': 'Copied post-merge records and collector. Windows main proof is bound separately.'})
spec = json.loads((BASE / 'index-final/spec.json').read_bytes())
for binder, fields in [('windows-final/main-v1/evidence.json', ['files']),
                       ('post-merge-v1/evidence.json', ['files_sha256'])]:
    path = BASE / binder
    spec.append({'binder': path.relative_to(ROOT).as_posix(),
                 'base': path.parent.relative_to(ROOT).as_posix(), 'fields': fields})
write_json(DEST / 'index-spec.json', spec)
print(json.dumps({'copied_records': len(copies), 'bound_files': len(files),
                  'destination': str(DEST), 'ci_jobs': [job['name'] for job in ci['jobs']],
                  'deployment': deployment}))
