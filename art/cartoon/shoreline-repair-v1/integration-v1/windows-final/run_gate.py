"""Run the existing Windows gate with explicit retained palm/wave work paths.

Only the copied gate's root assignment and four existing --work options differ.
The proven inactive-desktop launcher is reused without modifying its source.
"""
import argparse
import ctypes
from ctypes import wintypes
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

import psutil

ROOT = Path(__file__).resolve().parents[5]
HELPER = ROOT / 'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def snapshot():
    result = {p.relative_to(ROOT).as_posix(): sha(p)
              for name in ('src', 'platform', 'tests', 'tools', 'third_party', 'assets')
              for p in sorted((ROOT / name).rglob('*'))
              if p.is_file() and '__pycache__' not in p.parts}
    for name in ('gate.ps1', 'CMakeLists.txt'):
        result[name] = sha(ROOT / name)
    return result


def adapt_gate(output):
    original = ROOT / 'gate.ps1'
    text = original.read_bytes().decode('utf-8')
    source = text
    root_line = '$repo  = $PSScriptRoot'
    assert text.count(root_line) == 1, 'gate root assignment differs'
    text = text.replace(root_line, "$repo  = '" + str(ROOT).replace("'", "''") + "'")
    paths = []
    for family, binary in (('wave', '--exe $exe'), ('palm', '--driver $palmDriver')):
        base = f"& python -B (Join-Path $repo 'tests\\test_{family}_renderer.py') {binary} --archive $sourceZip"
        for phase in ('smoke', 'regression'):
            suffix = ' --phase smoke' if phase == 'smoke' else ''
            old = base + suffix + '\r\n'
            assert text.count(old) == 1, f'{family}/{phase} command differs'
            work = output / f'{family}-{phase}'
            assert not work.exists(), f'{family}/{phase} work already exists'
            paths.append(work.relative_to(ROOT).as_posix())
            new = base + suffix + " --work '" + str(work).replace("'", "''") + "'\r\n"
            text = text.replace(old, new)
    script = output / 'gate-retained.ps1'
    script.write_bytes(text.encode('utf-8'))
    diff = ''.join(difflib.unified_diff(source.splitlines(keepends=True), text.splitlines(keepends=True),
                                      fromfile='gate.ps1', tofile='gate-retained.ps1'))
    (output / 'gate-adaptation.diff').write_bytes(diff.encode('utf-8'))
    save(output / 'adaptation.json', {
        'original_gate_sha256': sha(original), 'adapted_gate_sha256': sha(script),
        'diff_sha256': sha(output / 'gate-adaptation.diff'), 'retained_work_paths': paths,
        'changes': 'Repository root assignment and four explicit existing --work options only. '
                   'No test assertions, ordering, build flags or runtime sources changed.'})
    return script


def captures(output):
    result = []
    for folder in ('wave-smoke', 'wave-regression', 'palm-smoke', 'palm-regression'):
        for p in sorted((output / folder).rglob('*.ppm')):
            data = p.read_bytes()
            match = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n', data)
            dimensions = list(map(int, match.groups())) if match else None
            payload = len(data) - match.end() if match else 0
            log = p.with_suffix('.log')
            native = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
            result.append({'path': p.relative_to(ROOT).as_posix(), 'ppm_sha256': sha(p),
                           'dimensions': dimensions, 'payload_bytes': payload,
                           'complete_ppm': dimensions == [1280, 960] and payload == 1280 * 960 * 3,
                           'log_sha256': sha(log) if log.exists() else None,
                           'capture_marker': f'Captured frame: {p}' in native})
    return result


