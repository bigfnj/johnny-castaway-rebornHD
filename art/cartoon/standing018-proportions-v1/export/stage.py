"""Stage exact frozen018 export tools and an explicit new raw in ignored scratch.

This adapter copies bytes only. Rendering remains the original arrival exporter.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
PRIOR = ROOT / 'art/cartoon/arrival-pilot-v1'
PINS = {
    'export.py': 'c382582ad113c917ee8b5f8e0ebda392ceb5f746bdb4be9982b7a51f04418c63',
    'test_export.py': 'efa45c937304cadc39bfd89a5c3160b886cd0a6c44d810c4a53d68b394b9b456',
    'reference/source.json': 'bd2ba0025626593641c575b794d9380bf66613dae9b7f456d5715aa810d9ceae',
    'reference/metadata.json': '130dcd25e05c45e22143adca37cb139679523f8dc4a84abce14efc9a170982d5',
    'reference/018-native.png': 'd4390dbd4e9df53d506dbedf540c4a2a0d867c23d3c5221743dad0bf07d2dbd8',
    'reference/018-nearest8.png': '228783a6a48523333a069592318308967e75537b83bb1a446c85c69fa7181c7a',
}
LEGACY = 'art/cartoon/walk-expansion-v1/export.py'
LEGACY_SHA = 'd467dc20eaf640c83dcd60568135e44234bbf27875448f8f801e126d01c9f09e'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def stage(source, work, expected):
    source, work = source.resolve(), work.resolve()
    require(work.is_relative_to(ROOT / 'build') and work != ROOT / 'build', 'staging-outside-build')
    require(not work.exists(), 'staging-already-exists')
    require(source.is_relative_to(ROOT) and source.suffix.lower() == '.png', 'source-path')
    raw = source.read_bytes()
    require(sha(raw) == expected, 'source-identity:018')
    files = {name: (PRIOR / name).read_bytes() for name in PINS}
    for name, payload in files.items():
        require(sha(payload) == PINS[name], 'frozen-input:' + name)
    require(sha((ROOT / LEGACY).read_bytes()) == LEGACY_SHA, 'frozen-legacy-export')
    files[source.name] = raw
    authoring = work / 'authoring'
    authoring.mkdir(parents=True, exist_ok=False)
    for name, payload in files.items():
        destination = authoring / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        require(destination.read_bytes() == payload, 'staged-copy:' + name)
    record = {
        'schema_version': 1, 'scope': 'Byte-exact staging only; no render, pose or color acceptance.',
        'source': {'path': source.relative_to(ROOT).as_posix(), 'sha256': expected},
        'work': work.relative_to(ROOT).as_posix(),
        'frozen_inputs_sha256': PINS, 'staged_files_sha256': {name: sha(payload) for name, payload in files.items()},
        'legacy': {'path': LEGACY, 'sha256': LEGACY_SHA},
        'adapter_sha256': sha(Path(__file__).read_bytes()),
        'contract': {'frame': 18, 'scale': .1, 'cap_target_hd': [17, .25], 'runtime_canvas': [64, 154]},
        'note': 'Call staged export.py and test_export.py. Supply the retained legacy path explicitly to tests.'}
    (work / 'staging.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    print('WITNESS stage.py SHA256=' + sha(Path(__file__).read_bytes()), flush=True)
    try:
        result = stage(args.source, args.work, args.source_sha256)
    except (ValueError, OSError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1
    print('PASS byte-exact018 authoring staging: ' + result['work'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
