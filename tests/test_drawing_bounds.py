"""Headless sanitizer checks for real drawing, SCR readers and BMP name ownership."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def build(root, output, sanitize=True):
    root, output = Path(root), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("unbuilt probe")
    os.utime(output, (1, 1))
    before = output.stat().st_mtime_ns
    command = ["cc", "-std=gnu11", "-DPLATFORM_LINUX", "-O1", "-g", "-no-pie",
               "-ffunction-sections", "-fdata-sections",
               "-I" + str(root / "platform"), "-I" + str(root / "src/engine"),
               str(root / "tests/test_drawing_bounds.c"), str(root / "src/engine/graphics.c"),
               str(root / "src/engine/utils.c"), str(root / "platform/platform_linux.c"),
               "-Wl,--gc-sections", "-Wl,--wrap=malloc", "-Wl,--wrap=calloc", "-Wl,--wrap=free",
               "-lX11", "-lasound", "-pthread", "-o", str(output)]
    if sanitize:
        command += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    p = subprocess.run(command, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    assert output.stat().st_mtime_ns > before, "probe artifact timestamp did not advance"


def run(exe, case, directory, extra=()):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "dump/SCR").mkdir(parents=True, exist_ok=True)
    p = subprocess.run([str(exe), case, *map(str, extra)], cwd=directory,
                       capture_output=True, text=True, timeout=20)
    output = p.stdout + p.stderr
    assert f"WITNESS graphics.c drawing {case} BEGIN" in output, output
    return p.returncode, output


def copy_source(source, target):
    for folder in ("src/engine", "platform", "tests"):
        (target / folder).mkdir(parents=True, exist_ok=True)
        for path in (source / folder).glob("*"):
            if path.suffix in (".c", ".h"):
                shutil.copyfile(path, target / folder / path.name)


def replace(path, old, new, count=1):
    text = path.read_text()
    assert text.count(old) == count, (str(path), old, text.count(old))
    path.write_text(text.replace(old, new))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=["smoke", "regression", "all"], default="all")
    parser.add_argument("--mutations", action="store_true", help="manual rebuilt negative controls")
    args = parser.parse_args()
    args.source, args.output = args.source.resolve(), args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "drawing-probe"
    build(args.source, exe)
    cases = ["circle-fill", "even-scr"] if args.phase == "smoke" else [
        "circle-outline", "empty-bmp-reload", "empty-bmp-alias", "odd-scr", "odd-dump", "even-dump"]
    if args.phase == "all": cases = ["circle-fill", "even-scr", *cases]
    records = []
    for case in cases:
        code, output = run(exe, case, args.output / case)
        if case.startswith("odd-"):
            assert code == 1 and "SCR 'ODD.SCR': unsupported odd width 3" in output, output
            assert "refused before style/decode allocation" in output, output
            assert not (args.output / case / "dump/SCR/ODD.SCR.xpm").exists()
        else:
            assert code == 0 and f"drawing {case} PASS" in output, output
        if case == "even-dump":
            data = (args.output / case / "dump/SCR/EVEN.SCR.xpm").read_bytes()
            assert b'"4 2 16 1"' in data and b'"1234",\n"5678"}' in data
        records.append({"case": case, "result": "PASS", "output": output})
        print(f"PASS src/engine/{'dump.c' if 'dump' in case else 'graphics.c'}: {case}", flush=True)

    parity = None
    if args.phase != "smoke":
        with tempfile.TemporaryDirectory(dir=args.output) as folder:
            legacy = Path(folder)
            copy_source(args.source, legacy)
            replace(legacy / "src/engine/graphics.c", "2 * (x - y)", "((x - y) << 1)", count=2)
            old_exe = legacy / "legacy-probe"
            build(legacy, old_exe, sanitize=False)
            current_pixels, legacy_pixels = legacy / "current.bin", legacy / "legacy.bin"
            for binary, pixels in ((exe, current_pixels), (old_exe, legacy_pixels)):
                code, output = run(binary, "circle-corpus", legacy, (pixels,))
                assert code == 0 and "circle-corpus PASS" in output, output
            current_data = current_pixels.read_bytes()
            assert current_data == legacy_pixels.read_bytes(), "src/engine/graphics.c: circle pixels changed"
            parity = {"byte_count": len(current_data), "sha256": hashlib.sha256(current_data).hexdigest(),
                      "cases": 12, "scales": [1, 2], "byte_identical": True}
            print("PASS src/engine/graphics.c: 12 circle pixel cases equal pre-fix arithmetic", flush=True)

    mutations = []
    if args.mutations:
        definitions = [
            ("circle-fill", "graphics.c",
             "void grDrawCircle(PlatformSurface *sfc, int x1, int y1, int width, int height, uint8 fgColor, uint8 bgColor)\n{",
             "void grDrawCircle(PlatformSurface *sfc, int x1, int y1, int width, int height, uint8 fgColor, uint8 bgColor)\n{\n    return;",
             "circle center pixel"),
            ("circle-fill", "graphics.c", "\n            d += 2 * (x - y) + 5;",
             "\n            d += ((x - y) << 1) + 5;", "left shift of negative value"),
            ("circle-outline", "graphics.c", "\n                d += 2 * (x - y) + 5;",
             "\n                d += ((x - y) << 1) + 5;", "left shift of negative value"),
            ("odd-scr", "graphics.c", "if (scrResource->width % 2)",
             "if (0 && scrResource->width % 2)", "heap-buffer-overflow"),
            ("odd-dump", "dump.c", "if (scrResource->width % 2)",
             "if (0 && scrResource->width % 2)", "odd SCR was accepted"),
            ("empty-bmp-reload", "graphics.c", "        grReleaseBmp(ttmSlot, slotNo);",
             "        if (ttmSlot->numSprites[slotNo]) grReleaseBmp(ttmSlot, slotNo);", "liveCount == 1"),
            ("empty-bmp-alias", "graphics.c", "findBmpResource(ttmSlot->bmpNames[slotNo])",
             "findBmpResource(strArg)", "heap-use-after-free"),
        ]
        for case, filename, old, new, expected in definitions:
            with tempfile.TemporaryDirectory(dir=args.output) as folder:
                mutant = Path(folder)
                copy_source(args.source, mutant)
                replace(mutant / "src/engine" / filename, old, new)
                mutant_exe = mutant / "mutant-probe"
                build(mutant, mutant_exe)
                code, output = run(mutant_exe, case, mutant)
                assert code != 0 and expected in output, f"SURVIVED src/engine/{filename}: {case}\n{output}"
                assert f"drawing {case} PASS" not in output
                mutations.append({"file": f"src/engine/{filename}", "case": case, "result": "FIRED",
                                  "rebuilt": True, "runtime_witness": True, "exit_code": code,
                                  "expected_failure": expected, "output": output})
                print(f"FIRED src/engine/{filename}: {case} (rebuilt and executed)", flush=True)
    report = {"phase": args.phase, "cases": records, "circle_parity": parity, "mutations": mutations}
    (args.output / "drawing-report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
