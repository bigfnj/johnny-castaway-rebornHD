"""Freeze the approved 14-slot composition without changing production."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import io

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SHORE = 'art/cartoon/shoreline-repair-v1/integrated-shore-v1'
SEASON = 'art/cartoon/seasonal-v1'
REL = HERE.relative_to(ROOT).as_posix()
BASE_COMMIT = '1aad361fe78dde2c956e05dc451b8d5bab100af0'
ART_COMMIT = 'aafb1ca380f7c50e26347893c30b1ca2a8dc4628'
BASE_SHA = '4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads((ROOT / p).read_bytes())


def bound(path):
    return {'path': path, 'sha256': sha((ROOT / path).read_bytes())}


def save(name, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    path = HERE / name
    if path.exists() and path.read_bytes() != raw:
        raise ValueError(name + ': refusing to overwrite a different frozen record')
    path.write_bytes(raw)


def main():
    wave_path = SHORE + '/side-fit-v1/selection.json'
    banner_path = SEASON + '/banner-inset-v1/selection.json'
    assert bound(wave_path)['sha256'] == '2e3796f8417a98bc249f71d3d9599a3f1dc5be987eb2c0f0c11818eb426341bb'
    assert bound(banner_path)['sha256'] == '070d0c06bcac3951e7b74e299c3178c4d1b01bd158569dcf76d2390f6ef89bbf'
    wave = load(wave_path)
    for key in ('shown_html', 'manifest', 'review_evidence', 'native_evidence'):
        if not wave[key].startswith('art/'):
            wave[key] = SHORE + '/side-fit-v1/' + wave[key]
    assert wave['user_response'] == 'Looks good, proceed' and wave['production_integration_authorized']
    baseline = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE_COMMIT + ':assets/scrantic_data.zip'])
    assert sha(baseline) == BASE_SHA
    prior_raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE_COMMIT + ':art/cartoon/pack.json'])
    prior = json.loads(prior_raw)
    metadata_path = SHORE + '/side-fit-v1/native/verification-v2/corrected-selection-v2.json'
    metadata = load(metadata_path)
    frames = []
    for old in metadata['frames']:
        row = {'frame': old['frame'], 'path': old['path'], 'runtime_canvas': old['canvas'],
               'candidate_png_sha256': old['sha256'], 'selected_png': bound(old['source_path']),
               'authoring_recipe': old['authoring_recipe'], 'authoring_report': old['authoring_report'],
               'footprint': old['footprint']}
        if 'source' in old:
            row['raw_source'] = {'path': old['source'], 'sha256': old['source_sha256']}
        else:
            row['raw_source'] = {'kind': 'zip_member', 'archive_sha256': BASE_SHA,
                                 'archive_git_commit': BASE_COMMIT, 'member': old['source_member'],
                                 'sha256': old['source_member_sha256']}
        frames.append(row)
    season_recipe = load(SEASON + '/recipe-v5.json')
    for f in range(4):
        folder = SEASON if f < 3 else SEASON + '/banner-inset-v1'
        recipe_path = folder + ('/recipe-v5.json' if f < 3 else '/recipe-v2.json')
        spec = season_recipe['frames'][f] if f < 3 else load(recipe_path)['frames'][0]
        candidate = folder + ('/candidates/v5/' if f < 3 else '/candidates/v2/') + spec['path']
        source = (ROOT / folder / spec['source']).resolve().relative_to(ROOT).as_posix()
        frames.append({'frame': f, 'path': spec['path'], 'runtime_canvas': spec['runtime_canvas'],
                       'candidate_png_sha256': bound(candidate)['sha256'], 'selected_png': bound(candidate),
                       'raw_source': bound(source), 'authoring_recipe': bound(recipe_path),
                       'authoring_report': bound(folder + ('/candidates/v5/export-report.json' if f < 3 else '/candidates/v2/export-report.json'))})
    assert len(frames) == 14 and len({r['path'] for r in frames}) == 14
    with zipfile.ZipFile(io.BytesIO(baseline)) as archive:
        for row in frames:
            row['source_sha256'] = sha(archive.read('data/hd/' + row['path']))
    recipe_path = REL + '/runtime-recipe.json'
    acceptance_path = REL + '/production-acceptance.json'
    save('runtime-recipe.json', {'schema_version': 1, 'accepted': True,
        'scope': 'Exact composition of approved shoreline, offshore waves and seasonal decorations. Per-row authoring records remain immutable ancestors.',
        'source_sha256_semantics': 'HD proxy bytes from the pinned baseline data/hd member, not generated raw art.',
        'selected_metadata': bound(metadata_path), 'frames': frames})
    selected = {r['path']: r for r in frames}
    ledger = copy.deepcopy(prior)
    newrows = {r['path']: {'path': r['path'], 'sha256': r['candidate_png_sha256'], 'source_sha256': r['source_sha256'],
                        'alpha': 'transparent', 'recipe': recipe_path, 'review': acceptance_path,
                        **({'footprint': r['footprint']} if 'footprint' in r else {})} for r in frames}
    ledger['assets'] = [newrows.get(r['path'], r) for r in prior['assets']] + [newrows[r['path']] for r in frames if r['path'] not in prior['required_assets']]
    ledger['required_assets'] += [r['path'] for r in frames if r['path'] not in prior['required_assets']]
    ledger['acceptance_record'] = acceptance_path
    ledger['review_status'] = 'Approved smooth shoreline, repositioned clean offshore wave motion, seasonal props and inset banner in the separately bound human checkpoints.'
    ledger['scope'] = 'Partial Cartoon pack: 28 Johnny poses, 15 island assets and four seasonal decorations. Other slots retain HD/original fallback; no universal story or original-executable parity claim.'
    ledger['pilot_history']['replaced_assets'] += [r['path'] for r in frames if r['path'].startswith('BMP/BACKGRND')]
    inherited = [r for r in prior['assets'] if r['path'] not in selected]
    assert len(inherited) == 33 and len(ledger['assets']) == 47
    save('prior-pack.json', prior)
    save('integrated-pack.json', ledger)
    parent = 'art/cartoon/skin-tone-v1/production-acceptance.json'
    approval = {'schema_version': 1, 'date': '2026-09-17', 'accepted': True, 'acceptance_record': acceptance_path,
        'human_response': wave['user_response'], 'reviewed_url': wave['shown_url'], 'reviewed_html_sha256': wave['shown_html_sha256'],
        'scope': 'Accept the ten selected shoreline assets and four seasonal assets, with the separately approved inset banner. Inherit exactly 33 unchanged assets. The shown native scenes and recorded responses define approval scope; no claim about which individual clips were watched or exhaustive story parity.',
        'runtime_coverage': 'partial', 'wave_approval': bound(wave_path), 'banner_approval': bound(banner_path),
        'newly_accepted_assets': list(selected), 'inherited_acceptances': [{**bound(parent), 'asset_paths': [r['path'] for r in inherited]}],
        'accepted_assets': [{k: r[k] for k in ('path', 'sha256', 'recipe')} for r in ledger['assets']],
        'runtime_recipe': bound(recipe_path),
        'review_bindings': {k: wave[k] for k in ('shown_html', 'shown_html_sha256', 'manifest', 'manifest_sha256', 'review_evidence', 'review_evidence_sha256', 'native_evidence', 'native_evidence_sha256')},
        'reviewed_wave_archive_sha256': wave['approved_private_archive_sha256'],
        'banner_composition': 'Replace only HOLIDAY003 in the reviewed wave package with e36e1030 approved inset banner; remaining 2597 payloads exact.'}
    save('production-acceptance.json', approval)
    private_path = ROOT / 'build/shoreline-repair-v1/side-clean-selected-v2/candidate.zip'
    assert sha(private_path.read_bytes()) == wave['approved_private_archive_sha256']
    with zipfile.ZipFile(private_path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == 2598
        save('reviewed-wave-members.json', {'archive_sha256': wave['approved_private_archive_sha256'],
            'members_sha256': {name: sha(archive.read(name)) for name in sorted(names)}})
    paths = {r['selected_png']['path'] for r in frames}
    for r in frames:
        paths.update(r[k]['path'] for k in ('authoring_recipe', 'authoring_report'))
        if 'path' in r['raw_source']: paths.add(r['raw_source']['path'])
    paths.update([wave_path, banner_path, metadata_path, parent])
    paths.update(wave[k] for k in ('shown_html', 'manifest', 'review_evidence', 'native_evidence'))
    paths.update(REL + '/' + name for name in ('prior-pack.json', 'integrated-pack.json', 'production-acceptance.json', 'runtime-recipe.json', 'reviewed-wave-members.json'))
    save('inputs.json', {'schema_version': 1, 'baseline_commit': BASE_COMMIT, 'source_snapshot_commit': ART_COMMIT,
        'baseline_archive_sha256': BASE_SHA, 'reviewed_wave_archive_sha256': wave['approved_private_archive_sha256'],
        'reviewed_wave_members': REL + '/reviewed-wave-members.json',
        'runtime_recipe': recipe_path, 'prior_pack': REL + '/prior-pack.json', 'integrated_pack': REL + '/integrated-pack.json',
        'protected_files_sha256': {p: bound(p)['sha256'] for p in sorted(paths)},
        'source_snapshot_paths': ['CMakeLists.txt', SEASON, 'art/cartoon/shoreline-repair-v1', 'art/cartoon/walk-pilot/profile-walk-v1/export.py'],
        'maintained_tools_lf_sha256': {p: sha((ROOT / p).read_bytes().replace(b'\r\n', b'\n')) for p in ['tools/art_pack.py', 'tools/art_common.py']}})
    print(json.dumps({'status': 'PASS', 'assets': 47, 'new': 14, 'inherited': 33, 'production_changed': False}))


if __name__ == '__main__':
    main()
