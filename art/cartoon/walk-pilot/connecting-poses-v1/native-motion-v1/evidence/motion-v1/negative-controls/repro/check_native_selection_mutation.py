"""Execute the real selection checker with and without its runtime binding."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
SELECTION = HERE.parent / 'candidate-selection.json'
OUT = ROOT / 'build/connecting-poses/native-motion-v1/negative-controls/runtime-binding-mutation'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert not OUT.exists(), 'preserve previous mutation evidence'
    code = (HERE / 'prepare_candidate.py').read_text(encoding='utf-8')
    nodes = [n for n in ast.walk(ast.parse(code)) if isinstance(n, ast.Assert)
             and isinstance(n.msg, ast.BinOp)
             and isinstance(n.msg.left, ast.Constant)
             and n.msg.left.value == 'selected runtime output binding:']
    assert len(nodes) == 1, 'one runtime-output binding condition'
    condition = nodes[0].test
    lines = code.splitlines(keepends=True)
    begin = sum(map(len, lines[:condition.lineno-1])) + condition.col_offset
    end = sum(map(len, lines[:condition.end_lineno-1])) + condition.end_col_offset
    mutant = code[:begin] + 'True' + code[end:]
    assert mutant != code
    before = sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    records = []
    for name, source in (('enabled', code), ('removed', mutant)):
        folder = OUT / name
        folder.mkdir(parents=True)
        for file in ('config.py', 'check_selection.py'):
            (folder / file).write_bytes((HERE / file).read_bytes())
        validator = folder / 'prepare_candidate.py'
        validator.write_text(source, encoding='utf-8', newline='\n')
        child = folder / 'run.py'
        child.write_text('''import hashlib
from pathlib import Path
import config
import prepare_candidate
import check_selection
config.OUT = Path(__file__).resolve().parent / "output"
config.OUT.mkdir()
print("WITNESS executed validator SHA256=" + hashlib.sha256(Path(prepare_candidate.__file__).read_bytes()).hexdigest(), flush=True)
check_selection.main()
''', encoding='utf-8', newline='\n')
        command = [sys.executable, '-B', str(child), '--selection', str(SELECTION)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        (folder / 'stdout.txt').write_text(result.stdout, encoding='utf-8', newline='\n')
        (folder / 'stderr.txt').write_text(result.stderr, encoding='utf-8', newline='\n')
        assert 'WITNESS executed validator SHA256=' + sha(validator.read_bytes()) in result.stdout
        if name == 'enabled':
            assert result.returncode == 0, result.stderr
            assert 'FIRED selected runtime output binding:009' in result.stdout
            assert 'FIRED selected runtime output binding:010' in result.stdout
            assert (folder / 'output/negative-controls/selection.json').is_file()
        else:
            assert result.returncode == 1
            labels = [line for line in result.stderr.splitlines() if line.startswith('AssertionError:')]
            assert labels == ['AssertionError: same-canvas wrong-frame substitution SURVIVED:009'], result.stderr
            assert not (folder / 'output/negative-controls/selection.json').exists()
        records.append({'variant': name, 'result': 'PASS' if name == 'enabled' else 'FIRED',
            'exit_code': result.returncode, 'executed_validator_sha256': sha(validator.read_bytes()),
            'checker_sha256': sha((folder / 'check_selection.py').read_bytes()),
            'stdout_sha256': sha((folder / 'stdout.txt').read_bytes()),
            'stderr_sha256': sha((folder / 'stderr.txt').read_bytes()),
            'expected_failure': None if name == 'enabled' else 'same-canvas wrong-frame substitution SURVIVED:009'})
    assert before == sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    record = {'status': 'PASS', 'selection_sha256': sha(SELECTION.read_bytes()),
        'production_unchanged_sha256': before, 'records': records,
        'scope': 'Copied real checker and validator in fresh python -B processes. One assert condition replaced by True; valid same-size wrong-pose bytes then trigger exactly one named checker failure. No package or source mutation.'}
    (OUT / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
