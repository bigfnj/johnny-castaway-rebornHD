"""Build Web in the pinned SDK container; browser tests run separately on the host.

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


def inside(source, output):
    version = subprocess.run(['emcc', '--version'], check=True, text=True, capture_output=True).stdout
    print(version, end='', flush=True)
    verify_version(version)
    subprocess.run(['emcmake', 'cmake', '-S', str(source), '-B', str(output),
                    '-DCMAKE_BUILD_TYPE=Release'], check=True)
    subprocess.run(['cmake', '--build', str(output), '--parallel', str(min(8, os.cpu_count() or 2))], check=True)
    verify_artifacts(source, output)


def build(source, output, run=subprocess.run):
    source = source.resolve()
    relative = output.as_posix()
    if output.is_absolute() or '..' in output.parts or output == Path('.'):
        raise RuntimeError('tools/build_web.py: output must be a relative directory within source')
    acquire_image(run=run)
    command = ['docker', 'run', '--rm', '--mount', f'type=bind,source={source},target=/src',
               '--workdir', '/src']
    if hasattr(os, 'getuid'):
        command += ['--user', f'{os.getuid()}:{os.getgid()}']
    command += [SDK_IMAGE, 'python3', 'tools/build_web.py', '--inside', '--source', '/src',
                '--output', relative]
    # Do not retry compilation or convert its failure into an artifact check.
    run(command, check=True, timeout=1200)
    destination = source / output
    verify_artifacts(source, destination)
    for name in ('index.html', 'favicon.ico'):
        shutil.copyfile(source / name, destination / name)
    print(f'PASS tools/build_web.py: servable output in {destination}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path('build_web'))
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    options = parser.parse_args()
    try:
        if options.inside:
            inside(options.source.resolve(), options.source.resolve() / options.output)
        else:
            build(options.source, options.output)
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
