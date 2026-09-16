"""Focused placement/control tests; no native launch or corrected-art mutation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from PIL import Image
import skin_compare

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'skin_compare.py'
MUTATIONS = {
    'disabled-skin-support': ('weights[(sy-y0)*width+source_x] > 0', 'True', 'test_unmasked_neighbor_refused'),
    'disabled-mirroring': ('width - 1 - sx if flip else sx', 'sx', 'test_mirrored_support'),
    'disabled-outside-row': ('before[row:row+WIDTH*3] == after[row:row+WIDTH*3]', 'True', 'test_outside_row_refused'),
    'disabled-outside-side': (
        'before[row:first] == after[row:first] and\n                     before[last:row+WIDTH*3] == after[last:row+WIDTH*3]',
        'True', 'test_outside_side_refused'),
}
CURRENT = skin_compare


class Placement(unittest.TestCase):
    def setUp(self):
        self.before = bytes(1280 * 960 * 3)
        self.mask = Image.frombytes('L', (3, 2), bytes([1, 0, 0, 0, 0, 255]))

    def changed(self, x, y):
        result = bytearray(self.before)
        result[(y * 1280 + x) * 3] = 1
        return bytes(result)

    def test_normal_support(self):
        self.assertEqual(CURRENT.compare_pixels(self.before, self.changed(20,40), [0,10,20,9], self.mask), 1)

    def test_identical_control(self):
        self.assertEqual(CURRENT.compare_pixels(self.before, self.before, [0,10,20,29], self.mask), 0)

    def test_mirrored_support(self):
        self.assertEqual(CURRENT.compare_pixels(self.before, self.changed(22,40), [1,10,20,9], self.mask), 1)

    def test_unmasked_neighbor_refused(self):
        with self.assertRaisesRegex(ValueError, 'outside transformed skin mask:009'):
            CURRENT.compare_pixels(self.before, self.changed(21,40), [0,10,20,9], self.mask)

    def test_outside_row_refused(self):
        with self.assertRaisesRegex(ValueError, 'outside skin canvas:009'):
            CURRENT.compare_pixels(self.before, self.changed(20,39), [0,10,20,9], self.mask)

    def test_outside_side_refused(self):
        with self.assertRaisesRegex(ValueError, 'outside skin canvas:009'):
            CURRENT.compare_pixels(self.before, self.changed(19,40), [0,10,20,9], self.mask)

    def test_no_change_in_empty_mask(self):
        blank = Image.new('L', (3,2))
        self.assertEqual(CURRENT.compare_pixels(self.before, self.before, [1,10,20,29], blank), 0)

    def test_lower_weight_is_support(self):
        self.assertEqual(CURRENT.compare_pixels(self.before, self.changed(22,41), [0,10,20,9], self.mask), 1)


def main():
    global CURRENT
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('smoke','regression'), required=True)
    parser.add_argument('--mutation', choices=tuple(MUTATIONS))
    parser.add_argument('--mutation-check', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    raw = SOURCE.read_text()
    source = raw
    tests = ['test_normal_support', 'test_identical_control'] if args.phase == 'smoke' else [
        name for name in unittest.defaultTestLoader.getTestCaseNames(Placement) if name not in ('test_normal_support','test_identical_control')]
    if args.mutation:
        old,new,test = MUTATIONS[args.mutation]
        assert source.count(old) == 1, 'unique executable mutation'
        source = source.replace(old,new)
        CURRENT = types.ModuleType('mutated_skin_compare')
        exec(compile(source, str(SOURCE) + ':' + args.mutation, 'exec'), CURRENT.__dict__)
        tests = [test]
    digest = hashlib.sha256(source.encode()).hexdigest()
    witness = f'WITNESS skin-compare compiled-source={digest} pid={os.getpid()}'
    print(witness, flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Placement(t) for t in tests))
    report = {'phase':args.phase,'passed':result.testsRun-len(result.failures)-len(result.errors),
              'tests':tests,'compiled_source_sha256':digest,'witness':witness,'native_launched':False,
              'mutation':args.mutation,'failures':len(result.failures)+len(result.errors)}
    if not result.wasSuccessful():
        return 1
    if args.mutation_check:
        controls=[]
        for name,(old,new,test) in MUTATIONS.items():
            run=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--phase','regression','--mutation',name],
                               capture_output=True,text=True,timeout=30)
            changed=raw.replace(old,new)
            expected=hashlib.sha256(changed.encode()).hexdigest()
            assert run.returncode==1 and f'compiled-source={expected}' in run.stdout, 'executed mutant:' + name
            assert test in run.stderr and ('FAILED (failures=1)' in run.stderr or 'FAILED (errors=1)' in run.stderr), 'one named failure:' + name
            controls.append({'name':name,'status':'FIRED','test':test,'compiled_source_sha256':expected,
                             'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        report['mutations']=controls
    if args.report:
        assert not args.report.exists(), 'preserve report'
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ('phase','passed','failures','native_launched')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
