"""Run the actual browser checker against one wrong native-pose selector."""
import os
from pathlib import Path
import subprocess
import sys
import config
import native_core as core


def main():
    original = config.OUT / 'review-v1'
    assert config.load_json(original / 'browser-validation.json')['status'] == 'PASS', 'positive browser control first'
    out = config.OUT / 'negative-controls/wrong-pose-selector'
    assert not out.exists(), 'preserve selector mutation'
    (out / 'images').mkdir(parents=True)
    for image in (original / 'images').glob('*.png'):
        os.link(image, out / 'images' / image.name)
    source = (original / 'review.html').read_text(encoding='utf-8')
    old = "$('pose').onchange=()=>choosePose(Number($('pose').value));"
    new = "$('pose').onchange=()=>choosePose((Number($('pose').value)+1)%data.pose_count);"
    assert source.count(old) == 1, 'unique live selector mutation site'
    (out / 'review.html').write_text(source.replace(old, new, 1), encoding='utf-8', newline='\n')
    command = [sys.executable, '-B', str(config.HERE / 'check_review.py'), '--review', str(out)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    (out / 'checker.stdout.txt').write_text(result.stdout, encoding='utf-8')
    (out / 'checker.stderr.txt').write_text(result.stderr, encoding='utf-8')
    assert result.returncode != 0, 'wrong selector must fail'
    assert 'SMOKE PASS exact native images loaded' in result.stdout, 'mutant page actually executed through smoke'
    assert 'AssertionError: pose selector native ordinal:right:0' in result.stderr, 'specific changed selector witness'
    assert result.stderr.count('AssertionError:') == 1, 'exactly one named failure'
    assert not (out / 'browser-validation.json').exists(), 'mutant cannot pass final browser validation'
    core.save(config.OUT / 'negative-controls/browser.json', {'status': 'PASS', 'mutation': 'native pose selector shifted by one', 'result': 'FIRED',
              'expected_failure': 'pose selector native ordinal:right:0', 'actual_exit_code': result.returncode,
              'harness_sha256': core.sha(Path(__file__).read_bytes()), 'executed_checker_sha256': core.sha((config.HERE / 'check_review.py').read_bytes()),
              'original_html_sha256': core.sha((original / 'review.html').read_bytes()), 'executed_mutant_html_sha256': core.sha((out / 'review.html').read_bytes()),
              'positive_control': 'Existing complete browser-validation.json must pass before mutation; mutant smoke passed before specific regression failure.',
              'scope': 'Headless browser executed changed HTML and the same complete checker. No native engine mutation.'})
    print('FIRED wrong native-pose selector after real browser smoke; original review unchanged')


if __name__ == '__main__':
    main()
