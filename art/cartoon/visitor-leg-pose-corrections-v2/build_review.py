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
    'approved_by_user': 'Appearance approved',
    'local_test_pending': 'Local test pending',
    'in_progress': 'New attempt running',
    'awaiting_correction': 'Awaiting correction',
}
LATEST_LABELS = {
    'returned': 'Image returned',
    'blocked': 'Blocked: no image returned',
    'not_submitted': 'Prepared, not submitted',
    'in_progress': 'Running',
}
ARTIFACT_LABELS = {
    'direct_png_composite': 'direct PNG composite',
    'imported_screenshot_crop': 'imported screenshot crop',
    'imported_screenshot_cutout': 'transparent screenshot cutout',
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
        row['previous'] = state.get('comparison_previous', item['previous'])
        row['previous_label'] = state.get('previous_label', item['previous_label'])
        if state.get('pose_reference'):
            row['pose_reference'] = linked_pin(ROOT / state['pose_reference']['path'])
        if state.get('instruction_references'):
            row['instruction_references'] = [
                {**linked_pin(ROOT / ref['path']), 'label': ref['label']}
                for ref in state['instruction_references']]
        if state.get('latest_feedback'):
            row['latest_feedback'] = linked_pin(ROOT / state['latest_feedback']['path'])
        if state.get('related_evidence'):
            row['related_evidence'] = [
                {**linked_pin(ROOT / ref['path']), 'label': ref['label']}
                for ref in state['related_evidence']]
        if state.get('appearance_approval'):
            row['appearance_approval'] = state['appearance_approval']
        if state.get('appearance_approval_history'):
            row['appearance_approval_history'] = state['appearance_approval_history']
        if state.get('artifact_history'):
            row['artifact_history'] = state['artifact_history']
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
                  ('earlier', row['previous_label'], ROOT / row['previous']['path'])]
        version = state['display_version']
        artifact = state.get('display_artifact')
        if artifact:
            record_path = ROOT / artifact['record']['path']
            artifact_record = json.loads(record_path.read_text(encoding='utf-8'))
            output = ROOT / artifact_record['output']['path']
            artifact_kind = artifact['kind']
            row['displayed_attempt'] = {
                'kind': artifact_kind, 'version': artifact['version'],
                'record': pin(record_path), 'output': artifact_record['output'],
                'references': artifact_record.get('references', [artifact_record[k] for k in ('source', 'generated') if k in artifact_record]),
                'tool': artifact_record.get('tool', artifact_record.get('mode', 'recorded artwork')),
                'method': artifact_record.get('method', 'The linked record preserves the generated bottle edit and the exact approved body used for the local composite.'),
                'image': artifact_record.get('image'),
            }
            latest['historical_to_current_artifact'] = True
            title = artifact.get('title') or state.get('display_label') or f'{ARTIFACT_LABELS[artifact_kind].capitalize()} v{artifact["version"]}'
            images.append(('attempt', title, output))
        elif version is not None:
            record_path = folder / f'{frame}-record-v{version}.json'
            generation = json.loads(record_path.read_text(encoding='utf-8'))
            output = ROOT / generation['output']['path']
            row['displayed_attempt'] = {
                'version': version, 'record': pin(record_path),
                'request': generation['request'], 'output': generation['output'],
                'references': generation['references'],
            }
            title = state.get('display_label') or (
                f'Approved drawing v{version}' if row['review_status'] == 'approved_by_user'
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
        if version is None and not artifact:
            missing = state.get('no_image_text') or (
                'A new attempt is running. No image has returned yet.' if latest['status'] == 'in_progress'
                else 'The latest request was blocked. No replacement drawing is available for this row.')
            cards.append('<figure><figcaption>No replacement drawing</figcaption>'
                         f'<div class="unavailable">{html.escape(missing)}</div></figure>')
        latest_request_label = f'Historical built-in v{latest_version} request' if artifact else 'Exact latest built-in request'
        links = [f'<a href="{html.escape(latest["request"]["url"], quote=True)}">{latest_request_label}</a>']
        if version is not None and version != latest_version and not artifact:
            shown_request_url = html.escape(rel(ROOT / row['displayed_attempt']['request']['path']), quote=True)
            links.append(f'<a href="{shown_request_url}">Exact displayed v{version} request</a>')
        if artifact:
            artifact_record_url = html.escape(rel(record_path), quote=True)
            artifact_record_label = {
                'imported_screenshot_crop': 'Crop source and method',
                'imported_screenshot_cutout': 'Cutout source and method',
                'direct_png_composite': 'Direct composite method and sources',
            }[artifact_kind]
            links.insert(0, f'<a href="{artifact_record_url}">{artifact_record_label}</a>')
        if row.get('pose_reference'):
            reference_url = html.escape(row['pose_reference']['url'], quote=True)
            links.append(f'<a href="{reference_url}" target="_blank" rel="noopener">Approved 003 leg reference</a>')
        for ref in row.get('instruction_references', []):
            url = html.escape(ref['url'], quote=True)
            links.append(f'<a href="{url}" target="_blank" rel="noopener">{html.escape(ref["label"])}</a>')
        if row.get('latest_feedback'):
            url = html.escape(row['latest_feedback']['url'], quote=True)
            links.append(f'<a href="{url}">Latest exact feedback</a>')
        if 'failure' in latest:
            failure_label = 'Historical tool failure' if artifact else 'Recorded tool failure'
            links.append(f'<a href="{html.escape(latest["failure"]["url"], quote=True)}">{failure_label}</a>')
        for attempt in row.get('history', []):
            if 'failure' in attempt:
                failure_url = html.escape(rel(ROOT / attempt['failure']['path']), quote=True)
                links.append(f'<a href="{failure_url}">Historical v{attempt["version"]} tool failure</a>')
            elif attempt['status'] == 'not_submitted':
                request_url = html.escape(rel(ROOT / attempt['request']['path']), quote=True)
                links.append(f'<a href="{request_url}">Historical v{attempt["version"]} unsubmitted request</a>')
            elif attempt['status'] == 'rejected_by_user':
                output_url = html.escape(rel(ROOT / attempt['output']['path']), quote=True)
                links.append(f'<a href="{output_url}">Rejected v{attempt["version"]} drawing</a>')
            elif attempt['status'] == 'reopened_for_correction':
                approval_url = html.escape(rel(ROOT / attempt['appearance_approval']['record']['path']), quote=True)
                links.append(f'<a href="{approval_url}">Historical v{attempt["version"]} appearance approval (reopened)</a>')
        for attempt in row.get('artifact_history', []):
            record_url = html.escape(rel(ROOT / attempt['record']['path']), quote=True)
            history_label = ARTIFACT_LABELS.get(attempt.get('kind'), 'artifact')
            links.append(f'<a href="{record_url}">Previous {history_label} source and method</a>')
        evidence_links = []
        for ref in row.get('related_evidence', []):
            url = html.escape(ref['url'], quote=True)
            evidence_links.append(f'<a href="{url}" target="_blank" rel="noopener">{html.escape(ref["label"])}</a>')
        evidence_markup = (f'<p class="request-links">{" · ".join(evidence_links)}</p>'
                           if evidence_links else '')
        label = STATUS_LABELS[row['review_status']]
        latest_label = LATEST_LABELS[latest['status']]
        source_label = (f'{row["displayed_attempt"]["tool"]}: {ARTIFACT_LABELS[artifact_kind]}' if artifact
                        else f'Built-in v{latest_version}: {latest_label}')
        method_markup = (f'<p class="status-detail">{html.escape(str(row["displayed_attempt"]["method"]))}</p>'
                         if artifact else '')
        sections[item['group']].append(
            f'<article class="comparison" id="frame-{key}" data-key="{key}" data-status="{row["review_status"]}">'
            f'<h3>SSUZY1 {frame}</h3>'
            f'<p class="row-status"><strong>{html.escape(label)}</strong> · {html.escape(source_label)}</p>'
            f'<p class="status-detail">{html.escape(row["status_text"])}</p>'
            + method_markup +
            f'<p class="instruction">Requested change: {html.escape(row["correction"])}</p>'
            f'<p class="request-links">{" · ".join(links)}</p>'
            + evidence_markup +
            '<div class="row">' + ''.join(cards) + '</div></article>')
        rows.append(row)
    counts = {
        'comparison_count': len(rows),
        'displayed_new_attempt_count': sum('attempt' in row['images'] for row in rows),
        'no_new_image_count': sum('attempt' not in row['images'] for row in rows),
        'latest_request_blocked_count': sum(row['latest_request']['status'] == 'blocked' for row in rows),
        'latest_request_not_submitted_count': sum(row['latest_request']['status'] == 'not_submitted' for row in rows),
        'image_panel_count': sum(len(row['images']) for row in rows),
        'placeholder_panel_count': sum('attempt' not in row['images'] for row in rows),
        'review_status_counts': {status: sum(row['review_status'] == status for row in rows)
                                 for status in STATUS_LABELS},
    }
    links = {'local_generation_handoff': 'local-generation-handoff/index.html',
             'prior_refusal_audit': 'prior-refusal-audit.json',
             'prior_refusal_notes': 'refusal-audit-notes.md'}
    if (HERE / 'acceptance/appearance-v1.json').exists():
        links['appearance_approval'] = 'acceptance/appearance-v1.json'
    local_review_path = HERE / 'local-generation-test/review.html'
    if local_review_path.exists():
        links['local_generation_review'] = 'local-generation-test/review.html'
        local_review_markup = '<a href="local-generation-test/review.html">Local test review</a>'
    else:
        local_review_markup = '<span>Local test review pending</span>'
    summary = (f'{counts["comparison_count"]} comparisons: '
               f'{counts["review_status_counts"]["approved_by_user"]} appearance approved, '
               f'{counts["review_status_counts"]["ready_for_review"]} revised drawings for review, '
               f'{counts["review_status_counts"]["awaiting_correction"]} awaiting correction. '
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
                          ['build_review.py', 'record_output.py', 'record-005-v2.py', 'review.js', 'review-template.html',
                           'prepare-feedback-004-005.py', 'finalize-feedback-004-005.py', 'finalize-005-v3-outcome.py']],
              'notes': [pin(path) for path in sorted(set(HERE.glob('*-notes.md')) | {
                  HERE / 'session-status.md', HERE / 'successful-prompts.md', HERE / '004-hip-attempts.md'})],
              'production_archive': pin(ROOT / 'assets/scrantic_data.zip'),
              'links': links, 'appearance_approval': selection.get('appearance_approval'),
              'production_integrated': False, 'native_motion_checked': False}
    if (HERE / 'prior-refusal-audit.json').exists():
        record['prior_refusal_audit'] = pin(HERE / 'prior-refusal-audit.json')
    if (HERE / 'feedback-local-followup.json').exists():
        record['local_followup_feedback'] = pin(HERE / 'feedback-local-followup.json')
    if (HERE / 'acceptance/appearance-v1.json').exists():
        record['appearance_acceptance'] = pin(HERE / 'acceptance/appearance-v1.json')
    feedback_004 = selection['frames'].get('SSUZY1.BMP-004', {}).get('latest_feedback')
    if feedback_004:
        record['latest_004_feedback'] = pin(ROOT / feedback_004['path'])
    feedback_005 = selection['frames'].get('SSUZY1.BMP-005', {}).get('latest_feedback')
    if feedback_005:
        record['latest_005_feedback'] = pin(ROOT / feedback_005['path'])
    if (HERE / '004-proportions-005-elbow-outcomes.json').exists():
        record['latest_004_005_outcomes'] = pin(HERE / '004-proportions-005-elbow-outcomes.json')
    save(HERE / 'review-record.json', record)
    print(json.dumps({'status': data['status'], 'counts': counts}))

if __name__ == '__main__':
    main()
