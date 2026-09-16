"""Fresh-process guard-removal witnesses for the final mixed-exporter handoff."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
SELECTION = HERE.parent / 'candidate-selection-v2.json'
OUT = ROOT / 'build/connecting-poses/native-motion-v1/negative-controls/selection-links-v2'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert not OUT.exists(), 'preserve final selection mutation evidence'
    source = (HERE / 'prepare_candidate.py').read_text(encoding='utf-8')
    cases = {
        'exporter': "'selected exporter binding:' + label",
        'test-inputs': "'selected ' + phase + ' input binding:' + label",
        'verification': "'selected verification binding:' + label",
        'runtime': "'selected runtime output binding:' + label",
    }
    variants = [('enabled', source)]
    for name, message in cases.items():
        nodes = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert)
                 and ast.get_source_segment(source, n.msg) == message]
        assert len(nodes) == 1, name
        condition = nodes[0].test
        lines = source.splitlines(keepends=True)
        begin = sum(map(len, lines[:condition.lineno-1])) + condition.col_offset
        end = sum(map(len, lines[:condition.end_lineno-1])) + condition.end_col_offset
        variants.append((name, source[:begin] + 'True' + source[end:]))
    before = sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    records = []
    for name, code in variants:
        folder = OUT / name
        folder.mkdir(parents=True)
        for file in ('config.py', 'check_selection.py'):
            shutil.copyfile(HERE / file, folder / file)
        validator = folder / 'prepare_candidate.py'
        validator.write_text(code, encoding='utf-8', newline='\n')
        child = folder / 'run.py'
        child.write_text('''import hashlib
from pathlib import Path
import sys
import unittest
import config
import prepare_candidate
import check_selection
config.HERE = config.ROOT / "art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1"
config.OUT = Path(__file__).resolve().parent / "output"
config.OUT.mkdir()
print("WITNESS executed validator SHA256=" + hashlib.sha256(Path(prepare_candidate.__file__).read_bytes()).hexdigest(), flush=True)
def test(self):
    check_selection.main()
suite = unittest.defaultTestLoader.loadTestsFromTestCase(type("SelectionLinks", (unittest.TestCase,), {"test_mixed_version_and_pose_bindings": test}))
raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
''', encoding='utf-8', newline='\n')
        run = subprocess.run([sys.executable, '-B', str(child), '--selection', str(SELECTION), '--candidate-version', '2'],
                             capture_output=True, text=True, timeout=30)
        (folder / 'stdout.txt').write_text(run.stdout, encoding='utf-8', newline='\n')
        (folder / 'stderr.txt').write_text(run.stderr, encoding='utf-8', newline='\n')
        assert 'WITNESS executed validator SHA256=' + sha(validator.read_bytes()) in run.stdout
        if name == 'enabled':
            assert run.returncode == 0 and '\nOK\n' in run.stderr, run.stderr
            assert 'PASS restored handoff after 6 exact named semantic-binding failures' in run.stdout
        else:
            assert run.returncode == 1 and 'FAILED (failures=1)' in run.stderr and 'ERROR:' not in run.stderr, run.stderr
            assert 'FAIL: test_mixed_version_and_pose_bindings' in run.stderr
        records.append({'case': name, 'result': 'PASS' if name == 'enabled' else 'FIRED',
            'failure_count': 0 if name == 'enabled' else 1, 'executed_validator_sha256': sha(validator.read_bytes()),
            'executed_checker_sha256': sha((folder / 'check_selection.py').read_bytes()),
            'stdout_sha256': sha((folder / 'stdout.txt').read_bytes()), 'stderr_sha256': sha((folder / 'stderr.txt').read_bytes())})
    assert before == sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    result = {'status': 'PASS', 'selection_sha256': sha(SELECTION.read_bytes()),
        'harness_sha256': sha(Path(__file__).read_bytes()), 'records': records,
        'production_unchanged_sha256': before,
        'scope': 'Actual final mixed-version checker executes in fresh python -B processes. Four individual validator assert conditions replaced by True, each produces exactly one named unittest failure. Enabled control passes all six valid-file input substitutions. No archive/source mutation.'}
    (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
