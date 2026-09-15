"""Rebuild isolated backend mutants and require a runtime witness before failure."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def command(argv: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, errors="replace", timeout=timeout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["linux", "web", "windows", "macos"], required=True)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    suffix = ".m" if args.platform == "macos" else ".c"
    backend = f"platform/platform_{args.platform}{suffix}"
    mutations = [
        ("surface-struct", backend, "test_platform_alloc", "surface-struct",
         'if (!surface) { lastError = "Out of memory allocating surface";',
         'if (0 && !surface) { lastError = "Out of memory allocating surface";'),
        ("surface-pixels", backend, "test_platform_alloc", "surface-pixels",
         "if (!surface->pixels) {", "if (0 && !surface->pixels) {"),
        ("borrowed-wrapper", backend, "test_platform_alloc", "borrowed-wrapper",
         'if (!surface) { lastError = "Out of memory allocating surface wrapper";',
         'if (0 && !surface) { lastError = "Out of memory allocating surface wrapper";'),
        ("window-struct", backend, "test_platform_alloc", "window-1",
         'if (!window) { lastError = "Out of memory allocating window";',
         'if (0 && !window) { lastError = "Out of memory allocating window";'),
        ("window-unwind", backend, "test_platform_alloc", "window-2",
         "if (!window->surface) { free(window); return NULL; }",
         "if (!window->surface) { return NULL; }"),
    ]
    if args.platform == "windows":
        mutations.append(("wic-pixel-unwind", "platform/png_loader.c", "test_platform_alloc", "png-wrapper",
                          "if (!sfc) free(pixels);", "if (!sfc) { /* mutation: leak decoded pixels */ }"))
        mutations.extend([
            ("native-window", backend, "test_platform_alloc", "native-window",
             "if (!window->hwnd) {", "if (0 && !window->hwnd) {"),
            ("native-context", backend, "test_platform_alloc", "native-context",
             'if (!window->hdc) { lastError = "Failed to get window device context"; goto fail; }',
             'if (0 && !window->hdc) { lastError = "Failed to get window device context"; goto fail; }'),
        ])
    if args.platform == "macos":
        mutations.extend([
            ("native-window", backend, "test_platform_alloc", "native-window",
             "if (!window->nsWindow) {", "if (0 && !window->nsWindow) {"),
            ("native-view", backend, "test_platform_alloc", "native-context",
             "if (!window->view) {", "if (0 && !window->view) {"),
            ("event-drain", backend, "test_macos_events", "drain",
             "                default:\n                    break;\n            }\n\n        }",
             "                default:\n                    return 0;\n            }\n\n        }"),
            ("dispatch-quit", backend, "test_macos_events", "delegate-quit",
             "[NSApp sendEvent:nsEvent];\n            if (quitRequested)",
             "[NSApp sendEvent:nsEvent];\n            if (0 && quitRequested)"),
            ("unknown-key", backend, "test_macos_events", "unknown-key",
             "event->data.key.keycode = KEY_UNKNOWN;\n                    NSString* chars",
             "/* mutation: stale key */\n                    NSString* chars"),
        ])
    if args.platform == "linux":
        mutations.extend([
            ("worker-error-join", backend, "test_linux_audio", "worker-error",
             "if (audioThreadCreated) {", "if (atomic_load(&audioThreadRunning)) {"),
            ("join-failure-retention", backend, "test_linux_audio", "join-failure",
             'lastError = "Failed to join the audio thread";\n            return;',
             'lastError = "Failed to join the audio thread";'),
            ("open-ownership", backend, "test_linux_audio", "normal-reopen",
             "if (audioThreadCreated || pcmHandle) {", "if (0 && (audioThreadCreated || pcmHandle)) {"),
            ("ignored-event-drain", backend, "test_linux_window", "events",
             "while (XPending(display)) {", "if (XPending(display)) {"),
            ("aspect-bars", backend, "test_linux_window", "pixels",
             "int left = (attr.width - drawW) / 2;", "int left = 0;"),
            ("presentation-memory", backend, "test_linux_window", "presentation-failure",
             'if (!pixels) { lastError = "Out of memory allocating presentation pixels"; return; }',
             'if (0 && !pixels) { lastError = "Out of memory allocating presentation pixels"; return; }'),
            ("presentation-image", backend, "test_linux_window", "presentation-failure",
             "if (!replacement) {", "if (0 && !replacement) {"),
            ("presentation-size", backend, "test_linux_window", "presentation-failure",
             "if (attr.width > INT_MAX / 4 ||", "if (0 && (attr.width > INT_MAX / 4 ||"),
            ("gc-unwind", backend, "test_linux_window", "gc-failure",
             'if (!window->gc) { lastError = "Failed to create X graphics context"; goto fail; }',
             'if (0 && !window->gc) { lastError = "Failed to create X graphics context"; goto fail; }'),
            ("image-unwind", backend, "test_linux_window", "image-failure",
             'if (!window->ximage) { lastError = "Failed to create X image"; goto fail; }',
             'if (0 && !window->ximage) { lastError = "Failed to create X image"; goto fail; }'),
            ("window-native-unwind", backend, "test_linux_window", "window-failure",
             'if (!window->window) { lastError = "Failed to create X window"; goto fail; }',
             'if (0 && !window->window) { lastError = "Failed to create X window"; goto fail; }'),
        ])
    if args.platform == "web":
        for name, old, new in [
            ("stereo", "spec->channels != 1", "0"),
            ("format", "spec->format != 8", "0"),
        ]:
            mutations.append((f"audio-{name}", backend, "test_web_audio", name, old, new))
    results = []
    for label, filename, driver, case, old, new in mutations:
        with tempfile.TemporaryDirectory(prefix=f"{label}-", dir=args.output.resolve()) as tmp:
            work = Path(tmp)
            for folder in ("platform", "src/engine", "tests", "vs/jc_reborn"):
                (work / folder).mkdir(parents=True, exist_ok=True)
            for p in (args.source / "platform").glob("*"):
                if p.is_file() and p.suffix in (".h", ".c", ".m"):
                    shutil.copyfile(p, work / "platform" / p.name)
            shutil.copyfile(args.source / "src/engine/mytypes.h", work / "src/engine/mytypes.h")
            for p in (args.source / "vs/jc_reborn").glob("*.h"):
                shutil.copyfile(p, work / "vs/jc_reborn" / p.name)
            driver_suffix = ".m" if driver == "test_macos_events" else ".c"
            driver_source = f"tests/{driver}{driver_suffix}"
            shutil.copyfile(args.source / driver_source, work / driver_source)
            target = work / filename
            source = target.read_text()
            assert source.count(old) == 1, (filename, label, source.count(old))
            changed = source.replace(old, new)
            if label == "presentation-size":
                changed = changed.replace("SIZE_MAX / ((size_t)attr.width * 4)) {",
                                          "SIZE_MAX / ((size_t)attr.width * 4))) {")
            target.write_text(changed)
            exe = work / ("probe.js" if args.platform == "web" else "probe")
            def build_sentinel(path: Path) -> int:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("not a compiled probe")
                os.utime(path, (1, 1))
                return path.stat().st_mtime_ns
            if args.platform == "windows":
                (work / "CMakeLists.txt").write_text(
                    "cmake_minimum_required(VERSION 3.10)\nproject(probe C)\n"
                    f"add_executable(probe {driver_source})\n"
                    "target_compile_definitions(probe PRIVATE PLATFORM_WINDOWS _CRT_SECURE_NO_WARNINGS NOMINMAX)\n"
                    "target_include_directories(probe PRIVATE platform src/engine)\n"
                    "target_link_libraries(probe gdi32 user32 winmm windowscodecs ole32 uuid)\n")
                configure = command(["cmake", "-S", str(work), "-B", str(work / "build"), "-A", "x64"])
                assert configure.returncode == 0, configure.stdout
                exe = work / "build/Release/probe.exe"
                before = build_sentinel(exe)
                built = command(["cmake", "--build", str(work / "build"), "--config", "Release"])
            else:
                compiler = "emcc" if args.platform == "web" else "cc"
                argv = [compiler, "-std=gnu11", f"-DPLATFORM_{args.platform.upper()}",
                        "-I" + str(work / "platform"), "-I" + str(work / "src/engine")]
                if args.platform == "macos": argv += ["-x", "objective-c"]
                argv += [str(work / driver_source), "-o", str(exe)]
                if args.platform == "linux": argv += ["-lX11", "-lasound", "-pthread"]
                elif args.platform == "web": argv += ["-sENVIRONMENT=node", "-sASYNCIFY", "-sALLOW_MEMORY_GROWTH", "-sSAFE_HEAP=1"]
                else: argv += ["-framework", "Cocoa", "-framework", "AudioToolbox"]
                before = build_sentinel(exe)
                built = command(argv)
            assert built.returncode == 0, f"{label} did not build:\n{built.stdout}"
            assert exe.exists() and exe.stat().st_mtime_ns > before, f"{label}: artifact timestamp did not advance"
            run = [str(exe), case]
            if args.platform == "web": run.insert(0, "node")
            elif args.platform == "linux" and driver != "test_linux_audio": run = ["xvfb-run", "-a"] + run
            executed = command(run, 15)
            assert "WITNESS " in executed.stdout and " BEGIN" in executed.stdout, f"{label}: no runtime witness\n{executed.stdout}"
            assert executed.returncode != 0 and " PASS" not in executed.stdout, f"SURVIVED {filename}: {label}"
            results.append({"file": filename, "mutation": label, "case": case,
                            "rebuilt": True, "runtime_witness": True, "exit_code": executed.returncode,
                            "result": "FIRED",
                            "failure_kind": "probe assertion" if "assert" in executed.stdout.lower() else "process crash or runtime trap",
                            "production_error_diagnostic_asserted": False,
                            "output": executed.stdout})
            print(f"FIRED {filename}: {label} (rebuilt and executed)", flush=True)
    (args.output / "mutation-report.json").write_text(json.dumps({"platform": args.platform, "mutations": results}, indent=2))


if __name__ == "__main__":
    main()
