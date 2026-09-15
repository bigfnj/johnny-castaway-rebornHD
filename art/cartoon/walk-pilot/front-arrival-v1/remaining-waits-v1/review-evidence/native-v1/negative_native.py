"""Execute unchanged native guards on exact capture replays and corrupted copies.

This tests Python parser/comparison guard behavior. It does not rebuild or rerun
the native executable and does not claim an engine mutation result.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import types
from unittest.mock import patch

import capture_candidate as tested

OUT = Path('/out')
TARGET = OUT / 'negative-controls' / 'native'
SOURCE = OUT / 'candidate-v1' / 'increasing' / 'full'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(), 'preserve native guard replay evidence'
    TARGET.mkdir(parents=True)
    witness = {name: sha(OUT / name) for name in ('capture.py', 'capture_candidate.py', 'native_core.py', 'negative_native.py')}
    print('WITNESS exact imported replay guards ' + json.dumps(witness, sort_keys=True), flush=True)
    prep = json.loads((OUT / 'candidate-v1/preparation.json').read_bytes())
    binding = json.loads((OUT / 'baseline-v1/build.json').read_bytes())
    results = []
    cases = [('control', None), ('changed-timestamp', 'turn capture: one display per completed native wait'),
             ('changed-approved-pose-pixel', 'turn capture: all prior-approved pose/background pixels unchanged')]
    source_report = json.loads((SOURCE / 'report.json').read_bytes())
    for case, expected in cases:
        stage = TARGET / case
        stage.mkdir()
        os.link(OUT / 'candidate-v1/scrantic_data.zip', stage / 'scrantic_data.zip')

        def replay(command, cwd, env, stdout, stderr, timeout):
            text = (SOURCE / 'capture.log').read_text()
            if case == 'changed-timestamp':
                old = 'TURN DISPLAY: 3 logical_ms=120 '
                assert text.count(old) == 1, 'unique timestamp mutation target'
                text = text.replace(old, 'TURN DISPLAY: 3 logical_ms=121 ')
            stdout.write(text.encode())
            stdout.flush()
            for path in SOURCE.glob('*.ppm'):
                target = cwd / path.name
                if case == 'changed-approved-pose-pixel' and path.name == source_report['displays'][0]['ppm']:
                    assert source_report['displays'][0]['actual_draw'][3] == 16
                    raw = bytearray(path.read_bytes())
                    header = raw.index(b'\n255\n') + 5
                    raw[header] ^= 1
                    target.write_bytes(raw)
                else:
                    os.link(path, target)
            return types.SimpleNamespace(returncode=0)

        tested.CANDIDATE = stage
        observed = None
        with patch.object(tested.subprocess, 'run', replay):
            try:
                tested.compare('increasing', 'full', prep, binding)
            except ValueError as error:
                observed = str(error)
        assert observed == expected, f'one expected replay failure:{case}:{observed!r}'
        result = {'case': case, 'status': 'PASS' if expected is None else 'FIRED', 'failure': observed,
                  'guard_module_sha256': witness, 'input_log_sha256': sha(stage / 'increasing/full/capture.log'),
                  'scope': 'Recorded native outputs replayed through unchanged Python guards; native engine not rerun.'}
        (stage / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        results.append(result)
        print('PASS replay control' if expected is None else 'FIRED ' + observed, flush=True)
    report = {'status': 'PASS', 'positive_controls': 1, 'mutations_fired': 2, 'source_capture_log_sha256': sha(SOURCE / 'capture.log'),
              'source_capture_report_sha256': sha(SOURCE / 'report.json'), 'cases': results,
              'limitation': 'Guard replay, not a fresh native engine mutation build or test.'}
    (TARGET / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
