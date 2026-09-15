import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time
from config import contract
SOURCE = Path('/source')
OUT = Path('/out')
BASE = OUT / 'baseline-v1'
FORMAT = SOURCE / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'
spec = importlib.util.spec_from_file_location('ring_codec', FORMAT)
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, label):
    if not ok:
        raise ValueError('turn capture: ' + label)

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def protected():
    result = {path.relative_to(SOURCE).as_posix(): sha(path.read_bytes())
              for folder in ('src', 'platform', 'third_party/miniz')
              for path in (SOURCE / folder).rglob('*') if path.is_file() and path.suffix in ('.c', '.h')}
    for name in ('CMakeLists.txt', 'assets/scrantic_data.zip', FORMAT.relative_to(SOURCE).as_posix()):
        result[name] = sha((SOURCE / name).read_bytes())
    return result

def build():
    require(not BASE.exists(), 'preserve baseline build evidence')
    prep = json.loads((OUT / 'preparation.json').read_bytes())
    inputs = protected()
    require(inputs['assets/scrantic_data.zip'] == prep['production_archive_sha256'], 'production source archive identity')
    require(sha((OUT / 'route_driver.c').read_bytes()) == prep['adapted_driver_sha256'], 'prepared observer identity')
    require(sha((OUT / 'baseline-pack.zip').read_bytes()) == prep['baseline_pack_sha256'], 'approved017 private baseline identity')
    BASE.mkdir()
    text = (SOURCE / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in text.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    exe = BASE / 'waiting_ring_probe'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX',
               '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz',
               '/out/route_driver.c', *['/source/' + name for name in sources],
               '-Wl,--wrap=eventsWaitTick', '-Wl,--wrap=platformUpdateWindow', '-Wl,--wrap=grDrawSprite',
               '-Wl,--wrap=grDrawSpriteFlip', '-Wl,--wrap=walkAnimate', '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (BASE / 'build.stdout.txt').write_text(result.stdout)
    (BASE / 'build.stderr.txt').write_text(result.stderr)
    require(result.returncode == 0 and exe.stat().st_mtime_ns >= started, 'fresh successful native build')
    binding = {'command': command, 'source_commit': prep['source_commit'], 'executable_sha256': sha(exe.read_bytes()),
               'driver_sha256': prep['adapted_driver_sha256'], 'executable_mtime_ns': exe.stat().st_mtime_ns,
               'build_started_ns': started, 'image_id': prep['image_id'], 'protected_sha256': inputs,
               'compiler': subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0],
               'libc': subprocess.check_output(['ldd', '--version'], text=True).splitlines()[0],
               'capture_helper_sha256': sha(Path(__file__).read_bytes()), 'codec_sha256': sha(FORMAT.read_bytes()),
               'baseline_pack_sha256': prep['baseline_pack_sha256']}
    save(BASE / 'build.json', binding)
    save(BASE / 'route-contract.json', contract())
    print('PASS fresh turn observer built; production sources untouched', flush=True)
    return exe, binding
