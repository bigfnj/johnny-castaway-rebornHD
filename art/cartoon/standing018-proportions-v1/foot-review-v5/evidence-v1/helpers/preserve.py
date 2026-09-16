"""Freeze the compact published foot-review checkpoint and its source links."""
import argparse
import json
from pathlib import Path
import build_review as build


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--controls', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists(), 'preserve prior foot-review evidence'
    publication = build.load(a.review / 'publication.json')
    assert publication['status'] == 'PASS', 'completed foot-review publication'
    files = {}
    for prefix in ('', 'motion/'):
        record = build.load(a.review / prefix / 'review-record.json')
        for name, digest in record['files_sha256'].items():
            if prefix and name.startswith('images/'): continue
            raw = (a.review / prefix / name).read_bytes()
            assert build.sha(raw) == digest, 'bound retained foot-review file:' + prefix + name
            files['review/' + prefix + name] = raw
        files['review/' + prefix + 'review-record.json'] = (a.review / prefix / 'review-record.json').read_bytes()
    for name in ('browser-validation.json', 'contact-browser.json', 'served-contact-browser.json', 'publication.json', 'motion/browser-validation.json'):
        files['review/' + name] = (a.review / name).read_bytes()
    for record_name in ('contact-browser.json', 'served-contact-browser.json'):
        row = build.load(a.review / record_name)
        raw = (a.review / row['screenshot']).read_bytes()
        assert build.sha(raw) == row['screenshot_sha256'], 'bound contact screenshot'
        files['review/' + row['screenshot']] = raw
    for path in a.controls.rglob('*'):
        if path.is_file() and (path.name in ('stdout.txt', 'stderr.txt', 'result.json') or path == a.controls / 'broken-motion-link/mutant-review/review.html'):
            files['controls/' + path.relative_to(a.controls).as_posix()] = path.read_bytes()
    original_path = build.HERE.parent / 'motion-review-v1/check_review.py'
    derived_path = build.HERE / 'shared_motion_check.py'
    original = original_path.read_text().replace('\r\n', '\n').strip()
    derived = derived_path.read_text().replace('\r\n', '\n').strip()
    old_labels = "['Earlier Cartoon', 'Revised Cartoon']"
    assert original.count(old_labels) == 1 and derived == original.replace(old_labels, "['Previous version', 'Corrected foot']"), 'only expected panel labels differ in reused motion checker'
    reuse = {'source': original_path.relative_to(build.ROOT).as_posix(), 'source_sha256': build.sha(original_path.read_bytes()),
             'derived_sha256': build.sha(derived_path.read_bytes()), 'change': 'One expected panel-label assertion; no pixel/timing/playback/control algorithm change.'}
    files['checker-reuse.json'] = (json.dumps(reuse, indent=2) + '\n').encode()
    attempts = []
    for name, error in [('foot-review-v5', "KeyError: 'segments'"), ('foot-review-v5-final', "KeyError: 'segment'")]:
        path = build.ROOT / 'build/standing018-proportions' / name / 'motion/review-record.json'
        raw = path.read_bytes()
        files['initial-build-attempts/' + name + '-partial-motion-record.json'] = raw
        attempts.append({'directory': path.parent.parent.relative_to(build.ROOT).as_posix(), 'exception_transcribed_from_tool_output': error,
                         'partial_motion_record_sha256': build.sha(raw), 'status': 'incomplete and unpublished; local artifacts retained'})
    files['initial-build-attempts/notes.json'] = (json.dumps(attempts, indent=2) + '\n').encode()
    for path in build.HERE.iterdir():
        if path.is_file() and path.suffix in ('.py', '.html', '.md'):
            files['helpers/' + path.name] = path.read_bytes()
    linked = {}
    for relative in ('art/cartoon/standing018-proportions-v1/native-review/foot-v5/evidence-v1/evidence.json',
                     'art/cartoon/standing018-proportions-v1/native-review/foot-v5/evidence-v1/readback.json',
                     'art/cartoon/standing018-proportions-v1/color/evidence-foot-v5/evidence.json',
                     'art/cartoon/standing018-proportions-v1/native-review/original-mirror-v1/evidence-v1/evidence.json',
                     'art/cartoon/standing018-proportions-v1/motion-review-v1/evidence-v1/evidence.json'):
        linked[relative] = build.sha((build.ROOT / relative).read_bytes())
    a.output.mkdir(parents=True)
    for name, raw in files.items():
        path = a.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    binder = {'status': 'PASS; human foot review pending at publication', 'url': publication['url'],
              'files_sha256': {n: build.sha(raw) for n, raw in files.items()}, 'linked_evidence_sha256': linked,
              'contact_html_sha256': publication['html_sha256'], 'motion_html_sha256': publication['motion_html_sha256'],
              'contact_record_sha256': publication['contact_record_sha256'], 'motion_record_sha256': publication['motion_record_sha256'],
              'baseline_archive_sha256': build.BASE_SHA, 'candidate_archive_sha256': build.CANDIDATE_SHA, 'runtime018_sha256': build.RUNTIME_SHA,
              'scope': 'Exact contact page, two-panel motion page, focused tests and linked native/color/original proof. Full motion images/ZIPs/binaries remain local-only. Human approval is separate.'}
    (a.output / 'evidence.json').write_text(json.dumps(binder, indent=2) + '\n', encoding='utf-8')
    for name, digest in binder['files_sha256'].items():
        assert build.sha((a.output / name).read_bytes()) == digest, 'preserved foot evidence:' + name
    for name, digest in linked.items():
        assert build.sha((build.ROOT / name).read_bytes()) == digest, 'linked foot evidence:' + name
    (a.output / 'readback.json').write_text(json.dumps({'status': 'PASS', 'files_checked': len(files), 'linked_evidence_checked': len(linked),
        'binder_sha256': build.sha((a.output / 'evidence.json').read_bytes())}, indent=2) + '\n', encoding='utf-8')
    print('PASS compact foot-review binder ' + build.sha((a.output / 'evidence.json').read_bytes()), flush=True)


if __name__ == '__main__': main()
