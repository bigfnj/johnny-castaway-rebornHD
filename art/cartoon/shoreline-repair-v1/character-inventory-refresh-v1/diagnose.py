import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "art/cartoon/character-inventory-v1"
spec = importlib.util.spec_from_file_location("character_inventory", BASE / "build_inventory.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def diff(before, after, path=()):
    if isinstance(before, dict) and isinstance(after, dict) and before.keys() == after.keys():
        return [change for key in before for change in diff(before[key], after[key], (*path, key))]
    if isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        return [change for index, (a, b) in enumerate(zip(before, after)) for change in diff(a, b, (*path, index))]
    return [] if before == after else [{"path": list(path), "before": before, "after": after}]


old_bytes = (BASE / "inventory.json").read_bytes()
old = json.loads(old_bytes)
current, _pixels, _cartoon = module.build(ROOT)
new_bytes = module.encode(current)
changes = diff(old, current)
assert module.encode(old) == old_bytes, "old inventory must be exactly reconstructible from JSON delta"
recovered = json.loads(new_bytes)
for row in changes:
    item = recovered
    for part in row["path"][:-1]:
        item = item[part]
    item[row["path"][-1]] = row["before"]
assert module.encode(recovered) == old_bytes
changed_assets = [{"id": before["id"], "fields": [row for row in changes if row["path"][:2] == ["assets", index]]}
                  for index, before in enumerate(old["assets"]) if before != current["assets"][index]]
readme_before = (BASE / "README.md").read_bytes()
readme_after = module.markdown(current).encode()
pins = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in BASE.rglob("*") if p.is_file()
        and p.name not in ("inventory.json", "README.md")}
report = {"status": "DIAGNOSED", "inventory_before_sha256": sha(old_bytes), "inventory_after_sha256": sha(new_bytes),
          "old_summary": old["summary"], "new_summary": current["summary"],
          "readme_changes": readme_before != readme_after, "readme_sha256": sha(readme_before),
          "leaf_changes": changes, "changed_assets": changed_assets,
          "exact_old_inventory_recovered_by_reverse_delta": True, "preserved_input_sha256": pins}
(OUT / "diagnosis.json").write_bytes(module.encode(report))
(OUT / "expected-inventory.json").write_bytes(new_bytes)
print(json.dumps({"changed_assets": [a["id"] for a in changed_assets], "leaf_changes": len(changes),
                  "summary_changed": old["summary"] != current["summary"], "README_changed": readme_before != readme_after,
                  "before_sha256": sha(old_bytes), "after_sha256": sha(new_bytes)}, indent=2))
