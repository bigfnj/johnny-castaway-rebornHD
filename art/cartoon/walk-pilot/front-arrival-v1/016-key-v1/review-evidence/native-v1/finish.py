"""Bind and stage only small native turn evidence, preserving failed attempts."""
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
        assert sha((ROOT / name).read_bytes()) == digest, 'protected source unchanged:' + name
    failure = {'status': 'FAIL retained', 'stage': 'candidate-v1 A1-to-A7 smoke comparison',
               'native_capture_completed': True, 'failure': 'turn capture: only016 candidate canvas',
               'capture_helper_sha256': sha((OUT / 'capture_candidate.py').read_bytes()),
               'cause': 'Packer metadata used numeric17 although its ZIP correctly added016.',
               'correction': 'Numeric frame16 in both live helper and generator; passing rerun in candidate-v2.'}
    (OUT / 'candidate-v1/failure.json').write_text(json.dumps(failure, indent=2) + '\n')
    correction = {'corrected_helper_sha256': sha((OUT / 'prepare_candidate.py').read_bytes()),
                  'corrected_generator_sha256': sha((OUT / 'prepare_candidate_helper.py').read_bytes()),
                  'failed_helper_sha256': sha((OUT / 'candidate-v1/failed-prepare-helper.py').read_bytes()),
                  'scope': 'Original candidate-packer-adaptation.json is retained as pre-correction history; this record identifies the corrected live files.'}
    (OUT / 'candidate-packer-correction.json').write_text(json.dumps(correction, indent=2) + '\n')
    names = ['prepare.py', 'capture.py', 'route_driver.c', 'preparation.json', 'prepare_candidate_helper.py',
             'prepare_candidate.py', 'capture_candidate.py', 'candidate-packer-adaptation.json', 'candidate-packer-correction.json',
             'build_review.py', 'check_review.py', 'publish.py', 'publication.json', 'finalize_label.py',
             'view-label-correction.json', 'browser-label-recheck-failure.json', 'README.md', 'finish.py',
             'baseline-v1/build.json', 'baseline-v1/build.stdout.txt', 'baseline-v1/build.stderr.txt',
             'baseline-v1/route-contract.json', 'baseline-v1/summary.json',
             'candidate-v1/preparation.json', 'candidate-v1/failed-prepare-helper.py', 'candidate-v1/failed-prepare-generator.py',
             'candidate-v1/failed-packer-adaptation.json', 'candidate-v1/failure.json', 'candidate-v1/A1-to-A7/smoke/capture.log',
             'candidate-v2/preparation.json', 'candidate-v2/summary.json',
             'review-v1/review.html', 'review-v1/review-record.json', 'review-v1/browser-validation.json',
             'pre-label-review/review.html', 'pre-label-review/review-record.json', 'pre-label-review/browser-validation.json']
    for clip in ('A1-to-A7', 'A7-to-A1'):
        names += [f'baseline-v1/{clip}/{phase}/{file}' for phase in ('smoke', 'full', 'repeat') for file in ('report.json', 'capture.log')]
        names += [f'candidate-v2/{clip}/{phase}/{file}' for phase in ('smoke', 'full') for file in ('report.json', 'capture.log')]
    assets = ['build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png',
              'build/front-arrival/export016-v2/BMP/JOHNWALK.BMP/016.png',
              'build/front-arrival/export016-v2/recipe.json', 'build/front-arrival/export016-v2/export-report.json',
              'art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/016-toe-fit-v2.png']
    publication = read('publication.json')
    screenshots = {path.name: sha(path.read_bytes()) for path in OUT.glob('published-*-1280.png')}
    result = {'status': 'published technical checkpoint; human approval recorded separately', 'url': publication['url'],
              'source_commit': binding['source_commit'], 'executable_sha256': binding['executable_sha256'],
              'production_archive_sha256': binding['protected_sha256']['assets/scrantic_data.zip'],
              'approved017_baseline_archive_sha256': binding['baseline_pack_sha256'],
              'candidate016_archive_sha256': read('candidate-v2/preparation.json')['archive_sha256'],
              'candidate_art_input_sha256': {name: sha((ROOT / name).read_bytes()) for name in assets},
              'baseline': read('baseline-v1/summary.json'), 'candidate': read('candidate-v2/summary.json'),
              'html_sha256': publication['html_sha256'], 'native_png_sha256': read('review-v1/review-record.json')['image_files'],
              'files_sha256': {name: sha((OUT / name).read_bytes()) for name in names}, 'published_screenshots_sha256': screenshots,
              'scope': 'Actual native two-direction turn comparison as shown for016 review, retaining approved017. No production changes or approval assigned by this binder; see separate human review record. Pixel constraints do not establish anatomy or original-executable parity.'}
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    copies = dict(result['files_sha256'])
    copies['evidence.json'] = sha(target.read_bytes())
    checkpoint.mkdir()
    for name, digest in copies.items():
        destination = checkpoint / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((OUT / name).read_bytes())
        assert sha(destination.read_bytes()) == digest, 'checkpoint exact copy:' + name
    preservation = {'status': 'PASS', 'files_preserved': len(copies), 'bytes_preserved': sum((checkpoint / name).stat().st_size for name in copies),
                    'evidence_sha256': copies['evidence.json'], 'checkpoint': 'build/front-arrival/front-turn-v1/checkpoint',
                    'excluded': 'Full native PNGs/PPMs, ZIPs, executable and screenshots remain local outside the small checkpoint.'}
    (OUT / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(preservation, indent=2))


if __name__ == '__main__':
    main()
