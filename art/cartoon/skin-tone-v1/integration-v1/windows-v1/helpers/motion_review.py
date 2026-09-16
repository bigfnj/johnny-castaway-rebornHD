"""Isolated original/current/candidate native motion review; never promotes art.

Candidate inputs are six already-exported runtime PNGs named 024.png..029.png.
Omitting --candidate-sprites explicitly creates a current-as-candidate control.
"""
import argparse
import copy
import contextlib
import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
import zipfile

from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREFIX = 'data/styles/cartoon/'
FRAMES = range(24, 30)
WALK = [f'BMP/JOHNWALK.BMP/{n:03}.png' for n in FRAMES]
DRAW = re.compile(r'DRAW_SPRITE\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)')
WAIT = re.compile(r'WAIT: (\d+) ticks')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, label, message):
    if not condition:
        raise AssertionError(f'{label}: {message}')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def output_path(path):
    path = Path(path).resolve()
    check(path.is_relative_to(HERE) and path != HERE, path, 'output must be a child of the ignored review directory')
    return path


def protected_ok(plan):
    for path, expected in plan['protected'].items():
        check(sha(Path(path).read_bytes()) == expected, path, 'protected input changed')


def pack_hashes(path):
    with zipfile.ZipFile(path) as archive:
        check(len(archive.namelist()) == len(set(archive.namelist())), path, 'duplicate archive member')
        return {name: sha(archive.read(name)) for name in archive.namelist()}


def route_from_source(repo, metadata):
    text = (repo / 'src/data/walk_data.h').read_text()
    marker = text.index('// E to A')
    segment = text[text.rfind('\n', 0, marker) + 1:]
    route = []
    for match in re.finditer(r'\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}', segment):
        flip, x, y, frame = map(int, match.groups())
        if x == 0:
            break
        check(flip == 0, 'walk_data.h', 'unexpected E/A flip')
        route.append([x - 1, y, frame, 5])
    expected = [r['draw_logical_xy'] + [r['frame'], 5] for r in metadata['motion']['route']]
    check(route == expected and len(route) == 23, 'walk_data.h', 'route differs from maintained metadata')
    check(metadata['motion']['pose_ms'] == 120 and metadata['motion']['captured_review_ms'] == 3760,
          'cartoon-art-metadata.json', 'review timing differs')
    return route


