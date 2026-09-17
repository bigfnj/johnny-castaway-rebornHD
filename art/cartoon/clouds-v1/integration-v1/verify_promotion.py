"""Exercise promotion only in disposable roots, including report-write rollback."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def probe(mode, sandbox):
    spec = importlib.util.spec_from_file_location('cloud_integration', HERE / 'prepare.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('WITNESS promotion ' + sha((HERE / 'prepare.py').read_bytes()), flush=True)
    module.ROOT = sandbox
    module.HERE = sandbox / HERE.relative_to(ROOT)
    baseline = (ROOT / 'build/clouds-v1/integration-v2/baseline.zip').read_bytes()
    prior_pack = (HERE / 'prior-pack.json').read_bytes()
    for name in ('package-readback.json', 'integrated-pack.json', 'prior-pack.json', 'runtime-recipe.json', 'production-acceptance.json'):
        target = module.HERE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((HERE / name).read_bytes())
    archive, ledger = sandbox / 'assets/scrantic_data.zip', sandbox / 'art/cartoon/pack.json'
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(baseline)
    ledger.write_bytes(prior_pack)
    candidate = sandbox / 'candidate.zip'
    candidate.write_bytes((ROOT / 'build/clouds-v1/candidate.zip').read_bytes())
    if mode == 'corrupt_candidate':
        candidate.write_bytes(candidate.read_bytes() + b'controlled-corruption')
    if mode == 'report_failure':
        def fail_save(path, value):
            path.write_bytes(b'partial report')
            raise OSError('controlled promotion record write failure')
        module.save = fail_save
    expected = {'corrupt_candidate': 'candidate identity changed',
                'report_failure': 'controlled promotion record write failure'}
    try:
        module.promote(candidate)
    except (AssertionError, OSError) as exc:
        assert mode in expected and str(exc) == expected[mode], str(exc)
        assert archive.read_bytes() == baseline and ledger.read_bytes() == prior_pack
        assert not (module.HERE / 'promotion.json').exists()
        print('PASS refused or rolled back: ' + str(exc), flush=True)
    else:
        assert mode == 'positive'
        assert archive.read_bytes() == candidate.read_bytes()
        assert ledger.read_bytes() == (HERE / 'integrated-pack.json').read_bytes()
        assert json.loads((module.HERE / 'promotion.json').read_bytes())['status'] == 'PASS'
        print('PASS disposable promotion readback', flush=True)


def main():
    if len(sys.argv) > 1:
        probe(sys.argv[1], Path(sys.argv[2]))
        return
    scratch = ROOT / 'build/clouds-v1/promotion-controls'
    scratch.mkdir(parents=True, exist_ok=True)
    rows = []
    for mode in ('positive', 'corrupt_candidate', 'report_failure', 'positive'):
        sandbox = Path(tempfile.mkdtemp(prefix=mode + '-', dir=scratch))
        result = subprocess.run([sys.executable, '-B', str(Path(__file__)), mode, str(sandbox)],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'WITNESS promotion ' + sha((HERE / 'prepare.py').read_bytes()) in result.stdout
        rows.append({'mode': mode, 'sandbox': str(sandbox), 'exit_code': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    report = {'status': 'PASS', 'helper_sha256': sha((HERE / 'prepare.py').read_bytes()),
              'harness_sha256': sha(Path(__file__).read_bytes()), 'cases': rows,
              'scope': 'Four fresh subprocesses use only disposable ZIP/ledger/report paths. Candidate corruption refuses writes; a partial report-write fault rolls back both files and removes the incomplete new record. No live promotion is performed by these checks.'}
    (HERE / 'promotion-controls.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS promotion controls: positive, bad candidate, partial report failure, restored positive')


if __name__ == '__main__':
    main()
