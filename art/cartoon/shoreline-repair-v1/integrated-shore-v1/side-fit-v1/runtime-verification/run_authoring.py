"""Ordered authoring checks and fresh-process side declaration mutations."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'CMakeLists.txt').is_file())
OUT = ROOT / 'build/side-fit-v1/authoring'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    results = []
    smoke = [
        ['tests/test_art_tools.py', 'ArtToolsTests.test_named_island_footprints_preserve_original_catalog',
         'ArtToolsTests.test_registered_ground_build_preserves_hd', '-v'],
        ['tests/test_art_production_catalog.py', '--phase', 'smoke'],
        ['tests/test_art_pilot_history.py', '--phase', 'smoke'],
        ['tests/test_art_review_metadata.py', '--phase', 'smoke'],
    ]
    regression = [
        ['tests/test_art_tools.py', '-v'],
        ['tests/test_art_production_catalog.py', '--phase', 'regression'],
        ['tests/test_art_pilot_history.py', '--phase', 'regression'],
        ['tests/test_art_review_metadata.py', '--phase', 'regression'],
        ['tools/art_review_metadata.py', '--check'],
        ['tools/art_production_catalog.py', '--check'],
    ]
    for phase, commands in [('smoke', smoke), ('regression', regression)]:
        for index, args in enumerate(commands):
            result = subprocess.run([sys.executable, '-B', *args], cwd=ROOT, capture_output=True, text=True,
                                    timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            name = f'{phase}-{index}.log'
            (OUT / name).write_text(result.stdout + result.stderr, encoding='utf-8', newline='\n')
            results.append({'phase': phase, 'arguments': args, 'exit_code': result.returncode,
                            'log': name, 'sha256': sha(OUT / name)})
            (OUT / 'ordered-results.json').write_text(json.dumps(results, indent=2)+'\n')
            assert result.returncode == 0, name
            print('PASS '+phase+' '+args[0], flush=True)
    source = (ROOT / 'tools/art_common.py').read_text()
    definitions = [
        ('left-slot', 'for i in (3, 4, 5)', 'for i in (2, 3, 4, 5)'),
        ('right-slot', 'for i in (9, 10, 11)', 'for i in (9, 10, 11, 12)'),
        ('left-source', 'list(logical) == [72, 29]', 'list(logical) in ([72, 29], [73, 29])'),
        ('right-source', 'list(logical) == [72, 32]', 'list(logical) in ([72, 32], [72, 33])'),
    ]
    mutations = []
    case = 'test_side_footprint_rejects_wrong_slot_source_scale_and_family'
    for name, old, new in definitions:
        scratch = OUT / ('mutant-'+name)
        shutil.copytree(ROOT / 'tools', scratch / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
        (scratch / 'tests').mkdir()
        shutil.copyfile(ROOT / 'tests/test_art_tools.py', scratch / 'tests/test_art_tools.py')
        assert source.count(old) == 1, name
        module = scratch / 'tools/art_common.py'
        module.write_text(source.replace(old, new), encoding='utf-8', newline='\n')
        code = "import sys,hashlib,unittest;from pathlib import Path;sys.path[:0]=['tools','tests'];import art_common,test_art_tools;print('WITNESS '+hashlib.sha256(Path(art_common.__file__).read_bytes()).hexdigest(),flush=True);r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test_art_tools.ArtToolsTests('"+case+"')]));sys.exit(not r.wasSuccessful())"
        run = subprocess.run([sys.executable, '-B', '-c', code], cwd=scratch, capture_output=True, text=True,
                             timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        text = run.stdout + run.stderr
        (OUT / ('mutation-'+name+'.log')).write_text(text, encoding='utf-8', newline='\n')
        assert run.returncode == 1 and 'WITNESS '+sha(module) in text and 'Ran 1 test' in text and 'FAILED (failures=1)' in text and case in text, text
        mutations.append({'name': name, 'status': 'FIRED', 'source_sha256': sha(module), 'case': case,
                          'log': 'mutation-'+name+'.log', 'fresh_process': True})
        print('FIRED authoring '+name, flush=True)
    restored = subprocess.run([sys.executable, '-B', 'tests/test_art_tools.py', 'ArtToolsTests.'+case, '-v'],
                              cwd=ROOT, capture_output=True, text=True, timeout=30)
    (OUT / 'restored.log').write_text(restored.stdout+restored.stderr, encoding='utf-8', newline='\n')
    assert restored.returncode == 0
    report = {'status': 'PASS', 'ordered_checks': results, 'mutations': mutations, 'restored_control': 'PASS',
              'source_sha256': {p: sha(ROOT / p) for p in ('tools/art_common.py', 'tests/test_art_tools.py',
                                  'tests/test_art_production_catalog.py')},
              'scope': 'Synthetic ledger/recipe/PNG fixtures plus current catalog checks; no production archive writes.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
