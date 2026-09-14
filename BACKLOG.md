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

All four platforms now build in CI. Rendering is verified on Windows and Web;
Linux and macOS are proven only as far as their decoders, because the check that
runs there is `dump`, which needs no window server.

| | Windows | Linux | Web | macOS |
|---|---|---|---|---|
| Builds | yes | yes | yes | yes |
| In CI | yes | yes | yes | yes |
| Decoders verified | yes | yes | yes | yes |
| **Rendering verified** | yes | **no** | yes | **no** |
| Ships in releases | yes | yes | yes | **no** |
| Tests | 27 smoke + 11 screensaver + 2,452-file corpus | decode parity vs Windows, all 2,452 byte-identical | 10-check browser smoke | decode parity vs Windows |

"Rendering verified" is the row that matters and the one that is easy to misread
off a green CI badge. Linux and macOS compile their window and blit code and then
never run a pixel of it in CI.

---

## Open

### macOS renders something nobody has looked at

**Resolved 2026-09-14: it builds, and its decoders are correct.** A `macos` job
on `macos-latest` runs `tests/unix-build.sh`, the same script Linux uses, and all
2,452 decoded files are byte-identical to the Windows golden manifest. It passed
first try, so the three fixes previously applied by reading alone at least
compile. Releases still ship no macOS artifact.

What is **still unverified is rendering**, and `dump` can never prove it: that
mode needs no window server, so parity says the decoders agree and says nothing
about `drawRect`. The open question is whether the frame comes out upside down.
The engine's buffer is top-down, `drawRect` builds a `CGImage` from it and draws
into an unflipped `NSView` where CoreGraphics puts the origin at bottom-left, and
the comment at `platform_macos.m:70` asserts the orientation is already fine. One
of the two is wrong.

**A test that could settle it without a Mac or a human.** The island scene is
sky at the top and sea at the bottom, so a vertical flip is detectable as a
luminance inversion. Run N frames windowed on the macOS runner, `screencapture`
the window, and assert the top band is brighter than the bottom. That is an
invariant rather than a pixel comparison, so it survives scaling, colour profiles
and scene selection. GitHub's macOS runners have a real window server, so this is
feasible; it was scoped but not built, to keep this pass from turning into an
open-ended macOS project.

Ruled out on the way: a macOS Docker image. Containers share the host kernel and
macOS needs XNU; `docker-osx` runs it under QEMU and needs `/dev/kvm`, which
Docker Desktop on WSL2 does not expose. Apple's licence also restricts macOS
virtualization to Apple hardware. CI already gives real Apple hardware for free.

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

### ~~`zipvfs` temp file is a TOCTOU~~ DONE 2026-09-14

Creation is now atomic: `_open` with `_O_CREAT|_O_EXCL|_O_RDWR|_O_BINARY|
_O_TEMPORARY|_O_SHORT_LIVED` then `_fdopen`, retrying a bounded 8 times on
`EEXIST` and stopping on anything else. The error message no longer claims
`tmpfile() failed` on a path that never called `tmpfile`.

### The Web present is the frame budget

`platformUpdateWindow` allocates a fresh `createImageData(1280, 960)` (4.7 MB)
and performs roughly 4.9M `HEAPU8` reads plus 4.9M typed-array writes in `EM_ASM`
JavaScript **every frame**, with no damage tracking. HD is on by default
(`"scale": 2`). A single `set()` from a heap subarray, with the BGRA swizzle done
once into a reusable buffer, would remove almost all of it.

This is why the missing yield mattered so much: the present is slow enough that
frames routinely outlast their own delay.

### Sound assets and the loader half-disagree

`sound0.wav` shipped and was never loaded, because the loop started at `i = 1`.
**Fixed 2026-09-14**: it starts at 0, so the data and the loader agree. Nothing
observable changed - no shipped TTM requests index 0 - but `soundPlay(0)` no
longer reports a missing sample about a file that is sitting in the archive.

Still open, and it is a data problem rather than a code one: `sound11.wav` and
`sound13.wav` are **absent from the archive entirely** while `NUM_OF_SOUNDS` is
25 and `ttm.c` plays a data-driven index. Both log a miss on every start under
`debug`. Either the files should be recovered from the original `SCRANTIC.SCR`
(`tools/extract_sound` exists for exactly that) or the gap should be recorded as
intentional.

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
- ~~**`jc_reborn island ads NAME TAG` never releases the island.**~~ **DONE
  2026-09-14.** `adsReleaseIsland` is now called on that path, guarded by the
  same `argIsland` flag that created it, so init and release are paired the way
  `storyPlay` already pairs them.

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
and the Web canvas copy.

**Correction to an earlier plan for this entry.** It said the cheap half was to
cap dimensions the way `pngDecodeToBGRA` caps at 16384×16384, on the grounds that
corrupt data can reach it. It cannot: `platformCreateSurface` has exactly ONE
caller outside the platform files, `graphics.c:351`, and it passes
`grRenderWidth`/`grRenderHeight`, which are engine-controlled. File-derived
dimensions go through `platformCreateSurfaceFrom` and the PNG decoder, which is
already capped. A cap here would guard nothing, so it was not added.

That leaves only the OOM case, which needs the contract changed to "may return
NULL" plus a caller audit across four backends, for a failure mode where a 4.7 MB
`calloc` failing means the machine is already gone. Low value, real cost.

### Web audio drops the channel count

`platformOpenAudio` sizes its buffer as `spec->samples` where Linux, macOS and
Windows all use `spec->samples * spec->channels`, and passes the same unscaled
figure as the callback length.

