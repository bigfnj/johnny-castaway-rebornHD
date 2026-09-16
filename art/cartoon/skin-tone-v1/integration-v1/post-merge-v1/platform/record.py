"""Record the completed main Windows gate and bounded fresh platform review."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'build/connecting-poses/windows-verification/connecting-main-v1'
EXPECTED_HEAD = '9ea8293f8efbd45a25717b4f8dd3bc5139586259'
BASE = '3af0242a74f234aab231d9203b48f78ca8e5c1b4'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def write(name, value):
    p = HERE / name
    assert not p.exists(), 'Existing audit record: ' + name
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    head = git('rev-parse', 'HEAD')
    assert head == EXPECTED_HEAD, 'Main HEAD changed during audit'
    result = read(RUN / 'result.json')
    assert result['passed'] and result['exit_code'] == 0, 'Full main gate failed'
    text = (RUN / 'gate.log').read_text(encoding='utf-8', errors='replace')
    stages = [line for line in text.splitlines() if line.startswith('=== ')]
    first_reg = next(i for i, line in enumerate(stages) if '=== regression (' in line)
    assert not any('smoke' in line for line in stages[first_reg:]), 'Smoke order changed'
    assert '2452 file(s) byte-identical to the golden corpus' in text
    for row in result['retained_captures']:
        assert row['complete_ppm'] and row['capture_marker'], row['path']
        assert sha(ROOT / row['path']) == row['ppm_sha256'], row['path']
        assert sha((ROOT / row['path']).with_suffix('.log')) == row['log_sha256']
    paths = ['src', 'platform', 'CMakeLists.txt', 'cmake', 'gate.ps1', '.github/workflows/ci.yml', 'tests', 'tools']
    diff = git('diff', BASE, head, '--', *paths)
    assert not diff, 'Runtime/build/maintained tooling changed relative to prior main'
    coverage = {
        'platform/platform.h': 'Full interface and ownership/yield/preview contract.',
        'platform/platform_windows.c': 'Raw input175-230; platform/window setup and teardown337-547; owned/borrowed surfaces704-762; audio refill, initialization and teardown1040-1295.',
        'platform/platform_linux.c': 'Display/window construction and destruction57-168; resize presentation238-277; owned/borrowed surfaces303-361; ALSA worker, setup, failure cleanup and close678-898.',
        'platform/platform_macos.m': 'CoreGraphics draw65-128; application/window/view ownership140-243; surface ownership280-323; AudioQueue setup/refill/teardown580-660.',
        'platform/platform_web.c': 'Application/window lifecycle68-124; cached presentation and heap-view lifetime195-252; surfaces262-319; unconditional yield558-582; audio allocation/pump/close597-753.',
        'platform/zipvfs.c': 'Full archive search/open/read/temp-file ownership and shutdown.',
        'platform/png_loader.c': 'Full WIC/portable decoder adapter, failure cleanup, premultiplied pixels and borrowed surface handoff.',
        'platform/png_decoder.c': 'Full chunk/decompression/filtering, size and allocation guards, failure cleanup and premultiplied BGRA conversion.',
        'src/engine/graphics.c': 'Relevant platform callsites: background/layer release60-86; capture and graphics teardown237-265; layer construction327-353; borrowed background/sprite ownership762-832.',
        'src/engine/sound.c': 'Callback shared state55-85; backend open and common teardown143-209.',
        'src/engine/events.c': 'Quit teardown, atexit registration and bounded-wait entry185-224.',
        'CMakeLists.txt': 'Compiler/platform/source/library selection, screensaver target, resource versioning, native runtime-data prerequisite and Web preload dependency.',
        'cmake/RuntimeData.cmake': 'Full always-run copy_if_different prerequisite and explicit executable dependency.',
        'gate.ps1': 'Verified byte-identical established full gate, executed against merged main; archive identity and ordered smoke/regression stages.',
        '.github/workflows/ci.yml': 'Previously inspected platform jobs unchanged by merge; current identity checked, no new CI execution claimed here.',
        'tools/build-macos.sh': 'Archive deployment callsite60 inspected; not a new complete direct-Clang audit.',
        'tools/build_web.py': 'Source archive hash/preload binding callsite inspected; not a new complete builder audit.',
    }
    known = [
        {'item': 'Windows foreground raw-input cleanup', 'source': 'platform/platform_windows.c:175',
         'backlog': 'BACKLOG.md:26', 'status': 'Existing WM_INPUT returns omit DefWindowProc; no new OS-resource leak measurement.'},
        {'item': 'Common audio state initialized after worker start', 'source': 'src/engine/sound.c:158',
         'backlog': 'BACKLOG.md:27', 'status': 'Existing currentRemaining assignment after backend open and zero-length NULL memcpy remain; no new audible/race measurement.'},
        {'item': 'Post-open audio failures', 'source': 'platform/platform_windows.c:1073',
         'related': 'platform/platform_macos.m:592; platform/platform_macos.m:654',
         'backlog': 'BACKLOG.md:40', 'status': 'Existing unchecked refill/enqueue/start results; initial construction cleanup is present. No physical-device failure injected.'},
        {'item': 'Full-frame presentation and flip cache optimization', 'source': 'platform/platform_web.c:237',
         'backlog': 'BACKLOG.md:47-48', 'status': 'Existing measurement-first opportunity. No new saving claimed.'},
        {'item': 'Physical desktop/audio coverage', 'source': 'platform/platform_linux.c:124',
         'backlog': 'BACKLOG.md:38-39', 'status': 'This Windows run and static read do not add Linux window-manager or macOS rendered-scene/physical-audio coverage.'},
        {'item': 'Capture marker diagnostic/retention', 'source': 'tests/test_palm_renderer.py',
         'backlog': 'BACKLOG.md:41-43', 'status': 'No recurrence in this main gate.32 captures and markers retained. Cause and automatic temporary failure-retention work remain open.'},
    ]
    copied = []
    for name in ('result.json', 'running.json', 'gate.log', 'adaptation.json', 'gate-adaptation.diff'):
        target = HERE / name
        assert not target.exists(), name
        shutil.copyfile(RUN / name, target)
        assert sha(target) == sha(RUN / name)
        copied.append({'path': target.relative_to(ROOT).as_posix(), 'source': (RUN / name).relative_to(ROOT).as_posix(), 'sha256': sha(target)})
    launcher = ROOT / 'build/connecting-poses/windows-verification/run_gate.py'
    record = {
        'schema_version': 1, 'status': 'PASS_WITH_EXISTING_BACKLOG', 'head': head, 'prior_main': BASE,
        'scope': 'Fresh bounded platform/adapter/build review plus full Windows deployment gate on merged main. No tracked source edits.',
        'source_diff_paths': paths, 'source_diff_empty': not diff,
        'inspected': [{'path': path, 'sha256': sha(ROOT / path), 'coverage': notes} for path, notes in coverage.items()],
        'new_actionable_findings': [], 'existing_backlog_confirmed': known,
        'intentional_or_nonleak_paths': [
            'SurfaceFrom borrows pixels consistently on all4 backends; engine explicitly frees decoded sprite/background pixels before the wrapper.',
            'Native frame-yield and non-Windows preview-parent setters intentionally do no work under the shared interface.',
            'Linux audio callback takes the common nonrecursive mutex itself; adding an outer callback lock would deadlock.',
            'Windows close deliberately leaves a driver-owned buffer allocated if unprepare fails; no new ordinary-run leak demonstrated.',
            'Portable PNG unsupported formats returnNULL for existing per-asset fallback; not a missing function.',
            'Web retained presentation buffer is one current-canvas cache; this audit makes no hot-restart or no-exit-runtime teardown claim.',
        ],
        'windows_gate': {
            'status': 'PASS', 'exit_code': result['exit_code'], 'elapsed_seconds': result['elapsed_seconds'],
            'source_archive_sha256': result['source_archive_sha256'], 'deployed_archive_sha256': result['deployed_archive_sha256'],
            'warning_free': 'OK   build clean, no warnings' in text,
            'ordered_smoke_then_regression': True, 'stages': stages,
            'golden_2452_byte_identical': True, 'retained_ppms': len(result['retained_captures']),
            'all_retained_ppms_and_markers_verified': True,
            'input_desktop_preserved': result['input_desktop_preserved'], 'poll_checks': result['poll_checks'],
            'observed_inactive_windows': len(result['observed_inactive_windows']),
            'protected_inputs_unchanged': result['protected_inputs_unchanged'],
            'explicit_skips': ['Inventory directory and file symlinks: WinError1314;9 of11 cases executed, including hardlink.'],
            'launcher_sha256': sha(launcher), 'result_sha256': sha(RUN / 'result.json'), 'log_sha256': sha(RUN / 'gate.log'),
            'capture_location': RUN.relative_to(ROOT).as_posix(),
            'binaries': {p.name: sha(p) for p in sorted((ROOT / 'build/Release').iterdir()) if p.suffix.lower() in ('.exe', '.scr')},
        },
        'exact_small_copies': copied,
        'limits': ['No new fault arose that justified extra probes or unchanged mutation reruns.',
                   'No sanitizer, physical-device failure, cross-platform native session or new performance experiment was run by this audit.',
                   'This is bounded review of listed regions, not proof that all paths are defect-free.',
                   'Full gate/captures retain the launcher fixed output location; compact copied logs and review record live here.',
                   'Core ADS/TTM/story semantics and complete art provenance are separate audit scopes.'],
    }
    write('audit.json', record)
    write('readback.json', {'status': 'PASS', 'audit_sha256': sha(HERE / 'audit.json'),
        'small_copies': len(copied), 'retained_ppms_checked': len(result['retained_captures']), 'head': head,
        'record_script_sha256': sha(Path(__file__))})
    print(json.dumps({'status': record['status'], 'head': head, 'audit_sha256': sha(HERE / 'audit.json'),
        'readback_sha256': sha(HERE / 'readback.json'), 'gate_seconds': result['elapsed_seconds']}, indent=2))


if __name__ == '__main__':
    main()
