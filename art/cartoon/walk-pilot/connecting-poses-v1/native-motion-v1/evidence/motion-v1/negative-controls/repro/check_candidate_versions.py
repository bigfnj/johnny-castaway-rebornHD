"""Fresh-process controls for the three explicit candidate-version entrypoints."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
OUT = ROOT / 'build/connecting-poses/native-motion-v1/negative-controls/candidate-version'
FILES = ('prepare_candidate.py', 'check_selection.py', 'capture_candidate.py')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def child(path, version):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('version_subject', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('WITNESS executed helper SHA256=' + sha(path.read_bytes()), flush=True)
    sys.argv = [str(path), '--candidate-version', str(version)]
    if path.name != 'capture_candidate.py':
        sys.argv += ['--selection', str(path.parent / 'absent-selection.json')]
    def test(self):
        caught = None
        try:
            module.main()
        except Exception as error:
            caught = error
        self.assertIs(type(caught), AssertionError, 'positive-version guard before reading any selection/capture input')
        self.assertEqual(str(caught), 'positive candidate version')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(type('CandidateVersion', (unittest.TestCase,),
        {'test_' + path.stem + '_positive_version': test}))
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--child', type=Path)
    parser.add_argument('--version', type=int)
    args = parser.parse_args()
    if args.child:
        return child(args.child, args.version)
    assert not OUT.exists(), 'preserve version controls'
    records = []
    before = sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    for filename in FILES:
        source = (HERE / filename).read_text(encoding='utf-8')
        condition = "assert args.candidate_version > 0, 'positive candidate version'"
        assert source.count(condition) == 1
        for variant, version in (('zero', 0), ('negative', -1), ('removed', 0)):
            folder = OUT / filename[:-3] / variant
            folder.mkdir(parents=True)
            for dependency in ('config.py', 'prepare_candidate.py', 'native_core.py', 'capture.py'):
                shutil.copyfile(HERE / dependency, folder / dependency)
            path = folder / filename
            code = source.replace(condition, "assert True, 'positive candidate version'") if variant == 'removed' else source
            path.write_text(code, encoding='utf-8', newline='\n')
            run = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--child', str(path), '--version', str(version)],
                                 capture_output=True, text=True, timeout=30)
            (folder / 'stdout.txt').write_text(run.stdout, encoding='utf-8', newline='\n')
            (folder / 'stderr.txt').write_text(run.stderr, encoding='utf-8', newline='\n')
            assert 'WITNESS executed helper SHA256=' + sha(path.read_bytes()) in run.stdout
            if variant == 'removed':
                assert run.returncode == 1 and 'FAILED (failures=1)' in run.stderr and 'ERROR:' not in run.stderr, run.stderr
                assert 'FAIL: test_' + filename[:-3] + '_positive_version' in run.stderr
            else:
                assert run.returncode == 0 and '\nOK\n' in run.stderr, run.stderr
            records.append({'helper': filename, 'variant': variant, 'version': version,
                'result': 'FIRED' if variant == 'removed' else 'PASS', 'executed_helper_sha256': sha(path.read_bytes()),
                'stdout_sha256': sha((folder / 'stdout.txt').read_bytes()), 'stderr_sha256': sha((folder / 'stderr.txt').read_bytes())})
    assert before == sha((ROOT / 'assets/scrantic_data.zip').read_bytes())
    record = {'status': 'PASS', 'negative_inputs_passed': 6, 'executed_guard_removals_fired': 3,
        'records': records, 'production_unchanged_sha256': before,
        'scope': 'Real copied helper main() executes before missing downstream input. Guard removal causes exactly one named unittest failure. No native launch or package output in these controls.'}
    (OUT / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(record, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