Deliberately **not** half-fixed. Every shipped WAV is mono - measured, all 23
files are 1 channel, 11025 Hz, 8-bit - so the multiplication is a no-op today,
and the `EM_ASM` scheduling block assumes mono interleaving as well. Correcting
only the buffer size would produce a silently wrong stereo path instead of a
consistently mono one. Fix both together, or not at all.

### The Web CI job is not reproducible

`.github/workflows/ci.yml` and `release.yml` both use
`mymindstorm/setup-emsdk@v14` with `version: latest`, which downloads
`emscripten-core/emsdk/archive/HEAD.zip` on every run. That means two things:

- **It fails when GitHub has a bad minute.** Observed 2026-09-14:
  `HTTP Error 504: Gateway Time-out` fetching that archive, on a commit whose
  only changes were Windows-side. A red CI that is nothing to do with the code
  teaches people to re-run rather than read, which is how a real failure gets
  waved through.
- **The toolchain silently moves.** A build that passed last week can fail today
  because upstream emsdk changed, with nothing in this repository's history to
  explain it. That is exactly the class of problem the golden corpus exists to
  catch everywhere else.

Pin a specific emsdk version and bump it deliberately. The release workflow wants
this more than CI does: a release should be reproducible from its tag, and right
now the web artifact depends on whatever emsdk `HEAD` was that day.

### Dead code

**Cleared 2026-09-14:** `platformMapRGB` (declared once, defined in all four
backends, called by nothing, and the Web one packed RGB while every surface in
that file is BGRA) is removed. `hexdump` and `storyGetForcedHoliday` are removed.
`createDumpDirs` is now `static`, since `dump.c` was its only user.

**CORRECTION, and the reason this section needs reading carefully.**
`grSaveZone` and `grSaveImage1` were listed here as dead. **They are not.**
`ttm.c:392` and `ttm.c:403` call them from the bytecode dispatch, for opcodes
0x4200 and 0x0400. They are reachable no-ops, which is a different defect: the
scripts invoke them, nothing happens, and `docs/AI_UNDERSTANDING.md` still
documents them as working. Removing them would have broken opcode handling.
They stay, and the category was wrong, not the observation.

`grRestoreZone` likewise ignores its parameters and frees the entire saved-zone
layer; its only non-TTM caller passes all zeros for exactly that side effect.

Still open:
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
- ~~`graphicsEnd()` and `atexit` both call `platformShutdown`~~ **DONE
  2026-09-14**, and it was redundancy rather than a bug: checked before removing,
  the second call was harmless on all four backends. Windows re-unregisters a
  class that is already gone and ignores the FALSE, Linux guards on `display` and
  NULLs it, macOS releases an already-nil queue, Web is empty. The `atexit`
  registration is the one kept, because it also covers `fatalError`, which exits
  without passing through `graphicsEnd`.
- No dirty-rectangle tracking anywhere: every frame composites and presents the
  full surface. At `grScale` 4 or higher this becomes CPU-bound.

### Screensaver polish

- ~~**No `VERSIONINFO`.**~~ **DONE 2026-09-14.** CMake passes the three version
  components to the `.rc` and the display strings are built back out of them, so
  the number still lives only in `CMakeLists.txt`. `JC_IS_SCR` lets the shared
  script describe whichever target it is linked into. The test asserts the
  binary's embedded version against `CMakeLists.txt` rather than a literal, so
  drift becomes a test failure.
  Worth knowing if this is ever touched: the block must be `1 VERSIONINFO`, not
  `VS_VERSION_INFO VERSIONINFO`, unless the script includes `<winver.h>`. That
  name is a `#define` for `1`; undefined, `rc.exe` silently emits a NAMED
  resource that Windows never reads, with no error, no warning, a `.res` that
  genuinely contains the version block, and every field reading back empty.
- The `/c` dialog is a message box, because the engine genuinely has no
  user-settable state (its persistence is two integers: the story day and the
  date it last advanced). If settings are ever wanted - sound, HD scale, forced
  holiday - note that `cfgFileRead` tolerates unknown keys but `cfgFileWrite`
  rewrites the file with only the two it knows, so any new key must be added to
  both or it is destroyed on the next day rollover.
- Fullscreen is primary-monitor only (`MONITOR_DEFAULTTOPRIMARY`), so other
  screens keep showing the desktop. **This is now a decision, not an oversight:**
  the owner was asked on 2026-09-14 and chose to leave it. Switching to the
  `SM_*VIRTUALSCREEN` metrics is about four lines if that ever changes, and the
  existing letterbox code would centre the island with black across every screen.
  Do not re-raise it as a bug.
- ~~**It does not exit on losing focus.**~~ **DONE 2026-09-14.** `WM_ACTIVATEAPP`
  with `wParam == FALSE` produces `EVENT_FOCUS_LOST`, gated on
  `evScreensaverMode` so a plain `jc_reborn.exe` is still usable as a background
  window. The `/p` preview needed no special case: `SCR_MODE_PREVIEW` never sets
  that flag. Two paired tests, and the gate was mutation-tested - removing it
  breaks the background-run check and leaves the screensaver check passing.

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

### Documentation has been spot-corrected, not audited

Five specific falsehoods were corrected in `4646848`: the phantom
`.github/workflows/main.yml` job matrix and the two `CHANGELOG.md` entries
recording edits to it, the claim that the non-Windows HD PNG path was inactive,
the web build instructions that produced an unservable directory and pointed at a
`jc_reborn.html` this build has never emitted, and a mingw toolchain path that
predated the 2026-04-21 reorganisation.

**`docs/AI_UNDERSTANDING.md` has not been read end to end.** It is ~950 lines
written largely by an AI describing its own understanding, and it has now been
caught inventing infrastructure that did not exist. Treat every load-bearing
claim in it as unverified until checked against the code. The corrected passages
say what was wrong rather than quietly dropping it, because the belief that CI
existed is the interesting part.

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
