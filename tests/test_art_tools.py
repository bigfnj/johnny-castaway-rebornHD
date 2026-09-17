"""Offline authoring contract tests, including deliberately broken inputs.

Run: python -m unittest discover -s tests -p test_art_tools.py -v
"""

import contextlib
import copy
import io
import json
import struct
import sys
import tempfile
import unittest
import warnings
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from art_common import ArtError, CENTER_FOAM_FOOTPRINT, ISLAND_FOOTPRINT, cartoon_footprint, digest, inspect_png
from art_inventory import inventory
from art_pack import accepted_pack, build_archive, main


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def png(width=2, height=2, pixels=None, color=6, depth=8, interlace=0, filter_type=0):
    """Synthetic fixture, independent forward row filtering exercises all axes."""
    channels = {2: 3, 4: 2, 6: 4}[color]
    if pixels is None:
        pixels = bytes((168, 0, 168, 255)) * (width * height)
    assert len(pixels) == width * height * channels
    stride = width * channels
    raw = bytearray()
    previous = bytes(stride)
    for y in range(height):
        row = pixels[y * stride:(y + 1) * stride]
        raw.append(filter_type)
        for i, byte in enumerate(row):
            left = row[i - channels] if i >= channels else 0
            above = previous[i]
            diagonal = previous[i - channels] if i >= channels else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            else:
                p = left + above - diagonal
                a, b, c = abs(p - left), abs(p - above), abs(p - diagonal)
                predictor = left if a <= b and a <= c else above if b <= c else diagonal
            raw.append((byte - predictor) & 255)
        previous = row
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, 0, 0, interlace))
            + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


class ArtToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "base.zip"
        self.accepted = self.root / "accepted"
        self.asset = "BMP/JOHNWALK.BMP/000.png"
        self.other = "BMP/JOHNWALK.BMP/001.png"
        self.screen = "SCR/OCEAN00.SCR.png"
        self.original = png()
        source_manifest = {"scale": 2, "BMP": {"JOHNWALK.BMP": {"numImages": 2, "images": [
            {"index": i, "width": 1, "height": 1, "file": path}
            for i, path in enumerate((self.asset, self.other))]}},
            "SCR": {"OCEAN00.SCR": {"width": 2, "height": 1, "file": self.screen}}}
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("data/RESOURCE.001", b"original binary payload\x00\xff")
            archive.writestr("data/sound1.wav", b"original sound")
            archive.writestr("data/hd/manifest.json", json.dumps(source_manifest))
            archive.writestr("data/hd/" + self.asset, self.original)
            archive.writestr("data/hd/" + self.other, self.original)
            archive.writestr("data/hd/" + self.screen, png(4, 2))
        self.ledger = {
            "schema_version": 1,
            "runtime": {"id": "cartoon", "scale": 2, "alpha": "straight", "coverage": "partial"},
            "required_assets": [self.asset],
            "assets": [{"path": self.asset, "source_sha256": digest(self.original),
                        "sha256": digest(self.original), "alpha": "opaque"}],
        }
        self.write_asset(self.original)

    def write_asset(self, data, path=None):
        file = self.accepted / (path or self.asset)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
        if path is None:
            self.ledger["assets"][0]["sha256"] = digest(data)

    def validate(self):
        with zipfile.ZipFile(self.archive) as archive:
            return accepted_pack(archive, self.ledger, self.accepted)

    def assert_cli_failure(self, named_path, reason):
        ledger_path = self.root / "pack.json"
        ledger_path.write_text(json.dumps(self.ledger), encoding="utf-8")
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(["validate", "--archive", str(self.archive), "--ledger", str(ledger_path),
                         "--accepted", str(self.accepted)])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(len(error.getvalue().splitlines()), 1)
        self.assertIn(named_path, error.getvalue())
        self.assertIn(reason, error.getvalue())

    def test_inventory_exports_unmodified_and_records_exact_aliases(self):
        exported = self.root / "reference"
        report = inventory(self.archive, ["JOHNWALK.BMP"], exported)
        self.assertEqual(report["summary"]["assets"], 2)
        self.assertEqual(report["summary"]["unique_png_bytes"], 1)
        self.assertEqual((exported / self.asset).read_bytes(), self.original)
        self.assertEqual(report["assets"][1]["identical_to"], self.asset)
        (exported / self.asset).write_bytes(b"deliberately changed reference")
        with self.assertRaisesRegex(ArtError, "refusing to overwrite"):
            inventory(self.archive, ["JOHNWALK.BMP"], exported)

    def test_true_alpha_preserves_opaque_magenta_and_binary_control(self):
        _, packed, alpha = self.validate()
        self.assertEqual(packed[self.asset], self.original)
        self.assertEqual(alpha["opaque"], 1)
        binary = png(pixels=bytes((168, 0, 168, 255, 0, 0, 0, 0)) * 2)
        self.write_asset(binary)
        self.ledger["assets"][0]["alpha"] = "transparent"
        _, packed, alpha = self.validate()
        self.assertEqual(packed[self.asset], binary)
        self.assertEqual(alpha["transparent"], 1)
        partial = png(pixels=bytes((168, 0, 168, 128, 0, 0, 0, 0)) * 2)
        self.write_asset(partial)
        _, packed, alpha = self.validate()
        self.assertEqual(packed[self.asset], partial)
        self.assertEqual(alpha["transparent"], 1)

    def test_complete_pack_accepts_blank_sprite_and_opaque_rgb_screen(self):
        blank = png(pixels=bytes(16))
        screen = png(4, 2, pixels=bytes((5, 10, 20)) * 8, color=2)
        self.write_asset(blank, self.other)
        self.write_asset(screen, self.screen)
        with zipfile.ZipFile(self.archive) as archive:
            screen_source_hash = digest(archive.read("data/hd/" + self.screen))
        self.ledger["assets"].extend([
            {"path": self.other, "source_sha256": digest(self.original), "sha256": digest(blank), "alpha": "blank"},
            {"path": self.screen, "source_sha256": screen_source_hash, "sha256": digest(screen), "alpha": "opaque"},
        ])
        self.ledger["runtime"]["coverage"] = "complete"
        runtime, packed, alpha = self.validate()
        self.assertEqual(runtime["coverage"], "complete")
        self.assertEqual(len(packed), 3)
        self.assertEqual(alpha, {"opaque": 2, "blank": 1, "transparent": 0})

    def test_all_filters_rgb_rgba_and_grayscale_alpha(self):
        for filter_type in range(5):
            for color, values in ((6, (1, 20, 93, 0, 252, 90, 7, 128, 98, 2, 87, 255, 4, 6, 9, 64)),
                                  (4, (11, 0, 93, 128, 234, 255, 55, 64)),
                                  (2, (11, 72, 45, 13, 20, 93, 18, 80, 230, 67, 5, 200))):
                with self.subTest(filter=filter_type, color=color):
                    info = inspect_png(png(pixels=bytes(values), color=color, filter_type=filter_type), "filtered.png")
                    self.assertEqual(info["alpha_opaque"], 4 if color == 2 else 1)
                    self.assertEqual(info["alpha_partial"], 0 if color == 2 else 2)
                    self.assertEqual(info["alpha_zero"], 0 if color == 2 else 1)

    def test_wrong_dimensions_mutation_names_one_asset(self):
        self.write_asset(png(4, 2))
        self.assert_cli_failure(self.asset, "wrong dimensions")

    def footprint_fixture(self, frame=0):
        """One original slot; changed canvas requires an explicit named ledger row."""
        old_file = self.accepted / self.asset
        old_file.unlink()
        self.asset = f"BMP/BACKGRND.BMP/{frame:03}.png"
        logical = [280, 52] if frame == 0 else [160, 25]
        self.original = png(logical[0]*2, logical[1]*2)
        manifest = {"scale": 2, "BMP": {"BACKGRND.BMP": {"numImages": frame+1, "images": [
            {"index": i, "width": logical[0], "height": logical[1],
             "file": f"BMP/BACKGRND.BMP/{i:03}.png"} for i in range(frame+1)]}}, "SCR": {}}
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("data/hd/manifest.json", json.dumps(manifest))
            for row in manifest["BMP"]["BACKGRND.BMP"]["images"]:
                archive.writestr("data/hd/" + row["file"], self.original)
        footprint = copy.deepcopy(ISLAND_FOOTPRINT if frame == 0 else CENTER_FOAM_FOOTPRINT)
        self.ledger["required_assets"] = [self.asset]
        self.ledger["assets"] = [{"path": self.asset, "source_sha256": digest(self.original),
                                  "footprint": footprint, "alpha": "opaque"}]
        self.write_asset(png(*footprint["canvas"]))

    def test_named_island_footprints_preserve_original_catalog(self):
        for frame in (0, 6, 7, 8):
            with self.subTest(frame=frame):
                self.footprint_fixture(frame)
                _, packed, _ = self.validate()
                expected = [640, 180] if frame == 0 else [384, 256]
                info = inspect_png(packed[self.asset], self.asset)
                self.assertEqual([info["width"], info["height"]], expected)
                original = inventory(self.archive, ["BACKGRND.BMP"])["assets"][-1]
                self.assertEqual([original["logical_width"], original["logical_height"]],
                                 [280, 52] if frame == 0 else [160, 25])

    def test_extended_png_without_declaration_is_refused(self):
        self.footprint_fixture()
        del self.ledger["assets"][0]["footprint"]
        self.assert_cli_failure(self.asset, "wrong dimensions")

    def test_registered_ground_build_preserves_hd(self):
        self.footprint_fixture()
        runtime, packed, _ = self.validate()
        target = self.root / "registered.zip"
        build_archive(self.archive, target, runtime, packed)
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(archive.read("data/hd/" + self.asset), self.original)
            self.assertEqual(archive.read("data/styles/cartoon/" + self.asset), packed[self.asset])

    def test_declared_footprint_requires_exact_png(self):
        self.footprint_fixture()
        self.write_asset(png(640, 179))
        self.assert_cli_failure(self.asset, "wrong dimensions")

    def test_footprint_name_size_and_offset_are_not_freeform(self):
        self.footprint_fixture()
        for key, value in (("id", "unknown"), ("canvas", [640, 181]), ("offset_hd", [-35, -10])):
            with self.subTest(key=key):
                self.ledger["assets"][0]["footprint"] = dict(ISLAND_FOOTPRINT, **{key: value})
                self.assert_cli_failure(self.asset, "invalid Cartoon footprint declaration")

    def test_footprint_rejects_other_slot_and_original_dimensions(self):
        for path, logical, declaration in (
                (self.asset, [280, 52], ISLAND_FOOTPRINT),
                ("BMP/BACKGRND.BMP/001.png", [280, 52], ISLAND_FOOTPRINT),
                ("BMP/BACKGRND.BMP/000.png", [281, 52], ISLAND_FOOTPRINT),
                ("BMP/BACKGRND.BMP/009.png", [160, 25], CENTER_FOAM_FOOTPRINT)):
            with self.subTest(path=path, logical=logical):
                with self.assertRaisesRegex(ArtError, "invalid Cartoon footprint declaration"):
                    cartoon_footprint(path, logical, 2, declaration)

    def test_missing_coverage_mutation_names_one_asset(self):
        self.ledger["required_resources"] = ["JOHNWALK.BMP"]
        self.assert_cli_failure(self.other, "missing required")

    def test_complete_coverage_requires_all_original_slots(self):
        self.ledger["runtime"]["coverage"] = "complete"
        self.assert_cli_failure(self.other, "missing required")

    def test_duplicate_accepted_path_mutation_names_one_asset(self):
        self.ledger["assets"].append(copy.deepcopy(self.ledger["assets"][0]))
        self.assert_cli_failure(self.asset, "duplicate accepted")

    def test_duplicate_archive_member_mutation_names_one_asset(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archive, "a") as archive:
                archive.writestr("data/hd/" + self.asset, self.original)
        self.assert_cli_failure("data/hd/" + self.asset, "duplicate archive")

    def test_unsupported_png_mutations_name_one_asset(self):
        for changes in ({"depth": 16}, {"interlace": 1}):
            with self.subTest(changes=changes):
                self.write_asset(png(**changes))
                self.assert_cli_failure(self.asset, "unsupported PNG")
        paletted = self.original[:8] + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 3, 0, 0, 0)) + self.original[33:]
        self.write_asset(paletted)
        self.assert_cli_failure(self.asset, "unsupported PNG")

    def test_missing_accepted_file_mutation_names_one_asset(self):
        (self.accepted / self.asset).unlink()
        self.assert_cli_failure(self.asset, "missing accepted PNG")

    def test_corrupt_crc_mutation_names_one_asset(self):
        self.write_asset(self.original[:-1] + bytes((self.original[-1] ^ 1,)))
        self.assert_cli_failure(self.asset, "CRC")

    def test_bad_deflate_with_correct_chunk_crc_is_rejected(self):
        broken = self.original[:33] + chunk(b"IDAT", b"bad zlib") + chunk(b"IEND", b"")
        self.write_asset(broken)
        self.assert_cli_failure(self.asset, "compressed PNG")

    def test_alpha_declaration_is_checked_against_pixels(self):
        self.ledger["assets"][0]["alpha"] = "transparent"
        self.assert_cli_failure(self.asset, "differs from actual opaque")

    def test_alpha_channel_is_required_for_sprites(self):
        self.write_asset(png(pixels=bytes((5, 10, 20)) * 4, color=2))
        self.assert_cli_failure(self.asset, "explicit alpha channel")

    def test_accepted_hash_mutation_is_rejected(self):
        (self.accepted / self.asset).write_bytes(png(pixels=bytes((4, 3, 2, 255)) * 4))
        self.assert_cli_failure(self.asset, "accepted sha256 does not match")

    def test_source_hash_mutation_is_rejected(self):
        self.ledger["assets"][0]["source_sha256"] = "0" * 64
        self.assert_cli_failure(self.asset, "source_sha256 does not match")

    def test_traversal_path_is_rejected_before_opening_a_file(self):
        self.ledger["assets"][0]["path"] = "../outside.png"
        self.assert_cli_failure("../outside.png", "unsafe archive member path")

    def test_unrecorded_png_is_rejected(self):
        self.write_asset(self.original, self.other)
        self.assert_cli_failure(self.other, "not recorded")

    def test_build_is_repeatable_preserves_originals_and_refuses_overwrite(self):
        runtime, packed, _ = self.validate()
        one, two = self.root / "one.zip", self.root / "two.zip"
        build_archive(self.archive, one, runtime, packed)
        build_archive(self.archive, two, runtime, packed)
        self.assertEqual(one.read_bytes(), two.read_bytes())
        with zipfile.ZipFile(self.archive) as base, zipfile.ZipFile(one) as candidate:
            for member in base.namelist():
                self.assertEqual(candidate.read(member), base.read(member), member)
            self.assertEqual(candidate.read("data/styles/cartoon/" + self.asset), self.original)
        with self.assertRaisesRegex(ArtError, "output must differ"):
            build_archive(self.archive, self.archive, runtime, packed)
        before = one.read_bytes()
        with self.assertRaisesRegex(ArtError, "refusing to overwrite"):
            build_archive(self.archive, one, runtime, packed)
        self.assertEqual(one.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