def prepare(args):
    out = output_path(args.output)
    check(not out.exists(), out, 'refusing to overwrite an existing review')
    repo, archive, exe = args.repo.resolve(), args.archive.resolve(), args.exe.resolve()
    sys.path.insert(0, str(repo / 'tools'))
    from art_common import inspect_png
    from art_pack import build_archive
    pack = read(repo / 'art/cartoon/pack.json')
    metadata = read(repo / 'docs/knowledge-base/cartoon-art-metadata.json')
    original = read(repo / 'docs/knowledge-base/cartoon-original-reference.json')
    identities = read(repo / 'docs/knowledge-base/original-extractor-reference.json')
    check(original['input_sha256'] == {r['name']: r['original_sha256'] for r in identities['source_resources']},
          'cartoon-original-reference.json', 'original source provenance differs')
    route = route_from_source(repo, metadata)
    override_record = read(repo / 'art/cartoon/island-pilot-v1/review-evidence/diagnostic-archive-overrides.json')
    template = args.diagnostic_template.resolve()
    overrides = {}
    with zipfile.ZipFile(template) as donor, zipfile.ZipFile(archive) as base:
        for item in override_record['diagnostic_candidate']['changed_members_only']:
            name = item['name']
            check(sha(base.read(name)) == item['normal_sha256'], name, 'base resource differs from reviewed diagnostic source')
            overrides[name] = donor.read(name)
            check(sha(overrides[name]) == item['diagnostic_sha256'], name, 'diagnostic resource hash differs')
        check(overrides['data/RESOURCE.001'].startswith(base.read('data/RESOURCE.001')),
              'data/RESOURCE.001', 'diagnostic must preserve complete normal resource prefix')
        current = {r['path']: base.read(PREFIX + r['path']) for r in pack['assets']}
        check(len(current) == 21, 'pack.json', 'expected 21 approved assets')
        for row in pack['assets']:
            check(sha(current[row['path']]) == row['sha256'], row['path'], 'current runtime PNG differs from approved pack')
    all_sprites = {'current': current, 'candidate': dict(current), 'original': dict(current)}
    protected = {str(p): sha(p.read_bytes()) for p in (archive, exe, template,
        repo / 'docs/knowledge-base/cartoon-art-metadata.json', repo / 'art/cartoon/pack.json')}
    for n, key in zip(FRAMES, WALK):
        native_path = HERE / f'{n:03}-original-native.png'
        native_bytes = native_path.read_bytes()
        protected[str(native_path)] = sha(native_bytes)
        facts = original['assets'][key]
        with Image.open(io.BytesIO(native_bytes)) as native:
            check(native.mode == 'RGBA' and list(native.size) == facts['canvas'], native_path.name, 'native canvas/mode differs')
            check(sha(native.tobytes()) == facts['rgba_sha256'], native_path.name, 'native original RGBA hash differs')
            doubled = native.resize((native.width * 2, native.height * 2), Image.Resampling.NEAREST)
            rows = []
            data = native.tobytes()
            for y in range(native.height):
                row = data[y * native.width * 4:(y + 1) * native.width * 4]
                rows.append(b''.join(row[x * 4:x * 4 + 4] * 2 for x in range(native.width)) * 2)
            check(doubled.tobytes() == b''.join(rows), native_path.name, 'native 2x pixel repeats differ')
            buffer = io.BytesIO()
            doubled.save(buffer, format='PNG')
            all_sprites['original'][key] = buffer.getvalue()
        if args.candidate_sprites:
            path = args.candidate_sprites.resolve() / f'{n:03}.png'
            all_sprites['candidate'][key] = path.read_bytes()
            protected[str(path)] = sha(path.read_bytes())
        expected = tuple(v * 2 for v in facts['canvas'])
        for label in all_sprites:
            info = inspect_png(all_sprites[label][key], f'{label}/{key}', expected)
            check(info['color_type'] in (4, 6), f'{label}/{key}', 'sprite needs explicit alpha')
    if args.candidate_sprites:
        check({p.name for p in args.candidate_sprites.glob('*.png')} == {f'{n:03}.png' for n in FRAMES},
              str(args.candidate_sprites), 'candidate directory must contain exactly 024.png through 029.png')
    out.mkdir(parents=True)
    plan = {'status': 'PREPARED', 'repo': str(repo), 'route': route, 'pose_ms': 120,
            'endpoint_ms': 3760, 'setup_control': not bool(args.candidate_sprites), 'protected': protected,
            'normal_source_sha256': sha(archive.read_bytes()), 'exe_source': str(exe), 'exe_sha256': sha(exe.read_bytes()),
            'helper_sha256': sha(Path(__file__).read_bytes()), 'packs': {}, 'canvases': {str(n): [v * 2 for v in original['assets'][key]['canvas']] for n, key in zip(FRAMES, WALK)},
            'scope': 'Original column uses supplied original resource pixels at exact2x, port dump palette and BMP index0 transparency, rendered by current engine. Not original executable palette/compositing/timing parity. All panels retain identical approved Cartoon island art. E/A positions are hosted in temporary MJREAD110; endpoint hold/reset is diagnostic. No runtime promotion.'}
    for label, sprites in all_sprites.items():
        folder = out / label
        folder.mkdir()
        normal = folder / 'normal.zip'
        built = build_archive(archive, normal, pack['runtime'], sprites)
        check(built['original_members_preserved'] == 2550, label, 'original corpus member count differs')
        diagnostic = folder / 'scrantic_data.zip'
        with zipfile.ZipFile(normal) as source, zipfile.ZipFile(diagnostic, 'x') as target:
            for item in source.infolist():
                target.writestr(copy.copy(item), overrides.get(item.filename, source.read(item.filename)))
        names = pack_hashes(normal)
        changed = [name for name, digest in pack_hashes(diagnostic).items() if digest != names[name]]
        check(sorted(changed) == sorted(overrides), label, 'unexpected diagnostic member changes')
        shutil.copyfile(exe, folder / 'jc_reborn.exe')
        (folder / 'profile').mkdir()
        plan['packs'][label] = {'normal_sha256': sha(normal.read_bytes()), 'diagnostic_sha256': sha(diagnostic.read_bytes()),
                                'style_members': {key: sha(value) for key, value in sprites.items()}, 'original_members_preserved': 2550}
    unchanged = [key for key in current if key not in WALK]
    check(all(all_sprites['original'][k] == current[k] == all_sprites['candidate'][k] for k in unchanged),
          'island assets', 'one of 15 shared island assets changed')
    protected_ok(plan)
    write(out / 'plan.json', plan)
    print(f'PASS prepare: 3 isolated21-asset packs; 2550 originals each; source preserved; setup_control={plan["setup_control"]}', flush=True)


