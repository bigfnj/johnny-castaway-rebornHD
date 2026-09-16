"""Run the frozen018 color tests against the explicit v5 adapter.

Assertions and fresh-process controls are imported unchanged. The inherited
test's v2 scope string is retained separately so this new report names v5
truthfully. Historical source files and evidence are not written.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    adapter = module('correct018', HERE / 'correct018_foot_v5.py')
    tests = module('frozen_test_color018', HERE / 'test_color018.py')
    tests.run(args.export.resolve(), args.output.resolve(), args.phase)
    path = args.output / (args.phase + '.json')
    record = json.loads(path.read_bytes())
    record['inherited_test_scope'] = record['scope']
    record['scope'] = 'Only selected018-foot-v5 color; no anatomy, native-playback or full28-pose revalidation. Assertions and test input identities come from the byte-unchanged018 test.'
    record['runner_sha256'] = adapter.sha(Path(__file__).read_bytes())
    record['runner_path'] = Path(__file__).relative_to(adapter.ROOT).as_posix()
    record['adapter_path'] = Path(adapter.__file__).relative_to(adapter.ROOT).as_posix()
    record['test_path'] = Path(tests.__file__).relative_to(adapter.ROOT).as_posix()
    path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
