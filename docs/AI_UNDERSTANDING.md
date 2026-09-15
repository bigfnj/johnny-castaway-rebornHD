# Engine architecture and maintenance guide

Johnny Reborn HD reimplements the Johnny Castaway screensaver using the original
resource files and animation scripts. C11 engine code drives native platform
backends; macOS also uses Objective-C. The application remains process-oriented,
with a single active story and renderer.

This is a navigation guide, not a copied API or opcode specification. Prefer the
linked source and focused records when changing a behavior. A script mnemonic or
an old comment does not establish the original screensaver's semantics.

## Where to start

| Area | Maintained entry points |
| --- | --- |
| Build and packaging | [CMakeLists.txt](../CMakeLists.txt), [build validation](../tests/BUILD_VALIDATION.md) |
| Startup and options | [jc_reborn.c](../src/engine/jc_reborn.c), [config.c](../src/engine/config.c) |
| Story and positioning | [story.c](../src/engine/story.c), [story_data.h](../src/data/story_data.h), [walk.c](../src/engine/walk.c) |
| Script execution | [ads.c](../src/engine/ads.c), [ttm.c](../src/engine/ttm.c) |
| Rendering | [graphics.c](../src/engine/graphics.c), [island.c](../src/engine/island.c), [platform.h](../platform/platform.h) |
| Resource decoding | [resource.c](../src/engine/resource.c), [uncompress.c](../src/engine/uncompress.c), [zipvfs.c](../platform/zipvfs.c) |
| Art packs | [art_style.c](../src/engine/art_style.c), [Cartoon authoring](cartoon-art.md), [image authoring lessons](art-style-learnings.md) |
| Unresolved command behavior | [Legacy command review](legacy-command-review.md), [BACKLOG.md](../BACKLOG.md) |

## Build and platform boundaries

CMake 3.19 or later builds the application and the applicable test executables.
Engine sources live in `src/engine`, compiled data tables in `src/data`, platform
adapters in `platform`, and vendored compression code in `third_party/miniz`.
Use CMake rather than assuming the older hand-maintained Visual Studio projects
provide the same source list or verification.

| Target | Window and presentation | Audio |
| --- | --- | --- |
| Windows | Win32 and GDI | WinMM |
| Linux | X11 | ALSA with a worker thread |
| macOS | Cocoa and CoreGraphics | AudioToolbox |
| Web | Emscripten and HTML Canvas | Web Audio |

The Windows build produces a console executable and a screensaver executable.
Their shared `jc_runtime_data` prerequisite refreshes the deployed ZIP even when
only artwork changes or the deployed copy is missing. An explicit executable
target build also runs that prerequisite; a C relink is not required.

Web CI and release compilation use [tools/build_web.py](../tools/build_web.py)
with the official Emscripten 6.0.9 Docker image pinned by digest. The wrapper
checks the compiler version, output artifacts and preloaded archive bytes.
Browser tests run on the host after compilation. A usable Web output contains
the page, JavaScript, Wasm, preload data and page assets together.

The macOS CI/release runner is explicitly Intel (`macos-15-intel`), matching the
`macos-x86_64` package label. Architecture checks inspect the produced binary.
Build and decode checks do not establish native window rendering or audio
behavior. See [build validation](../tests/BUILD_VALIDATION.md) for exact commands,
coverage limits and mutation controls; workflow details belong there and in
[CI](../.github/workflows/ci.yml) and [release](../.github/workflows/release.yml).

## Startup, settings and shutdown

[main](../src/engine/jc_reborn.c) parses options before loading resources.
Use the executable's `help` output for supported spelling and arguments.
The modes are story playback, resource dump, benchmark, single TTM and ADS/tag
playback. Options include bounded frames, seed, startup speed, day/night,
holiday, art style and a final PPM capture. Windows also handles `/s`, `/c` and
`/p` for screensaver execution, configuration and parent-window preview.

Art selection follows this order: explicit `style` option, saved configuration,
then HD for a missing or invalid saved identifier. `setstyle` updates the saved
style and exits without loading the archive, opening graphics or advancing the
story. The Windows configuration dialog also works before archive loading.
Configuration stores story day, calendar day and style in `.jc_reborn` beneath
the user's home location. Writes preserve those known settings together.

Ordinary playback opens the ZIP, parses original resources, validates the chosen
art pack during graphics initialization, creates the renderer, initializes
events/audio, and enters the selected mode. `dump` stays headless and decodes
original resources; it does not validate or render the selected PNG pack.

