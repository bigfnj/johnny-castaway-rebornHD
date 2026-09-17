"""Record the existing maintained authoring commands, in their required order."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--phase', choices=('smoke', 'generate', 'regression'), required=True)
    args = parser.parse_args()
    root, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '.json')
    if report_path.exists():
        raise SystemExit('Use a fresh report path')
    protected = ['assets/scrantic_data.zip', 'art/cartoon/pack.json',
        'art/cartoon/low-tide-v1/integration-v1/runtime-recipe.json',
        'art/cartoon/low-tide-v1/integration-v1/production-acceptance.json']
    protected += [p.relative_to(root).as_posix() for p in (root/'tools').glob('art_*.py')]
    protected += [p.relative_to(root).as_posix() for p in (root/'tests').glob('test_art_*.py')]
    pins = {p: digest(root/p) for p in protected}
    if args.phase == 'smoke':
        commands = [('pack-smoke', ['tests/test_art_tools.py',
            'ArtToolsTests.test_named_island_footprints_preserve_original_catalog',
            'ArtToolsTests.test_true_alpha_preserves_opaque_magenta_and_binary_control',
            'ArtToolsTests.test_inventory_exports_unmodified_and_records_exact_aliases', '-v']),
            ('inventory-smoke', ['tests/test_art_inventory.py', '--smoke'])]
        commands += [(name+'-smoke', ['tests/'+name+'.py', '--phase', 'smoke'])
            for name in ('test_art_pilot_history', 'test_art_review_metadata', 'test_art_production_catalog')]
    else:
        smoke = json.loads((out/'smoke.json').read_bytes())
        if smoke['status'] != 'PASS' or smoke['protected_inputs'] != pins:
            raise SystemExit('Smoke must pass on the same protected inputs first')
        if args.phase == 'generate':
            commands = [(name+'-generate', ['tools/'+name+'.py'])
                for name in ('art_review_metadata', 'art_production_catalog')]
            commands += [('character-inventory-generate',
                ['art/cartoon/character-inventory-v1/build_inventory.py'])]
        else:
            commands = [('pack-regression', ['tests/test_art_tools.py', '-v']),
                ('inventory-regression', ['tests/test_art_inventory.py'])]
            commands += [(name+'-regression', ['tests/'+name+'.py', '--phase', 'regression'])
                for name in ('test_art_pilot_history', 'test_art_review_metadata', 'test_art_production_catalog')]
            commands += [(name+'-check', ['tools/'+name+'.py', '--check'])
                for name in ('art_review_metadata', 'art_production_catalog')]
            commands += [('character-inventory-check',
                ['art/cartoon/character-inventory-v1/build_inventory.py', '--check'])]
    records = []
    for label, argv in commands:
        process = subprocess.run([sys.executable, '-B', *argv], cwd=root,
            capture_output=True, text=True)
        text = process.stdout + process.stderr
        log = out/(label+'.log')
        log.write_bytes(text.encode('utf-8'))
        counts = re.findall(r'Ran (\d+) tests?', text)
        skips = re.findall(r"(?m)^.*(?:skipped |SKIP).*$", text)
        records.append({'label': label, 'argv': ['TOOLBOX_PYTHON', '-B', *argv],
            'exit_code': process.returncode, 'log': log.name, 'sha256': digest(log),
            'tests': int(counts[-1]) if counts else None, 'skip_lines': skips})
        print(label, process.returncode, text[-500:], flush=True)
        if process.returncode:
            break
    unchanged = pins == {p: digest(root/p) for p in protected}
    passed = len(records) == len(commands) and all(r['exit_code'] == 0 for r in records) and unchanged
    report = {'status': 'PASS' if passed else 'FAIL', 'phase': args.phase,
        'command_recorder_sha256': digest(Path(__file__)), 'protected_inputs': pins,
        'protected_inputs_unchanged': unchanged, 'commands': records,
        'scope': 'Existing maintained commands only; this recorder adds no art or runtime validation rules.'}
    report_path.write_bytes((json.dumps(report, indent=2)+'\n').encode())
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
