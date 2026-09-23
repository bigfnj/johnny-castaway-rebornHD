"""Build the review from recorded attempts, scoped approval and pending follow-ups."""
import hashlib
import html
import json
import os
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROUPS = {'reclining': 'Reclining and leg bends', 'seated': 'Seated leg connection'}
STATUS_LABELS = {
    'blocked': 'No new image',
    'ready_for_review': 'Ready for appearance review',
    'needs_anatomy_review': 'Anatomy review needed',
    'diagnostic_insufficient': 'Diagnostic attempt: insufficient',
    'approved_by_user': 'Leg connection accepted by the user',
    'local_test_pending': 'Local test pending',
    'in_progress': 'New attempt running',
}
LATEST_LABELS = {
    'returned': 'Image returned',
    'blocked': 'Blocked: no image returned',
    'not_submitted': 'Prepared, not submitted',
    'in_progress': 'Running',
}

def pin(path):
    value = {'path': path.relative_to(ROOT).as_posix(),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix == '.png':
        with Image.open(path) as im:
            alpha = im.convert('RGBA').getchannel('A')
            bounds = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
            value.update(canvas=list(im.size), mode=im.mode,
                         alpha_range=list(alpha.getextrema()),
                         alpha8_bounds=list(bounds) if bounds else None)
    return value

def rel(path):
    return os.path.relpath(path, HERE).replace(os.sep, '/')

def linked_pin(path):
    return {**pin(path), 'url': rel(path)}

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')

def main():
    feedback = json.loads((HERE / 'feedback.json').read_text(encoding='utf-8'))
    selection = json.loads((HERE / 'selected-versions.json').read_text(encoding='utf-8'))
    rows, sections = [], {group: [] for group in GROUPS}
    folder = HERE / 'generation/SSUZY1.BMP'
    for item in feedback['frames']:
        key, frame = item['key'], item['frame']
        state = selection['frames'][key]
        row = {**item, 'review_status': state['review_status'],
               'status_text': state['status_text'],
               'display_version': state['display_version'], 'images': {}}
        row['correction'] = state.get('requested_change', item['correction'])
        if state.get('appearance_approval'):
            row['appearance_approval'] = state['appearance_approval']
        latest_version = state['latest_version']
        latest_request = folder / f'{frame}-v{latest_version}-request.json'
        latest = {'version': latest_version, 'status': state['latest_status'],
                  'request': linked_pin(latest_request)}
        if latest['status'] == 'blocked':
            latest['failure'] = linked_pin(folder / f'{frame}-v{latest_version}-failure.json')
        row['latest_request'] = latest
        if state.get('history'):
            row['history'] = state['history']
        images = [('original', 'Original', ROOT / item['original']['path']),
                  ('earlier', item['previous_label'], ROOT / item['previous']['path'])]
        version = state['display_version']
        if version is not None:
            record_path = folder / f'{frame}-record-v{version}.json'
            generation = json.loads(record_path.read_text(encoding='utf-8'))
            output = ROOT / generation['output']['path']
            row['displayed_attempt'] = {
                'version': version, 'record': pin(record_path),
                'request': generation['request'], 'output': generation['output'],
                'references': generation['references'],
            }
            title = (f'Accepted leg connection v{version}' if row['review_status'] == 'approved_by_user'
                     else f'New attempt v{version}')
            images.append(('attempt', title, output))
        cards = []
        for kind, title, path in images:
            info = linked_pin(path)
            row['images'][kind] = info
            url = html.escape(info['url'], quote=True)
            label = html.escape(f'{title} {key}', quote=True)
            cards.append(f'<figure><figcaption>{html.escape(title)}</figcaption>'
                         f'<a class="art" href="{url}" target="_blank" rel="noopener" aria-label="Open {label}">'
                         f'<canvas width="960" height="600" data-key="{key}" data-kind="{kind}" aria-label="{label}"></canvas>'
                         '</a></figure>')
        if version is None:
            missing = ('A new attempt is running. No image has returned yet.' if latest['status'] == 'in_progress'
                       else 'The latest request was blocked. No replacement drawing is available for this row.')
            cards.append('<figure><figcaption>No new image</figcaption>'
                         f'<div class="unavailable">{missing}</div></figure>')
        links = [f'<a href="{html.escape(latest["request"]["url"], quote=True)}">Exact latest built-in request</a>']
        if 'failure' in latest:
            links.append(f'<a href="{html.escape(latest["failure"]["url"], quote=True)}">Recorded tool failure</a>')
        for attempt in row.get('history', []):
            if 'failure' in attempt:
                failure_url = html.escape(rel(ROOT / attempt['failure']['path']), quote=True)
                links.append(f'<a href="{failure_url}">Historical v{attempt["version"]} tool failure</a>')
            elif attempt['status'] == 'not_submitted':
                request_url = html.escape(rel(ROOT / attempt['request']['path']), quote=True)
                links.append(f'<a href="{request_url}">Historical v{attempt["version"]} unsubmitted request</a>')
        label = STATUS_LABELS[row['review_status']]
        latest_label = LATEST_LABELS[latest['status']]
        sections[item['group']].append(
            f'<article class="comparison" id="frame-{key}" data-key="{key}" data-status="{row["review_status"]}">'
            f'<h3>SSUZY1 {frame}</h3>'
            f'<p class="row-status"><strong>{html.escape(label)}</strong> · Built-in v{latest_version}: {html.escape(latest_label)}</p>'
            f'<p class="status-detail">{html.escape(row["status_text"])}</p>'
            f'<p class="instruction">Requested change: {html.escape(row["correction"])}</p>'
            f'<p class="request-links">{" · ".join(links)}</p>'
            '<div class="row">' + ''.join(cards) + '</div></article>')
        rows.append(row)
    counts = {
        'comparison_count': len(rows),
        'displayed_new_attempt_count': sum(row['display_version'] is not None for row in rows),
        'no_new_image_count': sum(row['display_version'] is None for row in rows),
        'latest_request_blocked_count': sum(row['latest_request']['status'] == 'blocked' for row in rows),
        'latest_request_not_submitted_count': sum(row['latest_request']['status'] == 'not_submitted' for row in rows),
        'image_panel_count': sum(len(row['images']) for row in rows),
        'placeholder_panel_count': sum(row['display_version'] is None for row in rows),
        'review_status_counts': {status: sum(row['review_status'] == status for row in rows)
                                 for status in STATUS_LABELS},
    }
    links = {'local_generation_handoff': 'local-generation-handoff/index.html',
             'prior_refusal_audit': 'prior-refusal-audit.json',
             'prior_refusal_notes': 'refusal-audit-notes.md'}
    local_review_path = HERE / 'local-generation-test/review.html'
    if local_review_path.exists():
        links['local_generation_review'] = 'local-generation-test/review.html'
        local_review_markup = '<a href="local-generation-test/review.html">Local test review</a>'
    else:
        local_review_markup = '<span>Local test review pending</span>'
    summary = (f'{counts["comparison_count"]} comparisons: '
               f'{counts["review_status_counts"]["ready_for_review"]} revised drawings for review and '
               f'{counts["review_status_counts"]["approved_by_user"]} accepted leg connection. '
               f'{counts["displayed_new_attempt_count"]} new images available. Earlier attempt records remain linked.')
    data = {'schema_version': 2, 'total': len(rows), 'status': selection['status'],
            'counts': counts, 'summary': summary, 'links': links, 'frames': rows,
            'appearance_approval': selection.get('appearance_approval'),
            'latest_request_scope': 'Most recent built-in image-tool request per frame; local follow-up tests are recorded separately.',
            'production_integrated': False, 'native_motion_checked': False}
    save(HERE / 'review-data.json', data)
    markup = '\n'.join(
        f'<section class="group" id="group-{group}" data-group="{group}"><h2>{title}</h2>'
        + '\n'.join(sections[group]) + '</section>' for group, title in GROUPS.items())
    template = (HERE / 'review-template.html').read_text(encoding='utf-8')
    page = template.replace('{{SECTIONS}}', markup).replace('{{SUMMARY}}', html.escape(summary))
    page = page.replace('{{TOTAL}}', str(len(rows)))
    page = page.replace('{{LOCAL_REVIEW}}', local_review_markup)
    (HERE / 'review.html').write_text(page, encoding='utf-8', newline='\n')
    record = {'schema_version': 2, 'status': selection['status'], 'counts': counts,
              'frames': rows, 'page': pin(HERE / 'review.html'), 'data': pin(HERE / 'review-data.json'),
              'feedback': pin(HERE / 'feedback.json'), 'selected_versions': pin(HERE / 'selected-versions.json'),
              'helpers': [pin(HERE / name) for name in
                          ['build_review.py', 'record_output.py', 'review.js', 'review-template.html']],
              'notes': [pin(path) for path in sorted(HERE.glob('*-notes.md'))],
              'production_archive': pin(ROOT / 'assets/scrantic_data.zip'),
              'links': links, 'appearance_approval': selection.get('appearance_approval'),
              'production_integrated': False, 'native_motion_checked': False}
    if (HERE / 'prior-refusal-audit.json').exists():
        record['prior_refusal_audit'] = pin(HERE / 'prior-refusal-audit.json')
    if (HERE / 'feedback-local-followup.json').exists():
        record['local_followup_feedback'] = pin(HERE / 'feedback-local-followup.json')
    save(HERE / 'review-record.json', record)
    print(json.dumps({'status': data['status'], 'counts': counts}))

if __name__ == '__main__':
    main()
