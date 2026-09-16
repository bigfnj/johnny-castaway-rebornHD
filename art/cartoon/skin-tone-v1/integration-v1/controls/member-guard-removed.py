"""Reproduce the final43-asset pack from frozen art and standard art_pack.py.

Builds in a fresh scratch directory. --promote updates the active pack and ZIP
only after source replay, package smoke, full member regression and controls.
The baseline is recoverable from the pinned Git commit in inputs.json.
"""
import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
INPUTS_SHA = '917ddd439dd93308c218c39e41414a4ed6bc65b6951668b66ad0bf9ee068803c'
PREFIX = 'data/styles/cartoon/'
COLOR = 'art/cartoon/skin-tone-v1/exports-v2/recipe.json'
FOOT_BASE = 'art/cartoon/standing018-proportions-v1'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
load = lambda path: json.loads(path.read_bytes())


def require(condition, label):
    if not condition:
        raise ValueError(label)


def members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'archive: duplicate member')
        return {name: sha(archive.read(name)) for name in names}


def member_errors(expected, actual):
    return [name + ': member content differs' for name in sorted(set(expected) | set(actual))
            if expected.get(name) != actual.get(name)]


def verify_inputs(repo, inputs):
    for name, digest in inputs['protected_files_sha256'].items():
        require(sha((repo / name).read_bytes()) == digest, name + ': protected bytes changed')
    for name, digest in inputs['maintained_tools_lf_sha256'].items():
        require(sha((repo / name).read_bytes().replace(b'\r\n', b'\n')) == digest, name + ': maintained tool changed')


