"""Preserve small integration reports and exact witnesses, excluding other owners."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRATCH = ROOT / 'build/shoreline-repair-v1/integration-v1'
EVIDENCE = HERE / 'evidence'
sha = lambda b: hashlib.sha256(b).hexdigest()


def copy(source, target):
    raw = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != raw:
        raise ValueError(str(target) + ': frozen evidence differs')
    target.write_bytes(raw)


def main():
    for name, run in [('initial-private-comparison', 'run-v2'), ('fresh-replay', 'replay-v3')]:
        folder = SCRATCH / run
        report = json.loads((folder / 'verification.json').read_bytes())
        assert report['status'] == 'PASS'
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix in ('.json', '.txt', '.py'):
                copy(path, EVIDENCE / name / path.name)
    # Recover the exact original helper from its retained one-line mutant.
    old = (SCRATCH / 'run-v2/member-guard-removed.py').read_bytes()
    replacement = b'        pass  # executed guard removal\n'
    assert old.count(replacement) == 1
    old = old.replace(replacement, b"        require(not failures, '\\n'.join(failures))\n")
    expected = json.loads((SCRATCH / 'run-v2/verification.json').read_bytes())['helper_sha256']
    assert sha(old) == expected
    (EVIDENCE / 'initial-private-comparison/integrate.py').write_bytes(old)
    for name in ('inputs.json', 'integrate.py', 'prepare.py'):
        copy(HERE / name, EVIDENCE / 'fresh-replay' / name)
    failed = SCRATCH / 'run-v1'
    for name in ('replay-sides.stdout.txt', 'replay-sides.stderr.txt'):
        copy(failed / name, EVIDENCE / 'setup-failure' / name)
    setup = {'status': 'RETAINED_SETUP_FAILURE', 'cause': 'Snapshot omitted CMakeLists.txt; the side exporter located the outer repository and rejected the resulting recipe paths.',
             'resolution': 'Include the repository marker in the isolated source snapshot. No exporter, raw art or PNG changed.',
             'scratch': 'build/shoreline-repair-v1/integration-v1/run-v1'}
    (EVIDENCE / 'setup-failure/explanation.json').write_text(json.dumps(setup, indent=2)+'\n', encoding='utf-8', newline='\n')
    final = json.loads((SCRATCH / 'replay-v3/verification.json').read_bytes())
    initial = json.loads((SCRATCH / 'run-v2/verification.json').read_bytes())
    assert final['archive_sha256'] == initial['archive_sha256']
    files = {p.relative_to(HERE).as_posix(): sha(p.read_bytes()) for p in sorted(EVIDENCE.rglob('*')) if p.is_file() and p.name != 'evidence.json'}
    external = {p: sha((HERE / p).read_bytes()) for p in ('prepare.py', 'integrate.py', 'preserve.py', 'REPRODUCE.md', 'inputs.json', 'runtime-recipe.json', 'production-acceptance.json', 'prior-pack.json', 'integrated-pack.json', 'reviewed-wave-members.json')}
    binder = {'schema_version': 1, 'status': 'PASS', 'scope': 'Authoring reproduction and standard package verification; production/native/Windows gates remain separately recorded.',
              'paths_relative_to': HERE.relative_to(ROOT).as_posix(), 'files_sha256': files, 'external_files_sha256': external,
              'archive_sha256': final['archive_sha256'], 'candidate_scratch': 'build/shoreline-repair-v1/integration-v1/run-v2/scrantic_data.zip',
              'member_count': 2598, 'cartoon_assets': 47, 'source_reproduced_slots': 14, 'inherited_rows_exact': 33,
              'actual_private_zip_compared_in': 'evidence/initial-private-comparison/verification.json',
              'fresh_replay_without_private_zip_in': 'evidence/fresh-replay/verification.json',
              'excluded': ['Large ZIPs, duplicate PNGs and source-snapshot tree remain under ignored build/shoreline-repair-v1/integration-v1/',
                           'native-final/ and windows-final/ use separate binders; not included in this evidence set.'],
              'index_requirement': 'Every files_sha256 and external_files_sha256 path, plus this binder, must be present in Git index with these exact bytes before commit.'}
    target = EVIDENCE / 'evidence.json'
    target.write_text(json.dumps(binder, indent=2)+'\n', encoding='utf-8', newline='\n')
    for path, digest in {**files, **external}.items():
        assert sha((HERE / path).read_bytes()) == digest, path
    print(json.dumps({'status': 'PASS', 'copied_files': len(files), 'external_files': len(external), 'binder_sha256': sha(target.read_bytes()), 'archive_sha256': final['archive_sha256']}))


if __name__ == '__main__':
    main()