def main():
    global ROOT, HELPER
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-sha256', required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    HELPER = ROOT / 'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py'
    assert re.fullmatch(r'[a-z0-9-]+', args.label), 'label must be a simple directory name'
    assert sha(ROOT / 'assets/scrantic_data.zip') == args.zip_sha256, 'archive-ready-identity'
    output = ROOT / 'build/seasonal-final-windows' / args.label
    output.mkdir(parents=True, exist_ok=False)
    script = adapt_gate(output)
    before = snapshot()
    spec = importlib.util.spec_from_file_location('existing_inactive_desktop', HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    environment = {k: v for k, v in os.environ.items() if k.casefold() != 'psmodulepath'}
    environment['PATH'] = str(Path(sys.executable).parent) + os.pathsep + environment.get('PATH', '')
    (output / 'temp').mkdir()
    environment['TEMP'] = environment['TMP'] = str(output / 'temp')
    command = ['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(script)]
    log = output / 'gate.log'
    seen, windows, checks = set(), {}, 0
    started = time.time()
    with module.OffscreenDesktop() as desktop:
        with log.open('wb') as stream:
            process = module.NativeProcess(command, ROOT, environment, stream, desktop.name)
            save(output / 'running.json', {
                'command': command, 'pid': process.pid, 'desktop': desktop.name,
                'original_input_desktop': desktop.original_input_name, 'archive_sha256': args.zip_sha256,
                'helper_sha256': sha(HELPER), 'launcher_sha256': sha(Path(__file__)),
                'protected_sha256': before, 'started_epoch': started})
            print(f'RUN retained Windows gate PID {process.pid} on inactive desktop {desktop.name}; log {log}', flush=True)
            try:
                while process.poll() is None:
                    try:
                        children = psutil.Process(process.pid).children(recursive=True)
                    except psutil.NoSuchProcess:
                        children = []
                    seen.update(child.pid for child in children)
                    seen.add(process.pid)
                    desktop.observe(process.pid)
                    owner = wintypes.DWORD()
                    desktop.user.GetWindowThreadProcessId(desktop.user.GetForegroundWindow(), ctypes.byref(owner))
                    assert owner.value not in seen, 'gate-child-became-foreground'
                    @desktop.callback_type
                    def visit(hwnd, _):
                        pid = wintypes.DWORD()
                        desktop.user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                        if pid.value in seen:
                            windows[str(int(hwnd))] = pid.value
                        return True
                    desktop.user.EnumDesktopWindows(desktop.handle, visit, 0)
                    checks += 1
                    if time.time() - started > 3600:
                        raise TimeoutError('Windows gate exceeded one hour')
                    time.sleep(.5)
            finally:
                if process.poll() is None:
                    for child in reversed(psutil.Process(process.pid).children(recursive=True)):
                        try:
                            child.kill()
                        except psutil.NoSuchProcess:
                            pass
                    process.kill()
                    process.wait()
                code = process.poll()
                process.close()
        desktop.observe(process.pid)
        input_preserved = desktop.input_name() == desktop.original_input_name
    after = snapshot()
    text = log.read_text(encoding='utf-8', errors='replace')
    changed = [n for n in sorted(before.keys() | after.keys()) if before.get(n) != after.get(n)]
    runtime = ROOT / 'build/Release/scrantic_data.zip'
    deployed_sha = sha(runtime) if runtime.exists() else None
    rows = captures(output)
    passed = (code == 0 and 'gate passed' in text and not changed and bool(windows)
              and input_preserved and deployed_sha == args.zip_sha256)
    result = {
        'passed': passed, 'exit_code': code, 'elapsed_seconds': round(time.time() - started, 3),
        'log_sha256': sha(log), 'source_archive_sha256': args.zip_sha256,
        'deployed_archive_sha256': deployed_sha, 'input_desktop_preserved': input_preserved,
        'poll_checks': checks, 'observed_inactive_windows': windows,
        'protected_inputs_unchanged': not changed, 'changed_inputs': changed,
        'retained_captures': rows,
        'module_path_policy': 'Remove inherited PSModulePath case-insensitively.',
        'scope': 'Existing full gate with explicit retained palm/wave work directories; no assertion/order changes.'}
    save(output / 'result.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('observed_inactive_windows', 'retained_captures')}, indent=2), flush=True)
    print(f'Retained {len(rows)} PPMs; observed {len(windows)} inactive windows.', flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
