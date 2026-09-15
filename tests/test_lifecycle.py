"""Verify real compiled engine ownership using allocator tracking, without GUI."""
import argparse
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
    parser.add_argument('--only')
    options = parser.parse_args()
    checks = ['scene-release', 'graphics-release']
    if options.phase == 'regression' or options.only:
        checks += ['benchmark-release', 'standalone-saved-zone', 'reinitialize']
    if options.only:
        if options.only not in checks: parser.error(f'unknown check {options.only}')
        checks = [options.only]
    failures = 0
    for name in checks:
        print(f'WITNESS lifecycle assertion executed: {name}', flush=True)
        try:
            run = subprocess.run([str(options.exe.resolve()), name], capture_output=True, timeout=30)
            text = (run.stdout + run.stderr).decode('utf-8', 'replace')
            assert f'WITNESS production lifecycle executed: {name}' in text, text
            assert run.returncode == 0 and f'RESULT {name} allocations=' in text and 'live=0 bytes=0' in text, text
            print(f'PASS {name}')
        except (AssertionError, OSError, subprocess.SubprocessError) as error:
            failures += 1
            print(f'FAIL tests/test_lifecycle.py:{name}: {error}')
    print(f'Lifecycle {options.phase}: {len(checks) - failures}/{len(checks)} passed')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
