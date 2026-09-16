"""Exercise valid changed HTML/preparation/report inputs in a private copied checkpoint."""
import argparse
import json
import os
from pathlib import Path
import shutil

import preserve_browser

config = preserve_browser.config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'preserve readback-control evidence'
    review = args.review.resolve()
    record = config.load_json(review / 'review-record.json')
    original_out = config.OUT
    fixture = args.output / 'fixture'
    fixture_review = fixture / 'review'
    fixture_review.mkdir(parents=True)
    for name in record['files_sha256']:
        source, target = review / name, fixture_review / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == '.png':
            os.link(source, target)
        else:
            shutil.copyfile(source, target)
    for name in ('review-record.json', 'browser-validation.json', 'publication.json', 'publication-browser.json'):
        shutil.copyfile(review / name, fixture_review / name)
    candidate = record['candidate_directory']
    for name in ('preparation.json', 'correction-recipe.json', 'scrantic_data.zip'):
        source = original_out / candidate / name
        target = fixture / candidate / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name.endswith('.zip'):
            os.link(source, target)
        else:
            shutil.copyfile(source, target)
    for clip, kinds in record['reports_sha256'].items():
        for kind in kinds:
            folder = 'baseline-v1' if kind == 'baseline' else candidate
            source = original_out / folder / clip / 'full/report.json'
            target = fixture / folder / clip / 'full/report.json'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    cases = [
        ('changed-valid-html', fixture_review / 'review.html', 'identity:review file:review.html'),
        ('changed-valid-preparation', fixture / candidate / 'preparation.json', 'identity:captured preparation'),
        ('changed-valid-capture-report', fixture / candidate / 'waypoint_front/full/report.json', 'identity:captured report:candidate:waypoint_front'),
    ]
    controls = []
    config.OUT = fixture.resolve()
    try:
        preserve_browser.publication_identity(fixture_review)
        for name, path, expected in cases:
            old = path.read_bytes()
            if path.suffix == '.html':
                path.write_bytes(old + b'\n<!-- valid changed review -->\n')
            else:
                value = json.loads(old)
                value['readback_control_marker'] = True
                path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
            changed = config.sha(path.read_bytes())
            assert changed != config.sha(old), 'actual changed valid input:' + name
            try:
                preserve_browser.publication_identity(fixture_review)
            except AssertionError as error:
                assert str(error) == expected, 'one intended readback refusal:' + name
                controls.append({'case': name, 'status': 'FIRED', 'failure': str(error), 'changed_input_sha256': changed})
            else:
                raise AssertionError('readback control survived:' + name)
            finally:
                path.write_bytes(old)
            preserve_browser.publication_identity(fixture_review)
            print('FIRED ' + name + '; restored positive passed')
    finally:
        config.OUT = original_out
    preserve_browser.publication_identity(review)
    result = {'status': 'PASS', 'html_sha256': record['files_sha256']['review.html'], 'controls': controls,
              'checker_sha256': config.sha(Path(__file__).read_bytes()),
              'preserver_sha256': config.sha(Path(preserve_browser.__file__).read_bytes()),
              'publisher_sha256': config.sha(Path(preserve_browser.publish_native.__file__).read_bytes()),
              'positive_before_and_after_each_case': True,
              'scope': 'Actual valid HTML/JSON changes in copied files. Native image PNGs and ZIP are read-only hardlinks, never edited. Original review, preparations and capture reports retain their identities.'}
    (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS original published checkpoint unchanged')


if __name__ == '__main__':
    main()
