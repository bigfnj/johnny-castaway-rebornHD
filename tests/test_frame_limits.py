"""Actual CLI conversions and events.c stopping boundaries, without a display."""
import argparse
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
    parser.add_argument('--only')
    args = parser.parse_args()
    cases = []

    def cli(label, value, accepted):
        def check():
            run = subprocess.run([str(args.exe.resolve()), 'frames', value, 'version'],
                                 capture_output=True, text=True, timeout=10)
            output = run.stdout + run.stderr
            print(f'WITNESS frame CLI process value={value!r} exit={run.returncode}', flush=True)
            if accepted:
                assert run.returncode == 0 and 'Johnny Reborn ' in output, output
            else:
                assert run.returncode != 0 and f"Invalid frame count '{value}'" in output, output
                assert 'Johnny Reborn ' not in output and 'expected an integer from 1 to 4294967295' in output, output
        cases.append((label, check))

    def tick(label):
        def check():
            run = subprocess.run([str(args.probe.resolve()), label], capture_output=True,
                                 text=True, timeout=10)
            output = run.stdout + run.stderr
            assert f'WITNESS events.c frame {label} BEGIN' in output, output
            assert run.returncode == 0 and f'frame {label} PASS' in output, output
        cases.append((f'tick-{label}', check))

    cli('cli-ordinary', '13', True)
    tick('ordinary')
    if args.phase == 'regression' or args.only:
        for value in ['1', '2147483647', '2147483648', '4294967294', '4294967295', '+13', ' 13']:
            cli(f'cli-valid-{value.strip()}', value, True)
        for value in ['0', '-1', '', 'abc', '13x', '1.5', '4294967296',
                      '9223372036854775807', '9223372036854775808',
                      '18446744073709551616', '-9223372036854775809']:
            cli(f'cli-invalid-{value or "empty"}', value, False)
        tick('maximum')
        tick('unlimited')
    if args.only:
        cases = [case for case in cases if case[0] == args.only]
        if not cases: parser.error(f'unknown case: {args.only}')
    failures = 0
    for label, check in cases:
        print(f'WITNESS frame assertion {label} BEGIN', flush=True)
        try:
            check()
            print(f'PASS frame limits: {label}', flush=True)
        except (AssertionError, OSError, subprocess.SubprocessError) as exc:
            failures += 1
            print(f'FAIL tests/test_frame_limits.py:{label}: {exc}', flush=True)
    print(f'Frame {args.phase}: {len(cases) - failures}/{len(cases)} passed')
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
