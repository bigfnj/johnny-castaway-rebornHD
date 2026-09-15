"""Exercise the real inventory CLI on disposable archives only.

Run smoke before regression, then the compiled negative controls:
    python -B tests/test_art_inventory.py --smoke
    python -B tests/test_art_inventory.py
    python -B tests/test_art_inventory.py --mutations
"""

import argparse
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from test_art_tools import png


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/art_inventory.py"
WITNESS = None


class InventoryCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="johnny-inventory-cli-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = self.root / "fixture.zip"
        self.asset = "BMP/JOHNWALK.BMP/000.png"
        self.pixels = png()
        manifest = {"scale": 2, "BMP": {"JOHNWALK.BMP": {"numImages": 1, "images": [
            {"index": 0, "width": 1, "height": 1, "file": self.asset}]}}, "SCR": {}}
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("data/hd/manifest.json", json.dumps(manifest))
            archive.writestr("data/hd/" + self.asset, self.pixels)
        self.original = self.archive.read_bytes()

    def invoke(self, output=None, extra=()):
        command = [sys.executable, "-B", str(SOURCE), "--archive", str(self.archive)]
        if output is not None:
            command.extend(["--output", str(output)])
        environment = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
        result = subprocess.run(command + list(extra), cwd=self.root, env=environment,
                                capture_output=True, text=True, timeout=20)
        if WITNESS:
            lines = result.stdout.splitlines()
            self.assertEqual(lines.count(WITNESS), 1, "compiled inventory main must execute once")
            lines.remove(WITNESS)
            result.stdout = "\n".join(lines) + ("\n" if lines else "")
            print(WITNESS, flush=True)
        return result

    def assert_preserved(self):
        self.assertEqual(self.archive.read_bytes(), self.original, "source ZIP bytes changed")

    def assert_collision(self, output, extra=()):
        result = self.invoke(output, extra)
        self.assertEqual(result.returncode, 1,
                         "tools/art_inventory.py: source/output identity must be rejected before inventory")
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.splitlines(), [
            f"ERROR {output}: output must differ from the source archive {self.archive}"])
        self.assert_preserved()

    def assert_success(self, output=None, extra=()):
        result = self.invoke(output, extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout),
                         {"assets": 1, "screens": 0, "sprites": 1, "unique_png_bytes": 1})
        self.assert_preserved()
        if output is not None:
            report = json.loads(Path(output).read_text(encoding="utf-8"))
            self.assertEqual(report["assets"][0]["path"], self.asset)

    def test_distinct_new_output(self):
        self.assert_success(self.root / "reports/catalog.json")

    def test_stdout_only(self):
        self.assert_success()
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["fixture.zip"])

    def test_same_path(self):
        self.assert_collision(self.archive)

    def test_distinct_existing_output(self):
        output = self.root / "catalog.json"
        output.write_text("previous catalog", encoding="utf-8")
        self.assert_success(output)

    def test_relative_path_alias(self):
        self.assert_collision(Path("fixture.zip"))

    def test_hardlink_alias(self):
        output = self.root / "hardlink.json"
        try:
            output.hardlink_to(self.archive)
        except OSError as error:
            self.skipTest(f"hardlinks unavailable on this filesystem: {error}")
        self.assertNotEqual(output.resolve(), self.archive.resolve())
        self.assertTrue(output.samefile(self.archive))
        self.assert_collision(output)
        self.assertEqual(output.read_bytes(), self.original)

    def test_file_symlink_alias(self):
        output = self.root / "symlink.json"
        try:
            output.symlink_to(self.archive)
        except OSError as error:
            self.skipTest(f"file symlinks unavailable on this filesystem: {error}")
        self.assertTrue(output.is_symlink())
        self.assert_collision(output)
        self.assertTrue(output.is_symlink())

    def test_directory_symlink_alias(self):
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"directory symlinks unavailable on this filesystem: {error}")
        self.assertTrue(alias.is_symlink())
        self.assert_collision(alias / "fixture.zip")

    def test_identity_checked_before_archive_parsing(self):
        self.original = b"deliberately invalid ZIP to prove ordering"
        self.archive.write_bytes(self.original)
        self.assert_collision(self.archive)

    def test_identity_checked_before_export(self):
        exported = self.root / "exports"
        self.assert_collision(self.archive, ["--export", str(exported)])
        self.assertFalse(exported.exists(), "identity rejection must precede reference export")

    def test_distinct_output_with_export(self):
        exported = self.root / "exports"
        self.assert_success(self.root / "catalog.json", ["--export", str(exported)])
        self.assertEqual((exported / self.asset).read_bytes(), self.pixels)


def mutations():
    original = SOURCE.read_text(encoding="utf-8")
    anchor = "if source == output or (output.exists() and source.samefile(output)):"
    cases = [
        ("removed_identity_guard", "test_same_path", "if False:"),
        ("removed_file_identity", "test_hardlink_alias", "if source == output:"),
    ]
    with tempfile.TemporaryDirectory(prefix="johnny-inventory-mutants-") as temporary:
        root = Path(temporary)
        for name, case, replacement in cases:
            if original.count(anchor) != 1 or original.count("def main(argv=None):\n") != 1:
                raise AssertionError("inventory mutation anchors must be unique")
            witness = "WITNESS inventory-cli:" + name
            changed = original.replace(anchor, replacement).replace(
                "def main(argv=None):\n", "def main(argv=None):\n    print(" + repr(witness) + ")\n")
            source, artifact = root / (name + ".py"), root / (name + ".pyc")
            source.write_text(changed, encoding="utf-8")
            artifact.write_bytes(b"not bytecode")
            os.utime(artifact, ns=(1_000_000_000, 1_000_000_000))
            before = artifact.stat().st_mtime_ns
            py_compile.compile(str(source), cfile=str(artifact), doraise=True)
            if artifact.stat().st_mtime_ns <= before:
                raise AssertionError("compiled inventory artifact timestamp did not advance")
            result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()),
                                     "--source", str(artifact), "--case", case, "--witness", witness],
                                    capture_output=True, text=True, timeout=30)
            expected = "tools/art_inventory.py: source/output identity must be rejected before inventory"
            if (result.returncode != 1 or result.stdout.splitlines().count(witness) != 1
                    or result.stderr.count("FAIL: " + case) != 1
                    or "FAILED (failures=1)" not in result.stderr or expected not in result.stderr):
                raise AssertionError(f"{name}: expected one witnessed identity failure\n"
                                     + result.stdout + result.stderr)
            print(json.dumps({"file": "tools/art_inventory.py", "mutation": name, "status": "FIRED",
                              "case": case, "rebuilt": True, "witness": witness,
                              "failure": expected}), flush=True)


def main():
    global SOURCE, WITNESS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--mutations", action="store_true")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--case")
    parser.add_argument("--witness")
    args = parser.parse_args()
    SOURCE, WITNESS = args.source, args.witness
    if args.mutations:
        mutations()
        return 0
    names = ([args.case] if args.case else ["test_distinct_new_output", "test_stdout_only", "test_same_path"]
             if args.smoke else unittest.defaultTestLoader.getTestCaseNames(InventoryCliTests))
    suite = unittest.TestSuite(InventoryCliTests(name) for name in names)
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
