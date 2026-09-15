"""Executable negative controls for Docker acquisition/artifacts and Mac labels.

--mac-binary adds real lipo/clang checks on the macOS runner. Without it, the
architecture checks exercise command responses only and explicitly say so.
"""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / 'tools' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def rejected(operation, fragment):
    try:
        operation()
    except RuntimeError as exc:
        assert fragment in str(exc), f'tests/test_build_contracts.py: wrong failure: {exc}'
        return str(exc)
    owner = 'verify_macos_arch.py' if 'x86_64' in fragment else 'build_web.py'
    raise AssertionError(f'tools/{owner}: expected failure was not raised ({fragment})')


def mutant(module, needle, replacement):
    path = Path(module.__file__); source = path.read_text(encoding='utf-8')
    assert source.count(needle) == 1, f'{path.name}: expected one guarded condition'
    changed = source.replace(needle, replacement)
    result = ModuleType(module.__name__ + '_mutant'); result.__file__ = str(path)
    exec(compile(changed, str(path), 'exec'), result.__dict__)
    return result, hashlib.sha256(changed.encode()).hexdigest()


def fired(label, operation, digest):
    try:
        operation()
    except AssertionError as exc:
        assert 'expected failure was not raised' in str(exc), f'{label}: wrong mutant assertion: {exc}'
        print(f'FIRED 1/1 {label}: {exc}; executed source SHA256 {digest}')
    else:
        raise AssertionError(f'{label}: mutant survived')


