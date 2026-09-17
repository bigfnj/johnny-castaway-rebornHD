"""Build and run a scratch observer around unchanged production engine sources."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import zlib

SOURCE = Path('/source')
BASE = Path('/out')
OUT = BASE / 'baseline-v2'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def ppm(path):
    data = path.read_bytes()
    header = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\s', data)
    assert header and tuple(map(int, header.groups())) == (1280, 960), path
    pixels = data[header.end():]
    assert len(pixels) == 1280 * 960 * 3, path
    return pixels


def png_bytes(pixels):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    rows = b''.join(b'\0' + pixels[y * 3840:(y + 1) * 3840] for y in range(960))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1280, 960, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')


def main():
    OUT.mkdir()
    source_block = (SOURCE / 'CMakeLists.txt').read_text().split('set(COMMON_SOURCES\n', 1)[1].split('\n)', 1)[0]
    sources = [line.strip() for line in source_block.splitlines() if line.strip().endswith('.c')]
    sources.remove('src/engine/jc_reborn.c')
    sources.append('platform/platform_linux.c')
    protected = {str(p.relative_to(SOURCE)): sha(p.read_bytes())
                 for folder in ('src', 'platform', 'third_party/miniz')
                 for p in (SOURCE / folder).rglob('*') if p.is_file() and p.suffix in ('.c', '.h')}
    for name in ('CMakeLists.txt', 'assets/scrantic_data.zip', 'tests/test_palm_driver.c'):
        protected[name] = sha((SOURCE / name).read_bytes())
    exe = OUT / 'rear_route_probe'
    assert not exe.exists(), 'Preserve prior executable evidence'
    command = ['gcc', '-std=gnu11', '-O2', '-g', '-Wall', '-Wextra', '-DPLATFORM_LINUX',
               '-I/source/src/engine', '-I/source/src/data', '-I/source/platform', '-I/source/third_party/miniz',
               '/out/route_driver.c', *['/source/' + name for name in sources],
               '-Wl,--wrap=eventsWaitTick', '-Wl,--wrap=platformUpdateWindow',
               '-lX11', '-lasound', '-lpthread', '-lm', '-o', str(exe)]
    started = time.time_ns()
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=180)
    (OUT / 'build.stdout.txt').write_text(compiled.stdout)
    (OUT / 'build.stderr.txt').write_text(compiled.stderr)
    assert compiled.returncode == 0, compiled.stderr
    assert exe.stat().st_mtime_ns >= started, 'fresh build timestamp'
    build = dict(command=command, executable_sha256=sha(exe.read_bytes()),
                 executable_mtime_ns=exe.stat().st_mtime_ns, build_started_ns=started,
                 driver_sha256=sha((BASE / 'route_driver.c').read_bytes()), protected_sha256=protected)
    save(OUT / 'build.json', build)
    print('PASS fresh observer binary; unchanged production sources and archive', flush=True)

    rows = [list(map(int, row)) for row in re.findall(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}',
                                                    (SOURCE / 'src/data/walk_data.h').read_text())]
    route = []
    for row in rows[109:]:
        if row[1] == 0:
            break
        route.append(row)
    expected_rows = route + [rows[91 + 3 + 9]]
    assert len(route) == 23 and expected_rows[-1] == [0, 299, 240, 18]
    reports = {}
    for phase in ('smoke', 'full'):
        folder = OUT / phase
        folder.mkdir()
        shutil.copyfile(SOURCE / 'assets/scrantic_data.zip', folder / 'scrantic_data.zip')
        (folder / 'profile').mkdir()
        environment = dict(os.environ, HOME=str(folder / 'profile'))
        command = [str(exe), 'cartoon', phase]
        with (folder / 'capture.log').open('wb') as log:
            result = subprocess.run(command, cwd=folder, env=environment, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=90)
        text = (folder / 'capture.log').read_text()
        assert result.returncode == 0, text[-2000:]
        assert 'Captured frame: final.ppm (1280x960)' in text and 'Art assets decoded:' in text
        assert 'chosen path: BA' in text and 'api=adsPlayWalk(1,3,0,3)' in text
        assert 'island backdrop: OCEAN02.SCR' in text, 'Expected current Cartoon day ocean dependency'
        final_pixels = ppm(folder / 'final.ppm')
        (folder / 'final.png').write_bytes(png_bytes(final_pixels))
        observed_rows = [list(map(int, row)) for row in re.findall(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', text)]
        displays = []
        last_row = None
        for line in text.splitlines():
            row = re.search(r'WALKING:.*?data (\d+) (\d+) (\d+) (\d+)', line)
            if row:
                last_row = list(map(int, row.groups()))
            frame = re.search(r'REAR DISPLAY: (\d+) logical_ms=(\d+) file=(\S+)', line)
            if frame:
                index, when, name = frame.groups()
                pixels = ppm(folder / name)
                png = Path(name).with_suffix('.png').name
                (folder / png).write_bytes(png_bytes(pixels))
                displays.append(dict(index=int(index), logical_ms=int(when), stored_walk_row=last_row,
                                     draw_xy=[last_row[1] - 1, last_row[2]], frame=last_row[3],
                                     ppm=name, png=png, pixels_sha256=sha(pixels)))
        if phase == 'smoke':
            assert 'stopping after 1 frame(s)' in text and len(displays) == 1
            assert observed_rows[0] == expected_rows[0]
        else:
            assert observed_rows == expected_rows, observed_rows
            assert 'finite route returned; cleanup complete;' in text
            assert 'WALKING: end walk' in text
            end = len(route) * 120 + 1600
            expected_times = sorted(set(range(0, len(route) * 120 + 1, 120)) | set(range(0, end + 1, 160)) | {end})
            assert [row['logical_ms'] for row in displays] == expected_times, [row['logical_ms'] for row in displays]
            for row in displays:
                position = min(row['logical_ms'] // 120, len(expected_rows) - 1)
                assert row['stored_walk_row'] == expected_rows[position], row
            assert final_pixels == ppm(folder / displays[-1]['ppm'])
        for index, row in enumerate(displays):
            row['duration_ms'] = displays[index + 1]['logical_ms'] - row['logical_ms'] if index + 1 < len(displays) else 0
        dependencies = sorted(set(re.findall(r'Art asset: (\S+)', text)))
        record = dict(status='PASS', phase=phase, exit_code=result.returncode,
                      archive_sha256=sha((folder / 'scrantic_data.zip').read_bytes()),
                      executable_sha256=build['executable_sha256'], island_seed=11,
                      path_seed=int(re.search(r'path_seed=(\d+)', text)[1]),
                      api='adsPlayWalk(1,3,0,3)', actual_path=[1, 0, 6],
                      observed_rows=observed_rows, displays=displays, loaded_art=dependencies,
                      log_sha256=sha((folder / 'capture.log').read_bytes()),
                      final_pixels_sha256=sha(final_pixels),
                      note='Current production Cartoon island and existing fallback rear sprites. No candidate art; actual native API route and original timing, with observation-only linker wrappers. No Windows/EXE pixel-parity claim.')
        save(folder / 'report.json', record)
        reports[phase] = dict(status='PASS', displays=len(displays), path_seed=record['path_seed'])
        print('PASS ' + phase + ': native completion and ' + str(len(displays)) + ' observed display(s)', flush=True)
    assert all(sha((SOURCE / name).read_bytes()) == checksum for name, checksum in protected.items())
    save(OUT / 'summary.json', dict(reports=reports, protected_inputs_unchanged=len(protected),
                                   build_executable_sha256=build['executable_sha256']))


if __name__ == '__main__':
    main()
