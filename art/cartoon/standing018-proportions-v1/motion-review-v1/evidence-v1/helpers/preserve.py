"""Freeze compact018 browser evidence without all native images or private ZIPs."""
import argparse
import json
from pathlib import Path
import build_review as build


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--negatives', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists(), 'preserve earlier018 browser binder'
    record = build.load(a.review / 'review-record.json')
    publication = build.load(a.review / 'publication.json')
    assert publication['status'] == 'PASS' and publication['review_record_sha256'] == build.sha((a.review / 'review-record.json').read_bytes()), 'exact published018 record'
    assert publication['html_sha256'] == build.sha((a.review / 'review.html').read_bytes()) == record['files_sha256']['review.html'], 'exact published018 HTML'
    files = {}
    for name, digest in record['files_sha256'].items():
        if not name.startswith('images/'):
            raw = (a.review / name).read_bytes()
            assert build.sha(raw) == digest, 'retained018 bound file:' + name
            files['review/' + name] = raw
    for name in ('review-record.json', 'browser-validation.json', 'publication-browser.json', 'publication.json'):
        files['review/' + name] = (a.review / name).read_bytes()
    for name, digest in publication['screenshots_sha256'].items():
        raw = (a.review / name).read_bytes()
        assert build.sha(raw) == digest, 'published screenshot identity:' + name
        files['review/' + name] = raw
    for name in ('browser-validation-waypoint_front-frame023-1280.png', 'browser-validation-waypoint_front-frame018-1280.png'):
        raw = (a.review / name).read_bytes()
        assert build.sha(raw) == build.load(a.review / 'browser-validation.json')['screenshots_sha256'][name], 'local transition screenshot identity'
        files['review/' + name] = raw
    files['negatives/result.json'] = (a.negatives / 'result.json').read_bytes()
    failed = build.ROOT / 'build/standing018-proportions/motion-publication-attempt1'
    for name in ('publish.py', 'failure.json'):
        files['publication-first-attempt/' + name] = (failed / name).read_bytes()
    for path in a.negatives.rglob('*'):
        if path.is_file() and (path.name in ('stdout.txt', 'stderr.txt', 'mutant-browser-failure.json') or path == a.negatives / 'wrong018-selector/mutant-review/review.html'):
            files['negatives/' + path.relative_to(a.negatives).as_posix()] = path.read_bytes()
    for path in build.HERE.iterdir():
        if path.is_file() and path.suffix in ('.py', '.html', '.md'):
            files['helpers/' + path.name] = path.read_bytes()
    linked = {}
    for relative in ('art/cartoon/standing018-proportions-v1/native-review/motion-v1/evidence-v1/evidence.json',
                     'art/cartoon/standing018-proportions-v1/native-review/motion-v1/evidence-v1/readback.json',
                     'art/cartoon/standing018-proportions-v1/color/evidence-v2/evidence.json'):
        linked[relative] = build.sha((build.ROOT / relative).read_bytes())
    a.output.mkdir(parents=True)
    for name, raw in files.items():
        path = a.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    binder = {'status': 'PASS; historical human motion approval pending at capture',
              'files_sha256': {n: build.sha(raw) for n, raw in files.items()}, 'linked_evidence_sha256': linked,
              'url': publication['url'], 'html_sha256': publication['html_sha256'],
              'baseline_archive_sha256': build.BASE_SHA, 'candidate_archive_sha256': build.CANDIDATE_SHA, 'runtime018_sha256': build.RUNTIME_SHA,
              'scope': 'Compact exact browser checkpoint; full native PNGs/ZIPs/binary remain local-only and must be reconstructed. Separate native evidence owns capture execution proof. No production or approval change.'}
    (a.output / 'evidence.json').write_text(json.dumps(binder, indent=2) + '\n', encoding='utf-8')
    for name, digest in binder['files_sha256'].items():
        assert build.sha((a.output / name).read_bytes()) == digest, 'frozen browser byte readback:' + name
    for name, digest in linked.items():
        assert build.sha((build.ROOT / name).read_bytes()) == digest, 'linked native/color evidence readback:' + name
    (a.output / 'readback.json').write_text(json.dumps({'status': 'PASS', 'files_checked': len(files), 'linked_evidence_checked': len(linked), 'binder_sha256': build.sha((a.output / 'evidence.json').read_bytes())}, indent=2) + '\n', encoding='utf-8')
    print('PASS frozen018 browser evidence ' + build.sha((a.output / 'evidence.json').read_bytes()), flush=True)


if __name__ == '__main__': main()
