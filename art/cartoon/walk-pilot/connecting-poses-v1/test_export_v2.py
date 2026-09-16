"""Version2 connecting export checks, explicit Y derivation and prior-byte parity.

Adapted from the frozen profile-walk-v1 tests. Original references establish
all three geometries; synthetic opaque/partial/transparent pixels test filtering.

Run --phase smoke before --phase regression --mutation-check with one --recipe
and --output directory. Synthetic pixels are test fixtures, not painted art.
"""
import argparse
import ast
import copy
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
CANVASES = {9: (80, 148), 10: (80, 148), 12: (80, 146)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path, name="arrival_export"):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cli(script, recipe, output, frame, preview=False, source=None, prepare=False):
    command = [sys.executable, "-B", str(script), "--output", str(output)]
    if frame is not None:
        command += ["--frame", str(frame)]
    if recipe is not None:
        command += ["--recipe", str(recipe)]
    if source is not None:
        command += ["--source", source]
    if prepare:
        command.append("--prepare")
    if preview:
        command.append("--preview-only")
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert "WITNESS export_v2.py SHA256=" + sha(script.read_bytes()) in result.stdout
    return result


def synthetic(path, top=40, size=(1024, 1536), overhang=False):
    image = Image.new("RGBA", size, (250, 0, 200, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((300, top, 470, 1420), fill=(70, 150, 200, 255))
    draw.rectangle((290, top + 5, 299, 1415), fill=(220, 90, 30, 60))
    if overhang:
        draw.rectangle((1000, top + 100, 1023, top + 110), fill=(40, 60, 80, 255))
    image.save(path)


def guards(frame):
    return {
        "reference-source": f"reference-file:{frame:03}-source.json",
        "reference-native": f"reference-file:{frame:03}-original-native.png",
        "reference-nearest8": f"reference-file:{frame:03}-original-nearest8.png",
        "source-path": f"source-path:{frame:03}",
        "prepare-canvas": f"prepare-canvas:{frame:03}",
        "cap-outline": f"cap-outline:{frame:03}",
        "recipe-reference": f"recipe-reference:{frame:03}",
        "render-contract": f"render-contract:{frame:03}",
        "recipe-frame": f"recipe-frame:{frame:03}",
        "source-identity": f"source-identity:{frame:03}",
        "source-canvas": f"source-canvas:{frame:03}",
        "fixed-registration": f"fixed-registration:{frame:03}",
        "fixed-y-registration": f"fixed-registration:{frame:03}",
        "runtime-canvas": f"runtime-canvas:{frame:03}",
        "runtime-overhang": f"runtime-overhang:{frame:03}",
        "allowed-frame": "allowed-frame",
        "output-exists": "output-already-exists",
        "explicit-input": "explicit-input",
    }
POSITIVES = ["normal-synthetic", "preview-overhang", "recipe-byte-identity", "legacy-filter-parity",
             "explicit-prepare", "original-cap-target", "all-frame-configurations",
             "target-y-derivation", "prior-pose-byte-compatibility"]


def check_case(name, script, source_recipe, legacy_path, scratch, frame):
    module = load(script)
    print("WITNESS export_v2.py SHA256=" + sha(script.read_bytes()), flush=True)
    recipe = copy.deepcopy(json.loads(source_recipe.read_bytes()))
    authoring = script.parent
    original_source = authoring / recipe["frames"][0]["source"]
    original_bytes = original_source.read_bytes()
    if name in POSITIVES:
        if name == "target-y-derivation":
            raw = (HERE / "010-connecting-v5.png").read_bytes()
            assert sha(raw) == "cceef504e777f1fe9f794c35832c7c6e4273526fabc49b27a7d2032ae4056729"
            with Image.open(io.BytesIO(raw)) as image:
                alpha = image.getchannel("A")
                b = alpha.point(lambda a: 255 if a >= 8 else 0).getbbox()
                cap_y = module.measure_cap(image, 10)[1]
                lower = -(Fraction(2*b[1]+1, 2)-cap_y)/10
                upper = 148-(Fraction(2*b[3]-1, 2)-cap_y)/10
                full_lower = -(Fraction(b[1])-cap_y)/10
                full_upper = 148-(Fraction(b[3])-cap_y)/10
                assert (lower, upper) == (Fraction(-1,20), Fraction(3,20))
                assert (full_lower, full_upper) == (0, Fraction(1,10))
                target = Fraction(str(module.TARGETS[10][1]))
                assert target == Fraction(1,10), "declared010 Y margin changed"
                assert lower <= target < upper and full_lower <= target <= full_upper
            module.HERE = HERE
            images, observed = module.render(module.prepare(10, "010-connecting-v5.png"), 10)
            assert observed["runtime_fit_all_source_centers"]
            padded = Image.open(io.BytesIO(images["padded/010.png"]))
            a = padded.getchannel("A")
            bounds = a.point(lambda v: 255 if v >= 8 else 0).getbbox()
            assert [bounds[0]-64,bounds[1]-64,bounds[2]-64,bounds[3]-64] == [4,0,66,148]
            outside = [a.getpixel((x,y)) for y in range(padded.height) for x in range(padded.width)
                       if not (64 <= x < 144 and 64 <= y < 212)]
            assert max(outside) == 4 and sum(v > 0 for v in outside) == 25
            assert (HERE / "010-connecting-v5.png").read_bytes() == raw
            return
        if name == "prior-pose-byte-compatibility":
            module.HERE = HERE
            for selected in (9, 12):
                frozen = json.loads((HERE / f"exports/{selected:03}-v1/recipe.json").read_bytes())
                expected = json.loads((HERE / f"exports/{selected:03}-v1/export-report.json").read_bytes())
                images, observed = module.render(frozen, selected)
                assert observed["runtime_fit_all_source_centers"]
                assert {path: sha(raw) for path, raw in images.items()} == expected["outputs_sha256"], "prior009/012 bytes changed"
            return
        if name == "all-frame-configurations":
            synthetic(authoring / "fixture.png")
            for selected in (9, 10, 12):
                with Image.open(authoring / "reference" / f"{selected:03}-original-native.png") as native:
                    alpha = native.getchannel("A")
                    y = alpha.getbbox()[1]
                    xs = [x for x in range(native.width) if alpha.getpixel((x, y)) >= 128]
                    assert module.TARGETS[selected] == [min(xs) + max(xs) + 1, .10 if selected == 10 else .25], "original cap registration changed"
                    assert tuple(n * 2 for n in native.size) == CANVASES[selected]
                configured = module.prepare(selected, "fixture.png")
                outputs, report = module.render(configured, selected)
                assert report["runtime_fit_all_source_centers"]
                with Image.open(io.BytesIO(outputs[f"BMP/JOHNWALK.BMP/{selected:03}.png"])) as image:
                    assert image.mode == "RGBA" and image.size == CANVASES[selected]
            return
        if name in ("normal-synthetic", "preview-overhang", "legacy-filter-parity"):
            synthetic(authoring / "fixture.png", overhang=name == "preview-overhang")
            recipe = module.prepare(frame, "fixture.png")
        if name == "original-cap-target":
            with Image.open(authoring / "reference" / f"{frame:03}-original-native.png") as native:
                alpha = native.getchannel("A")
                y = alpha.getbbox()[1]
                xs = [x for x in range(native.width) if alpha.getpixel((x, y)) >= 128]
                # Independent original-pixel observation, not a copied recipe value.
                assert module.TARGETS[frame] == [min(xs) + max(xs) + 1, .10 if frame == 10 else .25], "original cap registration changed"
        elif name == "explicit-prepare":
            output = scratch / "explicit-prepare"
            result = cli(script, None, output, frame, source=original_source.name, prepare=True)
            assert result.returncode == 0, result.stderr
            expected, _ = module.render(module.prepare(frame, original_source.name), frame)
            for relative, data in expected.items():
                assert (output / relative).read_bytes() == data
        elif name == "recipe-byte-identity":
            raw = (json.dumps(recipe, indent=4) + "\r\n").encode("utf-8")
            path = scratch / "spaced-recipe.json"
            path.write_bytes(raw)
            output = scratch / "cli"
            result = cli(script, path, output, frame)
            assert result.returncode == 0, result.stderr
            assert (output / "recipe.json").read_bytes() == raw
            assert json.loads((output / "export-report.json").read_bytes())["recipe_sha256"] == sha(raw)
        else:
            images, report = module.render(recipe, frame, name == "preview-overhang")
            if name == "preview-overhang":
                assert set(images) == {f"padded/{frame:03}.png"}
                assert report["preview_only"] and not report["runtime_sprites_written"]
                assert not report["runtime_fit_all_source_centers"]
            else:
                assert set(images) == {f"padded/{frame:03}.png", f"BMP/JOHNWALK.BMP/{frame:03}.png"}
                assert report["runtime_fit_all_source_centers"]
                with Image.open(io.BytesIO(images[f"BMP/JOHNWALK.BMP/{frame:03}.png"])) as image:
                    assert image.mode == "RGBA" and image.size == CANVASES[frame]
                    assert image.getchannel("A").getextrema()[1] == 255
                if name == "legacy-filter-parity":
                    legacy = load(legacy_path, "frozen017_export")
                    legacy.HERE = authoring
                    # Reuse frozen 017 filter implementation with this fixture's
                    # geometry. No production references or legacy files change.
                    legacy.FRAME = frame
                    legacy.TARGET = module.TARGETS[frame].copy()
                    legacy.reference = lambda: module.reference(frame)
                    old_recipe = legacy.prepare("fixture.png")
                    expected, _ = legacy.render(old_recipe, False)
                    expected = {name.replace("017", f"{frame:03}"): data for name, data in expected.items()}
                    assert images == expected, "established premultiplied filter math changed"
        assert original_source.read_bytes() == original_bytes
        return

    label = guards(frame)[name]
    action = lambda: module.render(recipe, frame, False)
    if name.startswith("reference-") and name != "recipe-reference":
        filename = label.split(":", 1)[1]
        path = authoring / "reference" / filename
        path.write_bytes(path.read_bytes() + b"\n")  # Still valid JSON/PNG; exact-byte identity must reject.
    elif name == "source-path":
        (authoring.parent / "outside.png").write_bytes(original_bytes)
        recipe["frames"][0]["source"] = "../outside.png"
    elif name == "prepare-canvas":
        synthetic(authoring / "fixture.png", size=(1023, 1536))
        action = lambda: module.prepare(frame, "fixture.png")
    elif name == "cap-outline":
        synthetic(authoring / "fixture.png", top=350)
        action = lambda: module.prepare(frame, "fixture.png")
    elif name == "recipe-reference":
        recipe["reference_hashes"] = module.REFERENCE_HASHES[9 if frame != 9 else 10].copy()
    elif name == "render-contract":
        recipe["scale_exact"]["denominator"] = 11
    elif name == "recipe-frame":
        recipe["frames"][0]["frame"] = 9 if frame != 9 else 10
    elif name == "source-identity":
        recipe["frames"][0]["source_sha256"] = "0" * 64
    elif name == "source-canvas":
        recipe["frames"][0]["generated_canvas"] = [1024, 1535]
    elif name == "fixed-registration":
        recipe["frames"][0]["affine_forward"][1] = .01
    elif name == "fixed-y-registration":
        recipe["cap_target_hd"][1] += .15
        recipe["frames"][0]["cap_target_hd"][1] += .15
        recipe["frames"][0]["affine_forward"][5] += .15
    elif name == "runtime-canvas":
        recipe["frames"][0]["runtime_canvas"][1] += 2
    elif name == "runtime-overhang":
        synthetic(authoring / "fixture.png", overhang=True)
        recipe = module.prepare(frame, "fixture.png")
    elif name == "allowed-frame":
        for invalid in (None, -1, 0, 1, 8, 11, 13, 16, 17):
            output = scratch / ("invalid-frame-" + str(invalid))
            result = cli(script, source_recipe, output, invalid)
            assert result.returncode == 1 and result.stderr.strip() == "FAIL " + label, label
            assert not output.exists()
        return
    elif name == "explicit-input":
        for index, (prepare, source, path) in enumerate((
            (False, None, None),
            (True, None, None),
            (False, original_source.name, source_recipe),
            (True, original_source.name, source_recipe),
        )):
            output = scratch / ("invalid-input-" + str(index))
            result = cli(script, path, output, frame, source=source, prepare=prepare)
            assert result.returncode == 1 and result.stderr.strip() == "FAIL " + label, label
            assert not output.exists(), "invalid inputs must not create output"
        return
    elif name == "output-exists":
        output = scratch / "existing"
        output.mkdir()
        (output / "sentinel").write_bytes(b"preserve me")
        result = cli(script, source_recipe, output, frame)
        assert result.returncode == 1 and result.stderr.strip() == "FAIL " + label, label
        assert list(output.iterdir()) == [output / "sentinel"]
        assert (output / "sentinel").read_bytes() == b"preserve me"
        return
    caught = None
    try:
        action()
    except ValueError as error:
        caught = str(error)
    assert caught == label, "expected refusal: " + label


def mutation(source, label):
    calls = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "require"
             and ((isinstance(node.args[-1], ast.Constant) and node.args[-1].value == label)
                  or (isinstance(node.args[-1], ast.JoinedStr) and
                      isinstance(node.args[-1].values[0], ast.Constant) and
                      node.args[-1].values[0].value == label.split(":")[0] + ":")
                  or (label.startswith("reference-file:") and
                      ast.get_source_segment(source, node.args[-1]) == '"reference-file:" + name'))]
    assert len(calls) == 1, "mutant must replace exactly one executed condition: " + label
    arg = calls[0].args[0]
    lines = source.splitlines(keepends=True)
    begin = sum(len(line) for line in lines[:arg.lineno - 1]) + arg.col_offset
    end = sum(len(line) for line in lines[:arg.end_lineno - 1]) + arg.end_col_offset
    return source[:begin] + "True" + source[end:]


def isolated_case(name, code, recipe, legacy, output, frame):
    with tempfile.TemporaryDirectory(prefix=name + "-", dir=output) as tmp:
        scratch = Path(tmp)
        authoring = scratch / "authoring"
        authoring.mkdir()
        shutil.copytree(HERE / "reference", authoring / "reference")
        source = json.loads(recipe.read_bytes())["frames"][0]["source"]
        shutil.copyfile(HERE / source, authoring / source)
        script = authoring / "export_v2.py"
        script.write_text(code, encoding="utf-8", newline="\n")
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()),
            "--case", name, "--export", str(script), "--recipe", str(recipe),
            "--legacy", str(legacy), "--output", str(scratch), "--frame", str(frame)],
            capture_output=True, text=True, timeout=30)
        witness = "WITNESS export_v2.py SHA256=" + sha(script.read_bytes())
        assert witness in result.stdout, name + ": missing executed source witness"
        return result, sha(script.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=int, choices=(9, 10, 12), required=True)
    parser.add_argument("--phase", choices=("smoke", "regression"))
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mutation-check", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--export", type=Path, default=HERE / "export_v2.py")
    parser.add_argument("--legacy", type=Path, default=HERE.parent / "front-arrival-v1/export.py")
    args = parser.parse_args()
    frame = args.frame
    args.recipe = args.recipe.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.case:
        assert args.case in guards(frame) or args.case in POSITIVES
        def test(self):
            check_case(args.case, args.export, args.recipe, args.legacy, args.output, frame)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(type("ConnectingExport", (unittest.TestCase,),
            {"test_" + args.case.replace("-", "_"): test}))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    assert args.phase, "select smoke or regression"
    code = args.export.read_text(encoding="utf-8")
    inputs = {"export": sha(args.export.read_bytes()), "test": sha(Path(__file__).read_bytes()),
              "recipe": sha(args.recipe.read_bytes()), "legacy_export": sha(args.legacy.read_bytes()), "selected_frame": frame}
    if args.phase == "smoke":
        module = load(args.export)
        original = module.reference(frame)
        with Image.open(HERE / "reference" / f"{frame:03}-original-native.png") as native, Image.open(HERE / "reference" / f"{frame:03}-original-nearest8.png") as zoom:
            assert native.mode == zoom.mode == "RGBA"
            assert sha(native.tobytes()) == original["rgba_sha256"]
            assert zoom.size == tuple(n * 8 for n in original["canvas"]) and zoom.tobytes() == native.resize(zoom.size, Image.Resampling.NEAREST).tobytes()
        print(f"SMOKE PASS exact original{frame:03} reference and nearest8", flush=True)
        baseline = args.output / "smoke-export"
        r = cli(args.export, args.recipe, baseline, frame)
        assert r.returncode == 0, r.stderr
        with Image.open(baseline / f"BMP/JOHNWALK.BMP/{frame:03}.png") as image:
            assert image.mode == "RGBA" and image.size == CANVASES[frame] and image.getchannel("A").getbbox()
        assert len(list(baseline.rglob("*.png"))) == 2
        print(f"SMOKE PASS exact{frame:03} fixed-canvas export", flush=True)
        repeated = args.output / "smoke-repeated"
        r = cli(args.export, args.recipe, repeated, frame)
        assert r.returncode == 0, r.stderr
        for relative in (f"BMP/JOHNWALK.BMP/{frame:03}.png", f"padded/{frame:03}.png"):
            assert (baseline / relative).read_bytes() == (repeated / relative).read_bytes()
        report = {"inputs_sha256": inputs, "phase": "smoke", "passed": 3}
        print("SMOKE PASS repeated PNG bytes", flush=True)
    else:
        smoke = json.loads((args.output / "smoke.json").read_bytes())
        assert smoke["passed"] == 3 and smoke["inputs_sha256"] == inputs, "fresh matching smoke must precede regression"
        cases = list(guards(frame)) + POSITIVES
        records = []
        for name in cases:
            result, digest = isolated_case(name, code, args.recipe, args.legacy, args.output, frame)
            assert result.returncode == 0 and "\nOK\n" in result.stderr, name + ": " + result.stderr
            records.append(name)
        print(f"REGRESSION PASS {len(records)} cases", flush=True)
        mutants = []
        if args.mutation_check:
            for name, label in guards(frame).items():
                changed = mutation(code, label)
                result, digest = isolated_case(name, changed, args.recipe, args.legacy, args.output, frame)
                assert result.returncode == 1 and "FAILED (failures=1)" in result.stderr and "ERROR:" not in result.stderr, name + ": " + result.stderr
                assert "FAIL: test_" + name.replace("-", "_") in result.stderr
                mutants.append({"case": name, "result": "FIRED", "failure_count": 1, "executed_source_sha256": digest})
            old = 'source.convert("RGBa")'
            assert code.count(old) == 1
            result, digest = isolated_case("legacy-filter-parity", code.replace(old, 'source.convert("RGBA")'), args.recipe, args.legacy, args.output, frame)
            assert result.returncode == 1 and "FAILED (failures=1)" in result.stderr and "ERROR:" not in result.stderr
            assert "established premultiplied filter math changed" in result.stderr
            mutants.append({"case": "premultiplied-filter", "result": "FIRED", "failure_count": 1, "executed_source_sha256": digest})
            target = load(args.export).TARGETS[frame][0]
            margin = ".10" if frame == 10 else ".25"
            old = f"{frame}: [{target}, {margin}]"
            assert code.count(old) == 1
            result, digest = isolated_case("original-cap-target", code.replace(old, f"{frame}: [{target - 1}, {margin}]"), args.recipe, args.legacy, args.output, frame)
            assert result.returncode == 1 and "FAILED (failures=1)" in result.stderr and "ERROR:" not in result.stderr
            assert "original cap registration changed" in result.stderr
            mutants.append({"case": "original-cap-target", "result": "FIRED", "failure_count": 1, "executed_source_sha256": digest})
            old = "10: [35, .10]"
            assert code.count(old) == 1
            result, digest = isolated_case("target-y-derivation", code.replace(old, "10: [35, .25]"), args.recipe, args.legacy, args.output, frame)
            assert result.returncode == 1 and "FAILED (failures=1)" in result.stderr and "ERROR:" not in result.stderr
            assert "declared010 Y margin changed" in result.stderr
            mutants.append({"case": "declared-target-y", "result": "FIRED", "failure_count": 1, "executed_source_sha256": digest})
            print(f"MUTATIONS PASS {len(mutants)} executed controls, each one named failure", flush=True)
        report = {"inputs_sha256": inputs, "phase": "regression", "passed": len(records), "cases": records,
                  "mutations": mutants, "mutation_status": "executed" if args.mutation_check else "NOT RUN: use --mutation-check"}
    report["limit"] = "Authoring-only checks; no anatomical correctness or original-engine playback parity claim. Source mutations execute in fresh python -B processes."
    (args.output / (args.phase + ".json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
