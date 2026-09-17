"""Audit explicitly declared delivery evidence against Git index bytes."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[5]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def git(*args, env=None):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], env=env)


def expected_files(specs):
    expected = {}
    for spec in specs:
        binder = ROOT / spec['binder']
        raw = binder.read_bytes()
        expected[spec['binder']] = sha(raw)
        data = json.loads(raw)
        for field in spec['fields']:
            rows = data[field]
            if isinstance(rows, list):
                rows = {row['path']: row['sha256'] for row in rows}
            for name, digest in rows.items():
                if isinstance(digest, dict):
                    digest = digest['sha256']
                path = (ROOT / spec['base'] / name).resolve().relative_to(ROOT).as_posix()
                if path in expected and expected[path] != digest:
                    raise ValueError(path + ': conflicting binder identities')
                expected[path] = digest
    return expected


def check(expected, env=None):
    index = {}
    for row in git('ls-files', '--stage', '-z', env=env).split(b'\0'):
        if row:
            meta, path = row.decode('utf-8').split('\t', 1)
            _mode, object_id, stage = meta.split()
            if stage == '0':
                index[path] = object_id
    objects = sorted({index[path] for path in expected if path in index})
    run = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '--batch'],
                         input=('\n'.join(objects) + '\n').encode(),
                         capture_output=True, check=True, env=env)
    stream = io.BytesIO(run.stdout)
    digests = {}
    for _ in objects:
        object_id, kind, count = stream.readline().decode().split()
        if kind != 'blob':
            raise ValueError('Expected an indexed blob: ' + object_id)
        digests[object_id] = sha(stream.read(int(count)))
        if stream.read(1) != b'\n':
            raise ValueError('Invalid cat-file framing')
    return [path + ': missing from index' if path not in index else path + ': indexed bytes differ'
            for path, digest in sorted(expected.items())
            if path not in index or digests[index[path]] != digest]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    expected = expected_files(json.loads(args.spec.read_bytes()))
    failures = check(expected)
    if failures:
        print('\n'.join('FAIL ' + text for text in failures))
        return 1
    actual_index = Path(git('rev-parse', '--git-path', 'index').decode().strip())
    if not actual_index.is_absolute():
        actual_index = ROOT / actual_index
    index_before = sha(actual_index.read_bytes())
    scratch_index = output / 'dropped-record.index'
    shutil.copyfile(actual_index, scratch_index)
    env = dict(os.environ, GIT_INDEX_FILE=str(scratch_index))
    victim = next(path for path in sorted(expected) if path.endswith('capture.log'))
    git('update-index', '--force-remove', '--', victim, env=env)
    negative = check(expected, env)
    if negative != [victim + ': missing from index']:
        raise ValueError('Dropped-record control did not report exactly its missing path: ' + repr(negative))
    shutil.copyfile(actual_index, scratch_index)
    corrupt = subprocess.run(['git', '-C', str(ROOT), 'hash-object', '-w', '--stdin'],
                             input=b'Controlled wrong evidence bytes\n', capture_output=True, check=True)
    object_id = corrupt.stdout.decode().strip()
    git('update-index', '--cacheinfo', '100644,' + object_id + ',' + victim, env=env)
    wrong_bytes = check(expected, env)
    if wrong_bytes != [victim + ': indexed bytes differ']:
        raise ValueError('Wrong-byte control did not report exactly its changed path: ' + repr(wrong_bytes))
    if check(expected) or sha(actual_index.read_bytes()) != index_before:
        raise ValueError('Actual index changed during the disposable-index control')
    report = {'status': 'PASS', 'bound_files': len(expected),
              'spec_sha256': sha(args.spec.read_bytes()), 'checker_sha256': sha(Path(__file__).read_bytes()),
              'files_sha256': expected, 'negative_failure': negative,
              'wrong_bytes_failure': wrong_bytes,
              'actual_index_unchanged': True,
              'scope': 'Explicit binder copied/external fields and each binder itself. '
                       'Scratch captures and external original resources are not inferred as copied files.'}
    (output / 'result.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps({'status': 'PASS', 'bound_files': len(expected),
                      'dropped_record_failure': negative, 'wrong_bytes_failure': wrong_bytes}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
