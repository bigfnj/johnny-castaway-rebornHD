"""Focused technical smoke, fresh replay and phase-assignment refusal witness."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    spec = importlib.util.spec_from_file_location('comparison_verify_target', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=('offshore', 'wash'), required=True)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    offshore = args.variant == 'offshore'
    folder = HERE if offshore else HERE.parent / 'wash-over-sand-v1'
    exporter = folder / ('export_v2.py' if offshore else 'export.py')
    recipe_path = folder / ('recipe-v2.json' if offshore else 'recipe-v1.json')
    runtime = folder / ('candidates/v2' if offshore else 'candidates/v1')
    suffix = '-v2' if offshore else ''
    report_path = folder / f'verification-{args.phase}{suffix}.json'
    require(not report_path.exists(), 'verification: refusing overwrite')
    recipe = json.loads(recipe_path.read_bytes())
    report = json.loads((runtime / 'export-report.json').read_bytes())
    result = {'schema_version': 1, 'status': 'RUNNING', 'phase': args.phase, 'variant': args.variant,
              'test_sha256': sha(Path(__file__)), 'exporter_sha256': sha(exporter),
              'recipe_sha256': sha(recipe_path), 'report_sha256': sha(runtime / 'export-report.json'),
              'scope': 'Focused authoring evidence, not native animation or human approval.', 'checks': [], 'commands': []}

    def check(condition, label):
        require(condition, label)
        result['checks'].append(label)

    def run(command, expected, label):
        proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        record = {'label': label, 'arguments': [str(x).replace(str(ROOT), '<repo>').replace(str(work), '<scratch>') for x in command[1:]],
                  'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
        result['commands'].append(record)
        require(proc.returncode == expected, label + ': unexpected exit')
        return proc

    check(report['exporter_sha256'] == sha(exporter) and report['recipe_sha256'] == sha(recipe_path), 'Exact exporter and recipe identities')
    check(recipe['accepted'] is False and report['accepted'] is False, 'Comparison-only status retained')
    check([r['frame'] for r in report['frames']] == [0,3,4,5,6,7,8,9,10,11], 'Ten ordered runtime slots')
    for name, digest in report['outputs_sha256'].items():
        require(sha(runtime / name) == digest, name + ': output identity')
    check(True, 'Every report-bound output byte hash')
    for row in report['frames']:
        path = runtime / row['path']
        image = Image.open(path).convert('RGBA')
        require(list(image.size) == row['canvas'] and sha(path) == row['sha256'], f"{row['frame']:03}: runtime row identity")
        if row['frame'] not in (6,7,8):
            require(path.read_bytes() == (HERE.parent / 'candidates/v1' / row['path']).read_bytes(), f"{row['frame']:03}: retained parent bytes")
            continue
        require(row['footprint'] == {'id':'cartoon-island-center-foam-v1','canvas':[384,256],'offset_hd':[-32,-90]}, f"{row['frame']:03}: common footprint")
        require(row['cropped_filtered_alpha']['nonzero_pixels'] == 0, f"{row['frame']:03}: filtered alpha crop")
        padded = Image.open(runtime / f"audit/{row['frame']:03}-padded.png").convert('RGBA')
        direct = padded.crop((36,36,420,292) if offshore else (32,32,416,288))
        if offshore:
            require(direct.tobytes() == Image.open(runtime / f"audit/{row['frame']:03}-unmasked.png").convert('RGBA').tobytes(), 'Offshore exact world-aligned crop')
        else:
            require(direct.tobytes() == image.tobytes(), f"{row['frame']:03}: no-mask direct RGBA crop")
    check(True, 'Seven parent PNGs byte-identical; three full-source canvases retain all filtered alpha')
    check(True, 'Unmasked input crop is world-aligned' if offshore else 'All three runtime RGBA arrays equal direct resample crops without any ground masking')
    if args.phase == 'regression':
        smoke = folder / f'verification-smoke{suffix}.json'
        smoke_record = json.loads(smoke.read_bytes())
        check(smoke_record['status'] == 'PASS' and smoke_record['exporter_sha256'] == sha(exporter), 'Smoke passed first on the same exporter')
        result['smoke_sha256'] = sha(smoke)
        scratch_root = ROOT / 'build/shoreline-repair-v1/technical-replays'
        scratch_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=args.variant + '-', dir=scratch_root) as tmp:
            work = Path(tmp)
            replay = work / 'replay'
            proc = run([sys.executable, '-B', str(exporter), '--recipe', str(recipe_path), '--output', str(replay)], 0, 'Fresh-process exact replay')
            check(sha(exporter) in proc.stdout, 'Fresh exporter digest witness emitted')
            expected = sorted(p.relative_to(runtime).as_posix() for p in runtime.rglob('*') if p.is_file())
            actual = sorted(p.relative_to(replay).as_posix() for p in replay.rglob('*') if p.is_file())
            check(expected == actual and all((runtime / p).read_bytes() == (replay / p).read_bytes() for p in expected), f'Fresh replay matches every one of {len(expected)} files')
            bad = json.loads(recipe_path.read_bytes())
            if offshore:
                bad['footprint']['canvas'] = [356,102]
                failure = 'recipe: full-source common footprint contract differs'
            else:
                low = next(r for r in bad['frames'] if r['frame'] == 6)
                middle = next(r for r in bad['frames'] if r['frame'] == 7)
                low['source'], low['source_sha256'] = middle['source'], middle['source_sha256']
                failure = 'recipe: source/phase/registration contract differs'
            bad_path = work / 'wrong-recipe.json'
            bad_path.write_text(json.dumps(bad, indent=2)+'\n', encoding='utf-8')
            proc = run([sys.executable, '-B', str(exporter), '--recipe', str(bad_path), '--output', str(work / 'refused')], 1, 'Wrong footprint refusal' if offshore else 'Valid other-phase raw substitution refusal')
            check(proc.stderr.strip() == 'FAIL '+failure and not (work / 'refused').exists(), 'Named contract refusal before outputs')
            if not offshore:
                source = exporter.read_text(encoding='utf-8')
                guard = "    base.require(recipe == prepared(), 'recipe: source/phase/registration contract differs')"
                require(source.count(guard) == 1, 'mutation: exact guard uniqueness')
                mutant = work / 'mutant.py'
                mutant.write_text(source.replace(guard, '    pass  # Executed phase-binding guard removal control'), encoding='utf-8')
                launcher = work / 'launch.py'
                launcher.write_text("import importlib.util,sys\nfrom pathlib import Path\np=Path(sys.argv.pop(1)); original=Path(sys.argv.pop(1))\ns=importlib.util.spec_from_file_location('mutant',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\nm.HERE=original.parent; m.ROOT=m.HERE.parents[4]; m.PARENT=m.HERE.parent/'export.py'; m.OLD=m.HERE.parent/'candidates/v1'\nraise SystemExit(m.main())\n", encoding='utf-8')
                altered = work / 'mutant-output'
                proc = run([sys.executable, '-B', str(launcher), str(mutant), str(exporter), '--recipe', str(bad_path), '--output', str(altered)], 0, 'Guard-removed copied exporter executes corrupted phase assignment')
                target = 'BMP/BACKGRND.BMP/006.png'
                check(sha(mutant) in proc.stdout and (altered / target).read_bytes() != (runtime / target).read_bytes(), 'Actual mutant digest witnessed and wrong006 pixels accepted')
                result['mutation'] = {'guard_removed': guard, 'mutant_sha256': sha(mutant), 'launcher_sha256': sha(launcher),
                                      'corrupt_recipe_sha256': sha(bad_path), 'accepted_wrong006_sha256': sha(altered / target),
                                      'correct006_sha256': sha(runtime / target), 'result': 'FIRED: original refused; guard-removed fresh process accepted different006 pixels'}
                proc = run([sys.executable, '-B', str(exporter), '--check'], 0, 'Restored unchanged positive exporter')
                check(sha(exporter) in proc.stdout, 'Original exporter restored positive after isolated mutation')
    result['status'] = 'PASS'
    report_path.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status':'PASS','phase':args.phase,'variant':args.variant,'checks':len(result['checks']),'report':report_path.relative_to(ROOT).as_posix(),'sha256':sha(report_path)}))


if __name__ == '__main__':
    main()
