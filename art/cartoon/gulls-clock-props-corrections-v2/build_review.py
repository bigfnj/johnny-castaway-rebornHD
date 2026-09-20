"""Build the focused original/earlier/corrected appearance comparison."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = {
    'carrying': 'Carrying the book',
    'book': 'Ruffling the book',
    'hands': 'Hands',
    'propellers': 'Propellers',
    'rotors': 'Rotors',
    'parachutes': 'Parachutes',
}


def pin(path):
    item = {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix.lower() == '.png':
        with Image.open(path) as im:
            alpha = im.convert('RGBA').getchannel('A')
            item.update(canvas=list(im.size), mode=im.mode,
                        alpha_range=list(alpha.getextrema()),
                        alpha8_bounds=list(alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return item


def rel(path):
    return os.path.relpath(path, HERE).replace(os.sep, '/')


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    feedback = json.loads((HERE / 'feedback.json').read_text(encoding='utf-8'))
    versions = json.loads((HERE / 'selected-versions.json').read_text(encoding='utf-8'))
    rows = []
    groups = {group: [] for group in GROUPS}
    for item in feedback['frames']:
        key, resource, frame = item['key'], item['resource'], item['frame']
        version = versions[key]
        record_path = HERE / 'generation' / resource / f'{frame}-record-v{version}.json'
        generation = json.loads(record_path.read_text(encoding='utf-8'))
        request_path = ROOT / generation['request']['path']
        output_path = ROOT / generation['output']['path']
        row = {'key': key, 'resource': resource, 'frame': frame, 'group': item['group'],
               'correction': item['correction'], 'version': version,
               'record': pin(record_path), 'request': pin(request_path),
               'generation_references': generation['references'],
               'generation_output': generation['output'],
               'raw_tool_output': generation['raw_tool_output'],
               'prior_record': item['prior_record'], 'prior_request': item['prior_request'],
               'original_binding': item['original'], 'prior_output_binding': item['prior_raw'],
               'images': {}}
        cards = []
        for kind, title, path in [
            ('original', 'Original', ROOT / item['original']['path']),
            ('earlier', 'Earlier Cartoon', ROOT / item['prior_raw']['path']),
            ('corrected', 'Corrected Cartoon', output_path),
        ]:
            row['images'][kind] = {**pin(path), 'url': rel(path)}
            cards.append(
                f'<figure><figcaption>{title}</figcaption>'
                f'<a class="art" href="{html.escape(rel(path), quote=True)}" target="_blank" rel="noopener" '
                f'aria-label="Open {title} {html.escape(key)}">'
                f'<canvas width="960" height="600" data-key="{html.escape(key)}" data-kind="{kind}" '
                f'aria-label="{title} {html.escape(key)}"></canvas></a></figure>')
        groups[item['group']].append(
            f'<article class="comparison" id="frame-{html.escape(key)}" data-key="{html.escape(key)}">'
            f'<h3>{html.escape(resource)} {frame}</h3><p class="instruction">{html.escape(item["correction"])}</p>'
            '<div class="row">' + ''.join(cards) + '</div></article>')
        rows.append(row)
    sections = '\n'.join(
        f'<section class="group" id="group-{group}" data-group="{group}"><h2>{title}</h2>'
        + '\n'.join(groups[group]) + '</section>' for group, title in GROUPS.items())
    data = {'schema_version': 1, 'total': len(rows), 'status': 'appearance_review_pending',
            'groups': GROUPS, 'frames': rows}
    save(HERE / 'review-data.json', data)
    template = (HERE / 'review-template.html').read_text(encoding='utf-8')
    (HERE / 'review.html').write_text(template.replace('{{SECTIONS}}', sections), encoding='utf-8')
    review = {
        'schema_version': 1, 'status': 'awaiting_24_targeted_corrections_appearance_review',
        'scope': 'Only the 24 corrected drawings. No implied approval of the other 47 prior drawings.',
        'frame_count': len(rows), 'panel_count': len(rows) * 3, 'frames': rows,
        'page': pin(HERE / 'review.html'), 'data': pin(HERE / 'review-data.json'),
        'feedback': pin(HERE / 'feedback.json'), 'prior_review': feedback['prior_review'],
        'attachments': feedback['attachments'],
        'helpers': [pin(HERE / p) for p in ('build_review.py', 'review.js', 'review-template.html',
                                           'record_output.py', 'prepare_feedback.py')],
        'selected_versions': pin(HERE / 'selected-versions.json'),
        'production_archive': pin(ROOT / 'assets/scrantic_data.zip'),
        'human_approval': None, 'production_package_changed': False, 'native_testing': False,
    }
    save(HERE / 'review-record.json', review)
    print(f'Built {len(rows)} corrections with {len(rows) * 3} comparison panels')


if __name__ == '__main__':
    main()
