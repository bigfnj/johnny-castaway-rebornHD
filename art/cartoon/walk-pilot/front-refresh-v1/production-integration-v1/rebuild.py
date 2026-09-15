#!/usr/bin/env python3
"""Rebuild the reviewed two-frame replacement without changing its art evidence.

Use a fresh --output directory. --baseline must be the pinned pre-promotion ZIP.
The default only builds and verifies; --promote explicitly updates the repo ZIP.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


BASELINE_COMMIT = "4551081495eee81e5e5bf2d8b5f00a5619a176a2"
BASELINE_SHA = "0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd"
PRIVATE_SHA = "1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63"
PREFIX = "data/styles/cartoon/"
FRONT = "art/cartoon/walk-pilot/front-refresh-v1/"
CHANGED = {
    "BMP/JOHNWALK.BMP/028.png": "5b645ae3003c54dc65946118999f0f3906ca0f7fa47a10fa61c60ba10b46e3f4",
    "BMP/JOHNWALK.BMP/029.png": "8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a",
}
RECORDS = {
    FRONT + "feedback-native-v1.json": "6f58b747582591c6172e166f31f50a7258fcca17dde1195c273e532f26c6059d",
    FRONT + "motion-acceptance-v1.json": "96cc1dfd845fbf08d07d174d091bd07e51d47aaa19654be970861046ed03e091",
    FRONT + "review-evidence/native-publication-v1/publication.json": "1564d54ec4e97b0348cd76cc773c7a39bdb7b413f9f3e69c81e9a8f56ec82a6c",
    FRONT + "review-evidence/native-island-v1/evidence.json": "deb5ec550a8f5a7ea25fcbe5799a0e2d313be160ca5808080210f61f7e416805",
    FRONT + "review-evidence/motion-v1/export/recipe.json": "8b72e60b5598e29909f5897a47e4304a54f9e5b96564624811e0f57e56218725",
    FRONT + "review-evidence/motion-v1/export/export-report.json": "3130e9bb9f6e027a5ce1d4b7ab91d321ef29abc003f47d62a8bf9c3a3f5633fd",
    "art/cartoon/arrival-pilot-v1/production-acceptance.json": "52d71dd6255a544791d2de24c64882716b95cb0e90085f23a798612aef71f4e2",
    "art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json": "ce7f3832982bcfbef13f9ce6dc06c1f60ce774b89aca088247442040fd767a0c",
    "art/cartoon/walk-expansion-v1/production-acceptance.json": "70942da086c93ca2fca2693fc35fb295be7d1ea38c29c38598124b5a1c16adc8",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), f"{path}: duplicate ZIP member")
        return {name: sha(archive.read(name)) for name in names}


def member_errors(expected, actual):
    return [f"{name}: member content differs" for name in sorted(set(expected) | set(actual))
            if expected.get(name) != actual.get(name)]


def protected_inputs(repo):
    expected = dict(RECORDS)
    bundle = FRONT + "review-evidence/native-island-v1/"
    for name, digest in json.loads((repo / bundle / "evidence.json").read_text())["files_sha256"].items():
        expected[bundle + name] = digest
    for name, digest in expected.items():
        require(sha((repo / name).read_bytes()) == digest, f"{name}: frozen evidence changed")
    return expected


def run_pack(repo, baseline, accepted, output, mode):
    command = [sys.executable, "-B", str(repo / "tools/art_pack.py"), mode,
               "--archive", str(baseline), "--ledger", str(repo / "art/cartoon/pack.json"),
               "--accepted", str(accepted)]
    if mode == "build":
        command += ["--output", str(output / "scrantic_data.zip")]
    result = subprocess.run(command, cwd=repo, text=True, capture_output=True)
    (output / f"{mode}.stdout.txt").write_text(result.stdout, encoding="utf-8", newline="\n")
    (output / f"{mode}.stderr.txt").write_text(result.stderr, encoding="utf-8", newline="\n")
    require(result.returncode == 0, f"art_pack {mode}: {result.stderr}")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--private-candidate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()
    repo, baseline, output = args.repo.resolve(), args.baseline.resolve(), args.output.resolve()
    require(sha(baseline.read_bytes()) == BASELINE_SHA, f"{baseline}: baseline identity mismatch")
    require(not output.exists(), f"{output}: use a fresh output directory")
    protected = protected_inputs(repo)
    prior = json.loads(subprocess.check_output(
        ["git", "-C", str(repo), "show", BASELINE_COMMIT + ":art/cartoon/pack.json"]))
    ledger = json.loads((repo / "art/cartoon/pack.json").read_text())
    prior_rows = {row["path"]: row for row in prior["assets"]}
    rows = {row["path"]: row for row in ledger["assets"]}
    require(len(rows) == len(ledger["assets"]) == 28, "pack.json: expected 28 unique assets")
    require(rows.keys() == prior_rows.keys(), "pack.json: required asset scope changed")
    require(ledger["required_assets"] == prior["required_assets"], "pack.json: required asset order changed")
    require(ledger["runtime"] == prior["runtime"], "pack.json: runtime contract changed")
    for path, row in rows.items():
        expected = dict(prior_rows[path])
        if path in CHANGED:
            expected.update(sha256=CHANGED[path], recipe=FRONT + "review-evidence/motion-v1/export/recipe.json",
                            review=FRONT + "production-acceptance.json")
        require(row == expected, f"{path}: unexpected pack row change")

    before = members(baseline)
    require(len(before) == 2579, "baseline: expected 2579 ZIP members")
    expected = dict(before)
    expected.update({PREFIX + path: digest for path, digest in CHANGED.items()})
    private = None
    if args.private_candidate:
        private = args.private_candidate.resolve()
        require(sha(private.read_bytes()) == PRIVATE_SHA, f"{private}: reviewed archive identity mismatch")
        require(not member_errors(expected, members(private)), "reviewed archive: unexpected member delta")

    output.mkdir(parents=True)
    accepted = output / "accepted"
    with zipfile.ZipFile(baseline) as archive:
        for path, row in rows.items():
            data = ((repo / FRONT / "review-evidence/motion-v1/export" / path).read_bytes()
                    if path in CHANGED else archive.read(PREFIX + path))
            require(sha(data) == row["sha256"], f"{path}: accepted input identity mismatch")
            target = accepted / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    smoke = run_pack(repo, baseline, accepted, output, "validate")
    require(smoke["assets"] == 28, "art_pack validate: expected 28 accepted PNGs")
    print("SMOKE passed: art_pack validate accepted all 28 PNGs", flush=True)
    build = run_pack(repo, baseline, accepted, output, "build")
    built = output / "scrantic_data.zip"
    actual = members(built)
    errors = member_errors(expected, actual)
    require(not errors, "\n".join(errors))
    changed = [name for name in before if before[name] != actual[name]]
    require(set(changed) == {PREFIX + path for path in CHANGED}, "built archive: replacement scope differs")
    if private:
        require(not member_errors(members(private), actual), "built archive differs from reviewed private candidate")

    # Execute the comparison against a real altered ZIP, not a fabricated result.
    wrong = output / "negative-control.zip"
    mutated = PREFIX + "BMP/JOHNWALK.BMP/028.png"
    with zipfile.ZipFile(built) as src, zipfile.ZipFile(wrong, "x") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            dst.writestr(info, data + b"mutation" if info.filename == mutated else data)
    negative = member_errors(expected, members(wrong))
    require(negative == [f"{mutated}: member content differs"], "negative control failed to name exactly changed 028")
    wrong.unlink()
    require(protected_inputs(repo) == protected, "frozen evidence set changed during verification")
    print("REGRESSION passed: all 2579 members match; exactly 028/029 replaced; named negative control fired", flush=True)

    report = {
        "schema_version": 1, "date": "2026-09-15",
        "scope": "Package smoke, independent full ZIP member comparison and deliberate changed-member control. Native runtime observations are recorded separately.",
        "baseline_commit": BASELINE_COMMIT, "before_sha256": BASELINE_SHA,
        "archive_sha256": sha(built.read_bytes()), "member_count": len(actual),
        "cartoon_asset_count": len(rows), "unchanged_members": len(before) - len(changed),
        "changed_members": {name: {"before_sha256": before[name], "after_sha256": actual[name]} for name in sorted(changed)},
        "added_members": [], "removed_members": [], "prior_26_pack_rows_unchanged": True,
        "runtime_manifest_unchanged": before[PREFIX + "manifest.json"] == actual[PREFIX + "manifest.json"],
        "original_resource_sha256": {name: actual[name] for name in ("data/RESOURCE.MAP", "data/RESOURCE.001")},
        "reviewed_private_archive_sha256": PRIVATE_SHA,
        "private_archive_independently_compared": private is not None,
        "all_reviewed_member_content_hashes_equal": private is not None,
        "smoke": smoke, "production_builder_report": build,
        "negative_control": {"input": "Fresh ZIP with 028 member payload appended by mutation", "failures": negative, "restored": "Corrupt scratch ZIP removed; verified candidate retained unchanged"},
        "protected_files_sha256": protected,
        "accepted_pngs_sha256": {path: row["sha256"] for path, row in rows.items()},
        "production_promoted": False,
    }
    if args.promote:
        production = repo / "assets/scrantic_data.zip"
        require(sha(production.read_bytes()) == BASELINE_SHA, "production archive changed since baseline")
        # Atomic replacement follows successful validation and complete independent readback.
        handle, staged_name = tempfile.mkstemp(prefix=".front-refresh-", suffix=".zip", dir=production.parent)
        os.close(handle)
        staged = Path(staged_name)
        try:
            shutil.copyfile(built, staged)
            require(sha(staged.read_bytes()) == report["archive_sha256"], "promotion copy changed")
            os.replace(staged, production)
        finally:
            if staged.exists():
                staged.unlink()
        require(sha(production.read_bytes()) == report["archive_sha256"], "promoted archive identity mismatch")
        require(not member_errors(expected, members(production)), "promoted archive member readback differs")
        report["production_promoted"] = True
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"archive_sha256": report["archive_sha256"], "production_promoted": report["production_promoted"]}))


if __name__ == "__main__":
    main()