class OffscreenDesktop:
    """Own an inactive desktop without changing the user's input desktop."""
    def __enter__(self):
        check(os.name == 'nt', 'native capture', 'this helper currently requires Windows')
        self.user = ctypes.WinDLL('user32', use_last_error=True)
        self.user.CreateDesktopW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
        self.user.CreateDesktopW.restype = wintypes.HANDLE
        self.user.CloseDesktop.argtypes = [wintypes.HANDLE]
        self.user.GetForegroundWindow.restype = wintypes.HWND
        self.user.GetThreadDesktop.argtypes = [wintypes.DWORD]
        self.user.GetThreadDesktop.restype = wintypes.HANDLE
        self.user.SetThreadDesktop.argtypes = [wintypes.HANDLE]
        self.user.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.user.OpenInputDesktop.restype = wintypes.HANDLE
        self.user.GetUserObjectInformationW.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        self.user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.user.EnumDesktopWindows.argtypes = [wintypes.HANDLE, self.callback_type, wintypes.LPARAM]
        self.name = 'JohnnyPoseReview_' + uuid.uuid4().hex
        self.original_thread_desktop = self.user.GetThreadDesktop(ctypes.WinDLL('kernel32').GetCurrentThreadId())
        self.original_input_name = self.input_name()
        self.handle = self.user.CreateDesktopW(self.name, None, None, 0, 0x01ff, None)
        check(bool(self.handle), 'inactive desktop', f'CreateDesktopW failed {ctypes.get_last_error()}')
        # CreateDesktop assigns the new desktop to its caller. Restore only this
        # helper thread so foreground checks observe the original input desktop.
        # Neither operation switches the user's input desktop.
        check(bool(self.user.SetThreadDesktop(self.original_thread_desktop)), 'inactive desktop', 'restore helper thread desktop failed')
        check(self.input_name() == self.original_input_name != self.name, 'inactive desktop', 'input desktop changed')
        return self

    def input_name(self):
        handle = self.user.OpenInputDesktop(0, False, 1)
        check(bool(handle), 'inactive desktop', 'cannot inspect input desktop')
        try:
            name = ctypes.create_unicode_buffer(256)
            needed = wintypes.DWORD()
            check(bool(self.user.GetUserObjectInformationW(handle, 2, name, ctypes.sizeof(name), ctypes.byref(needed))),
                  'inactive desktop', 'cannot read input desktop name')
            return name.value
        finally:
            self.user.CloseDesktop(handle)

    def observe(self, pid):
        found = []
        @self.callback_type
        def visit(hwnd, param):
            owner = wintypes.DWORD()
            self.user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == pid:
                found.append(int(hwnd))
            return True
        self.user.EnumDesktopWindows(self.handle, visit, 0)
        check(self.input_name() == self.original_input_name != self.name, 'inactive desktop', 'input desktop changed during capture')
        foreground_owner = wintypes.DWORD()
        self.user.GetWindowThreadProcessId(self.user.GetForegroundWindow(), ctypes.byref(foreground_owner))
        check(foreground_owner.value != pid, 'inactive desktop', 'capture process became foreground on caller desktop')
        return found

    def __exit__(self, *exc):
        check(bool(self.user.CloseDesktop(self.handle)), 'inactive desktop', 'CloseDesktop failed')


