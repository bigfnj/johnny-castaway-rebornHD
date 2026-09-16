"""Fresh-process negative controls for the new018 report/view adapter."""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback
import build_review as build
import check_review as check

CASES = {
    'wrong-native-clip': 'capture clip/phase identity:candidate:waypoint_front',
    'wrong-native-archive': 'capture archive/executable identity:candidate:waypoint_front',
    'changed-native-time': 'matching native panel timeline:waypoint_front',
    'changed-model-time': 'review native time/draw binding:waypoint_front',
    'changed-camera': 'review fixed full-canvas camera:waypoint_front',
    'wrong-image-side': 'review native image binding:waypoint_front',
    'wrong018-selector': 'reference selector native ordinal:',
}


def bundle(review):
    return json.loads(re.search(r'<script id="capture-data" type="application/json">(.*?)</script>', (review / 'review.html').read_text(), re.S)[1])


def one(review, out, name):
    print('WITNESS executed case=' + name + ' builder=' + build.sha(Path(build.__file__).read_bytes()) + ' checker=' + build.sha(Path(check.__file__).read_bytes()), flush=True)
    model = bundle(review)
    if name.startswith('wrong-native') or name == 'changed-native-time':
        left = build.load(review / 'inputs/waypoint_front/baseline-full.json')
        right = build.load(review / 'inputs/waypoint_front/candidate-full.json')
        executable = right['executable_sha256']
        if name == 'wrong-native-clip': right['clip'] = 'front_arc'
        elif name == 'wrong-native-archive': right['archive_sha256'] = build.BASE_SHA
        else: right['displays'][0]['logical_ms'] += 1
        build.validate_pair(left, right, 'waypoint_front', executable)
    elif name == 'wrong018-selector':
        target = out / 'mutant-review'
        # Reuse exact immutable PNGs and reports. Only this scratch page and
        # its local record differ, so the executable DOM control is exercised.
        shutil.copytree(review, target, copy_function=shutil.copy2)
        page = target / 'review.html'
        text = page.read_text()
        old = "choosePose(Number($('reference').value));"
        assert text.count(old) == 1, 'single018 selector mutation target'
        page.write_text(text.replace(old, "choosePose(Number($('reference').value)-1);"), encoding='utf-8', newline='\n')
        record = build.load(target / 'review-record.json')
        record['files_sha256']['review.html'] = build.sha(page.read_bytes())
        (target / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        check.check(target, record_name='mutant-browser.json')
    else:
        values = model['clips']['waypoint_front']
        if name == 'changed-model-time': values['frames'][0]['logical_ms'] += 1
        elif name == 'changed-camera': values['camera_hd_xywh'][0] += 1
        else:
            row = next(r for r in values['frames'] if r['frame'] == 18)
            row['candidate'] = row['baseline']
        check.validate_model(model, review)
    raise RuntimeError('MUTATION SURVIVED:' + name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--case', choices=CASES)
    a = p.parse_args()
    if a.case:
        return one(a.review, a.output, a.case)
    assert not a.output.exists(), 'preserve018 negative evidence'
    a.output.mkdir(parents=True)
    check.validate_model(bundle(a.review), a.review)
    results = []
    for name, expected in CASES.items():
        folder = a.output / name
        folder.mkdir()
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--review', str(a.review.resolve()), '--output', str(folder.resolve()), '--case', name]
        run = subprocess.run(command, text=True, capture_output=True, timeout=180)
        (folder / 'stdout.txt').write_text(run.stdout, encoding='utf-8')
        (folder / 'stderr.txt').write_text(run.stderr, encoding='utf-8')
        assert run.returncode != 0 and ('WITNESS executed case=' + name) in run.stdout and expected in run.stderr and 'MUTATION SURVIVED' not in run.stderr, 'named fresh-process negative:' + name
        results.append({'case': name, 'expected_failure': expected, 'exit_code': run.returncode,
                        'stdout_sha256': build.sha(run.stdout.encode()), 'stderr_sha256': build.sha(run.stderr.encode())})
        print('FIRED ' + name + ' -> ' + expected, flush=True)
    check.validate_model(bundle(a.review), a.review)
    result = {'status': 'PASS', 'executed_negative_count': len(results), 'controls': results,
              'positive_before_and_restored_after': 'exact retained source model passes',
              'review_record_sha256': build.sha((a.review / 'review-record.json').read_bytes()),
              'builder_sha256': build.sha(Path(build.__file__).read_bytes()), 'checker_sha256': build.sha(Path(check.__file__).read_bytes()),
              'harness_sha256': build.sha(Path(__file__).read_bytes()),
              'scope': 'New report/model adapter and018 occurrence DOM selector. Existing playback/cache behavior is covered by the positive browser run; historical mutation matrices are not rerun.'}
    (a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__': main()
