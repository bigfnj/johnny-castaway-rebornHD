"""Execute wrong-pose and changed served-HTML controls in isolated pages."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, default=config.OUT / 'review-v1')
    args = parser.parse_args()
    original = args.review.resolve()
    positive = config.load_json(original / 'browser-validation.json')
    assert positive['status'] == 'PASS' and len(positive['regressions_after_smoke']) == len(config.CLIPS), 'positive browser controls first'
    review_name = original.relative_to(config.OUT.resolve()).as_posix()
    assert '/' not in review_name and review_name.startswith('review-'), 'explicit local review directory'
    destination = config.OUT / 'negative-controls' / ('browser' if review_name == 'review-v1' else 'browser-' + review_name)
    assert not destination.exists(), 'preserve browser mutation evidence'
    destination.mkdir(parents=True)
    source = (original / 'review.html').read_text(encoding='utf-8')
    old = "$('pose').onchange=()=>choosePose(Number($('pose').value));"
    new = "$('pose').onchange=()=>choosePose((Number($('pose').value)+1)%data.pose_count);"
    assert source.count(old) == 1, 'unique live selector mutation site'
    cases = [('wrong-pose-selector', source.replace(old, new, 1), 'pose selector native ordinal:' + config.DEFAULT_CLIP + ':0'),
             ('changed-served-html', source + ' ', 'exact served HTML')]
    results = []
    for name, text, witness in cases:
        out = destination / name
        (out / 'images').mkdir(parents=True)
        for image in (original / 'images').glob('*.png'):
            os.link(image, out / 'images' / image.name)
        (out / 'review.html').write_text(text, encoding='utf-8', newline='\n')
        command = [sys.executable, '-B', str(config.HERE / 'check_review.py'), '--review', str(out)]
        if name == 'changed-served-html':
            command.extend(['--expected-html', str(original / 'review.html')])
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        (out / 'checker.stdout.txt').write_text(result.stdout, encoding='utf-8')
        (out / 'checker.stderr.txt').write_text(result.stderr, encoding='utf-8')
        assert result.returncode != 0, 'browser control must fire:' + name
        assert 'WITNESS served HTML SHA256=' + config.sha((out / 'review.html').read_bytes()) in result.stdout, 'actual mutated HTTP response:' + name
        if name == 'wrong-pose-selector':
            assert 'SMOKE PASS exact native images loaded' in result.stdout, 'selector mutant executes through smoke'
        assert 'AssertionError: ' + witness in result.stderr and result.stderr.count('AssertionError:') == 1, 'exactly one specific browser failure:' + name
        assert not (out / 'browser-validation.json').exists(), 'mutant cannot pass final browser validation'
        results.append({'name': name, 'result': 'FIRED', 'expected_failure': witness, 'actual_exit_code': result.returncode,
                        'executed_html_sha256': config.sha((out / 'review.html').read_bytes()),
                        'stdout_sha256': config.sha((out / 'checker.stdout.txt').read_bytes()), 'stderr_sha256': config.sha((out / 'checker.stderr.txt').read_bytes())})
        print('FIRED ' + name + ': ' + witness, flush=True)
    assert config.sha((original / 'review.html').read_bytes()) == positive['html_sha256'], 'original positive page untouched'
    record = {'status': 'PASS', 'controls': results, 'harness_sha256': config.sha(Path(__file__).read_bytes()),
              'executed_checker_sha256': config.sha((config.HERE / 'check_review.py').read_bytes()),
              'original_html_sha256': positive['html_sha256'], 'positive_control_sha256': config.sha((original / 'browser-validation.json').read_bytes()),
              'scope': 'Fresh headless browsers request both mutated pages. Wrong selector executes through smoke before named regression; changed served bytes fail exact HTTP identity. No production/native mutation.'}
    record['review_directory'] = review_name
    (destination.with_suffix('.json')).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