Frame-budget completion exits with status 0 through sound and graphics teardown.
Input-driven exits use the event handlers' shutdown path. Screensaver input rules
include mouse movement, clicks and focus loss as well as keyboard input.
Ordinary hotkey-enabled playback supports pause, stepping, speed and fullscreen.
`eventsInit` registers platform shutdown with `atexit`.

Mode completion releases its scene resources where execution returns normally.
An event exit can terminate while the ADS call stack is active; the process then
reclaims remaining process allocations. Graphics teardown is not a general API
for unloading every parsed resource or restarting the whole application.

## Resource and art loading

`assets/scrantic_data.zip` is the runtime source archive. It contains original
`data/RESOURCE.MAP` and resource data, extracted WAVs, HD PNGs, and the partial
Cartoon pack. Native ZIP lookup tries the requested path first, then locations
relative to the executable. Web uses its preloaded virtual filesystem.

`zipvfs_read` returns caller-owned extracted bytes. `zipvfs_fopen` supplies a
seekable temporary stream for legacy parsers; callers close it. On Windows,
temporary creation uses exclusive `_open` followed by `_fdopen` and delete-on-close,
not a create-or-truncate `fopen` race.

The resource parser builds global tables for ADS, TTM, BMP, SCR and PAL resources.
Original image data uses palette-indexed nibbles. RLE and LZW output-length checks
reject incomplete decoded buffers. LZW's existing full-output early return is
retained for compatible streams. Header fields no longer retained in the structs
are still consumed through the checked readers.

[art_style.h](../src/engine/art_style.h) defines the shared startup catalog and
loading interface. The built-in choices are HD and `Cartoon (preview)`, rooted at
`data/hd` and `data/styles/cartoon`. Packs are not discovered dynamically and
selection does not replace already loaded surfaces in a live scene.

HD retains its permissive legacy manifest interpretation and original-resource
fallback. Cartoon requires a valid manifest declaring its identifier, scale 2,
straight alpha and partial or complete coverage. Partial coverage must be nonempty;
complete coverage must include every original BMP/SCR slot.

Cartoon PNGs must have exact original dimensions multiplied by two and use the
portable supported PNG formats. Missing Cartoon art falls back to compatible HD,
then original decoding at the current scale. A present but invalid Cartoon asset
is an error naming that asset, not a silent fallback. Pack diagnostics distinguish
partial coverage and report actual fallback use.

Windows PNG loading uses WIC; the other backends use the bundled PNG decoder.
Both produce premultiplied BGRA for composition. Only HD sprite loading applies
the legacy opaque `#A800A8` transparency key. Cartoon preserves intentional
opaque magenta and partial alpha.

The offline authoring validator further requires suitable sprite alpha and opaque
screens. Runtime composition does not universally discard screen alpha, so do
not rely on it to repair a translucent background. Original canvas dimensions,
padding, script positions and flips remain authoritative. See the
[art guide](cartoon-art.md) for packaging, source records and visual acceptance.

## Story, animation and composition

`story.c` selects scenes from compiled data, advances the saved 1-11 story day
when the calendar day changes, sets the island state and schedules transitions.
Walking uses the original route graph and extracted keyframes. Replacing PNGs
does not add animation frames, change scripted positions or replace
palette-drawn script effects.

Calendar holiday windows are October 29-31, March 15-17, December 23-25 and
December 29-January 1. Night is 21:00-05:59 unless overridden. Tide, island
position, raft stage and cloud choices also affect the rendered scene.

ADS schedules TTM threads and resolves scene conditions. TTM executes drawing,
loading and timing instructions until a yield or end condition. Thread activity
and resource ownership are separate: an inactive thread can still own a layer.
Unknown original command semantics remain recorded in the
[legacy command review](legacy-command-review.md); logging a command does not
mean its named behavior is implemented.

`grUpdateDisplay` composites the global background with the supplied scene,
holiday and cloud threads. It no longer takes an unused background-thread
argument. Its actual back-to-front order is:

1. Background screen with static island and current waves.
2. Clouds.
3. Saved-zone overlay, when present.
4. Active TTM layers in slot order.
5. Holiday overlay.

It then waits for the frame tick and presents the composed window surface.
`eventsWaitTick` interprets delays as 20 ms units using widened arithmetic and
yields to the browser even in max-speed mode. Timing limits belong to the actual
instruction path: the SET_DELAY floor does not describe every possible timer.

