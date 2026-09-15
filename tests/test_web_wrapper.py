"""Actual PowerShell 5.1/7 wrapper tests with a recording builder and SDK fixture.

These test delegation, quoting, failure propagation and parent environment, not
compilation. A real pinned SDK build and browser checks remain separate gates.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def psquote(value):
    return "'" + str(value).replace("'", "''") + "'"


def run_case(work, shell, label, *, local=False, status=0, relative=False, mutation=None):
    case = work / (shell + '-' + label); case.mkdir()
    source = case / 'source with spaces'; (source / 'scripts').mkdir(parents=True)
    (source / 'tools').mkdir()
    for name in ('build_web.ps1', 'build_web_local.ps1'):
        content = (ROOT / 'scripts' / name).read_text(encoding='utf-8-sig')
        if mutation and name == mutation[0]:
            assert content.count(mutation[1]) == 1, f'scripts/{name}: mutation target is not unique'
            content = content.replace(mutation[1], mutation[2])
        (source / 'scripts' / name).write_text(content, encoding='utf-8-sig')
    record = case / 'record.json'
    (source / 'tools/build_web.py').write_text(
        'import json, os, pathlib, sys\n'
        f'pathlib.Path({str(record)!r}).write_text(json.dumps(dict(args=sys.argv[1:], marker=os.environ.get("JCR_SDK_MARKER"), config=os.environ.get("EM_CONFIG"))), encoding="utf-8")\n'
        f'sys.exit({status})\n', encoding='utf-8')
    sdk = case / 'SDK with spaces'; sdk.mkdir()
    (sdk / 'emsdk_env.ps1').write_text(
        "$env:JCR_SDK_MARKER = 'activated'\n$env:EM_CONFIG = 'child-config'\n"
        "$env:PATH = $env:PATH + ';child-only'\nSet-Location $PSScriptRoot\n", encoding='utf-8-sig')
    output = Path('relative output') if relative else case / 'external output'
    wrapper = source / 'scripts/build_web.ps1'
    harness = case / 'run.ps1'
    harness.write_text(
        "$ErrorActionPreference = 'Stop'\n"
        "$before = @($env:PATH, $env:EM_CONFIG, (Get-Location).Path)\n"
        f"& {psquote(wrapper)} -Python {psquote(sys.executable)}\n"
        "if ($before[0] -cne $env:PATH -or $before[1] -cne $env:EM_CONFIG -or $before[2] -cne (Get-Location).Path) { throw 'scripts/build_web.ps1: caller environment or location changed' }\n"
        "Write-Output 'WITNESS scripts/build_web.ps1: caller environment assertion executed'\n", encoding='utf-8-sig')
    env = {k: v for k, v in os.environ.items() if k.lower() not in ('psmodulepath', 'emsdk', 'jcr_build_dir', 'jcr_sdk_marker')}
    env['JCR_BUILD_DIR'] = str(output)
    if local: env['EMSDK'] = str(sdk)
    command = [shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File']
    command += [str(wrapper), '-Python', sys.executable] if status else [str(harness)]
    result = subprocess.run(command, cwd=case, env=env, capture_output=True, timeout=45)
    text = (result.stdout + result.stderr).decode('utf-8', 'replace')
    (case / 'run.log').write_text(text, encoding='utf-8')
    assert record.exists(), f'scripts/build_web.ps1: {label}: builder was not reached: {text}'
    data = json.loads(record.read_text(encoding='utf-8'))
    print(f'WITNESS scripts/build_web.ps1: {label} delegation/exit assertion executed', flush=True)
    assert result.returncode == status, f'scripts/build_web.ps1: {label}: expected exit {status}, got {result.returncode}: {text}'
    assert data['args'] == ['--backend', 'local' if local else 'container', '--output', str((case / output).resolve())], f'scripts/build_web.ps1: {label}: backend/output arguments changed: {data}'
    assert data['marker'] == ('activated' if local else None), f'scripts/build_web_local.ps1: {label}: SDK activation changed'
    if status == 0:
        assert 'caller environment assertion executed' in text, f'scripts/build_web.ps1: {label}: parent state assertion not reached'
    return text


def verify(work, phase, mutations):
    for shell in ('powershell.exe', 'pwsh'):
        if phase == 'smoke':
            run_case(work, shell, 'container')
            run_case(work, shell, 'local', local=True)
        else:
            run_case(work, shell, 'relative', local=True, relative=True)
            run_case(work, shell, 'container-failure', status=37)
            run_case(work, shell, 'local-failure', local=True, status=37)
            if mutations:
                for name, local in (('build_web.ps1', False), ('build_web_local.ps1', True)):
                    change = (name, 'if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }', '# status propagation disabled')
                    try:
                        run_case(work, shell, 'mutant-' + name, local=local, status=37, mutation=change)
                    except AssertionError as exc:
                        assert 'expected exit 37, got 0' in str(exc), f'wrong mutation failure: {exc}'
                        executed = work / (shell + '-mutant-' + name) / 'source with spaces/scripts' / name
                        print(f'FIRED 1/1 scripts/{name}: {exc}; executed source SHA256 {hashlib.sha256(executed.read_bytes()).hexdigest()}')
                    else: raise AssertionError(f'scripts/{name}: mutation survived')
    print('INFO wrapper uses recording builder/SDK fixtures; real SDK compilation is a separate required build')
    print(f'PASS PowerShell wrapper {phase}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
    parser.add_argument('--mutations', action='store_true')
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if os.name != 'nt': parser.error('requires Windows PowerShell 5.1 and PowerShell 7')
    if args.work:
        work = args.work.resolve(); work.mkdir(parents=True, exist_ok=False)
    else:
        parent = ROOT / 'build/maintenance-wrapper'; parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(dir=parent))
    print(f'Wrapper evidence: {work}')
    try: verify(work, args.phase, args.mutations)
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}'); return 1
    return 0


if __name__ == '__main__': raise SystemExit(main())
