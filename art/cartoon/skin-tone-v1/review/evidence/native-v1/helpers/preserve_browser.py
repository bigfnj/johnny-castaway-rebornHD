"""Preserve a new browser checkpoint and link the separately frozen native evidence."""
import argparse
import json
from pathlib import Path

import publish_native

config = publish_native.config
HERE = Path(__file__).resolve().parent


def publication_identity(review):
    publication = config.load_json(review / 'publication.json')
    assert publication['status'] == 'PASS', 'successful publication first'
    publish_native.identity((review / 'review-record.json').read_bytes(), publication['review_record_sha256'], 'published review record')
    publish_native.identity((review / 'browser-validation.json').read_bytes(), publication['browser_validation_sha256'], 'published local browser checks')
    record, checked, candidate = publish_native.checkpoint_identity(review)
    assert publication['html_sha256'] == record['files_sha256']['review.html'], 'published HTML identity'
    assert publication['candidate_archive_sha256'] == record['candidate_archive_sha256'] and publication['recipe_sha256'] == record['recipe_sha256'], 'published color selection'
    publish_native.identity((candidate / 'preparation.json').read_bytes(), publication['candidate_preparation_sha256'], 'published candidate preparation')
    served = config.load_json(review / 'publication-browser.json')
    assert served == publication['browser_smoke_then_regression'], 'published served-browser record'
    for name, digest in publication['guard_records_sha256'].items():
        publish_native.identity((config.ROOT / name).read_bytes(), digest, 'published guard:' + name)
    return publication, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--native-evidence', type=Path, required=True)
    parser.add_argument('--native-evidence-sha256', required=True)
    parser.add_argument('--browser-controls', type=Path, required=True)
    parser.add_argument('--builder-controls', type=Path, required=True)
    parser.add_argument('--readback-controls', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve historical browser checkpoint'
    publication, record = publication_identity(args.review)
    publish_native.identity(args.native_evidence.read_bytes(), args.native_evidence_sha256, 'frozen native evidence')
    native_readback_path = args.native_evidence.parent / 'readback.json'
    native_readback = config.load_json(native_readback_path)
    assert native_readback['status'] == 'PASS' and native_readback['evidence_sha256'] == args.native_evidence_sha256, 'native evidence independent readback'
    readback = config.load_json(args.readback_controls)
    assert readback['status'] == 'PASS' and readback['html_sha256'] == publication['html_sha256'], 'executed publication readback controls'
    sources = {}
    for name in ('review.html', 'review-record.json', 'browser-validation.json', 'publication-browser.json', 'publication.json'):
        sources[name] = args.review / name
    for folder_name, path in [('browser-controls', args.browser_controls), ('builder-controls', args.builder_controls)]:
        for source in path.rglob('*'):
            if source.is_file() and source.suffix in ('.json', '.txt', '.html'):
                sources[folder_name + '/' + source.relative_to(path).as_posix()] = source
    sources['browser-controls.json'] = args.browser_controls.with_suffix('.json')
    sources['publication-readback.json'] = args.readback_controls
    for source in HERE.iterdir():
        if source.is_file() and source.suffix in ('.py', '.html', '.md'):
            sources['helpers/' + source.name] = source
    args.output.mkdir(parents=True)
    copies = {}
    for name, path in sources.items():
        raw = path.read_bytes()
        target = args.output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        assert target.read_bytes() == raw, 'exact browser evidence copy:' + name
        copies[name] = {'source': path.resolve().relative_to(config.ROOT).as_posix(), 'sha256': config.sha(raw)}
    # Recheck inputs after copying; preserve no success binder on a changed source.
    publication_identity(args.review)
    native = {'path': args.native_evidence.resolve().relative_to(config.ROOT).as_posix(), 'sha256': args.native_evidence_sha256}
    result = {'status': 'PASS; published technical color review; human corrected-output approval pending at capture',
              'url': publication['url'], 'html_sha256': publication['html_sha256'], 'recipe_sha256': publication['recipe_sha256'],
              'candidate_archive_sha256': publication['candidate_archive_sha256'], 'native_evidence': native,
              'native_evidence_readback': {'path': native_readback_path.resolve().relative_to(config.ROOT).as_posix(), 'sha256': config.sha(native_readback_path.read_bytes())},
              'files': copies, 'native_source_scope': 'The linked native binder preserves capture reports, preparations, adapters, helpers, native/input controls and retained first-launch failure. Those files are not duplicated here.',
              'limits': ['Full native PNGs, PPMs, private ZIPs and binaries remain local or reconstructable. Their hashes remain bound by the native and browser records.',
                         'Browser screenshots and generated contact sheets remain local with hashes in browser/still records.',
                         'This checkpoint preserves the published review and technical checks. Human color approval is separate.',
                         'One-time preservation writer. Do not rerun into an existing historical evidence path.']}
    (args.output / 'evidence.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS preserved browser publication with ' + str(len(copies)) + ' exact small files and linked native evidence')


if __name__ == '__main__':
    main()
