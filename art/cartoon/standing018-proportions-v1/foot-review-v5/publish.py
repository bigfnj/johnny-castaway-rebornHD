"""Publish the verified contact landing and exact tested motion page once."""
import argparse
import copy
import json
from pathlib import Path
import urllib.request
import build_review as build
import check_review as check

SERVER = Path('D:/.ai-work/worktrees/johnny-art-metadata/build/art-review')
SLUG = 'standing018-contact-v3'
URL = 'http://127.0.0.1:8932/' + SLUG + '/review.html'


def html_binding(review, contact, motion):
    assert build.sha((review / 'review.html').read_bytes()) == contact['files_sha256']['review.html'], 'publication contact HTML identity'
    assert build.sha((review / 'motion/review.html').read_bytes()) == motion['files_sha256']['review.html'], 'publication motion HTML identity'


def publish(review, controls):
    target = SERVER / SLUG
    assert not target.exists(), 'preserve previous contact publication'
    contact, motion = build.load(review / 'review-record.json'), build.load(review / 'motion/review-record.json')
    browser, negatives = build.load(review / 'browser-validation.json'), build.load(controls / 'result.json')
    assert browser['status'] == negatives['status'] == 'PASS' and negatives['executed_negative_count'] == 4, 'completed contact and motion checks'
    assert browser['checker_sha256'] == negatives['checker_sha256'] == build.sha(Path(check.__file__).read_bytes()), 'current contact checker tested'
    assert browser['bindings_sha256'] == negatives['builder_sha256'] == contact['builder_sha256'] == build.sha(Path(build.__file__).read_bytes()), 'current source adapter tested'
    assert negatives['review_record_sha256'] == build.sha((review / 'review-record.json').read_bytes()), 'tested contact record'
    assert browser['contact_record_sha256'] == build.sha((review / 'contact-browser.json').read_bytes()) and browser['motion_record_sha256'] == build.sha((review / 'motion/browser-validation.json').read_bytes()), 'completed bound browser records'
    html_binding(review, contact, motion)
    changed = []
    for kind in ('contact', 'motion'):
        c, m = copy.deepcopy(contact), copy.deepcopy(motion)
        (c if kind == 'contact' else m)['files_sha256']['review.html'] = '0' * 64
        expected = 'publication ' + kind + ' HTML identity'
        try: html_binding(review, c, m)
        except AssertionError as error:
            assert str(error) == expected, 'named published HTML control'
            changed.append({'case': 'stale-' + kind + '-HTML', 'failure': expected})
        else: raise AssertionError('publication HTML mutation survived')
    html_binding(review, contact, motion)
    files = {}
    for prefix, record in [('', contact), ('motion/', motion)]:
        for name, digest in record['files_sha256'].items():
            raw = (review / prefix / name).read_bytes()
            assert build.sha(raw) == digest, 'published exact bound input:' + prefix + name
            files[prefix + name] = raw
        files[prefix + 'review-record.json'] = (review / prefix / 'review-record.json').read_bytes()
    target.mkdir()
    for name, raw in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    for name, raw in files.items():
        with urllib.request.urlopen(URL.rsplit('/', 1)[0] + '/' + name) as response:
            assert response.status == 200 and response.read() == raw, 'exact served contact/motion file:' + name
    check.contact_check(review, record_name='served-contact-browser.json', base_url=URL)
    result = {'status': 'PASS', 'url': URL, 'html_sha256': contact['files_sha256']['review.html'],
              'motion_html_sha256': motion['files_sha256']['review.html'],
              'contact_record_sha256': build.sha((review / 'review-record.json').read_bytes()),
              'motion_record_sha256': build.sha((review / 'motion/review-record.json').read_bytes()),
              'served_file_count': len(files), 'publication_HTML_controls': changed, 'restored_positive': True,
              'served_contact_browser_sha256': build.sha((review / 'served-contact-browser.json').read_bytes()),
              'local_full_browser_sha256': build.sha((review / 'browser-validation.json').read_bytes()),
              'focused_negative_sha256': build.sha((controls / 'result.json').read_bytes()), 'publisher_sha256': build.sha(Path(__file__).read_bytes()),
              'scope': 'New immutable slug. Served contact smoke then six-crop/link regression; exact motion files equal the locally tested full164-display review. No unchanged full motion matrix repeated after publication; human foot approval pending.'}
    (review / 'publication.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS published ' + URL, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--controls', type=Path, required=True)
    a = p.parse_args()
    publish(a.review, a.controls)
