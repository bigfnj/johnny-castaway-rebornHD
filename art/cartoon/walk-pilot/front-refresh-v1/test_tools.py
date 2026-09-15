"""Bounded export/review smoke, regression and executed mutation checks."""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
e = r = None


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="front-art-tools-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.approved = {frame: "approved" for frame in e.FRAMES}

    def candidate(self, preview_only=False, outside=False, frame=28):
        # Deliberately artificial test pixels, never visual-review artwork.
        image = Image.new("RGBA", (1024, 1536))
        draw = ImageDraw.Draw(image)
        draw.rectangle((380, 40, 390, 50), fill=(255, 255, 255, 255))
        draw.rectangle((400, 200, 500, 1400), fill=(180, 120, 50, 255))
        if outside:
            image.putpixel((0, 1400), (255, 0, 0, 255))
        source = self.work / "TEST-PIXELS.png"
        image.save(source)
        return e.prepare({**self.approved, frame: str(source)}, preview_only)

    def test_smoke_export(self):
        recipe, inputs, images, report = e.prepare(self.approved)
        self.assertEqual(len(recipe["frames"]), 6)
        for row in recipe["frames"]:
            self.assertEqual(images[row["path"]], inputs[row["baseline"]], f"exact retained PNG:{row['frame']}")
        self.assertTrue(report["runtime_fit_all_source_centers"])

    def test_reproduce_from_frozen_inputs(self):
        result = self.candidate()
        output = self.work / "export"
        e.write_output(output, *result)
        repeated = e.reproduce(output / "recipe.json")
        self.assertEqual(result, repeated)
        self.assertEqual([row["frame"] for row in repeated[0]["frames"] if row["mode"] == "generated"], [28])

    def test_source_identity(self):
        recipe, inputs, _, _ = self.candidate()
        recipe["frames"][4]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "^source-identity:028$"):
            e.render(recipe, inputs)

    def test_input_identity(self):
        recipe, inputs, _, _ = e.prepare(self.approved)
        inputs["inputs/walk-data.h"] += b"\n"
        with self.assertRaisesRegex(ValueError, "^frozen-input-identity$"):
            e.render(recipe, inputs)

    def test_registration(self):
        recipe, inputs, _, _ = self.candidate()
        recipe["frames"][4]["affine_forward"][2] += 1
        with self.assertRaisesRegex(ValueError, "^fixed-registration:028$"):
            e.render(recipe, inputs)

    def test_runtime_canvas(self):
        recipe, inputs, _, _ = e.prepare(self.approved)
        recipe["frames"][0]["runtime_canvas"] = [64, 148]
        with self.assertRaisesRegex(ValueError, "^runtime-canvas:024$"):
            e.render(recipe, inputs)

    def test_pillow_contract(self):
        recipe, inputs, _, _ = e.prepare(self.approved)
        recipe["pillow_version"] = "deliberately-different"
        with self.assertRaisesRegex(ValueError, "^family-render-contract$"):
            e.render(recipe, inputs)

    def test_runtime_overhang(self):
        with self.assertRaisesRegex(ValueError, "^runtime-overhang:028$"):
            self.candidate(outside=True)

    def test_preview_overhang_is_explicit(self):
        recipe, inputs, images, report = self.candidate(preview_only=True, outside=True)
        self.assertFalse(report["runtime_fit_all_source_centers"])
        self.assertFalse(report["runtime_sprites_written"])
        self.assertTrue(all(name.startswith("padded/") for name in images))
        self.assertEqual(images, e.render(recipe, inputs)[0])

    def test_output_identity(self):
        recipe, inputs, _, _ = e.prepare(self.approved)
        recipe["output_sha256"]["padded/024.png"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "^recorded-output-identity$"):
            e.render(recipe, inputs)

    def test_existing_output_is_preserved(self):
        result = e.prepare(self.approved)
        output = self.work / "export"
        output.mkdir()
        sentinel = output / "sentinel.txt"
        sentinel.write_bytes(b"preserve")
        with self.assertRaisesRegex(ValueError, "^output-already-exists$"):
            e.write_output(output, *result)
        self.assertEqual(sentinel.read_bytes(), b"preserve")
        self.assertEqual(list(output.iterdir()), [sentinel])

    def test_route_contract(self):
        source = (e.ROOT / "src/data/walk_data.h").read_bytes()
        rows = r.route(source)
        self.assertEqual(len(rows), 23)
        self.assertEqual(rows[0], {"flip": 0, "frame": 28, "x": 394, "y": 212, "duration_ms": 120})
        self.assertEqual([row["frame"] for row in rows[-2:]], [25, 27])

    def test_wrong_route_refused(self):
        source = (e.ROOT / "src/data/walk_data.h").read_bytes()
        old = b"{ 0, 301, 242, 27 }"
        self.assertEqual(source.count(old), 1)
        with self.assertRaisesRegex(ValueError, "^original-e-to-a-travel-contract$"):
            r.route(source.replace(old, b"{ 0, 301, 242, 26 }"))

    def browser(self, exercise, result=None):
        from playwright.sync_api import sync_playwright
        result = e.prepare(self.approved) if result is None else result
        exported, review = self.work / "export", self.work / "review"
        e.write_output(exported, *result)
        data, evidence = r.build(exported, review)
        self.assertEqual(len(data["timeline"]), 24)
        self.assertEqual(data["timeline"][-1], {**data["timeline"][-2], "start_ms": 2760, "duration_ms": 1000, "hold": True})
        for name, checksum in evidence["files"].items():
            self.assertEqual(e.sha((review / name).read_bytes()), checksum)
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(review)))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1600, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.add_init_script("window.__frames=[];window.requestAnimationFrame=callback=>{window.__frames.push(callback);return window.__frames.length};window.__step=t=>{const callbacks=window.__frames.splice(0);callbacks.forEach(callback=>callback(t));};")
                page.goto(f"http://127.0.0.1:{server.server_port}/review.html")
                page.wait_for_function("window.frontReviewState && window.frontReviewState.ready")
                self.assertEqual(errors, [])
                exercise(page, data)
            finally:
                browser.close()

    def test_smoke_browser(self):
        def check(page, data):
            self.assertEqual(page.locator("#status").inner_text(), "Pose 1 / 23 | JOHNWALK.BMP 028 | x 394, y 212")
            self.assertIn("not Johnny's native standing arrival", page.locator("main").inner_text())
            equal = page.evaluate("['current','revised'].map(id=>Array.from(document.getElementById(id).getContext('2d').getImageData(0,0,document.getElementById(id).width,document.getElementById(id).height).data))")
            self.assertEqual(equal[0], equal[1], "unchanged control must render equal pixels")
        self.browser(check)

    def test_labels_follow_explicit_selection(self):
        def check(page, data):
            self.assertEqual(data["revised_frames"], [24])
            self.assertEqual(page.locator("#changes").inner_text(), "Revised frames: 024.")
            self.assertEqual(page.locator("main > p").first.inner_text(),
                "Watch the feet and the turn of Johnny's body. Only the frames listed below as revised use new drawings.")
        self.browser(check, self.candidate(frame=24))

    def test_browser_controls(self):
        def check(page, data):
            page.evaluate("window.__step(0);window.__step(121)")
            self.assertEqual(page.evaluate("frontReviewState.index"), 1, "normal timer advances a stored pose")
            page.locator("#play").click()
            page.evaluate("window.__step(500);window.__step(1000)")
            self.assertEqual(page.evaluate("frontReviewState.index"), 1)
            page.locator("#next").click()
            self.assertEqual(page.evaluate("frontReviewState.frame"), 24)
            page.locator("#previous").click()
            self.assertEqual(page.evaluate("frontReviewState.frame"), 29)
            page.locator("#speed").select_option("0.5")
            page.locator("#play").click()
            page.evaluate("window.__step(2000);window.__step(2120)")
            self.assertEqual(page.evaluate("frontReviewState.index"), 1)
            page.evaluate("window.__step(2242)")
            self.assertEqual(page.evaluate("frontReviewState.index"), 2)
            page.locator("#repeat").uncheck()
            page.evaluate("window.__step(20000)")
            self.assertTrue(page.evaluate("frontReviewState.hold"))
            self.assertFalse(page.evaluate("frontReviewState.playing"))
            self.assertIn("Diagnostic endpoint hold", page.locator("#status").inner_text())
            page.locator("#next").click()
            self.assertEqual(page.evaluate("frontReviewState.index"), 0)
        self.browser(check)


