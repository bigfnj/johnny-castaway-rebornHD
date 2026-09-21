"""Build the worker, clothed beach visitor and mermaid fix review."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / 'art/cartoon/workers-and-mermaids-batch-v1'
WORKERS = ROOT / 'art/cartoon/worker-tool-pose-corrections-v2'
GROUPS = [
    ('workers', 'Worker fixes', [('LILIPUTS.BMP', 78), ('LILIPUTS.BMP', 93)]),
    ('ssuzy', 'Redhead beach visitor', [('SSUZY1.BMP', n) for n in range(12)]),
    ('mermaid', 'Mermaid head poses', [('SBREAKUP.BMP', 15), ('SBREAKUP.BMP', 16)])
]

def pin(p):
    value = {'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix == '.png':
        with Image.open(p) as im:
            alpha = im.convert('RGBA').getchannel('A')
            value.update(canvas=list(im.size), mode=im.mode, alpha_range=list(alpha.getextrema()),
                         alpha8_bounds=list(alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()))
    return value

def rel(p):
    return os.path.relpath(p, HERE).replace(os.sep, '/')

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def main():
    versions = json.loads((HERE / 'selected-versions.json').read_text())
    rows, nav, sections = [], [], []
    for group, title, frames in GROUPS:
        nav.append(f'<a href="#{group}">{title} ({len(frames)})</a>')
        cards = []
        for resource, n in frames:
            frame = f'{n:03}'
            key = f'{resource}-{frame}'
            original = PRIOR / 'reference/original' / resource / f'{frame}.png'
            if resource == 'SSUZY1.BMP' and n == 3:
                row = {'key': key, 'resource': resource, 'frame': frame, 'group': group, 'version': None,
                       'blocked': True, 'retained_prior_drawing': False, 'original_reference': pin(original),
                       'original_url': rel(original),
                       'failure_records': [pin(HERE / 'generation/SSUZY1.BMP' / f'003-v{v}-failure.json') for v in (1, 2)]}
                rows.append(row)
                cards.append(f'<figure id="{key}" data-filter="{key} {title}"><figcaption>SSUZY1 003<span>Still blocked</span></figcaption>'
                             '<div class="unavailable">No drawing returned after two attempts with the pink-swimsuit context. The original is shown below.</div>'
                             f'<details open><summary>Original {key}</summary><a class="original" href="{rel(original)}" target="_blank" rel="noopener"><canvas width="720" height="250" data-key="{key}" data-kind="original" aria-label="Original {key}"></canvas></a></details></figure>')
                continue
            retained = resource == 'SSUZY1.BMP' and n in (1, 11)
            version = (1 if n == 1 else 2) if retained else versions[key]
            folder = (PRIOR if retained else HERE) / 'generation' / resource
            raw = folder / f'{frame}-generated-v{version}.png'
            record_path = folder / f'{frame}-record-v{version}.json'
            generation = json.loads(record_path.read_text())
            original = PRIOR / 'reference/original' / resource / f'{frame}.png'
            row = {'key': key, 'resource': resource, 'frame': frame, 'group': group, 'version': version,
                   'retained_prior_drawing': retained, 'selected_raw': pin(raw), 'original_reference': pin(original),
                   'generation_record': pin(record_path), 'request': generation['request'],
                   'url': rel(raw), 'original_url': rel(original)}
            caption = ('Existing matching drawing retained' if n == 1 else 'Existing bottle retained') if retained else title
            if resource == 'LILIPUTS.BMP':
                previous_version = 2 if n == 78 else 1
                previous = WORKERS / 'generation' / resource / f'{frame}-generated-v{previous_version}.png'
                caption = 'Thumb moved to the opposite side' if n == 78 else 'Rope attached to the wooden peg'
                row['previous_drawing'] = pin(previous)
            elif resource == 'SBREAKUP.BMP':
                previous = PRIOR / 'generation' / resource / f'{frame}-generated-v2.png'
                row['previous_drawing'] = pin(previous)
            else:
                previous = None
            previous_link = f'<p class="previous"><a href="{rel(previous)}" target="_blank" rel="noopener">Previous drawing</a></p>' if previous else ''
            rows.append(row)
            cards.append(f'<figure id="{key}" data-filter="{html.escape(key + " " + title)}"><figcaption>{resource.removesuffix(".BMP")} {frame}<span>{caption}</span></figcaption>'
                         f'<a class="art" href="{row["url"]}" target="_blank" rel="noopener" aria-label="Open Cartoon {key}"><canvas width="720" height="440" data-key="{key}" data-kind="cartoon" aria-label="Cartoon {key}"></canvas></a>'
                         f'<details open><summary>Original {key}</summary><a class="original" href="{row["original_url"]}" target="_blank" rel="noopener"><canvas width="720" height="250" data-key="{key}" data-kind="original" aria-label="Original {key}"></canvas></a></details>{previous_link}</figure>')
        sections.append(f'<section><h2 id="{group}">{title}</h2><div class="grid {group}">' + '\n'.join(cards) + '</div></section>')
    assert len(rows) == 16 and len({r['key'] for r in rows}) == 16
    save(HERE / 'review-data.json', {'assets': rows})
    template = (HERE / 'review-template.html').read_text()
    (HERE / 'review.html').write_text(template.replace('{{NAV}}', ''.join(nav)).replace('{{SECTIONS}}', '\n'.join(sections)), encoding='utf-8')
    save(HERE / 'review-record.json', {
        'schema_version': 1, 'status': 'awaiting_appearance_review',
        'new_drawing_count': 13, 'retained_drawing_count': 2, 'blocked_frame_count': 1, 'assets': rows,
        'page': pin(HERE / 'review.html'), 'data': pin(HERE / 'review-data.json'),
        'feedback': pin(HERE / 'feedback.json'), 'selected_versions': pin(HERE / 'selected-versions.json'),
        'helpers': [pin(HERE / name) for name in ['build_review.py', 'record_output.py', 'review-template.html', 'review.js']],
        'source_notes': [pin(p) for p in sorted(HERE.glob('*-notes.md'))],
        'production_archive': pin(ROOT / 'assets/scrantic_data.zip'),
        'appearance_approval': None, 'production_integrated': False, 'native_motion_checked': False
    })
    print('Built 13 new drawings, two retained drawings and one blocked original with 31 image panels.')

if __name__ == '__main__':
    main()
