"""Focused integrity checks; meaningful shoreline clipping remains diagnostic."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parents[2]
HELPER = BUNDLE / 'export.py'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
helper = HELPER.read_bytes()
recipe_raw = (HERE / 'recipe.json').read_bytes()
runs = []


def run(label, options, failure=None, script=HELPER, mutant=None):
    result = subprocess.run([sys.executable, '-B', str(script), *map(str, options)],
                            capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert result.returncode == (1 if failure else 0), (label, result.stdout, result.stderr)
    assert 'WITNESS shore-export ' + sha(helper) in result.stdout
    assert result.stderr.strip() == ('FAIL ' + failure if failure else ''), (label, result.stderr)
    assert failure or 'DIAGNOSTIC ' in result.stdout
    assert not mutant or 'EXECUTED_MUTANT_SHA256=' + mutant in result.stdout
    runs.append({'name': label, 'result': 'FIRED' if failure else 'PASS',
                 'stdout': result.stdout, 'stderr': result.stderr})


run('007_smoke_readback', ['--recipe', HERE/'recipe.json', '--output', HERE, '--check'])
with tempfile.TemporaryDirectory(prefix='check-', dir=HERE) as temporary:
    work = Path(temporary).resolve()
    assert work.is_relative_to(HERE.resolve())
    run('007_fresh_replay', ['--recipe', HERE/'recipe.json', '--output', work/'replay'])
    report = json.loads((HERE / 'export-report.json').read_bytes())
    for name in [*report['outputs_sha256'], 'export-report.json']:
        assert (HERE / name).read_bytes() == (work / 'replay' / name).read_bytes()
    bad = json.loads(recipe_raw)
    bad['runtime_canvas'][1] += 1
    changed_recipe = work / 'wrong-canvas.json'
    changed_recipe.write_text(json.dumps(bad), encoding='utf-8')
    run('007_canvas_change_rejected', ['--recipe', changed_recipe, '--output', work/'bad'],
        '007: recipe/source/original registration differs')
    statement = "    base.require(recipe == prepare(frame, HERE / recipe['source']), f'{frame:03}: recipe/source/original registration differs')"
    text = helper.decode('utf-8')
    assert text.count(statement) == 1
    mutant = text.replace(statement, '    pass  # executed control: fixed recipe guard removed', 1).encode('utf-8')
    (work/'mutant.py').write_bytes(mutant)
    driver = work/'execute.py'
    driver.write_text('from pathlib import Path\nimport hashlib\nraw=Path(' + repr(str(work/'mutant.py')) + ').read_bytes()\n'
                      + "print('EXECUTED_MUTANT_SHA256='+hashlib.sha256(raw).hexdigest())\n"
                      + 'exec(compile(raw,' + repr(str(HELPER)) + ',"exec"),{"__name__":"__main__","__file__":' + repr(str(HELPER)) + '})\n', encoding='utf-8')
    run('007_canvas_change_accepted_only_without_guard', ['--recipe', changed_recipe, '--output', work/'mutated'], script=driver, mutant=sha(mutant))
    wrong = json.loads((work/'mutated/export-report.json').read_bytes())
    assert wrong['runtime_canvas'] == [320,51]
    assert wrong['outputs_sha256']['BMP/BACKGRND.BMP/007.png'] != report['outputs_sha256']['BMP/BACKGRND.BMP/007.png']
run('007_restored_positive', ['--recipe', HERE/'recipe.json', '--output', HERE, '--check'])
assert HELPER.read_bytes() == helper and (HERE/'recipe.json').read_bytes() == recipe_raw
evidence = {'status': 'PASS', 'scope': 'Recipe/export integrity only.377 filtered alpha>=8 pixels are cropped; no visual acceptance or clipping waiver.',
            'exporter_sha256': sha(helper), 'test_sha256': sha(Path(__file__).read_bytes()),
            'recipe_sha256': sha(recipe_raw), 'guard_removal_sha256': sha(mutant),
            'actual_wrong_canvas_written': [320,51], 'runs': runs}
(HERE/'verification.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8', newline='\n')
print('PASS007 smoke/replay and executed wrong-canvas guard control; diagnostic clipping remains')
