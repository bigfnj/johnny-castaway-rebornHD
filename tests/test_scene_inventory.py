#!/usr/bin/env python3
"""Small synthetic inventory controls and isolated compiled-Python mutations.

No original files or graphical engine are needed. Every mutation invokes one
named behavioral fixture through freshly compiled bytecode and requires its
case-specific runtime witness and exactly one intended failed assertion.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import py_compile
import re
import struct
import subprocess
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools/inventory_scenes.py'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rejected(call, expected):
    try:
        call()
    except ValueError as error:
        require(expected in str(error), 'wrong diagnostic: ' + expected)
    except Exception as error:
        raise AssertionError('wrong exception: ' + expected) from error
    else:
        raise AssertionError('not rejected: ' + expected)


def map_fixture(names=('ONE.BIN',)):
    volume, offsets = bytearray(), []
    for name in names:
        offsets.append(len(volume))
        volume += name.encode().ljust(13, b'\0') + struct.pack('<I', 3) + b'abc'
    index = b'\0' * 6 + b'RESOURCE.001\0' + struct.pack('<H', len(offsets))
    index += b''.join(struct.pack('<II', 0, offset) for offset in offsets)
    return index, bytes(volume)


def metadata_fixture(kind):
    if kind == 'BMP':
        return b'\0' * 8 + b'INF:' + b'\0' * 4 + struct.pack('<H', 2)
    script = b'\x01' + struct.pack('<I', 0) + b'\0'
    tags = b'TAG:' + b'\0' * 4 + struct.pack('<HH', 1, 7) + b'Entry\0'
    if kind == 'ADS':
        return b'\0' * 21 + b'RES:' + b'\0' * 4 + struct.pack('<HH', 1, 0) + b'ONE.TTM\0' + b'SCR:' + struct.pack('<I', len(script)) + script + tags
    return b'\0' * 21 + struct.pack('<H', 1) + b'TT3:' + struct.pack('<I', len(script)) + script + b'TTI:' + b'\0' * 4 + tags


def probe_fixture(module, data=b'\x01\x00', *, size=2, consumed=1, code=0, kind='ADS'):
    resource = {'name': 'PROBE.' + kind, 'type': kind, 'compression_method': 2,
                '_compressed': b'x', 'script_bytes': size}
    result = subprocess.CompletedProcess([], code, 'RESULT ' + data.hex() + ' consumed=' + str(consumed) + '\n', '')
    with patch.object(module.subprocess, 'run', return_value=result):
        module.decode(resource, Path('unused-probe'))
    return resource


def story_fixture(directory, rows, count):
    path = directory / 'src/data/story_data.h'
    path.parent.mkdir(parents=True)
    path.write_text('#define NUM_SCENES ' + str(count) + '\n' + rows, encoding='utf-8')


def run_case(module, name):
    if name == 'smoke':
        index, volume = map_fixture(('ONE.BIN', 'TWO.BIN'))
        _, catalog = module.resource_catalog(index, volume)
        require(list(catalog) == ['ONE.BIN', 'TWO.BIN'], 'two distinct resources retained')
        require(catalog['TWO.BIN']['_payload'] == b'abc', 'map offset selects payload')
        for kind in ('BMP', 'ADS', 'TTM'):
            resource = {'name': 'VALID.' + kind, 'type': kind, '_payload': metadata_fixture(kind)}
            module.metadata(resource)
        require(probe_fixture(module)['script_tag_ids'] == [1], 'decoded ADS tag retained')
        resource = {'name': 'MIXED.TTM', 'compression_method': 1,
                    '_compressed': (b'\x03abc\x82Z' * 1400), 'script_bytes': 7000}
        parts = module.compressed_parts(resource)
        require(len(parts) > 1 and b''.join(p for p, _ in parts) == resource['_compressed'], 'split preserves every RLE packet')
        require(sum(size for _, size in parts) == 7000, 'mixed literal and run lengths retained')
        original = {'_commands': [{'offset': 0, 'command': 'SET_DELAY', 'args': [0]}, {'offset': 4, 'command': 'UPDATE', 'args': []}]}
        shifted = {'_commands': [{'offset': 20, 'command': 'SET_DELAY', 'args': [0]}, {'offset': 24, 'command': 'UPDATE', 'args': []}]}
        removed = {'_commands': [{'offset': 0, 'command': 'UPDATE', 'args': []}]}
        require(module.command_changes(original, shifted) == [], 'offset-only changes ignored')
        change = module.command_changes(original, removed)
        require(len(change) == 1 and change[0]['original_commands'] == original['_commands'][:1], 'real removed delay detected')
        require('_payload' not in module.public(catalog['ONE.BIN']), 'private resource bytes excluded')
    elif name in ('map_length', 'map_duplicate', 'map_payload'):
        index, volume = map_fixture(('ONE.BIN', 'ONE.BIN') if name == 'map_duplicate' else ('ONE.BIN',))
        if name == 'map_length':
            index += b'x'
        elif name == 'map_payload':
            volume = volume[:-1]
        rejected(lambda: module.resource_catalog(index, volume), 'entry count' if name == 'map_length' else 'Invalid or duplicate resource')
    elif name.startswith('metadata_'):
        kind, marker = {'metadata_bmp': ('BMP', b'INF:'), 'metadata_res': ('ADS', b'RES:'),
                        'metadata_script': ('TTM', b'TT3:'), 'metadata_tti': ('TTM', b'TTI:'),
                        'metadata_tag': ('TTM', b'TAG:')}[name]
        data = metadata_fixture(kind).replace(marker, b'BAD!')
        resource = {'name': 'BAD.' + kind, 'type': kind, '_payload': data}
        rejected(lambda: module.metadata(resource), {'metadata_bmp': 'missing BMP INF', 'metadata_res': 'missing RES',
                 'metadata_script': 'missing script', 'metadata_tti': 'missing TTI', 'metadata_tag': 'missing TAG'}[name])
    elif name in ('rle_packet', 'rle_size'):
        resource = {'name': 'BAD.TTM', 'compression_method': 1, '_compressed': b'\x82' if name == 'rle_packet' else b'\x83Z', 'script_bytes': 2}
        rejected(lambda: module.compressed_parts(resource), 'truncated RLE packet' if name == 'rle_packet' else 'RLE size differs')
    elif name in ('probe_exit', 'probe_size', 'probe_consumption', 'script_padding'):
        kwargs = {'probe_exit': {'code': 1}, 'probe_size': {'size': 3}, 'probe_consumption': {'consumed': 0},
                  'script_padding': {'data': b'\x1f\xf0AB\0', 'size': 5, 'kind': 'TTM'}}[name]
        rejected(lambda: probe_fixture(module, **kwargs), 'decompressor failed' if name == 'probe_exit' else 'command exceeds' if name == 'script_padding' else 'incomplete decompression')
    elif name.startswith('story_'):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = '{ "TEST.ADS", 1, 0, 0, 0, 0, 0, ISLAND | FINAL }\n'
            if name == 'story_witness':
                rows = rows.replace(' | FINAL', '')
            if name == 'story_controls':
                rows += '// { "TEST.ADS", 9, 0, 0, 0, 0, 0, ISLAND } // alias\n{ "TEST.ADS", 2, 0, 0, 0, 0, 6, ISLAND | FIRST }\n'
            story_fixture(root, rows, 0 if name == 'story_count' else 2 if name == 'story_controls' else 1)
            if name == 'story_controls':
                scenes, excluded = module.scheduler(root)
                require(len(scenes) == 2 and excluded[0]['scene'] == 'TEST.ADS#9', 'comments excluded from active story')
                require(scenes[1]['eligible_days'] == [6] and scenes[1]['leadup_witnesses'] == {'6': 'TEST.ADS#1'}, 'day and FIRST lead-in witness preserved')
            else:
                rejected(lambda: module.scheduler(root), 'count differs' if name == 'story_count' else 'no eligible final predecessor')
    elif name in ('golden_mismatch', 'golden_exit'):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'tests').mkdir()
            expected_hash = '0' * 64 if name == 'golden_mismatch' else module.digest(b'changed')
            (root / 'tests/golden-dump.sha256').write_text(expected_hash + '  one.txt\n', encoding='utf-8')
            (root / 'archive.zip').write_bytes(b'fixture only')
            def fake_dump(*args, **kwargs):
                output = kwargs['cwd'] / 'dump'
                output.mkdir()
                (output / 'one.txt').write_text('changed', encoding='utf-8')
                return subprocess.CompletedProcess([], int(name == 'golden_exit'), '', '')
            with patch.object(module.subprocess, 'run', side_effect=fake_dump):
                rejected(lambda: module.dump_validation(Path('unused'), root / 'archive.zip', root),
                         "Golden dump differs in 1 files: ['one.txt']" if name == 'golden_mismatch' else 'Production dump failed')
    else:
        raise AssertionError('unknown fixture: ' + name)


MUTATIONS = [
    ('map_length', 'resource_catalog', 'if pos + count * 8 != len(map_bytes):', 'if False:'),
    ('map_duplicate', 'resource_catalog', 'if name in result or len(payload) != size:', 'if len(payload) != size:'),
    ('map_payload', 'resource_catalog', 'if name in result or len(payload) != size:', 'if name in result:'),
    ('metadata_bmp', 'metadata', "if data[8:12] != b'INF:':", 'if False:'),
    ('metadata_res', 'metadata', "if data[pos:pos + 4] != b'RES:':", 'if False:'),
    ('metadata_script', 'metadata', 'if data[pos:pos + 4] != expected:', 'if False:'),
    ('metadata_tti', 'metadata', "if data[pos:pos + 4] != b'TTI:':", 'if False:'),
    ('metadata_tag', 'metadata', "if data[pos:pos + 4] != b'TAG:':", 'if False:'),
    ('rle_packet', 'compressed_parts', 'if pos + consumed > len(data):', 'if False:'),
    ('rle_size', 'compressed_parts', "if sum(size for _, size in parts) != resource['script_bytes']:", 'if False:'),
    ('probe_exit', 'decode', 'if result.returncode or not match:', 'if not match:'),
    ('probe_size', 'decode', 'if len(part) != size or int(match[2]) != len(compressed):', 'if int(match[2]) != len(compressed):'),
    ('probe_consumption', 'decode', 'if len(part) != size or int(match[2]) != len(compressed):', 'if len(part) != size:'),
    ('script_padding', 'decode', 'if pos > len(data):', 'if False:'),
    ('story_count', 'scheduler', 'if len(result) != declared:', 'if False:'),
    ('story_witness', 'scheduler', 'if not finals:', 'if False:'),
    ('golden_mismatch', 'dump_validation', 'if mismatches:', 'if False:'),
    ('golden_exit', 'dump_validation', 'if result.returncode:', 'if False:'),
]

DIAGNOSTICS = {
    'map_length': 'entry count', 'map_duplicate': 'Invalid or duplicate resource', 'map_payload': 'Invalid or duplicate resource',
    'metadata_bmp': 'missing BMP INF', 'metadata_res': 'missing RES', 'metadata_script': 'missing script',
    'metadata_tti': 'missing TTI', 'metadata_tag': 'missing TAG', 'rle_packet': 'truncated RLE packet', 'rle_size': 'RLE size differs',
    'probe_exit': 'decompressor failed', 'probe_size': 'incomplete decompression', 'probe_consumption': 'incomplete decompression',
    'script_padding': 'command exceeds', 'story_count': 'count differs', 'story_witness': 'no eligible final predecessor',
    'golden_mismatch': "Golden dump differs in 1 files: ['one.txt']", 'golden_exit': 'Production dump failed',
}


def load_module(path):
    spec = importlib.util.spec_from_file_location('inventory_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutations', action='store_true')
    parser.add_argument('--case')
    parser.add_argument('--module', type=Path, default=SOURCE)
    args = parser.parse_args()
    if args.case:
        try:
            run_case(load_module(args.module), args.case)
        except AssertionError as error:
            print(json.dumps({'file': 'tools/inventory_scenes.py', 'case': args.case, 'status': 'FAIL', 'assertion': str(error)}))
            return 1
        print(json.dumps({'case': args.case, 'status': 'PASS'}))
        return 0
    module = load_module(SOURCE)
    cases = ['smoke', 'story_controls'] + [row[0] for row in MUTATIONS]
    for case in cases:
        run_case(module, case)
        print(json.dumps({'case': case, 'status': 'PASS'}), flush=True)
    if args.mutations:
        text = SOURCE.read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='johnny-inventory-mutations-') as temporary:
            root = Path(temporary)
            for case, function, old, new in MUTATIONS:
                require(text.count(old) == 1, case + ': unique mutation anchor')
                mutated = text.replace(old, new)
                witness = 'WITNESS inventory-mutation:' + case
                mutated, count = re.subn(r'(^def ' + function + r'\([^\n]*\):\n)', lambda m: m[0] + '    print(' + repr(witness) + ')\n', mutated, count=1, flags=re.M)
                require(count == 1, case + ': witness insertion')
                source, artifact = root / (case + '.py'), root / (case + '.pyc')
                source.write_text(mutated, encoding='utf-8')
                artifact.write_bytes(b'not bytecode')
                previous = artifact.stat().st_mtime_ns
                py_compile.compile(str(source), cfile=str(artifact), doraise=True)
                require(artifact.stat().st_mtime_ns > previous, case + ': compiled artifact timestamp advanced')
                result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--module', str(artifact), '--case', case], capture_output=True, text=True, timeout=20)
                records = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
                require(result.stdout.splitlines().count(witness) == 1, case + ': actual mutated function executed')
                require(result.returncode == 1 and len(records) == 1 and records[0]['case'] == case and records[0]['status'] == 'FAIL', case + ': exactly one named failure')
                expected = records[0]['assertion']
                prefix = 'wrong exception: ' if case == 'story_witness' else 'not rejected: '
                require(expected == prefix + DIAGNOSTICS[case], case + ': intended rejection assertion fired')
                print(json.dumps({'file': 'tools/inventory_scenes.py', 'case': case, 'mutation': 'FIRED', 'assertion': expected, 'rebuilt': True, 'witness': witness}), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
