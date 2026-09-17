import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEST = ROOT / "art/cartoon/shoreline-repair-v1/character-inventory-refresh-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode())


assert not DEST.exists()
result = json.loads((HERE / "verification.json").read_bytes())
assert result["status"] == "PASS" and result["protected_files_unchanged"]
assert all(sha(ROOT / name) == digest for name, digest in result["protected_files_sha256"].items())
assert sha(ROOT / "art/cartoon/character-inventory-v1/inventory.json") == result["inventory_after_sha256"]
DEST.mkdir(parents=True)
for name in ("diagnosis.json", "verification.json", "smoke.json", "regression.json",
             "stale-check.log", "regenerate.log", "smoke.log", "regression.log", "final-check.log"):
    shutil.copyfile(HERE / name, DEST / name)
for name in ("diagnose.py", "run.py", "preserve.py"):
    shutil.copyfile(HERE / name, DEST / name)
mutant = HERE / "regression/build_inventory-preserved-png-guard-removed.py"
assert sha(mutant) == result["source_mutation"]["sha256"]
shutil.copyfile(mutant, DEST / mutant.name)
(DEST / "README.md").write_bytes(b"""# Current character inventory refresh after shoreline promotion

CI's additional character-inventory check correctly refused the stale generated inventory after production promotion. No builder, test, classification, source reference, approval record or historical verification file needed a change. Only `art/cartoon/character-inventory-v1/inventory.json` changes in the existing character bundle. Its generated README remains byte-identical.

The exact delta has 19 changed JSON leaves: the production ZIP SHA-256, ten shoreline acceptance pointers, and status/acceptance fields for four newly approved HOLIDAY drawings. Character counts, original identities, resource classifications, scene associations and all other fields remain unchanged. There are still 1,002 outstanding confirmed Johnny slots and 28 accepted Johnny slots. Accepted holiday props remain classified as non-Johnny.

`diagnosis.json` preserves both values of every changed leaf. Reversing those changes in the current inventory and encoding with the unchanged builder's `encode()` reconstructs the exact prior inventory SHA-256. This was executed before regeneration. It retains the historical output without another large JSON copy. All old historical verification records remain unchanged and continue to describe that older snapshot.

`verification.json` records the expected stale check failure, normal regeneration, the existing complete inventory smoke, full regression and final CI `--check`, in that order. Regression passed nine named damaged-input controls and an executed guard-removal mutant, followed by restored positive reproduction. This validates input identity and inventory mechanics, not a new visual classification or approval.

For normal future production promotions, run the unchanged builder without `--check` to regenerate the current inventory, then its smoke/regression tests and `--check`. The exact commands and fresh scratch paths are in `verification.json`. The preserved orchestration scripts assume their original `build/shoreline-repair-v1/inventory-refresh-v1/` depth. Do not run them inside this frozen evidence directory. No browser page was republished and no runtime or image bytes were changed here.

The binder's `files_sha256` keys are relative to this directory. `external_outputs_sha256` names the current generated files from the repository root. Other historical/source hashes in diagnosis and verification describe read-only inputs, not copied child artifacts.
""")
files = {p.name: sha(p) for p in sorted(DEST.iterdir()) if p.is_file()}
save(DEST / "evidence.json", {"schema_version": 1, "status": "PASS", "evidence_root": DEST.relative_to(ROOT).as_posix(),
     "files_sha256": files, "external_outputs_sha256": {
         "art/cartoon/character-inventory-v1/inventory.json": result["inventory_after_sha256"],
         "art/cartoon/character-inventory-v1/README.md": result["readme_unchanged_sha256"]}})
assert all(sha(DEST / name) == digest for name, digest in files.items())
save(DEST / "readback.json", {"status": "PASS", "exact_copied_files": len(files),
                             "evidence_sha256": sha(DEST / "evidence.json")})
print("PASS preserved inventory refresh", len(files), sha(DEST / "evidence.json"), flush=True)
