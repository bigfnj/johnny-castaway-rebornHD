"""Rebuild isolated Linux audio mutants and require their exact C assertions.

Run the unchanged delivery probe's smoke cases, then every regression case,
before mutating production code. Each mutant gets its own copied sources and
fresh executable; a compiler failure, timeout, or unrelated crash is not FIRED.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys


BACKEND = 'platform/platform_linux.c'
DRIVER = 'tests/test_linux_audio_delivery.c'
SOURCE_FILES = [BACKEND, DRIVER, 'platform/platform.h', 'src/engine/mytypes.h']
SMOKE = ['full', 'rate-near']
REGRESSION = [
    'any-failure', 'access-failure', 'format-failure', 'channels-failure',
    'rate-failure', 'commit-failure', 'partial-mono', 'partial-stereo',
    'recover', 'interrupted', 'would-block', 'zero-progress', 'wait-failure',
    'recover-failure', 'blocked-stop', 'close-pending',
]


def mutations():
    cases = []
    setters = [
        ('any', 'snd_pcm_hw_params_any(pcmHandle, params)'),
        ('access', 'snd_pcm_hw_params_set_access(pcmHandle, params, SND_PCM_ACCESS_RW_INTERLEAVED)'),
        ('format', 'snd_pcm_hw_params_set_format(pcmHandle, params, SND_PCM_FORMAT_U8)'),
        ('channels', 'snd_pcm_hw_params_set_channels(pcmHandle, params, spec->channels)'),
        ('rate', 'snd_pcm_hw_params_set_rate_near(pcmHandle, params, &rate, 0)'),
    ]
    for label, call in setters:
        # Keep the setter executed. Only discard its result, so removing the
        # call cannot accidentally be what makes the fixture reject the mutant.
        cases.append((f'ignore-{label}-failure', f'{label}-failure',
                      f'if ({call} < 0) {{', f'if (({call} < 0) && 0) {{',
                      'failed setup must refuse audio open'))
    cases.extend([
        ('ignore-commit-failure', 'commit-failure',
         'err = snd_pcm_hw_params(pcmHandle, params);\n    if (err < 0) {',
         'err = snd_pcm_hw_params(pcmHandle, params);\n    if ((err < 0) && 0) {',
         'failed setup must refuse audio open'),
        ('partial-buffer-complete', 'partial-mono',
         'offset += (snd_pcm_uframes_t)written;',
         'offset = (snd_pcm_uframes_t)audioFrames;',
         'callback must not replace an unwritten tail'),
        ('omit-tail-channel-factor', 'partial-stereo',
         'audioBuffer + (size_t)offset * audioFrameBytes,',
         'audioBuffer + (size_t)offset,',
         'write tail has the wrong byte offset'),
        ('discard-negotiated-rate', 'rate-near',
         'spec->freq = (int)rate;', '/* mutant discards the negotiated rate */',
         'spec.freq == (!strcmp(scenario, "rate-near") ? 22050 : 11025)'),
    ])
    for case in ['recover', 'interrupted']:
        cases.append((f'skip-{case}-tail', case,
                      '/* A recovered write retries the unchanged tail. */\n                        usleep(1000);',
                      '/* mutant discards the recovered tail */\n                        offset = (snd_pcm_uframes_t)audioFrames;',
                      'callback must not replace an unwritten tail'))
    for case in ['would-block', 'zero-progress']:
        cases.append((f'skip-{case}-wait', case,
                      'error = snd_pcm_wait(pcmHandle, 20);',
                      # Retain a compile-time reference to the fixture's wait
                      # function while deliberately never calling it.
                      'error = (0 ? snd_pcm_wait(pcmHandle, 20) : 1);',
                      'waitCalls == 1 && writeCalls == 3'))
    for case in ['recover-failure', 'wait-failure']:
        cases.append((f'ignore-{case}-stop', case,
                      'if (snd_pcm_recover(pcmHandle, error, 1 /* silent */) < 0) {',
                      'if ((snd_pcm_recover(pcmHandle, error, 1 /* silent */) < 0) && 0) {',
                      'delivered == 5 && recoverCalls == 1'))
    for case, assertion in [
        ('blocked-stop', 'pending write ignored shutdown'),
        ('close-pending', 'no pending-tail write after concurrent close'),
    ]:
        cases.append((f'ignore-{case}', case,
                      'while (atomic_load(&audioThreadRunning) && offset < (snd_pcm_uframes_t)audioFrames) {',
                      'while (offset < (snd_pcm_uframes_t)audioFrames) {', assertion))
    return cases


def command(argv, logfile, timeout):
    try:
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, errors='replace', timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b''
        if isinstance(output, bytes):
            output = output.decode('utf-8', 'replace')
        logfile.write_text(output, encoding='utf-8')
        raise AssertionError(f'{logfile.name}: timed out before the intended assertion') from exc
    logfile.write_text(result.stdout, encoding='utf-8')
    return result


def build(folder, snapshot, replacement=None):
    folder.mkdir()
    source = folder / 'source'
    for name, data in snapshot.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    backend = source / BACKEND
    if replacement:
        old, new = replacement
        text = backend.read_text(encoding='utf-8')
        assert text.count(old) == 1, f'{BACKEND}: {folder.name} needs exactly one mutation site'
        backend.write_text(text.replace(old, new), encoding='utf-8')
    exe = folder / 'probe'
    exe.write_text('not a compiled probe', encoding='utf-8')
    os.utime(exe, ns=(1_000_000_000, 1_000_000_000))
    before = exe.stat().st_mtime_ns
    result = command([
        'cc', '-std=c11', '-D_DEFAULT_SOURCE', '-DPLATFORM_LINUX',
        '-Wall', '-Wextra', '-Werror', '-I' + str(source / 'platform'),
        '-I' + str(source / 'src/engine'), str(source / DRIVER),
        '-o', str(exe), '-lX11', '-lasound', '-pthread',
    ], folder / 'build.log', 120)
    assert result.returncode == 0, f'{folder.name}: build failed\n{result.stdout}'
    after = exe.stat().st_mtime_ns
    assert after > before, f'{folder.name}: executable timestamp did not advance'
    assert exe.read_bytes().startswith(b'\x7fELF'), f'{folder.name}: build did not produce an ELF executable'
    return exe, {
        'before_ns': before, 'after_ns': after,
        'executable_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(),
        'backend_sha256': hashlib.sha256(backend.read_bytes()).hexdigest(),
        'driver_sha256': hashlib.sha256((source / DRIVER).read_bytes()).hexdigest(),
    }


def run_case(exe, case):
    result = command([str(exe), case], exe.parent / f'{case}.log', 10)
    witness = f'WITNESS platform_linux.c delivery {case} BEGIN'
    assert result.stdout.splitlines().count(witness) == 1, f'{case}: missing unique runtime witness\n{result.stdout}'
    return result, witness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', required=True, type=Path,
                        help='New isolated output directory; copied sources and evidence are retained')
    args = parser.parse_args()
    assert sys.platform.startswith('linux'), 'run this Linux probe on Linux or in the Linux test image'
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    snapshot = {name: (source / name).read_bytes() for name in SOURCE_FILES}
    report = {'status': 'RUNNING', 'controls': [], 'mutations': []}
    try:
        exe, artifact = build(output / 'control', snapshot)
        for phase, cases in [('smoke', SMOKE), ('regression', REGRESSION)]:
            for case in cases:
                result, witness = run_case(exe, case)
                passed = f'WITNESS platform_linux.c delivery {case} PASS'
                assert result.returncode == 0 and result.stdout.splitlines().count(passed) == 1, result.stdout
                assert 'Assertion ' not in result.stdout, result.stdout
                report['controls'].append({'phase': phase, 'case': case, 'exit_code': 0,
                                           'runtime_witness': witness, 'artifact': artifact})
                print(f'PASS {DRIVER}: {phase} {case}', flush=True)
        cases = mutations()
        for label, case, old, new, assertion in cases:
            exe, artifact = build(output / label, snapshot, (old, new))
            result, witness = run_case(exe, case)
            failures = [line for line in result.stdout.splitlines() if 'Assertion ' in line and line.endswith(' failed.')]
            assert result.returncode == -signal.SIGABRT, f'{label}: expected an assertion abort, got {result.returncode}\n{result.stdout}'
            assert len(failures) == 1 and result.stdout.count('Assertion ') == 1, f'{label}: expected exactly one assertion\n{result.stdout}'
            assert 'test_linux_audio_delivery.c:' in failures[0] and assertion in failures[0], f'{label}: wrong assertion\n{result.stdout}'
            assert ' PASS' not in result.stdout, f'{label}: a failed case reported PASS\n{result.stdout}'
            named_failure = f'{DRIVER}:{case}: {assertion}'
            report['mutations'].append({
                'mutation': label, 'case': case, 'file': BACKEND, 'result': 'FIRED',
                'exit_code': result.returncode, 'runtime_witness': witness,
                'named_failure': named_failure, 'assertion_output': failures[0],
                'artifact': artifact,
            })
            print(f'FIRED 1/1 {named_failure} ({label})', flush=True)
        assert len(report['mutations']) == len(cases), 'not every mutation produced evidence'
        assert all((source / name).read_bytes() == data for name, data in snapshot.items()), 'input source changed during verification'
        report['status'] = 'PASS'
        print(f'Linux audio delivery mutations: {len(cases)}/{len(cases)} FIRED', flush=True)
        return 0
    except (AssertionError, OSError) as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc)
        print(f'FAIL tests/test_linux_audio_delivery_mutations.py: {exc}', flush=True)
        return 1
    finally:
        (output / 'mutation-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    raise SystemExit(main())
