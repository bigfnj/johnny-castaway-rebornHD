#!/usr/bin/env python3
"""Smoke, regression and executed mutations for explicit pilot replacements."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from art_pilot_fixture import legacy_pilot, promoted_pilot

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE = ROOT / "tools/art_review_metadata.py"
sys.path.insert(0, str(ROOT / "tools"))
ASSET = "BMP/JOHNWALK.BMP/024.png"
CONTROL = "BMP/JOHNWALK.BMP/029.png"
NEW = "art/cartoon/front-history-fixture/production-acceptance.json"
RECIPE = "art/cartoon/front-history-fixture/recipe.json"
OUTER = "art/cartoon/front-history-fixture/outer-acceptance.json"
# Independent expected geometry for the four accepted shoreline families.
SHORELINE = {0: ([640, 180], [-36, -10], "ground")}
SHORELINE.update({frame: ([150, 66], [-6, 0], "left-foam") for frame in (3, 4, 5)})
SHORELINE.update({frame: ([384, 256], [-32, -90], "center-foam") for frame in (6, 7, 8)})
SHORELINE.update({frame: ([154, 74], [0, 0], "right-foam") for frame in (9, 10, 11)})
m = None


def encoded(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def fixture():
    pack = json.loads((ROOT / m.PACK).read_bytes())
    previous = pack["acceptance_record"]
    row = next(item for item in pack["assets"] if item["path"] == ASSET)
    control = next(item for item in pack["assets"] if item["path"] == CONTROL)
    row.update(sha256=control["sha256"], recipe=RECIPE, review=NEW)
    recipe = copy.deepcopy(json.loads((ROOT / m.RECIPES[0]).read_bytes()))
    recipe["frames"] = [next(item for item in recipe["frames"] if item["path"] == ASSET)]
    recipe["frames"][0]["candidate_png_sha256"] = control["sha256"]
    recipe["required_assets"] = [ASSET]
    pack["acceptance_record"] = NEW
    pack["pilot_history"] = {"acceptance_record": m.ACCEPTANCE,
        "sha256": m.digest((ROOT / m.ACCEPTANCE).read_bytes()), "replaced_assets": [ASSET]}
    accepted = {"accepted": True, "accepted_assets": [
        {key: item[key] for key in ("path", "sha256", "recipe")} for item in pack["assets"]],
        "inherited_acceptances": [{"path": previous, "sha256": m.digest((ROOT / previous).read_bytes()),
            "asset_paths": [item["path"] for item in pack["assets"] if item["path"] != ASSET]}],
        "newly_accepted_assets": [ASSET]}
    return {m.PACK: pack, NEW: accepted, RECIPE: recipe}


def shoreline_fixture():
    """Replace ten shore slots and six Johnny approvals without touching history."""
    from test_art_tools import png
    images = {"data/styles/cartoon/BMP/BACKGRND.BMP/" + f"{frame:03}.png": png(*shape)
              for frame, (shape, _offset, _kind) in SHORELINE.items()}

    def change(records):
        pack, accepted, recipe = records[m.PACK], records[NEW], records[RECIPE]
        walk_rows = json.loads((ROOT / m.RECIPES[0]).read_bytes())["frames"]
        frames = {row["path"]: copy.deepcopy(row) for row in walk_rows}
        frames[ASSET] = recipe["frames"][0]
        for frame, (shape, offset, kind) in SHORELINE.items():
            path = f"BMP/BACKGRND.BMP/{frame:03}.png"
            footprint = {"id": "cartoon-island-" + kind + "-v1", "canvas": list(shape), "offset_hd": list(offset)}
            frames[path] = {"path": path, "candidate_png_sha256": m.digest(images["data/styles/cartoon/" + path]),
                            "runtime_canvas": shape, "footprint": footprint}
        for item in pack["assets"]:
            if item["path"] in frames:
                frame = frames[item["path"]]
                item.update(sha256=frame["candidate_png_sha256"], recipe=RECIPE, review=NEW)
                if "footprint" in frame:
                    item["footprint"] = copy.deepcopy(frame["footprint"])
        for item in accepted["accepted_assets"]:
            if item["path"] in frames:
                item.update(sha256=frames[item["path"]]["candidate_png_sha256"], recipe=RECIPE)
        selected = sorted(frames)
        pack["pilot_history"]["replaced_assets"] = list(selected)
        accepted["newly_accepted_assets"] = list(selected)
        accepted["inherited_acceptances"][0]["asset_paths"] = [row["path"] for row in pack["assets"]
                                                              if row["path"] not in frames]
        recipe["frames"] = list(frames.values())
        recipe["required_assets"] = selected

    return change, images


class HistoryTests(unittest.TestCase):
    def valid_report(self, *args, **kwargs):
        try:
            return self.report(*args, **kwargs)
        except m.ArtError as caught:
            self.fail("Valid replacement fixture rejected: " + str(caught))

    def report(self, change=None, replace_png=True, extra_pngs=None):
        with legacy_pilot(ROOT):
            return self.fixture_report(change, replace_png, extra_pngs)

    def fixture_report(self, change=None, replace_png=True, extra_pngs=None):
        records = fixture()
        if change:
            change(records)
        read_file, read_zip = Path.read_bytes, zipfile.ZipFile.read

        def file_bytes(path):
            relative = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else ""
            return encoded(records[relative]) if relative in records else read_file(path)

        def zip_bytes(archive, name, *args, **kwargs):
            if extra_pngs and name in extra_pngs:
                return extra_pngs[name]
            if replace_png and name == "data/styles/cartoon/" + ASSET:
                name = "data/styles/cartoon/" + CONTROL
            return read_zip(archive, name, *args, **kwargs)

        with patch.object(Path, "read_bytes", file_bytes), patch.object(zipfile.ZipFile, "read", zip_bytes):
            return m.build(ROOT)

    def refused(self, change, label, reason, **kwargs):
        try:
            self.report(change, **kwargs)
        except Exception as caught:
            self.assertIsInstance(caught, m.ArtError)
            self.assertEqual(str(caught), label + ": " + reason)
        else:
            self.fail("Expected named refusal: " + label + ": " + reason)

    def test_smoke_replacement(self):
        result = self.valid_report()
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["summary"], {"assets": 21, "walking_assets": 6, "island_assets": 15})
        self.assertEqual(result["production_summary"], {"retained": 20, "replaced": 1})
        row = next(item for item in result["assets"] if item["id"] == ASSET[:-4])
        self.assertEqual(row["production"]["acceptance"], NEW)
        self.assertNotEqual(row["variant"]["sha256"], row["production"]["sha256"])
        self.assertIsNone(row["variant"]["member"])

    def test_smoke_extended_island_keeps_historical_canvas(self):
        from test_art_tools import png
        ground = "BMP/BACKGRND.BMP/000.png"
        footprint = {"id": "cartoon-island-ground-v1", "canvas": [640, 180], "offset_hd": [-36, -10]}
        data = png(640, 180)
        with legacy_pilot(ROOT):
            before = m.build(ROOT)
        def change(records):
            pack, accepted = records[m.PACK], records[NEW]
            row = next(row for row in pack["assets"] if row["path"] == ground)
            row.update(sha256=m.digest(data), recipe=RECIPE, review=NEW, footprint=copy.deepcopy(footprint))
            pack["pilot_history"]["replaced_assets"].append(ground)
            approval = next(row for row in accepted["accepted_assets"] if row["path"] == ground)
            approval.update(sha256=m.digest(data), recipe=RECIPE)
            accepted["inherited_acceptances"][0]["asset_paths"].remove(ground)
            accepted["newly_accepted_assets"].append(ground)
            records[RECIPE]["frames"].append({"path": ground, "candidate_png_sha256": m.digest(data),
                "runtime_canvas": [640, 180], "footprint": copy.deepcopy(footprint)})
        after = self.valid_report(change, extra_pngs={"data/styles/cartoon/" + ground: data})
        previous = next(row for row in before["assets"] if row["id"] == ground[:-4])
        current = next(row for row in after["assets"] if row["id"] == ground[:-4])
        self.assertEqual(current["original"], previous["original"])
        self.assertEqual(current["variant"]["canvas"], [560, 104])
        self.assertEqual(current["production"]["canvas"], [640, 180])
        self.assertEqual(current["production"]["footprint"], footprint)
        self.assertFalse(current["production"]["canvas_matches_original_at_scale"])
        self.assertIn("Historical pilot canvases", m.markdown(after))

    def test_history_and_original_facts_unchanged(self):
        with legacy_pilot(ROOT):
            before = m.build(ROOT)
        fingerprints = {path: m.digest((ROOT / path).read_bytes()) for path, facts in before["evidence"].items()
                        if facts["hash_basis"] == "file-bytes"}
        after = self.valid_report()
        self.assertEqual(after["historical_pilot_human_review"], before["current_human_review"])
        self.assertNotIn("current_human_review", after)
        self.assertEqual(after["historical_pilot_acceptance_record"], m.ACCEPTANCE)
        self.assertEqual(after["current_acceptance_record"], NEW)
        for original, current in zip(before["assets"], after["assets"]):
            self.assertEqual(original["original"], current["original"])
            expected = copy.deepcopy(original["variant"])
            expected["production_status"] = current["production"]["status"]
            if current["production"]["status"] == "replaced":
                expected["member"] = None
            self.assertEqual(expected, current["variant"])
            self.assertEqual(original["comparison"]["current_user_review_ids"],
                             current["comparison"]["historical_user_review_ids"])
        self.assertEqual(fingerprints, {path: m.digest((ROOT / path).read_bytes()) for path in fingerprints})

    def test_smoke_all_shoreline_replacements_keep_history(self):
        with legacy_pilot(ROOT):
            before = m.build(ROOT)
        change, images = shoreline_fixture()
        after = self.valid_report(change, extra_pngs=images)
        self.assertEqual(after["production_summary"], {"retained": 5, "replaced": 16})
        self.assertEqual(after["historical_pilot_human_review"], before["current_human_review"])
        for prior, current in zip(before["assets"], after["assets"]):
            self.assertEqual(prior["original"], current["original"])
            self.assertEqual(prior["variant"]["canvas"], current["variant"]["canvas"])
            self.assertEqual(prior["variant"]["registration"], current["variant"]["registration"])
            if current["id"].startswith("BMP/BACKGRND.BMP/") and int(current["id"][-3:]) in SHORELINE:
                shape, offset, kind = SHORELINE[int(current["id"][-3:])]
                self.assertEqual(current["production"]["canvas"], shape)
                self.assertEqual(current["production"]["footprint"],
                                 {"id": "cartoon-island-" + kind + "-v1", "canvas": shape, "offset_hd": offset})
                self.assertEqual(current["production"]["acceptance"], NEW)
                self.assertIsNone(current["variant"]["member"])

    def test_shoreline_replacement_must_be_declared(self):
        change, images = shoreline_fixture()
        def damaged(records):
            change(records)
            records[m.PACK]["pilot_history"]["replaced_assets"].remove("BMP/BACKGRND.BMP/007.png")
        self.refused(damaged, m.PACK, "declared pilot replacements differ from active approvals", extra_pngs=images)
        self.assertEqual(self.valid_report(change, extra_pngs=images)["production_summary"]["replaced"], 16)

    def test_shoreline_recipe_footprint_must_match_ledger(self):
        change, images = shoreline_fixture()
        path = "BMP/BACKGRND.BMP/007.png"
        def damaged(records):
            change(records)
            row = next(row for row in records[RECIPE]["frames"] if row["path"] == path)
            row["footprint"]["offset_hd"][0] += 1
        self.refused(damaged, path, "active recipe footprint differs from ledger", extra_pngs=images)
        self.assertEqual(self.valid_report(change, extra_pngs=images)["production_summary"]["replaced"], 16)

    def test_nested_selected_approval(self):
        def change(records):
            records[OUTER] = {"accepted": True, "accepted_assets": copy.deepcopy(records[NEW]["accepted_assets"]),
                "newly_accepted_assets": [], "inherited_acceptances": [{"path": NEW,
                    "sha256": m.digest(encoded(records[NEW])),
                    "asset_paths": [item["path"] for item in records[NEW]["accepted_assets"]]}]}
            records[m.PACK]["acceptance_record"] = OUTER
        result = self.valid_report(change)
        self.assertEqual(result["current_acceptance_record"], OUTER)
        row = next(item for item in result["assets"] if item["id"] == ASSET[:-4])
        self.assertEqual(row["production"]["acceptance"], NEW)
        self.assertEqual(result["evidence"][NEW]["hash_basis"], "file-bytes")

    def test_new_review_of_unchanged_pixels_is_explicit(self):
        def change(records):
            old = json.loads((ROOT / m.ACCEPTANCE).read_bytes())
            prior = next(item for item in old["accepted_assets"] if item["path"] == ASSET)
            next(item for item in records[m.PACK]["assets"] if item["path"] == ASSET).update(prior)
            next(item for item in records[NEW]["accepted_assets"] if item["path"] == ASSET).update(prior)
        result = self.valid_report(change, replace_png=False)
        row = next(item for item in result["assets"] if item["id"] == ASSET[:-4])
        self.assertEqual(row["variant"]["sha256"], row["production"]["sha256"])
        self.assertEqual(row["production"]["status"], "replaced")
        self.assertEqual(row["production"]["acceptance"], NEW)

    def test_all_pilot_slots_can_preserve_history_without_inheritance(self):
        def change(records):
            pilot = json.loads((ROOT / m.ACCEPTANCE).read_bytes())
            paths = {item["path"] for item in pilot["accepted_assets"]}
            records[m.PACK]["pilot_history"]["replaced_assets"] = sorted(paths)
            records[NEW]["newly_accepted_assets"] = sorted(paths)
            records[NEW]["inherited_acceptances"][0]["asset_paths"] = [
                path for path in records[NEW]["inherited_acceptances"][0]["asset_paths"] if path not in paths]
            for item in records[m.PACK]["assets"]:
                if item["path"] in paths:
                    item["review"] = NEW
        result = self.valid_report(change)
        self.assertEqual(result["production_summary"], {"retained": 0, "replaced": 21})
        self.assertEqual(result["historical_pilot_acceptance_record"], m.ACCEPTANCE)

    def test_declaration_shape(self):
        self.refused(lambda d: d[m.PACK].update(pilot_history=[]), m.PACK, "invalid pilot history declaration")

    def test_history_identity(self):
        self.refused(lambda d: d[m.PACK]["pilot_history"].update(sha256="0" * 64),
                     m.PACK, "historical pilot acceptance identity differs")

    def test_history_pointer(self):
        self.refused(lambda d: d[m.PACK]["pilot_history"].update(acceptance_record=NEW),
                     m.PACK, "historical pilot acceptance identity differs")

    def test_replacement_list(self):
        self.refused(lambda d: d[m.PACK]["pilot_history"].update(replaced_assets=[ASSET, ASSET]),
                     m.PACK, "invalid replaced pilot asset list")

    def test_missing_active_pointer(self):
        self.refused(lambda d: d[m.PACK].pop("acceptance_record"), m.PACK, "active acceptance pointer differs")

    def test_pending_replacement(self):
        self.refused(lambda d: d[NEW].update(accepted=False), NEW, "active production acceptance is pending")

    def test_unapproved_replacement(self):
        self.refused(lambda d: d[NEW]["accepted_assets"].pop(), NEW, "acceptance coverage differs from production")

    def test_undeclared_replacement(self):
        self.refused(lambda d: d[m.PACK]["pilot_history"].update(replaced_assets=[]),
                     m.PACK, "declared pilot replacements differ from active approvals")

    def test_false_replacement(self):
        self.refused(lambda d: d[m.PACK]["pilot_history"]["replaced_assets"].append(CONTROL),
                     m.PACK, "declared pilot replacements differ from active approvals")

    def test_recipe_pointer(self):
        def change(records):
            next(item for item in records[m.PACK]["assets"] if item["path"] == ASSET)["recipe"] = m.RECIPES[0]
        self.refused(change, ASSET, "active recipe or acceptance pointer differs")

    def test_review_pointer(self):
        def change(records):
            next(item for item in records[m.PACK]["assets"] if item["path"] == ASSET)["review"] = m.ACCEPTANCE
        self.refused(change, ASSET, "active recipe or acceptance pointer differs")

    def test_recipe_coverage(self):
        self.refused(lambda d: d[RECIPE].update(frames=[]), ASSET, "asset is absent from referenced recipe")

    def test_recipe_hash(self):
        self.refused(lambda d: d[RECIPE]["frames"][0].update(candidate_png_sha256="0" * 64),
                     ASSET, "accepted PNG hashes differ")

    def test_recipe_canvas(self):
        self.refused(lambda d: d[RECIPE]["frames"][0].update(runtime_canvas=[64, 148]),
                     ASSET, "active recipe canvas differs from original or declared footprint")

    def test_recipe_footprint(self):
        self.refused(lambda d: d[RECIPE]["frames"][0].update(footprint={"id": "unapproved"}),
                     ASSET, "active recipe footprint differs from ledger")

    def test_production_bytes(self):
        self.refused(None, "data/styles/cartoon/" + ASSET, "production PNG hash differs", replace_png=False)

    def test_shared_inheritance_hash_guard(self):
        self.refused(lambda d: d[NEW]["inherited_acceptances"][0].update(sha256="0" * 64),
                     m.ACCEPTANCE, "inherited acceptance file hash differs")

    def test_schema2_deviations_are_historical(self):
        report = self.valid_report()
        self.assertNotIn("Current displayed foot lift", " ".join(report["limits"]))
        self.assertIn("historical Calm focus pilot", " ".join(report["limits"]))
        for row in report["assets"]:
            clearance = row["comparison"]["recorded_deviations"].get("rear_foot_clearance_hd")
            if clearance:
                self.assertNotIn("current_disposition", clearance)
                self.assertNotIn("current_variant_independently_remeasured", clearance)
                self.assertIn("historical_pilot_disposition", clearance)
                self.assertIs(clearance["historical_pilot_variant_independently_remeasured"], False)

    def test_both_suites_after_future_promotion(self):
        # Exercise the entire historical test surface against an ambient live
        # schema2 pack, including its regenerated output. The fixture remains
        # independent of production and no real pack or artwork is changed.
        import test_art_review_metadata as historical
        historical.m = m
        with promoted_pilot(ROOT, m) as future:
            self.assertEqual(future["schema_version"], 2)
            self.assertIn("BMP/JOHNWALK.BMP/028.png", future["pilot_history"]["replaced_assets"])
            self.assertNotIn("current_human_review", future)
            tests = [historical.MetadataTests(name) for name in
                     unittest.defaultTestLoader.getTestCaseNames(historical.MetadataTests)]
            tests += [HistoryTests(name) for name in unittest.defaultTestLoader.getTestCaseNames(HistoryTests)
                      if name != "test_both_suites_after_future_promotion"]
            result = unittest.TestResult()
            unittest.TestSuite(tests).run(result)
        failures = result.failures + result.errors
        self.assertEqual(failures, [], "Future promotion broke a historical test: " +
                         "\n".join(str(test) + "\n" + reason for test, reason in failures))
        self.assertEqual(result.testsRun, len(tests))
        print(f"PASS future028 promotion: {result.testsRun} historical and replacement tests", flush=True)


MUTATIONS = [
    ("test_declaration_shape", 'isinstance(declaration, dict)'),
    ("test_history_identity", 'declaration.get("sha256") == record_hash(ACCEPTANCE)'),
    ("test_replacement_list", 'len(replacements) == len(set(replacements))'),
    ("test_pending_replacement", 'isinstance(current, dict) and current.get("accepted") is True'),
    ("test_unapproved_replacement", 'set(approved) == set(packed)'),
    ("test_undeclared_replacement", 'set(replacements) == changed'),
    ("test_shoreline_replacement_must_be_declared", 'set(replacements) == changed'),
    ("test_recipe_pointer", 'isinstance(recipe_path, str) and recipe_path == approval.get("recipe")\n                and item.get("review") == origins[path]'),
    ("test_recipe_coverage", 'row is not None'),
    ("test_recipe_hash", 'item.get("sha256") == approval.get("sha256") == row.get("candidate_png_sha256")'),
    ("test_recipe_canvas", 'production[asset]["canvas"] == current_canvas'),
    ("test_recipe_footprint", 'row.get("footprint") == item.get("footprint")'),
    ("test_shoreline_recipe_footprint_must_match_ledger", 'row.get("footprint") == item.get("footprint")'),
    ("test_production_bytes", 'digest(data) == production_item["sha256"]'),
    ("test_history_and_original_facts_unchanged", 'item = dict(item, **approved[asset], review=ACCEPTANCE)', 'item = item'),
    ("test_smoke_replacement", 'assets[-1]["variant"]["member"] = None', 'pass'),
    ("test_schema2_deviations_are_historical", 'clearance["historical_pilot_disposition"] = clearance.pop("current_disposition")', 'pass'),
]


def mutations():
    source = DEFAULT_MODULE.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as temporary:
        for index, (case, condition, *replacement) in enumerate(MUTATIONS):
            if source.count(condition) != 1:
                raise RuntimeError(f"{case}: ambiguous mutation condition")
            mutant = Path(temporary) / f"history-mutant-{index}.py"
            mutant.write_text(source.replace(condition, replacement[0] if replacement else "True"), encoding="utf-8")
            witness = hashlib.sha256(mutant.read_bytes()).hexdigest()
            run = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--case", case,
                                  "--module", str(mutant)], capture_output=True, text=True)
            output = run.stdout + run.stderr
            if not (run.returncode == 1 and "WITNESS module " + witness in output and case in output
                    and "Ran 1 test" in output and "FAILED (failures=1)" in output):
                raise RuntimeError(f"{case}: mutation did not produce exactly one witnessed failure\n{output}")
            print(f"FIRED {case} source={witness}")
    print(f"PASS pilot history mutations {len(MUTATIONS)}/{len(MUTATIONS)}")


def main():
    global m
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("smoke", "regression"), default="smoke")
    parser.add_argument("--module", type=Path, default=DEFAULT_MODULE)
    parser.add_argument("--case")
    parser.add_argument("--mutation-check", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("history_metadata", args.module)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("WITNESS module " + hashlib.sha256(args.module.read_bytes()).hexdigest(), flush=True)
    names = [args.case] if args.case else [name for name in unittest.defaultTestLoader.getTestCaseNames(HistoryTests)
        if name.startswith("test_smoke") == (args.phase == "smoke")]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(HistoryTests(name) for name in names))
    if not result.wasSuccessful():
        return 1
    if args.mutation_check:
        mutations()
    return 0


if __name__ == "__main__":
    sys.exit(main())
