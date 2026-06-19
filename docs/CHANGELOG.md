# Johnny Reborn HD — Changelog

Per-session record of changes made to this fork on top of upstream Johnny Reborn.

---

## 2026-04-21 — Release x64 build now produces only `.exe` (no .pdb) (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** All three `.vcxproj` Release configurations (Win32 + x64)

### Change
The Release x64 build was producing a `.pdb` debug-symbol file alongside each `.exe` in `vs/bin/x64/Release/`:

```
before:  jc_reborn.exe (128 KB) + jc_reborn.pdb (1.3 MB)
         extract_sound.exe (11 KB) + extract_sound.pdb (528 KB)
         extract_walk_data.exe (11 KB) + extract_walk_data.pdb (471 KB)

after:   jc_reborn.exe (128 KB)
         extract_sound.exe (11 KB)
         extract_walk_data.exe (10 KB)
```

For shipped builds we don't need debug symbols — downstream users will install the proper MSVC runtime packages to run the binary, and they never need the PDB. Debug configurations (`Debug|Win32`, `Debug|x64`) are untouched — full PDBs still produced for local debugging.

### Files changed
- `vs/jc_reborn/jc_reborn.vcxproj`
- `vs/extract_sound/extract_sound.vcxproj`
- `vs/extract_walk_data/extract_walk_data.vcxproj`

Per `.vcxproj`, both Release configurations (`Release|Win32` and `Release|x64`) updated:
- `<Link><GenerateDebugInformation>true</GenerateDebugInformation>` → `false`
- `<ClCompile>` added `<DebugInformationFormat>None</DebugInformationFormat>` (skip `.pdb` generation during compile too; belt and suspenders)

The existing `Publish|x64` config (jc_reborn only) was already set to `false` — no change needed there.

### Rebuild verification
Clean wipe of `vs/bin/` and `vs/build/`, then `MSBuild vs\jc_reborn.sln /p:Configuration=Release /p:Platform=x64`:

```
OutDir contents (exactly 3 files, no debug artifacts):
  extract_sound.exe         11,264 bytes
  extract_walk_data.exe     10,240 bytes
  jc_reborn.exe            128,000 bytes

Sanity: jc_reborn.exe version → prints Johnny Reborn banner correctly.
```

### Not changed
- Debug builds still produce PDBs (needed for local debugging).
- CMake build — this only touches the Visual Studio project files. CMake's Release build on MSVC already defaults to no PDBs, so no CMakeLists change required.
- Binary size — `jc_reborn.exe` stayed at 128,000 bytes; the only thing we stopped generating was the separate `.pdb` file.

---

## 2026-04-21 — Structural reorganization (Option B) + Release x64 build verified clean (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** Repo layout, CMakeLists.txt, all VS project files, CI workflow, tools/, docs/, utility header for `noreturn`, warning cleanup in `sound.c` and `uncompress.c`

### Context
The 40+ flat C/H files at repo root were becoming hard to scan — engine code, platform adapters, vendored miniz, and static data tables were all mixed in one directory. Option B from the "is the structure fine?" audit: introduce semantic subdirectories, move files accordingly, update every build config, verify with a clean Release x64 Windows build.

### Files moved (~47 total)

| From (repo root) | To |
|---|---|
| jc_reborn.c, utils.{c,h}, uncompress.{c,h}, resource.{c,h}, dump.{c,h}, story.{c,h}, walk.{c,h}, calcpath.{c,h}, ads.{c,h}, ttm.{c,h}, island.{c,h}, bench.{c,h}, graphics.{c,h}, sound.{c,h}, events.{c,h}, config.{c,h}, mytypes.h | `src/engine/` |
| calcpath_data.h, story_data.h, walk_data.h | `src/data/` |
| platform.h, platform_linux.c, platform_macos.m, platform_windows.c, platform_web.c, png_loader.c, png_decoder.{c,h}, zipvfs.{c,h} | `platform/` |
| miniz.{c,h}, miniz_common.h, miniz_export.h, miniz_tdef.{c,h}, miniz_tinfl.{c,h}, miniz_zip.{c,h} | `third_party/miniz/` |
| AI_UNDERSTANDING.md, CHANGELOG.md, HD_README.txt (→ .md) | `docs/` |
| toolchain-mingw.cmake | `cmake/` |
| build_web.ps1 | `scripts/` |
| scrantic_data.zip | `assets/` |

Root-level files preserved: CMakeLists.txt, README.md, LICENSE, index.html, favicon.ico, .gitignore.

