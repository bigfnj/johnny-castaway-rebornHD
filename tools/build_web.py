"""Build Web with the pinned SDK container or an activated local SDK of that version.

The digest selects the official 6.0.9 multi-platform image, verified with emcc.
Only image acquisition is retried. A compiler or artifact failure ends the run.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

SDK_VERSION = '6.0.9'
SDK_IMAGE = 'emscripten/emsdk@sha256:96617f27fe16421588241def73908fd348a7f9d260440ed0d00b36dcf7a063cc'


def verify_version(output):
    actual = re.search(r'^emcc .*? (\d+\.\d+\.\d+)(?:\s|$)', output, re.MULTILINE)
    if not actual or actual.group(1) != SDK_VERSION:
        raise RuntimeError(f'tools/build_web.py: expected emcc {SDK_VERSION}, got {output.splitlines()[:1]}')
    print(f'WITNESS tools/build_web.py: emcc {actual.group(1)} verified', flush=True)


def verify_artifacts(source, output):
    for name in ('jc_reborn.js', 'jc_reborn.wasm', 'jc_reborn.data'):
        path = output / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f'tools/build_web.py: missing or empty {path}')
    # CMake preloads exactly one ZIP, so the .data payload is its exact bytes.
    archive_hash = hashlib.sha256((source / 'assets/scrantic_data.zip').read_bytes()).hexdigest()
    data_hash = hashlib.sha256((output / 'jc_reborn.data').read_bytes()).hexdigest()
    if data_hash != archive_hash:
        raise RuntimeError(f'tools/build_web.py: stale {output / "jc_reborn.data"}; source archive differs')
    print(f'WITNESS tools/build_web.py: artifacts verified; archive SHA256 {archive_hash}', flush=True)


def acquire_image(run=subprocess.run, sleep=time.sleep):
    for attempt in range(1, 4):
        print(f'Pulling pinned SDK image ({attempt}/3): {SDK_IMAGE}', flush=True)
        try:
            result = run(['docker', 'pull', SDK_IMAGE], timeout=600)
            if result.returncode == 0:
                return
        except subprocess.TimeoutExpired:
            print('Pinned SDK image pull timed out', flush=True)
        if attempt < 3:
            sleep(5 * attempt)
    raise RuntimeError('tools/build_web.py: pinned SDK image acquisition failed after 3 attempts')


def verify_cache(source, output):
    """Keep user caches intact; reject a native or differently mounted build tree."""
    cache = output / 'CMakeCache.txt'
    if not cache.exists():
        return
    fields = dict(re.findall(r'^([A-Za-z_][A-Za-z_0-9]*):[^=\r\n]+=([^\r\n]*)$', cache.read_text(encoding='utf-8'), re.MULTILINE))
    home = fields.get('CMAKE_HOME_DIRECTORY', '').replace('\\', '/').rstrip('/')
    toolchain = fields.get('CMAKE_TOOLCHAIN_FILE', '').replace('\\', '/')
    if home.casefold() != source.as_posix().rstrip('/').casefold() or not toolchain.endswith('/Emscripten.cmake'):
        raise RuntimeError(f'tools/build_web.py: incompatible {cache}; select a new output directory for this backend (cache preserved)')


def assemble_page(source, output):
    verify_artifacts(source, output)
    for name in ('index.html', 'favicon.ico'):
        shutil.copyfile(source / name, output / name)
    print(f'PASS tools/build_web.py: servable output in {output}', flush=True)


def inside(source, output, platform_phase=None, probes_only=False):
    version = subprocess.run(['emcc', '--version'], check=True, text=True, capture_output=True).stdout
    print(version, end='', flush=True)
    verify_version(version)
    if not probes_only:
        verify_cache(source, output)
        subprocess.run(['emcmake', 'cmake', '-S', str(source), '-B', str(output),
                        '-DCMAKE_BUILD_TYPE=Release'], check=True)
        subprocess.run(['cmake', '--build', str(output), '--parallel', str(min(8, os.cpu_count() or 2))], check=True)
        verify_artifacts(source, output)
    if platform_phase:
        env = dict(os.environ, SRC=str(source), OUT=str(source / 'build/platform-web-tests'))
        subprocess.run(['bash', str(source / 'tests/run_web_platform.sh'), '--phase', platform_phase],
                       env=env, check=True, timeout=180)


def build(source, output, run=subprocess.run, platform_phase=None, probes_only=False):
    source = source.resolve()
    destination = (source / output).resolve()
    if destination == source or not destination.is_relative_to(source):
        raise RuntimeError(f'tools/build_web.py: container output must be a directory within {source}: {destination}')
    relative = destination.relative_to(source).as_posix()
    acquire_image(run=run)
    command = ['docker', 'run', '--rm', '--mount', f'type=bind,source={source},target=/src',
               '--workdir', '/src']
    if hasattr(os, 'getuid'):
        command += ['--user', f'{os.getuid()}:{os.getgid()}']
    command += [SDK_IMAGE, 'python3', 'tools/build_web.py', '--inside', '--source', '/src',
                '--output', relative]
    if platform_phase:
        command += ['--platform-probes', platform_phase]
    if probes_only:
        command += ['--probes-only']
    # Do not retry compilation or convert its failure into an artifact check.
    run(command, check=True, timeout=1200)
    if not probes_only:
        assemble_page(source, destination)
    if platform_phase:
        print(f'PASS tools/build_web.py: platform {platform_phase} completed', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path('build_web'))
    parser.add_argument('--backend', choices=['container', 'local'], default='container',
                        help='Local requires an activated emsdk 6.0.9; the PowerShell wrapper activates EMSDK in a child shell')
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--platform-probes', choices=['smoke', 'regression'], help='Run real Web backend probes inside the SDK container')
    parser.add_argument('--probes-only', action='store_true', help='Run the requested backend phase without rebuilding the application')
    options = parser.parse_args()
    if options.probes_only and not options.platform_probes:
        parser.error('--probes-only requires --platform-probes')
    try:
        if options.inside:
            inside(options.source.resolve(), options.source.resolve() / options.output, options.platform_probes, options.probes_only)
        elif options.backend == 'local':
            source = options.source.resolve()
            output = (source / options.output).resolve()
            if output == source:
                raise RuntimeError(f'tools/build_web.py: output must differ from source: {output}')
            inside(source, output, options.platform_probes, options.probes_only)
            if not options.probes_only:
                assemble_page(source, output)
        else:
            build(options.source, options.output, platform_phase=options.platform_probes, probes_only=options.probes_only)
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
