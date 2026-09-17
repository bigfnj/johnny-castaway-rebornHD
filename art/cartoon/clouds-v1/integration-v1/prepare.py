"""Bind the approved clouds, validate standard packing, and promote exact reviewed bytes."""
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
CLOUD = HERE.parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from art_common import ArtError, source_catalog
from art_pack import accepted_pack, build_archive
from art_production_catalog import approval_origins, keyed

BASE_COMMIT = 'de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc'
BASE_SHA = 'a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'
FINAL_SHA = 'a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d'
EVIDENCE_SHA = '1d156cb3f398643d4a8d4be9a9d65943396bd15c61a9b9c87d76efcf46045ce0'
PREFIX = 'data/styles/cartoon/'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def payloads(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert len(z.namelist()) == len(set(z.namelist())), 'duplicate ZIP member'
        return {name: sha(z.read(name)) for name in z.namelist()}


def approval_check(acceptance):
    name = (HERE / 'production-acceptance.json').relative_to(ROOT).as_posix()
    return approval_origins(acceptance, keyed(acceptance['accepted_assets'], name), name,
                            lambda p: load(ROOT / p), lambda p: sha((ROOT / p).read_bytes()))


def prepare(output, reviewed):
    assert not output.exists(), 'use a fresh integration output directory'
    candidate_bytes = reviewed.read_bytes()
    assert sha(candidate_bytes) == FINAL_SHA, 'reviewed cloud candidate identity differs'
    baseline = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE_COMMIT + ':assets/scrantic_data.zip'])
    assert sha(baseline) == BASE_SHA, 'baseline archive identity differs'
    old_pack = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE_COMMIT + ':art/cartoon/pack.json'])
    prior = json.loads(old_pack)
    assert len(prior['assets']) == 61, 'prior accepted asset count differs'
    assert load(ROOT / 'art/cartoon/pack.json') == prior, 'live ledger changed before preparation'
    evidence_dir = CLOUD / 'native-v1/evidence-v1'
    evidence = load(evidence_dir / 'evidence.json')
    assert sha((evidence_dir / 'evidence.json').read_bytes()) == EVIDENCE_SHA, 'approved evidence identity differs'
    for name, row in evidence['files'].items():
        assert sha((evidence_dir / name).read_bytes()) == row['sha256'], 'approved evidence member differs: ' + name
    assert evidence['candidate_sha256'] == FINAL_SHA and evidence['status'] == 'PASS'
    before, shown = payloads(baseline), payloads(candidate_bytes)
    selected = load(CLOUD / 'export/export-report.json')['frames']
    assert [r['frame'] for r in selected] == [16, 17]
    added = {PREFIX + r['path'] for r in selected}
    assert len(before) == 2612 and len(shown) == 2614
    assert set(shown) - set(before) == added and all(shown.get(n) == h for n, h in before.items()), 'prior membership or payload differs'
    output.mkdir(parents=True)
    (output / 'baseline.zip').write_bytes(baseline)
    (HERE / 'prior-pack.json').write_bytes(old_pack)
    ledger = copy.deepcopy(prior)
    recipe_path, approval_path = HERE / 'runtime-recipe.json', HERE / 'production-acceptance.json'
    recipe_name, approval_name = recipe_path.relative_to(ROOT).as_posix(), approval_path.relative_to(ROOT).as_posix()
    frames = []
    with zipfile.ZipFile(io.BytesIO(baseline)) as z:
        catalog = source_catalog(z)
        for row in selected:
            path, frame = row['path'], row['frame']
            png = CLOUD / 'export' / path
            assert sha(png.read_bytes()) == row['sha256'] == shown[PREFIX + path], path + ': selected payload differs'
            frames.append({'frame': frame, 'path': path, 'runtime_canvas': row['canvas'],
                'candidate_png_sha256': row['sha256'], 'selected_png': binding(png),
                'source_sha256': catalog[path]['source_sha256'],
                'generated_source': binding(CLOUD / f'generation/{frame:03}-generated-v2.png'),
                'generation_record': binding(CLOUD / 'generation/record.json'),
                'authoring_recipe': binding(CLOUD / 'recipe.json'),
                'authoring_report': binding(CLOUD / 'export/export-report.json'),
                'exporter': binding(CLOUD / 'export.py'), 'affine_forward': row['affine_forward']})
            ledger['assets'].append({'path': path, 'sha256': row['sha256'], 'source_sha256': catalog[path]['source_sha256'],
                                    'alpha': 'transparent', 'recipe': recipe_name, 'review': approval_name})
            ledger['required_assets'].append(path)
    save(recipe_path, {'schema_version': 1, 'accepted': True,
        'scope': 'Two approved ordinary island clouds on unchanged original runtime canvases and logical coordinates.',
        'source_sha256_semantics': 'Existing HD proxy bytes, not generated raw art.',
        'baseline_commit': BASE_COMMIT, 'baseline_archive_sha256': BASE_SHA,
        'reviewed_candidate_sha256': FINAL_SHA, 'frames': frames,
        'replay': 'Recover the pinned baseline into separate scratch and use export.py --baseline; do not replace promoted live assets to replay.'})
    acceptance = {'schema_version': 1, 'date': '2026-09-17', 'accepted': True,
        'human_question': 'Do the new medium and large clouds in the right-hand panel look right in shape, style and motion? The medium cloud is slightly flatter than the original.',
        'human_response': 'Yes, keep these clouds', 'reviewed_url': 'http://127.0.0.1:8938/review.html',
        'scope': 'Accept the displayed medium016 and large017 Cartoon cloud shapes, style and motion, including the slightly flatter medium cloud. Prior61 approvals are inherited unchanged.',
        'offered_review_variants': ['day_left', 'day_right', 'night_shift_right'],
        'scope_limits': 'The review offered daylight both wind directions and the night edge/shift case. This does not assert that the user watched every clip, complete wrap traversal, every story context, or approval of styling the fallback night background.',
        'review': binding(evidence_dir / 'review/review.html'),
        'review_manifest': binding(evidence_dir / 'review/manifest.json'),
        'review_atlases': [binding(p) for p in sorted((evidence_dir / 'review').glob('atlas-*.png'))],
        'review_build': binding(evidence_dir / 'review/build.json'),
        'browser_observation': binding(evidence_dir / 'review/browser-review.md'),
        'native_evidence': binding(evidence_dir / 'evidence.json'),
        'native_summary': binding(evidence_dir / 'native/summary.json'),
        'reviewed_candidate_sha256': FINAL_SHA, 'runtime_coverage': 'partial',
        'newly_accepted_assets': [r['path'] for r in selected],
        'inherited_acceptances': [{**binding(ROOT / prior['acceptance_record']), 'asset_paths': [r['path'] for r in prior['assets']]}],
        'accepted_assets': [{'path': r['path'], 'sha256': r['sha256'], 'recipe': r['recipe']} for r in ledger['assets']],
        'runtime_recipe': binding(recipe_path)}
    save(approval_path, acceptance)
    origins = approval_check(acceptance)
    assert all(origins[r['path']] == r['review'] for r in ledger['assets']), 'approval origin differs from ledger'
    ledger['acceptance_record'] = approval_name
    ledger['review_status'] = 'Approved medium and large ordinary island cloud companions; prior character, island, tide and seasonal approvals inherited unchanged.'
    ledger['scope'] = 'Partial Cartoon pack: 28 Johnny poses, 31 island/environment assets and four seasonal decorations. Other story slots and night backgrounds retain fallback.'
    save(HERE / 'integrated-pack.json', ledger)
    accepted = output / 'accepted'
    with zipfile.ZipFile(io.BytesIO(candidate_bytes)) as z:
        for row in ledger['assets']:
            dest = accepted / row['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(PREFIX + row['path']))
    with zipfile.ZipFile(output / 'baseline.zip') as z:
        runtime, packed, alpha = accepted_pack(z, ledger, accepted, 'cloud integrated-pack.json')
    print('SMOKE PASS maintained pack validation and63 approval origins', flush=True)
    rebuilt = output / 'standard-rebuilt.zip'
    built = build_archive(output / 'baseline.zip', rebuilt, runtime, packed)
    assert payloads(rebuilt.read_bytes()) == shown, 'standard rebuilt member payloads differ from review'
    corrupt = accepted / selected[0]['path']
    valid = corrupt.read_bytes()
    corrupt.write_bytes(valid + b'controlled-invalid-payload')
    try:
        with zipfile.ZipFile(output / 'baseline.zip') as z:
            accepted_pack(z, ledger, accepted, 'cloud integrated-pack.json')
    except ArtError as exc:
        failure = str(exc)
        assert failure == 'BMP/BACKGRND.BMP/016.png: accepted sha256 does not match PNG', failure
    else:
        raise AssertionError('corrupt016 accepted PNG unexpectedly passed')
    finally:
        corrupt.write_bytes(valid)
    with zipfile.ZipFile(output / 'baseline.zip') as z:
        assert len(accepted_pack(z, ledger, accepted)[1]) == 63
    bad = copy.deepcopy(acceptance)
    bad['newly_accepted_assets'] = bad['newly_accepted_assets'][:1]
    try:
        approval_check(bad)
    except ArtError as exc:
        approval_failure = str(exc)
        assert approval_failure.endswith(': new approval coverage differs from inherited complement')
    else:
        raise AssertionError('missing new approval unexpectedly passed')
    assert approval_check(acceptance) == origins
    save(HERE / 'package-readback.json', {'status': 'PASS', 'phase': 'prepared; production not yet promoted',
        'helper': binding(Path(__file__)), 'baseline_commit': BASE_COMMIT, 'baseline_archive_sha256': BASE_SHA,
        'reviewed_archive_sha256': FINAL_SHA, 'members': 2614, 'accepted_assets': 63,
        'baseline_payloads_unchanged': 2612, 'inherited_ledger_rows_unchanged': ledger['assets'][:61] == prior['assets'],
        'pilot_history_unchanged': ledger['pilot_history'] == prior['pilot_history'],
        'added_members_sha256': {n: shown[n] for n in sorted(added)},
        'alpha': alpha, 'standard_rebuild': built, 'standard_rebuild_payloads_equal_review': True,
        'standard_rebuild_envelope_equal_review': rebuilt.read_bytes() == candidate_bytes,
        'archive_format_note': 'The reviewed exporter retains the baseline member order and appends two clouds. The maintained packer rewrites the entire Cartoon prefix, including its manifest, in sorted order with its standard ZIP metadata/compression policy. All2614 payloads match; the ZIP envelope does not. Reproduce the exact approved envelope with the fixed cloud exporter and separately recovered baseline.',
        'maintained_controls': {'corrupt_accepted016_failure': failure, 'corrupt_accepted016_restored': 'PASS',
            'missing_new_approval_failure': approval_failure, 'approval_restored': 'PASS'},
        'control_scope': 'Actual disposable accepted PNG corruption and in-memory approval input through maintained validators; no source-removal mutant.',
        'runtime_recipe': binding(recipe_path), 'acceptance': binding(approval_path), 'ledger': binding(HERE / 'integrated-pack.json')})
    print('REGRESSION PASS payload-equivalent standard rebuild, two maintained refusal controls and restored positives', flush=True)


def promote(reviewed):
    report = load(HERE / 'package-readback.json')
    assert report['status'] == 'PASS' and report['reviewed_archive_sha256'] == FINAL_SHA
    candidate = reviewed.read_bytes()
    assert sha(candidate) == FINAL_SHA, 'candidate identity changed'
    ledger_bytes = (HERE / 'integrated-pack.json').read_bytes()
    assert sha(ledger_bytes) == report['ledger']['sha256'], 'prepared ledger identity changed'
    for field in ('runtime_recipe', 'acceptance'):
        assert sha((ROOT / report[field]['path']).read_bytes()) == report[field]['sha256'], field + ' changed'
    zip_path, pack_path = ROOT / 'assets/scrantic_data.zip', ROOT / 'art/cartoon/pack.json'
    old_zip, old_pack = zip_path.read_bytes(), pack_path.read_bytes()
    assert sha(old_zip) == BASE_SHA and json.loads(old_pack) == load(HERE / 'prior-pack.json'), 'live baseline changed'
    promotion_path = HERE / 'promotion.json'
    assert not promotion_path.exists(), 'promotion record already exists'
    promotion_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        zip_path.write_bytes(candidate)
        pack_path.write_bytes(ledger_bytes)
        assert zip_path.read_bytes() == candidate and pack_path.read_bytes() == ledger_bytes, 'promotion readback differs'
        save(promotion_path, {'status': 'PASS', 'archive_sha256': sha(zip_path.read_bytes()),
            'pack_sha256': sha(pack_path.read_bytes()), 'prior_archive_sha256': sha(old_zip), 'prior_pack_sha256': sha(old_pack),
            'package_readback': binding(HERE / 'package-readback.json'), 'approval': binding(HERE / 'production-acceptance.json'),
            'scope': 'Exact reviewed candidate promoted after maintained pack and approval checks; generated catalog checks follow.'})
    except BaseException:
        zip_path.write_bytes(old_zip)
        pack_path.write_bytes(old_pack)
        if promotion_path.exists():
            promotion_path.unlink()
        raise
    print('PROMOTED ' + FINAL_SHA, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'promote'])
    p.add_argument('--output', type=Path, default=ROOT / 'build/clouds-v1/integration-v1')
    p.add_argument('--reviewed-candidate', type=Path, default=ROOT / 'build/clouds-v1/candidate.zip')
    args = p.parse_args()
    print('WITNESS cloud-integration ' + sha(Path(__file__).read_bytes()), flush=True)
    if args.mode == 'prepare':
        prepare(args.output, args.reviewed_candidate)
    else:
        promote(args.reviewed_candidate)


if __name__ == '__main__':
    main()
