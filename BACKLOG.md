# Backlog - johnny-castaway-rebornHD

## How to read this

Every entry here was **reproduced against the code**, and where a measurement is
quoted it was taken rather than estimated. Items that an audit claimed and that
did not survive checking are recorded in "Claims that did not hold" at the
bottom, so nobody re-raises them.

Severity is about consequence. Note that most of the remaining memory-safety
items are **latent**: real defects that the shipped data cannot currently reach.
That is stated per item rather than implied, because "unreachable today" and
"not a bug" are different things and the margin is often zero.

---

## The state of the project

Builds and is tested on Windows, Linux and Web, all three in CI. macOS is the one
platform that is neither built nor verified anywhere, and its backend has had
changes made to it by reading only.

| | Windows | Linux | Web | macOS |
|---|---|---|---|---|
| Builds | yes | yes | yes | **unverified** |
| Runs | yes | yes (headless `dump`) | yes | **unverified** |
| In CI | yes | yes | yes | no |
| Tests | 27 smoke + 7 screensaver + 2,452-file corpus | decode parity vs Windows, all 2,452 byte-identical | 10-check browser smoke | none |

---

## Open

### macOS is entirely unverified

`platform_macos.m` has had three fixes applied by reading: the `[NSApp
terminate:]` that never returned (so `zipvfs_shutdown` never ran), an unchecked
`AudioQueueAllocateBuffer` whose result was dereferenced on the next line, and
the preview-parent stub. None has been compiled, let alone run.

The platform audit also believes the frame is drawn **upside down**: the engine's
buffer is top-down (`platform_windows.c` sets `biHeight = -height`), and
`drawRect` builds a `CGImage` from it and draws into an unflipped `NSView`, where
CoreGraphics puts the origin at bottom-left. The comment at
`platform_macos.m:70` asserts the orientation is already correct. One of the two
is wrong and it cannot be settled without a Mac.

**Cheapest fix: add a macOS job to `.github/workflows/ci.yml`.** GitHub provides
macOS runners; a compile alone would catch most of this class, and `dump` runs
headless there exactly as it does on Linux, so the decode-parity check works too.

### Latent memory-safety, with zero margin

All fixed defensively in the engine hardening pass; listed because the *data*
margin is what makes them latent, and that margin is nil.

- TTM tag tables: `tagNo == numTags` **exactly** on all 41 shipped scripts. One
  extra `0x1111`/`0x1101` word writes past the allocation.
- Every TTM and ADS script decodes to its **exact** last byte; all sizes even.
- BMP pixel walks: all 116 BMPs sum to **exactly** their decoded size.
- The one item with real slack is `numImages`: 102 used against an array of 120.

Nothing here fires on the shipped archive. Everything here fires on a corrupt or
hand-edited one, which is the normal state of a 1992 data file being modded.

### `zipvfs` temp file is a TOCTOU

`_tempnam` names a file without creating it and `fopen(..., "w+b")` is
create-or-truncate, so anything that plants a file at that path in between is
silently truncated and used as the resource cache. Two concurrent instances
sharing `%TMP%` can collide the same way. `_open` with `_O_CREAT|_O_EXCL|
_O_TEMPORARY` plus `_fdopen` makes creation atomic and keeps delete-on-close.

Its failure message also says `tmpfile() failed` on a path that never calls
`tmpfile`, which will mislead whoever triages it.

### The Web present is the frame budget

`platformUpdateWindow` allocates a fresh `createImageData(1280, 960)` (4.7 MB)
and performs roughly 4.9M `HEAPU8` reads plus 4.9M typed-array writes in `EM_ASM`
JavaScript **every frame**, with no damage tracking. HD is on by default
(`"scale": 2`). A single `set()` from a heap subarray, with the BGRA swizzle done
once into a reusable buffer, would remove almost all of it.

This is why the missing yield mattered so much: the present is slow enough that
frames routinely outlast their own delay.

### Sound assets and the loader disagree

`sound0.wav` ships in the archive and is **never loaded**: the loop starts at
`i = 1`. `sound11.wav` and `sound13.wav` are **absent** from the archive
entirely, while `NUM_OF_SOUNDS` is 25 and `ttm.c` plays a data-driven index. No
shipped script requests 0, 11 or 13, so nothing is audibly missing today; the
mismatch is between the data and the code's expectations.

### Init/teardown asymmetries that are unreachable today

Each of these is a real pairing bug that the current call graph happens to keep
out of reach. They are listed because "unreachable" here rests on every entry
point running exactly once per process, which is a property nobody is enforcing.

- **`adsInit` frees nothing.** It sets `isRunning = TTM_FREE` on all 10 threads
  but never calls `grFreeLayer` on their `ttmLayer`, and `adsAddScene`
  unconditionally overwrites that pointer with a fresh `grNewLayer`. All three
  callers (`adsPlaySingleTtm`, `adsPlayBench`, `storyPlay`) run at most once,
  before any scene exists, so the array is still statically zeroed each time.
  The first "restart the story without exiting" feature makes this leak
  per-restart.
