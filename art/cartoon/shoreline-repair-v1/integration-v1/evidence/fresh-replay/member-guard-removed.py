"""Reproduce the approved 47-asset composition in fresh scratch; no promotion."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import zipfile
import PIL

HERE = Path(__file__).resolve().parent
PREFIX = 'data/styles/cartoon/'
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_bytes())


def require(ok, label):
    if not ok:
        raise ValueError(label)


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def members(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'archive: duplicate member')
        return {n: sha(z.read(n)) for n in names}


def member_errors(expected, actual):
    return [n + ': member content differs' for n in sorted(set(expected) | set(actual)) if expected.get(n) != actual.get(n)]


def verify_inputs(repo, inputs):
    for name, digest in inputs['protected_files_sha256'].items():
        require(sha((repo / name).read_bytes()) == digest, name + ': protected bytes changed')
    for name, digest in inputs['maintained_tools_lf_sha256'].items():
        require(sha((repo / name).read_bytes().replace(b'\r\n', b'\n')) == digest, name + ': maintained tool changed')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--inputs', type=Path, default=HERE / 'inputs.json')
    p.add_argument('--output', type=Path)
    p.add_argument('--baseline', type=Path)
    p.add_argument('--wave-candidate', type=Path)
    p.add_argument('--audit-archive', type=Path)
    args = p.parse_args()
    repo = args.repo.resolve()
    inputs = load(args.inputs)
    helper_sha = sha(Path(__file__).read_bytes())
    witness = 'WITNESS shore-package ' + helper_sha
    print(witness, flush=True)
    verify_inputs(repo, inputs)
    specs = load(repo / inputs['runtime_recipe'])['frames']
    require(len(specs) == 14 and len({r['path'] for r in specs}) == 14, 'composition: expected14unique slots')
    baseline_raw = args.baseline.read_bytes() if args.baseline else subprocess.check_output(['git', '-C', str(repo), 'show', inputs['baseline_commit'] + ':assets/scrantic_data.zip'])
    require(sha(baseline_raw) == inputs['baseline_archive_sha256'], 'baseline: identity mismatch')
    before = members(io.BytesIO(baseline_raw))
    require(len(before) == 2594, 'baseline: expected2594members')
    expected = {**before, **{PREFIX + r['path']: r['candidate_png_sha256'] for r in specs}}
    if args.audit_archive:
        failures = member_errors(expected, members(args.audit_archive))
        pass  # executed guard removal
        print('PASS independent member audit', flush=True)
        return 0
    require(args.output is not None and not args.output.exists(), 'output: use a fresh directory')
    require(PIL.__version__ == '12.3.0', 'Pillow: reproduction requires12.3.0')
    wave_members = load(repo / inputs['reviewed_wave_members'])['members_sha256']
    if args.wave_candidate:
        require(sha(args.wave_candidate.read_bytes()) == inputs['reviewed_wave_archive_sha256'], 'reviewed wave package: identity differs')
        require(members(args.wave_candidate) == wave_members, 'reviewed wave package: recorded member map differs')
    else:
        print('LIMIT private ZIP not supplied: using preserved approved member map; independent private ZIP read NOT RUN', flush=True)
    banner = next(r for r in specs if r['path'] == 'BMP/HOLIDAY.BMP/003.png')
    composed = {**wave_members, PREFIX + banner['path']: banner['candidate_png_sha256']}
    require(expected == composed, 'reviewed wave plus inset banner: expected member map differs')
    prior = load(repo / inputs['prior_pack'])
    ledger_path = repo / inputs['integrated_pack']
    ledger = load(ledger_path)
    selected = {r['path']: r for r in specs}
    inherited = [r for r in prior['assets'] if r['path'] not in selected]
    require(len(inherited) == 33 and [r for r in ledger['assets'] if r['path'] not in selected] == inherited, 'ledger:33inherited rows changed')
    require(len(ledger['assets']) == 47 and ledger['runtime'] == prior['runtime'], 'ledger:47assets and retained runtime')
    require(ledger['pilot_history']['replaced_assets'] == prior['pilot_history']['replaced_assets'] + [r['path'] for r in specs if r['path'].startswith('BMP/BACKGRND')], 'ledger: pilot replacement scope')
    output = args.output.resolve()
    output.mkdir(parents=True)
    baseline = output / 'prior-4c8085be.zip'
    baseline.write_bytes(baseline_raw)
    commands = []

    def execute(label, argv, code=0, cwd=repo):
        completed = subprocess.run([sys.executable, '-B', *map(str, argv)], cwd=cwd, capture_output=True, text=True, timeout=300)
        for stream in ('stdout', 'stderr'):
            (output / (label + '.' + stream + '.txt')).write_text(getattr(completed, stream), encoding='utf-8', newline='\n')
        commands.append({'order': len(commands)+1, 'label': label, 'argv': ['python', '-B', *map(str, argv)],
                         'exit_code': completed.returncode, 'stdout': label + '.stdout.txt', 'stderr': label + '.stderr.txt',
                         'stdout_sha256': sha((output / (label + '.stdout.txt')).read_bytes()), 'stderr_sha256': sha((output / (label + '.stderr.txt')).read_bytes())})
        require(completed.returncode == code, label + ': ' + completed.stderr)
        return completed

    # Frozen exporters hardcode their repository-relative archive. Recover their
    # exact committed tree into isolated scratch, never replace the live archive.
    print('Preparing isolated source snapshot', flush=True)
    archive_bytes = subprocess.check_output(['git', '-C', str(repo), 'archive', '--format=zip', inputs['source_snapshot_commit'], *inputs['source_snapshot_paths']])
    source = output / 'source-snapshot'
    source.mkdir()
    snapshot_files = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            target = (source / info.filename).resolve()
            require(target.is_relative_to(source), 'source snapshot: path escapes scratch')
            raw = z.read(info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            snapshot_files[info.filename] = sha(raw)
    (source / 'assets').mkdir()
    (source / 'assets/scrantic_data.zip').write_bytes(baseline_raw)
    save(output / 'source-snapshot.json', {'commit': inputs['source_snapshot_commit'], 'paths': inputs['source_snapshot_paths'],
        'files_sha256': snapshot_files, 'archive_recovered_separately': inputs['baseline_archive_sha256']})
    shore = 'art/cartoon/shoreline-repair-v1/integrated-shore-v1'
    season = 'art/cartoon/seasonal-v1'
    jobs = [
        ('banner-smoke', season + '/banner-inset-v1/export_v2.py', season + '/banner-inset-v1/recipe-v2.json', ['BMP/HOLIDAY.BMP/003.png']),
        ('ground', shore + '/export.py', shore + '/recipe-v1.json', ['BMP/BACKGRND.BMP/000.png']),
        ('centers', shore + '/foam-refresh-v1/export_v2.py', shore + '/foam-refresh-v1/recipe-v2.json', ['BMP/BACKGRND.BMP/006.png', 'BMP/BACKGRND.BMP/008.png']),
        ('sides', shore + '/side-fit-v1/export.py', shore + '/side-fit-v1/recipe-v1.json', [f'BMP/BACKGRND.BMP/{f:03}.png' for f in (3,4,5,9,10,11)]),
        ('clean007', shore + '/foam-shading-v1/export.py', shore + '/foam-shading-v1/recipe-v1.json', ['BMP/BACKGRND.BMP/007.png']),
        ('seasonal', season + '/export_v5.py', season + '/recipe-v5.json', [f'BMP/HOLIDAY.BMP/{f:03}.png' for f in (0,1,2)])]
    reproduced = {}
    source_records = []
    for label, helper, recipe, paths in jobs:
        require((repo / helper).read_bytes() == (source / helper).read_bytes(), helper + ': snapshot helper differs')
        require((repo / recipe).read_bytes() == (source / recipe).read_bytes(), recipe + ': snapshot recipe differs')
        folder = output / ('replay-' + label)
        argv = [source / helper, '--recipe', source / recipe, '--output', folder]
        if label == 'sides':
            argv += ['--archive', baseline]
        execute('replay-' + label, argv, cwd=source)
        for path in paths:
            raw = (folder / path).read_bytes()
            require(sha(raw) == selected[path]['candidate_png_sha256'], path + ': source replay differs')
            reproduced[path] = raw
        source_records.append({'phase': 'smoke' if label == 'banner-smoke' else 'regression', 'label': label,
            'exporter': helper, 'exporter_sha256': sha((source / helper).read_bytes()), 'recipe': recipe,
            'recipe_sha256': sha((source / recipe).read_bytes()), 'exact_selected_pngs': paths})
        print(('SMOKE' if label == 'banner-smoke' else 'REGRESSION') + ' PASS exact source replay: ' + label, flush=True)
    require(set(reproduced) == set(selected), 'reproduction: all14selected slots required')
    save(output / 'source-replay.json', {'status': 'PASS', 'source_snapshot_sha256': sha((output / 'source-snapshot.json').read_bytes()),
        'selected_pngs': {p: sha(b) for p, b in reproduced.items()}, 'commands': source_records,
        'limit': 'Replayed the14 changed assets. The33 inherited outputs are checked byte-for-byte against their prior accepted package, not re-authored.'})
    accepted = output / 'accepted'
    with zipfile.ZipFile(baseline) as z:
        for row in ledger['assets']:
            path = row['path']
            raw = reproduced[path] if path in reproduced else z.read(PREFIX + path)
            require(sha(raw) == row['sha256'], path + ': staged accepted bytes differ')
            target = accepted / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    common = [repo / 'tools/art_pack.py', '--archive', baseline, '--ledger', ledger_path, '--accepted', accepted]
    smoke = json.loads(execute('pack-smoke', [common[0], 'validate', *common[1:]]).stdout)
    require(smoke['assets'] == 47, 'pack smoke: expected47assets')
    print('SMOKE PASS standard pack validates47assets', flush=True)
    built = output / 'scrantic_data.zip'
    packed = json.loads(execute('pack-build', [common[0], 'build', *common[1:], '--output', built]).stdout)
    actual = members(built)
    failures = member_errors(expected, actual)
    require(not failures, 'built archive: ' + '\n'.join(failures))
    additions = sorted(set(actual) - set(before))
    changed = sorted(n for n in before if actual.get(n) != before[n])
    require(len(actual) == 2598 and len(changed) == 10 and additions == [PREFIX + f'BMP/HOLIDAY.BMP/{f:03}.png' for f in range(4)], 'package: expected2598members,10changes,4additions')
    require(actual == composed, 'package: reviewed wave plus banner differs')
    # Named damage remains a valid ZIP, isolating the full member identity check.
    damaged_name = PREFIX + 'BMP/BACKGRND.BMP/007.png'
    wrong = output / 'negative-clean007.zip'
    with zipfile.ZipFile(built) as src, zipfile.ZipFile(wrong, 'x') as dst:
        for info in src.infolist():
            raw = src.read(info.filename)
            dst.writestr(copy.copy(info), raw + b'mutation' if info.filename == damaged_name else raw)
    audit_args = ['--repo', repo, '--inputs', args.inputs.resolve(), '--baseline', baseline]
    negative = execute('negative-member', [Path(__file__).resolve(), *audit_args, '--audit-archive', wrong], 1)
    require(negative.stdout.strip() == witness and negative.stderr.strip() == 'FAIL ' + damaged_name + ': member content differs', 'negative: expected exactly one witnessed007failure')
    text = Path(__file__).read_text(encoding='utf-8')
    needle = "        require(not failures, '\\n'.join(failures))"
    require(text.count(needle) == 1, 'mutation: unique audit guard')
    mutant = output / 'member-guard-removed.py'
    mutant.write_text(text.replace(needle, '        pass  # executed guard removal'), encoding='utf-8', newline='\n')
    removed = execute('removed-member-guard', [mutant, *audit_args, '--audit-archive', wrong])
    mutant_sha = sha(mutant.read_bytes())
    require('WITNESS shore-package ' + mutant_sha in removed.stdout and 'PASS independent member audit' in removed.stdout, 'mutation: actual changed helper execution witness')
    restored = execute('restored-member-audit', [Path(__file__).resolve(), *audit_args, '--audit-archive', built])
    require(witness in restored.stdout and 'PASS independent member audit' in restored.stdout, 'restored: current helper witness')
    verify_inputs(repo, inputs)
    report = {'schema_version': 1, 'status': 'PASS', 'helper_sha256': helper_sha, 'inputs_sha256': sha(args.inputs.read_bytes()),
        'python_version': platform.python_version(), 'pillow_version': PIL.__version__, 'archive_sha256': sha(built.read_bytes()),
        'baseline_commit': inputs['baseline_commit'], 'baseline_archive_sha256': inputs['baseline_archive_sha256'],
        'reviewed_wave_archive_sha256': inputs['reviewed_wave_archive_sha256'], 'inset_banner_sha256': banner['candidate_png_sha256'],
        'private_zip_read_this_run': args.wave_candidate is not None,
        'private_comparison_limit': None if args.wave_candidate else 'Used the frozen member map extracted from the approved ZIP during integration preparation; did not independently read that private ZIP this run.',
        'member_count': len(actual), 'cartoon_asset_count': 47, 'added_members': additions, 'changed_members': changed,
        'unchanged_existing_members': len(before) - len(changed), 'inherited_ledger_rows_unchanged': 33,
        'reviewed_wave_plus_banner_all_payloads_identical': True, 'source_replay_sha256': sha((output / 'source-replay.json').read_bytes()),
        'package_smoke': smoke, 'builder': packed, 'production_promoted': False,
        'negative_control': {'member': damaged_name, 'failure_count': 1, 'stderr': negative.stderr.strip(),
            'helper_sha256': helper_sha, 'mutant_sha256': mutant_sha, 'damaged_archive_sha256': sha(wrong.read_bytes()),
            'guard_removed_accepts_damaged_input': True, 'restored_positive_passed': True},
        'commands_in_execution_order': commands,
        'scope': 'Exact source replay and standard package build. Native final composition validation and authorized promotion are subsequent distinct steps.'}
    save(output / 'verification.json', report)
    print(json.dumps({'status': 'PASS', 'archive_sha256': report['archive_sha256'], 'members': 2598, 'assets': 47, 'production_promoted': False}), flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        raise SystemExit(1)
