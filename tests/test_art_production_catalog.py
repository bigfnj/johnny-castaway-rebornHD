"""Full catalog controls with tiny independent PNG/ledger fixtures and mutants.

Smoke reads the real catalog once. Negative controls use isolated memory data;
source mutations import a separate module and must fail one named assertion.
"""
import argparse
import copy
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/art_production_catalog.py"
sys.path.insert(0, str(ROOT / "tools"))
m = None
ASSET = "BMP/ONE.BMP/000.png"
RECIPE = "art/cartoon/example/recipe.json"
REVIEW = "art/cartoon/example/acceptance.json"
FRAMES = "art/cartoon/example/reference/metadata.json"
FRAME_SOURCE = "art/cartoon/example/reference/source.json"
AGGREGATE = "art/cartoon/expanded/acceptance.json"
SECOND = "BMP/ONE.BMP/002.png"
THIRD = "BMP/ONE.BMP/001.png"
REVIEW2 = "art/cartoon/another/acceptance.json"
FOOTPRINT = {"id": "cartoon-island-ground-v1", "canvas": [640, 180], "offset_hd": [-36, -10]}
GROUND = "BMP/BACKGRND.BMP/000.png"


def record_digest(data, path):
    # Explicit fixture file bytes, not a pretend hash accepted by the tool.
    return m.digest(json.dumps(data["records"][path], sort_keys=True, separators=(",", ":")).encode())


def inherited_fixture():
    data = fixture()
    item = dict(data["pack"]["assets"][0], path=SECOND, review=AGGREGATE,
                source_sha256=m.digest(data["members"]["data/hd/" + SECOND]))
    data["pack"]["assets"].append(item)
    data["pack"]["required_assets"].append(SECOND)
    data["pack"]["acceptance_record"] = AGGREGATE
    data["members"][m.PREFIX + SECOND] = data["members"][m.PREFIX + ASSET]
    data["records"][RECIPE]["frames"].append(dict(data["records"][RECIPE]["frames"][0], path=SECOND))
    data["records"][AGGREGATE] = {"accepted": True,
        "accepted_assets": [dict(path=row["path"], sha256=row["sha256"], recipe=row["recipe"]) for row in data["pack"]["assets"]],
        "inherited_acceptances": [{"path": REVIEW, "sha256": record_digest(data, REVIEW), "asset_paths": [ASSET]}],
        "newly_accepted_assets": [SECOND]}
    return data


def rehash_previous(data):
    data["records"][AGGREGATE]["inherited_acceptances"][0]["sha256"] = record_digest(data, REVIEW)