- **`jc_reborn island ads NAME TAG` never releases the island.**
  `adsInitIsland` has two callers, `adsReleaseIsland` has one. `storyPlay` pairs
  them; the CLI path at `jc_reborn.c:644` does not, so the backdrop, holiday and
  cloud slots plus their BMP surfaces are still held at `graphicsEnd`. The
  process exits immediately afterwards, so nothing accumulates across runs.

### Unchecked allocations in all four platform backends

`platformCreateWindow` and `platformCreateSurface` `malloc` their structs and
dereference on the next line, in every backend. The surface pixel buffer is the
worse case:

```c
surface->pixels = (uint8*)calloc(width * height, 4);
...
return surface;            /* "success" even when pixels == NULL */
```

That NULL then flows into `StretchDIBits`, `XPutImage`, `CGBitmapContextCreate`
and the Web canvas copy. It is inconsistent with this codebase's own convention:
`pngDecodeToBGRA` returns NULL on any allocation failure and caps dimensions at
16384×16384, while `platformCreateSurface` applies no cap at all.

OOM-gated, so latent - but fixing it means changing the contract to "may return
NULL" and auditing every caller, which is why it is here rather than done.

### Web audio drops the channel count

`platformOpenAudio` sizes its buffer as `spec->samples` where Linux, macOS and
Windows all use `spec->samples * spec->channels`, and passes the same unscaled
figure as the callback length.

Deliberately **not** half-fixed. Every shipped WAV is mono - measured, all 23
files are 1 channel, 11025 Hz, 8-bit - so the multiplication is a no-op today,
and the `EM_ASM` scheduling block assumes mono interleaving as well. Correcting
only the buffer size would produce a silently wrong stereo path instead of a
consistently mono one. Fix both together, or not at all.

### Dead code

- **`platformMapRGB` is implemented in all four backends and called by nothing.**
  Verified by grepping the whole tree: only the declaration and the four
  definitions. The Web one also returns RGB packing while every surface in that
  file is BGRA, so if it were ever wired up it would be wrong.
- `grSaveZone` and `grSaveImage1` take five parameters, `UNUSED` all of them and
  have empty bodies. `grRestoreZone` ignores its parameters and frees the entire
  saved-zone layer; its only non-TTM caller passes all zeros for that side
  effect. `docs/AI_UNDERSTANDING.md` still documents them as working.
- `hexdump` (`utils.c`) and `storyGetForcedHoliday` (`story.c`) each have exactly
  two references in the repo: the definition and the declaration.
- `createDumpDirs` has external linkage but is used only inside `dump.c`.
- `parseResourceFile` takes a `filename` it immediately `UNUSED`es, rebuilding
  the path from the `mapFile` global its caller populated one line earlier. The
  caller passes a real string to both functions as if both used it.
- `TMapFileEntry.length` is written by `parseResourceFile` and read nowhere. Its
  name suggests it should bound the per-entry read, which is exactly the kind of
  bound the TTM and ADS loaders now carry.
- The TTM palette opcodes (`SET_PALETTE_SLOT` 0x1061, `LOAD_PALETTE` 0xF05F) and
  `DRAW_BACKGROUND` 0x0080 / `DRAW_SCREEN` 0xB606 parse their arguments and then
  only `debugMsg`. Harmless as shipped: `MAX_PAL_RESOURCES` is 1, so there is
  never a second palette to switch to.
- `ads.c`'s `if (adsResource == NULL)` after `findAdsResource` is unreachable:
  that function calls the `noreturn` `fatalError` on a miss. Same shape at three
  other sites.

### Optimization

- `grDrawSpriteFlip` calls `platformBlitSurface` **once per column** of the
  sprite, so a 96-pixel-wide sprite costs 96 blit calls with full setup each. A
  single blit with a horizontal-flip flag would replace it.
- `graphicsEnd()` calls `platformShutdown()` and `eventsInit` separately
  registers `atexit(platformShutdown)`, so it runs twice on a normal exit.
- No dirty-rectangle tracking anywhere: every frame composites and presents the
  full surface. At `grScale` 4 or higher this becomes CPU-bound.

### Screensaver polish

- **No `VERSIONINFO`.** The `STRINGTABLE` is done - the dropdown now reads
  "Johnny Reborn" instead of the filename, asserted by
  `tests/Test-ScreensaverPreview.ps1`, which loads the `.scr` as a data file and
  reads string resource 1. `VERSIONINFO` is what is still missing, and it is
  what puts a product name and version in the file properties dialog.
  Note before adding it: `FILEVERSION` needs comma-separated integers, so the
  version has to reach `jc_reborn.rc` from `project(... VERSION ...)` rather than
  being typed in. That means `set_source_files_properties(... COMPILE_DEFINITIONS)`
  from CMake plus `#ifndef` fallbacks for the hand-maintained `vs/` projects,
  which do not define them - otherwise the version now lives in three places.
- The `/c` dialog is a message box, because the engine genuinely has no
  user-settable state (its persistence is two integers: the story day and the
  date it last advanced). If settings are ever wanted - sound, HD scale, forced
  holiday - note that `cfgFileRead` tolerates unknown keys but `cfgFileWrite`
  rewrites the file with only the two it knows, so any new key must be added to
  both or it is destroyed on the next day rollover.
