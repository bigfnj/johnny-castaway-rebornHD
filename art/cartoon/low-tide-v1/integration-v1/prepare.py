"""Prepare and validate the accepted low-tide package without promoting it."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOW = HERE.parent
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import source_catalog
from art_pack import accepted_pack, build_archive

BASE = 'da787d63279ea91bd6c637e02133821339470bfc'
BASE_SHA = '4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6'
FINAL_SHA = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
PREFIX = 'data/styles/cartoon/'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def hashes(archive):
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'duplicate ZIP member'
        return {n: sha(z.read(n)) for n in names}


def differences(expected, actual):
    return [n for n in sorted(set(expected) | set(actual)) if expected.get(n) != actual.get(n)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--reviewed-candidate', required=True, type=Path)
    args = p.parse_args()
    assert not args.output.exists(), 'use a fresh output directory'
    assert sha(args.reviewed_candidate.read_bytes()) == FINAL_SHA, 'reviewed candidate identity'
    baseline = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':assets/scrantic_data.zip'])
    assert sha(baseline) == BASE_SHA, 'baseline identity'
    prior_bytes = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':art/cartoon/pack.json'])
    prior = json.loads(prior_bytes)
    selected = load(LOW / 'wave-candidate-v1.json')['frames']
    assert len(selected) == 14 and len(prior['assets']) == 47
    selected_paths = {r['path'] for r in selected}
    assert not selected_paths.intersection(r['path'] for r in prior['assets'])
    before = hashes(io.BytesIO(baseline))
    reviewed = hashes(args.reviewed_candidate)
    assert len(before) == 2598 and len(reviewed) == 2612
    assert not differences(before, {n: reviewed.get(n) for n in before}), 'existing payload changed'
    assert set(reviewed) - set(before) == {PREFIX + p for p in selected_paths}

    args.output.mkdir(parents=True)
    base_path = args.output / 'baseline.zip'
    base_path.write_bytes(baseline)
    recipe_path = HERE / 'runtime-recipe.json'
    approval_path = HERE / 'production-acceptance.json'
    recipe_name = recipe_path.relative_to(ROOT).as_posix()
    approval_name = approval_path.relative_to(ROOT).as_posix()
    prior_approval = ROOT / prior['acceptance_record']
    ledger = copy.deepcopy(prior)
    frames = []
    with zipfile.ZipFile(io.BytesIO(baseline)) as z:
        sources = source_catalog(z)
        for row in selected:
            path = row['path']
            png = ROOT / row['source']
            assert sha(png.read_bytes()) == row['sha256'] == reviewed[PREFIX + path], path
            frame = int(Path(path).stem)
            report = (LOW / 'static-v2/export.json' if frame < 3 else
                      LOW / 'wave-reuse-v1/candidates/v1/export-report.json' if frame < 39 else
                      LOW / 'rock-waves-v1/exports-v1/export.json')
            exporter = (LOW / 'export_draft.py' if frame < 3 else
                        LOW / 'wave-reuse-v1/export.py' if frame < 39 else
                        LOW / 'rock-waves-v1/export.py')
            frames.append({'frame': frame, 'path': path, 'runtime_canvas': row['size'],
                           'candidate_png_sha256': row['sha256'], 'selected_png': binding(png),
                           'source_sha256': sources[path]['source_sha256'],
                           'authoring_report': binding(report), 'exporter': binding(exporter)})
            ledger['assets'].append({'path': path, 'sha256': row['sha256'],
                                     'source_sha256': sources[path]['source_sha256'],
                                     'alpha': 'transparent', 'recipe': recipe_name, 'review': approval_name})
            ledger['required_assets'].append(path)
    save(recipe_path, {'schema_version': 1, 'accepted': True,
         'scope': 'Fourteen approved low-tide additions on existing native canvases; no runtime or logical-coordinate changes.',
         'source_sha256_semantics': 'HD proxy bytes, not generated raw art.',
         'baseline_commit': BASE, 'baseline_archive_sha256': BASE_SHA,
         'reviewed_candidate_sha256': FINAL_SHA, 'frames': frames,
         'reproduction': 'Exporters pin the old baseline. Replay from commit 9e2f061 with its baseline archive in isolated scratch; do not replace a promoted live archive to replay historical authoring.'})
    save(approval_path, {'schema_version': 1, 'date': '2026-09-17', 'accepted': True,
         'human_response': 'oh, the low-tide does it, nm, its fine.',
         'reviewed_url': 'http://127.0.0.1:8937/review.html',
         'scope': 'Accept the combined low-tide beach, rock and ripple composition shown. The user withdrew the objection to the broad gaps between ripple families. Preserve this spacing. This records acceptance of the shown composition, not a claim that every clip or story context was individually reviewed.',
         'static_approval': binding(LOW / 'static-shape-approval.json'),
         'review': binding(LOW / 'motion-review-v1/review.html'),
         'review_manifest': binding(LOW / 'motion-review-v1/manifest.json'),
         'native_evidence': binding(LOW / 'waves-native-v1/evidence-v1/evidence.json'),
         'reviewed_candidate_sha256': FINAL_SHA, 'runtime_coverage': 'partial',
         'newly_accepted_assets': [r['path'] for r in selected],
         'inherited_acceptances': [{**binding(prior_approval), 'asset_paths': [r['path'] for r in prior['assets']]}],
         'accepted_assets': [{'path': r['path'], 'sha256': r['sha256'], 'recipe': r['recipe']} for r in ledger['assets']],
         'runtime_recipe': binding(recipe_path)})
    ledger['acceptance_record'] = approval_name
    ledger['review_status'] = 'Approved low-tide beach, rock and ripple composition; prior character, high-tide and seasonal approvals inherited unchanged.'
    ledger['scope'] = 'Partial Cartoon pack: 28 Johnny poses, 29 island/environment assets and four seasonal decorations. Clouds, night and other story slots retain fallback.'
    save(HERE / 'integrated-pack.json', ledger)
    (HERE / 'prior-pack.json').write_bytes(prior_bytes)
    accepted = args.output / 'accepted'
    with zipfile.ZipFile(args.reviewed_candidate) as z:
        for row in ledger['assets']:
            dest = accepted / row['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(PREFIX + row['path']))
    with zipfile.ZipFile(base_path) as z:
        runtime, packed, alpha = accepted_pack(z, ledger, accepted, 'integrated-pack.json')
    print('SMOKE PASS standard pack validation: 61 accepted PNGs', flush=True)
    output = args.output / 'scrantic_data.zip'
    packed_report = build_archive(base_path, output, runtime, packed)
    assert hashes(output) == reviewed and sha(output.read_bytes()) == FINAL_SHA, 'rebuilt package differs from review'
    print('REGRESSION PASS exact reviewed ZIP and all 2598 prior payloads', flush=True)
    changed_name = PREFIX + 'BMP/BACKGRND.BMP/034.png'
    damaged = dict(reviewed, **{changed_name: '0' * 64})
    assert differences(reviewed, damaged) == [changed_name], 'one named member control'
    assert differences(reviewed, reviewed) == [], 'restored member control'
    save(HERE / 'package-verification.json', {'status': 'PASS', 'baseline_commit': BASE,
         'baseline_archive_sha256': BASE_SHA, 'archive_sha256': FINAL_SHA,
         'members': len(reviewed), 'accepted_assets': len(packed), 'alpha': alpha,
         'added_members': sorted(set(reviewed) - set(before)), 'existing_members_unchanged': len(before),
         'inherited_ledger_rows_unchanged': ledger['assets'][:47] == prior['assets'],
         'pilot_history_unchanged': ledger['pilot_history'] == prior['pilot_history'],
         'runtime_manifest_bytes_unchanged': before[PREFIX+'manifest.json'] == reviewed[PREFIX+'manifest.json'],
         'standard_packer': packed_report, 'exact_reviewed_archive_reproduced': True,
         'member_negative_control': {'name': changed_name, 'failures': differences(reviewed, damaged), 'restored': 'PASS'},
         'helper': binding(Path(__file__)), 'production_promoted': False})


if __name__ == '__main__':
    main()