def load(path):
    spec = importlib.util.spec_from_file_location("catalog_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png(rows, filtering=0, color=6, invalid_filter=False, extra_scanline=False):
    """Independent forward filter encoder: test all five inverse branches."""
    bpp = {2: 3, 4: 2, 6: 4}[color]
    width, height = len(rows[0]) // bpp, len(rows)
    raw = bytearray()
    for y, row in enumerate(rows):
        raw.append(5 if invalid_filter and y == len(rows) - 1 else filtering)
        for i, value in enumerate(row):
            a = row[i - bpp] if i >= bpp else 0
            b = rows[y - 1][i] if y else 0
            c = rows[y - 1][i - bpp] if y and i >= bpp else 0
            if filtering == 0: prediction = 0
            elif filtering == 1: prediction = a
            elif filtering == 2: prediction = b
            elif filtering == 3: prediction = (a + b) // 2
            else:
                p = a + b - c
                da, db, dc = abs(p - a), abs(p - b), abs(p - c)
                prediction = a if da <= db and da <= dc else b if db <= dc else c
            raw.append((value - prediction) % 256)
    if extra_scanline: raw.append(0)
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")


def fixture():
    keyed = png([b"\xa8\0\xa8\xff" * 2] * 2, 4)
    visible = png([b"\x12\x34\x56\x80" * 2] * 2, 1)
    paths = [f"BMP/ONE.BMP/{i:03}.png" for i in range(3)] + ["SCR/ONE.SCR.png"]
    hd = {paths[0]: keyed, paths[1]: keyed, paths[2]: visible, paths[3]: keyed}
    manifest = {"scale": 2, "BMP": {"ONE.BMP": {"numImages": 3, "images": [
        {"index": i, "width": 1, "height": 1, "file": paths[i]} for i in range(3)]}},
        "SCR": {"ONE.SCR": {"width": 1, "height": 1, "file": paths[3]}}}
    item = {"path": ASSET, "source_sha256": m.digest(keyed), "sha256": m.digest(visible),
            "recipe": RECIPE, "review": REVIEW, "alpha": "transparent"}
    runtime = {"id": "cartoon", "scale": 2, "alpha": "straight", "coverage": "partial"}
    pack = {"schema_version": 1, "runtime": runtime, "required_assets": [ASSET], "assets": [item], "acceptance_record": REVIEW}
    records = {REVIEW: {"accepted": True, "accepted_assets": [{"path": ASSET, "sha256": item["sha256"], "recipe": RECIPE}]},
               RECIPE: {"frames": [{"path": ASSET, "candidate_png_sha256": item["sha256"], "runtime_canvas": [2, 2]}]}}
    members = {"data/hd/manifest.json": json.dumps(manifest).encode(), m.PREFIX + "manifest.json": json.dumps(runtime).encode(),
               m.PREFIX + ASSET: visible, **{"data/hd/" + path: data for path, data in hd.items()}}
    return {"plan": {"schema_version": 1, "style": "cartoon", "priority_resources": ["ONE.BMP"], "scope": "fixture", "review_policy": "human review"},
            "pack": pack, "original": {"assets": {ASSET: {"canvas": [1, 1]}}}, "records": records,
            "canvases": {path: [1, 1] for path in paths}, "members": members}


def footprint_fixture():
    data = fixture()
    hd = png([b"\x01\x02\x03\xff" * 560] * 104)
    current = png([b"\x04\x05\x06\x80" * 640] * 180)
    manifest = json.loads(data["members"]["data/hd/manifest.json"])
    manifest["BMP"]["BACKGRND.BMP"] = {"numImages": 1, "images": [
        {"index": 0, "width": 280, "height": 52, "file": GROUND}]}
    data["members"]["data/hd/manifest.json"] = json.dumps(manifest).encode()
    data["members"]["data/hd/" + GROUND] = hd
    data["members"][m.PREFIX + GROUND] = current
    data["canvases"][GROUND] = [280, 52]
    data["original"]["assets"][GROUND] = {"canvas": [280, 52]}
    data["pack"]["required_assets"].append(GROUND)
    data["pack"]["assets"].append({"path": GROUND, "source_sha256": m.digest(hd),
        "sha256": m.digest(current), "recipe": RECIPE, "review": REVIEW,
        "alpha": "transparent", "footprint": copy.deepcopy(FOOTPRINT)})
    data["records"][REVIEW]["accepted_assets"].append({"path": GROUND, "sha256": m.digest(current), "recipe": RECIPE})
    data["records"][RECIPE]["frames"].append({"path": GROUND, "candidate_png_sha256": m.digest(current),
        "runtime_canvas": [640, 180], "footprint": copy.deepcopy(FOOTPRINT)})
    return data


def report(data):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, body in data["members"].items(): archive.writestr(name, body)
    with zipfile.ZipFile(buffer) as archive:
        return m.assemble(archive, data["plan"], data["pack"], data["original"],
                          lambda path: data["records"][path], data["canvases"], lambda path: record_digest(data, path))


def reference_fixture():
    data = fixture()
    facts = {"resource": "ONE.BMP", "frame": 0, "canvas": [1, 1], "transparent_index": 0,
             "xpm_sha256": "a" * 64, "index_plane_sha256": "b" * 64, "rgba_sha256": "c" * 64}
    data["original"]["assets"][ASSET] = facts.copy()
    data["original"]["input_sha256"] = {"RESOURCE.MAP": "d" * 64, "RESOURCE.001": "e" * 64}
    data["plan"]["additional_original_frame_records"] = [FRAMES]
    data["records"][FRAMES] = {"source": "source.json", "frame_count": 2, "frames": [facts, dict(facts, frame=1)]}
    data["records"][FRAME_SOURCE] = {"resource_sha256": data["original"]["input_sha256"].copy(),
                                     "xpm_sha256": {"000": facts["xpm_sha256"], "001": facts["xpm_sha256"]}}
    return data


class CatalogTests(unittest.TestCase):
    def refused(self, callback, label, reason):
        try:
            callback()
        except Exception as exc:
            self.assertIsInstance(exc, m.ArtError)
            self.assertEqual(str(exc), label + ": " + reason)
        else:
            self.fail("Expected refusal: " + label + ": " + reason)

    def bad(self, edit, label, reason):
        data = fixture()
        edit(data)
        self.refused(lambda: report(data), label, reason)

    def test_smoke_real(self):
        result = m.build(ROOT)
        self.assertEqual(result["summary"]["slots"], 2401)
        self.assertEqual(result["summary"]["sprites"], 2391)
        self.assertEqual(result["summary"]["accepted"], len(json.loads((ROOT / m.PACK).read_text())["assets"]))
        self.assertEqual(result["families"][0]["resource"], "JOHNWALK.BMP")
        self.assertEqual(result["families"][1]["resource"], "BACKGRND.BMP")

    def test_smoke_fixture(self):
        result = report(fixture())
        self.assertEqual(result["summary"], {"slots": 4, "sprites": 3, "screens": 1, "accepted": 1, "pending": 3,
            "hd_proxy_blank_slots": 2, "distinct_hd_png_bytes": 2, "exact_duplicate_slots": 2, "supplied_original_evidence_slots": 1})

    def test_smoke_inherited(self):
        data = inherited_fixture()
        before = copy.deepcopy(data)
        result = report(data)
        self.assertEqual(data, before)
        self.assertEqual(result["summary"]["accepted"], 2)
        approvals = {row["path"]: row["production"]["acceptance"] for row in result["assets"]}
        self.assertEqual(approvals[ASSET], REVIEW)
        self.assertEqual(approvals[SECOND], AGGREGATE)
        self.assertIsNone(approvals[THIRD])

    def test_smoke_registered_footprint(self):
        data = footprint_fixture()
        result = report(data)
        row = next(row for row in result["assets"] if row["path"] == GROUND)
        self.assertEqual(row["bundled_logical_canvas"], [280, 52])
        self.assertEqual(row["hd_proxy"]["canvas"], [560, 104])
        self.assertEqual(row["runtime_canvas"], [640, 180])
        self.assertEqual(row["footprint"], FOOTPRINT)
        self.assertEqual(data["original"]["assets"][GROUND]["canvas"], [280, 52])

    def test_footprint_recipe_binding(self):
        data = footprint_fixture()
        data["records"][RECIPE]["frames"][-1].pop("footprint")
        self.refused(lambda: report(data), GROUND, "recipe footprint differs from ledger")

    def test_footprint_contract_rejects_other_offset(self):
        data = footprint_fixture()
        data["pack"]["assets"][-1]["footprint"]["offset_hd"][0] += 1
        self.refused(lambda: report(data), GROUND, "invalid Cartoon footprint declaration")

    def test_footprint_recipe_canvas(self):
        data = footprint_fixture()
        data["records"][RECIPE]["frames"][-1]["runtime_canvas"] = [560, 104]
        self.refused(lambda: report(data), GROUND, "recipe canvas differs from runtime")

    def inherited_bad(self, edit, label, reason):
        data = inherited_fixture()
        edit(data)
        self.refused(lambda: report(data), label, reason)

    def test_inherited_multiple_parents(self):
        data = inherited_fixture()
        item = dict(data["pack"]["assets"][0], path=THIRD, review=REVIEW2)
        data["pack"]["assets"].append(item)
        data["pack"]["required_assets"].append(THIRD)
        data["members"][m.PREFIX + THIRD] = data["members"][m.PREFIX + ASSET]
        data["records"][RECIPE]["frames"].append(dict(data["records"][RECIPE]["frames"][0], path=THIRD))
        approval = dict(path=THIRD, sha256=item["sha256"], recipe=RECIPE)
        data["records"][REVIEW2] = {"accepted": True, "accepted_assets": [approval]}
        data["records"][AGGREGATE]["accepted_assets"].append(approval)
        data["records"][AGGREGATE]["inherited_acceptances"].append(
            {"path": REVIEW2, "sha256": record_digest(data, REVIEW2), "asset_paths": [THIRD]})
        result = report(data)
        self.assertEqual(result["summary"]["accepted"], 3)
        self.assertEqual({row["path"]: row["production"]["acceptance"] for row in result["assets"]},
                         {ASSET: REVIEW, THIRD: REVIEW2, SECOND: AGGREGATE, "SCR/ONE.SCR.png": None})

    def test_inherited_nested_preserves_leaf_review(self):
        data = inherited_fixture()
        data["pack"]["acceptance_record"] = REVIEW2
        data["records"][REVIEW2] = {"accepted": True,
            "accepted_assets": copy.deepcopy(data["records"][AGGREGATE]["accepted_assets"]),
            "inherited_acceptances": [{"path": AGGREGATE, "sha256": record_digest(data, AGGREGATE), "asset_paths": [ASSET, SECOND]}],
            "newly_accepted_assets": []}
        approvals = {row["path"]: row["production"]["acceptance"] for row in report(data)["assets"]}
        self.assertEqual(approvals[ASSET], REVIEW)
        self.assertEqual(approvals[SECOND], AGGREGATE)

    def test_inherited_subset_allows_replacement(self):
        data = inherited_fixture()
        previous_png = png([b"\x32\x45\x67\x80" * 2] * 2)
        data["records"][REVIEW]["accepted_assets"].append(
            {"path": SECOND, "sha256": m.digest(previous_png), "recipe": "art/cartoon/previous/recipe.json"})
        rehash_previous(data)
        self.assertNotEqual(data["records"][REVIEW]["accepted_assets"][1]["sha256"], data["pack"]["assets"][1]["sha256"])
        result = report(data)
        self.assertEqual(result["summary"]["accepted"], 2)
        approvals = {row["path"]: row["production"]["acceptance"] for row in result["assets"]}
        self.assertEqual(approvals[ASSET], REVIEW)
        self.assertEqual(approvals[SECOND], AGGREGATE)

    def test_inherited_selected_history_still_validated(self):
        data = inherited_fixture()
        data["records"][AGGREGATE]["newly_accepted_assets"] = []  # Prior history is invalid for SECOND.
        data["pack"]["acceptance_record"] = REVIEW2
        data["pack"]["assets"][1]["review"] = REVIEW2
        data["records"][REVIEW2] = {"accepted": True,
            "accepted_assets": copy.deepcopy(data["records"][AGGREGATE]["accepted_assets"]),
            "inherited_acceptances": [{"path": AGGREGATE, "sha256": record_digest(data, AGGREGATE), "asset_paths": [ASSET]}],
            "newly_accepted_assets": [SECOND]}
        self.refused(lambda: report(data), AGGREGATE, "new approval coverage differs from inherited complement")

    def test_inherited_list(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE].update(inherited_acceptances={}), AGGREGATE, "invalid inherited acceptance list")

    def test_inherited_newly_list(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE].update(newly_accepted_assets=[SECOND, SECOND]), AGGREGATE, "invalid newly accepted asset list")

    def test_inherited_record_path(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE]["inherited_acceptances"][0].update(path=AGGREGATE), AGGREGATE, "invalid or duplicate inherited acceptance path")

    def test_inherited_record_duplicate(self):
        def edit(d):
            d["records"][AGGREGATE]["inherited_acceptances"].append(copy.deepcopy(d["records"][AGGREGATE]["inherited_acceptances"][0]))
        self.inherited_bad(edit, AGGREGATE, "invalid or duplicate inherited acceptance path")

    def test_inherited_asset_list(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE]["inherited_acceptances"][0].update(asset_paths=[ASSET, ASSET]), REVIEW, "invalid inherited asset list")

    def test_inherited_unknown_asset(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE]["inherited_acceptances"][0].update(asset_paths=[THIRD]), REVIEW, "inherited assets are unknown or overlap")

    def test_inherited_overlap(self):
        def edit(d):
            d["records"][REVIEW2] = copy.deepcopy(d["records"][REVIEW])
            d["records"][AGGREGATE]["inherited_acceptances"].append({"path": REVIEW2, "sha256": record_digest(d, REVIEW2), "asset_paths": [ASSET]})
        self.inherited_bad(edit, REVIEW2, "inherited assets are unknown or overlap")

    def test_inherited_hash(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE]["inherited_acceptances"][0].update(sha256="0" * 64), REVIEW, "inherited acceptance file hash differs")

    def test_inherited_exact_file_bytes(self):
        # Exercise build's real file reader/hash callback with both changed and
        # unchanged newline axes. Resource geometry is outside this I/O test.
        for ending in ("\n", "\r\n"):
            with self.subTest(ending=repr(ending)), tempfile.TemporaryDirectory() as temporary:
                root, data = Path(temporary), inherited_fixture()
                previous_bytes = (json.dumps(data["records"][REVIEW], indent=2) + "\n").replace("\n", ending).encode()
                data["records"][AGGREGATE]["inherited_acceptances"][0]["sha256"] = m.digest(previous_bytes)
                files = {m.PLAN: data["plan"], m.PACK: data["pack"], m.ORIGINAL: data["original"], **data["records"]}
                for name, value in files.items():
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(json.dumps(value).encode())
                (root / REVIEW).write_bytes(previous_bytes)
                (root / m.ARCHIVE).parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(root / m.ARCHIVE, "w") as archive:
                    for name, value in data["members"].items():
                        archive.writestr(name, value)
                    archive.writestr("data/RESOURCE.MAP", b"geometry supplied by fixture")
                    archive.writestr("data/RESOURCE.001", b"geometry supplied by fixture")
                with patch.object(m, "bundled_canvases", return_value=data["canvases"]):
                    try:
                        result = m.build(root)
                    except m.ArtError as exc:
                        self.fail("Exact-byte inherited record must pass: " + str(exc))
                    self.assertEqual(result["summary"]["accepted"], 2)
                    self.assertEqual(result["inputs"][REVIEW], {"basis": "file-bytes", "sha256": m.digest(previous_bytes)})
                    if ending == "\r\n":
                        declared = data["records"][AGGREGATE]["inherited_acceptances"][0]
                        declared["sha256"] = m.digest(previous_bytes.replace(b"\r\n", b"\n"))
                        (root / AGGREGATE).write_text(json.dumps(data["records"][AGGREGATE]), encoding="utf-8")
                        self.refused(lambda: m.build(root), REVIEW, "inherited acceptance file hash differs")

    def test_inherited_pending(self):
        def edit(d):
            d["records"][REVIEW]["accepted"] = False
            rehash_previous(d)
        self.inherited_bad(edit, REVIEW, "inherited acceptance is pending")

    def test_inherited_coverage(self):
        def edit(d):
            d["records"][REVIEW]["accepted_assets"].clear()
            rehash_previous(d)
        self.inherited_bad(edit, REVIEW, "selected asset is missing from inherited acceptance")

    def test_inherited_approval_hash(self):
        def edit(d):
            d["records"][REVIEW]["accepted_assets"][0]["sha256"] = "0" * 64
            rehash_previous(d)
        self.inherited_bad(edit, ASSET, "inherited approval differs from aggregate")

    def test_inherited_approval_recipe(self):
        def edit(d):
            d["records"][REVIEW]["accepted_assets"][0]["recipe"] = "different-recipe.json"
            rehash_previous(d)
        self.inherited_bad(edit, ASSET, "inherited approval differs from aggregate")

    def test_inherited_newly_coverage(self):
        self.inherited_bad(lambda d: d["records"][AGGREGATE].update(newly_accepted_assets=[]), AGGREGATE, "new approval coverage differs from inherited complement")

    def test_inherited_review_pointer(self):
        self.inherited_bad(lambda d: d["pack"]["assets"][0].update(review=AGGREGATE), ASSET, "active recipe or acceptance pointer differs")

    def test_reproduction(self):
        result = m.build(ROOT)
        self.assertEqual(json.loads((ROOT / (m.OUTPUT + ".json")).read_text()), result)
        self.assertEqual((ROOT / (m.OUTPUT + ".md")).read_text(), m.markdown(result))

    def test_duplicate_does_not_inherit_acceptance(self):
        rows = report(fixture())["assets"]
        self.assertEqual(rows[1]["hd_proxy"]["exact_duplicate_of"], ASSET)
        self.assertEqual(rows[1]["production"]["status"], "pending")
        self.assertEqual(rows[3]["hd_proxy"]["exact_duplicate_of"], ASSET)
        self.assertFalse(rows[3]["hd_proxy"]["blank_under_hd_runtime_rule"])
        self.assertEqual(rows[1]["supplied_original_evidence"]["status"], "not_cataloged")

    def test_blank_rule_varies(self):
        for filtering in range(5):
            for color in (2, 4, 6):
                pixel = {2: b"\xa8\0\xa8", 4: b"\x55\0", 6: b"\xa8\0\xa8\xff"}[color]
                data = png([pixel * 3] * 3, filtering, color)
                self.assertTrue(m.proxy_blank(data, "fixture.png", True))
                self.assertEqual(m.proxy_blank(data, "fixture.png", False), color == 4)
                visible = {2: b"\xa8\0\xa7", 4: b"\x55\x01", 6: b"\xa8\0\xa8\xfe"}[color]
                varied = png([pixel * 3, pixel + visible + pixel, pixel * 3], filtering, color)
                self.assertFalse(m.proxy_blank(varied, "fixture.png", True))
        self.assertTrue(m.proxy_blank(png([b"\x55\x33\x22\0"]), "hidden.png", True))

    def test_proxy_length(self):
        self.refused(lambda: m.proxy_blank(png([b"\0\0\0\0"], extra_scanline=True), "bad.png", True), "bad.png", "proxy PNG scanline length differs")

    def test_proxy_filter(self):
        self.refused(lambda: m.proxy_blank(png([b"\xff\0\0\xff", b"\0\0\0\0"], invalid_filter=True), "bad.png", True), "bad.png", "invalid proxy PNG filter")

    def test_plan_schema(self):
        self.bad(lambda d: d["plan"].update(schema_version=9), m.PLAN, "expected schema_version 1 and style cartoon")

    def test_priority(self):
        self.bad(lambda d: d["plan"]["priority_resources"].append("UNKNOWN.BMP"), m.PLAN, "unknown or duplicate priority resource")

    def test_priority_duplicate(self):
        self.bad(lambda d: d["plan"]["priority_resources"].append("ONE.BMP"), m.PLAN, "unknown or duplicate priority resource")

    def test_hd_coverage(self):
        self.bad(lambda d: d["canvases"].pop(ASSET), "data/hd/manifest.json", "HD inventory differs from bundled RESOURCE slots")

    def test_runtime(self):
        self.bad(lambda d: d["pack"]["runtime"].update(scale=3), m.PACK, "invalid Cartoon runtime contract")

    def test_pack_coverage(self):
        self.bad(lambda d: d["pack"]["required_assets"].clear(), m.PACK, "pack coverage differs from required source slots")

    def test_required_duplicate(self):
        self.bad(lambda d: d["pack"]["required_assets"].append(ASSET), m.PACK, "invalid or duplicate required asset")

    def test_complete(self):
        self.bad(lambda d: d["pack"]["runtime"].update(coverage="complete"), m.PACK, "complete pack is missing source slots")

    def test_archive_coverage(self):
        self.bad(lambda d: d["members"].update({m.PREFIX + "unexpected.png": b"unused"}), m.PACK, "production archive coverage differs from ledger")

    def test_manifest(self):
        self.bad(lambda d: d["members"].update({m.PREFIX + "manifest.json": b'{}'}), m.PREFIX + "manifest.json", "runtime manifest differs from ledger")

    def test_acceptance_pending(self):
        self.bad(lambda d: d["records"][REVIEW].update(accepted=False), REVIEW, "active production acceptance is pending")

    def test_acceptance_coverage(self):
        self.bad(lambda d: d["records"][REVIEW]["accepted_assets"].clear(), REVIEW, "acceptance coverage differs from production")

    def test_duplicate(self):
        self.bad(lambda d: d["pack"]["assets"].append(copy.deepcopy(d["pack"]["assets"][0])), m.PACK, "duplicate asset path")

    def test_bad_rows(self):
        self.bad(lambda d: d["pack"].update(assets=[{}]), m.PACK, "expected asset rows with paths")

    def test_missing_acceptance(self):
        self.bad(lambda d: d["pack"].pop("acceptance_record"), m.PACK, "missing active acceptance record")

    def test_missing_recipe(self):
        self.bad(lambda d: d["pack"]["assets"][0].pop("recipe"), ASSET, "missing recipe reference")

    def test_missing_recipe_asset(self):
        self.bad(lambda d: d["records"][RECIPE]["frames"].clear(), ASSET, "asset is absent from referenced recipe")

    def test_recipe_canvas(self):
        self.bad(lambda d: d["records"][RECIPE]["frames"][0].update(runtime_canvas=[3, 3]), ASSET, "recipe canvas differs from runtime")

    def test_bundled_canvas(self):
        self.bad(lambda d: d["canvases"].update({ASSET: [2, 2]}), ASSET, "HD logical canvas differs from bundled RESOURCE")

    def test_original_canvas(self):
        self.bad(lambda d: d["original"]["assets"][ASSET].update(canvas=[2, 2]), ASSET, "stored supplied-original canvas differs from bundled RESOURCE")

    def test_review_pointer(self):
        self.bad(lambda d: d["pack"]["assets"][0].update(review="wrong.json"), ASSET, "active recipe or acceptance pointer differs")

    def test_proxy_hash(self):
        self.bad(lambda d: d["pack"]["assets"][0].update(source_sha256="0" * 64), ASSET, "accepted HD proxy hash differs")

    def test_accepted_hash(self):
        self.bad(lambda d: d["records"][REVIEW]["accepted_assets"][0].update(sha256="0" * 64), ASSET, "accepted PNG hashes differ")

    def test_production_hash(self):
        self.bad(lambda d: d["members"].update({m.PREFIX + ASSET: b"changed"}), m.PREFIX + ASSET, "production PNG hash differs")

    def test_alpha_declaration(self):
        self.bad(lambda d: d["pack"]["assets"][0].update(alpha="opaque"), ASSET, "accepted alpha declaration differs")

    def test_sprite_alpha(self):
        def edit(d):
            raw = png([b"\x12\x34\x56" * 2] * 2, color=2)
            d["members"][m.PREFIX + ASSET] = raw
            checksum = m.digest(raw)
            d["pack"]["assets"][0]["sha256"] = checksum
            d["records"][REVIEW]["accepted_assets"][0]["sha256"] = checksum
            d["records"][RECIPE]["frames"][0]["candidate_png_sha256"] = checksum
        self.bad(edit, ASSET, "accepted sprite has no alpha channel")

    def test_screen_opacity(self):
        def edit(d):
            screen = "SCR/ONE.SCR.png"
            raw = d["members"].pop(m.PREFIX + ASSET)
            d["members"][m.PREFIX + screen] = raw
            d["pack"]["required_assets"] = [screen]
            d["pack"]["assets"][0]["path"] = screen
            d["records"][REVIEW]["accepted_assets"][0]["path"] = screen
            d["records"][RECIPE]["frames"][0]["path"] = screen
        self.bad(edit, "SCR/ONE.SCR.png", "accepted screen is not opaque")

    def test_check_refuses_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = report(fixture())
            for suffix in (".json", ".md"):
                path = root / (m.OUTPUT + suffix)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale", encoding="utf-8")
            output, error = io.StringIO(), io.StringIO()
            with patch.object(m, "build", return_value=result), contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                status = m.main(["--root", str(root), "--check"])
            self.assertEqual(status, 1)
            self.assertEqual(error.getvalue(), "ERROR " + m.OUTPUT + ".json: generated production catalog differs\n")
            self.assertNotIn("PASS", output.getvalue())
            self.assertEqual((root / (m.OUTPUT + ".json")).read_text(), "stale")

    def test_text_hash_varies(self):
        self.assertEqual(m.text_hash(b"a\r\nb\r"), m.text_hash(b"a\nb\n"))
        self.assertNotEqual(m.text_hash(b"a \nb\n"), m.text_hash(b"a\nb\n"))
        self.assertNotEqual(m.text_hash(b"\xef\xbb\xbfa\nb\n"), m.text_hash(b"a\nb\n"))

    def test_reference_links(self):
        data = reference_fixture()
        before = copy.deepcopy(data)
        result = report(data)
        self.assertEqual(data, before)
        self.assertEqual(result["summary"]["supplied_original_evidence_slots"], 2)
        evidence = result["assets"][1]["supplied_original_evidence"]
        self.assertEqual(evidence, {"status": "available", "record": FRAMES, "record_format": "bmp-frame-list",
                                   "asset_key": "BMP/ONE.BMP/001.png", "independently_reread": False})
        self.assertEqual(result["assets"][1]["production"]["status"], "pending")

    def reference_bad(self, edit, label, reason):
        data = reference_fixture()
        edit(data)
        self.refused(lambda: report(data), label, reason)

    def test_reference_paths(self):
        self.reference_bad(lambda d: d["plan"]["additional_original_frame_records"].append(FRAMES), m.PLAN, "invalid or duplicate original frame record")

    def test_reference_identities(self):
        self.reference_bad(lambda d: d["records"][FRAMES].update(frame_count=3), FRAMES, "invalid original frame identities or count")

    def test_reference_source(self):
        self.reference_bad(lambda d: d["records"][FRAMES].pop("source"), FRAMES, "missing original frame source")

    def test_reference_distribution(self):
        self.reference_bad(lambda d: d["records"][FRAME_SOURCE]["resource_sha256"].update({"RESOURCE.MAP": "0" * 64}), FRAME_SOURCE, "supplied-original distribution differs")

    def test_reference_duplicate(self):
        self.reference_bad(lambda d: d["records"][FRAMES]["frames"][1].update(frame=0), FRAMES, "duplicate original frame identity")

    def test_reference_facts(self):
        self.reference_bad(lambda d: d["records"][FRAMES]["frames"][1].update(index_plane_sha256="unknown"), FRAMES, "invalid stored original pixel facts")

    def test_reference_overlap(self):
        self.reference_bad(lambda d: d["records"][FRAMES]["frames"][0].update(index_plane_sha256="0" * 64), FRAMES, "overlapping original frame facts differ")

    def test_reference_xpm_source(self):
        self.reference_bad(lambda d: d["records"][FRAMES]["frames"][1].update(xpm_sha256="0" * 64), FRAMES, "original frame XPM hash differs from source record:001")

    def test_reference_unknown_slot(self):
        def edit(d):
            d["records"][FRAMES]["frames"][1]["frame"] = 999
            d["records"][FRAME_SOURCE]["xpm_sha256"]["999"] = "a" * 64
        self.reference_bad(edit, m.PLAN, "original reference names an unknown runtime slot")


