"""Fresh-process reproduction and damaged-input checks for the complete worklist.

Standard library only. All damaged files and mutant outputs stay in --work.
The tests verify inventory mechanics, not the human visual classifications.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import warnings
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.relative_to(ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


def changed_png(data):
    """Change a real decompressed pixel sample and rebuild valid PNG checksums."""
    chunks, position = [], 8
    while position < len(data):
        length = struct.unpack_from('>I', data, position)[0]
        kind = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        chunks.append((kind, payload))
        position += length + 12
    raw = bytearray(zlib.decompress(b''.join(p for k, p in chunks if k == b'IDAT')))
    raw[-1] ^= 1
    replacement = zlib.compress(bytes(raw))
    result, written = bytearray(data[:8]), False
    for kind, payload in chunks:
        if kind == b'IDAT':
            if written:
                continue
            payload, written = replacement, True
        result.extend(struct.pack('>I', len(payload)) + kind + payload)
        result.extend(struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))
    return bytes(result)


def copy_fixture(work):
    """Copy precisely the maintained production catalog's file dependencies."""
    sys.path.insert(0, str(ROOT / 'tools'))
    import art_production_catalog
    production = art_production_catalog.build(ROOT)
    names = {name for name in production['inputs'] if '!' not in name}
    names.add('assets/scrantic_data.zip')
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'tools').glob('*.py'))
    names.update(str(BASE / relative) for relative in (
        'source/frame-index.json', 'reference-originals.zip',
        'scene-map/resource-map.json', 'inventory.json', 'README.md'))
    names.update(p.relative_to(ROOT).as_posix() for p in (HERE / 'classification').glob('*.json'))
    fingerprints = {}
    for name in sorted(names):
        source = ROOT / name
        target = work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        target.write_bytes(data)
        fingerprints[Path(name).as_posix()] = sha(data)
    return fingerprints


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.work.exists():
        raise ValueError('--work must be a fresh directory')
    args.work.mkdir(parents=True)
    helper = HERE / 'build_inventory.py'
    helper_bytes = helper.read_bytes()
    helper_hash = sha(helper_bytes)
    runs = []

    def invoke(label, root, expected=None, script=helper, check=True):
        checksum = sha(script.read_bytes())
        command = [sys.executable, '-B', str(script), '--root', str(root)]
        if check:
            command.append('--check')
        completed = subprocess.run(command, cwd=ROOT, capture_output=True,
                                   text=True, encoding='utf-8', timeout=180)
        stdout, stderr = completed.stdout, completed.stderr
        (args.work / (label + '.stdout.txt')).write_text(stdout, encoding='utf-8', newline='\n')
        (args.work / (label + '.stderr.txt')).write_text(stderr, encoding='utf-8', newline='\n')
        assert 'WITNESS character-inventory ' + checksum in stdout, (label, 'executed helper witness missing', stdout)
        assert completed.returncode == (1 if expected else 0), (label, completed.returncode, stdout, stderr)
        if expected:
            assert stderr.strip() == 'ERROR ' + expected, (label, stderr)
        else:
            assert 'PASS character-inventory ' in stdout and not stderr, (label, stdout, stderr)
        runs.append({'name': label, 'helper_sha256': checksum, 'returncode': completed.returncode,
                     'result': 'FIRED' if expected else 'PASS', 'expected_failure': expected,
                     'stdout': stdout, 'stderr': stderr})

    # The first smoke runs the maintained CLI against real current inputs and
    # compares both generated files. No fixture or cached catalog grants PASS.
    invoke('current_full_catalog_reproduction', ROOT)
    report = {'schema_version': 1, 'phase': args.phase, 'status': 'PASS',
              'helper_sha256': helper_hash, 'test_sha256': sha(Path(__file__).read_bytes()),
              'inventory_sha256': sha((HERE / 'inventory.json').read_bytes()),
              'readme_sha256': sha((HERE / 'README.md').read_bytes()),
              'summary': json.loads((HERE / 'inventory.json').read_bytes())['summary'],
              'scope': 'Mechanics and input identity only. Visual labels, original executable colors and scene execution are not independently validated.'}
    if args.phase == 'smoke':
        report.update(runs=runs, negative_controls_fired=0, mutation_check='not run in smoke')
        write_json(args.report, report)
        print('PASS inventory smoke: complete catalog and README reproduce')
        return 0

    fixture = args.work / 'fixture'
    fingerprints = copy_fixture(fixture)
    base = fixture / BASE
    watched = [base / 'source/frame-index.json', base / 'reference-originals.zip',
               base / 'inventory.json', base / 'README.md', *sorted((base / 'classification').glob('*.json'))]
    clean = {path: path.read_bytes() for path in watched}

    def restore():
        for path, data in clean.items():
            path.write_bytes(data)

    classifier = base / 'classification/gj-family.json'
    classifier_value = json.loads(clean[classifier])
    resource = classifier_value['resources'][0]['resource']
    invoke('isolated_positive_before', fixture)
    try:
        value = json.loads(clean[classifier])
        value['source_index_sha256'] = '0' * 64
        write_json(classifier, value)
        invoke('stale_source_pin', fixture, 'gj-family.json: stale source index', check=False)
        restore()

        value = json.loads(clean[classifier])
        removed = value['resources'].pop(0)['resource']
        write_json(classifier, value)
        invoke('missing_resource', fixture, f"classification: missing resources {[removed]}", check=False)
        restore()

        value = json.loads(clean[classifier])
        first = value['resources'][0]['overrides'][0]
        repeated = first['frames'][0]
        first['frames'].append(repeated)
        write_json(classifier, value)
        invoke('duplicate_override', fixture, f'{resource}: duplicate override for frame {repeated}', check=False)
        restore()

        value = json.loads(clean[classifier])
        value['resources'][0]['overrides'][0]['frames'].append(1000000)
        write_json(classifier, value)
        invoke('unknown_frame', fixture, f'{resource}: override has unknown frame 1000000', check=False)
        restore()

        value = json.loads(clean[classifier])
        value['resources'][0]['reviewed_pages'].pop()
        write_json(classifier, value)
        invoke('reviewed_page_coverage', fixture, f'{resource}: incomplete reviewed-page coverage', check=False)
        restore()

        source_path = base / 'source/frame-index.json'
        index = json.loads(clean[source_path])
        # Hide one genuinely shipped slot. Classification and reference PNG
        # coverage stay complete, so the full build must catch lost port mapping.
        slot = next(r for r in index['frames'] if r['id'] == 'BMP/GJGULL1.BMP/000')
        slot['bundled'] = None
        write_json(source_path, index)
        new_source = sha(source_path.read_bytes())
        for path in (base / 'classification').glob('*.json'):
            value = json.loads(clean[path])
            value['source_index_sha256'] = new_source
            write_json(path, value)
        invoke('port_coverage_mismatch', fixture, 'source index: port coverage mismatch', check=False)
        restore()

        archive_path = base / 'reference-originals.zip'
        member = 'native/BMP/JOHNWALK.BMP/018.png'
        with zipfile.ZipFile(archive_path) as archive:
            contents = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]
        with zipfile.ZipFile(archive_path, 'w') as archive:
            for entry, data in contents:
                if entry.filename != member:
                    archive.writestr(entry, data)
        invoke('missing_preserved_zip_member', fixture, 'reference-originals.zip: member coverage differs from source index', check=False)
        restore()

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Duplicate name:', category=UserWarning)
            with zipfile.ZipFile(archive_path, 'a') as archive:
                entry, data = next((entry, data) for entry, data in contents if entry.filename == member)
                archive.writestr(entry, data)
        invoke('duplicate_preserved_zip_member', fixture, 'reference-originals.zip: duplicate ZIP member', check=False)
        restore()

        corrupted = changed_png(dict((entry.filename, data) for entry, data in contents)[member])
        with zipfile.ZipFile(archive_path, 'w') as archive:
            for entry, data in contents:
                archive.writestr(entry, corrupted if entry.filename == member else data)
        invoke('altered_preserved_png', fixture, 'BMP/JOHNWALK.BMP/018: preserved PNG hash mismatch', check=False)

        statement = "            require(digest(data) == row['png_sha256'], row['id'], 'preserved PNG hash mismatch')"
        source = helper_bytes.decode('utf-8')
        assert source.count(statement) == 1, 'mutant must remove exactly one guard'
        mutant = source.replace(statement, '            pass  # executed control: preserved PNG identity guard removed', 1).encode('utf-8')
        mutant_path = args.work / 'build_inventory-preserved-png-guard-removed.py'
        mutant_path.write_bytes(mutant)
        # __file__ parents lookup is valid at this absolute scratch depth;
        # explicit --root selects the isolated fixture. Its own CLI hashes the
        # copied mutant bytes, then executes the real full builder.
        invoke('corrupt_png_accepted_only_by_guard_removed_mutant', fixture, script=mutant_path, check=False)
        mutation = {'artifact': mutant_path.name, 'sha256': sha(mutant),
                    'corrupt_member': member, 'corrupt_png_sha256': sha(corrupted),
                    'change': 'Exactly one preserved PNG digest guard removed.',
                    'witness': 'WITNESS character-inventory ' + sha(mutant),
                    'result': 'FIRED: original rejects changed PNG; copied executed mutant accepts the same archive.'}
        restore()
        invoke('isolated_positive_after_restoration', fixture)
    finally:
        restore()
    assert helper.read_bytes() == helper_bytes, 'maintained builder changed during verification'
    for name, checksum in fingerprints.items():
        assert sha((ROOT / name).read_bytes()) == checksum, 'live input changed: ' + name
    report.update(runs=runs, negative_controls_fired=sum(r['result'] == 'FIRED' for r in runs),
                  mutation_check=mutation, inputs_sha256=fingerprints,
                  original_inputs_unchanged=True, fixture_restored=True)
    write_json(args.report, report)
    print('PASS inventory regression: ' + str(report['negative_controls_fired']) + ' named negatives and executed guard-removal proof')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
