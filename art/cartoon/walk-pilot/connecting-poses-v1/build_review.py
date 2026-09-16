"""Build one static 009 review into an explicitly new output directory."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.export / 'export-report.json'
    report = json.loads(report_path.read_bytes())
    recipe_path = args.export / 'recipe.json'
    recipe = json.loads(recipe_path.read_bytes())
    member = 'BMP/JOHNWALK.BMP/009.png'
    candidate_path = args.export / member
    candidate = candidate_path.read_bytes()
    if sha(candidate) != report['outputs_sha256'][member]:
        raise ValueError('candidate-png:009:' + str(candidate_path))
    if recipe['frames'][0]['frame'] != 9 or report['frames'][0]['frame'] != 9:
        raise ValueError('candidate-frame:009:' + str(recipe_path))
    original_path = HERE / 'reference/009-original-native.png'
    original = original_path.read_bytes()
    with zipfile.ZipFile(ROOT / 'assets/scrantic_data.zip') as archive:
        identity017 = archive.read('data/styles/cartoon/BMP/JOHNWALK.BMP/017.png')
        identity003 = archive.read('data/styles/cartoon/BMP/JOHNWALK.BMP/003.png')
    blobs = {'original': original, 'candidate': candidate,
             'identity017': identity017, 'identity003': identity003}
    data = {name: 'data:image/png;base64,' + base64.b64encode(value).decode('ascii')
            for name, value in blobs.items()}
    data['canvas'] = recipe['frames'][0]['runtime_canvas']
    template_path = HERE / 'review-template.html'
    template = template_path.read_text(encoding='utf-8')
    html = template.replace('__REVIEW_DATA__', json.dumps(data)).encode('utf-8')
    record = {'schema_version': 1, 'scope': 'Static 009 draft only; human and native review pending.',
              'blob_sha256': {name: sha(value) for name, value in blobs.items()},
              'input_sha256': {str(p.resolve().relative_to(ROOT).as_posix()): sha(p.read_bytes())
                               for p in [report_path, recipe_path, original_path, template_path]},
              'production_archive_sha256': sha((ROOT / 'assets/scrantic_data.zip').read_bytes()),
              'builder_sha256': sha(Path(__file__).read_bytes()),
              'review_html_sha256': sha(html)}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'review.html').write_bytes(html)
    (args.output / 'review-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'output': str(args.output), 'review_html_sha256': sha(html)}))


if __name__ == '__main__':
    main()