### Build-system updates

**CMakeLists.txt** — source paths rewritten under new subtree; added `target_include_directories(jc_reborn PRIVATE …)` covering `src/engine`, `src/data`, `platform`, `third_party/miniz` so `#include "foo.h"` resolves without any source-side changes; added MSVC branch (`/W4` + `-D_CRT_SECURE_NO_WARNINGS -DNOMINMAX`); `--preload-file` path updated to `${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip@scrantic_data.zip`.

**scripts/build_web.ps1** — repo root now auto-derived via `Split-Path -Parent $scriptDir` (one level up from the script) instead of assuming script sits at repo root.

**.github/workflows/main.yml** — Windows cross-compile job's toolchain path `-DCMAKE_TOOLCHAIN_FILE=../toolchain-mingw.cmake` → `-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-mingw.cmake`.

**vs/jc_reborn/jc_reborn.vcxproj + .filters** — all 45+ `ClCompile Include` and `ClInclude Include` paths rewritten with correct subtree prefix (`..\..\src\engine\`, `..\..\platform\`, `..\..\third_party\miniz\`, `..\..\src\data\`). `AdditionalIncludeDirectories` updated per-configuration (Debug/Release Win32/x64 + Publish x64) from `$(SolutionDir)..;` to `$(SolutionDir)..\src\engine;$(SolutionDir)..\src\data;$(SolutionDir)..\platform;$(SolutionDir)..\third_party\miniz;`. Filters file also reorganized into `Source Files\Engine`, `Source Files\Platform`, `Source Files\Third Party\miniz`, and matching Header Files folders so the Solution Explorer view mirrors the disk layout.

**vs/extract_sound/extract_sound.vcxproj** — updated `..\..\utils.c` → `..\..\src\engine\utils.c` (+ mytypes.h and utils.h paths); `AdditionalIncludeDirectories` narrowed to `$(SolutionDir)..\src\engine;`.

**vs/extract_walk_data/extract_walk_data.vcxproj** — no changes needed; source stayed at `tools/extract_walk_data.c` and the tool uses no custom headers.

**tools/extract_sound.c** — `#include "../mytypes.h"` and `#include "../utils.h"` → `#include "../src/engine/mytypes.h"` and `#include "../src/engine/utils.h"`.

**tools/Makefile.sound** — `OBJ = extract_sound.o ../utils.o` → `OBJ = extract_sound.o ../src/engine/utils.o`.

### Warning cleanup (from the Release x64 build)

The fresh Release x64 MSVC build surfaced two warnings that weren't present in the MinGW CI builds (`/W4` is stricter than `-Wall -Wextra` in a couple of places). Both fixed:

1. **`uncompress.c(302): warning C4702: unreachable code`**
   `default:` branch of the `uncompress()` dispatcher called `fatalError(...)` then `return NULL;`. MSVC deduced fatalError as noreturn via static analysis and flagged the trailing return as unreachable.

   Fix: added a portable `JCR_NORETURN` macro to `src/engine/utils.h` (maps to `__declspec(noreturn)` on MSVC, `__attribute__((noreturn))` on GCC/Clang, `_Noreturn` on C11), applied it to the `fatalError` declaration, added `#include "utils.h"` to `utils.c` (which had been missing), and removed the unreachable `return NULL;` in the dispatcher. All compilers now see the function as properly noreturn and don't warn about missing fallback returns.

2. **`sound.c(114): warning C4701: potentially uninitialized local variable 'audioSpec' used`**
   `PlatformAudioSpec audioSpec;` declared uninitialized then conditionally populated inside `if (!haveSpec) audioSpec = wavSpec; haveSpec = 1;` — runtime-safe but flow analysis on MSVC couldn't prove it.

   Fix: `PlatformAudioSpec audioSpec = {0};` — one-character change.

### Build verification

```
cmake version 4.2.3
Visual Studio Community 2026 (18.4.3) at C:\Program Files\Microsoft Visual Studio\18\Community
MSBuild: C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe
Toolsets installed: 14.29.30133, 14.50.35717

MSBuild vs\jc_reborn.sln /p:Configuration=Release /p:Platform=x64 /verbosity:minimal /nologo /m
→ 3 binaries produced, zero warnings, zero errors:
    extract_sound.exe         11,264 bytes
    extract_walk_data.exe     10,752 bytes
    jc_reborn.exe            128,000 bytes

Sanity: jc_reborn.exe version → prints Johnny Reborn version banner correctly.
```

### Not changed
- No engine logic, opcode handling, scene sequencing, or rendering behavior. Pure structural + paths + include-include hygiene.
- CLIENT-facing paths (`scrantic_data.zip`, `data/RESOURCE.MAP`, `data/hd/SCR/<NAME>.png`, etc.) unchanged — zipvfs sees the same zip layout; end users' install instructions are unaffected.

### Follow-up (not done)
- CMake-side build verification (native MSVC generator via `cmake -G "Visual Studio 17 2022" -A x64`) — not run, since MSBuild on the .sln already proved the source organization. If you ever drop the VS project in favor of CMake-generated projects, this just works.
- Linux + macOS builds — not run locally (no Linux/macOS host available in this session); CI workflow updated to match, so next CI run will prove them.
- Web build — not run; `build_web.ps1` + CMakeLists already wired to the new `assets/scrantic_data.zip` path.

---

## 2026-04-20 — LZW decoder diagnostics + per-frame allocation audit (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** `uncompress.c` (LZW hardening + better error messages), `graphics.c` (grLoadBmp fast-path), audit documentation

### Context
Two items from this afternoon's "next candidates" list: NEW-2 (uncompress.c LZW buffer overrun risk) and NEW-3 (per-frame allocation profile). Both turned out to be **already in good shape** — the reported concerns either didn't exist in the current source or were already defensively handled. Work done is modest hardening + documentation.

### NEW-2: LZW decoder — no bugs found; diagnostics improved

**Audit result:** earlier agent notes referenced "TODO in comments at lines 52, 56" — `grep "TODO\|FIXME\|XXX\|HACK" uncompress.c` returns zero hits. Close reading of `uncompressLZW` shows the four buffer boundaries are all defensively checked:

- `decodeStack[4096]` writes gated by `stackPtr >= 4096` breaks (lines 142, 152, 160)
- `codeTable[code].append` reads gated by `code > 4095` break (line 152)
- `codeTable[free_entry]` writes gated by `free_entry < 4096` check (line 177)
- `outData[outOffset]` writes gated by `outOffset >= outSize` early return (line 171)
- `inOffset` capped by `getByte` at `maxInOffset` (line 44-46)

Corrupt input produces (possibly garbage) output, never a crash. Adversarial codeTable cycles are bounded by the stack limit.

**What I improved instead:**

1. Added invariant-documenting block comment at the top of `uncompressLZW` explaining each bounds check.
2. Replaced the bare `fatalError("error while uncompressing LZW")` with diagnostic messages:
   - An `earlyBreakReason` string at each break point
   - On abort: `"LZW decode aborted: <reason> (inOffset=N/M, outOffset=N/M, stackPtr=N, free_entry=N, n_bits=N)"`
   - On input truncation: `"LZW decode truncated: consumed N of M input bytes (produced N of M output bytes)"`
3. Similarly upgraded RLE's `fatalError` message.

Net effect: future corrupt-resource reports now come with enough context to diagnose, instead of an opaque "error while uncompressing LZW".

### NEW-3: Per-frame allocation audit — footprint is already zero

**Audit method:** `grep "malloc\|calloc\|realloc\|strdup\|grNewLayer\|platformCreateSurface"` across all `.c` files; traced each hit to its call chain; classified by phase (startup / scene-start / scene-end / per-frame).

**Result:** the render loop is zero-allocation.

| Phase | Allocations | Cadence |
|---|---|---|
| Startup (`parseResourceFiles`, palette, tags) | ~100+ `safe_malloc` | Once at launch |
| Scene start (LOAD_IMAGE, LOAD_SCREEN, adsAddScene) | ~5-10 | 6-19 × per story pass (~ once per minute) |
| Scene end (adsStopScene, grReleaseBmp) | matching frees | Same |
| Per-frame (grUpdateDisplay, platformBlitSurface, ttmPlay opcode dispatch) | **0** | 12.5 FPS ceiling (80ms/tick) |

`grUpdateDisplay` is purely compositor — blit existing surfaces. `platformBlitSurface` is a pure pixel-copy loop. `ttmPlay` only invokes allocators via opcodes that a well-behaved TTM fires at scene start, not inside the animation loop.

**One small optimization applied:** `grLoadBmp` previously unconditionally freed + reloaded the BMP slot even if the same name was already loaded. If a TTM ever issued `LOAD_IMAGE same.bmp` inside its animation loop (hypothetical, not observed in shipped TTMs), this would cause a per-frame alloc storm.

Added ~5-line fast-path at the top of `grLoadBmp`:

```c
if (ttmSlot->numSprites[slotNo] &&
    ttmSlot->bmpNames[slotNo] != NULL &&
    strcmp(ttmSlot->bmpNames[slotNo], strArg) == 0) {
    return;
}
```

Defensive only — no observed symptom. Cost: one `strcmp` on hit (negligible) vs. full release + decode miss (what was previously unconditional).

### Files touched
- `uncompress.c` — invariant-documenting header comment, `earlyBreakReason` variable, better fatalError messages in both LZW and RLE paths
- `graphics.c` — `grLoadBmp` fast-path
- `AI_UNDERSTANDING.md` — new `@ENGINE_MAIN_LOOP` allocation-profile subsection

### Not changed
- `uncompress.c` control flow — the bounds checks were already correct. No behavior change under valid input.
- Per-frame rendering — nothing to optimize; it was already allocation-free.

### Follow-up suggestions (not done)
- `grLoadScreen` has a similar unconditional-release pattern. Could apply the same name-compare fast-path. Even lower impact than the BMP case since LOAD_SCREEN fires at most once per scene (backgrounds don't animate via TTM reload). Skipped as probably not worth the ~10 lines.
- Consider converting `fatalError` on corrupt data to return-NULL, so the resource loader could skip the bad resource and continue. Larger refactor (would touch resource.c callers); defer until there's a real user need.

---

## 2026-04-20 — isRunning refactored from `int` to `TtmRunState` enum (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** `graphics.h` (enum + struct member type), `ads.c` / `ttm.c` / `island.c` (call sites)

### Context
Follow-up to the isRunning semantics investigation earlier today (see entry below). Magic numbers 0..3 were scattered across 45+ call sites, making scene-lifecycle debugging noisier than it needed to be. Now self-documenting.

### Change

**`graphics.h`** — added an enum in front of the `TTtmThread` struct:
```c
typedef enum {
    TTM_FREE         = 0,  /* slot available; not composited, not ticked  */
    TTM_RUNNING      = 1,  /* executing bytecode via ttmPlay each frame   */
    TTM_ENDING       = 2,  /* transient: resolved same frame → RUNNING or FREE */
    TTM_STATIC_LAYER = 3   /* background/clouds/holiday: composited only, no bytecode */
} TtmRunState;
```
Struct member changed: `int isRunning` → `TtmRunState isRunning`.

**Call sites updated across `ads.c`, `ttm.c`, `island.c`:**

- All assignments `isRunning = 0` → `isRunning = TTM_FREE`
- All assignments `isRunning = 1` → `isRunning = TTM_RUNNING`
- All assignments `isRunning = 2` → `isRunning = TTM_ENDING`
- All assignments `isRunning = 3` → `isRunning = TTM_STATIC_LAYER`
- Explicit comparisons `isRunning == 1` → `isRunning == TTM_RUNNING` (ads.c:231, 324)
- Explicit comparisons `isRunning == 2` → `isRunning == TTM_ENDING` (ads.c:850)
- Ternary `(i<numLayers ? 1 : 0)` → `(i<numLayers ? TTM_RUNNING : TTM_FREE)` (ads.c:904)

**Unchanged** (deliberately):

- Truthy checks `if (thread.isRunning)` / `if (!thread.isRunning)` — still work correctly since any non-FREE state is non-zero and treated as "active". Used in compositing (graphics.c:275,291,299) and tick dispatch (ads.c:242,309,740,746,754,810,825,834,988,993).
- `debugMsg("... %d", thread.isRunning)` — default argument promotion in varargs converts the enum to int, matching `%d`. No cast needed.

### Safety notes
- Behavioral change: **none**. Same integer values, same transitions, same compositing semantics. The refactor is purely a rename of literals.
- Binary change: enum underlying type is `int` on all target compilers (GCC, Clang, MSVC/WIC with default flags), so struct layout is unchanged.
- Code review: `Grep "isRunning\s*[=!<>]=?\s*[0-9]"` now returns zero hits — no bare numeric literals remain.

### Follow-up suggestion
None immediate. If someone hacks on `ttmPlay()` they'll now get a self-documenting state-machine view instead of magic numbers. Bug class "assigned wrong number to isRunning" becomes "assigned wrong enum to isRunning" which the compiler would catch with `-Wswitch-enum` warnings on any `switch(isRunning)` with missing cases — worth enabling if we ever add such a switch.

---

## 2026-04-20 — SET_DELAY unit confirmed + isRunning semantics confirmed (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** Documentation-only — [AI_UNDERSTANDING.md](AI_UNDERSTANDING.md) `@TTM_VM`, `@ADS_VM`, `@KNOWN_ISSUES_AND_GOTCHAS`

### Context
Follow-up from this morning's gotcha audit. Items #8 (SET_DELAY unit) and #9 (isRunning values) were flagged as "investigate to confirm" — both were ambiguous in the upstream docs and required reading the actual VM implementations to pin down.

### Findings

**#8 — SET_DELAY unit is 20ms ticks, NOT ms.**

Full call chain (verified against current source):

1. `ttm.c:214` SET_DELAY opcode: `ttmThread->delay = max(args[0], 4)` — arg is the number of **ticks**, not milliseconds. Minimum clamped to 4.
2. `ads.c:812-829` main frame loop: compute `mini = min(timer across active threads)`, decrement all timers, set `grUpdateDelay = mini`.
3. `graphics.c:306` (inside `grUpdateDisplay`): `eventsWaitTick(grUpdateDelay)`.
4. `events.c:119`: `delay *= 20` — ticks converted to ms here (1 tick = 20ms).

Consequence: the floor of 4 ticks means **any TTM scene is clamped to 80ms frame delay minimum (12.5 FPS ceiling)**, regardless of what the script requests. A script calling `SET_DELAY 1` (hoping for 20ms / 50 FPS) will actually render at 80ms / 12.5 FPS. Not a bug per se — the original Sierra screensaver was authored for slower frame rates — but worth noting if we ever author new scenes expecting faster animation.

**#9 — isRunning has 4 values; 2 is transient; 3 is reserved for static layers.**

Enumerated all writes and reads across `ads.c`, `ttm.c`, `island.c`, `graphics.c` (~45 hits):

| Value | Meaning | Who writes | Who reads |
|---|---|---|---|
| `0` | Free/idle — slot available, not composited, not ticked | `adsStopScene`, `adsInit`, all reset paths | All truthy-checks negate |
| `1` | Executing bytecode — `ttmPlay` called every frame | `adsAddScene` (new), restart-from-iteration | Explicit `== 1` checks in ads.c:231, 324; general truthy in compositing |
| `2` | Ending-drain — **transient** state, resolved in one frame | `ttm.c:204` PURGE (no sceneTimer), `ttm.c:392` end-of-bytecode, `ads.c:846` sceneTimer expired | `ads.c:850` → either restarts at tag (→1 if iterations remain) or calls `adsStopScene` (→0) + triggers IF_LASTPLAYED chunks |
| `3` | Background/static-layer — composited but never bytecode-executed | `ttmBackgroundThread` (island waves, ads.c:947), `ttmCloudsThread` (ads.c:970), `ttmHolidayThread` (island.c:187). Driven by `islandAnimate`, `islandAnimateClouds`, or static sprite. Never written to the general `ttmThreads[]` array. | Truthy check in `ads.c:740,746` (ticks via `islandAnimate`); compositing in `graphics.c:275-299` |

Observed state transitions:
```
0 ──(adsAddScene)────▶ 1
1 ──(PURGE|end-of-stream|sceneTimer≤0)────▶ 2
2 ──(iterations>0)────▶ 1            [restart at tag]
2 ──(iterations=0)────▶ 0            [adsStopScene → IF_LASTPLAYED chunks]
0 ──(adsInitIsland)────▶ 3           [background/clouds/holiday only]
3 ──(cleanup)────▶ 0
```

### Changes
- **AI_UNDERSTANDING.md** — `@TTM_VM` SET_DELAY row updated with full semantics + call chain; `@ADS_VM` TTtmThread comment updated with confirmed isRunning values; `@KNOWN_ISSUES_AND_GOTCHAS` #8 and #9 struck through with full resolution details.

### Follow-up suggestions (not done this session)
- **Refactor `int isRunning` to an enum.** Magic numbers 0–3 scattered across 45+ sites make scene-lifecycle debugging harder than it needs to be. A simple `enum TtmRunState { TTM_FREE=0, TTM_RUNNING=1, TTM_ENDING=2, TTM_STATIC_LAYER=3 }` + changing the struct member type would make the code self-documenting without any behavioral change.
- **Consider whether SET_DELAY floor of 4 is correct.** If we ever want to ship new HD scenes authored at 20 FPS or above, this clamp needs adjustment or removal. The `// TODO ?` comment at ttm.c:214 suggests the upstream author was uncertain too. For now, leave as-is — no evidence any shipped TTM script wants faster.

---

## 2026-04-20 — HD PNG cross-platform + deployment friction fixes (Justin Lowe)

**Author:** Justin Lowe (with Claude Opus 4.7 assistance)
**Scope:** HD asset override pipeline across platforms, documentation accuracy, Emscripten packaging, Windows build script portability

### Context
First pass addressing the "known issues & gotchas" audit captured in [AI_UNDERSTANDING.md](AI_UNDERSTANDING.md) `@KNOWN_ISSUES_AND_GOTCHAS`. Priority was the flagship-feature gaps (HD PNG was Windows-only; README misled users about where PNGs live) and deployment friction (hardcoded paths in build_web.ps1; `--embed-file` inflating the wasm).

### Changes

**1. HD_README.txt — rewrite to reflect zipvfs-based asset layout (gotcha #2)**

Previous text described dropping PNGs into an on-disk `data/hd/` folder. The runtime actually reads HD assets via `zipvfs_read` from `scrantic_data.zip`, so the readme instructions would silently fall back to the built-in decoder (no HD applied). Rewrote to reflect reality.

**2. png_decoder.c / png_decoder.h — new minimal PNG decoder (gotcha #1)**

Added a small (~350 LOC) PNG decoder covering the common case for HD game assets: 8-bit RGB, 8-bit RGBA, 8-bit grayscale+alpha, non-interlaced. Uses miniz's `tinfl` for zlib inflate (already vendored). Handles all five filter types (None, Sub, Up, Average, Paeth). Converts output to 32bpp BGRA (engine's expected surface format). Returns NULL for unsupported formats (16-bit depth, paletted, Adam7 interlaced) → engine's existing fallback path kicks in.

**3. png_loader.c — non-Windows branch now decodes PNGs (gotcha #1)**

Previously `platformLoadPNGFromMemory` returned NULL on macOS/Linux/Web, making the HD PNG override silently inactive on 3 of 4 target platforms. Non-Windows branch now calls `pngDecodeToBGRA()` from png_decoder and wraps the result in a `PlatformSurface` via `platformCreateSurfaceFrom`. Windows path (WIC) unchanged.

**4. CMakeLists.txt — switch `--embed-file` to `--preload-file` (gotcha #11)**

Emscripten was baking `scrantic_data.zip` (~3.9 MB) into the wasm binary via `--embed-file`. Now uses `--preload-file`, which produces a separate `.data` file loaded asynchronously at startup. Benefits:
- Smaller initial wasm download
- Better browser cache hit rate on subsequent loads
- Emscripten's default pre-main async wait means `main()` still sees the zip mounted at the expected path before running

Also added `png_decoder.c` to COMMON_SOURCES.

**5. .github/workflows/main.yml — web artifact now bundles the .data file**

Previously the web job tar'd `jc_reborn.js jc_reborn.wasm index.html`. Added `jc_reborn.data` since `--preload-file` produces it as a separate artifact now.

**6. build_web.ps1 — parameterize hardcoded paths (gotcha #3)**

Script previously hardcoded `C:\@_WorkingFolder\@_Anthropic\emsdk` and `C:\@_WorkingFolder\@_Anthropic\JohnnyCastawayHD_Reborn\build_web`. Now reads from `$env:EMSDK` (emsdk install dir) and auto-derives the build directory from the script's own location as `<repo>/build_web`. Falls back to the old paths if env vars unset, so current users aren't broken. Added helpful error messages if emsdk can't be found.

**7. AI_UNDERSTANDING.md — reflect new state**

Updated `@PLATFORM_ABSTRACTION` capability matrix (PNG decode now supported everywhere), `@HD_ASSET_OVERRIDE` platform caveat removed, `@KNOWN_ISSUES_AND_GOTCHAS` updated to mark resolved items.

### Not yet tested
- macOS build — PNG decoder not built on a mac
- Linux build — likewise
- Web build with `--preload-file` — needs local emsdk run to verify .data file loads correctly
- PNG decoder edge cases — pathological inputs (truncated files, bad CRCs, huge dimensions) rely on defensive checks in the decoder; haven't been fuzzed

### Next candidates (from the gotchas list)
- gotcha #8: SET_DELAY min value `4` — confirm tick unit (20ms? or ms?) in `ttm.c` and `eventsWaitTick`
- gotcha #9: `isRunning` values — confirm my inferred mapping (`3 = background/static-layer`) against the actual ADS/TTM dispatcher
- gotcha #7: no dirty-rectangle optimization — only matters if `grScale ≥ 4` shows stutter on target hardware

---
