"""Freeze the disposable promotion-preflight proof, separate from package evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT)
WORK = ROOT / 'build/shoreline-repair-v1/integration-v1/preflight-tests-v2'
OUT = HERE / 'promotion-preflight'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    report = json.loads((WORK / 'verification.json').read_bytes())
    assert report['status'] == 'PASS' and not report['production_promoted']
    OUT.mkdir(exist_ok=True)
    sources = {p.name: p for p in WORK.iterdir() if p.is_file() and p.suffix in ('.json', '.txt')}
    sources['promote-native-guard-removed.py'] = WORK / 'fixture' / REL / 'promote-native-guard-removed.py'
    sources['synthetic-native-summary.json'] = WORK / 'fixture/build/synthetic-native-summary.json'
    sources['initial-smoke-failure.stdout.txt'] = WORK.parent / 'preflight-tests-v1/smoke-preflight.stdout.txt'
    sources['initial-smoke-failure.stderr.txt'] = WORK.parent / 'preflight-tests-v1/smoke-preflight.stderr.txt'
    for name, path in sources.items():
        raw = path.read_bytes()
        dest = OUT / name
        if dest.exists(): assert dest.read_bytes() == raw, name
        dest.write_bytes(raw)
    files = {('promotion-preflight/' + name): sha((OUT / name).read_bytes()) for name in sorted(sources)}
    external = {name: sha((HERE / name).read_bytes()) for name in ('promote.py', 'test_promote.py', 'preserve_preflight.py')}
    binder = {'schema_version': 1, 'status': 'PASS', 'paths_relative_to': REL.as_posix(), 'files_sha256': files,
              'external_files_sha256': external, 'smoke_before_regression': True, 'case_count': 16,
              'scope': 'Disposable preflight guard proof only. Synthetic native PASS is not actual native evidence or authorization. No call used --promote.',
              'initial_setup_failure': 'Synthetic summary was first outside its disposable repository; moved inside that fixture. Real files were never touched.',
              'excluded': 'Disposable copied archive, source fixture and candidate ZIP remain ignored scratch. Live archive, ledger and native candidate hashes remained exact.'}
    target = OUT / 'evidence.json'
    target.write_text(json.dumps(binder, indent=2)+'\n', encoding='utf-8', newline='\n')
    for name, digest in {**files, **external}.items(): assert sha((HERE/name).read_bytes()) == digest, name
    print(json.dumps({'status': 'PASS', 'copied_files': len(files), 'external_files': len(external), 'binder_sha256': sha(target.read_bytes())}))


if __name__ == '__main__':
    main()