MUTATIONS = [
    ("export.py", "test_input_identity", 'set(inputs) == set(recipe["input_sha256"]) and all(sha(raw) == recipe["input_sha256"][name] for name, raw in inputs.items())', "True"),
    ("export.py", "test_source_identity", 'sha(inputs[row["source"]]) == row["source_sha256"]', "True"),
    ("export.py", "test_registration", 'all(math.isclose(a, b, rel_tol=0, abs_tol=1e-12) for a, b in zip(affine, row["affine_forward"]))', "True"),
    ("export.py", "test_runtime_canvas", 'row["runtime_canvas"] == canvas == previous["runtime_canvas"]', "True"),
    ("export.py", "test_pillow_contract", 'recipe["pillow_version"] == PIL.__version__', "True"),
    ("export.py", "test_runtime_overhang", 'recipe["preview_only"] or fits', "True"),
    ("export.py", "test_output_identity", '{name: sha(raw) for name, raw in sorted(images.items())} == recipe["output_sha256"]', "True"),
    ("export.py", "test_smoke_export", 'runtime = inputs[row["baseline"]]', 'runtime = png(Image.new("RGBA", canvas))'),
    ("review.py", "test_wrong_route_refused", '[row["frame"] for row in rows] == expected', "True"),
    ("review.py", "test_browser_controls", 'position+=(time-last)*Number($(\'speed\').value);', 'position+=0;'),
    ("review.py", "test_labels_follow_explicit_selection", 'Only the frames listed below as revised use new drawings.',
     'Frames 024–027 retain the approved Cartoon artwork; revised frames are listed below.'),
]


