"""Copy compact Windows delivery evidence; raw PPM diagnostics remain in scratch."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / 'build/seasonal-final-windows' / args.label
    target = HERE / args.label
    target.mkdir(exist_ok=False)
    copied = []
    for name in ('adaptation.json', 'gate-adaptation.diff', 'gate-retained.ps1',
                 'gate.log', 'running.json', 'result.json'):
        raw = (source / name).read_bytes()
        shutil.copyfile(source / name, target / name)
        copied.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(),
                       'bytes': len(raw)})
    record = {'schema_version': 1, 'source_directory': str(source),
              'files': copied,
              'scratch_only': 'Raw wave/palm PPMs and temporary native fixtures. '
                              'Their hashes and capture-marker results are retained in result.json.',
              'helper': 'art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py',
              'launcher': 'art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py'}
    (target / 'evidence.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps({'copied': len(copied), 'target': str(target)}))


if __name__ == '__main__':
    main()
