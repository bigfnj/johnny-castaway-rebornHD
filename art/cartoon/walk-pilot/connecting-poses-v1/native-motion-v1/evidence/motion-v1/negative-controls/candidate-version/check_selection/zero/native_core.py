"""Native observer build and independent compiled draw/delay trace."""
import importlib.util
import json
from pathlib import Path
import subprocess
import time
import config

SOURCE, OUT, sha = config.ROOT, config.OUT, config.sha
BASE = OUT / 'baseline-v1'
FORMAT = SOURCE / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec = importlib.util.spec_from_file_location('connecting_codec', FORMAT)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


def require(ok, label):
    if not ok:
        raise ValueError('connecting capture: ' + label)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def protected():
    result = {p.relative_to(SOURCE).as_posix(): sha(p.read_bytes()) for folder in ('src', 'platform', 'third_party/miniz') for p in (SOURCE / folder).rglob('*') if p.is_file() and p.suffix in ('.c', '.h')}
    for name in ('CMakeLists.txt', 'assets/scrantic_data.zip', FORMAT.relative_to(SOURCE).as_posix()):
        result[name] = sha((SOURCE / name).read_bytes())
    return result


def compile_observer(command, exe, label):
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (BASE / (label + '.stdout.txt')).write_text(result.stdout)
    (BASE / (label + '.stderr.txt')).write_text(result.stderr)
    require(result.returncode == 0 and exe.is_file() and exe.stat().st_mtime_ns >= started, 'fresh successful build:' + label)
    return {'command': command, 'executable_sha256': sha(exe.read_bytes()), 'executable_mtime_ns': exe.stat().st_mtime_ns, 'build_started_ns': started, 'exit_code': result.returncode}


def build():
    require(not BASE.exists(), 'preserve baseline build evidence')
    prep = config.load_json(OUT / 'preparation.json')
    inputs = protected()
    require(inputs['assets/scrantic_data.zip'] == prep['production_archive_sha256'], 'production source archive identity')
    require(sha((OUT / 'route_driver.c').read_bytes()) == prep['adapted_driver_sha256'], 'prepared observer identity')
    require(sha((OUT / 'trace_driver.c').read_bytes()) == prep['trace_driver_sha256'], 'prepared C trace identity')
    require(sha((OUT / 'baseline-pack.zip').read_bytes()) == prep['baseline_pack_sha256'], 'current production baseline identity')
    BASE.mkdir()
    trace_exe = BASE / 'connecting_trace'
    trace_command = ['gcc', '-O0', '-I/source/src/engine', '-I/source/platform', '-I/source/src/data', '/out/trace_driver.c', '/source/src/engine/walk.c', '/source/src/engine/calcpath.c', '/source/src/engine/utils.c', '-o', str(trace_exe)]
    trace_build = compile_observer(trace_command, trace_exe, 'trace-build')
    contract = config.contract()
    observed = {}
    for clip, stages in contract['clips'].items():
        observed[clip] = {}
        for name, stage in stages.items():
            command = [str(trace_exe), *map(str, stage['api_arguments']), '2']
            run = subprocess.run(command, capture_output=True, text=True, timeout=5)
            require(run.returncode == 0, 'compiled C trace returned:' + clip + ':' + name)
            rows = [list(map(int, line.split())) for line in run.stdout.splitlines()]
            expected = [[r[k] for k in ('frame', 'flip_x', 'x', 'y', 'delay_ticks')] for r in stage['draws']]
            require(rows == expected, 'independent compiled C trace agrees with source contract:' + clip + ':' + name)
            observed[clip][name] = {'command': command, 'exit_code': run.returncode, 'rows': rows, 'stdout': run.stdout, 'stderr': run.stderr}
    save(BASE / 'independent-trace.json', {'status': 'PASS', 'build': trace_build, 'cases': observed, 'scope': 'Untouched production walk/calcPath logic; stubbed drawing, no display-timing or original-executable parity claim.'})
    save(BASE / 'route-contract.json', contract)
    text = (SOURCE / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    exe = BASE / 'connecting_walk_probe'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX', '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz', '/out/route_driver.c', *['/source/' + name for name in sources], '-Wl,--wrap=eventsWaitTick', '-Wl,--wrap=platformUpdateWindow', '-Wl,--wrap=grDrawSprite', '-Wl,--wrap=grDrawSpriteFlip', '-Wl,--wrap=walkAnimate', '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    binding = compile_observer(command, exe, 'build')
    binding.update(source_commit=prep['source_commit'], driver_sha256=prep['adapted_driver_sha256'], image_id=prep['image_id'], protected_sha256=inputs,
                   compiler=subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0], libc=subprocess.check_output(['ldd', '--version'], text=True).splitlines()[0],
                   helper_sha256={p.name: sha(p.read_bytes()) for p in config.HERE.glob('*.py')}, codec_sha256=sha(FORMAT.read_bytes()), baseline_pack_sha256=prep['baseline_pack_sha256'])
    save(BASE / 'build.json', binding)
    print('PASS independent C trace and fresh native observer built; sources untouched', flush=True)
    return exe, binding
