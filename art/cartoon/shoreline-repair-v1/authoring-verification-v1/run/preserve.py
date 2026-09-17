"""Copy this completed, bounded authoring check without rewriting prior evidence."""
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEST = ROOT / "art/cartoon/shoreline-repair-v1/authoring-verification-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode())


def copy(source, relative):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists(), target
    shutil.copyfile(source, target)
    assert sha(source) == sha(target)


assert not DEST.exists(), DEST
smoke = json.loads((HERE / "smoke.json").read_bytes())
regression = json.loads((HERE / "regression.json").read_bytes())
controls = json.loads((HERE / "controls-v2/controls.json").read_bytes())
assert all(row["status"] == "PASS" for row in (smoke, regression, controls))
assert smoke["inputs"] == regression["inputs"]
assert all(sha(ROOT / name) == digest for name, digest in regression["inputs"].items())
for name in ("run.py", "preserve.py", "smoke.json", "regression.json"):
    copy(HERE / name, "run/" + name)
for row in smoke["runs"] + regression["runs"]:
    copy(HERE / row["log"], "run/" + row["log"])
for path in sorted((HERE / "controls-v2").iterdir()):
    if path.is_file():
        copy(path, "controls/" + path.name)
copy(HERE / "test_shoreline_replacement_must_be_declared-positive.log", "first-fixture-attempt/failure.log")
for name in ("tests/test_art_pilot_history.py", "tools/art_review_metadata.py", "tools/art_production_catalog.py"):
    copy(ROOT / name, "source/" + name)

outputs = {name: sha(ROOT / name) for name in
           ("docs/knowledge-base/cartoon-art-metadata.json", "docs/knowledge-base/cartoon-art-metadata.md",
            "docs/knowledge-base/cartoon-production-catalog.json", "docs/knowledge-base/cartoon-production-catalog.md")}
pilot = json.loads((ROOT / "docs/knowledge-base/cartoon-art-metadata.json").read_bytes())
catalog = json.loads((ROOT / "docs/knowledge-base/cartoon-production-catalog.json").read_bytes())
assert catalog["summary"]["accepted"] == 47
assert pilot["production_summary"] == {"retained": 5, "replaced": 16}
assert len(pilot["pilot_history"]["replaced_assets"]) == 16
acceptance = "art/cartoon/shoreline-repair-v1/integration-v1/production-acceptance.json"
recipe = "art/cartoon/shoreline-repair-v1/integration-v1/runtime-recipe.json"
assert pilot["current_acceptance_record"] == acceptance

readme = """# Final shoreline authoring verification

The maintained tools accept the final 47-asset production pack through the existing selected-inheritance and named-footprint rules. No acceptance or geometry guard was relaxed. The pilot catalog retains its 21 historical drawings and original facts, with 16 explicitly replaced slots: six Johnny poses and ten shoreline sprites. Five pilot drawings remain retained. The production catalog records all 47 accepted slots.

The maintained change adds a combined shoreline/history fixture and two damaged-input tests, plus explanatory footprint wording. The fixture keeps historical source canvases and registration intact while current ground, left, center and right families use their separately declared runtime canvases and offsets.

## Ordered checks

`run/smoke.json` records the maintained pack, inventory, pilot history, pilot metadata and production catalog smoke tests, followed by both catalog generators. `run/regression.json` records their regressions and both read-only catalog checks against the same package and maintained sources. The histories and catalogs resolve actual production approval and recipe records; external original resources are not reread. No visual approval or original-executable parity is inferred from these checks.

`controls/controls.json` records two fresh-process source mutations against the new damaged-input cases. Disabling the declared-replacement guard or the recipe/ledger footprint guard causes exactly one named test failure. Each run prints the imported source SHA-256; restored original-source controls pass. Mutants run only from scratch copies. Existing unchanged guard mutation matrices were not repeated.

The unchanged inventory suite explicitly skipped its two Windows symlink cases because this process lacks symlink creation privilege (WinError 1314). Its other nine cases, including hardlink and ordinary path identity, executed successfully. The final report distinguishes scheduled, executed and skipped counts. No symlink result is claimed from this run.

The initial fixture accidentally shared one list between its replacement declaration and newly accepted list. Removing a replacement also altered new-approval coverage and therefore reached an earlier guard. That failed test log is retained in `first-fixture-attempt/failure.log`; independent lists corrected the fixture before the final controls. This was a test-fixture defect, not a production failure.

## Reproduction

Use this checkpoint's exact 47-asset source checkout and toolbox Python. Copy `run/run.py` into a fresh `build/shoreline-repair-v1/final-authoring-v1/run.py`; its repository-root calculation assumes that depth. The output directory must be fresh because the runner refuses to overwrite logs. Run from the repository root:

```
python -B build/shoreline-repair-v1/final-authoring-v1/run.py smoke
python -B build/shoreline-repair-v1/final-authoring-v1/run.py regression
python -B build/shoreline-repair-v1/final-authoring-v1/run.py controls --label controls-v2
```

Use the configured toolbox interpreter in place of `python` where required. Smoke regeneration writes only the maintained catalog JSON/Markdown outputs. Regression and controls do not promote or modify artwork. Do not rerun this historical preservation writer into its existing frozen destination. Preserved maintained-source snapshots identify the executed Windows bytes; working-tree line endings may differ after another platform's checkout.
"""
(DEST / "README.md").write_bytes(readme.encode())
files = {p.relative_to(DEST).as_posix(): sha(p) for p in sorted(DEST.rglob("*")) if p.is_file()}
regression_total = sum(r["tests"] or 0 for r in regression["runs"])
skips = {row["log"]: int(match[1]) for row in regression["runs"]
         if (match := re.search(r"OK \(skipped=(\d+)\)", (HERE / row["log"]).read_text()))}
result = {"schema_version": 1, "status": "PASS", "scope": "maintained authoring and generated catalogs after final shoreline/seasonal promotion",
          "inputs": regression["inputs"], "current_approval": {acceptance: sha(ROOT / acceptance), recipe: sha(ROOT / recipe)},
          "outputs": outputs, "production_summary": catalog["summary"], "pilot_production_summary": pilot["production_summary"],
          "smoke_tests": sum(r["tests"] or 0 for r in smoke["runs"]),
          "regression_scheduled_tests": regression_total,
          "regression_executed_tests": regression_total - sum(skips.values()),
          "regression_skipped_tests": sum(skips.values()), "skipped_by_log": skips,
          "source_mutations_fired": 2, "restored_controls": 2, "copied_files_sha256": files}
save(DEST / "verification.json", result)
assert all(sha(DEST / name) == checksum for name, checksum in files.items())
save(DEST / "readback.json", {"status": "PASS", "copied_files": len(files),
                             "verification_sha256": sha(DEST / "verification.json")})
print("PASS authoring preservation", len(files), sha(DEST / "verification.json"), flush=True)
