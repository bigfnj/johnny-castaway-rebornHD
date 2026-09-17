import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "art/cartoon/character-inventory-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode())


protected = {p.relative_to(ROOT).as_posix(): sha(p) for p in BASE.rglob("*") if p.is_file()
             and p not in (BASE / "inventory.json", BASE / "README.md")}
protected.update({name: sha(ROOT / name) for name in ("assets/scrantic_data.zip", "art/cartoon/pack.json",
                  "tools/art_production_catalog.py", "tools/art_common.py", "tools/art_review_metadata.py")})
readme = (BASE / "README.md").read_bytes()
diagnosis = json.loads((OUT / "diagnosis.json").read_bytes())
assert sha(BASE / "inventory.json") == diagnosis["inventory_before_sha256"]
assert not (OUT / "verification.json").exists()
commands = [("stale-check", ["art/cartoon/character-inventory-v1/build_inventory.py", "--check"], 1),
            ("regenerate", ["art/cartoon/character-inventory-v1/build_inventory.py"], 0)]
for phase in ("smoke", "regression"):
    commands.append((phase, ["art/cartoon/character-inventory-v1/test_inventory.py", "--phase", phase,
                            "--work", str(OUT / phase), "--report", str(OUT / (phase + ".json"))], 0))
commands.append(("final-check", ["art/cartoon/character-inventory-v1/build_inventory.py", "--check"], 0))
runs = []
for name, arguments, expected in commands:
    result = subprocess.run([sys.executable, "-B", *arguments], cwd=ROOT, capture_output=True, text=True)
    path = OUT / (name + ".log")
    assert not path.exists(), path
    path.write_bytes((result.stdout + result.stderr).encode())
    print(name, result.returncode, result.stdout[-300:], result.stderr[-300:], flush=True)
    assert result.returncode == expected, name
    if name == "stale-check":
        assert result.stderr.strip() == "ERROR inventory.json: generated inventory differs"
    runs.append({"command": ["TOOLBOX_PYTHON", "-B", *arguments], "expected_exit_code": expected,
                 "exit_code": result.returncode, "log": path.name, "sha256": sha(path)})
assert (BASE / "inventory.json").read_bytes() == (OUT / "expected-inventory.json").read_bytes()
assert (BASE / "README.md").read_bytes() == readme
assert all(sha(ROOT / name) == checksum for name, checksum in protected.items())
regression = json.loads((OUT / "regression.json").read_bytes())
assert regression["status"] == "PASS"
save(OUT / "verification.json", {"status": "PASS", "diagnosis_sha256": sha(OUT / "diagnosis.json"),
     "inventory_before_sha256": diagnosis["inventory_before_sha256"],
     "inventory_after_sha256": sha(BASE / "inventory.json"), "readme_unchanged_sha256": sha(BASE / "README.md"),
     "changed_leaf_count": len(diagnosis["leaf_changes"]), "changed_assets": [r["id"] for r in diagnosis["changed_assets"]],
     "character_summary_unchanged": diagnosis["old_summary"] == diagnosis["new_summary"],
     "negative_controls_fired": regression["negative_controls_fired"], "source_mutation": regression["mutation_check"],
     "protected_files_sha256": protected, "protected_files_unchanged": True, "runs": runs})
print("PASS refresh", sha(OUT / "verification.json"), flush=True)
