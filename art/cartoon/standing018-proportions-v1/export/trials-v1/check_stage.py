"""Bounded staging-only input and guard-removal checks in fresh fake repositories."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'art/cartoon/standing018-proportions-v1/export/stage.py'
RAW = ROOT / 'art/cartoon/standing018-proportions-v1/018-torso-v2.png'
sha = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location('stager', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
code = SOURCE.read_text()
cases = {'wrong-raw-identity': 'source-identity:018', 'changed-exporter': 'frozen-input:export.py',
         'changed-reference': 'frozen-input:reference/source.json', 'changed-legacy': 'frozen-legacy-export',
         'occupied-output': 'staging-already-exists', 'outside-build': 'staging-outside-build',
         'wrong-source-extension': 'source-path'}


def remove_guard(label):
    nodes = [n for n in ast.walk(ast.parse(code)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == 'require' and ((isinstance(n.args[-1], ast.Constant) and n.args[-1].value == label)
             or (label.startswith('frozen-input:') and isinstance(n.args[-1], ast.BinOp)
                 and isinstance(n.args[-1].left, ast.Constant) and n.args[-1].left.value == 'frozen-input:'))]
    assert len(nodes) == 1
    node = nodes[0].args[0]
    lines = code.splitlines(keepends=True)
    lo = sum(map(len, lines[:node.lineno-1])) + node.col_offset
    hi = sum(map(len, lines[:node.end_lineno-1])) + node.end_col_offset
    return code[:lo] + 'True' + code[hi:]


def run_case(name, changed):
    with tempfile.TemporaryDirectory(prefix='stage-probe-', dir=ROOT/'build/standing018-proportions') as temp:
        fake = Path(temp)
        script = fake / SOURCE.relative_to(ROOT)
        script.parent.mkdir(parents=True)
        script.write_text(changed, encoding='utf-8', newline='\n')
        for relative in module.PINS:
            destination = fake / module.PRIOR.relative_to(ROOT) / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((module.PRIOR / relative).read_bytes())
        legacy = fake / module.LEGACY
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes((ROOT/module.LEGACY).read_bytes())
        raw = fake / RAW.relative_to(ROOT)
        raw.write_bytes(RAW.read_bytes())
        work = fake / 'build/new-stage'
        expected = sha(raw.read_bytes())
        if name == 'wrong-raw-identity': expected = '0' * 64
        if name == 'changed-exporter':
            p = fake/module.PRIOR.relative_to(ROOT)/'export.py'
            p.write_bytes(p.read_bytes() + b'\n')
        if name == 'changed-reference':
            p = fake/module.PRIOR.relative_to(ROOT)/'reference/source.json'
            p.write_bytes(p.read_bytes() + b'\n')
        if name == 'changed-legacy': legacy.write_bytes(legacy.read_bytes() + b'\n')
        if name == 'occupied-output': work.mkdir(parents=True)
        if name == 'outside-build': work = fake / 'not-build'
        if name == 'wrong-source-extension':
            raw = raw.with_suffix('.dat')
            raw.write_bytes(RAW.read_bytes())
        result = subprocess.run([sys.executable, '-B', str(script), '--source', str(raw),
            '--source-sha256', expected, '--work', str(work)], capture_output=True, text=True)
        digest = sha(script.read_bytes())
        assert 'WITNESS stage.py SHA256=' + digest in result.stdout
        return {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
                'executed_source_sha256': digest}


records = []
positive = run_case('positive', code)
assert positive['exit_code'] == 0
for name, label in cases.items():
    normal = run_case(name, code)
    assert normal['exit_code'] == 1 and normal['stderr'].strip() == 'FAIL ' + label, name
    altered = run_case(name, remove_guard(label))
    assert altered['exit_code'] == 0, name + ': removed guard did not reach the corrupted staging'
    # One changed expectation per control: its exact input refusal is absent.
    records.append({'case': name, 'expected_failure': label, 'normal': normal, 'mutant': altered,
                    'result': 'FIRED', 'failed_expectations': 1})
positive_after = run_case('positive', code)
assert positive_after['exit_code'] == 0
for relative, expected in module.PINS.items():
    assert sha((module.PRIOR / relative).read_bytes()) == expected
report = {'status': 'PASS', 'scope': 'Staging adapter only; no image rendering or anatomy validation.',
          'adapter_sha256': sha(SOURCE.read_bytes()), 'probe_sha256': sha(Path(__file__).read_bytes()),
          'positive_before': positive, 'positive_after': positive_after, 'controls': records,
          'historical_inputs_unchanged': True}
target = ROOT/'build/standing018-proportions/staging-validation-v1.json'
assert not target.exists()
target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
print('PASS staging positive before/after;7 named input refusals and7 executed guard removals detected')
