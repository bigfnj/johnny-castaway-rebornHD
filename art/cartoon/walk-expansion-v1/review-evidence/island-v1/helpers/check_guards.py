"""Bounded executed-source probes for the private archive and pixel comparator."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def run(script, exports, output):
    result = subprocess.run([sys.executable, '-B', str(script), '--exports', str(exports), '--output', str(output)],
                            capture_output=True, text=True)
    assert 'WITNESS prepare_candidate.py SHA256=' + sha(script.read_bytes()) in result.stdout
    return result


def main():
    folder = HERE / 'guard-probes-v1'
    folder.mkdir()
    source = HERE / 'prepare_candidate.py'
    text = source.read_text(encoding='utf-8')
    exports = REPO / 'build/cartoon-production-reference/runtime-candidate-v1'
    results = []
    cases = [
        ('candidate-source:011', 'source-hash',
         "require(sha(source.read_bytes()) == recipe_row['source_sha256'] == row['source_sha256'], f'candidate-source:{frame:03}')",
         "require(True, f'candidate-source:{frame:03}')"),
        ('candidate-runtime-crop:011', 'same-canvas-wrong-pose',
         "require(crop.convert('RGBA').tobytes() == runtime.convert('RGBA').tobytes(), f'candidate-runtime-crop:{frame:03}')",
         "require(True, f'candidate-runtime-crop:{frame:03}')"),
        ('runtime-export-required', 'preview-flag',
         "require(report['preview_only'] is False and report['runtime_sprites_written'] is True\n            and report['runtime_fit_all_source_centers'] is True, 'runtime-export-required')",
         "require(True, 'runtime-export-required')")]
    for number, (label, change, old, new) in enumerate(cases):
        assert text.count(old) == 1, label
        bad = folder / f'bad-{number}'
        shutil.copytree(exports, bad)
        if change == 'same-canvas-wrong-pose':
            shutil.copyfile(bad / 'BMP/JOHNWALK.BMP/023.png', bad / 'BMP/JOHNWALK.BMP/011.png')
        else:
            data = json.loads((bad / 'export-report.json').read_bytes())
            if change == 'source-hash':
                data['frames'][0]['source_sha256'] = '0' * 64
            else:
                data['preview_only'] = True
            (bad / 'export-report.json').write_text(json.dumps(data), encoding='utf-8')
        refused = folder / f'refused-{number}'
        result = run(source, bad, refused)
        assert result.returncode != 0 and result.stderr.strip().endswith('ValueError: ' + label)
        assert not refused.exists()
        mutant = HERE / f'prepare_guard_mutant_{number}.py'
        mutant.write_text(text.replace(old, new), encoding='utf-8', newline='\n')
        output = folder / f'mutant-{number}'
        result = run(mutant, bad, output)
        assert result.returncode == 0 and (output / 'scrantic_data.zip').is_file(), label + ': mutant survived'
        results.append({'label': 'prepare_candidate.py:' + label, 'result': 'FIRED', 'failure_count': 1,
                        'mutant_source_sha256': sha(mutant.read_bytes()),
                        'witness': 'Fresh python -B printed exact executed mutant source hash; original refused before output; disabled guard admitted its targeted bad input.'})

    comparator_source = HERE / 'run_candidate.py'
    comparator_text = comparator_source.read_text(encoding='utf-8')
    start = comparator_text.index('def outside_equal(')
    end = comparator_text.index('\n\ndef capture(', start)
    changed = comparator_text[:start] + 'def outside_equal(left, right, box):\n    return True\n' + comparator_text[end:]
    mutant = HERE / 'capture_outside_guard_mutant.py'
    mutant.write_text(changed, encoding='utf-8', newline='\n')
    probe = HERE / 'outside_pixel_probe.py'
    probe.write_text('''import importlib.util,hashlib,json,sys
from pathlib import Path
from run_baseline import ppm
path=Path(sys.argv[1]);print('WITNESS comparator SHA256='+hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
spec=importlib.util.spec_from_file_location('subject',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
root=Path(__file__).resolve().parent
left=ppm(root/'baseline-v2/full/display-001.ppm');right=ppm(root/'candidate-v1/full/display-001.ppm')
row=json.loads((root/'candidate-v1/full/report.json').read_bytes())['displays'][0];box=row['changed_region_allowed']
assert left!=right and module.outside_equal(left,right,box),'positive-inside-only-difference'
assert module.outside_equal(left,left,box),'positive-identical-input'
bad=bytearray(right);bad[0]^=1
if module.outside_equal(left,bytes(bad),box):
 print('FAIL run_candidate.py:outside-pixel-difference',file=sys.stderr);raise SystemExit(1)
print('PASS inside-only,identical,and-outside-difference controls')
''', encoding='utf-8', newline='\n')
    for path, failure in ((comparator_source, False), (mutant, True)):
        result = subprocess.run([sys.executable, '-B', str(probe), str(path)], capture_output=True, text=True)
        assert 'WITNESS comparator SHA256=' + sha(path.read_bytes()) in result.stdout
        if failure:
            assert result.returncode == 1 and result.stderr.strip() == 'FAIL run_candidate.py:outside-pixel-difference'
        else:
            assert result.returncode == 0, result.stderr
    results.append({'label': 'run_candidate.py:outside-pixel-difference', 'result': 'FIRED', 'failure_count': 1,
                    'mutant_source_sha256': sha(mutant.read_bytes()),
                    'witness': 'Fresh Python source-hash witness; actual native pair plus one outside RGB-byte mutation, with identical/inside-only positive controls.'})
    evidence = {'scope': 'Four bounded helper guard mutations, not exhaustive malformed-input coverage. Production inputs and real candidate captures untouched.',
                'test_sha256': sha(Path(__file__).read_bytes()), 'mutations': results}
    (folder / 'verification.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS four executed-source guard mutations; each one named failure', flush=True)


if __name__ == '__main__':
    main()
