# Platform cleanup probes

The probes compile the real backend source with test-only allocation or device
hooks. They do not modify artwork or production archives. Each case emits a
runtime `WITNESS` before assertions; Release allocator probes keep assertions on.
The shell scripts accept `--phase smoke` or `--phase regression`; the PowerShell
script accepts `-Phase Smoke` or `-Phase Regression`. Omitting the phase runs all
cases. Run source mutations after the normal runtime checks when guards change.
macOS CI runs its mutations on the real runner because the development host is
Windows; the other backends' mutation commands are manual checks.

Windows, after the normal CMake build:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/Test-PlatformAlloc.ps1 -Exe build/Release/jc_platform_alloc_test.exe
python -B tests/test_platform_mutations.py --platform windows --output build/platform-mutations
```

The eleven Windows cases exercise surfaces, window allocation failures and WIC
pixel ownership. The device-context failure creates a hidden OS window and
destroys it before `ShowWindow`; other window failures occur before OS creation.

Linux needs a C11 compiler, X11 and ALSA development headers/libraries, pthreads,
Python 3, Xvfb and xauth. On Ubuntu these are provided by `build-essential`,
`libx11-dev`, `libasound2-dev`, `python3`, `xvfb` and `xauth`.

```sh
SRC="$PWD" OUT=/tmp/johnny-platform-tests bash tests/run_linux_platform.sh
python3 tests/test_platform_mutations.py --platform linux --output /tmp/johnny-platform-mutations
```

Linux audio tests use real pthreads with controlled ALSA responses. They establish
thread ownership and cleanup, not physical device compatibility. X11 tests create
real windows under Xvfb and compare `XGetImage` pixels after resize, including
letterboxing, shrinking and returning to the native size. A virtual display does
not validate a desktop window manager's fullscreen policy.

The graphics caller probe is also headless and uses the Linux compiler and
libraries above. It injects NULL surface constructors into the real graphics
loader, checking all four required-surface errors and exactly-once release of
caller-owned pixel buffers:

```sh
python3 tests/test_graphics_alloc.py --output /tmp/johnny-graphics-alloc
python3 tests/test_graphics_alloc.py --output /tmp/johnny-graphics-alloc-mutations --mutations
```

The first command runs four regression cases. The optional mutation command
additionally rebuilds each removed guard and requires a named runtime failure.

Web needs the same Emscripten 6.0.9 toolchain as CI and its Node runtime:

```sh
SRC="$PWD" OUT=/tmp/johnny-web-platform-tests bash tests/run_web_platform.sh
python3 tests/test_platform_mutations.py --platform web --output /tmp/johnny-web-platform-mutations
```

The Web probe executes the actual C callback and embedded JavaScript against an
AudioContext substitute, checking channel count, samples and scheduling duration.
Test builds also enable Emscripten SAFE_HEAP memory checks. Like the other audio
backends, this API takes a valid specification pointer; the new contract checks
only its supported channel count and sample format.
Run the existing `tests/web-smoke.py` and `tests/web-art-controls.py` against the
full built page afterward for browser integration.

macOS requires its SDK, Clang, AppKit and AudioToolbox:

```sh
bash tests/run_macos_platform.sh
python3 tests/test_platform_mutations.py --platform macos --output /tmp/johnny-platform-mutations
```

The macOS queue probe uses real NSEvent objects with controlled dequeue/dispatch
and no visible window. It tests production polling and translation, not OS key
delivery, and does not replace manual native rendering/fullscreen checks.

Mutation runs copy only source/header/test files into isolated output children,
replace one guard, rebuild over an old timestamped sentinel, and require a runtime
witness followed by failure. Reports distinguish probe assertions from process
crashes/runtime traps; neither is labeled a production error message. The
unchanged source remains outside the fixture.
Run platform smoke before these mutations and broader regression; the normal
application gate and golden dump remain required after integration.
