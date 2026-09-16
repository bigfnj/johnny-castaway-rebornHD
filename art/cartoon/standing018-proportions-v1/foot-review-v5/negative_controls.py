"""Four focused fresh-process controls for changed foot-review bindings/view."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import build_review as build
import check_review as check

CASES = {'old-baseline': 'capture archive/executable identity:baseline:waypoint_rear',
         'wrong018-occurrence': 'contact mirrored arrival occurrence',
         'wrong-contact-image': 'contact image/source binding:revised',
         'broken-motion-link': 'contact motion link destination'}


def one(review, out, name):
    print('WITNESS executed ' + name + ' builder=' + build.sha(Path(build.__file__).read_bytes()) + ' checker=' + build.sha(Path(check.__file__).read_bytes()), flush=True)
    values = check.data(review)
    if name == 'old-baseline':
        left = build.load(review / 'motion/inputs/waypoint_rear/baseline-full.json')
        right = build.load(review / 'motion/inputs/waypoint_rear/candidate-full.json')
        left['archive_sha256'] = 'bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf'
        build.validate_pair(left, right, 'waypoint_rear', right['executable_sha256'])
    elif name == 'wrong018-occurrence':
        values['display_index'] = 1
        values['draw'] = [0, 452, 254, 18]
        values['logical_ms'] = 0
        check.validate_contact(review, values)
    elif name == 'wrong-contact-image':
        values['panels'][2]['image'] = values['panels'][1]['image']
        check.validate_contact(review, values)
    else:
        target = out / 'mutant-review'
        record = build.load(review / 'review-record.json')
        for name2 in list(record['files_sha256']) + ['review-record.json', 'motion/review-record.json', 'motion/review.html']:
            path = target / name2
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((review / name2).read_bytes())
        page = target / 'review.html'
        text = page.read_text()
        needle = 'id="motion-link" class="action" href="motion/review.html"'
        assert text.count(needle) == 1, 'one motion-link target'
        page.write_text(text.replace(needle, 'id="motion-link" class="action" href="missing/review.html"'), encoding='utf-8', newline='\n')
        record['files_sha256']['review.html'] = build.sha(page.read_bytes())
        (target / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        check.contact_check(target, record_name='mutant-browser.json')
    raise AssertionError('MUTATION SURVIVED:' + name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--case', choices=CASES)
    a = p.parse_args()
    if a.case: return one(a.review, a.output, a.case)
    assert not a.output.exists(), 'preserve focused foot controls'
    a.output.mkdir(parents=True)
    check.validate_contact(a.review, check.data(a.review))
    rows = []
    for name, failure in CASES.items():
        folder = a.output / name
        folder.mkdir()
        cmd = [sys.executable, '-B', str(Path(__file__).resolve()), '--review', str(a.review.resolve()), '--output', str(folder.resolve()), '--case', name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        (folder / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
        (folder / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
        assert result.returncode != 0 and ('WITNESS executed ' + name) in result.stdout and failure in result.stderr and 'MUTATION SURVIVED' not in result.stderr, 'specific executed foot control:' + name
        rows.append({'case': name, 'expected_failure': failure, 'exit_code': result.returncode,
                     'stdout_sha256': build.sha(result.stdout.encode()), 'stderr_sha256': build.sha(result.stderr.encode())})
        print('FIRED ' + name + ': ' + failure, flush=True)
    check.validate_contact(a.review, check.data(a.review))
    record = {'status': 'PASS', 'executed_negative_count': 4, 'controls': rows, 'restored_positive': True,
              'review_record_sha256': build.sha((a.review / 'review-record.json').read_bytes()),
              'builder_sha256': build.sha(Path(build.__file__).read_bytes()), 'checker_sha256': build.sha(Path(check.__file__).read_bytes()),
              'harness_sha256': build.sha(Path(__file__).read_bytes()), 'scope': 'Only changed baseline, actual mirrored018 selection, three-panel image binding and motion link. Existing motion control mutation matrices are retained, not rerun.'}
    (a.output / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__': main()
