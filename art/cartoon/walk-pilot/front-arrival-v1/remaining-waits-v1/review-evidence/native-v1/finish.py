"""Bind a small immutable complete-ring checkpoint after checked publication."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    return json.loads((OUT / name).read_bytes())


def main():
    target = OUT / 'evidence.json'
    checkpoint = OUT / 'checkpoint'
    assert not target.exists() and not checkpoint.exists(), 'preserve completed checkpoint'
    binding = read('baseline-v1/build.json')
    for name, digest in binding['protected_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == digest, 'protected input unchanged:' + name
    publication = read('publication.json')
    review = read('review-v1/review-record.json')
    checked = read('review-v1/browser-validation.json')
    assert publication['status'] == checked['status'] == 'PASS'
    assert publication['html_sha256'] == review['html_sha256'] == checked['html_sha256']
    native_negative = read('negative-controls/native/report.json')
    browser_negative = read('negative-controls/browser/report.json')
    assert native_negative['status'] == browser_negative['status'] == 'PASS'
    assert native_negative['positive_controls'] == 1 and native_negative['mutations_fired'] == 2
    assert browser_negative['mutations_fired'] == 1
    names = ['config.py', 'prepare.py', 'capture.py', 'native_core.py', 'route_driver.c', 'preparation.json',
             'candidate-selection.json', 'prepare_candidate.py', 'capture_candidate.py', 'review-template.html',
             'build_review.py', 'check_review.py', 'publish.py', 'publication.json', 'README.md', 'finish.py',
             'baseline-v1/build.json', 'baseline-v1/build.stdout.txt', 'baseline-v1/build.stderr.txt',
             'baseline-v1/route-contract.json', 'baseline-v1/summary.json', 'candidate-v1/preparation.json',
             'candidate-v1/summary.json', 'review-v1/review.html', 'review-v1/review-record.json', 'review-v1/browser-validation.json']
    names += ['negative_native.py', 'negative_browser.py', 'negative-controls/native/report.json',
              'negative-controls/browser/report.json', 'negative-controls/browser/stdout.txt',
              'negative-controls/browser/stderr.txt', 'negative-controls/browser/run_checker.py',
              'negative-controls/browser/check_review.py', 'negative-controls/browser/config.py',
              'negative-controls/browser/review-v1/review.html', 'negative-controls/browser/review-v1/browser-failure.json']
    for case in ('control', 'changed-timestamp', 'changed-approved-pose-pixel'):
        names += [f'negative-controls/native/{case}/result.json', f'negative-controls/native/{case}/increasing/full/capture.log']
    for clip in ('decreasing', 'increasing'):
        names += [f'baseline-v1/{clip}/{phase}/{name}' for phase in ('smoke', 'full', 'repeat') for name in ('report.json', 'capture.log')]
        names += [f'candidate-v1/{clip}/{phase}/{name}' for phase in ('smoke', 'full') for name in ('report.json', 'capture.log')]
    selection = read('candidate-selection.json')
    asset_paths = []
    for row in selection['frames']:
        asset_paths += [row['path'], row['recipe_path'], str(Path(row['recipe_path']).parent / 'export-report.json').replace('\\', '/')]
    asset_paths += ['art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/000-profile-v1.png',
                    'art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/015-rear-v1.png']
    result = {'status': 'published technical checkpoint; human approval recorded separately', 'url': publication['url'],
              'source_commit': binding['source_commit'], 'executable_sha256': binding['executable_sha256'],
              'production_archive_sha256': binding['protected_sha256']['assets/scrantic_data.zip'],
              'approved_baseline_archive_sha256': binding['baseline_pack_sha256'],
              'candidate_archive_sha256': read('candidate-v1/preparation.json')['archive_sha256'],
              'candidate_art_input_sha256': {name: sha((ROOT / name).read_bytes()) for name in asset_paths},
              'baseline': read('baseline-v1/summary.json'), 'candidate': read('candidate-v1/summary.json'),
              'html_sha256': publication['html_sha256'], 'native_png_sha256': review['image_files'],
              'files_sha256': {name: sha((OUT / name).read_bytes()) for name in names},
              'published_screenshots_sha256': publication['screenshots_sha256'],
              'negative_controls': {'native_guard_replay': native_negative, 'scratch_browser_mapping': browser_negative,
                                    'served_identity': publication['negative_control']},
              'scope': 'Both full eight-heading native rings; only000015 new, all previously approved art exact. No production changes or approval assigned by this binder. Original-binary timing/anatomical correctness remain separate.'}
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    copies = dict(result['files_sha256'])
    copies['evidence.json'] = sha(target.read_bytes())
    checkpoint.mkdir()
    for name, digest in copies.items():
        destination = checkpoint / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((OUT / name).read_bytes())
        assert sha(destination.read_bytes()) == digest, 'exact checkpoint copy:' + name
    report = {'status': 'PASS', 'files_preserved': len(copies), 'bytes_preserved': sum((checkpoint / name).stat().st_size for name in copies),
              'evidence_sha256': copies['evidence.json'], 'checkpoint': 'build/front-arrival/waits-ring-v1/checkpoint',
              'excluded': 'Full native PNGs/PPMs, ZIPs, executable and screenshots stay local outside this small checkpoint.'}
    (OUT / 'preservation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