class NativeProcess:
    """CreateProcessW is required: subprocess.STARTUPINFO omits lpDesktop."""
    def __init__(self, command, directory, env, stream, desktop):
        import msvcrt
        class StartupInfo(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('lpReserved', wintypes.LPWSTR), ('lpDesktop', wintypes.LPWSTR),
                        ('lpTitle', wintypes.LPWSTR), ('dwX', wintypes.DWORD), ('dwY', wintypes.DWORD),
                        ('dwXSize', wintypes.DWORD), ('dwYSize', wintypes.DWORD), ('dwXCountChars', wintypes.DWORD),
                        ('dwYCountChars', wintypes.DWORD), ('dwFillAttribute', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                        ('wShowWindow', wintypes.WORD), ('cbReserved2', wintypes.WORD), ('lpReserved2', ctypes.c_void_p),
                        ('hStdInput', wintypes.HANDLE), ('hStdOutput', wintypes.HANDLE), ('hStdError', wintypes.HANDLE)]
        class ProcessInfo(ctypes.Structure):
            _fields_ = [('hProcess', wintypes.HANDLE), ('hThread', wintypes.HANDLE),
                        ('dwProcessId', wintypes.DWORD), ('dwThreadId', wintypes.DWORD)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateProcessW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
            wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(StartupInfo), ctypes.POINTER(ProcessInfo)]
        self.kernel.CreateProcessW.restype = wintypes.BOOL
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        self.kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.GetCurrentProcess.restype = wintypes.HANDLE
        self.kernel.DuplicateHandle.argtypes = [wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE,
                                               ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.returncode = None
        info, startup = ProcessInfo(), StartupInfo()
        startup.cb = ctypes.sizeof(startup)
        startup.lpDesktop = 'winsta0\\' + desktop
        startup.dwFlags = 0x100  # STARTF_USESTDHANDLES
        output_handle = msvcrt.get_osfhandle(stream.fileno())
        stderr_handle = wintypes.HANDLE()
        own_process = self.kernel.GetCurrentProcess()
        check(bool(self.kernel.DuplicateHandle(own_process, output_handle, own_process, ctypes.byref(stderr_handle), 0, True, 2)),
              'CreateProcessW', 'duplicate stderr handle failed')
        with open(os.devnull, 'rb') as stdin:
            input_handle = msvcrt.get_osfhandle(stdin.fileno())
            os.set_handle_inheritable(output_handle, True)
            os.set_handle_inheritable(input_handle, True)
            startup.hStdInput = input_handle
            # Separate inheritable handles share one file cursor. Giving the
            # CRT exactly the same handle for two streams permits closing one
            # stream to invalidate the other's still-buffered output.
            startup.hStdOutput = output_handle
            startup.hStdError = stderr_handle.value
            environment = ctypes.create_unicode_buffer('\0'.join(f'{k}={v}' for k, v in sorted(env.items(), key=lambda row: row[0].upper())) + '\0\0')
            argv = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
            try:
                okay = self.kernel.CreateProcessW(None, argv, None, None, True, 0x08000400,
                    environment, str(directory), ctypes.byref(startup), ctypes.byref(info))
                error = ctypes.get_last_error()
            finally:
                os.set_handle_inheritable(output_handle, False)
                os.set_handle_inheritable(input_handle, False)
                self.kernel.CloseHandle(stderr_handle)
        check(bool(okay), 'CreateProcessW', f'failed with error{error}')
        self.handle, self.pid = info.hProcess, info.dwProcessId
        self.kernel.CloseHandle(info.hThread)

    def poll(self):
        if self.returncode is None and self.kernel.WaitForSingleObject(self.handle, 0) == 0:
            code = wintypes.DWORD()
            check(bool(self.kernel.GetExitCodeProcess(self.handle, ctypes.byref(code))), 'native process', 'exit-code read failed')
            self.returncode = code.value
        return self.returncode

    def kill(self):
        self.kernel.TerminateProcess(self.handle, 1460)

    def wait(self):
        self.kernel.WaitForSingleObject(self.handle, 10000)
        return self.poll()

    def close(self):
        self.kernel.CloseHandle(self.handle)


def native_run(plan, folder, budget, desktop, prefix='display'):
    exe = folder / 'jc_reborn.exe'
    check(sha(exe.read_bytes()) == plan['exe_sha256'], str(exe), 'runner executable differs')
    canonical_png = folder / f'{prefix}-{budget:03}.png'
    attempt = 1
    attempt_prefix = prefix
    while (folder / f'{attempt_prefix}-{budget:03}.log').exists():
        attempt += 1
        attempt_prefix = f'{prefix}-attempt{attempt}'
    ppm = folder / f'{attempt_prefix}-{budget:03}.ppm'
    log = folder / f'{attempt_prefix}-{budget:03}.log'
    env = os.environ.copy()
    env['HOME'] = env['USERPROFILE'] = str(folder / 'profile')
    command = [str(exe), 'window', 'nosound', 'hotkeys', 'debug', 'maxspeed', 'day', 'holiday', 'none',
               'seed', '9', 'island', 'ads', 'ACTIVITY.ADS', '7', 'style', 'cartoon', 'frames', str(budget), 'capture', str(ppm)]
    observed = set()
    began = time.monotonic()
    with log.open('wb') as stream:
        process = NativeProcess(command, folder, env, stream, desktop.name)
        try:
            while process.poll() is None:
                observed.update(desktop.observe(process.pid))
                if time.monotonic() - began > 40:
                    process.kill()
                    process.wait()
                    break
                time.sleep(.01)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.close()
    text = log.read_text(encoding='utf-8', errors='replace')
    check(process.returncode == 0 and f'stopping after {budget} frame(s)' in text and 'Captured frame:' in text,
          log.name, f'native exit={process.returncode}; expected bounded capture markers\n{text[-1500:]}')
    check(bool(observed), log.name, 'no owned window observed on the inactive desktop')
    draws = [list(map(int, match.groups())) for match in DRAW.finditer(text)]
    loaded = sorted(set(re.findall(r'Art asset: data/styles/cartoon/BMP/JOHNWALK\.BMP/(\d{3})\.png', text)))
    check(loaded == [f'{n:03}' for n in FRAMES], log.name, 'all six reviewed sprite paths must load')
    with Image.open(ppm) as image:
        check(image.size == (1280, 960), ppm.name, 'native frame dimensions differ')
        image = image.convert('RGB')
        if canonical_png.exists():
            with Image.open(canonical_png) as prior:
                check(prior.convert('RGB').tobytes() == image.tobytes(), canonical_png.name, 'repeated native capture pixels differ')
        else:
            image.save(canonical_png)
    record = {'budget': budget, 'draws': draws, 'last_draw': draws[-1] if draws else None,
            'time_ms': 20 * sum(map(int, WAIT.findall(text))), 'bg_updates': len(re.findall(r'------> Animate bg', text)),
            'png': canonical_png.name, 'png_sha256': sha(canonical_png.read_bytes()), 'attempt': attempt,
            'log': log.name, 'log_sha256': sha(log.read_bytes()), 'exit_code': process.returncode,
            'inactive_desktop_window_count': len(observed), 'loaded_walk': loaded,
            'exe_sha256': plan['exe_sha256'], 'diagnostic_sha256': sha((folder / 'scrantic_data.zip').read_bytes())}
    write(folder / f'{prefix}-{budget:03}.record.json', record)
    return record


def smoke(args):
    out = output_path(args.output)
    plan = read(out / 'plan.json')
    protected_ok(plan)
    check(not (out / 'smoke.json').exists(), out, 'existing smoke report preserved')
    report = {'status': 'PASS', 'plan_sha256': sha((out / 'plan.json').read_bytes()), 'runs': {},
              'mode': 'unchanged windowed native executable on temporary inactive desktop; no SwitchDesktop call'}
    with contextlib.nullcontext():
        for label in ('original', 'current', 'candidate'):
            with OffscreenDesktop() as desktop:
                record = native_run(plan, out / label, 1, desktop, 'smoke')
            check(record['draws'] == plan['route'][:1], f'{label}/smoke', 'first diagnostic draw differs')
            report['runs'][label] = record
            print(f'PASS smoke {label}: six paths, first route pose, bounded capture, inactive desktop window', flush=True)
    protected_ok(plan)
    write(out / 'smoke.json', report)


def assert_timeline(records, plan, label):
    expected = sorted(set(range(0, 2761, 120)) | set(range(160, 3760, 160)))
    check([r['time_ms'] for r in records] == expected, label, '42 display schedule differs')
    for i, record in enumerate(records):
        end = records[i + 1]['time_ms'] if i + 1 < len(records) else 3760
        check(end > record['time_ms'], label, 'non-positive display interval')
        position = min(record['time_ms'] // 120, 22)
        check(record['last_draw'] == plan['route'][position], label, 'intervening pose differs')
        check(record['draws'] == plan['route'][:len(record['draws'])], label, 'draw history differs')
        record.update(duration_ms=end - record['time_ms'], pose=position)


def outside_difference(a, b, draw, canvas, label):
    difference = ImageChops.difference(a, b)
    total = difference.getbbox() is not None
    x, y = (v * 2 for v in draw[:2])
    difference.paste((0, 0, 0), (x, y, x + canvas[0], y + canvas[1]))
    check(difference.getbbox() is None, label, 'pixels changed outside the placed sprite canvas')
    return total


def capture(args):
    out = output_path(args.output)
    plan = read(out / 'plan.json')
    smoke_report = read(out / 'smoke.json')
    check(smoke_report['status'] == 'PASS' and smoke_report['plan_sha256'] == sha((out / 'plan.json').read_bytes()),
          'smoke.json', 'matching smoke must pass before capture regression')
    check(not (out / 'capture-report.json').exists(), out, 'existing captures preserved')
    protected_ok(plan)
    report = {'status': 'PASS', 'plan_sha256': sha((out / 'plan.json').read_bytes()), 'captures': {}, 'setup_control': plan['setup_control']}
    with contextlib.nullcontext():
        for label in ('original', 'current', 'candidate'):
            records = []
            for budget in range(1, 80):
                cached = out / label / f'display-{budget:03}.record.json'
                if cached.exists():
                    record = read(cached)
                    check(record['exe_sha256'] == plan['exe_sha256'] and record['diagnostic_sha256'] == plan['packs'][label]['diagnostic_sha256'],
                          cached.name, 'cached capture inputs differ')
                    for key in ('png', 'log'):
                        check(sha((out / label / record[key]).read_bytes()) == record[key + '_sha256'], cached.name, 'cached capture evidence changed')
                else:
                    with OffscreenDesktop() as desktop:
                        record = native_run(plan, out / label, budget, desktop)
                if record['time_ms'] >= 3760:
                    check(record['time_ms'] == 3760, label, 'endpoint witness differs')
                    write(out / label / 'endpoint.json', record)
                    break
                if budget == 1:
                    text = (out / label / record['log']).read_text(encoding='utf-8')
                    tail = text.split('******* WAIT:', 1)[1]
                    check(record['time_ms'] == 80 and not any(t in tail for t in ('DRAW_', 'Animate bg', 'Animate clouds', 'CLEAR_', 'LOAD_')),
                          label, 'initial display alias changed composed layers')
                    record['time_ms'] = 0
                records.append(record)
                if budget == 1 or budget % 10 == 0:
                    print(f'Captured {label} display{budget} at {record["time_ms"]}ms', flush=True)
            else:
                check(False, label, 'endpoint not reached within bounded display count')
            assert_timeline(records, plan, label)
            report['captures'][label] = records
            print(f'PASS {label}:42 displays,23 positions,3760ms timeline', flush=True)
    reference = report['captures']['current']
    differences = {'original': [], 'candidate': []}
    for label in differences:
        rows = report['captures'][label]
        check([(r['time_ms'], r['last_draw'], r['bg_updates']) for r in rows] ==
              [(r['time_ms'], r['last_draw'], r['bg_updates']) for r in reference], label, 'cross-panel timeline differs')
        for baseline, row in zip(reference, rows):
            with Image.open(out / 'current' / baseline['png']) as a, Image.open(out / label / row['png']) as b:
                differences[label].append(outside_difference(a.convert('RGB'), b.convert('RGB'), row['last_draw'],
                    plan['canvases'][str(row['last_draw'][2])], f'{label}/{row["png"]}'))
                if label == 'candidate' and plan['setup_control']:
                    check(a.tobytes() == b.tobytes(), row['png'], 'current-as-candidate pixels differ')
    check(all(differences['original']), 'original control', 'original sprite must visibly differ on every captured display')
    report['comparison'] = {'original_visible_differences': sum(differences['original']),
                            'candidate_visible_differences': sum(differences['candidate']), 'outside_sprite_pixels_changed': 0,
                            'current_as_candidate_exact': plan['setup_control']}
    protected_ok(plan)
    write(out / 'capture-report.json', report)


def regression(args):
    out = output_path(args.output)
    plan = read(out / 'plan.json')
    capture_report = read(out / 'capture-report.json')
    check(capture_report['status'] == 'PASS' and capture_report['plan_sha256'] == sha((out / 'plan.json').read_bytes()),
          'capture-report.json', 'complete matching capture smoke is required')
    protected_ok(plan)
    archive = Path(next(p for p in plan['protected'] if p.endswith('assets\\scrantic_data.zip') or p.endswith('assets/scrantic_data.zip')))
    baseline = pack_hashes(archive)
    preserved = [name for name in baseline if not name.startswith(PREFIX)]
    check(len(preserved) == 2550, 'normal archive', 'expected2550 original members')
    for label in ('original', 'current', 'candidate'):
        hashes = pack_hashes(out / label / 'normal.zip')
        check(set(hashes) == set(baseline), label, 'normal archive member names differ')
        for name in preserved:
            check(hashes[name] == baseline[name], name, 'normal original member differs')
        check(sha((out / label / 'normal.zip').read_bytes()) == plan['packs'][label]['normal_sha256'], label, 'normal pack changed')
        check(sha((out / label / 'scrantic_data.zip').read_bytes()) == plan['packs'][label]['diagnostic_sha256'], label, 'diagnostic pack changed')
    golden = out / 'golden'
    check(not golden.exists(), golden, 'existing golden evidence preserved')
    golden.mkdir()
    shutil.copyfile(Path(plan['exe_source']), golden / 'jc_reborn.exe')
    shutil.copyfile(out / 'candidate/normal.zip', golden / 'scrantic_data.zip')
    (golden / 'profile').mkdir()
    env = {k: v for k, v in os.environ.items() if k.upper() != 'PSMODULEPATH'}
    env['PSModulePath'] = str(Path(env['SYSTEMROOT']) / 'System32/WindowsPowerShell/v1.0/Modules')
    env['HOME'] = env['USERPROFILE'] = str(golden / 'profile')
    command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
               str(Path(plan['repo']) / 'tests/Invoke-DumpRegression.ps1'), '-Exe', str(golden / 'jc_reborn.exe')]
    result = subprocess.run(command, cwd=golden, env=env, capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    text = result.stdout.decode('utf-8', 'replace') + result.stderr.decode('utf-8', 'replace')
    (golden / 'regression.log').write_text(text, encoding='utf-8')
    check(result.returncode == 0 and '2452 file(s) byte-identical' in text, 'golden/regression.log', f'exit{result.returncode}\n{text[-1500:]}')
    protected_ok(plan)
    write(out / 'regression.json', {'status': 'PASS', 'original_members_per_pack': 2550, 'normal_candidate_golden': 2452,
                                   'capture_report_sha256': sha((out / 'capture-report.json').read_bytes()), 'exe_sha256': plan['exe_sha256'],
                                   'scope': 'Capture smoke then archive/render comparisons and normal-candidate golden. Diagnostic resource overrides are not compared to the normal golden.'})
    print('PASS regression:3×2550 original member hashes, normal candidate2452 golden files', flush=True)


def viewer(args):
    out = output_path(args.output)
    plan = read(out / 'plan.json')
    report = read(out / 'capture-report.json')
    regression_report = read(out / 'regression.json')
    check(regression_report['status'] == 'PASS' and regression_report['capture_report_sha256'] == sha((out / 'capture-report.json').read_bytes()),
          'regression.json', 'matching regression required before viewer')
    columns = [('original', 'Original resource pixels'), ('current', 'Current Cartoon'), ('candidate', 'Candidate (setup control)' if plan['setup_control'] else 'Candidate Cartoon')]
    for label, _ in columns:
        folder = out / label / 'crops'
        folder.mkdir(exist_ok=True)
        for row in report['captures'][label]:
            with Image.open(out / label / row['png']) as image:
                crop = image.crop((560, 380, 880, 660))
                crop.save(folder / row['png'])
                with Image.open(folder / row['png']) as check_image:
                    check(check_image.tobytes() == crop.tobytes(), row['png'], 'crop pixels differ')
    rows = report['captures']['current']
    data = {'columns': columns, 'frames': [{'png': row['png'], 'time': row['time_ms'], 'duration': row['duration_ms'],
             'pose': row['pose'], 'draw': row['last_draw']} for row in rows], 'setup': plan['setup_control'], 'scope': plan['scope']}
    template = (HERE / 'motion_review.html').read_text(encoding='utf-8')
    check(template.count('__DATA__') == 1, 'motion_review.html', 'template placeholder differs')
    (out / 'review.html').write_text(template.replace('__DATA__', json.dumps(data)), encoding='utf-8')
    print(f'PASS viewer generated: {out / "review.html"}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--repo', type=Path, default=REPO)
    p.add_argument('--archive', type=Path, default=REPO / 'assets/scrantic_data.zip')
    p.add_argument('--exe', type=Path, required=True)
    p.add_argument('--candidate-sprites', type=Path)
    p.add_argument('--diagnostic-template', type=Path, default=Path('D:/.ai-work/worktrees/johnny-cartoon-art/build/art-work/walk-pilot/extended-native-ea-hd.zip'))
    p.add_argument('--output', type=Path, required=True)
    for mode in ('smoke', 'capture', 'regression', 'viewer'):
        p = sub.add_parser(mode)
        p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        globals()[args.mode](args)
    except Exception as exc:
        print(f'FAIL {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
