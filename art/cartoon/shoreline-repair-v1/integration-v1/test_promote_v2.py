"""Promotion V2 transaction tests, exclusively in a disposable repository copy."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = HERE.relative_to(ROOT)
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    assert not a.work.exists()
    work = a.work.resolve()
    # Exact, restored V1 disposable fixture; never use the live repository as target.
    source = ROOT / 'build/shoreline-repair-v1/integration-v1/preflight-tests-v2'
    fixture = work / 'fixture'
    shutil.copytree(source / 'fixture', fixture)
    local = fixture / REL
    shutil.copy2(HERE / 'promote_v2.py', local / 'promote_v2.py')
    candidate = source / 'candidate.zip'
    native = fixture / 'build/synthetic-native-summary.json'
    archive, ledger = fixture / 'assets/scrantic_data.zip', fixture / 'art/cartoon/pack.json'
    original = {archive: archive.read_bytes(), ledger: ledger.read_bytes()}
    live = {p: sha(p.read_bytes()) for p in (ROOT/'assets/scrantic_data.zip', ROOT/'art/cartoon/pack.json', candidate)}
    helper = local / 'promote_v2.py'
    digest = sha(helper.read_bytes())
    records = []

    def run(name, promote=False, mode=None, expected=None):
        report = fixture / ('build/' + name + '.json')
        argv = [sys.executable, '-B', str(helper)]
        if mode:
            driver = local / ('fault-' + name + '.py')
            code = "import sys\nfrom pathlib import Path\nimport promote_v2 as m\noriginal = m.atomic_bytes\n"
            code += "report = Path(sys.argv[sys.argv.index('--report')+1])\n"
            code += "def fail(path, raw):\n    if path == report:\n"
            code += "        print('WITNESS both disposable production files changed', flush=True)\n"
            code += "        assert m.ROOT.joinpath('assets/scrantic_data.zip').read_bytes() == Path(sys.argv[sys.argv.index('--candidate')+1]).read_bytes()\n"
            code += "        assert m.ROOT.joinpath('art/cartoon/pack.json').read_bytes() == m.HERE.joinpath('integrated-pack.json').read_bytes()\n"
            if mode == 'after':
                code += "        original(path, raw)\n"
            code += "        raise OSError('injected report write failure')\n    original(path, raw)\n"
            code += "m.atomic_bytes = fail\ntry: m.main()\nexcept OSError as error:\n    print('FAIL '+str(error), file=sys.stderr)\n    raise SystemExit(1)\n"
            driver.write_text(code, encoding='utf-8', newline='\n')
            argv = [sys.executable, '-B', str(driver)]
        argv += ['--candidate', str(candidate), '--native-summary', str(native), '--native-summary-sha256', sha(native.read_bytes()), '--report', str(report)]
        if promote: argv += ['--promote']
        result = subprocess.run(argv, capture_output=True, text=True, timeout=90)
        for stream in ('stdout', 'stderr'):
            (work / (name+'.'+stream+'.txt')).write_text(getattr(result, stream), encoding='utf-8', newline='\n')
        assert result.stdout.splitlines()[0] == 'WITNESS shore-promote-v2 ' + digest
        if expected:
            assert result.returncode == 1 and result.stderr.strip() == 'FAIL '+expected, result.stderr
            assert 'WITNESS both disposable production files changed' in result.stdout
            assert not report.exists()
            assert all(p.read_bytes() == raw for p, raw in original.items()), 'rollback failed'
        else:
            assert result.returncode == 0, result.stderr
            record = json.loads(report.read_bytes())
            assert record['production_promoted'] == promote
            if promote:
                assert archive.read_bytes() == candidate.read_bytes() and ledger.read_bytes() == (local/'integrated-pack.json').read_bytes()
                for path, raw in original.items(): path.write_bytes(raw)
            else:
                assert all(p.read_bytes() == raw for p, raw in original.items())
            shutil.copy2(report, work / report.name)
        records.append({'name': name, 'status': 'PASS', 'helper_sha256': digest, 'exit_code': result.returncode,
                        'fault': expected, 'disposable_production_restored': True})

    run('smoke-preflight')
    run('report-write-refused', promote=True, mode='before', expected='injected report write failure')
    run('report-write-then-failure', promote=True, mode='after', expected='injected report write failure')
    original_helper = helper.read_bytes()
    text = original_helper.decode()
    needle = '            atomic_bytes(zip_path, old_zip)\n            atomic_bytes(pack_path, old_pack)'
    assert text.count(needle) == 1
    helper.write_bytes(text.replace(needle, '            pass  # executed rollback-removal witness').encode())
    digest = sha(helper.read_bytes())
    shutil.copy2(helper, work/'promote-rollback-removed.py')
    try:
        run('removed-rollback', promote=True, mode='before', expected='injected report write failure')
    except AssertionError as error:
        assert str(error) == 'rollback failed'
        assert archive.read_bytes() == candidate.read_bytes() and ledger.read_bytes() == (local/'integrated-pack.json').read_bytes()
        records.append({'name':'removed-rollback','status':'FIRED','failure':'rollback failed',
                        'executed_helper_sha256':digest,'disposable_files_left_changed_as_expected':True})
    else:
        raise AssertionError('rollback removal was not detected')
    helper.write_bytes(original_helper)
    digest = sha(original_helper)
    for path, raw in original.items(): path.write_bytes(raw)
    run('restored-successful-transaction', promote=True)
    assert live == {p: sha(p.read_bytes()) for p in live}
    report = {'schema_version': 1, 'status': 'PASS', 'scope': 'Synthetic native fixture and disposable repository only; not native evidence or authorization.',
              'helper_sha256': digest, 'test_sha256': sha(Path(__file__).read_bytes()), 'controls': records,
              'actual_report_write_failures_after_both_production_files_changed': 2, 'archive_and_ledger_rollback_exact': True,
              'partial_promotion_report_removed': True, 'restored_positive_transaction_passed': True,
              'executed_rollback_removal_detected': True,
              'live_files_unchanged': {str(p): v for p,v in live.items()}}
    (work/'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status':'PASS','controls':len(records),'real_production_changed':False}))


if __name__ == '__main__':
    main()
