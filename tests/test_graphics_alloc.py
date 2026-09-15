"""Verify required engine surfaces fail explicitly and release wrapper inputs."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

CASES = {
    "layer": "Could not create drawing layer",
    "empty": "Could not create empty background",
    "screen": "Could not create background surface",
    "sprite": "Could not create sprite surface",
}


def build(root, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    args = ["cc", "-std=gnu11", "-DPLATFORM_LINUX", "-ffunction-sections", "-fdata-sections",
            "-I" + str(root / "platform"), "-I" + str(root / "src/engine"),
            "-I" + str(root / "src/data"), "-I" + str(root / "third_party/miniz"),
            str(root / "tests/test_graphics_alloc_driver.c"), str(root / "src/engine/graphics.c"),
            str(root / "src/engine/utils.c"), str(root / "platform/platform_linux.c"),
            "-Wl,--gc-sections", "-Wl,--wrap=platformCreateSurface",
            "-Wl,--wrap=platformCreateSurfaceFrom", "-Wl,--wrap=free",
            "-lX11", "-lasound", "-pthread", "-o", str(output)]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def run(exe, case):
    p = subprocess.run([str(exe), case], capture_output=True, text=True, timeout=10)
    output = p.stdout + p.stderr
    assert f"WITNESS graphics.c allocation {case} BEGIN" in output
    correct = p.returncode == 1 and CASES[case] in output
    if case != "layer": correct = correct and "WITNESS graphics failed pixels freed" in output
    return correct, p.returncode, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "graphics-alloc"
    build(args.source, exe)
    for case in CASES:
        correct, code, output = run(exe, case)
        assert correct, (case, code, output)
        print(f"PASS src/engine/graphics.c: {case} failure and ownership", flush=True)
    records = []
    if args.mutations:
        for case, old, new in [
            ("layer", 'if (!sfc) fatalError("Could not create drawing layer', 'if (0 && !sfc) fatalError("Could not create drawing layer'),
            ("empty", "if (!grBackgroundSfc) {\n        free(data);", "if (0 && !grBackgroundSfc) {\n        free(data);"),
            ("screen", "if (!grBackgroundSfc) {\n        free(outData);", "if (0 && !grBackgroundSfc) {\n        free(outData);"),
            ("sprite", "if (!surface) {\n            free(outData);", "if (0 && !surface) {\n            free(outData);"),
        ]:
            with tempfile.TemporaryDirectory(dir=args.output.resolve()) as folder:
                root = Path(folder)
                for directory in ("src/engine", "src/data", "platform", "third_party/miniz", "tests"):
                    (root / directory).mkdir(parents=True)
                    for p in (args.source / directory).glob("*"):
                        if p.suffix in (".h", ".c"):
                            shutil.copyfile(p, root / directory / p.name)
                source = root / "src/engine/graphics.c"
                text = source.read_text()
                assert text.count(old) == 1
                source.write_text(text.replace(old, new))
                mutant = root / "probe"
                mutant.write_text("unbuilt")
                import os
                os.utime(mutant, (1, 1))
                before = mutant.stat().st_mtime_ns
                build(root, mutant)
                assert mutant.stat().st_mtime_ns > before
                correct, code, output = run(mutant, case)
                assert not correct, f"SURVIVED src/engine/graphics.c {case}"
                records.append({"file": "src/engine/graphics.c", "case": case, "result": "FIRED",
                                "rebuilt": True, "runtime_witness": True, "exit_code": code,
                                "failure_kind": "probe assertion" if "assert" in output.lower() else "process crash or runtime trap",
                                "output": output})
                print(f"FIRED src/engine/graphics.c: {case} (rebuilt and executed)", flush=True)
    (args.output / "graphics-allocation-report.json").write_text(json.dumps({"cases": list(CASES), "mutations": records}, indent=2))


if __name__ == "__main__":
    main()
