"""Execute CI authoring and CI/release Web commands with command witnesses.

This checks GitHub bash step ordering/failure propagation. Actual compilation,
browser tests, authoring suites and platform probes run separately in those workflows.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ['platform-smoke', 'browser-smoke', 'logging-smoke', 'platform-regression',
            'audio-regression', 'logging-regression', 'selector-regression', 'build-regression']
AUTHORING = ['inventory-smoke', 'history-smoke', 'inventory-regression', 'history-regression']


def commands(source):
    # These maintained workflows use two-space job and eight-space run keys.
    body = source.split('\n  web:\n', 1)[1]
    body = re.split(r'\n  [A-Za-z][^\n]*:\n', body, maxsplit=1)[0]
    result = []
    for line in body.splitlines():
        text = line.strip()
        if text.startswith('run: '): text = text[5:]
        if re.match(r'python3? (?:-B )?(?:tools/build_web|tests/(?:web-smoke|web-logging|web-audio-timing|web-art-controls|test_build_contracts))\.py\b', text):
            result.append(text)
    return result


def authoring_commands(source, job):
    body = source.split('\n  ' + job + ':\n', 1)[1]
    body = re.split(r'\n  [A-Za-z][^\n]*:\n', body, maxsplit=1)[0]
    return [line.strip() for line in body.splitlines()
            if re.match(r'\s+python3 -B tests/test_art_(?:inventory|pilot_history)\.py(?:\s|$)', line)]


def execute(work, name, sequence, fail='none'):
    folder = work / name; folder.mkdir()
    driver = folder / 'python'
    driver.write_text('''#!/usr/bin/env python3
import os, sys
a = sys.argv[1:]
joined = ' '.join(a)
if 'test_art_inventory.py' in joined: stage = 'inventory-' + ('smoke' if '--smoke' in a else 'regression')
elif 'test_art_pilot_history.py' in joined: stage = 'history-' + a[a.index('--phase') + 1]
elif 'build_web.py' in joined: stage = 'platform-' + a[a.index('--platform-probes') + 1]
elif 'web-smoke.py' in joined: stage = 'browser-smoke'
elif 'web-logging.py' in joined: stage = 'logging-' + a[a.index('--phase') + 1]
elif 'web-audio-timing.py' in joined: stage = 'audio-regression'
elif 'web-art-controls.py' in joined: stage = 'selector-regression'
else: stage = 'build-regression'
with open(os.environ['JCR_WEB_TRACE'], 'a') as f: f.write(stage + '\\n')
if stage == os.environ['JCR_WEB_FAIL']:
    print('FAIL fixture ' + stage)
    sys.exit(43)
''', encoding='utf-8')
    # A fixed interpreter avoids resolving this same stub recursively.
    driver.write_text(driver.read_text().replace('#!/usr/bin/env python3', '#!' + sys.executable), encoding='utf-8')
    driver.chmod(0o755)
    (folder / 'python3').symlink_to(driver)
    script = folder / 'run.sh'; script.write_text('\n'.join(sequence) + '\n', encoding='utf-8')
    env = dict(os.environ, PATH=str(folder) + os.pathsep + os.environ['PATH'],
               JCR_WEB_TRACE=str(folder / 'trace.txt'), JCR_WEB_FAIL=fail)
    result = subprocess.run(['bash', '--noprofile', '--norc', '-e', '-o', 'pipefail', str(script)],
                            env=env, capture_output=True, timeout=15)
    text = (result.stdout + result.stderr).decode('utf-8', 'replace')
    trace = (folder / 'trace.txt').read_text().splitlines() if (folder / 'trace.txt').exists() else []
    (folder / 'run.log').write_text(text, encoding='utf-8')
    return result.returncode, text, trace


def oracle(path, fail, result, stages=EXPECTED, kind='Web'):
    code, text, trace = result
    print(f'WITNESS {path}: {fail} ordering assertion executed', flush=True)
    if fail == 'none':
        assert code == 0 and trace == stages, f'{path}: {kind} smoke/regression command order differs: {trace}'
    else:
        expected = stages[:stages.index(fail) + 1]
        assert code == 43 and text.count('FAIL fixture ' + fail) == 1 and trace == expected, f'{path}: {fail} failure reached later tests or lost its status'


def verify(work, mutations):
    records = []
    source = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
    for job in ('linux', 'macos', 'web'):
        path = '.github/workflows/ci.yml (' + job + ')'
        sequence = authoring_commands(source, job)
        for fail in ['none'] + AUTHORING:
            result = execute(work, 'authoring-' + job + '-' + fail, sequence, fail)
            oracle(path, fail, result, AUTHORING, 'authoring')
        if mutations:
            for index, stage in enumerate(AUTHORING):
                changed = sequence[:index] + sequence[index + 1:]
                result = execute(work, 'authoring-' + job + '-omit-' + stage, changed)
                assert result[0] == 0 and result[2] == AUTHORING[:index] + AUTHORING[index + 1:], (
                    f'{path}: omission mutant did not execute the remaining command witnesses')
                try: oracle(path, 'none', result, AUTHORING, 'authoring')
                except AssertionError as exc:
                    expected = f'{path}: authoring smoke/regression command order differs: {result[2]}'
                    assert str(exc) == expected, f'wrong authoring wiring mutation failure: {exc}'
                    records.append({'file': path, 'mutation': 'omitted-' + stage, 'result': 'FIRED',
                                    'failure': str(exc), 'trace': result[2]})
                    print(f'FIRED 1/1 {path}: omitted {stage}', flush=True)
                else: raise AssertionError(f'{path}: {stage} omission survived')
    for name in ('ci', 'release'):
        path = '.github/workflows/' + name + '.yml'
        source = (ROOT / path).read_text(encoding='utf-8')
        sequence = commands(source)
        for fail in ('none', 'platform-smoke', 'browser-smoke', 'logging-smoke', 'audio-regression', 'logging-regression'):
            result = execute(work, name + '-' + fail, sequence, fail)
            oracle(path, fail, result)
        if mutations:
            for stage, needle in [('logging-smoke', 'python tests/web-logging.py build_web --phase smoke'),
                                  ('audio-regression', 'python tests/web-audio-timing.py build_web')]:
                assert source.count(needle) == 1, f'{path}: expected one {needle}'
                changed = source.replace(needle, needle + ' || true')
                result = execute(work, name + '-mutant-' + stage, commands(changed), stage)
                assert result[2] == EXPECTED, f'{path}: mutant did not reach the later command witnesses'
                try: oracle(path, stage, result)
                except AssertionError as exc:
                    expected = f'{path}: {stage} failure reached later tests or lost its status'
                    assert str(exc) == expected, f'wrong workflow mutation failure: {exc}'
                    records.append({'file': path, 'mutation': stage, 'result': 'FIRED', 'failure': str(exc),
                                    'executed_source_sha256': hashlib.sha256(changed.encode()).hexdigest(), 'trace': result[2]})
                    print(f'FIRED 1/1 {exc}', flush=True)
                else: raise AssertionError(f'{path}: mutation survived')
    (work / 'report.json').write_text(json.dumps({'status': 'PASS', 'mutations': records}, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path); parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    if os.name == 'nt': parser.error('run under Linux/macOS bash, matching the Web CI runners')
    try:
        if args.work:
            work = args.work.resolve(); work.mkdir(parents=True, exist_ok=False); verify(work, args.mutations)
        else:
            with tempfile.TemporaryDirectory(prefix='jcr-web-flow-') as path: verify(Path(path), args.mutations)
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}'); return 1
    print('PASS Web and authoring workflow ordering; command fixtures run separately from actual suites')
    return 0


if __name__ == '__main__': raise SystemExit(main())
