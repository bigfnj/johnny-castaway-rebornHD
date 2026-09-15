"""Exercise the production CMake data prerequisite in isolated native projects.
No production archive changes or graphical processes. --mutations regenerates
disabled-prerequisite projects and requires one target-naming failure per mutant.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'cmake/RuntimeData.cmake'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(args, cwd, log):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, timeout=180)
    text = (result.stdout + result.stderr).decode('utf-8', 'replace')
    log.write_text(text, encoding='utf-8')
    assert result.returncode == 0, f'cmake/RuntimeData.cmake: command failed; {log.name}: {text[-3000:]}'
    return text

def probe(work, options, module, name):
    folder = work / name; folder.mkdir()
    source = folder / 'source'; source.mkdir()
    (source / 'RuntimeData.cmake').write_text(module, encoding='utf-8')
    (source / 'main.c').write_text('#include <stdio.h>\nint main(void) { puts("WITNESS runtime-data binary executed"); return 0; }\n', encoding='utf-8')
    (source / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.19)
project(runtime_data_fixture C)
include(RuntimeData.cmake)
foreach(target jc_reborn jc_reborn_scr)
    add_executable(${target} main.c)
    set_target_properties(${target} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/runtime space/${target}/$<CONFIG>")
endforeach()
jc_add_runtime_data("${CMAKE_SOURCE_DIR}/scrantic_data.zip" jc_reborn jc_reborn_scr)
''', encoding='utf-8')
    archive = source / 'scrantic_data.zip'
    def change_archive(label):
        with zipfile.ZipFile(archive, 'w') as z: z.writestr('witness.txt', label)
        return digest(archive)
    change_archive('initial')
    build = folder / 'build'
    configure = [options.cmake, '-S', source, '-B', build, '-DCMAKE_BUILD_TYPE=Release']
    if options.generator: configure += ['-G', options.generator]
    command(configure, folder, folder / 'configure.log')
    cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8')
    generator = next(line.partition('=')[2] for line in cache.splitlines() if line.startswith('CMAKE_GENERATOR:INTERNAL='))
    command([options.cmake, '--build', build, '--config', 'Release'], folder, folder / 'initial-build.log')
    binaries = {}
    for target in ('jc_reborn', 'jc_reborn_scr'):
        binary = build / 'runtime space' / target / 'Release' / (target + ('.exe' if os.name == 'nt' else ''))
        text = command([binary], folder, folder / f'{target}-execution.log')
        assert 'WITNESS runtime-data binary executed' in text, f'{target}: compiled witness not executed'
        binaries[target] = (binary, digest(binary), binary.stat().st_mtime_ns)
    results = []
    for sequence, target in enumerate(('jc_reborn', 'jc_reborn_scr', 'jc_runtime_data', None)):
        label=f'{name}-{sequence}-{target}'; expected = change_archive(label)
        args = [options.cmake, '--build', build, '--config', 'Release']
        if target: args += ['--target', target]
        command(args, folder, folder / f'refresh-{sequence}.log')
        for checked, (binary, _, _) in binaries.items():
            deployed = binary.parent / 'scrantic_data.zip'
            assert deployed.exists() and digest(deployed) == expected, f'cmake/RuntimeData.cmake: {target or "ALL"} did not refresh {checked}/scrantic_data.zip'
            with zipfile.ZipFile(deployed) as z: assert z.read('witness.txt').decode() == label, f'{checked}/scrantic_data.zip: witness differs'
        results.append(f'{target or "ALL"}: both archive hashes and witness members match')
    for target, (binary, original_hash, original_time) in binaries.items():
        deployed = binary.parent / 'scrantic_data.zip'; deployed.unlink()
        command([options.cmake, '--build', build, '--config', 'Release', '--target', target], folder, folder / f'recover-{target}.log')
        assert deployed.exists() and digest(deployed) == digest(archive), f'cmake/RuntimeData.cmake: {target} did not restore deleted archive'
        assert digest(binary) == original_hash and binary.stat().st_mtime_ns == original_time, f'{target}: artwork refresh unexpectedly rebuilt binary'
    report = {'status':'PASS','generator':generator,'checks':results,'binary_execution_witnesses':2,
              'deleted_archives_restored':2,'binary_hashes_and_timestamps_unchanged':True,
              'module_sha256':digest(source / 'RuntimeData.cmake')}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def run(options, work):
    original_hash = digest(MODULE); module = MODULE.read_text(encoding='utf-8')
    good = probe(work, options, module, 'control')
    print(f'PASS cmake/RuntimeData.cmake: {good["generator"]}; explicit/ALL/data targets, output paths, deletion recovery; no relink',flush=True)
    mutations=[]
    if options.mutations:
        needle='        add_dependencies(${runtime_target} jc_runtime_data)'
        assert module.count(needle)==1, 'cmake/RuntimeData.cmake: expected one prerequisite declaration'
        for target in ('jc_reborn','jc_reborn_scr'):
            mutant=module.replace(needle,f'        if(NOT runtime_target STREQUAL "{target}")\n{needle}\n        endif()')
            try: probe(work, options, mutant, 'mutant-'+target)
            except AssertionError as exc:
                expected=f'cmake/RuntimeData.cmake: {target} did not refresh jc_reborn/scrantic_data.zip'
                assert str(exc)==expected, f'{target}: wrong mutation failure: {exc}'
                folder=work/('mutant-'+target)
                assert (folder/'build/CMakeCache.txt').is_file(), 'Mutation project was not configured'
                assert 'WITNESS runtime-data binary executed' in (folder/'jc_reborn-execution.log').read_text(), 'Mutation binary was not executed'
                mutations.append({'target':target,'result':'FIRED','named_failure':str(exc),
                                  'configured_module_sha256':digest(folder/'source/RuntimeData.cmake'),'compiled_binary_witness':True})
                print(f'FIRED 1/1 {exc}',flush=True)
            else: raise AssertionError(f'cmake/RuntimeData.cmake: {target} prerequisite mutant survived')
    assert digest(MODULE)==original_hash, 'Production CMake module changed'
    (work/'report.json').write_text(json.dumps({'status':'PASS','control':good,'mutations':mutations},indent=2)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmake',default='cmake'); parser.add_argument('--generator')
    parser.add_argument('--work',type=Path); parser.add_argument('--mutations',action='store_true')
    options=parser.parse_args()
    try:
        if options.work:
            work=options.work.resolve(); work.mkdir(parents=True,exist_ok=False); run(options,work)
        else:
            with tempfile.TemporaryDirectory(prefix='jcr-runtime-data-') as tmp: run(options,Path(tmp))
        return 0
    except (AssertionError,subprocess.TimeoutExpired) as exc:
        print(f'FAIL {exc}'); return 1

if __name__=='__main__': raise SystemExit(main())
