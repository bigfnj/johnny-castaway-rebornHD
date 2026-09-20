"""Bind the captured fishing scene and one flag correction for appearance review."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EARLIER = HERE.parent / 'fishing-and-props-batch-v1'


def pin(path):
    result = {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == '.png':
        with Image.open(path) as image:
            alpha = image.convert('RGBA').getchannel('A')
            result.update(canvas=list(image.size), alpha8_bounds=list(alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()))
    return result


def bind(path, **extra):
    return {**pin(path), 'url': os.path.relpath(path, HERE).replace(os.sep, '/'), **extra}


def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def cards(items):
    return ''.join(f'<figure><figcaption>{html.escape(row["title"])}</figcaption><a class="art" href="{row["url"]}" target="_blank" rel="noopener" aria-label="Open {html.escape(row["title"])}"><canvas width="800" height="700" id="{row["id"]}" aria-label="{html.escape(row["title"])}"></canvas></a></figure>' for row in items)


def main():
    manifest = json.loads((HERE / 'scene-manifest.json').read_text(encoding='utf-8'))
    fish = []
    for item in manifest['fish']:
        frame = item['frame']
        captures = {}
        for kind in ('scene', 'original_scene'):
            capture = item[kind]
            scene_path = ROOT / capture['path']
            assert pin(scene_path)['sha256'] == capture['sha256'], f'Capture bytes changed: {scene_path}'
            captures[kind] = bind(scene_path, **{k: capture[k] for k in ('fish_bounds', 'context_crop', 'fish_crop', 'caption')})
        fish.append({
            'frame': frame,
            'diagnostic': bind(EARLIER / f'reference/original/MJFISH3.BMP/{frame}.png'),
            'cartoon': bind(EARLIER / f'generation/MJFISH3.BMP/{frame}-generated-v2.png'),
            **captures,
        })
    assert [row['frame'] for row in fish] == ['008', '009', '010']
    flag = [
        bind(EARLIER / 'reference/original/GJBIPLAN.BMP/021.png', id='flag-original', role='original', title='Original 021'),
        bind(EARLIER / 'generation/GJBIPLAN.BMP/021-generated-v1.png', id='flag-earlier', role='earlier', title='Earlier Cartoon 021'),
        bind(HERE / 'generation/GJBIPLAN.BMP/021-generated-v1.png', id='flag-corrected', role='corrected', title='Corrected Cartoon 021'),
    ]
    reference = [
        bind(EARLIER / 'reference/original/GJBIPLAN.BMP/022.png', id='flag-reference-original', role='original', title='Original 022: long cloth'),
        bind(EARLIER / 'generation/GJBIPLAN.BMP/022-generated-v1.png', id='flag-reference-cartoon', role='reference', title='Cartoon 022: style reference'),
    ]
    save('review-data.json', {'fish': fish, 'flag': flag, 'flag_reference': reference})
    template = (HERE / 'review-template.html').read_text(encoding='utf-8')
    page = template.replace('{{FLAG_CARDS}}', cards(flag)).replace('{{REFERENCE_CARDS}}', cards(reference))
    page = page.replace('{{SOURCE_NOTE}}', html.escape(manifest['source_note'])).replace('{{CAPTURE_LIMITS}}', html.escape(manifest['capture_limits']))
    (HERE / 'review.html').write_text(page, encoding='utf-8')
    record_path = HERE / 'generation/GJBIPLAN.BMP/021-record-v1.json'
    generation = json.loads(record_path.read_text(encoding='utf-8'))
    save('review-record.json', {
        'schema_version': 1,
        'status': 'awaiting_fish_palette_and_flag_drape_review',
        'fish': fish, 'flag': flag, 'flag_reference': reference,
        'flag_generation_record': pin(record_path), 'flag_request': pin(ROOT / generation['request']['path']),
        'page': pin(HERE / 'review.html'), 'data': pin(HERE / 'review-data.json'),
        'feedback': pin(HERE / 'feedback.json'), 'scene_manifest': pin(HERE / 'scene-manifest.json'),
        'helpers': [pin(HERE / name) for name in ('build_review.py', 'review.js', 'review-template.html', 'flag_record_output.py')],
        'production_archive': pin(ROOT / 'assets/scrantic_data.zip'),
        'human_approval': None, 'production_package_changed': False,
        'native_scope': 'Targeted Original-mode and current Cartoon-environment fishing scene captures for visual review only',
        'bulk_tests': 'Deferred at user request',
    })
    print('Built three fish scene views and corrected flag comparison.')


if __name__ == '__main__':
    main()
