"""Run the exact browser checker against a scratch wrong-heading page."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
TARGET = OUT / 'negative-controls/browser'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not TARGET.exists(), 'preserve browser negative-control evidence'
    target_review = TARGET / 'review-v1'
    target_review.mkdir(parents=True)
    for name in ('check_review.py', 'config.py'):
        (TARGET / name).write_bytes((OUT / name).read_bytes())
    raw = (OUT / 'review-v1/review.html').read_text(encoding='utf-8')
    old = "$('heading').onchange=()=>chooseHeading(Number($('heading').value));"
    assert raw.count(old) == 1, 'unique heading-mapping mutation target'
    raw = raw.replace(old, "$('heading').onchange=()=>chooseHeading((Number($('heading').value)+1)%8);")
    (target_review / 'review.html').write_text(raw, encoding='utf-8')
    (target_review / 'images').mkdir()
    for path in (OUT / 'review-v1/images').iterdir():
        os.link(path, target_review / 'images' / path.name)
    checker_sha = sha(TARGET / 'check_review.py')
    assert checker_sha == sha(OUT / 'check_review.py'), 'unchanged executed checker identity'
    launcher = TARGET / 'run_checker.py'
    launcher.write_text("import hashlib, runpy\nfrom pathlib import Path\np=Path(__file__).parent/'check_review.py'\nprint('WITNESS exact executed checker SHA256='+hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)\nrunpy.run_path(str(p),run_name='__main__')\n", encoding='utf-8')
    result = subprocess.run([sys.executable, '-B', str(launcher)], capture_output=True, text=True, timeout=180)
    (TARGET / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
    (TARGET / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    assert result.returncode != 0, 'wrong heading mapping must fail'
    assert 'WITNESS exact executed checker SHA256=' + checker_sha in result.stdout
    assert 'SMOKE PASS exact native image set loaded' in result.stdout, 'mutation reaches regression after smoke'
    condition = "assert state['heading'] == heading and not state['playing'] and state['view'] == 'walk'"
    assert condition in result.stderr and result.stderr.count('AssertionError') == 1, 'one actual heading guard failure'
    report = {'status': 'PASS', 'mutations_fired': 1, 'case': 'wrong-heading-selector-mapping',
              'named_failure': 'heading selector mapping: unchanged check_review.py heading state assertion',
              'exit_code': result.returncode, 'executed_checker_sha256': checker_sha,
              'source_html_sha256': sha(OUT / 'review-v1/review.html'), 'mutated_html_sha256': sha(target_review / 'review.html'),
              'launcher_sha256': sha(launcher), 'helper_sha256': sha(Path(__file__)),
              'smoke_before_expected_regression_failure': True,
              'scope': 'Fresh headless browser loads scratch mutated HTML; exact original checker executed. Published page unchanged.'}
    (TARGET / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
