"""Run the actual Unix build script with isolated build/smoke/dump witnesses.

The failing-build fixture still produces runnable binaries, proving that file
existence cannot stand in for the build exit status. No compiler is mocked in
the separate runtime-data or real Unix build checks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tests/unix-build.sh'
LINUX = sys.platform != 'darwin'

def executable(path,text):
    path.write_text(text,encoding='utf-8'); path.chmod(0o755)

def run_case(work,source,mode,name):
    folder=work/name; folder.mkdir(); src=folder/'source'; src.mkdir()
    (src/'tests').mkdir(); commands=folder/'bin'; commands.mkdir()
    script=folder/'unix-build.sh'
    # Keep the actual command/control flow; isolate its fixed scratch paths.
    source=source.replace('/tmp/build.log',str(folder/'build.log')).replace('/tmp/dump.log',str(folder/'dump.log')).replace('/tmp/jcr-run',str(folder/'run')).replace('/tmp/unix-dump.sha256',str(folder/'unix-dump.sha256'))
    script.write_text(source,encoding='utf-8')
    (src/'tests/golden-dump.sha256').write_text(hashlib.sha256(b'fixture\n').hexdigest()+'  file.txt\n',encoding='utf-8')
    (src/'tests/test_uncompress.py').write_text('''import os, sys
phase = 'smoke' if '--phase' in sys.argv else 'regression'
with open(os.environ['JCR_TRACE'], 'a') as stream: stream.write('WITNESS decoder-' + phase + '\\n')
if os.environ['JCR_CASE'] == 'decoder-' + phase + '-fail':
    print('FAIL tests/test_uncompress.py: fixture rejected')
    sys.exit(32 if phase == 'smoke' else 34)
''',encoding='utf-8')
    (src/'tests/test_frame_limits.py').write_text('''import argparse, os, sys
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--exe', required=True, type=Path)
parser.add_argument('--probe', required=True, type=Path)
parser.add_argument('--phase', choices=['smoke', 'regression'], default='regression')
args = parser.parse_args()
expected = Path(__file__).resolve().parents[1] / 'build-unix'
assert args.exe.resolve() == expected / 'jc_reborn' and args.exe.is_file(), 'tests/test_frame_limits.py: wrong engine path'
assert args.probe.resolve() == expected / 'jc_frame_test' and args.probe.is_file(), 'tests/test_frame_limits.py: wrong probe path'
with open(os.environ['JCR_TRACE'], 'a') as stream: stream.write('WITNESS frame-' + args.phase + '\\n')
if os.environ['JCR_CASE'] == 'frame-' + args.phase + '-fail':
    print('FAIL tests/test_frame_limits.py: fixture rejected')
    sys.exit(39 if args.phase == 'smoke' else 40)
''',encoding='utf-8')
    (src/'tests/test_extractors.py').write_text('''import argparse, os, sys
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('--sound', required=True, type=Path)
parser.add_argument('--walk', required=True, type=Path)
parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)
args = parser.parse_args()
expected = Path(__file__).resolve().parents[1] / 'build-unix'
assert args.sound.resolve() == expected / 'extract_sound' and args.sound.is_file(), 'tests/test_extractors.py: wrong sound path'
assert args.walk.resolve() == expected / 'extract_walk_data' and args.walk.is_file(), 'tests/test_extractors.py: wrong walk path'
with open(os.environ['JCR_TRACE'], 'a') as stream: stream.write('WITNESS extractor-' + args.phase + '\\n')
if os.environ['JCR_CASE'] == 'extractor-' + args.phase + '-fail':
    print('FAIL tests/test_extractors.py: fixture rejected')
    sys.exit(41 if args.phase == 'smoke' else 42)
''',encoding='utf-8')
    (src/'tests/test_graphics_alloc.py').write_text('''import os, sys
with open(os.environ['JCR_TRACE'], 'a') as stream: stream.write('WITNESS graphics-regression\\n')
if os.environ['JCR_CASE'] == 'graphics-regression-fail':
    print('FAIL tests/test_graphics_alloc.py: fixture rejected')
    sys.exit(36)
''',encoding='utf-8')
    (src/'tests/test_drawing_bounds.py').write_text('''import os, sys
phase = sys.argv[sys.argv.index('--phase') + 1]
with open(os.environ['JCR_TRACE'], 'a') as stream: stream.write('WITNESS drawing-' + phase + '\\n')
if os.environ['JCR_CASE'] == 'drawing-' + phase + '-fail':
    print('FAIL tests/test_drawing_bounds.py: fixture rejected')
    sys.exit(37 if phase == 'smoke' else 38)
''',encoding='utf-8')
    platform_fixture = '''#!/usr/bin/env bash
phase="$2"
echo "WITNESS platform-$phase" >> "$JCR_TRACE"
if [ "$JCR_CASE" = "platform-$phase-fail" ]; then
    echo 'FAIL tests/run_linux_platform.sh: fixture rejected'
    if [ "$phase" = smoke ]; then exit 33; else exit 35; fi
fi
'''
    executable(src/'tests/run_linux_platform.sh',platform_fixture)
    executable(src/'tests/run_macos_platform.sh',platform_fixture)
    executable(src/'fixture-png','''#!/usr/bin/env bash
echo "WITNESS png-smoke" >> "$JCR_TRACE"
if [ "$JCR_CASE" = smoke-fail ]; then echo 'FAIL tests/test_png_decoder.c: fixture rejected'; exit 31; fi
''')
    executable(src/'fixture-main','''#!/usr/bin/env bash
echo "WITNESS dump-regression" >> "$JCR_TRACE"
mkdir -p dump
printf 'fixture\n' > dump/file.txt
''')
    executable(commands/'cmake','''#!/usr/bin/env bash
if [ "$1" = --version ]; then echo 'cmake fixture'; exit 0; fi
if [ "$1" = --build ]; then
  echo "WITNESS build-executed" >> "$JCR_TRACE"
  mkdir -p build-unix
  cp fixture-main build-unix/jc_reborn
  cp fixture-png build-unix/jc_png_test
  cp fixture-png build-unix/jc_frame_test
  cp fixture-png build-unix/extract_sound
  cp fixture-png build-unix/extract_walk_data
  if [ "$JCR_CASE" = build-fail ]; then echo 'error: deliberate extra ALL target failure'; exit 23; fi
  if [ "$JCR_CASE" = warning ]; then echo 'warning: successful fixture build'; fi
fi
exit 0
''')
    executable(commands/'cc',"#!/usr/bin/env bash\necho 'cc fixture'\n")
    executable(commands/'xvfb-run',"#!/usr/bin/env bash\nexit 0\n")
    env=dict(os.environ,PATH=str(commands)+os.pathsep+os.environ['PATH'],SRC=str(src),WORK=str(folder/'copied-source'),JCR_CASE=mode,JCR_TRACE=str(folder/'witness.log'))
    proc=subprocess.run(['bash',str(script)],env=env,capture_output=True,timeout=30)
    text=(proc.stdout+proc.stderr).decode('utf-8','replace'); (folder/'run.log').write_text(text,encoding='utf-8')
    trace=(folder/'witness.log').read_text()
    return proc.returncode,text,trace,folder

def assert_case(mode, code, text, trace):
    full_trace = ['WITNESS build-executed', 'WITNESS png-smoke', 'WITNESS decoder-smoke', 'WITNESS frame-smoke', 'WITNESS extractor-smoke', 'WITNESS platform-smoke']
    if LINUX: full_trace.append('WITNESS drawing-smoke')
    full_trace.extend(['WITNESS decoder-regression', 'WITNESS frame-regression', 'WITNESS extractor-regression', 'WITNESS platform-regression'])
    if LINUX: full_trace.extend(['WITNESS graphics-regression', 'WITNESS drawing-regression'])
    full_trace.append('WITNESS dump-regression')
    if mode in ('clean', 'warning'):
        assert code == 0 and trace.splitlines() == full_trace, f'tests/unix-build.sh: {mode} control did not reach smoke then regression'
    elif mode == 'build-fail':
        assert code == 23 and text.count('FAIL tests/unix-build.sh: CMake build failed') == 1 and trace.splitlines() == ['WITNESS build-executed'], 'tests/unix-build.sh: failed build reached smoke/regression or lost its diagnostic/status'
    elif mode == 'smoke-fail':
        assert code == 31 and text.count('FAIL tests/test_png_decoder.c: fixture rejected') == 1 and trace.splitlines() == ['WITNESS build-executed', 'WITNESS png-smoke'], 'tests/unix-build.sh: failed PNG smoke reached regression'
    else:
        cases = {'decoder-smoke-fail': (32, 'decoder-smoke', 'tests/test_uncompress.py'), 'platform-smoke-fail': (33, 'platform-smoke', 'tests/run_linux_platform.sh'),
                 'decoder-regression-fail': (34, 'decoder-regression', 'tests/test_uncompress.py'), 'platform-regression-fail': (35, 'platform-regression', 'tests/run_linux_platform.sh'),
                 'graphics-regression-fail': (36, 'graphics-regression', 'tests/test_graphics_alloc.py'),
                 'drawing-smoke-fail': (37, 'drawing-smoke', 'tests/test_drawing_bounds.py'),
                 'drawing-regression-fail': (38, 'drawing-regression', 'tests/test_drawing_bounds.py'),
                 'frame-smoke-fail': (39, 'frame-smoke', 'tests/test_frame_limits.py'),
                 'frame-regression-fail': (40, 'frame-regression', 'tests/test_frame_limits.py'),
                 'extractor-smoke-fail': (41, 'extractor-smoke', 'tests/test_extractors.py'),
                 'extractor-regression-fail': (42, 'extractor-regression', 'tests/test_extractors.py')}
        status, stage, file = cases[mode]
        length = full_trace.index('WITNESS ' + stage) + 1
        assert code == status and text.count(f'FAIL {file}: fixture rejected') == 1 and trace.splitlines() == full_trace[:length], f'tests/unix-build.sh: {mode} reached later regression or lost its diagnostic/status'


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--work',type=Path); parser.add_argument('--mutations',action='store_true'); args=parser.parse_args()
    original=SCRIPT.read_text(encoding='utf-8')
    def verify(work):
        records=[]
        modes = ['clean','warning','build-fail','smoke-fail','decoder-smoke-fail','frame-smoke-fail','extractor-smoke-fail','platform-smoke-fail','decoder-regression-fail','frame-regression-fail','extractor-regression-fail','platform-regression-fail']
        if LINUX: modes.extend(['graphics-regression-fail', 'drawing-smoke-fail', 'drawing-regression-fail'])
        for mode in modes:
            code,text,trace,folder=run_case(work,original,mode,mode)
            assert_case(mode, code, text, trace)
            records.append({'case':mode,'status':code,'trace':trace.splitlines()})
            print(f'PASS tests/unix-build.sh: {mode}',flush=True)
        if args.mutations:
            needle='    exit "$build_status"'
            assert original.count(needle)==1, 'tests/unix-build.sh: expected one build short-circuit'
            mutant=original.replace(needle,'    : # disabled build-failure exit')
            code,text,trace,folder=run_case(work,mutant,'build-fail','mutant')
            assert code==0 and 'WITNESS dump-regression' in trace and text.count('FAIL tests/unix-build.sh: CMake build failed')==1, 'tests/unix-build.sh: mutation did not execute the bad continuation'
            try:
                assert_case('build-fail', code, text, trace)
            except AssertionError as exc:
                assert str(exc) == 'tests/unix-build.sh: failed build reached smoke/regression or lost its diagnostic/status', f'Wrong mutation failure: {exc}'
                records.append({'mutation':'disabled build failure exit','result':'FIRED','named_failure':str(exc),'executed_trace':trace.splitlines(),'mutant_script_sha256':hashlib.sha256((folder/'unix-build.sh').read_bytes()).hexdigest()})
                print(f'FIRED 1/1 {exc}',flush=True)
            else:
                raise AssertionError('tests/unix-build.sh: disabled exit mutation survived')
            guarded_commands = [
                ('decoder-smoke-fail', 'python3 "$WORK/tests/test_uncompress.py" --probe "$WORK/build-unix/jc_uncompress_test" --engine "$WORK/build-unix/jc_reborn" --phase smoke'),
                ('frame-smoke-fail', 'python3 "$WORK/tests/test_frame_limits.py" --exe "$WORK/build-unix/jc_reborn" --probe "$WORK/build-unix/jc_frame_test" --phase smoke'),
                ('frame-regression-fail', 'python3 "$WORK/tests/test_frame_limits.py" --exe "$WORK/build-unix/jc_reborn" --probe "$WORK/build-unix/jc_frame_test" --phase regression'),
                ('extractor-smoke-fail', 'python3 "$WORK/tests/test_extractors.py" --sound "$WORK/build-unix/extract_sound" --walk "$WORK/build-unix/extract_walk_data" --phase smoke'),
                ('extractor-regression-fail', 'python3 "$WORK/tests/test_extractors.py" --sound "$WORK/build-unix/extract_sound" --walk "$WORK/build-unix/extract_walk_data" --phase regression'),
                ('platform-smoke-fail', 'SRC="$WORK" OUT="$WORK/build-unix/platform-tests" bash "$PLATFORM_TEST" --phase smoke')]
            if LINUX:
                guarded_commands.extend([
                    ('graphics-regression-fail', 'python3 "$WORK/tests/test_graphics_alloc.py" --output "$WORK/build-unix/graphics-tests"'),
                    ('drawing-smoke-fail', 'python3 "$WORK/tests/test_drawing_bounds.py" --output "$WORK/build-unix/drawing-tests" --phase smoke'),
                    ('drawing-regression-fail', 'python3 "$WORK/tests/test_drawing_bounds.py" --output "$WORK/build-unix/drawing-tests" --phase regression')])
            for mode, needle in guarded_commands:
                assert original.count(needle) == 1, f'tests/unix-build.sh: expected one {mode} command'
                mutant = original.replace(needle, needle + ' || true')
                code, text, trace, folder = run_case(work, mutant, mode, 'mutant-' + mode)
                assert 'WITNESS dump-regression' in trace, f'tests/unix-build.sh: {mode} mutant did not execute regression witness'
                try:
                    assert_case(mode, code, text, trace)
                except AssertionError as exc:
                    assert str(exc) == f'tests/unix-build.sh: {mode} reached later regression or lost its diagnostic/status', f'Wrong mutation failure: {exc}'
                    records.append({'mutation':mode,'result':'FIRED','named_failure':str(exc),'executed_trace':trace.splitlines(),'mutant_script_sha256':hashlib.sha256((folder/'unix-build.sh').read_bytes()).hexdigest()})
                    print(f'FIRED 1/1 {exc}',flush=True)
                else:
                    raise AssertionError(f'tests/unix-build.sh: {mode} mutation survived')
        (work/'report.json').write_text(json.dumps({'status':'PASS','checks':records},indent=2)+'\n',encoding='utf-8')
    try:
        if args.work:
            work=args.work.resolve(); work.mkdir(parents=True,exist_ok=False); verify(work)
        else:
            with tempfile.TemporaryDirectory(prefix='jcr-unix-flow-') as tmp: verify(Path(tmp))
        return 0
    except (AssertionError,subprocess.TimeoutExpired) as exc:
        print(f'FAIL {exc}'); return 1

if __name__=='__main__': raise SystemExit(main())
