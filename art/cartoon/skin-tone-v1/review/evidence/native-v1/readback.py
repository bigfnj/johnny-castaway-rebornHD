"""Read back this frozen browser checkpoint without rerunning native/browser tests."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'assets/scrantic_data.zip').is_file())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-local-originals', action='store_true')
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve earlier readback result'
    evidence = json.loads((HERE / 'evidence.json').read_bytes())
    original_count = 0
    for name, row in evidence['files'].items():
        copied = (HERE / name).read_bytes()
        assert sha(copied) == row['sha256'], 'frozen browser file:' + name
        if args.check_local_originals:
            assert copied == (ROOT / row['source']).read_bytes(), 'exact source copy:' + row['source']
            original_count += 1
    for key in ('native_evidence', 'native_evidence_readback'):
        row = evidence[key]
        assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], 'native link:' + key
    native_readback = json.loads((ROOT / evidence['native_evidence_readback']['path']).read_bytes())
    assert native_readback['evidence_sha256'] == evidence['native_evidence']['sha256'], 'native readback identifies linked evidence'
    publication = json.loads((HERE / 'publication.json').read_bytes())
    assert publication['html_sha256'] == evidence['html_sha256'] == sha((HERE / 'review.html').read_bytes()), 'published HTML consistency'
    report = {'status': 'PASS', 'evidence_sha256': sha((HERE / 'evidence.json').read_bytes()),
              'preserved_files_verified': len(evidence['files']), 'local_originals_verified': original_count,
              'native_evidence_and_readback_verified': True, 'publication_html_verified': True,
              'script_sha256': sha(Path(__file__).read_bytes()),
              'scope': 'Preservation readback only; no native capture, browser or color algorithm test rerun.'}
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS ' + str(len(evidence['files'])) + ' preserved files, ' + str(original_count) + ' exact local copies and linked native evidence/readback')


if __name__ == '__main__':
    main()