def verify(work, mutations, mac_binary):
    web = load('build_web'); mac = load('verify_macos_arch')
    version = 'emcc (Emscripten gcc/clang-like replacement + linker emulating GNU ld) 6.0.9 (fixture)\n'
    web.verify_version(version)
    wrong_version = version.replace('6.0.9', '6.0.8')
    rejected(lambda: web.verify_version(wrong_version), 'expected emcc 6.0.9')
    source = work / 'source'; output = source / 'build_web'
    output.mkdir(parents=True); (source / 'assets').mkdir()
    (source / 'assets/scrantic_data.zip').write_bytes(b'archive-control')
    for name in ('jc_reborn.js', 'jc_reborn.wasm', 'jc_reborn.data'):
        (output / name).write_bytes(b'archive-control')
    web.verify_artifacts(source, output)
    for name in ('jc_reborn.js', 'jc_reborn.wasm', 'jc_reborn.data'):
        path = output / name; path.unlink()
        rejected(lambda: web.verify_artifacts(source, output), f'missing or empty {path}')
        path.write_bytes(b'')
        rejected(lambda: web.verify_artifacts(source, output), f'missing or empty {path}')
        path.write_bytes(b'archive-control')
    (output / 'jc_reborn.data').write_bytes(b'stale')
    rejected(lambda: web.verify_artifacts(source, output), f'stale {output / "jc_reborn.data"}')
    if mutations:
        bad, digest = mutant(web, 'if not actual or actual.group(1) != SDK_VERSION:', 'if False:')
        fired('tools/build_web.py version guard', lambda: rejected(lambda: bad.verify_version(wrong_version), 'expected emcc 6.0.9'), digest)
        bad, digest = mutant(web, 'if data_hash != archive_hash:', 'if False:')
        fired('tools/build_web.py archive guard', lambda: rejected(lambda: bad.verify_artifacts(source, output), 'stale'), digest)
        bad, digest = mutant(web, 'if not path.is_file() or path.stat().st_size == 0:', 'if False:')
        (output / 'jc_reborn.data').write_bytes(b'archive-control'); (output / 'jc_reborn.js').write_bytes(b'')
        fired('tools/build_web.py empty artifact guard', lambda: rejected(lambda: bad.verify_artifacts(source, output), 'missing or empty'), digest)
    for statuses in ([0], [1, 0], [1, 1, 0], [1, 1, 1], ['timeout', 1, 0]):
        calls = []; delays = []
        def pull(args, **kwargs):
            assert args == ['docker', 'pull', web.SDK_IMAGE], 'tools/build_web.py: retry escaped acquisition scope'
            status = statuses[len(calls)]; calls.append(args)
            if status == 'timeout': raise subprocess.TimeoutExpired(args, 600)
            return SimpleNamespace(returncode=status)
        if statuses[-1] == 0:
            web.acquire_image(pull, delays.append)
        else:
            rejected(lambda: web.acquire_image(pull, delays.append), 'acquisition failed after 3 attempts')
        assert len(calls) == len(statuses) and delays == [5, 10][:len(statuses)-1], 'tools/build_web.py: wrong acquisition retry count/order'
    calls = []
    for name in ('jc_reborn.js', 'jc_reborn.wasm', 'jc_reborn.data'):
        (output / name).write_bytes(b'archive-control')
    for name in ('index.html', 'favicon.ico'):
        (source / name).write_bytes(b'page-control')
    def failed_compile(args, **kwargs):
        calls.append(args)
        if args[1] == 'pull': return SimpleNamespace(returncode=0)
        if kwargs.get('check'): raise subprocess.CalledProcessError(37, args)
        return SimpleNamespace(returncode=37)
    def assert_compile_stops(module):
        calls.clear()
        try: module.build(source, Path('build_web'), failed_compile)
        except subprocess.CalledProcessError as exc: assert exc.returncode == 37
        else: raise AssertionError('tools/build_web.py: expected failure was not raised (compiler status 37)')
    assert_compile_stops(web)
    assert len(calls) == 2 and calls[1][:3] == ['docker', 'run', '--rm'], 'tools/build_web.py: compiler failure was retried'
    if mutations:
        bad, digest = mutant(web, 'run(command, check=True, timeout=1200)', 'run(command, check=False, timeout=1200)')
        fired('tools/build_web.py compiler status', lambda: assert_compile_stops(bad), digest)
        needle = "raise RuntimeError('tools/build_web.py: pinned SDK image acquisition failed after 3 attempts')"
        bad, digest = mutant(web, needle, 'return')
        fired('tools/build_web.py exhausted pull status', lambda: rejected(lambda: bad.acquire_image(lambda *a, **k: SimpleNamespace(returncode=1), lambda _: None), 'acquisition failed after 3 attempts'), digest)
    def assert_platform_stops(module):
        commands = []
        def fake_run(args, **kwargs):
            commands.append(args)
            if args == ['emcc', '--version']:
                return SimpleNamespace(stdout=version, returncode=0)
            assert args[0] == 'bash' and args[-2:] == ['--phase', 'smoke'], 'tools/build_web.py: probe-only mode rebuilt application or changed phase'
            if kwargs.get('check'): raise subprocess.CalledProcessError(47, args)
            return SimpleNamespace(returncode=47)
        with patch.object(module.subprocess, 'run', fake_run):
            try: module.inside(source, output, platform_phase='smoke', probes_only=True)
            except subprocess.CalledProcessError as exc: assert exc.returncode == 47
            else: raise AssertionError('tools/build_web.py: expected failure was not raised (platform smoke status 47)')
        assert len(commands) == 2, 'tools/build_web.py: platform failure was retried'
    assert_platform_stops(web)
    if mutations:
        bad, digest = mutant(web, 'env=env, check=True, timeout=180)', 'env=env, check=False, timeout=180)')
        fired('tools/build_web.py platform smoke status', lambda: assert_platform_stops(bad), digest)
    def fake_lipo(architecture):
        return lambda args, **kwargs: SimpleNamespace(stdout=architecture + '\n')
    mac.verify(Path('control'), fake_lipo('x86_64'))
    for arch in ('arm64', 'x86_64 arm64', ''):
        rejected(lambda: mac.verify(Path('wrong-arch'), fake_lipo(arch)), 'expected x86_64')
    if mutations:
        bad, digest = mutant(mac, "if architectures != ['x86_64']:", 'if False:')
        fired('tools/verify_macos_arch.py architecture guard', lambda: rejected(lambda: bad.verify(Path('wrong-arch'), fake_lipo('arm64')), 'expected x86_64'), digest)
    if mac_binary:
        mac.verify(mac_binary)
        c = work / 'wrong-architecture.c'; c.write_text('int main(void) { return 0; }\n', encoding='utf-8')
        wrong = work / 'wrong-architecture'
        subprocess.run(['clang', '-arch', 'arm64', str(c), '-o', str(wrong)], check=True)
        error = rejected(lambda: mac.verify(wrong), 'expected x86_64')
        print(f'FIRED 1/1 real Mach-O wrong-architecture fixture: {error}')
    else:
        print('INFO macOS architecture checks used command fixtures; real Mach-O/lipo/clang is UNTESTED here (use --mac-binary)')
    print('PASS build contracts: acquisition retries, compiler failure, artifacts/version, architecture controls')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutations', action='store_true'); parser.add_argument('--mac-binary', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='jcr-build-contracts-') as folder:
        verify(Path(folder), args.mutations, args.mac_binary)


if __name__ == '__main__': main()
