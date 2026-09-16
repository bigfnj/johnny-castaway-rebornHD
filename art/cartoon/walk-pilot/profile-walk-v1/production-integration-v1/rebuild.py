"""Reproduce the approved eight-profile-pose package from pinned inputs.

Requires Pillow12.3.0, the pinned production baseline and a fresh output folder.
Default operation only builds and verifies. --promote explicitly updates the
production ZIP after all checks. Frozen ledger snapshots permit later replay.
"""
# Adapted from front-arrival-v1/production-integration-v1/rebuild.py; rendering and
# packaging use the unchanged maintained exporters and tools/art_pack.py.
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile

import PIL

HERE = Path(__file__).resolve().parent
INPUTS_SHA = "1b34668a0b002dcf6cbfd41f92dcf56c176d620cb3483e89e7aa8cc24b9f415b"
PREFIX = "data/styles/cartoon/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_bytes())


def members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "archive: duplicate member")
        return {name: sha(archive.read(name)) for name in names}


def member_errors(expected, actual):
    return [f"{name}: member content differs" for name in sorted(set(expected) | set(actual))
            if expected.get(name) != actual.get(name)]


def verify_protected(repo, inputs):
    for name, digest in inputs["protected_files_sha256"].items():
        require(sha((repo / name).read_bytes()) == digest, name + ": protected bytes changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--private-candidate", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--audit-archive", type=Path, help="Read-only comparison used by the executed negative control")
    args = parser.parse_args()
    witness = "WITNESS profile-package " + sha(Path(__file__).read_bytes())
    print(witness, flush=True)
    repo, baseline = args.repo.resolve(), args.baseline.resolve()
    require(sha((HERE / "inputs.json").read_bytes()) == INPUTS_SHA, "inputs.json: identity mismatch")
    inputs = load(HERE / "inputs.json")
    verify_protected(repo, inputs)
    require(sha(baseline.read_bytes()) == inputs["baseline_archive_sha256"], "baseline: identity mismatch")
    before = members(baseline)
    require(len(before) == 2583, "baseline: expected2583 members")
    specs = load(HERE / inputs["runtime_sources"])["frames"]
    require([s["frame"] for s in specs] == list(range(1, 9)), "scope: expected eight profile frames")
    expected = dict(before)
    additions = {PREFIX + s["path"]: s["sha256"] for s in specs}
    require(not set(additions).intersection(before), "scope: profile members must be additions")
    expected.update(additions)
    if args.audit_archive:
        require(not args.promote and args.output is None, "audit: no output or promotion")
        failures = member_errors(expected, members(args.audit_archive))
        require(not failures, "\n".join(failures))
        print("PASS independent member audit", flush=True)
        return 0
    require(args.output is not None, "output: required")
    output = args.output.resolve()
    require(not output.exists(), "output: use a fresh directory")
    require(PIL.__version__ == "12.3.0", "Pillow: reproduction requires12.3.0")
    prior = load(HERE / inputs["prior_pack"])
    ledger_path = HERE / inputs["integrated_pack"]
    ledger = load(ledger_path)
    require(len(prior["assets"]) == 32 and len(ledger["assets"]) == 40, "ledger: expected32-to40 assets")
    require(ledger["assets"][:32] == prior["assets"], "ledger: previous32 rows changed")
    require(ledger["required_assets"] == prior["required_assets"] + [s["path"] for s in specs], "ledger: required scope changed")
    require(ledger["runtime"] == prior["runtime"] and ledger["pilot_history"] == prior["pilot_history"], "ledger: historical/runtime contract changed")
    if args.promote:
        require(load(repo / "art/cartoon/pack.json") == ledger, "promotion: current ledger differs from frozen40-asset snapshot")
        require(sha((repo / "assets/scrantic_data.zip").read_bytes()) == inputs["baseline_archive_sha256"], "promotion: production no longer matches baseline")
    private = args.private_candidate.resolve() if args.private_candidate else None
    if private:
        require(sha(private.read_bytes()) == inputs["reviewed_private_archive_sha256"], "reviewed private archive: identity mismatch")
        require(not member_errors(expected, members(private)), "reviewed private archive: unexpected member delta")
    else:
        print("LIMIT private archive not supplied: pinned baseline and approved member identities remain checked; independent private-archive comparison NOT RUN", flush=True)
    output.mkdir(parents=True)
    commands = []

    def portable(value):
        path = Path(value)
        try:
            return path.resolve().relative_to(repo).as_posix()
        except (ValueError, OSError):
            if path == baseline:
                return "${BASELINE_ARCHIVE}"
            if private and path == private:
                return "${REVIEWED_PRIVATE_ARCHIVE}"
            try:
                return "${OUTPUT}/" + path.resolve().relative_to(output).as_posix()
            except ValueError:
                return str(value)

    def execute(label, argv, expected_status=0):
        command = [sys.executable, "-B", *map(str, argv)]
        run = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=120)
        stdout = output / (label + ".stdout.txt")
        stderr = output / (label + ".stderr.txt")
        stdout.write_text(run.stdout, encoding="utf-8", newline="\n")
        stderr.write_text(run.stderr, encoding="utf-8", newline="\n")
        commands.append({"order": len(commands) + 1, "label": label,
                         "argv": ["${PYTHON}", "-B", *[portable(v) if Path(str(v)).is_absolute() else str(v) for v in argv]],
                         "cwd": "${REPO}", "exit_code": run.returncode,
                         "stdout": stdout.name, "stderr": stderr.name,
                         "stdout_sha256": sha(stdout.read_bytes()), "stderr_sha256": sha(stderr.read_bytes())})
        require(run.returncode == expected_status, label + ": " + run.stderr)
        return run

    reproduced = {}
    for spec in specs:
        frame, path = spec["frame"], spec["path"]
        recipe = load(repo / spec["runtime_recipe"])
        reviewed = load(repo / spec["reviewed_recipe"])
        restored = copy.deepcopy(recipe)
        restored.pop("reviewed_recipe")
        restored.pop("runtime_annotation_limit")
        restored["frames"][0].pop("path")
        restored["frames"][0].pop("candidate_png_sha256")
        require(restored == reviewed, path + ": runtime recipe changed rendering fields")
        target = output / f"export-{frame:03}"
        argv = [repo / spec["exporter"], "--recipe", repo / spec["runtime_recipe"], "--output", target]
        argv += ["--frame", str(frame)]
        run = execute(f"export-{frame:03}", argv)
        require("WITNESS export.py SHA256=" + spec["exporter_sha256"] in run.stdout, path + ": exporter witness missing")
        report = load(target / "export-report.json")
        prior_report = load(repo / spec["reviewed_report"])
        require(report["outputs_sha256"] == prior_report["outputs_sha256"], path + ": reviewed padded/runtime outputs differ")
        require(sha((target / path).read_bytes()) == spec["sha256"], path + ": runtime bytes differ")
        reproduced[path] = target / path
    print("SMOKE PASS eight annotated recipes reproduce reviewed PNG and padded bytes", flush=True)

    accepted = output / "accepted"
    with zipfile.ZipFile(baseline) as archive:
        for row in ledger["assets"]:
            path = row["path"]
            data = reproduced[path].read_bytes() if path in reproduced else archive.read(PREFIX + path)
            require(sha(data) == row["sha256"], path + ": accepted input mismatch")
            target = accepted / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    common = [repo / "tools/art_pack.py", "--archive", baseline, "--ledger", ledger_path, "--accepted", accepted]
    smoke = json.loads(execute("pack-smoke", [common[0], "validate", *common[1:]]).stdout)
    require(smoke["assets"] == 40, "pack-smoke: expected40 accepted sprites/screens")
    print("SMOKE PASS art_pack validates40 approved PNGs", flush=True)
    built = output / "scrantic_data.zip"
    packing = json.loads(execute("pack-build", [common[0], "build", *common[1:], "--output", built]).stdout)
    actual = members(built)
    require(not member_errors(expected, actual), "built archive: unexpected member delta")
    require(len(actual) == 2591 and set(actual) - set(before) == set(additions), "built archive: wrong addition scope")
    require(all(actual[name] == digest for name, digest in before.items()), "built archive: existing member changed")
    if private:
        require(not member_errors(members(private), actual), "built archive: private candidate member mismatch")

    wrong = output / "negative-control.zip"
    damaged = PREFIX + "BMP/JOHNWALK.BMP/001.png"
    with zipfile.ZipFile(built) as src, zipfile.ZipFile(wrong, "x") as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            dst.writestr(info, data + b"mutation" if info.filename == damaged else data)
    control = execute("negative-member", [Path(__file__).resolve(), "--repo", repo, "--baseline", baseline, "--audit-archive", wrong], 1)
    require(witness in control.stdout and control.stderr.strip() == "FAIL " + damaged + ": member content differs", "negative control: expected one witnessed named failure")
    wrong.unlink()
    verify_protected(repo, inputs)
    print("REGRESSION PASS2591 members;2583 unchanged; exactly eight additions; named001 corruption control fired", flush=True)
    report = {"schema_version": 1, "scope": "Eight runtime reproductions, package smoke, complete member regression and executed corrupted-member control. Native/human evidence remains separate.",
              "inputs_sha256": INPUTS_SHA, "helper_sha256": sha(Path(__file__).read_bytes()),
              "python_version": platform.python_version(), "pillow_version": PIL.__version__,
              "baseline_commit": inputs["baseline_commit"], "baseline_archive_sha256": inputs["baseline_archive_sha256"],
              "archive_sha256": sha(built.read_bytes()), "member_count": len(actual), "cartoon_asset_count": 40,
              "unchanged_members": len(before), "added_members": additions, "removed_members": [], "changed_members": [],
              "prior32_pack_rows_unchanged": True, "runtime_manifest_unchanged": before[PREFIX + "manifest.json"] == actual[PREFIX + "manifest.json"],
              "reviewed_private_archive_sha256": inputs["reviewed_private_archive_sha256"], "private_members_independently_compared": private is not None,
              "private_archive_limit": None if private else "Private ZIP not supplied; pinned baseline and approved member identities checked, private-archive comparison not rerun.",
              "negative_control": {"status": "FIRED", "failure_count": 1, "failure": control.stderr.strip(), "executed_helper_sha256": sha(Path(__file__).read_bytes()), "restored": "Corrupt scratch ZIP removed; candidate unchanged"},
              "package_smoke": smoke, "builder": packing, "commands_in_execution_order": commands,
              "archive_envelope": "Standard art_pack builder. ZIP envelope may differ from the reviewed private candidate; exact equality applies to every named member payload.",
              "canonical_builder_lf_sha256": sha((repo / "tools/art_pack.py").read_bytes().replace(b"\r\n", b"\n")),
              "protected_files_sha256": inputs["protected_files_sha256"], "production_promoted": False}
    if args.promote:
        production = repo / "assets/scrantic_data.zip"
        require(sha(production.read_bytes()) == inputs["baseline_archive_sha256"], "production: changed during verification")
        handle, name = tempfile.mkstemp(prefix=".profile-family-", suffix=".zip", dir=production.parent)
        os.close(handle)
        staged = Path(name)
        try:
            shutil.copyfile(built, staged)
            require(sha(staged.read_bytes()) == report["archive_sha256"], "promotion: copy identity differs")
            os.replace(staged, production)
        finally:
            if staged.exists():
                staged.unlink()
        require(members(production) == expected and sha(production.read_bytes()) == report["archive_sha256"], "promotion: readback differs")
        report["production_promoted"] = True
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in ("archive_sha256", "production_promoted", "member_count")}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print("FAIL " + str(error), file=sys.stderr)
        raise SystemExit(1)