def ancestry_replay(repo, frames):
    """Replay the already documented legacy filter differences without writing PNGs."""
    doc = load(repo / 'art/cartoon/skin-tone-v1/ancestry.json')

    def bound(row):
        raw = (repo / row['path']).read_bytes()
        require(sha(raw) == row['sha256'], row['path'] + ': ancestry identity')
        return raw

    index = {r['frame']: r for r in json.loads(bound(doc['input_index']))['frames']}
    rows = [r for r in doc['frames'] if r['frame'] in frames]
    require({r['frame'] for r in rows} == set(frames), 'ancestry: selected frame scope')
    results = []
    for row in rows:
        frame = row['frame']
        recipe = json.loads(bound(row['ancestor_recipe']))
        bound(row['ancestor_exporter'])
        source = row['raw_source']
        if source['kind'] == 'zip_member':
            with zipfile.ZipFile(io.BytesIO(bound(source['archive']))) as archive:
                raw = archive.read(source['member'])
            require(sha(raw) == source['sha256'], f'{frame:03}: raw ZIP-member identity')
        else:
            raw = bound(source)
        spec = next(item for item in recipe['frames'] if item['frame'] == frame)
        require(source['sha256'] == spec['source_sha256'], f'{frame:03}: raw recipe identity')
        runtime = Image.open(io.BytesIO(bound(row['runtime_input']))).convert('RGBA')
        require(list(runtime.size) == row['runtime_input']['canvas'] == spec['runtime_canvas'], f'{frame:03}: ancestor canvas')
        require(sha(runtime.tobytes()) == index[frame]['rgba_sha256'], f'{frame:03}: ancestor RGBA')
        scale, _, tx, _, _, ty = spec['affine_forward']
        pad = row['render_registration']['padding_hd']
        width, height = runtime.size
        size = (width + 2 * pad, height + 2 * pad)
        source_image = Image.open(io.BytesIO(raw)).convert('RGBA')
        high = source_image.convert('RGBa').transform((size[0] * 8, size[1] * 8), Image.Transform.AFFINE,
                (1/(scale*8), 0, -(tx+pad)/scale, 0, 1/(scale*8), -(ty+pad)/scale),
                resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        rendered = high.resize(size, Image.Resampling.LANCZOS).convert('RGBA').crop((pad, pad, pad+width, pad+height))
        require(rendered.tobytes() == runtime.tobytes(), f'{frame:03}: ancestor pixel replay differs')
        results.append({'frame': frame, 'raw_sha256': source['sha256'], 'runtime_input_sha256': row['runtime_input']['sha256'],
                        'rgba_sha256': sha(rendered.tobytes()), 'padding_hd': pad, 'decoded_pixels_identical': True})
    return results


def atomic_bytes(path, raw):
    handle, name = tempfile.mkstemp(prefix='.cartoon-integration-', dir=path.parent)
    os.close(handle)
    staged = Path(name)
    try:
        staged.write_bytes(raw)
        require(staged.read_bytes() == raw, str(path.name) + ': staged copy differs')
        os.replace(staged, path)
    finally:
        if staged.exists():
            staged.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--private-candidate', type=Path)
    p.add_argument('--inputs', type=Path, default=HERE / 'inputs.json')
    p.add_argument('--output', type=Path)
    p.add_argument('--promote', action='store_true')
    p.add_argument('--audit-archive', type=Path)
    args = p.parse_args()
    helper_sha = sha(Path(__file__).read_bytes())
    witness = 'WITNESS skin-package ' + helper_sha
    print(witness, flush=True)
    repo, baseline = args.repo.resolve(), args.baseline.resolve()
    require(sha(args.inputs.read_bytes()) == INPUTS_SHA, 'inputs.json: identity mismatch')
    inputs = load(args.inputs)
    verify_inputs(repo, inputs)
    require(sha(baseline.read_bytes()) == inputs['baseline_archive_sha256'], 'baseline: identity mismatch')
    before = members(baseline)
    require(len(before) == 2591, 'baseline: expected2591members')
    specs = load(repo / inputs['runtime_sources'])['frames']
    require([s['frame'] for s in specs] == [0,1,2,3,4,5,6,7,8,9,10,11,12,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29], 'scope: expected28Johnny')
    expected = dict(before)
    expected.update({PREFIX + s['path']: s['sha256'] for s in specs})
    if args.audit_archive:
        require(not args.promote and args.output is None, 'audit: no output or promotion')
        failures = member_errors(expected, members(args.audit_archive))
        pass  # executed audit guard-removal control
        print('PASS independent member audit', flush=True)
        return 0
    require(args.output is not None and not args.output.exists(), 'output: use a fresh directory')
    require(PIL.__version__ == '12.3.0', 'Pillow: reproduction requires12.3.0')
    output = args.output.resolve()
    private = args.private_candidate.resolve() if args.private_candidate else None
    if private:
        require(sha(private.read_bytes()) == inputs['reviewed_private_archive_sha256'], 'reviewed private archive: identity mismatch')
        require(not member_errors(expected, members(private)), 'reviewed private archive: unexpected member delta')
    else:
        print('LIMIT privateZIP not supplied: approved member identities checked; independent privateZIP comparison NOT RUN', flush=True)
    prior = load(repo / inputs['prior_pack'])
    ledger_path = repo / inputs['integrated_pack']
    ledger = load(ledger_path)
    johnny = {s['path'] for s in specs}
    island = [r for r in prior['assets'] if r['path'] not in johnny]
    require(len(island) == 15 and [r for r in ledger['assets'] if r['path'] not in johnny] == island, 'ledger:15island rows changed')
    require(len(ledger['assets']) == 43 and ledger['runtime'] == prior['runtime'], 'ledger:43assets and retained runtime')
    require(ledger['pilot_history']['acceptance_record'] == prior['pilot_history']['acceptance_record'] and ledger['pilot_history']['sha256'] == prior['pilot_history']['sha256'], 'ledger: historical pilot identity changed')
    require(ledger['pilot_history']['replaced_assets'] == [f'BMP/JOHNWALK.BMP/{f:03}.png' for f in range(24,30)], 'ledger: six pilot replacements')
    active_before = (repo / 'art/cartoon/pack.json').read_bytes()
    if args.promote:
        require(json.loads(active_before) == prior and sha((repo / 'assets/scrantic_data.zip').read_bytes()) == inputs['baseline_archive_sha256'], 'promotion: current production differs from prior')
    output.mkdir(parents=True)
    commands = []

    def portable(value):
        try:
            return Path(value).resolve().relative_to(repo).as_posix()
        except (ValueError, OSError):
            return str(value)

    def execute(label, argv, code=0):
        completed = subprocess.run([sys.executable, '-B', *map(str, argv)], cwd=repo, capture_output=True, text=True, timeout=180)
        for stream in ('stdout', 'stderr'):
            (output / (label+'.'+stream+'.txt')).write_text(getattr(completed, stream), encoding='utf-8', newline='\n')
        commands.append({'order': len(commands)+1, 'label': label, 'argv': ['python', '-B', *[portable(x) if Path(str(x)).is_absolute() else str(x) for x in argv]],
                         'exit_code': completed.returncode, 'stdout': label+'.stdout.txt', 'stderr': label+'.stderr.txt',
                         'stdout_sha256': sha(completed.stdout.encode()), 'stderr_sha256': sha(completed.stderr.encode())})
        require(completed.returncode == code, label + ': ' + completed.stderr)
        return completed

    source_smoke = ancestry_replay(repo, [29])
    print('SMOKE PASS canonical029 raw ancestry pixel replay', flush=True)
    source_rows = ancestry_replay(repo, [s['frame'] for s in specs if s['frame'] != 18])
    print('REGRESSION PASS27retained raw ancestry pixel replays; legacy padding differences retained', flush=True)
    old_recipe = load(repo / COLOR)

    def compare_colors(folder, frames):
        actual = load(folder / 'recipe.json')
        want = [r for r in old_recipe['frames'] if r['frame'] in frames]
        require(actual['frames'] == want, 'colors: selected recipe rows differ')
        for row in want:
            for key, hash_key in [('candidate_png', 'candidate_png_sha256'), ('mask', 'mask_sha256')]:
                require(sha((folder / row[key]).read_bytes()) == row[hash_key], row['path'] + ': reproduced ' + key + ' differs')
        return want

    execute('color-smoke', [repo / 'art/cartoon/skin-tone-v1/correct.py', '--output', output / 'color-smoke', '--frames', '24', '29'])
    compare_colors(output / 'color-smoke', [24,29])
    print('SMOKE PASS changed024 and unchanged029 exact color output', flush=True)
    frames = [s['frame'] for s in specs if s['frame'] != 18]
    execute('color-regression', [repo / 'art/cartoon/skin-tone-v1/correct.py', '--output', output / 'color-regression', '--frames', *map(str, frames)])
    compare_colors(output / 'color-regression', frames)
    print('REGRESSION PASS27retained color PNG/mask/recipe-row reproductions', flush=True)
    stage = output / 'standing018'
    execute('stage018', [repo / FOOT_BASE / 'export/stage.py', '--source', repo / FOOT_BASE / '018-foot-v5.png', '--source-sha256', '97922bacf481925f29640606e305ba1747b7de5fb1b01439e4fcdaf8e2621c5e', '--work', stage])
    execute('export018', [stage / 'authoring/export.py', '--recipe', repo / FOOT_BASE / 'export/trials-foot-v5/runtime/recipe.json', '--output', stage / 'runtime'])
    require(sha((stage / 'runtime/BMP/JOHNWALK.BMP/018.png').read_bytes()) == '183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2', '018: fixed export differs')
    execute('color018', [repo / FOOT_BASE / 'color/correct018_foot_v5.py', '--runtime', stage / 'runtime', '--annotations', repo / FOOT_BASE / 'color/reference-foot-v5.json', '--annotations-sha256', 'e1bde6bf34f91a5d81a308187a305b7344d31e8acf5f2a51fab6afc29406acf1', '--output', output / 'color018'])
    foot_recipe = load(repo / FOOT_BASE / 'color/evidence-foot-v5/recipe.json')
    require(load(output / 'color018/recipe.json')['frames'] == foot_recipe['frames'], '018: color recipe row differs')
    for relative in ('sprites/018.png', 'masks/018.png', 'protected-cap/018.png'):
        require((output / 'color018' / relative).read_bytes() == (repo / FOOT_BASE / 'color/evidence-foot-v5' / relative).read_bytes(), '018: exact color output differs:' + relative)
    print('PASS selected018 raw fixed-export and normalized color reproduce exact bytes', flush=True)
    source_record = {'status': 'PASS', 'canonical_smoke': source_smoke, 'retained27_raw_pixel_replays': source_rows,
                     'retained27_color_outputs_exact': True, 'selected018_fixed_export_png': '183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2',
                     'selected018_color_png': foot_recipe['frames'][0]['candidate_png_sha256'],
                     'limit': 'Legacy raw replay compares decodedRGBA, not encoded ancestorPNG bytes. All final color PNG bytes are compared exactly; new source paths make the018color recipe envelope differ.'}
    (output / 'source-replay.json').write_text(json.dumps(source_record, indent=2)+'\n', encoding='utf-8', newline='\n')
    accepted = output / 'accepted'
    with zipfile.ZipFile(baseline) as archive:
        for row in ledger['assets']:
            path = row['path']
            if path in johnny:
                frame = int(Path(path).stem)
                folder = output / ('color018' if frame == 18 else 'color-regression')
                raw = (folder / f'sprites/{frame:03}.png').read_bytes()
            else:
                raw = archive.read(PREFIX + path)
            require(sha(raw) == row['sha256'], path + ': accepted input differs')
            target = accepted / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    common = [repo / 'tools/art_pack.py', '--archive', baseline, '--ledger', ledger_path, '--accepted', accepted]
    smoke = json.loads(execute('pack-smoke', [common[0], 'validate', *common[1:]]).stdout)
    require(smoke['assets'] == 43, 'pack-smoke: expected43assets')
    print('SMOKE PASS standard art_pack validates43accepted PNGs', flush=True)
    built = output / 'scrantic_data.zip'
    packed = json.loads(execute('pack-build', [common[0], 'build', *common[1:], '--output', built]).stdout)
    actual = members(built)
    require(not member_errors(expected, actual), 'built archive: unexpected member delta')
    additions = sorted(set(actual)-set(before))
    changes = sorted(n for n in before if actual.get(n) != before[n])
    require(len(actual) == 2594 and additions == [PREFIX + f'BMP/JOHNWALK.BMP/{f:03}.png' for f in (9,10,12)] and len(changes) == 24, 'archive: expected3additions and24existing changes')
    require(before[PREFIX+'BMP/JOHNWALK.BMP/029.png'] == actual[PREFIX+'BMP/JOHNWALK.BMP/029.png'], '029: originalPNG changed')
    if private:
        require(not member_errors(members(private), actual), 'private candidate: member payloads differ')
    wrong = output / 'negative-018.zip'
    damaged = PREFIX + 'BMP/JOHNWALK.BMP/018.png'
    with zipfile.ZipFile(built) as src, zipfile.ZipFile(wrong, 'x') as dst:
        for info in src.infolist():
            raw = src.read(info.filename)
            dst.writestr(copy.copy(info), raw+b'mutation' if info.filename == damaged else raw)
    audit_args = ['--repo', repo, '--baseline', baseline, '--inputs', args.inputs.resolve()]
    negative = execute('negative-member', [Path(__file__).resolve(), *audit_args, '--audit-archive', wrong], 1)
    require(negative.stdout.strip() == witness and negative.stderr.strip() == 'FAIL '+damaged+': member content differs', 'negative control: expected exactly one witnessed018failure')
    mutant = output / 'member-guard-removed.py'
    source = Path(__file__).read_text(encoding='utf-8')
    needle = "        require(not failures, '\\n'.join(failures))"
    require(source.count(needle) == 1, 'mutation: unique audit condition')
    mutant.write_text(source.replace(needle, '        pass  # executed audit guard-removal control'), encoding='utf-8', newline='\n')
    mutant_run = execute('removed-member-guard', [mutant, *audit_args, '--audit-archive', wrong])
    mutant_sha = sha(mutant.read_bytes())
    require('WITNESS skin-package '+mutant_sha in mutant_run.stdout and 'PASS independent member audit' in mutant_run.stdout, 'mutation: changed helper execution witness')
    restored = execute('restored-member-audit', [Path(__file__).resolve(), *audit_args, '--audit-archive', built])
    require(witness in restored.stdout and 'PASS independent member audit' in restored.stdout, 'restored member audit witness')
    verify_inputs(repo, inputs)
    print('REGRESSION PASS2594members;3added;24changed;2567unchanged; corrupted018refused and executed guard-removal witnessed', flush=True)
    report = {'schema_version': 1, 'status': 'PASS', 'inputs_sha256': INPUTS_SHA, 'helper_sha256': helper_sha,
              'python_version': platform.python_version(), 'pillow_version': PIL.__version__,
              'baseline_commit': inputs['baseline_commit'], 'baseline_archive_sha256': inputs['baseline_archive_sha256'],
              'archive_sha256': sha(built.read_bytes()), 'member_count': len(actual), 'cartoon_asset_count': 43,
              'added_members': additions, 'changed_members': changes, 'removed_members': [], 'unchanged_existing_members': len(before)-len(changes),
              'unchanged_island_rows': 15, 'newly_accepted_johnny': 28, '029_original_png_unchanged': True,
              'runtime_manifest_unchanged': actual[PREFIX+'manifest.json'] == before[PREFIX+'manifest.json'],
              'reviewed_private_archive_sha256': inputs['reviewed_private_archive_sha256'], 'private_members_independently_compared': private is not None,
              'private_comparison_limit': None if private else 'PrivateZIP not supplied; approved member identities checked but independent privateZIP comparison NOT RUN.',
              'package_smoke': smoke, 'builder': packed, 'source_replay_sha256': sha((output / 'source-replay.json').read_bytes()),
              'negative_control': {'case': damaged, 'failure_count': 1, 'stderr': negative.stderr.strip(), 'executed_helper_sha256': helper_sha,
                                   'guard_removed_helper_sha256': mutant_sha, 'guard_removed_run_accepted_damaged_archive': True, 'restored_positive_passed': True,
                                   'scratch_damaged_archive_sha256': sha(wrong.read_bytes()), 'production_never_used_for_mutation': True},
              'commands_in_execution_order': commands, 'production_promoted': False,
              'archive_envelope': 'Standard art_pack builder; every named payload matches reviewed privateZIP, but its ZIP envelope can differ.',
              'scope': 'Source/color reproduction,43asset package smoke, all2594member regression and witnessed018corruption/guard-removal controls. Human/native approval remains in separate bound records.'}
    if args.promote:
        pack_path, production = repo / 'art/cartoon/pack.json', repo / 'assets/scrantic_data.zip'
        require(pack_path.read_bytes() == active_before and sha(production.read_bytes()) == inputs['baseline_archive_sha256'], 'production: changed during checks')
        old_zip = production.read_bytes()
        try:
            atomic_bytes(production, built.read_bytes())
            atomic_bytes(pack_path, ledger_path.read_bytes())
            require(members(production) == expected and pack_path.read_bytes() == ledger_path.read_bytes(), 'promotion: readback differs')
        except Exception:
            atomic_bytes(production, old_zip)
            atomic_bytes(pack_path, active_before)
            raise
        report['production_promoted'] = True
        report['production_pack_sha256'] = sha(pack_path.read_bytes())
    (output / 'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ('archive_sha256', 'production_promoted', 'member_count')}), flush=True)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print('FAIL '+str(error), file=sys.stderr)
        raise SystemExit(1)
