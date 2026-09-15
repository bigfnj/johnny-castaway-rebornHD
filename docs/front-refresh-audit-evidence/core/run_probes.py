"""Compile untouched main source into tiny headless boundary probes."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/src')
OUT = Path('/out')
probe_root = ROOT / 'build/front-refresh-postmerge-audit/core'
records = []


def run(label, command, cwd=None, timeout=10):
    try:
        p = subprocess.run(command, cwd=cwd, capture_output=True, timeout=timeout)
        result = {'label': label, 'command': command, 'exit_code': p.returncode,
                  'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(), 'timeout': False}
    except subprocess.TimeoutExpired as e:
        result = {'label': label, 'command': command, 'exit_code': None,
                  'stdout': (e.stdout or b'').decode(), 'stderr': (e.stderr or b'').decode(), 'timeout': True}
    records.append(result)
    print(json.dumps(result), flush=True)
    return result


common = ['gcc', '-O0', '-g', '-ffunction-sections', '-fdata-sections', '-I/src/src/engine', '-I/src/platform']
tag = OUT / 'ttm_tag_probe'
dump = OUT / 'dump_write_probe'
assert run('build-ttm', common + [str(probe_root / 'ttm_tag_probe.c'), '/src/src/engine/ttm.c',
    '/src/src/engine/utils.c', '-Wl,--gc-sections', '-Wl,--wrap=malloc', '-o', str(tag)])['exit_code'] == 0
assert run('build-dump', common + [str(probe_root / 'dump_write_probe.c'), '/src/src/engine/utils.c',
    '-Wl,--gc-sections', '-Wl,--wrap=fclose', '-o', str(dump)])['exit_code'] == 0
valid = run('valid-tag-control', [str(tag), 'valid'])
assert valid['exit_code'] == 0 and 'tag7=4 missing8=0' in valid['stdout']
pattern = run('missing-tag-pattern', [str(tag), 'pattern'])
assert pattern['exit_code'] == 0 and 'sentinel lookup returned 2779096485' in pattern['stdout']
zero = run('missing-tag-zero', [str(tag), 'zero'], timeout=1)
assert zero['timeout'] and 'sentinel-id=65535' in zero['stdout'] and 'lookup returned' not in zero['stdout']
for label in ('dump-regular-control', 'dump-full-device'):
    work = OUT / label
    target = work / 'dump/BMP/PROBE.BMP.000.xpm'
    target.parent.mkdir(parents=True)
    if label.endswith('device'):
        target.symlink_to('/dev/full')
    result = run(label, [str(dump)], cwd=work)
    assert result['exit_code'] == 0 and 'dumpBmp returned normally' in result['stdout']
    assert ('fclose result=-1 errno=28' if label.endswith('device') else 'fclose result=0') in result['stderr']
evidence = {'source_commit': '71f3e5f8d158e4d6a7315fe633d3c9944a4b21e5',
            'method': 'Untouched ttm.c/dump.c/utils.c; deterministic allocator-fill and observed fclose wrappers; no renderer/UI or production resource mutation.',
            'scope': 'Malformed TTM metadata and output I/O failure, not evidence of a shipped-scene regression.',
            'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                ('src/engine/ttm.c', 'src/engine/dump.c', 'src/engine/utils.c')},
            'executables_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (tag, dump)},
            'records': records}
(OUT / 'probe-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
