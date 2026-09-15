"""Manual rebuilt extractor mutations and real-source injected I/O failures.

Each variant uses an isolated copied source tree, compiler timestamp proof, an
executed assertion witness and the same oracle as its control. Production files
and assets are never modified. Not a routine gate or original-data parity test.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import test_extractors as checks

ROOT = Path(__file__).resolve().parents[1]


def command(args, work, name):
    result = subprocess.run(list(map(str, args)), capture_output=True, timeout=180)
    output = (result.stdout + result.stderr).decode('utf-8', 'replace')
    (work / (name + '.log')).write_text(output, encoding='utf-8')
    assert result.returncode == 0, f'tests/test_extractor_mutations.py: {name} failed: {output}'
    return output


def prepare(work):
    source = work / 'source'; source.mkdir()
    for name in ('extract_sound.c', 'extract_walk_data.c', 'extract_io.c', 'extract_io.h'):
        shutil.copyfile(ROOT / 'tools' / name, source / name)
    for name in ('extractor_faults.c', 'extractor_faults.h'):
        shutil.copyfile(ROOT / 'tests' / name, source / name)
    cmake = '''cmake_minimum_required(VERSION 3.19)
project(extractor_controls C)
foreach(name extract_sound extract_walk_data)
  add_executable(${name} ${name}.c extract_io.c extractor_faults.c)
  if(MSVC)
    target_compile_definitions(${name} PRIVATE _CRT_SECURE_NO_WARNINGS)
  endif()
endforeach()
# Per-source options keep fault substitution out of the wrapper functions.
set_source_files_properties(extract_sound.c extract_walk_data.c extract_io.c
  PROPERTIES COMPILE_OPTIONS "$<$<C_COMPILER_ID:MSVC>:/FI${CMAKE_CURRENT_SOURCE_DIR}/extractor_faults.h>;$<$<NOT:$<C_COMPILER_ID:MSVC>>:-include;${CMAKE_CURRENT_SOURCE_DIR}/extractor_faults.h>")
'''
    # Both target names intentionally execute the injected build. An unset
    # JCR_EXTRACT_FAULT exercises the same real C I/O as production.
    (source / 'CMakeLists.txt').write_text(cmake, encoding='utf-8')
    build = work / 'build'
    command(['cmake', '-S', source, '-B', build], work, 'configure')
    command(['cmake', '--build', build, '--config', 'Release'], work, 'control-build')
    folder = build / 'Release' if os.name == 'nt' else build
    suffix = '.exe' if os.name == 'nt' else ''
    return source, build, folder / ('extract_sound' + suffix), folder / ('extract_walk_data' + suffix)


def check(name, sound, walk, work, fault=None):
    env = dict(os.environ)
    env.pop('JCR_EXTRACT_FAULT', None)
    if fault: env['JCR_EXTRACT_FAULT'] = fault
    checks.check_case(name, sound, walk, work, env)


def verify(work, controls_only):
    source, build, sound, walk = prepare(work)
    for phase, names in [('smoke', checks.SMOKE), ('regression', checks.REGRESSION)]:
        phase_work = work / phase; phase_work.mkdir()
        for name in names: check(name, sound, walk, phase_work)
    faults = work / 'faults'; faults.mkdir()
    for kind in ('read', 'seek', 'tell', 'input-close', 'write', 'close', 'allocate'):
        check('sound-' + kind + '-fault', sound, walk, faults, kind)
        if kind != 'allocate': check('walk-' + kind + '-fault', sound, walk, faults, kind)
    check('walk-stdout-fault', sound, walk, faults, 'stdout')
    records = []
    if not controls_only:
        variants = [
            ('range', 'extract_io.c', 'if (offset < 0 || offset > size || length > (size_t)(size - offset)) {', 'if (0) {', 'sound-truncated', None),
            ('read', 'extract_io.c', 'if (fread(buffer, 1, length, file) != length) {', 'if (fread(buffer, 1, length, file) != length && 0) {', 'walk-read-fault', 'read'),
            ('seek', 'extract_io.c', 'if (fseek(file, offset, SEEK_SET) != 0) {', 'if (fseek(file, offset, SEEK_SET) != 0 && 0) {', 'walk-seek-fault', 'seek'),
            ('tell', 'extract_io.c', '(*size = ftell(file)) < 0', '(*size = ftell(file)) < 0 && 0', 'sound-tell-fault', 'tell'),
            ('write', 'extract_io.c', 'if (!written || !closed)', 'if (!closed)', 'walk-write-fault', 'write'),
            ('close', 'extract_io.c', 'if (!written || !closed)', 'if (!written)', 'sound-close-fault', 'close'),
            ('exclusive', 'extract_io.c', ' | _O_EXCL' if os.name == 'nt' else ' | O_EXCL', '', 'sound-existing', None),
            ('rollback', 'extract_sound.c', 'if (result != 0 && created[j]) remove(paths[j]);', '(void)created[j];', 'sound-existing', None),
            ('walk-count', 'extract_walk_data.c', '#define WALK_RECORDS 489', '#define WALK_RECORDS 488', 'walk-valid', None),
            ('length', 'extract_sound.c', '(size_t)extract_u16(header) + 8', '(size_t)extract_u16(header) + 7', 'sound-valid', None),
            ('endianness', 'extract_io.c', '(unsigned int)bytes[0] | ((unsigned int)bytes[1] << 8)', '(unsigned int)bytes[1] | ((unsigned int)bytes[0] << 8)', 'walk-valid', None),
            ('sound-input-close', 'extract_sound.c', 'if (fclose(file) != 0)', 'if (fclose(file) != 0 && 0)', 'sound-input-close-fault', 'input-close'),
            ('walk-input-close', 'extract_walk_data.c', 'if (fclose(file) != 0)', 'if (fclose(file) != 0 && 0)', 'walk-input-close-fault', 'input-close'),
            ('allocate', 'extract_sound.c', 'if (!buffers[j] || !paths[j])', 'if (0)', 'sound-allocate-fault', 'allocate'),
            ('stdout', 'extract_walk_data.c', 'if (fwrite(text, 1, used, stdout) != used || fflush(stdout) != 0)', 'if (fwrite(text, 1, used, stdout) != used && 0)', 'walk-stdout-fault', 'stdout'),
        ]
        for label, name, before, after, case, fault in variants:
            path = source / name; original = path.read_text(encoding='utf-8')
            assert original.count(before) == 1, f'tools/{name}: mutation target count differs'
            timestamp = max(sound.stat().st_mtime_ns, walk.stat().st_mtime_ns)
            time.sleep(1.05)
            path.write_text(original.replace(before, after), encoding='utf-8')
            command(['cmake', '--build', build, '--config', 'Release'], work, label + '-build')
            exe = sound if case.startswith('sound') else walk
            assert exe.stat().st_mtime_ns > timestamp, f'tools/{name}: mutated executable was not rebuilt'
            case_work = work / ('mutation-' + label); case_work.mkdir()
            captured = io.StringIO()
            try:
                with contextlib.redirect_stdout(captured): check(case, sound, walk, case_work, fault)
            except AssertionError as exc:
                witness = captured.getvalue()
                assert 'assertion executed' in witness, f'tools/{name}: no executed assertion witness'
                expected = 'tools/extract_sound.c' if case.startswith('sound') else 'tools/extract_walk_data.c'
                assert str(exc).startswith(expected + ' ' + case + ':'), f'tools/{name}: wrong mutation failure: {exc}'
                record = {'mutation': label, 'source': 'tools/' + name, 'result': 'FIRED', 'failure': str(exc),
                          'exe_mtime_advanced': True, 'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest(), 'witness': witness}
                records.append(record); print(f'FIRED 1/1 tools/{name} {label}: {exc}', flush=True)
            else: raise AssertionError(f'tools/{name}: {label} mutant survived')
            finally: path.write_text(original, encoding='utf-8')
        command(['cmake', '--build', build, '--config', 'Release'], work, 'restored-build')
        restored = work / 'restored'; restored.mkdir()
        for case in checks.SMOKE: check(case, sound, walk, restored)
    (work / 'report.json').write_text(json.dumps({'status': 'PASS', 'mutations': records, 'fault_controls': 14,
        'scope': 'compiled C with test-only I/O substitution; original SCRANTIC.SCR unavailable'}, indent=2) + '\n', encoding='utf-8')
    print(f'PASS extractor fault controls and {len(records)} rebuilt mutations; evidence {work}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path); parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve(); work.mkdir(parents=True, exist_ok=False)
    else:
        parent = ROOT / 'build/extractor-mutations'; parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(dir=parent))
    print(f'Extractor mutation evidence: {work}', flush=True)
    try: verify(work, args.controls_only); return 0
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}; evidence: {work}'); return 1


if __name__ == '__main__': raise SystemExit(main())
