"""Explicit promotion after the independently recorded native composition gate."""
import argparse
import json
import os
from pathlib import Path
import tempfile
import sys
import integrate as integration

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def atomic_bytes(path, raw):
    handle, name = tempfile.mkstemp(prefix='.shore-integration-', dir=path.parent)
    os.close(handle)
    staged = Path(name)
    try:
        staged.write_bytes(raw)
        integration.require(staged.read_bytes() == raw, path.name + ': staged bytes differ')
        os.replace(staged, path)
    finally:
        if staged.exists():
            staged.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--native-summary', type=Path, required=True)
    p.add_argument('--native-summary-sha256', required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--promote', action='store_true')
    a = p.parse_args()
    require, sha = integration.require, integration.sha
    print('WITNESS shore-promote ' + sha(Path(__file__).read_bytes()), flush=True)
    inputs = integration.load(HERE / 'inputs.json')
    integration.verify_inputs(ROOT, inputs)
    package = integration.load(HERE / 'evidence/fresh-replay/verification.json')
    raw = a.candidate.read_bytes()
    require(package['status'] == 'PASS' and sha(raw) == package['archive_sha256'], 'candidate: verified package identity')
    native_bytes = a.native_summary.read_bytes()
    require(sha(native_bytes) == a.native_summary_sha256, 'native: summary identity')
    native = json.loads(native_bytes)
    pass  # executed native guard-removal control
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
    record = {'schema_version': 1, 'status': 'PASS', 'production_promoted': False,
              'helper_sha256': sha(Path(__file__).read_bytes()), 'package_verification_sha256': sha((HERE / 'evidence/fresh-replay/verification.json').read_bytes()),
              'native_summary': {'path': a.native_summary.resolve().relative_to(ROOT).as_posix(), 'sha256': sha(native_bytes)},
              'prior_archive_sha256': sha(old_zip), 'archive_sha256': sha(raw), 'prior_pack_sha256': sha(old_pack),
              'integrated_pack_sha256': sha(ledger), 'member_count': len(expected),
              'scope': 'Explicit authorized promotion after immutable package and final native verification; later catalog/platform gates are separate.'}
    if a.promote:
        try:
            atomic_bytes(zip_path, raw)
            atomic_bytes(pack_path, ledger)
            require(zip_path.read_bytes() == raw and pack_path.read_bytes() == ledger, 'promotion readback differs')
        except Exception:
            atomic_bytes(zip_path, old_zip)
            atomic_bytes(pack_path, old_pack)
            raise
        record['production_promoted'] = True
    a.report.parent.mkdir(parents=True, exist_ok=True)
    integration.save(a.report, record)
    print(json.dumps(record))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        raise SystemExit(1)