MUTATIONS = [
    ("test_inherited_list", 'isinstance(inherited, list) and all(isinstance(item, dict) for item in inherited)'),
    ("test_inherited_newly_list", 'isinstance(newly, list) and all(isinstance(path, str) for path in newly)\n                and len(newly) == len(set(newly))'),
    ("test_inherited_record_path", 'isinstance(previous_path, str) and previous_path not in (*ancestors, acceptance_path)\n                    and previous_path not in seen_records'),
    ("test_inherited_asset_list", 'isinstance(paths, list) and all(isinstance(path, str) for path in paths)\n                    and len(paths) == len(set(paths))'),
    ("test_inherited_unknown_asset", 'set(paths) <= set(approved) and not (set(paths) & inherited_paths)'),
    ("test_inherited_hash", 'isinstance(checksum, str) and re.fullmatch(r"[0-9a-f]{64}", checksum)\n                    and record_hash is not None and record_hash(previous_path) == checksum'),
    ("test_inherited_exact_file_bytes", 'lambda path: raw_hashes[path]', 'lambda path: text_hash((root / path).read_bytes())'),
    ("test_inherited_pending", 'previous.get("accepted") is True'),
    ("test_inherited_coverage", 'set(paths) <= set(previous_rows)'),
    ("test_inherited_selected_history_still_validated", 'requests.append((previous, previous_rows, previous_path, (*ancestors, acceptance_path), None))',
     'requests.append((previous, {path: previous_rows[path] for path in paths}, previous_path, (*ancestors, acceptance_path), None))'),
    ("test_inherited_approval_hash", 'all(previous_rows[path].get(key) == approved[path].get(key) for key in ("sha256", "recipe"))'),
    ("test_inherited_newly_coverage", 'set(newly) == set(approved) - inherited_paths'),
    ("test_smoke_inherited", '"acceptance": approval_paths[path], "recipe": recipe_path', '"acceptance": acceptance_path, "recipe": recipe_path'),
    ("test_reference_paths", 'isinstance(paths, list) and all(isinstance(path, str) for path in paths)\n            and len(paths) == len(set(paths))'),
    ("test_reference_identities", 'isinstance(frames, list) and metadata.get("frame_count") == len(frames)\n                and all(isinstance(row, dict) and isinstance(row.get("resource"), str)\n                        and row["resource"].endswith(".BMP") and type(row.get("frame")) is int\n                        and row["frame"] >= 0 for row in frames)'),
    ("test_reference_source", 'isinstance(source_name, str)'),
    ("test_reference_distribution", 'source.get("resource_sha256") == original["input_sha256"]'),
    ("test_reference_duplicate", 'slot not in seen'),
    ("test_reference_facts", 'isinstance(row.get("canvas"), list) and len(row["canvas"]) == 2\n                    and all(type(n) is int and n > 0 for n in row["canvas"])\n                    and row.get("transparent_index") == 0\n                    and all(isinstance(row.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", row[key])\n                            for key in ("xpm_sha256", "index_plane_sha256", "rgba_sha256"))'),
    ("test_reference_overlap", 'previous is None or all(previous.get(key) == row.get(key) for key in\n                    ("canvas", "xpm_sha256", "index_plane_sha256", "rgba_sha256", "transparent_index"))'),
    ("test_reference_xpm_source", '''isinstance(source.get("xpm_sha256"), dict)
                    and source["xpm_sha256"].get(f"{row['frame']:03}") == row["xpm_sha256"]'''),
    ("test_reference_unknown_slot", 'set(original_assets) <= set(catalog)'),
    ("test_proxy_length", "len(raw) == expected and decoder.eof and not decoder.unused_data"),
    ("test_proxy_filter", "all(raw[y * (stride + 1)] <= 4 for y in range(height))"),
    ("test_plan_schema", 'isinstance(plan, dict) and plan.get("schema_version") == 1 and plan.get("style") == "cartoon"'),
    ("test_priority", 'isinstance(priorities, list) and all(isinstance(name, str) and name in resources for name in priorities)\n            and len(priorities) == len(set(priorities))'),
    ("test_hd_coverage", "set(catalog) == set(canvases)"),
    ("test_runtime", 'pack.get("schema_version") == 1 and runtime.get("id") == "cartoon" and type(runtime.get("scale")) is int and runtime["scale"] == 2\n            and runtime.get("alpha") == "straight" and runtime.get("coverage") in ("partial", "complete")'),
    ("test_pack_coverage", 'set(packed) == set(pack.get("required_assets", [])) and set(packed) <= set(catalog)'),
    ("test_required_duplicate", 'isinstance(required, list) and all(isinstance(path, str) for path in required)\n            and len(required) == len(set(required))'),
    ("test_complete", 'runtime["coverage"] != "complete" or set(packed) == set(catalog)'),
    ("test_archive_coverage", "archive_assets == set(packed)"),
    ("test_manifest", "manifest == runtime"),
    ("test_acceptance_pending", 'accepted.get("accepted") is True'),
    ("test_acceptance_coverage", "set(approved) == set(packed)"),
    ("test_duplicate", "len(result) == len(rows)"),
    ("test_bad_rows", 'isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("path"), str)\n            for row in rows)'),
    ("test_missing_acceptance", "isinstance(acceptance_path, str)"),
    ("test_missing_recipe", 'require(isinstance(path, str), item["path"], "missing recipe reference")', 'require(True, item["path"], "missing recipe reference")'),
    ("test_missing_recipe_asset", "row is not None"),
    ("test_recipe_canvas", 'row.get("runtime_canvas") == footprint["canvas"]'),
    ("test_footprint_recipe_binding", 'row.get("footprint") == item.get("footprint")'),
    ("test_bundled_canvas", "logical == canvases[path]"),
    ("test_original_canvas", 'native["canvas"] == logical'),
    ("test_review_pointer", 'item.get("review") == approval_paths[path] and approval.get("recipe") == recipe_path'),
    ("test_proxy_hash", 'item.get("source_sha256") == proxy_hash'),
    ("test_accepted_hash", 'item.get("sha256") == approval.get("sha256") == row.get("candidate_png_sha256")'),
    ("test_production_hash", 'digest(data) == item["sha256"]'),
    ("test_alpha_declaration", 'item.get("alpha") == alpha'),
    ("test_sprite_alpha", 'info["color_type"] in (4, 6)'),
    ("test_screen_opacity", 'info["alpha_opaque"] == info["width"] * info["height"]'),
    ("test_check_refuses_drift", '(args.root / name).read_text(encoding="utf-8") == text'),
    ("test_blank_rule_varies", 'sprite and color in (2, 6) and alpha == 255 and row[offset:offset + 3] == b"\\xa8\\x00\\xa8"', "False"),
    ("test_duplicate_does_not_inherit_acceptance", 'blank_key = (proxy_hash, source["kind"])', 'blank_key = proxy_hash'),
]


