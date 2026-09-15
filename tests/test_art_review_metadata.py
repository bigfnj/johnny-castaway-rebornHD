"""Original-first review catalog smoke, regression and executed-source mutants."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
DEFAULT_MODULE = ROOT / "tools/art_review_metadata.py"
m = None


def load_module(path):
    spec = importlib.util.spec_from_file_location("review_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_xpm(rows=("01", "10"), zero="a800a8", one="102030"):
    palette = [zero, one] + ["123456"] * 14
    strings = [f"{len(rows[0])} {len(rows)} 16 1"]
    strings += [f"{i:x} c #{color}" for i, color in enumerate(palette)]
    strings += list(rows)
    return ("/* XPM */\nstatic char * x[] = {\n" + ",\n".join('"' + x + '"' for x in strings) + "}\n").encode()


class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global m
        if m is None:
            m = load_module(DEFAULT_MODULE)

    def report(self, mutate=None):
        original_read = m.read_json

        def changed(data, label):
            value = original_read(data, label)
            if mutate:
                mutate(label, value)
            return value

        with patch.object(m, "read_json", side_effect=changed):
            return m.build(ROOT)

    def refused(self, callback, label, reason):
        try:
            callback()
        except Exception as caught:
            self.assertIsInstance(caught, m.ArtError)
            self.assertEqual(str(caught), label + ": " + reason)
        else:
            self.fail("Expected named refusal: " + label + ": " + reason)

    def test_smoke_pilot(self):
        result = self.report()
        self.assertEqual(result["summary"], {"assets": 21, "walking_assets": 6, "island_assets": 15})
        self.assertEqual(len(result["motion"]["route"]), 23)
        self.assertEqual(result["motion"]["route"][-2]["frame"], 25)
        self.assertEqual(result["motion"]["route"][-1]["frame"], 27)
        self.assertEqual(result["motion"]["travel_logical_xy"], [-94, 30])

    def test_smoke_original_pixels(self):
        reference = m.read_json((ROOT / m.ORIGINAL).read_bytes(), m.ORIGINAL)
        self.assertEqual(len(reference["assets"]), 21)
        self.assertFalse(reference["original_executable_render_parity"])
        self.assertEqual(reference["assets"]["BMP/JOHNWALK.BMP/024.png"]["canvas"], [32, 75])
        self.assertEqual(reference["assets"]["SCR/OCEAN02.SCR.png"]["transparent_index"], None)

    def test_reproduction_and_classification(self):
        result = self.report()
        self.assertEqual(json.loads((ROOT / (m.OUTPUT + ".json")).read_text()), result)
        self.assertEqual((ROOT / (m.OUTPUT + ".md")).read_text(), m.markdown(result))
        self.assertFalse(result["motion"]["original_executable_timing_verified"])
        self.assertEqual({x["comparison"]["artistic_fidelity"] for x in result["assets"]}, {"unverified-by-this-tool"})
        self.assertEqual(sum(bool(x["comparison"]["recorded_deviations"]) for x in result["assets"]), 9)
        self.assertEqual([x["frame"] for x in result["current_human_review"]["observations"]], [24, 28, 29])
        self.assertTrue(result["current_human_review"]["not_automatically_verified"])
        self.assertEqual(result["current_acceptance_record"], m.ACCEPTANCE)
        self.assertEqual(result["current_human_review"]["awaiting_human_decision"], [])
        self.assertEqual(result["current_human_review"]["accepted_retained_differences"][0]["frames"], [26, 27])
        self.assertEqual([x["status"] for x in result["current_human_review"]["observations"]],
                         ["accepted-as-displayed", "accepted-as-displayed-with-known-leg-difference",
                          "accepted-as-displayed-with-known-leg-difference"])
        self.assertEqual(result["motion"]["historical_route_acceptance"], m.ROUTE_ACCEPTANCE)
        self.assertEqual(result["motion"]["historical_capture_evidence"], m.TIMING)
        for asset in result["assets"]:
            if asset["family"] == "walk-e-to-a":
                self.assertEqual(asset["variant"]["recipe"], m.WALK + "/recipe.json")
                self.assertEqual(asset["variant"]["acceptance"], m.ACCEPTANCE)
                if asset["original"]["frame_index"] in (26, 27):
                    clearance = asset["comparison"]["recorded_deviations"]["rear_foot_clearance_hd"]
                    self.assertEqual(clearance["measured_variant_recipe"], m.HISTORICAL_WALK + "/recipe.json")
                    self.assertFalse(clearance["current_variant_independently_remeasured"])

    def test_newline_normalization_varies(self):
        baseline = self.report()
        read = Path.read_bytes
        for target, should_normalize in [(m.ORIGINAL, True), (m.PACK, True), (m.RECIPES[0], False)]:
            def changed(path):
                data = read(path)
                if path != ROOT / target:
                    return data
                return data.replace(b"\r\n", b"\n") if b"\r\n" in data else data.replace(b"\n", b"\r\n")
            with patch.object(Path, "read_bytes", changed):
                result = self.report()
            if should_normalize:
                self.assertEqual(result, baseline)
            else:
                self.assertNotEqual(result["evidence"][target], baseline["evidence"][target])
        self.assertEqual(m.text_fingerprint(b"abc\n"), m.text_fingerprint(b"abc\r\n"))
        self.assertEqual(m.text_fingerprint(b"abc\n"), m.text_fingerprint(b"abc\r"))
        for changed in (b"\xef\xbb\xbfabc\n", b"abc \n", b"abc\n\n"):
            self.assertNotEqual(m.text_fingerprint(b"abc\n"), m.text_fingerprint(changed))

    def test_actual_git_checkout_and_rule_mutations(self):
        paths = [m.OUTPUT + ".json", m.OUTPUT + ".md", m.ORIGINAL]
        attributes = (ROOT / ".gitattributes").read_text()
        version = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True).stdout.strip()

        def checkout(rules):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                def git(*args):
                    return subprocess.run(["git", "-C", str(root), "-c", "core.autocrlf=true",
                        "-c", "core.safecrlf=false", *args], capture_output=True, check=True)
                git("init", "--quiet")
                (root / ".gitattributes").write_text(rules, encoding="utf-8", newline="\n")
                expected = {}
                for path in paths:
                    expected[path] = (ROOT / path).read_bytes()
                    self.assertNotIn(b"\r", expected[path])
                    (root / path).parent.mkdir(parents=True, exist_ok=True)
                    (root / path).write_bytes(expected[path])
                (root / "control.txt").write_bytes(b"control\n")
                git("add", "--", ".gitattributes", "control.txt", *paths)
                dest = root / "checkout"
                self.assertFalse(dest.exists())
                git("checkout-index", "--all", "--prefix=" + dest.as_posix() + "/")
                self.assertEqual((dest / "control.txt").read_bytes(), b"control\r\n")
                return [path for path in paths if (dest / path).read_bytes() != expected[path]]

        self.assertEqual(checkout(attributes), [])
        for path in paths:
            rule = path + " text eol=lf"
            self.assertEqual(attributes.count(rule), 1)
            changed = checkout(attributes.replace(rule, "# deliberately disabled " + path))
            self.assertEqual(changed, [path], "Wrong or multiple changed files from isolated LF-rule mutation")
            print("FIRED Git LF rule " + path + " via " + version, flush=True)

    def test_arrival_acceptance_raw_bytes(self):
        active = "art/cartoon/arrival-pilot-v1/production-acceptance.json"
        pilot = json.loads((ROOT / m.ACCEPTANCE).read_bytes())
        link = {"path": m.ACCEPTANCE,
                "sha256": hashlib.sha256((ROOT / m.ACCEPTANCE).read_bytes()).hexdigest(),
                "asset_paths": [row["path"] for row in pilot["accepted_assets"]]}
        # The pilot checks its direct inherited21; the full catalog owns the
        # additional rear/arrival approvals. Use real build() I/O with valid
        # immutable acceptance bytes in each newline form, without changing art.
        value = {"accepted": True, "inherited_acceptances": [link]}
        lf = (json.dumps(value, indent=2) + "\n").encode("utf-8")
        forms = {"LF": lf, "CRLF": lf.replace(b"\n", b"\r\n"), "CR": lf.replace(b"\n", b"\r")}
        read = Path.read_bytes
        results = {}
        for name, raw in forms.items():
            def changed(path):
                return raw if path == ROOT / active else read(path)
            def choose(label, record):
                if label == m.PACK:
                    record["acceptance_record"] = active
            with patch.object(Path, "read_bytes", changed):
                results[name] = self.report(choose)
        self.assertNotEqual(forms["LF"], forms["CRLF"])
        self.assertEqual(results["CRLF"]["evidence"][active]["sha256"],
                         hashlib.sha256(forms["CRLF"]).hexdigest(),
                         active + ": preserve exact immutable acceptance bytes")
        self.assertEqual(len({result["evidence"][active]["sha256"] for result in results.values()}), 3)
        for name, result in results.items():
            self.assertEqual(result["evidence"][active],
                             {"sha256": hashlib.sha256(forms[name]).hexdigest(), "hash_basis": "file-bytes"})
            self.assertEqual(result["assets"], results["LF"]["assets"])
            self.assertEqual(result["summary"], {"assets": 21, "walking_assets": 6, "island_assets": 15})

    def test_transparency_normalization_varies(self):
        # Same hidden RGB change is ignored for sprites but retained for screens.
        a, b = fixture_xpm(), fixture_xpm(zero="ff00ff")
        self.assertNotEqual(m.xpm_facts(a, "a", True)["xpm_sha256"], m.xpm_facts(b, "b", True)["xpm_sha256"])
        self.assertEqual(m.xpm_facts(a, "a", True)["rgba_sha256"], m.xpm_facts(b, "b", True)["rgba_sha256"])
        self.assertNotEqual(m.xpm_facts(a, "a", False)["rgba_sha256"], m.xpm_facts(b, "b", False)["rgba_sha256"])
        self.assertNotEqual(m.xpm_facts(a, "a", True)["rgba_sha256"], m.xpm_facts(fixture_xpm(one="123456"), "c", True)["rgba_sha256"])
        self.assertEqual(m.xpm_facts(fixture_xpm(("000", "010")), "bounds", True)["visible_bounds_exclusive"], [1, 1, 2, 2])
        self.assertIsNone(m.xpm_facts(fixture_xpm(("00",)), "blank", True)["visible_bounds_exclusive"])
        self.assertEqual(m.xpm_facts(fixture_xpm(("00",)), "opaque", False)["visible_bounds_exclusive"], [0, 0, 2, 1])

    def test_coordinate_normalization_varies(self):
        for scale, raw, target in [(1, [0, 0], [0, 0]), (.1, [385, 42], [17.5, .25]),
                                   (.25, [13, 29], [-2, 4]), (2, [3, 5], [10, 20])]:
            row = {"runtime_canvas": [80, 140], "cap_raw": raw, "cap_target_hd": target,
                   "affine_forward": [scale, 0, target[0] - scale * raw[0], 0, scale, target[1] - scale * raw[1]]}
            recipe = {"scale_exact": {"numerator": scale, "denominator": 1}}
            try:
                actual = m.registration(row, recipe, "control")
            except m.ArtError as exc:
                self.fail("Valid coordinate control was rejected: " + str(exc))
            self.assertEqual(actual["landmark_residual_hd"], [0, 0])
        full = {"runtime_canvas": [6, 4], "generated_canvas": [3, 2],
                "transform_kind": "opaque_resize", "scale_exact": {"numerator": 2, "denominator": 1}}
        self.assertIsNone(m.registration(full, {}, "full")["landmark_residual_hd"])

    def test_duplicate_identity(self):
        self.refused(lambda: m.keyed([{"path": "x"}, {"path": "x"}], "path", "fixture"), "fixture", "duplicate identity")

    def test_nonuniform_transform(self):
        row = {"runtime_canvas": [2, 2], "affine_forward": [1, 0, 0, 0, 2, 0],
               "cap_raw": [0, 0], "cap_target_hd": [0, 0]}
        self.refused(lambda: m.registration(row, {"scale_exact": {"numerator": 1, "denominator": 1}}, "frame"),
                     "frame", "transform is not the declared uniform scale and translation")

    def test_landmark_mismatch(self):
        row = {"runtime_canvas": [2, 2], "affine_forward": [1, 0, 1, 0, 1, 0],
               "cap_raw": [0, 0], "cap_target_hd": [0, 0]}
        self.refused(lambda: m.registration(row, {"scale_exact": {"numerator": 1, "denominator": 1}}, "frame"),
                     "frame", "recorded landmark does not map to target")

    def test_resize_mismatch(self):
        row = {"runtime_canvas": [6, 5], "generated_canvas": [3, 2], "transform_kind": "opaque_resize",
               "scale_exact": {"numerator": 2, "denominator": 1}}
        self.refused(lambda: m.registration(row, {}, "screen"), "screen", "nonuniform full-canvas resize")

    def test_canvas_mismatch(self):
        def mutate(label, value):
            if label == m.RECIPES[0]:
                value["frames"][0]["runtime_canvas"][0] += 2
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "recipe canvas differs from original")

    def test_original_canvas_mismatch(self):
        def mutate(label, value):
            if label == m.ORIGINAL:
                value["assets"]["BMP/JOHNWALK.BMP/024.png"]["canvas"][0] += 1
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "supplied original canvas differs from bundled resource")

    def test_acceptance_mismatch(self):
        def mutate(label, value):
            if label == m.ACCEPTANCE:
                value["accepted_assets"][0]["sha256"] = "0" * 64
        self.refused(lambda: self.report(mutate), "BMP/BACKGRND.BMP/000.png", "acceptance hash differs")

    def test_active_acceptance_pointer(self):
        def mutate(label, value):
            if label == m.PACK:
                value["acceptance_record"] = m.ISLAND + "/acceptance.json"
        self.refused(lambda: self.report(mutate), m.PACK, "active acceptance pointer differs")

    def inherited_pilot(self, change=None):
        pilot = json.loads((ROOT / m.ACCEPTANCE).read_bytes())
        link = {"path": m.ACCEPTANCE, "sha256": hashlib.sha256((ROOT / m.ACCEPTANCE).read_bytes()).hexdigest(),
                "asset_paths": [row["path"] for row in pilot["accepted_assets"]]}
        active = m.ISLAND + "/acceptance.json"
        def mutate(label, value):
            if label == m.PACK:
                value["acceptance_record"] = active
            if label == active:
                value.update(accepted=True, inherited_acceptances=[link])
                if change:
                    change(value)
        return self.report(mutate)

    def test_direct_and_inherited_pilot_scope(self):
        inherited = self.inherited_pilot()
        def direct(label, value):
            if label == m.PACK:
                value["acceptance_record"] = m.ACCEPTANCE
        original = self.report(direct)
        self.assertEqual(inherited["assets"], original["assets"])
        self.assertEqual(inherited["summary"], {"assets": 21, "walking_assets": 6, "island_assets": 15})

    def test_inherited_pilot_hash(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d["inherited_acceptances"][0].update(sha256="0" * 64)),
                     m.PACK, "active acceptance pointer differs")

    def test_missing_acceptance_pointer(self):
        def mutate(label, value):
            if label == m.PACK:
                value.pop("acceptance_record")
        self.refused(lambda: self.report(mutate), m.PACK, "active acceptance pointer differs")

    def test_inherited_pilot_row_shape(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d.update(inherited_acceptances=["bad"])),
                     m.PACK, "invalid inherited acceptance list")

    def test_inherited_pilot_record_shape(self):
        original_read = m.read_json
        active = m.ISLAND + "/acceptance.json"
        def changed(data, label):
            value = original_read(data, label)
            if label == m.PACK:
                value["acceptance_record"] = active
            return [] if label == active else value
        with patch.object(m, "read_json", side_effect=changed):
            self.refused(lambda: m.build(ROOT), m.PACK, "invalid inherited acceptance record")

    def test_inherited_pilot_list_shape(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d.update(inherited_acceptances=None)),
                     m.PACK, "invalid inherited acceptance list")

    def test_inherited_pilot_asset_list_shape(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d["inherited_acceptances"][0].update(asset_paths=None)),
                     m.PACK, "active acceptance pointer differs")

    def test_inherited_pilot_asset_shape(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d["inherited_acceptances"][0].update(asset_paths=[{}])),
                     m.PACK, "active acceptance pointer differs")

    def test_inherited_pilot_scope(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d["inherited_acceptances"][0]["asset_paths"].pop()),
                     m.PACK, "active acceptance pointer differs")

    def test_pending_inheriting_acceptance(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d.update(accepted=False)),
                     m.PACK, "active acceptance pointer differs")

    def test_duplicate_inherited_pilot(self):
        self.refused(lambda: self.inherited_pilot(lambda d: d["inherited_acceptances"].append(dict(d["inherited_acceptances"][0]))),
                     m.PACK, "active acceptance pointer differs")

    def test_pack_required_coverage(self):
        def mutate(label, value):
            if label == m.PACK:
                value["required_assets"].pop()
        self.refused(lambda: self.report(mutate), m.PACK, "accepted coverage differs")

    def test_missing_pilot_pack_asset(self):
        def mutate(label, value):
            if label == m.PACK:
                path = "BMP/JOHNWALK.BMP/024.png"
                value["assets"] = [row for row in value["assets"] if row["path"] != path]
                value["required_assets"].remove(path)
        self.refused(lambda: self.report(mutate), m.PACK, "accepted coverage differs")

    def test_pending_production_acceptance(self):
        def mutate(label, value):
            if label == m.ACCEPTANCE:
                value["accepted"] = False
        self.refused(lambda: self.report(mutate), m.ACCEPTANCE, "production acceptance is pending")

    def test_runtime_scale(self):
        def mutate(label, value):
            if label == m.PACK:
                value["runtime"]["scale"] = 3
        self.refused(lambda: self.report(mutate), m.PACK, "pilot scale differs")

    def test_pack_recipe_pointer(self):
        def mutate(label, value):
            if label == m.PACK:
                row = next(x for x in value["assets"] if x["path"] == "BMP/JOHNWALK.BMP/024.png")
                row["recipe"] = m.HISTORICAL_WALK + "/recipe.json"
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "active recipe pointer differs")

    def test_accepted_recipe_pointer(self):
        def mutate(label, value):
            if label == m.ACCEPTANCE:
                row = next(x for x in value["accepted_assets"] if x["path"] == "BMP/JOHNWALK.BMP/024.png")
                row["recipe"] = m.HISTORICAL_WALK + "/recipe.json"
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "active recipe pointer differs")

    def test_active_review_pointer(self):
        def mutate(label, value):
            if label == m.PACK:
                row = next(x for x in value["assets"] if x["path"] == "BMP/JOHNWALK.BMP/024.png")
                row["review"] = m.ISLAND + "/acceptance.json"
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "active review pointer differs")

    def test_hd_proxy_mismatch(self):
        def mutate(label, value):
            if label == m.PACK:
                value["assets"][0]["source_sha256"] = "0" * 64
        self.refused(lambda: self.report(mutate), "BMP/BACKGRND.BMP/000.png", "HD reference hash differs")

    def test_missing_coverage(self):
        def mutate(label, value):
            if label == m.ACCEPTANCE:
                value["accepted_assets"].pop()
        self.refused(lambda: self.report(mutate), m.PACK, "accepted coverage differs")

    def test_route_draw_mismatch(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["frames"]["hd"][0]["original_draw_xy_frame_slot"][2] = 24
        self.refused(lambda: self.report(mutate), m.TIMING, "capture draw differs from original route")

    def test_route_cadence_mismatch(self):
        def mutate(label, value):
            if label == m.TIMING:
                # Still contiguous with a valid pose at each timestamp, but the
                # first visit to pose1 occurs late. Shift its first120ms record.
                for style in value["frames"].values():
                    style[0]["duration_ms"] += 1
                    style[1]["logical_time_ms"] += 1
                    style[1]["duration_ms"] -= 1
        self.refused(lambda: self.report(mutate), m.TIMING, "display interval crosses a pose boundary")

    def test_missing_hd_timeline(self):
        def mutate(label, value):
            if label == m.TIMING:
                del value["frames"]["hd"]
        self.refused(lambda: self.report(mutate), m.TIMING, "both HD and Cartoon timelines are required")

    def test_capture_status(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["status"] = "FAIL"
        self.refused(lambda: self.report(mutate), m.TIMING, "capture evidence is not successful")

    def test_intervening_pose(self):
        def mutate(label, value):
            if label == m.TIMING:
                records = value["frames"]["hd"]
                records[2]["pose_index_zero_based"] = 0
                records[2]["original_draw_xy_frame_slot"] = records[0]["original_draw_xy_frame_slot"]
        self.refused(lambda: self.report(mutate), m.TIMING, "intervening display has the wrong pose")

    def test_display_count(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["frames_per_style"] = 999
        self.refused(lambda: self.report(mutate), m.TIMING, "display count differs")

    def test_review_end(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["duration_ms"] += 20
                for records in value["frames"].values():
                    records[-1]["duration_ms"] += 20
        self.refused(lambda: self.report(mutate), m.TIMING, "review duration differs from poses plus endpoint hold")

    def test_positive_display_duration(self):
        def mutate(label, value):
            if label == m.TIMING:
                records = value["frames"]["hd"]
                records[1]["duration_ms"] += records[0]["duration_ms"]
                records[0]["duration_ms"] = 0
        self.refused(lambda: self.report(mutate), m.TIMING, "display duration must be positive")

    def test_background_schedule(self):
        def mutate(label, value):
            if label == m.TIMING:
                for records in value["frames"].values():
                    records[1]["duration_ms"] += 1
                    records[2]["logical_time_ms"] += 1
                    records[2]["duration_ms"] -= 1
        self.refused(lambda: self.report(mutate), m.TIMING, "reviewed background display schedule differs")

    def test_initial_cadence(self):
        # Positive control independent of the generated timestamp list.
        result = self.report()
        self.assertEqual([r["start_ms"] for r in result["motion"]["route"]], list(range(0, 2760, 120)))

    def test_route_length_mismatch(self):
        def mutate(label, value):
            if label == m.ROUTE_ACCEPTANCE:
                value["motion_scope"]["positions"] += 1
        self.refused(lambda: self.report(mutate), "src/data/walk_data.h", "reviewed route length differs")

    def test_duration_mismatch(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["frames"]["hd"][-1]["duration_ms"] += 1
        self.refused(lambda: self.report(mutate), m.TIMING, "display durations do not cover review")

    def test_timeline_mismatch(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["frames"]["hd"][0]["logical_time_ms"] = 1
        self.refused(lambda: self.report(mutate), m.TIMING, "display timeline is not contiguous")

    def test_position_mismatch(self):
        def mutate(label, value):
            if label == m.TIMING:
                value["frames"]["hd"][0]["pose_index_zero_based"] = 99
        self.refused(lambda: self.report(mutate), m.TIMING, "unknown route position")

    def test_recipe_coverage(self):
        def mutate(label, value):
            if label == m.RECIPES[0]:
                value["required_assets"].pop()
        self.refused(lambda: self.report(mutate), m.RECIPES[0], "recipe coverage differs")

    def test_raw_bundle_hash(self):
        def mutate(label, value):
            if label == m.RECIPES[0]:
                value["source_bundle"]["sha256"] = "0" * 64
        self.refused(lambda: self.report(mutate), m.WALK + "/source-images.zip", "source bundle hash differs")

    def test_raw_selected_hash(self):
        def mutate(label, value):
            if label == m.RECIPES[0]:
                value["frames"][0]["source_sha256"] = "0" * 64
        self.refused(lambda: self.report(mutate), "BMP/JOHNWALK.BMP/024.png", "selected raw hash differs")

    def test_production_hash(self):
        read = m.zipfile.ZipFile.read
        def changed(archive, name, *args, **kwargs):
            data = read(archive, name, *args, **kwargs)
            return data[:-1] + bytes([data[-1] ^ 1]) if name == "data/styles/cartoon/BMP/BACKGRND.BMP/000.png" else data
        with patch.object(m.zipfile.ZipFile, "read", changed):
            self.refused(lambda: self.report(), "data/styles/cartoon/BMP/BACKGRND.BMP/000.png", "production PNG hash differs")

    def test_xpm_row_guard(self):
        self.refused(lambda: m.xpm_facts(fixture_xpm(("01", "0")), "bad.xpm", True), "bad.xpm", "invalid XPM pixel rows")

    def test_xpm_count_guard(self):
        data = fixture_xpm().replace(b'"2 2 16 1"', b'"2 3 16 1"')
        self.refused(lambda: m.xpm_facts(data, "bad.xpm", True), "bad.xpm", "XPM row count differs")

    def test_xpm_palette_guard(self):
        data = fixture_xpm().replace(b'"1 c #102030"', b'"0 c #102030"')
        self.refused(lambda: m.xpm_facts(data, "bad.xpm", True), "bad.xpm", "invalid XPM palette")

    def test_import_hash_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dump = root / "dump"
            (dump / "BMP").mkdir(parents=True)
            (root / m.PACK).parent.mkdir(parents=True)
            (root / m.PACK).write_text(json.dumps({"required_assets": ["BMP/X.BMP/000.png"]}))
            (root / m.ACCEPTANCE).parent.mkdir(parents=True)
            (root / m.ACCEPTANCE).write_text(json.dumps({"accepted_assets": [{"path": "BMP/X.BMP/000.png"}]}))
            (root / m.ORIGINAL_IDENTITY).parent.mkdir(parents=True, exist_ok=True)
            (root / m.ORIGINAL_IDENTITY).write_text(json.dumps({"source_resources": []}))
            data = fixture_xpm()
            (dump / "BMP/X.BMP.000.xpm").write_bytes(data)
            (root / "report.json").write_text(json.dumps({"exit_code": 0,
                "dump_sha256": {"BMP/X.BMP.000.xpm": "0" * 64}, "engine_sha256": "1" * 64, "input_sha256": {}}))
            self.refused(lambda: m.import_original(root, dump), "BMP/X.BMP.000.xpm", "original dump hash differs")

    def test_original_distribution_identity(self):
        def mutate(label, value):
            if label == m.ORIGINAL:
                value["input_sha256"]["RESOURCE.001"] = "0" * 64
        self.refused(lambda: self.report(mutate), m.ORIGINAL, "resource identity is not the supplied original distribution")

    def test_import_retains_pilot_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dump = root / "dump"
            (dump / "BMP").mkdir(parents=True)
            (root / m.PACK).parent.mkdir(parents=True)
            (root / m.PACK).write_text(json.dumps({"required_assets": ["BMP/X.BMP/000.png", "BMP/X.BMP/001.png"]}))
            (root / m.ACCEPTANCE).parent.mkdir(parents=True)
            (root / m.ACCEPTANCE).write_text(json.dumps({"accepted_assets": [{"path": "BMP/X.BMP/000.png"}]}))
            (root / m.ORIGINAL_IDENTITY).parent.mkdir(parents=True)
            (root / m.ORIGINAL_IDENTITY).write_text(json.dumps({"source_resources": []}))
            data = fixture_xpm()
            hashes = {}
            for index in (0, 1):
                name = f"BMP/X.BMP.{index:03}.xpm"
                (dump / name).write_bytes(data)
                hashes[name] = hashlib.sha256(data).hexdigest()
            (root / "report.json").write_text(json.dumps({"exit_code": 0, "dump_sha256": hashes,
                "engine_sha256": "1" * 64, "input_sha256": {}}))
            result = m.import_original(root, dump)
            self.assertEqual(set(result["assets"]), {"BMP/X.BMP/000.png"})

    def test_import_distribution_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dump = root / "dump"
            (dump / "BMP").mkdir(parents=True)
            (root / m.PACK).parent.mkdir(parents=True)
            (root / m.PACK).write_text(json.dumps({"required_assets": ["BMP/X.BMP/000.png"]}))
            (root / m.ORIGINAL_IDENTITY).parent.mkdir(parents=True)
            (root / m.ORIGINAL_IDENTITY).write_bytes((ROOT / m.ORIGINAL_IDENTITY).read_bytes())
            data = fixture_xpm()
            (dump / "BMP/X.BMP.000.xpm").write_bytes(data)
            (root / "report.json").write_text(json.dumps({"exit_code": 0,
                "dump_sha256": {"BMP/X.BMP.000.xpm": hashlib.sha256(data).hexdigest()},
                "engine_sha256": "1" * 64, "input_sha256": {"RESOURCE.MAP": "0" * 64, "RESOURCE.001": "0" * 64}}))
            self.refused(lambda: m.import_original(root, dump), "original dump report", "resource identity is not the supplied original distribution")

    def test_original_decoder_identity(self):
        def mutate(label, value):
            if label == m.ORIGINAL:
                value["decoder_executable_sha256"] = "not-a-sha256"
        self.refused(lambda: self.report(mutate), m.ORIGINAL, "decoder identity is not a SHA-256")


# Each replacement disables only the selected condition. Every subprocess runs
# exactly one negative control, reports the actual imported source SHA, and must
# produce one named test failure. No real input or approved asset is modified.
MUTATIONS = [
    ("test_arrival_acceptance_raw_bytes", ', "art/cartoon/arrival-pilot-v1/"', ""),
    ("test_inherited_pilot_record_shape", 'isinstance(active, dict)'),
    ("test_missing_acceptance_pointer", 'isinstance(active_path, str)'),
    ("test_inherited_pilot_row_shape", 'all(isinstance(row, dict) for row in links)'),
    ("test_inherited_pilot_list_shape", 'isinstance(links, list)'),
    ("test_inherited_pilot_asset_list_shape", 'isinstance(inherited[0].get("asset_paths"), list)'),
    ("test_inherited_pilot_asset_shape", 'all(isinstance(path, str) for path in inherited[0]["asset_paths"])'),
    ("test_active_acceptance_pointer", 'require(inherits_pilot, PACK, "active acceptance pointer differs")', 'require(True, PACK, "active acceptance pointer differs")'),
    ("test_inherited_pilot_hash", 'inherited[0].get("sha256") == evidence[ACCEPTANCE]["sha256"]'),
    ("test_inherited_pilot_scope", 'set(inherited[0].get("asset_paths", [])) == set(approved)'),
    ("test_pending_inheriting_acceptance", 'active.get("accepted") is True'),
    ("test_missing_pilot_pack_asset", 'set(approved) <= set(all_packed)'),
    ("test_duplicate_inherited_pilot", 'len(inherited) == 1'),
    ("test_pack_required_coverage", 'set(all_packed) == set(pack["required_assets"])'),
    ("test_import_retains_pilot_scope", '[row["path"] for row in accepted["accepted_assets"]]', 'read_json((root / PACK).read_bytes(), PACK)["required_assets"]'),
    ("test_pending_production_acceptance", 'accepted.get("accepted") is True'),
    ("test_runtime_scale", 'pack["runtime"]["scale"] == 2'),
    ("test_pack_recipe_pointer", 'item.get("recipe") == approved[asset].get("recipe") == path'),
    ("test_accepted_recipe_pointer", 'item.get("recipe") == approved[asset].get("recipe") == path'),
    ("test_active_review_pointer", 'item.get("review") == ACCEPTANCE'),
    ("test_duplicate_identity", "len(result) == len(rows)"),
    ("test_nonuniform_transform", "matrix[0] == matrix[4] == scale and matrix[1] == matrix[3] == 0"),
    ("test_landmark_mismatch", "all(abs(x) <= 1e-9 for x in residual)"),
    ("test_resize_mismatch", "all(math.isclose(source[i] * scale, canvas[i], abs_tol=1e-9)\n                    for i in (0, 1))"),
    ("test_canvas_mismatch", "row[\"runtime_canvas\"] == canvas"),
    ("test_original_canvas_mismatch", "native[\"canvas\"] == logical"),
    ("test_acceptance_mismatch", "approved[asset][\"sha256\"] == item[\"sha256\"] == row[\"candidate_png_sha256\"]"),
    ("test_hd_proxy_mismatch", "item[\"source_sha256\"] == original[\"source_sha256\"]"),
    ("test_missing_coverage", 'set(approved) == set(supplied_original["assets"])'),
    ("test_route_draw_mismatch", "record[\"original_draw_xy_frame_slot\"] == expected"),
    ("test_route_cadence_mismatch", "position == len(route) - 1 or end <= (position + 1) * pose_ms"),
    ("test_xpm_row_guard", "all(len(row) == width and set(row) <= set(palette) for row in rows)"),
    ("test_import_hash_guard", "digest(data) == report[\"dump_sha256\"][name]"),
    ("test_route_length_mismatch", 'len(route) == scope["positions"]'),
    ("test_duration_mismatch", 'sum(r["duration_ms"] for r in records) == timing["duration_ms"]'),
    ("test_timeline_mismatch", 'record["logical_time_ms"] == end'),
    ("test_position_mismatch", '0 <= position < len(route)'),
    ("test_recipe_coverage", 'set(rows) == set(recipe["required_assets"])'),
    ("test_raw_bundle_hash", 'digest((root / bundle_path).read_bytes()) == bundle["sha256"]'),
    ("test_raw_selected_hash", 'digest(data) == row["source_sha256"]'),
    ("test_production_hash", 'digest(data) == item["sha256"]'),
    ("test_xpm_count_guard", 'len(strings) == 1 + colors + height'),
    ("test_xpm_palette_guard", 'match is not None and match[1] in "0123456789abcdef" and match[1] not in palette'),
    ("test_missing_hd_timeline", 'set(timing["frames"]) == {"hd", "cartoon"}'),
    ("test_capture_status", 'timing["status"] == "PASS"'),
    ("test_intervening_pose", 'position == min(record["logical_time_ms"] // pose_ms, len(route) - 1)'),
    ("test_display_count", 'len(records) == timing["frames_per_style"]'),
    ("test_review_end", 'timing["duration_ms"] == expected_end'),
    ("test_positive_display_duration", 'record["duration_ms"] > 0'),
    ("test_background_schedule", '[r["logical_time_ms"] for r in records] == display_times'),
    ("test_original_distribution_identity", 'inputs == expected'),
    ("test_original_decoder_identity", 'isinstance(engine, str) and re.fullmatch(r"[0-9a-f]{64}", engine) is not None'),
    ("test_import_distribution_identity", 'validate_original_identity(report["input_sha256"], report["engine_sha256"], reference, "original dump report")', 'None'),
    # Normalization mutations must be caught by controls in both branches.
    ("test_transparency_normalization_varies", 'sprite and code == "0"', "False"),
    ("test_coordinate_normalization_varies", 'matrix[0] * raw[0] + matrix[2]', 'matrix[0] * raw[0]'),
    ("test_newline_normalization_varies", 'data.decode("utf-8").replace("\\r\\n", "\\n").replace("\\r", "\\n").encode("utf-8")', 'data'),
]


def mutations():
    source = DEFAULT_MODULE.read_text()
    with tempfile.TemporaryDirectory() as temporary:
        for index, entry in enumerate(MUTATIONS):
            case, condition, *replacement = entry
            if source.count(condition) != 1:
                raise RuntimeError(f"{case}: ambiguous mutation condition")
            changed = source.replace(condition, replacement[0] if replacement else "True")
            path = Path(temporary) / f"mutant_{index:02d}.py"
            path.write_text(changed, encoding="utf-8")
            expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            run = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--case", case, "--module", str(path)],
                                 capture_output=True, text=True)
            output = run.stdout + run.stderr
            if not (run.returncode == 1 and "WITNESS module " + expected_hash in output
                    and "Ran 1 test" in output and "FAILED (failures=1)" in output and case in output):
                raise RuntimeError(f"{case}: mutation did not produce exactly one witnessed failure\n{output}")
            print(f"FIRED {case} source={expected_hash}")
    print(f"PASS metadata mutations {len(MUTATIONS)}/{len(MUTATIONS)}")


def main():
    global m
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("smoke", "regression"), default="smoke")
    parser.add_argument("--case")
    parser.add_argument("--module", type=Path, default=DEFAULT_MODULE)
    parser.add_argument("--mutation-check", action="store_true")
    args = parser.parse_args()
    m = load_module(args.module)
    print("WITNESS module " + hashlib.sha256(args.module.read_bytes()).hexdigest(), flush=True)
    names = [args.case] if args.case else [name for name in unittest.defaultTestLoader.getTestCaseNames(MetadataTests)
        if name.startswith("test_smoke") == (args.phase == "smoke")]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(MetadataTests(name) for name in names))
    if not result.wasSuccessful():
        return 1
    if args.mutation_check:
        mutations()
    return 0


if __name__ == "__main__":
    sys.exit(main())