- Fullscreen is primary-monitor only (`MONITOR_DEFAULTTOPRIMARY`). On a
  multi-monitor machine the other screens are left showing the desktop.

### Cross-platform contract gaps

- `EVENT_QUIT` is never produced on macOS or Web, so `events.c`'s handler is dead
  code on half the backends and the close button cannot terminate the app there.
- `EVENT_WINDOW_REFRESH` exists only on Linux.
- `platformPollEvent` drain semantics differ: Windows and Web buffer into a queue
  and return 0 only when empty; Linux and macOS return 0 at the first event they
  do not translate, so an untranslated event truncates the drain loop.
- Presentation differs: Windows letterboxes with aspect preservation, Linux
  `XPutImage` is 1:1 at the origin, macOS draws into a fixed `CGRect`. Fullscreen
  on Linux or macOS puts the frame in a corner at native size.

### Documentation that is still wrong

`docs/AI_UNDERSTANDING.md` describes a `.github/workflows/main.yml` job matrix in
detail (lines 64-70) and `docs/CHANGELOG.md` twice records edits to that file.
**It never existed** until this work added real workflows, and the fiction is the
direct reason three of four platforms went unbuilt for months. The same document
claims at line 219 that the non-Windows HD PNG path is inactive; it has been live
since the decoder landed.

---

## Claims that did not hold

Recorded so they are not re-raised. Each was investigated and rejected with
evidence.

- **"HD sprites render with bright halos on Linux, macOS and Web."** The code
  asymmetry was real - the decoder emitted straight alpha while all four blitters
  implement premultiplied source-over - but the symptom cannot occur. Measured
  across **all 2,402 HD PNGs, 39,254,880 pixels: zero partially transparent
  pixels.** Alpha is strictly 0 or 255, where straight and premultiplied are
  identical and both blitter fast paths absorb every pixel. Fixed anyway, because
  it fires the moment anti-aliased art is added, but it was never visible.
  Side note worth keeping: the HD art is hard-edged, so it was upscaled without
  anti-aliasing.
- **"Linux and macOS call the audio callback without holding the mutex."** They
  do not need to. `soundCallback` takes `platformLockAudio()` itself and so does
  `soundPlay`, so the critical section is inside the callback. "Fixing" it would
  deadlock on the first sound, because `audioMutex` is a default, non-recursive
  pthread mutex. Windows only gets away with wrapping the callback because
  `CRITICAL_SECTION` is recursive.
- **"CMake here tops out at the Visual Studio 17 2022 generator."** It offers
  `Visual Studio 18 2026` and defaults to it, so a plain `cmake ..` already
  matches the `v145` toolset the `vs/` projects pin. No mismatch.
- **"`fsutil`-style unchecked returns in `ttmLoadTtm` are reachable."** The
  one-byte over-read at the tag scan is real in the code but unreachable on
  shipped data: no TTM has an odd length and every one decodes exactly.

---

## Notes for whoever picks this up

The two things most likely to waste your time, both learned the hard way here:

**The RNG makes false negatives that look completely convincing.** Scene
selection, cloud count, backdrop choice, low tide and path finding all come off
one stream. The night branch skips a `rand()` call, so the same seed reaches
different scenes by day and by night: seed 2 gives 1,244 cloud draws by day and
exactly 0 at night. "Clouds are broken at night" is the obvious conclusion and it
is wrong. Always compare across several seeds before believing a negative.

**The saved story day is an input.** `~/.jc_reborn` holds the story day, which
selects eligible scenes, so a developer's saved progress silently changes what a
test exercises. Two cloud assertions passed locally and were incapable of passing
on a clean machine for exactly this reason. `tests/Invoke-SmokeTests.ps1` now
points `HOME` at a throwaway directory per run; keep it that way.

Three smaller traps, each of which produced a green result over broken code here:

**A negative test must assert the diagnostic, not just a non-zero exit.** Three
assertions read `$r.Code -ne 0`. The harness returns `-999` on timeout, which is
also non-zero, so when `fatalError` started raising a modal dialog on
harness-spawned processes, all three hung for their full 120 seconds and then
reported `ok`. The suite was green while the binary was hanging. They now require
the specific message.

**An error path that blocks is worse than one that is silent.** The dialog was
added so the `.scr` could report a missing archive, guarded by
`GetConsoleWindow() == NULL`. That is also true of any process started with
`CreateNoWindow` and redirected pipes, i.e. every CI run. The right question is
whether stderr is *writable* (`GetFileType` on the handle), not whether a console
window exists.

**Playwright's `page.evaluate` ignores `set_default_timeout`.** The web freeze
check was built on it, so a frozen tab could not fail the check - only hang it,
which it did twice, for 20 and 30 minutes. Measured against a page blocked for
120s: `wait_for_function(timeout=5000)` raised in 5.0s, `evaluate` returned after
114.1s and reported success. Use `wait_for_function` for anything that must
survive an unresponsive page.
