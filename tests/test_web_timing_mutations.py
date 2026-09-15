"""Rebuild isolated Web audio timing mutants and require a specific executed failure."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build-browser-mutant", action="store_true",
                        help="Also leave a full application without the delay pump for the host browser timing test")
    options = parser.parse_args()
    source, output = options.source.resolve(), options.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    definitions = [
        ("timed-wait", "void platformDelay(uint32 ms) {\n    webAudioPump();",
         "void platformDelay(uint32 ms) {", "platform_web.c: timed wait audio continuity"),
        ("maxspeed", "    webAudioPump();\n    emscripten_sleep(0);",
         "    emscripten_sleep(0);", "platform_web.c: maxspeed frame does not schedule audio"),
        ("suspended", "if (!ctx || ctx.state !== 'running') return 0;",
         "if (!ctx) return 0;", "platform_web.c: suspended callback consumption"),
        ("timed-wait", "(window.jcAudioNext - now) < 0.25 ? 1 : 0",
         "(window.jcAudioNext - now) < 20 ? 1 : 0", "platform_web.c: audio lookahead bound"),
        ("timed-wait", "ch[i] = (HEAPU8[ptr + i] - 128) / 128.0;",
         "ch[i] = (HEAPU8[ptr] - 128) / 128.0;", "platform_web.c: timing PCM sample order"),
    ]
    records = []
    for case, old, new, expected in definitions:
        with tempfile.TemporaryDirectory(dir=output) as temporary:
            work = Path(temporary)
            for directory in ("platform", "src/engine", "tests"):
                (work / directory).mkdir(parents=True, exist_ok=True)
            for directory in ("platform", "src/engine"):
                for path in (source / directory).glob("*.h"):
                    shutil.copyfile(path, work / directory / path.name)
            for name in ("platform/platform_web.c", "src/engine/events.c", "tests/test_web_audio_timing.c"):
                shutil.copyfile(source / name, work / name)
            backend = work / "platform/platform_web.c"
            text = backend.read_text()
            assert text.count(old) == 1, (case, old)
            backend.write_text(text.replace(old, new))
            executable = work / "timing.js"
            wasm = work / "timing.wasm"
            before = {}
            for path in (executable, wasm):
                path.write_text("unbuilt probe")
                os.utime(path, (1, 1))
                before[path] = path.stat().st_mtime_ns
            command = ["emcc", "-std=gnu11", "-DPLATFORM_WEB", "-Wall", "-Wextra", "-Wno-unused-parameter",
                       "-I" + str(work / "platform"), "-I" + str(work / "src/engine"),
                       str(work / "tests/test_web_audio_timing.c"), "-sENVIRONMENT=node", "-sASYNCIFY",
                       "-sALLOW_MEMORY_GROWTH", "-sSAFE_HEAP=1", "-o", str(executable)]
            compiled = subprocess.run(command, text=True, capture_output=True, timeout=120)
            assert compiled.returncode == 0, compiled.stdout + compiled.stderr
            assert all(path.stat().st_mtime_ns > stamp for path, stamp in before.items()), "Web mutant JS/WASM did not rebuild"
            result = subprocess.run(["node", str(executable), case], text=True, capture_output=True, timeout=15)
            text = result.stdout + result.stderr
            witness = f"WITNESS platform_web.c timing {case} BEGIN"
            assert witness in text, f"missing runtime witness: {case}"
            assert result.returncode != 0 and expected in text, f"SURVIVED or wrong failure: {expected}\n{text}"
            assert f"WITNESS platform_web.c timing {case} PASS" not in text
            records.append({"case": case, "result": "FIRED", "expected_failure": expected,
                            "rebuilt_js_and_wasm": True, "runtime_witness": witness,
                            "source_sha256": hashlib.sha256(backend.read_bytes()).hexdigest(),
                            "wasm_sha256": hashlib.sha256(wasm.read_bytes()).hexdigest(),
                            "exit_code": result.returncode})
            print(f"FIRED {expected} (rebuilt JS/WASM and executed)", flush=True)
    report = {"mutations": records}
    if options.build_browser_mutant:
        work = Path(tempfile.mkdtemp(prefix="browser-delay-", dir=output))
        for directory in ("src", "platform", "third_party", "tests", "vs"):
            shutil.copytree(source / directory, work / directory, ignore=shutil.ignore_patterns("__pycache__"))
        (work / "assets").mkdir()
        for name in ("CMakeLists.txt", "assets/scrantic_data.zip"):
            shutil.copyfile(source / name, work / name)
        backend = work / "platform/platform_web.c"
        original = backend.read_text()
        old, new = definitions[0][1:3]
        assert original.count(old) == 1
        backend.write_text(original.replace(old, new))
        browser_build = work / "build_web"
        browser_build.mkdir()
        before = {}
        for name in ("jc_reborn.js", "jc_reborn.wasm"):
            path = browser_build / name
            path.write_text("unbuilt application")
            os.utime(path, (1, 1))
            before[path] = path.stat().st_mtime_ns
        result = subprocess.run([sys.executable, str(source / "tools/build_web.py"), "--inside",
                                 "--source", str(work), "--output", "build_web"],
                                text=True, capture_output=True, timeout=240)
        assert result.returncode == 0, result.stdout + result.stderr
        assert all(path.stat().st_mtime_ns > stamp for path, stamp in before.items()), "browser mutant JS/WASM did not rebuild"
        for name in ("index.html", "favicon.ico"):
            shutil.copyfile(source / name, browser_build / name)
        report["browser_mutant"] = {"build": str(browser_build), "rebuilt_js_and_wasm": True,
                                    "source_sha256": hashlib.sha256(backend.read_bytes()).hexdigest(),
                                    "wasm_sha256": hashlib.sha256((browser_build / "jc_reborn.wasm").read_bytes()).hexdigest()}
        print(f"WITNESS rebuilt full browser delay-pump mutant: {browser_build}", flush=True)
    (output / "mutation-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
