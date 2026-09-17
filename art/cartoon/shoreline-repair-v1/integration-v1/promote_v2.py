"""V2 promotion: include the final report in the rollback-protected transaction.

The V1 helper and its preflight proof remain immutable. Validation is identical;
only report preparation, atomic report write and rollback scope are amended.
"""
import argparse
import json
from pathlib import Path
import sys
import integrate as integration
from promote import atomic_bytes

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--native-summary', type=Path, required=True)
    p.add_argument('--native-summary-sha256', required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--promote', action='store_true')
    a = p.parse_args()
    require, sha = integration.require, integration.sha
    print('WITNESS shore-promote-v2 ' + sha(Path(__file__).read_bytes()), flush=True)
    inputs = integration.load(HERE / 'inputs.json')
    integration.verify_inputs(ROOT, inputs)
    package = integration.load(HERE / 'evidence/fresh-replay/verification.json')
    raw = a.candidate.read_bytes()
    require(package['status'] == 'PASS' and sha(raw) == package['archive_sha256'], 'candidate: verified package identity')
    native_bytes = a.native_summary.read_bytes()
    require(sha(native_bytes) == a.native_summary_sha256, 'native: summary identity')
    native = json.loads(native_bytes)
    require(native['status'] == 'PASS' and native['phase'] == 'full' and native['package_pair']['candidate_sha256'] == sha(raw), 'native: successful candidate composition required')
    require(native['smoke_captures'] == 28 and native['fresh_repeat_captures'] == 28 and native['negative_controls'] == 8, 'native: final scoped gate coverage')
    ledger = (HERE / 'integrated-pack.json').read_bytes()
    pack_path, zip_path = ROOT / 'art/cartoon/pack.json', ROOT / 'assets/scrantic_data.zip'
    old_pack, old_zip = pack_path.read_bytes(), zip_path.read_bytes()
    require(json.loads(old_pack) == integration.load(HERE / 'prior-pack.json'), 'production ledger differs from prior')
    require(sha(old_zip) == inputs['baseline_archive_sha256'], 'production archive differs from prior')
    expected = integration.members(zip_path)
    expected.update({integration.PREFIX + r['path']: r['candidate_png_sha256'] for r in integration.load(HERE / 'runtime-recipe.json')['frames']})
    require(integration.members(a.candidate) == expected, 'candidate: complete payload map differs')
    require(not a.report.exists(), 'report: use a fresh output')
    # Fail here, before either production write, if the report parent is invalid.
    a.report.parent.mkdir(parents=True, exist_ok=True)
    record = {'schema_version': 2, 'status': 'PASS', 'production_promoted': False,
              'helper_sha256': sha(Path(__file__).read_bytes()), 'atomic_helper_sha256': sha((HERE/'promote.py').read_bytes()),
              'package_verification_sha256': sha((HERE / 'evidence/fresh-replay/verification.json').read_bytes()),
              'native_summary': {'path': a.native_summary.resolve().relative_to(ROOT).as_posix(), 'sha256': sha(native_bytes)},
              'prior_archive_sha256': sha(old_zip), 'archive_sha256': sha(raw), 'prior_pack_sha256': sha(old_pack),
              'integrated_pack_sha256': sha(ledger), 'member_count': len(expected),
              'scope': 'Explicit authorized promotion after immutable package and final native verification; later catalog/platform gates are separate.'}
    if a.promote:
        try:
            atomic_bytes(zip_path, raw)
            atomic_bytes(pack_path, ledger)
            require(zip_path.read_bytes() == raw and pack_path.read_bytes() == ledger, 'promotion readback differs')
            record['production_promoted'] = True
            encoded = (json.dumps(record, indent=2)+'\n').encode()
            atomic_bytes(a.report, encoded)
            require(a.report.read_bytes() == encoded, 'promotion report readback differs')
        except Exception:
            atomic_bytes(zip_path, old_zip)
            atomic_bytes(pack_path, old_pack)
            if a.report.exists():
                a.report.unlink()
            raise
    else:
        atomic_bytes(a.report, (json.dumps(record, indent=2)+'\n').encode())
    print(json.dumps(record))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        raise SystemExit(1)