def mutations():
    source = SOURCE.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="jcr-catalog-mutants-") as temporary:
        for index, (case, condition, *replacement) in enumerate(MUTATIONS):
            if source.count(condition) != 1: raise AssertionError(case + ": ambiguous source mutation")
            path = Path(temporary) / f"mutant_{index}.py"
            path.write_text(source.replace(condition, replacement[0] if replacement else "True"), encoding="utf-8")
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--case", case, "--module", str(path)],
                                    capture_output=True, text=True, timeout=30)
            text = result.stdout + result.stderr
            if not (result.returncode == 1 and "WITNESS module " + checksum in text and "Ran 1 test" in text
                    and "FAILED (failures=1)" in text and case in text):
                raise AssertionError(case + ": expected exactly one witnessed failure\n" + text)
            print(f"FIRED tools/art_production_catalog.py {case} source={checksum}", flush=True)


def main():
    global m
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("smoke", "regression"), default="smoke")
    parser.add_argument("--mutation-check", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--module", type=Path, default=SOURCE)
    args = parser.parse_args()
    m = load(args.module)
    print("WITNESS module " + hashlib.sha256(args.module.read_bytes()).hexdigest(), flush=True)
    names = [args.case] if args.case else [name for name in unittest.defaultTestLoader.getTestCaseNames(CatalogTests)
        if name.startswith("test_smoke") == (args.phase == "smoke")]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(CatalogTests(name) for name in names))
    if not result.wasSuccessful(): return 1
    if args.mutation_check: mutations()
    return 0


if __name__ == "__main__":
    sys.exit(main())