`COPY_ZONE_TO_BG` copies into the saved-zone overlay, including its legacy width
adjustment. `SAVE_ZONE` and `SAVE_IMAGE1` currently have no drawing effect.
`RESTORE_ZONE` releases the whole overlay and ignores its rectangle. Cleanup uses
the explicit saved-layer release API without assigning new opcode semantics.
`CLEAR_SCREEN` clears a layer to transparent pixels.

Island animation has three high-tide wave families or four low-tide families,
each with three phases. When an active family has selected Cartoon art, the
renderer restores a clean wave base and redraws current families in their latest
update order. This prevents translucent accumulation and stale transparent edges.
Mixed fallback families participate in that clean composition. HD and Cartoon
without active-tide replacements retain legacy wave behavior.

On walking routes behind the palm, selected Cartoon palm art uses source-atop
on Johnny's layer so the already painted tree is not blended twice outside him.
HD and packs without the selected palm replacement retain the legacy path.
The wave and palm tests cover these distinct branches with expected pixels.

## Ownership and lifetime

| Owner | Responsibility |
| --- | --- |
| Parsed resource tables | Process-owned resource names, decoded buffers and metadata remain allocated for the process lifetime; this cleanup deliberately adds no global resource-unload API. |
| TTM slot | Borrows resource bytecode; owns its VM tag table, decoded sprite buffers, surface wrappers and cached BMP names, including names with zero sprites. |
| ADS scene thread | Owns its layer regardless of activity state; release clears the pointer and decrements active bookkeeping only when appropriate. |
| Island threads | Cloud and holiday layers are owned; the background thread borrows the graphics-owned screen. |
| Graphics | Owns the background pixels/wrapper and saved overlay; screen replacement and teardown invalidate the wave snapshot. |
| Platform surface | `platformCreateSurface` owns pixels; `platformCreateSurfaceFrom` borrows supplied pixels, which the engine/PNG owner frees separately. |
| Sound | Owns decoded WAV buffers independently of whether opening the audio device succeeded. |

`adsInit` releases old ownership before resetting bookkeeping. Scene, island,
slot and graphics release paths tolerate repeated cleanup. Standalone TTM and
ADS completion release their saved overlay. These guarantees are exercised by
the compiled allocation tracker, not inferred from pointer assignments alone.

Audio is single-voice: starting another sample replaces the current sample.
`nosound` skips initialization. The callback uses 128 as silence for unsigned
8-bit PCM. Device failure and decoded-buffer ownership have separate state.

## Verification and reproducible scene review

Run the Windows [gate](../gate.ps1) for the integrated build, smoke and regression
sequence. Smoke failure must stop later regression. Test wiring and platform
applicability are maintained in [build validation](../tests/BUILD_VALIDATION.md),
not as fixed counts in this guide.

| Evidence | What it establishes |
| --- | --- |
| [Native smoke](../tests/Invoke-SmokeTests.ps1) and screensaver tests | Bounded process behavior, argument failures, archive discovery and Windows integration. |
| [Golden dump](../tests/Invoke-DumpRegression.ps1), [Unix build](../tests/unix-build.sh) | Original-resource decode output matches the checked-in corpus; no PNG rendering is exercised by dump. |
| [Decoder tests](../tests/test_uncompress.py) | Complete/short output and preserved LZW early-return behavior through compiled code and real resource fixtures. |
| [Lifecycle tests](../tests/test_lifecycle.py) | Real engine ownership with tracked Windows surface allocations and no window; the benchmark uses a test-only clock. |
| [Art integration](../tests/Invoke-ArtStyleTests.ps1), [waves](../tests/test_wave_renderer.py), [palm](../tests/test_palm_renderer.py) | Actual native captures, alpha, fallback, geometry and relevant layering behavior. |
| [Browser smoke](../tests/web-smoke.py), [selector tests](../tests/web-art-controls.py) | Host-browser runtime and style control behavior against a compiled Web build. |
| [Authoring tests](../tests/test_art_tools.py) | Asset dimensions, source-byte preservation, declared scope and packaging contracts, not artistic quality. |

Use bounded frames and an explicit seed for captures, but also control the saved
story day, day/night, holiday, selected mode/tag and archive bytes. A seed alone
does not freeze calendar state or guarantee the same random sequence across C
libraries. Confirm the actual script/frames from execution traces rather than
assuming a scene name implies a particular asset set.

Mutation controls must rebuild changed production code, prove the rebuilt binary
executed, and produce the intended named failure before restoration. Pixel and
decode parity demonstrate their tested cases, not universal semantic equivalence.
Native rendering on another OS and human acceptance of motion remain separate
evidence from compilation, static inventories or successful PNG validation.
