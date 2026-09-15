# Build and packaging checks

Native builds require CMake 3.19 or later. `jc_reborn` and `jc_reborn_scr`
depend on the shared `jc_runtime_data` prerequisite. Artwork changes and deleted
deployed ZIPs are therefore handled by explicit executable builds as well as a
normal build, without requiring a C relink.

Run `python -B tests/test_runtime_data.py --mutations` to exercise the production
module in small isolated projects. `--generator Ninja` or
`--generator "Unix Makefiles"` selects another generator. Windows also runs
`python -B tests/test_runtime_data_project.py --mutations`, which builds an
isolated copy of the real application, disables its CMake integration, and
checks that both PowerShell 5.1 and 7 refuse stale data before smoke. These tests
never modify the production ZIP. `--work <new-directory>` retains their logs.

The Unix build script must stop on a failing build even if an executable was
produced. `python3 -B tests/test_unix_build_flow.py --mutations` executes that
script with build, smoke and dump witnesses. The mutation is checked by the
same ordering assertion as the passing failure control.

Web CI and release compilation use `python3 -B tools/build_web.py`. It pulls
the official Emscripten 6.0.9 image pinned to manifest-list digest
`sha256:96617f27fe16421588241def73908fd348a7f9d260440ed0d00b36dcf7a063cc`,
checks the actual `emcc` version, builds in Docker, verifies nonempty JS/Wasm/data
artifacts and exact preload ZIP bytes, then copies the page sources. On Unix it
uses the host UID/GID. Only image acquisition has bounded retries; build and
test failures are propagated. This removes the setup action's GitHub/codeload
fetch and action Node runtime. Docker registry availability is still required.

Browser tests stay on the host and run in order:

```text
python3 -B tools/build_web.py --platform-probes smoke
python tests/web-smoke.py build_web
python3 -B tools/build_web.py --platform-probes regression --probes-only
python tests/web-art-controls.py build_web --mutation-check
```

`python3 -B tests/test_build_contracts.py --mutations` checks acquisition failure
and retry limits, compiler failure propagation, SDK version, missing/empty/stale
artifacts, and macOS architecture responses. A run without `--mac-binary` says
explicitly that actual Mach-O tools were not exercised. On the Intel macOS
runner, `--mac-binary /tmp/jcr/build-unix/jc_reborn` adds real `lipo` inspection
and a deliberately compiled ARM64 negative control. Both CI and release use
`macos-15-intel`; the package label remains `macos-x86_64`. These checks establish
architecture and build/decode behavior, not native window rendering.

The Windows gate runs decoder, ownership and platform-constructor smoke before
any regression. Its focused ownership probe uses tracked Win32 allocations and
is Windows-specific. Linux and macOS run the portable decoder and their actual
backend probe scripts, with all smoke phases before focused regressions and the
golden dump. Linux needs Xvfb/xauth for its real X11 probes and also runs required
graphics-surface allocation failure checks before the corpus. The Web platform
probes run in the pinned SDK container; browser rendering stays on the host.
Backend fault-injection checks are normal regression. Recompiling deliberately
mutated C sources is separate verification. macOS CI runs its source mutations
on the actual runner; other backend mutation commands remain manual checks.

References checked when choosing this implementation:

- [CMake CMP0112](https://cmake.org/cmake/help/latest/policy/CMP0112.html):
  CMake 3.19 avoids reverse target dependencies from `TARGET_FILE_DIR`.
- [Official Emscripten Docker instructions](https://github.com/emscripten-core/emsdk/blob/main/docker/README.md):
  the self-contained SDK image supports compilation as the host UID/GID.
- [GitHub hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners):
  the explicit Intel runner preserves the release architecture.
