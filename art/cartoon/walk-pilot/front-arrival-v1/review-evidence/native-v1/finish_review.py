"""Bind final native017 review evidence without changing the saved baseline."""
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
    target = OUT / 'review-evidence.json'
    if target.exists():
        raise ValueError('preserve existing final review evidence')
    baseline = read('baseline-v1/summary.json')
    candidate = read('candidate-v1/summary.json')
    browser = read('island-review-v1/browser-validation.json')
    publication = read('publication.json')
    review = read('island-review-v1/review-record.json')
    art_paths = ['build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png',
                 'build/front-arrival/export-v3/recipe.json',
                 'build/front-arrival/export-v3/export-report.json',
                 'art/cartoon/walk-pilot/front-arrival-v1/017-foot-depth-v3.png']
    art_hashes = {name: sha((ROOT / name).read_bytes()) for name in art_paths}
    assert art_hashes[art_paths[0]] == '60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1', 'selected runtime017 identity'
    assert art_hashes[art_paths[1]] == '32b7588894a0ef9b2aa623b2da5fd5aaaa25af362b61e985a8b4eaa41af34d85', 'selected recipe identity'
    assert sha((ROOT / 'assets/scrantic_data.zip').read_bytes()) == baseline['archive_sha256'], 'unchanged production archive'
    assert publication['html_sha256'] == review['html_sha256'] == browser['html_sha256'], 'built tested published page identity'
    names = ['prepare.py', 'capture.py', 'route_driver.c', 'preparation.json', 'finish.py', 'evidence.json', 'README.md',
             'prepare_candidate.py', 'adapt_candidate.py', 'capture_candidate.py', 'candidate-adaptation.json',
             'check_helpers.py', 'helper-checks-v1/report.json', 'helper-checks-v1/mutation.stdout.txt', 'helper-checks-v1/mutation.stderr.txt',
             'prepare_review.py', 'build_review.py', 'check_review.py', 'review-adaptation.json',
             'prepare_publication.py', 'publish.py', 'publication-adaptation.json', 'publication.json',
             'baseline-v1/build.json', 'baseline-v1/route-contract.json', 'baseline-v1/summary.json',
             'candidate-v1/preparation.json', 'candidate-v1/summary.json',
             'island-review-v1/review.html', 'island-review-v1/review-record.json', 'island-review-v1/browser-validation.json',
             'finish_review.py', 'HANDOFF.md']
    names += [f'baseline-v1/{phase}/{name}' for phase in ('smoke', 'full', 'repeat') for name in ('report.json', 'capture.log')]
    names += [f'candidate-v1/{phase}/{name}' for phase in ('smoke', 'full') for name in ('report.json', 'capture.log')]
    record = {'status': 'published for human review', 'url': publication['url'],
              'source_commit': read('baseline-v1/build.json')['source_commit'],
              'production_archive_sha256': baseline['archive_sha256'], 'private_archive_sha256': candidate['archive_sha256'],
              'observer_executable_sha256': baseline['executable_sha256'],
              'candidate_art_inputs_sha256': art_hashes, 'display_count': candidate['display_count'],
              'duration_ms': candidate['duration_ms'], 'changed_arrival_displays': candidate['changed_displays'],
              'identical_displays': candidate['unchanged_displays'], 'fixed_camera_hd_xywh': [560, 400, 400, 280],
              'arrival_mask_hd_xyxy': [586, 486, 666, 636], 'html_sha256': publication['html_sha256'],
              'native_png_sha256': review['image_files'], 'files_sha256': {name: sha((OUT / name).read_bytes()) for name in names},
              'verification': {'baseline': 'smoke then full then fresh-process exact repeat',
                               'candidate': 'smoke then full; one added ZIP member, all2579 existing members unchanged',
                               'mask': 'smoke, five controls and executed rebuilt mask-removal mutation',
                               'browser': 'two smoke checks, four grouped regressions, three executed browser mutations',
                               'publication': '95 served identities then native timing/pixel/control/layout regressions'},
              'scope': 'Technical native017 comparison and publication only. No human acceptance or production promotion; no original-executable or physical timing parity claim.'}
    target.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': record['status'], 'url': record['url'], 'files_bound': len(names), 'images_bound': len(review['image_files']), 'evidence_sha256': sha(target.read_bytes())}))


if __name__ == '__main__':
    main()