def mutations():
    with tempfile.TemporaryDirectory(prefix="front-art-mutants-") as temporary:
        for number, (name, case, old, new) in enumerate(MUTATIONS):
            folder = Path(temporary) / str(number)
            folder.mkdir()
            for helper in ("export.py", "review.py"):
                source = (HERE / helper).read_text(encoding="utf-8")
                if helper == name:
                    if source.count(old) != 1:
                        raise AssertionError("unique mutation anchor: " + case)
                    source = source.replace(old, new)
                (folder / helper).write_text(source, encoding="utf-8")
            witness = hashlib.sha256((folder / name).read_bytes()).hexdigest()
            run = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--module-directory", str(folder), "--case", case], capture_output=True, text=True, timeout=90)
            output = run.stdout + run.stderr
            if not (run.returncode == 1 and f"WITNESS {name} {witness}" in output and f"FAIL: {case}" in output
                    and "Ran 1 test" in output and "FAILED (failures=1)" in output):
                raise AssertionError("mutation must produce one witnessed failure: " + case + "\n" + output)
            print(f"FIRED {name} {case} source={witness}", flush=True)


def main():
    global e, r
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("smoke", "regression"), default="smoke")
    parser.add_argument("--mutations", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--module-directory", type=Path, default=HERE)
    args = parser.parse_args()
    e = load(args.module_directory / "export.py", "front_export_test")
    r = load(args.module_directory / "review.py", "front_review_test")
    e.HERE, e.ROOT = HERE, HERE.parents[3]
    # Function defaults are bound at import, including in isolated mutants.
    e.prepare.__defaults__ = (False, e.ROOT, e.HERE)
    for name in ("export.py", "review.py"):
        print(f"WITNESS {name} {hashlib.sha256((args.module_directory / name).read_bytes()).hexdigest()}", flush=True)
    names = [args.case] if args.case else [name for name in unittest.defaultTestLoader.getTestCaseNames(ToolsTests)
        if name.startswith("test_smoke") == (args.phase == "smoke")]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(ToolsTests(name) for name in names))
    if not result.wasSuccessful():
        return 1
    if args.mutations:
        mutations()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
