"""Ordered maintained authoring verification; runs only isolated test mutations."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode())


def run(name, arguments, expected=0, witness=None):
    log = OUT / (name + ".log")
    assert not log.exists(), log
    command = [sys.executable, "-B", *arguments]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    output = process.stdout + process.stderr
    log.write_bytes(output.encode())
    print(name, process.returncode, output[-600:], flush=True)
    assert process.returncode == expected, (name, process.returncode)
    if witness:
        assert "WITNESS module " + witness in output and "Ran 1 test" in output, name
    if expected:
        assert "FAILED (failures=1)" in output, name
    counts = re.findall(r"Ran (\d+) tests?", output)
    return {"command": ["TOOLBOX_PYTHON", "-B", *arguments], "exit_code": process.returncode,
            "log": log.name, "sha256": sha(log), "tests": int(counts[-1]) if counts else None}


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("smoke", "regression", "controls"))
    parser.add_argument("--label")
    args = parser.parse_args()
    if args.label:
        OUT = OUT / args.label
        OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / (args.phase + ".json")
    assert not output.exists(), output
    pack = ROOT / "art/cartoon/pack.json"
    if args.phase != "controls":
        assert len(json.loads(pack.read_bytes())["assets"]) == 47, "final 47-asset pack must be ready"
    files = ["assets/scrantic_data.zip", "art/cartoon/pack.json", "tools/art_common.py", "tools/art_pack.py",
             "tools/art_inventory.py", "tools/art_production_catalog.py", "tools/art_review_metadata.py",
             "tests/test_art_tools.py", "tests/test_art_inventory.py", "tests/test_art_pilot_history.py",
             "tests/test_art_review_metadata.py", "tests/test_art_production_catalog.py", "tests/art_pilot_fixture.py"]
    pins = {name: sha(ROOT / name) for name in files}
    records = []
    if args.phase == "controls":
        source = ROOT / "tools/art_review_metadata.py"
        text = source.read_text(encoding="utf-8")
        cases = [("test_shoreline_replacement_must_be_declared", "set(replacements) == changed"),
                 ("test_shoreline_recipe_footprint_must_match_ledger", 'row.get("footprint") == item.get("footprint")')]
        for index, (case, condition) in enumerate(cases):
            assert text.count(condition) == 1, case
            mutant = OUT / ("mutant-" + str(index) + ".py")
            mutant.write_bytes(text.replace(condition, "True").encode())
            for label, path in (("positive", source), ("disabled", mutant), ("restored", source)):
                entry = run(case + "-" + label, ["tests/test_art_pilot_history.py", "--case", case,
                            "--module", str(path)], 1 if label == "disabled" else 0, sha(path))
                entry.update(case=case, variant=label, executed_source_sha256=sha(path))
                if label == "disabled":
                    data = (OUT / entry["log"]).read_text()
                    assert data.count("FAIL: " + case) == 1, case
                    assert "Expected named refusal:" in data, case
                records.append(entry)
    else:
        if args.phase == "regression":
            smoke = json.loads((OUT / "smoke.json").read_bytes())
            assert smoke["status"] == "PASS" and smoke["inputs"] == pins, "same inputs and smoke first"
        command = ["tests/test_art_tools.py"]
        if args.phase == "smoke":
            command += ["ArtToolsTests.test_named_island_footprints_preserve_original_catalog",
                        "ArtToolsTests.test_true_alpha_preserves_opaque_magenta_and_binary_control",
                        "ArtToolsTests.test_inventory_exports_unmodified_and_records_exact_aliases"]
        commands = [("pack", command + ["-v"]),
                    ("inventory", ["tests/test_art_inventory.py"] + (["--smoke"] if args.phase == "smoke" else []))]
        commands += [(name, ["tests/" + name + ".py", "--phase", args.phase]) for name in
                     ("test_art_pilot_history", "test_art_review_metadata", "test_art_production_catalog")]
        for name, command in commands:
            records.append(run(name + "-" + args.phase, command))
        if args.phase == "smoke":
            for name in ("art_review_metadata", "art_production_catalog"):
                records.append(run(name + "-generate", ["tools/" + name + ".py"]))
        else:
            for name in ("art_review_metadata", "art_production_catalog"):
                records.append(run(name + "-check", ["tools/" + name + ".py", "--check"]))
    assert pins == {name: sha(ROOT / name) for name in pins}, "protected inputs changed during authoring checks"
    save(output, {"status": "PASS", "phase": args.phase, "inputs": pins, "runs": records})
    print("PASS", args.phase, sum(row["tests"] or 0 for row in records), flush=True)


if __name__ == "__main__":
    main()
