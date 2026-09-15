"""Require the architecture advertised by the macOS release filename."""
import argparse
from pathlib import Path
import subprocess
import sys


def verify(binary, run=subprocess.run):
    result = run(['lipo', '-archs', str(binary)], check=True, text=True, capture_output=True)
    architectures = result.stdout.split()
    print(f'WITNESS tools/verify_macos_arch.py: {binary}: {architectures}', flush=True)
    if architectures != ['x86_64']:
        raise RuntimeError(f'tools/verify_macos_arch.py: {binary}: expected x86_64, got {architectures}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    args = parser.parse_args()
    try:
        verify(args.binary)
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
