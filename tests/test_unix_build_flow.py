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
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tests/unix-build.sh'

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
  if [ "$JCR_CASE" = build-fail ]; then echo 'error: deliberate extra ALL target failure'; exit 23; fi
  if [ "$JCR_CASE" = warning ]; then echo 'warning: successful fixture build'; fi
fi
exit 0
''')
    executable(commands/'cc',"#!/usr/bin/env bash\necho 'cc fixture'\n")
    env=dict(os.environ,PATH=str(commands)+os.pathsep+os.environ['PATH'],SRC=str(src),WORK=str(folder/'copied-source'),JCR_CASE=mode,JCR_TRACE=str(folder/'witness.log'))
    proc=subprocess.run(['bash',str(script)],env=env,capture_output=True,timeout=30)
    text=(proc.stdout+proc.stderr).decode('utf-8','replace'); (folder/'run.log').write_text(text,encoding='utf-8')
    trace=(folder/'witness.log').read_text()
    return proc.returncode,text,trace,folder

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--work',type=Path); parser.add_argument('--mutations',action='store_true'); args=parser.parse_args()
    original=SCRIPT.read_text(encoding='utf-8')
    def verify(work):
        records=[]
        for mode in ('clean','warning','build-fail','smoke-fail'):
            code,text,trace,folder=run_case(work,original,mode,mode)
            if mode in ('clean','warning'):
                assert code==0 and trace.splitlines()==['WITNESS build-executed','WITNESS png-smoke','WITNESS dump-regression'], f'tests/unix-build.sh: {mode} control did not reach smoke then regression'
            elif mode=='build-fail':
                assert code==23 and text.count('FAIL tests/unix-build.sh: CMake build failed')==1 and trace.splitlines()==['WITNESS build-executed'], 'tests/unix-build.sh: failed build reached smoke/regression or lost its diagnostic/status'
            else:
                assert code==31 and text.count('FAIL tests/test_png_decoder.c: fixture rejected')==1 and trace.splitlines()==['WITNESS build-executed','WITNESS png-smoke'], 'tests/unix-build.sh: failed PNG smoke reached regression'
            records.append({'case':mode,'status':code,'trace':trace.splitlines()})
            print(f'PASS tests/unix-build.sh: {mode}',flush=True)
        if args.mutations:
            needle='    exit "$build_status"'
            assert original.count(needle)==1, 'tests/unix-build.sh: expected one build short-circuit'
            mutant=original.replace(needle,'    : # disabled build-failure exit')
            code,text,trace,folder=run_case(work,mutant,'build-fail','mutant')
            assert code==0 and 'WITNESS dump-regression' in trace and text.count('FAIL tests/unix-build.sh: CMake build failed')==1, 'tests/unix-build.sh: mutation did not execute the bad continuation'
            records.append({'mutation':'disabled build failure exit','result':'FIRED','named_failure':'tests/unix-build.sh: failed build reached smoke/regression','executed_trace':trace.splitlines(),'mutant_script_sha256':hashlib.sha256((folder/'unix-build.sh').read_bytes()).hexdigest()})
            print('FIRED 1/1 tests/unix-build.sh: disabled build exit reaches regression and ordering oracle rejects it',flush=True)
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
