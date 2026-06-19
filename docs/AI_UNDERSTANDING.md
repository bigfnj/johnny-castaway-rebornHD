---
project: Johnny Reborn HD
upstream: Jeremie Guillaume, "Johnny Reborn" (2019), GPLv3
fork: HD PNG override + zipvfs + platform-native backends (post-SDL2)
languages: C11 + Objective-C (macOS only)
license: GPLv3
generated: 2026-04-20
audience: machine-readable (dense, file:line refs, opcode tables)
---

# @PROJECT_SUMMARY

Open-source reimplementation of the 1992 Sierra / Dynamix "Johnny Castaway" Windows-3.x screensaver. Drives Johnny (the shipwrecked cartoon character) through ~63 daily-progression scenes on a desert island, with walk-between-scene animation, calendar-aware holidays (Halloween/StPatrick/Christmas/NewYear), and an 11-day story arc (raft-building progression) persisted in `~/.jc_reborn`.

Fork distinguishers vs. upstream Johnny Reborn:
- **No SDL2** — native backends per OS (platform_linux.c = X11+ALSA; platform_macos.m = Cocoa+AudioToolbox; platform_windows.c = Win32+WinMM; platform_web.c = Emscripten+HTML5 Canvas + Web Audio).
- **zipvfs** — all game data (RESOURCE.MAP/001, SCRANTIC-derived sounds, optional HD PNG pack) served from a single `scrantic_data.zip` via miniz.
- **HD asset override** — optional PNG replacements for SCR backgrounds and BMP sprites at configurable integer upscale (1×..8×), keyed off `data/hd/manifest.json` inside the zip.
- **Per-pixel alpha** for sprites (with legacy magenta-key fallback, RGB `#A800A8`).

Total source ~250 KB C/H (engine ~5-7 KLOC) + miniz (vendored, ~400 KB). 19 engine files + 5 platform files + 4 miniz files + 2 extraction tools.

---

# @BUILD_SYSTEM

**Build tool:** CMake ≥ 3.10. Single target `jc_reborn`. Platform auto-detected:

| Condition | Source selection | Define | Linker |
|---|---|---|---|
| `EMSCRIPTEN` | `platform_web.c` | `-DPLATFORM_WEB` | `-Os -sASYNCIFY -sALLOW_MEMORY_GROWTH -sSTANDALONE_WASM=0 -sNO_EXIT_RUNTIME -sFORCE_FILESYSTEM --preload-file scrantic_data.zip@scrantic_data.zip`; suffix `.js` (+ `.wasm` + `.data`) |
| `WIN32` | `platform_windows.c` | `-DPLATFORM_WINDOWS` | `gdi32 user32 winmm windowscodecs ole32 uuid`; MinGW cross adds `-static-libgcc` |
| `APPLE` | `platform_macos.m` (compiled `-x objective-c`) | `-DPLATFORM_MACOS` | `Cocoa.framework AudioToolbox.framework` |
| `UNIX` (else) | `platform_linux.c` | `-DPLATFORM_LINUX` | `X11 ALSA pthread m` |
| else | — | — | `FATAL_ERROR "Unsupported platform"` |

**Common sources** (CMakeLists.txt:30-55, organized by subtree after 2026-04-21 reorg):
- `src/engine/` — jc_reborn, utils, uncompress, resource, dump, story, walk, calcpath, ads, ttm, island, bench, graphics, sound, events, config
- `platform/` — png_loader, png_decoder, zipvfs (I/O adapters, platform-agnostic)
- `third_party/miniz/` — miniz, miniz_tdef, miniz_tinfl, miniz_zip

`target_include_directories(jc_reborn PRIVATE …)` adds `src/engine`, `src/data`, `platform`, `third_party/miniz` so `#include "foo.h"` resolves without source-side path changes.

**Compiler flags:** `-Wall -Wpedantic -Wextra -Wshadow` on GCC/Clang; `/W4` on MSVC. C11. MSVC build also sets `/D_CRT_SECURE_NO_WARNINGS /DNOMINMAX`.

**Artifacts:**

| Platform | Binary | Runtime deps |
|---|---|---|
| Linux | `jc_reborn` (ELF) | libX11, libasound | 
| macOS | `jc_reborn` (Mach-O) | (frameworks linked) |
| Windows | `jc_reborn.exe` (PE) | Win32 DLLs in OS |
| Web | `jc_reborn.js` + `jc_reborn.wasm` + `jc_reborn.data` + `index.html` | Browser with WebAssembly + Web Audio |

**Cross-compile to Windows from Linux/macOS:** `toolchain-mingw.cmake` locates `x86_64-w64-mingw32-gcc/g++/windres`. Used by CI.

**Local Windows web build script:** `scripts/build_web.ps1` — wraps `emcmake cmake $repoRoot -DCMAKE_BUILD_TYPE=Release` + `emmake cmake --build .`. Reads `$env:EMSDK` (with legacy hardcoded fallback for backward compat) and `$env:JCR_BUILD_DIR` (defaults to `<repo>/build_web`). Repo root auto-derived as `Split-Path -Parent $scriptDir`.

**VS project:** `vs/jc_reborn.sln` + `vs/jc_reborn/jc_reborn.vcxproj` + `.filters` + `jc_reborn.ico` + `jc_reborn.rc`. Also `vs/extract_sound/` and `vs/extract_walk_data/` for the two tools.

**CI** (`.github/workflows/main.yml`): trigger on push/PR to `master`; 4 parallel build jobs + `release` job gated on `push && ref == master`:

| Job | Runner | Steps |
|---|---|---|
| `macos` | macos-latest | cmake + build; artifact `jc_reborn_macos_v0<run>` |
| `linux` | ubuntu-latest | apt install `libx11-dev libasound2-dev`; cmake + build; artifact `jc_reborn_linux_v0<run>` |
| `windows` | ubuntu-latest (cross) | apt install `mingw-w64`; cmake `-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-mingw.cmake`; build; artifact `jc_reborn_windows_v0<run>.exe` |
| `web` | ubuntu-latest | `mymindstorm/setup-emsdk@v12`; emcmake + build; tar `jc_reborn.js jc_reborn.wasm jc_reborn.data index.html` |
| `release` | ubuntu-latest | Download all artifacts; `actions/create-release@v1` with tag `v0.<run>`; upload 4 release assets |

Repo layout on disk (after 2026-04-21 structural reorg):
```
@Project-JohnnyHD/
├── CMakeLists.txt           — cross-platform build config
├── README.md / LICENSE / index.html / favicon.ico  — top-level docs + web entry
├── src/
│   ├── engine/              — engine core (VMs, graphics, sound, story, I/O plumbing)
│   └── data/                — static data tables baked in as C headers
├── platform/                — platform abstraction + HD I/O adapters (zipvfs, png)
├── third_party/miniz/       — vendored zip/deflate
├── assets/scrantic_data.zip — runtime data bundle; embedded into wasm via --preload-file
├── cmake/toolchain-mingw.cmake — MinGW cross-compile toolchain
├── scripts/build_web.ps1    — local Windows convenience wrapper around emcmake
├── tools/                   — extract_sound.c, extract_walk_data.c + Makefiles
├── vs/                      — .sln + 3 .vcxproj for native Windows build
├── .github/workflows/main.yml — 4-platform CI + release
└── docs/                    — AI_UNDERSTANDING.md, CHANGELOG.md, HD_README.md
```

Runtime layout on disk (non-web):
```
<cwd>/
  jc_reborn(.exe)
  scrantic_data.zip        # required at runtime; source-of-truth at assets/scrantic_data.zip.
                           # Copy/symlink next to the binary for local runs.
                           # Web target bakes it in via Emscripten --preload-file.
```
Inside `scrantic_data.zip`:
```
data/RESOURCE.MAP                # opened by parseResourceFiles()
data/RESOURCE.001                # resource data file; path via RESOURCE.MAP header
data/sound1.wav .. sound24.wav   # extracted sounds; loaded by soundInit()
data/hd/manifest.json            # optional; triggers HD mode
data/hd/SCR/<NAME>.SCR.png       # optional HD screens (e.g. OCEAN00.SCR.png)
data/hd/BMP/<NAME>.BMP/<NNN>.png # optional HD per-sprite images (3-digit, zero-padded)
```

Web build: `assets/scrantic_data.zip` is `--preload-file`'d into a separate `jc_reborn.data` file via Emscripten. Must be served alongside `jc_reborn.js` + `jc_reborn.wasm` + `index.html`. Emscripten waits for preload to finish before calling `main()`, so engine code is unaffected.

---

# @RUNTIME_ASSET_LAYOUT

**zipvfs** (`zipvfs.c:19-133`) — thin miniz wrapper:

| API | Purpose |
|---|---|
| `zipvfs_init(path)` | Open zip (fatal on failure); sets `g_zipInitialized` |
| `zipvfs_fopen(entry) -> FILE*` | Extract to heap, write to `tmpfile()` / Windows `_tempnam + fopen(..., "w+bTD")`, rewind → returns seekable FILE* for legacy parsers |
| `zipvfs_read(entry, *size) -> uint8*` | Extract entry to heap (`mz_zip_reader_extract_to_heap`); caller `free()`s |
| `zipvfs_exists(entry) -> int` | `mz_zip_reader_locate_file` returns ≥ 0 |
| `zipvfs_shutdown()` | `mz_zip_reader_end` |

Opened exactly once from `main()` (`jc_reborn.c:368`): `zipvfs_init("scrantic_data.zip")` → `parseResourceFiles("data/RESOURCE.MAP")` → ... → `zipvfs_shutdown()` (line 445).

**Windows tmpfile quirk:** `tmpfile()` requires admin; code uses `_tempnam` + `fopen(..., "w+bTD")` instead — `T` = short-lived, `D` = delete-on-close.

---

# @PLATFORM_ABSTRACTION

Defined in `platform.h` (162 lines). Engine never touches OS APIs directly — all goes through this interface. Opaque types: `PlatformWindow`, `PlatformSurface`, `PlatformRect`.

**Interface catalog:**

```c
// Lifecycle
int  platformInit(void);
void platformShutdown(void);
const char* platformGetError(void);

// Window
PlatformWindow* platformCreateWindow(const char* title, int w, int h, int fullscreen);
void            platformDestroyWindow(PlatformWindow*);
void            platformShowCursor(int show);
void            platformToggleFullscreen(PlatformWindow*);
void            platformUpdateWindow(PlatformWindow*);
PlatformSurface* platformGetWindowSurface(PlatformWindow*);

// Surfaces (32bpp BGRA implied by png_loader output format; see graphics.c uses)
PlatformSurface* platformCreateSurface(int w, int h);
PlatformSurface* platformCreateSurfaceFrom(void* pixels, int w, int h, int pitch);
void             platformFreeSurface(PlatformSurface*);
void             platformLockSurface(PlatformSurface*);
void             platformUnlockSurface(PlatformSurface*);
uint8*           platformGetSurfacePixels(PlatformSurface*);
int              platformGetSurfacePitch(PlatformSurface*);
int              platformGetSurfaceWidth(PlatformSurface*);
int              platformGetSurfaceHeight(PlatformSurface*);
int              platformGetSurfaceBytesPerPixel(PlatformSurface*);

// Drawing
void    platformBlitSurface(PlatformSurface* src, PlatformRect* sr,
                            PlatformSurface* dst, PlatformRect* dr);
void    platformFillRect(PlatformSurface*, PlatformRect*, r,g,b,a);
void    platformSetColorKey(PlatformSurface*, r,g,b);
void    platformSetClipRect(PlatformSurface*, PlatformRect*);
void    platformGetClipRect(PlatformSurface*, PlatformRect*);
uint32  platformMapRGB(PlatformSurface*, r,g,b);

// Events
int platformPollEvent(PlatformEvent*);      // 1 = event retrieved, 0 = none

// Timing
uint32 platformGetTicks(void);              // ms since init
void   platformDelay(uint32 ms);

// Audio (SDL_Audio-style callback API, kept for compatibility with sound.c)
typedef void (*PlatformAudioCallback)(void* userdata, uint8* stream, int len);
typedef struct { int freq; uint16 format; uint8 channels;
                 uint16 samples; PlatformAudioCallback callback; void* userdata; } PlatformAudioSpec;
int  platformInitAudio(void);
void platformCloseAudio(void);
int  platformOpenAudio(PlatformAudioSpec*);
void platformPauseAudio(int pause);
void platformLockAudio(void);
void platformUnlockAudio(void);
int  platformLoadWAVFromMemory(const uint8* data, uint32 size,
                               PlatformAudioSpec* spec, uint8** buf, uint32* len);
void platformFreeWAV(uint8* buf);

// Optional HD helper (only Windows implements; others return NULL → legacy path)
PlatformSurface* platformLoadPNGFromMemory(const uint8* data, size_t size);
```

**PlatformKeyCode:** `KEY_UNKNOWN KEY_SPACE KEY_RETURN KEY_ESCAPE KEY_M KEY_LALT`.
**PlatformEventType:** `EVENT_NONE EVENT_QUIT EVENT_KEY_DOWN EVENT_KEY_UP EVENT_WINDOW_REFRESH`.
**PlatformKeyMod:** bitmask — `KEYMOD_{NONE,LALT,RALT,LSHIFT,RSHIFT,LCTRL,RCTRL}`.

**Per-platform implementation map:**

| Concern | Linux (`platform_linux.c`) | macOS (`platform_macos.m`) | Windows (`platform_windows.c`) | Web (`platform_web.c`) |
|---|---|---|---|---|
| Window | X11 (`Display*`, `Window`) | Cocoa `NSWindow` + `NSView` | `CreateWindowEx` + GDI | HTML5 Canvas via Emscripten |
| Blit / present | X11 `XPutImage` + `XFlush` | `NSBitmapImageRep` → `NSImage` | `BitBlt` / `StretchDIBits` | Emscripten `emscripten_set_canvas_element_size` + direct pixel copy |
| Events | `XPending`/`XNextEvent` → translate keycodes | NSEvent via `NSApplication` event loop | `PeekMessage`/`DispatchMessage` | `emscripten_set_{keydown,keyup,...}_callback` queued |
| Audio | ALSA `snd_pcm_open` + worker thread + ring buffer | `AudioToolbox` `AudioQueue` callback | `waveOutOpen` + `WAVEHDR` queue, `waveOutWrite` | Web Audio via Emscripten `EM_ASM`; `AudioContext` |
| Timer | `clock_gettime(CLOCK_MONOTONIC)` | `mach_absolute_time` / `CFAbsoluteTimeGetCurrent` | `GetTickCount` / `QueryPerformanceCounter` | `emscripten_get_now()` |
| PNG decode | **minimal PNG decoder** via `png_decoder.c` (miniz-backed inflate; 8-bit RGB/RGBA/GA non-interlaced) | **minimal PNG decoder** same as Linux | WIC (Windows Imaging Component) via `IWICImagingFactory` + `GUID_WICPixelFormat32bppPBGRA` — see `png_loader.c:42-129` | **minimal PNG decoder** same as Linux |

**PNG decode detail (Windows only, `png_loader.c`):**
1. Lazy `CoInitializeEx(NULL, COINIT_MULTITHREADED)` once.
2. Create `IWICImagingFactory` → `IWICStream::InitializeFromMemory` → `CreateDecoderFromStream(..., WICDecodeMetadataCacheOnLoad)` → `GetFrame(0)`.
3. `IWICFormatConverter::Initialize(..., GUID_WICPixelFormat32bppPBGRA, WICBitmapDitherTypeNone, NULL, 0.0, WICBitmapPaletteTypeCustom)`.
4. `GetSize` → overflow checks (UINT_MAX/4 and stride × height) → `malloc(stride × h)` → `CopyPixels(NULL, stride, bufferSize, pixels)`.
5. `platformCreateSurfaceFrom(pixels, w, h, stride)` → returned as-is.
6. Always-run cleanup releases all COM interfaces.

Non-Windows: HD PNG fallback path is inactive; engine uses built-in BMP decoder at `grScale × grScale` nearest-neighbor upscaling (see `graphics.c:675-695`).

---

# @ENGINE_BOOT

**Entry:** `jc_reborn.c:361 main(argc, argv)`.

```
parseArgs(argc, argv)                        # 243-358
  -> one-of: argDump, argBench, argTtm, argAds, (else) argPlayAll
  -> flags: grWindowed, soundDisabled, argIsland, debugMode, evHotKeysEnabled, argMinimize
  -> forced holiday via storySetForcedHoliday()
  -> validate mutual exclusion (line 353); argPlayAll = 1 if no mode

[argDump]    debugMode = 1

zipvfs_init("scrantic_data.zip")             # jc_reborn.c:368
parseResourceFiles("data/RESOURCE.MAP")      # resource.c — populates global arrays

if (argPlayAll) {
    graphicsInit();                          # platform + window + palette + srand + events
    if (argMinimize) minimizeConsoleWindow();  # Windows-only ShowWindow(SW_MINIMIZE)
    soundInit();
    storyPlay();                             # never returns; exits via events loop
}
else if (argDump)   dumpAllResources();
else if (argBench)  graphicsInit(); adsPlayBench(); graphicsEnd();
else if (argTtm)    graphicsInit + soundInit; adsPlaySingleTtm(args[0]); soundEnd + graphicsEnd();
else if (argAds)    graphicsInit + soundInit; {argIsland?storyUpdateIslandFromDateAndTime()+adsInitIsland():adsNoIsland()}; adsPlay(args[0], tag); soundEnd + graphicsEnd();

zipvfs_shutdown(); return 0;
```

**CLI grammar:**
```
jc_reborn [OPT...] [MODE]
MODE = help | version | dump | bench | ttm <TTMNAME> | ads <ADSNAME> <TAGNO> | (default = play story)
OPT  = window | minimize | nosound | island | debug | hotkeys
     | holiday <halloween|stpatricks|christmas|newyear|random|none|auto>
     | (shorthand) halloween|stpatricks|christmas|newyear|xmas|random|none|auto
```

**Holiday flag resolution (`jc_reborn.c:93-167, 278-287`):**
- normalizeToken strips non-alnum + lowercases
- numeric `0..4` = direct
- `auto|calendar|date|system` → `-1` (use system date)
- `random|rand|any` → pick 1..4 from independent RNG (mix `time()` + `clock()`, not affecting main rand stream)
- `none|no|off|noholiday` → 0
- `halloween` → 1, `stpatricks/stpatrick/...` → 2, `christmas|xmas` → 3, `newyear|newyears|newyearseve` → 4
- `storySetForcedHoliday(h)` overrides calendar detection

**Hotkeys** (if `evHotKeysEnabled`, `events.c`):
| Key | Effect |
|---|---|
| `ESC` | terminate (graphicsEnd + exit 255) |
| `SPACE` | toggle pause |
| `M` | toggle maxSpeed (uncap FPS) |
| `ALT+RETURN` | toggle fullscreen |
| `RETURN` (while paused) | advance one frame (`oneFrame=1`) |

---

# @ENGINE_MAIN_LOOP

**Frame tick abstraction** (`events.c:66-95`):
```c
void eventsWaitTick(uint16 delay) {
    delay *= 20;  // each unit = 20ms
    oneFrame = 0;
    eventsProcessEvents();
    while ( (paused && !oneFrame) ||
            (!maxSpeed && (platformGetTicks() - lastTicks < delay)) ) {
        platformDelay(5);
        eventsProcessEvents();
    }
    lastTicks = platformGetTicks();
}
```
- Delay arg is in **20ms ticks** (so `delay=6` → 120ms). Fixed-timestep, no delta-time.
- Pause blocks the loop until SPACE (unpause) or RETURN (oneFrame step).
- `maxSpeed=1` drops the sleep entirely.

**Story outer loop** (`story.c` / `storyPlay`):
```
storyUpdateCurrentDay()                  # roll currentDay on calendar date change
storyCalculateIslandFromDateAndTime()    # set night (clock time), holiday (calendar)
finalScene = storyPickScene(FINAL, 0)    # terminal scene for the pass
if finalScene.flags & ISLAND {
    storyCalculateIslandFromScene(finalScene)   # randomize xPos, yPos, raft stage, lowTide
    adsInitIsland()                             # spawn ttmBackgroundThread + draw island, waves, raft, clouds, holiday
}
for i in range(6 + rand()%14):           # 6..19 intermediate scenes
    scene = storyPickScene(wantedFlags, unwantedFlags)
    if prevSpot != -1:
        adsPlayWalk(prevSpot, prevHdg, scene.spotStart, scene.hdgStart)
    ttmDx = island.xPos + (LEFT_ISLAND ? 272 : 0); ttmDy = island.yPos
    adsPlay(scene.adsName, scene.adsTagNo)
    prevSpot, prevHdg = scene.spotEnd, scene.hdgEnd
adsPlayWalk(prevSpot, prevHdg, finalScene.spotStart, finalScene.hdgStart)
adsPlay(finalScene.adsName, finalScene.adsTagNo)
grFadeOut()
→ repeat forever (only exits via ESC/QUIT → exit(255))
```

**ADS per-frame loop** (`ads.c:658-806, adsPlay`):
```
while any ttmThread isRunning:
  if ttmBackgroundThread.timer == 0:
    islandAnimate(&ttmBackgroundThread)
    ttmBackgroundThread.timer = ttmBackgroundThread.delay   # 8..12
  for i in 0..MAX_TTM_THREADS-1:
    if ttmThreads[i].isRunning == TTM_RUNNING and ttmThreads[i].timer == 0:
      ttmPlay(&ttmThreads[i])                               # execute TTM bytecode until yield
  grUpdateDisplay(&ttmBackgroundThread, ttmThreads, &ttmHolidayThread, &ttmCloudsThread)
  mini = min(timer across all active threads)
  decrement all timers by mini
  eventsWaitTick(mini)                                      # sleep + handle input
```

**Allocation profile** (audited 2026-04-20):
- Startup (`parseResourceFiles`): ~100+ `safe_malloc` calls for resource buffers, tags, palettes. One-time.
- Scene start (LOAD_IMAGE → `grLoadBmp`, LOAD_SCREEN → `grLoadScreen`, `adsAddScene` → `grNewLayer`): ~5-10 allocs per scene; fires 6-19 times per story pass (~once per minute).
- Scene end (`adsStopScene` → `grReleaseBmp` → `grFreeLayer`): matching frees.
- **Per-frame render loop: zero allocations.** `grUpdateDisplay` only blits existing surfaces; `platformBlitSurface` is a pure pixel-copy loop; `ttmPlay`'s opcode dispatch doesn't allocate. The only allocator-invoking opcodes are LOAD_IMAGE / LOAD_SCREEN which a well-behaved TTM fires once per scene entry, not per frame. A defensive guard was added to `grLoadBmp` (2026-04-20) to skip the full release-decode cycle if the slot already holds the same BMP name — protects against a TTM that fires LOAD_IMAGE on unchanged name inside its animation loop.

**Layer composition** (`graphics.c: grUpdateDisplay`):
1. `grBackgroundSfc` (island + SCR background) → window surface.
2. `grSavedZonesLayer` (if any) — transient overlays restored by RESTORE_ZONE.
3. For `i in 0..MAX_TTM_THREADS-1`: `ttmThreads[i].ttmLayer` (in slot order).
4. `ttmHolidayThread.ttmLayer` (holiday decorations).
5. `ttmCloudsThread.ttmLayer` (clouds, drifts separately).
6. `platformUpdateWindow(platform_window)` → present.

---

# @RESOURCE_FORMAT

Files addressed inside `scrantic_data.zip`:

**RESOURCE.MAP** (~1461 B):
```
[6 bytes  header/flags]
[13 bytes resource filename, e.g. "RESOURCE.001"]
[uint16   numEntries]
[ struct{ uint32 length; uint32 offset; }[numEntries] ]
```

**RESOURCE.001** (~1.17 MB): concatenated resources; each entry at its map offset:
```
[13 bytes name, e.g. "ACTIVITY.ADS"]
[uint32   size]
[type-specific payload — usually starts with tag "VER:", "PAG:", etc.]
```

Resource dispatch by filename extension → parser:

| Ext | Parser | Output struct | Compression | Global array | Max |
|---|---|---|---|---|---|
| `.ADS` | parseAdsResource | `TAdsResource` | LZW (2) or RLE (1) | `adsResources[100]` | 100 |
| `.BMP` | parseBmpResource | `TBmpResource` | LZW or RLE | `bmpResources[200]` | 200 |
| `.SCR` | parseScrResource | `TScrResource` | LZW or RLE | `scrResources[20]` | 20 |
| `.TTM` | parseTtmResource | `TTtmResource` | LZW or RLE | `ttmResources[100]` | 100 |
| `.PAL` | parsePalResource | `TPalResource` | none | `palResources[1]` | 1 |
| `.VIN` | (skipped) | — | — | — | — |

**Tag markers inside payloads** (4-byte ASCII): `VER:` (version string), `ADS:` / `TT3:` (bytecode), `RES:` / `PAG:` (metadata), `SCR:` (data blob w/ compression header), `TAG:` (tag table), `TTI:` (TTM tag info), `BMP:` (bitmap header), `INF:` (widths/heights table), `BIN:` (nibble pixel data), `PAL:` / `VGA:` (palette).

**Compression dispatch** (`uncompress.c:123-136`):

```c
uint8 *uncompress(FILE *f, uint8 method, uint32 inSize, uint32 outSize)
  method == 1 → RLE
  method == 2 → LZW 9..12-bit
  else      → fatal
```

| Method | Details |
|---|---|
| RLE (1) | Control byte: bit7=1 → `[10xxxxxx][value]` repeat (ctrl & 0x7F) times; bit7=0 → `[0xxxxxxx]` followed by `ctrl` literal bytes. |
| LZW (2) | Variable 9..12-bit codes; code 256 resets dictionary (back to 9-bit); dict max 4096 entries; 4096-byte decode stack. Byte alignment on reset. |

**TBmpResource** (`resource.h`):
```c
struct TBmpResource {
    char     resName[14];
    uint16   width, height;                  // max of any sub-image
    uint16   numImages;
    uint16   *widths, *heights;              // per sub-image
    uint32   uncompressedSize;
    uint8    *uncompressedData;              // 4-bit nibbles, 2 pixels/byte
};
```
Per-image offsets implicit; decoder walks sequentially sized `widths[i]*heights[i]/2` bytes.

**TScrResource:** background image, 640×480 typical, same nibble encoding.

**TAdsResource / TTtmResource:** carry bytecode in `uncompressedData` + tag table (`TTags[]` → `TTtmTag { uint16 id; uint32 offset; }`).

---

# @ADS_VM

Scene-level scheduler. High-level: decides which TTM scenes to spawn, in what order, under what conditions. Called from `storyPlay` via `adsPlay(name, tag)`. Bytecode stream of uint16 opcodes with uint16 args.

**Opcode table** (`ads.c:118-191`, `dump.c:325-343`):

| Opcode | Mnemonic | nArgs | Purpose |
|---|---|---|---|
| `0x1070` | IF_LASTPLAYED_LOCAL | 2 | Conditional: played locally (rare; ACTIVITY.ADS only) |
| `0x1330` | IF_UNKNOWN_1 | 2 | Synonym of IF_NOT_RUNNING (unused mostly) |
| `0x1350` | IF_LASTPLAYED | 2 | Condition: (slot, tag) was the last scene executed |
| `0x1360` | IF_NOT_RUNNING | 2 | Condition: (slot, tag) is NOT currently animating |
| `0x1370` | IF_IS_RUNNING | 2 | Condition: (slot, tag) IS currently animating |
| `0x1420` | AND | 0 | Combines preceding conditions |
| `0x1430` | OR | 0 | Alternate branch for conditions |
| `0x1510` | PLAY_SCENE | 0 | Terminates conditional block; if true, execute following ADD/STOP |
| `0x1520` | ADD_SCENE_LOCAL | 5 | Local variant of ADD_SCENE (slot, tag, iter, unk, unk) |
| `0x2005` | ADD_SCENE | 4 | Spawn TTM scene: (slot, tag, numPlays, weight) — weight used inside RANDOM block |
| `0x2010` | STOP_SCENE | 3 | Halt running TTM: (slot, tag, weight-if-random) |
| `0x2014` | UNKNOWN_5 | 0 | Parsed, no-op |
| `0x3010` | RANDOM_START | 0 | Begin weighted-random choice block |
| `0x3020` | NOP | 1 | Placeholder inside RANDOM (weighted skip) |
| `0x30ff` | RANDOM_END | 0 | Resolve random block: pick one op by weight |
| `0x4000` | UNKNOWN_6 | 3 | BUILDING.ADS tag 7 only |
| `0xf010` | FADE_OUT | 0 | Visual fade (not implemented) |
| `0xf200` | GOSUB_TAG | 1 | Call subroutine at tag; returns (no real stack, effectively 1-level) |
| `0xfff0` | END_IF | 0 | End conditional block |
| `0xffff` | END | 0 | Script termination |
| other | `:TAG N` | 0 | Label at current offset; stored in tag table |

Args are uint16. ADS does not use string args (TTM does).

**Scene thread state:** `TTtmThread` (`graphics.h:61-76`):
```c
struct TTtmThread {
    struct TTtmSlot *ttmSlot;   // TTM bytecode + sprite slots
    TtmRunState isRunning;      // TTM_FREE (0) | TTM_RUNNING (1) | TTM_ENDING (2, transient) | TTM_STATIC_LAYER (3, non-bytecode — bg/clouds/holiday only). See graphics.h for the enum.
    uint16 sceneSlot;           // slot index
    uint16 sceneTag;            // entry tag
    short  sceneTimer;          // neg=timed; pos=iteration count
    uint16 sceneIterations;
    uint32 ip;                  // bytecode instruction pointer
    uint16 delay;               // frame delay in ticks (20ms units)
    uint16 timer;               // countdown to next execute
    uint32 nextGotoOffset;
    uint8  selectedBmpSlot;     // for LOAD_IMAGE / DRAW_SPRITE
    uint8  fgColor, bgColor;    // palette indices 0..15
    PlatformSurface *ttmLayer;  // per-scene compositing layer (grRenderWidth × grRenderHeight, magenta-keyed)
};
```

`MAX_TTM_THREADS = 10`, `MAX_TTM_SLOTS = 10`, `MAX_BMP_SLOTS = 6`, `MAX_SPRITES_PER_BMP = 120`.

---

# @TTM_VM

Animation/drawing VM. One VM per active `TTtmThread`; executes per-frame opcodes against its private `ttmLayer`.

**Opcode encoding:** uint16 opcode; bottom nibble = arg-count spec:
- `0x0..0xE` (0-14) → that many uint16 args
- `0xF` (15) → one null-terminated ASCII string, padded to even bytes

**Opcode table** (`ttm.c:124-207`, `dump.c:394-502`):

| Opcode | Mnemonic | Args | Semantics |
|---|---|---|---|
| `0x0080` | DRAW_BACKGROUND | 0 | Reset/refresh background layer; free BMP slots |
| `0x0110` | PURGE | 0 | Scene finished: loop if `sceneTimer != 0`, else transition isRunning → `TTM_ENDING` (resolved same frame) |
| `0x0FF0` | UPDATE | 0 | End of frame — yield control to scheduler |
| `0x1021` | SET_DELAY | 1 | Set frame delay (in **20ms ticks**, NOT ms). `delay = max(arg0, 4)` → **80ms floor = 12.5 FPS ceiling** for any TTM scene. Flow: `ttmThread.delay/timer → adsPlay mini → grUpdateDelay → eventsWaitTick(ticks) → delay *= 20` (events.c:119). Confirmed 2026-04-20. |
| `0x1051` | SET_BMP_SLOT | 1 | Select active BMP slot (0..5) |
| `0x1061` | SET_PALETTE_SLOT | 1 | (unused in current impl) |
| `0x1101` | `:LOCAL_TAG N` | 1 | Local tag marker |
| `0x1111` | `:TAG N` | 1 | Global entry tag marker |
| `0x1121` | TTM_UNKNOWN_1 | 1 | Region ID hint for SAVE_IMAGE1 (not used) |
| `0x1201` | GOTO_TAG | 1 | Set `nextGotoOffset` to tag's offset; next UPDATE jumps there |
| `0x2002` | SET_COLORS | 2 | `fgColor = arg0; bgColor = arg1` (0..15) |
| `0x2012` | SET_FRAME1 | 2 | Frame bounds (args always 0,0; unused) |
| `0x2022` | TIMER | 2 | `delay = (arg0 + arg1) / 2` |
| `0x4004` | SET_CLIP_ZONE | 4 | Define clip rect (x1,y1,x2,y2) |
| `0x4204` | COPY_ZONE_TO_BG | 4 | Persist zone into background layer |
| `0x4214` | SAVE_IMAGE1 | 4 | Dirty-rect hint (not used) |
| `0xA002` | DRAW_PIXEL | 2 | Pixel at (x,y) with fgColor |
| `0xA054` | SAVE_ZONE | 4 | Save zone to `grSavedZonesLayer` |
| `0xA064` | RESTORE_ZONE | 4 | Restore saved zone; release layer when empty |
| `0xA0A4` | DRAW_LINE | 4 | Bresenham's line |
| `0xA104` | DRAW_RECT | 4 | Filled rect |
| `0xA404` | DRAW_CIRCLE | 4 | Bresenham's circle/ellipse |
| `0xA504` | DRAW_SPRITE | 4 | Blit `(slot, imgIdx, x, y)` |
| `0xA524` | DRAW_SPRITE_FLIP | 4 | Horizontally flipped blit |
| `0xA601` | CLEAR_SCREEN | 1 | Fill layer with magenta color-key |
| `0xB606` | DRAW_SCREEN | 6 | (unused) |
| `0xC051` | PLAY_SAMPLE | 1 | `soundPlay(arg0)` — sample 0..24 |
| `0xF01F` | LOAD_SCREEN | str | `grLoadScreen(strArg)` → SCR resource |
| `0xF02F` | LOAD_IMAGE | str | `grLoadBmp(slot, strArg)` → BMP resource |
| `0xF05F` | LOAD_PALETTE | str | Load PAL (currently unused) |

**Coordinates:** logical 640×480; offset by globals `grDx, grDy` (applied by drawing primitives). HD scaling applied separately (see @GRAPHICS).

---

# @GRAPHICS

**Palette model** (`graphics.c:42-131`):
- One 16-entry palette: `static uint8 ttmPalette[16][4]` — BGRA rows. (First 16 colors of the 256-entry PAL resource.)
- PAL data: 6-byte header, then 256 `{R,G,B}` 6-bit entries. Conversion: `ttmPalette[i][0/1/2] = palResource->colors[i].{b,g,r} << 2`, `[3]=255`.
- Magenta transparency key: `(r=0xA8, g=0x00, b=0xA8)` → treated transparent in sprite blits and HD PNG back-compat.

**Surfaces & compositing:**
- `grBackgroundSfc` — allocated at render-size (`grRenderWidth × grRenderHeight`), holds island + SCR background or HD PNG.
- `grSavedZonesLayer` — transient, lifecycle tied to SAVE_ZONE / RESTORE_ZONE opcodes.
- `ttmThread.ttmLayer` — per-thread compositing layer, magenta-keyed for transparency.

**HD / scale (`graphics.c:54-183`):**
- Globals: `int grScale = 1`, `int grRenderWidth = SCREEN_WIDTH (640)`, `int grRenderHeight = SCREEN_HEIGHT (480)`, `int grHdEnabled = 0`.
- `grDetectHDAssets()` (called by `graphicsInit`): reads `data/hd/manifest.json` from zipvfs; scans for `"scale": <int>`; if `1 < scale ≤ 8` → `grScale = scale; grHdEnabled = 1; grRenderWidth = 640*scale; grRenderHeight = 480*scale`.
- Window created at `grRenderWidth × grRenderHeight`; logical coordinate system stays 640×480.
- Every `grPutPixel(x,y)` writes a `grScale × grScale` block at `(x*grScale, y*grScale)` — nearest-neighbor upscale for all legacy opcodes.
- Per-opcode effect: line/rect/circle all go through `grPutPixel`, so they scale implicitly.

---

# @HD_ASSET_OVERRIDE

**Gate:** `data/hd/manifest.json` must exist inside `scrantic_data.zip` with `"scale": <int>` (2..8).

**SCR override** (`graphics.c:649-664`, in `grLoadScreen`):
```
if (grHdEnabled):
    path = "data/hd/SCR/<scrResource.resName>.png"   # e.g. "data/hd/SCR/OCEAN00.SCR.png"
    if zipvfs_read(path) returns data:
        pngSfc = platformLoadPNGFromMemory(data, size)
        if pngSfc != NULL:
            grBackgroundSfc = pngSfc           # done — no nibble decode
            return
# fall through to built-in nibble decode + grScale upscale
```

**BMP override** (`graphics.c:791-...`, in `grLoadBmp`, per image):
```
if (grHdEnabled):
    path = "data/hd/BMP/<bmpResource.resName>/<NNN>.png"   # 3-digit zero-padded, e.g. "data/hd/BMP/MJJOG2.BMP/000.png"
    if zipvfs_read returns data:
        pngSfc = platformLoadPNGFromMemory(...)
        if pngSfc != NULL:
            # Back-compat: if pixel is (0xA8, 0x00, 0xA8) + alpha=255, rewrite alpha=0
            # (supports old HD packs that used magenta-key instead of PNG alpha)
            for each pixel: if RGB==A8-00-A8 && A==255: A=0
            use as sprite
            continue
# fall through to built-in BMP decode
```

**Path conventions summary:**
| Asset type | Path inside `scrantic_data.zip` | Example |
|---|---|---|
| Manifest | `data/hd/manifest.json` | — |
| Screen | `data/hd/SCR/<NAME>.png` | `data/hd/SCR/OCEAN00.SCR.png` |
| Sprite image | `data/hd/BMP/<NAME>/<NNN>.png` | `data/hd/BMP/MJJOG2.BMP/000.png` |

**Alpha semantics:**
- Sprites: real per-pixel alpha preferred. Legacy magenta fallback auto-applied at load time.
- Screens: treated as opaque backgrounds (alpha ignored).

**Platform support** (as of 2026-04-20): PNG decode now works on ALL four targets. Windows uses WIC (`png_loader.c`), the others use the vendored minimal PNG decoder (`png_decoder.c`) backed by miniz for zlib inflate. Supported PNG formats: 8-bit RGB, 8-bit RGBA, 8-bit grayscale+alpha, non-interlaced. Unsupported formats (16-bit depth, paletted, Adam7 interlaced) return NULL → engine falls back to legacy RESOURCE.001 decode + `grScale` upscale for that specific asset (per-asset graceful degradation).

**HD_README.txt** was rewritten 2026-04-20 to reflect that HD assets live inside `scrantic_data.zip` (read via `zipvfs_read`), not on an on-disk `data/hd/` folder as the previous README claimed.

---

# @SOUND

**Model:** 25 pre-loaded WAV samples (`sound0..sound24.wav`), single-voice playback.

**Loader** (`sound.c`):
```c
static struct TSound { uint32 length; uint8 *data; } sounds[NUM_OF_SOUNDS];  // 25
```
- `soundInit()`: iterate paths `data/sound%d.wav` via zipvfs, call `platformLoadWAVFromMemory()`; on failure, log and continue (sets no global disable).
- Global `soundDisabled` (CLI `nosound`) suppresses playback only.

**Playback:** `soundPlay(int nb)` → `platformLockAudio()` sets `currentPtr = sounds[nb].data; currentRemaining = sounds[nb].length` → `platformUnlockAudio()`.

**Audio callback:** copies `currentPtr` to stream, fills remainder with silence byte `127`. No mixing — new sample replaces previous mid-playback.

**TTM integration:** `PLAY_SAMPLE` opcode (`0xC051`, arg in 0..24) triggers `soundPlay()`.

**Extraction:** `tools/extract_sound.c` pulls 24 hard-coded byte offsets out of `SCRANTIC.SCR` and writes `sound1..sound24.wav` (see @TOOLS).

---

# @ISLAND_SCENE_LOGIC

**Island state** (`island.h`): `static struct TIslandState islandState` = `{ lowTide, night, raft, holiday, xPos, yPos }`.
- `night`: 0 = OCEAN0[0-2].SCR (random), 1 = NIGHT.SCR.
- `raft`: 0..5 construction stage (story-day-driven).
- `holiday`: 0=none, 1=Halloween, 2=StPatrick, 3=Christmas, 4=NewYear.
- `lowTide`: affects wave + rock sprite set, raft Y offset.
- `xPos` ∈ [-272, 0], `yPos` ∈ [-73, 85] — controlled by scene flags.

**Calendar calendar** (`story.c`):
| Holiday | Date range |
|---|---|
| Halloween | 10-28 .. 10-31 |
| St Patrick's | 03-14 .. 03-18 |
| Christmas | 12-22 .. 12-26 |
| New Year | 12-28 .. 01-02 |

**Story progression:** days 1..11 (day 0 unused); raft stage advances with day (1-2→stage 1, 3-5→stages 2-4, 6+→stage 5). System-date changes (via `getDayOfYear()` compared to `config.date` in `~/.jc_reborn`) trigger `currentDay++`. Persisted via `cfgFileRead` / `cfgFileWrite` (`config.c:37-89`).

**Island drawing** (`island.c:32-133, islandInit`):
- Blit OCEAN0*.SCR or NIGHT.SCR to `grBackgroundSfc`.
- Draw raft sprite `MRAFT.BMP[stage]` at `(512, 266)` or `(529, 281)` if lowTide.
- Spawn 0–5 clouds from `BACKGRND.BMP` sprites 15–17 (random size/pos/direction) → `ttmCloudsThread`.
- Draw main island `BACKGRND.BMP[0]`, trunk `[13]`, leaves `[12]`, shadow `[14]`.
- If lowTide: add shore sprite `[1]` + rock `[2]`.
- Init wave animation counters.

**Wave animation** (`island.c:136-174, islandAnimate`) — timer 8..12 ticks:
- Dual counters (`counter1`, `counter2`) cycle sprite frames.
- High tide: 3 sprites per position × 3 positions (left/center/right) → sprites 3-5, 6-8, 9-11.
- Low tide: 4 sprites per position × 3 positions → sprites 30-32, 33-35, 36-38; rock animates with 39-41.
- Blit coords fixed at screen Y=303..356, X range 270..558.

**Holiday overlay** (`island.c:176-199, islandInitHoliday`): dedicated `ttmHolidayThread` with `isRunning = TTM_STATIC_LAYER` (background/static, no bytecode). Blits a single sprite from `HOLIDAY.BMP`:
| Holiday | Sprite | Position |
|---|---|---|
| Halloween | 0 | (410, 298) |
| St Patrick's | 1 | (333, 286) |
| Christmas | 2 | (404, 267) |
| New Year | 3 | (361, 155) |

**Composition order:** background → saved zones → TTM layers → holiday layer → clouds layer.

---

# @WALK_AND_PATH

**`calcpath.c:59-131`** — DFS over a 6-node graph (spots A..F = 0..5), edges in `walkMatrix[6+1][6][6]` (reachability with direction bits). Returns a random valid path.

**`walk.c:25-114, walk_data.h`** — pre-computed animation keyframes extracted from `SCRANTIC.SCR` at ROM offset `0x188EA..0x19456` via `tools/extract_walk_data.c`. Each keyframe: `uint16[4] = { flipped, spriteX, spriteY, spriteNo }`. Terminator `{0,0,0,0}`. Bookmarks (`walk_data_Bookmarks`, `walk_data_BookmarksTurns`) index segments:
- Phase 1: turn from `currentHdg` to heading-needed-to-reach-next-spot.
- Phase 2: walk frames until segment terminator.
- Phase 3: at `finalSpot`, "hands in pockets" idle (9 frames).

**`adsPlayWalk(fromSpot, fromHdg, toSpot, toHdg)`** (`ads.c:912-960`):
```
adsAddScene(0, 0, 0)                      # allocate ttmThreads[0]
grLoadBmp(ttmSlots, 0, "JOHNWALK.BMP")
grDx = islandState.xPos; grDy = islandState.yPos
walkInit(fromSpot, fromHdg, toSpot, toHdg)
ttmThreads[0].delay = walkAnimate(...)
while ttmThreads[0].delay != 0:
    if ttmBackgroundThread.timer == 0: islandAnimate; reset timer
    if ttmThreads[0].timer == 0: ttmThreads[0].delay = walkAnimate(...); reset timer
    grUpdateDisplay(...)
    mini = min(background.timer, thread0.timer)
    decrement both; eventsWaitTick(mini)
adsStopScene(0)
```

---

# @SCENE_DATABASE

`story_data.h` — 63 `TStoryScene` entries:
```c
struct TStoryScene {
    char adsName[13];   // e.g. "ACTIVITY.ADS"
    int  adsTagNo;      // tag within ADS
    int  spotStart;     // A-F (arrival spot)
    int  hdgStart;      // 0..7 compass (N..NW-ish)
    int  spotEnd;       // exit spot (0 if scene doesn't trigger walk)
    int  hdgEnd;
    int  dayNo;         // 0 = any day; 1..11 = specific story day
    int  flags;         // bitmask
};
```

**Scene flags:**
| Flag | Meaning |
|---|---|
| FIRST | First scene of a pass |
| FINAL | Terminal scene |
| ISLAND | Requires island render |
| LEFT_ISLAND | Render island shifted 272px left |
| VARPOS_OK | Allow random xPos/yPos within band |
| LOWTIDE_OK | Compatible with low tide |
| NORAFT | Incompatible with raft-present state |
| HOLIDAY_NOK | Skip during holiday mode |

`storyPickScene(wantedFlags, unwantedFlags)` filters and picks uniformly at random among matches.

---

# @GLOBAL_STATE_REFERENCE

| File | Symbol | Type | Purpose |
|---|---|---|---|
| `jc_reborn.c:51-57` | `argDump`, `argBench`, `argTtm`, `argAds`, `argPlayAll`, `argIsland`, `argMinimize` | static int | CLI mode flags |
| `graphics.c:49-58` | `grDx, grDy, grWindowed, grUpdateDelay, grScale, grRenderWidth, grRenderHeight, grHdEnabled` | int | render state |
| `graphics.c` | `ttmPalette[16][4]` | static uint8[][] | active 16-color palette |
| `graphics.c` | `grBackgroundSfc, grSavedZonesLayer` | PlatformSurface* | compositing layers |
| `events.c` | `lastTicks, paused, maxSpeed, oneFrame, evHotKeysEnabled` | static + extern int | event/timing state |
| `sound.c` | `sounds[25], currentPtr, currentRemaining, soundDisabled` | static + extern | audio state |
| `ads.c` | `ttmSlots[10], ttmThreads[10], ttmBackgroundThread, ttmHolidayThread, ttmCloudsThread, adsChunks[], ttmDx, ttmDy` | static/extern | scene state |
| `island.h` | `islandState` | extern struct | island configuration |
| `story.c` | `storyCurrentDay, storyForcedHoliday` | static int | story progression |
| `resource.c` | `adsResources[100], bmpResources[200], scrResources[20], ttmResources[100], palResources[1]` | globals | resource index |
| `config.c` | `struct TConfig { int currentDay; int date; }` | persisted to `~/.jc_reborn` | calendar-progression |
| `utils.c` | `debugMode` | extern int | debug printing gate |

---

# @FILE_MAP

**Engine core:**
| File | LOC | Role |
|---|---|---|
| `jc_reborn.c` | ~450 | `main`, CLI parsing, mode dispatch, zipvfs init |
| `config.c/h` | ~100 | `~/.jc_reborn` calendar persistence |
| `events.c/h` | ~90 | Frame-tick timing, input hotkeys, pause/maxSpeed |
| `bench.c/h` | ~50 | FPS benchmark harness (1/4/8 layers × 3s) |
| `story.c/h`, `story_data.h` | 63 scenes + logic | Scene selection, calendar, holidays, island config |
| `walk.c/h`, `walk_data.h` | ~120 | Johnny's inter-scene walking state machine |
| `calcpath.c/h`, `calcpath_data.h` | ~130 | Path DFS over spot graph |
| `island.c/h` | ~200 | Island drawing, wave animation, holiday overlay |
| `mytypes.h` | — | `uint8..sint32` typedefs |
| `utils.c/h` | ~150 | fatalError, debugMsg, safe_malloc, readUint16, etc. |

**Script VMs + assets:**
| File | LOC | Role |
|---|---|---|
| `ads.c/h` | ~900 | ADS VM, `adsPlay`, `adsPlayWalk`, `adsInitIsland`, `adsPlayBench`, `adsPlaySingleTtm` |
| `ttm.c/h` | ~350 | TTM VM, `ttmPlay`, `ttmLoadTtm`, `ttmFindTag` |
| `dump.c/h` | ~500 | `dumpAllResources` — emits ADS/TTM disassembly + BMP/SCR as XPM |

**Graphics & IO:**
| File | LOC | Role |
|---|---|---|
| `graphics.c/h` | ~1200 | Rendering primitives, SCR/BMP loading, HD manifest detection, PNG override hook, fade |
| `png_loader.c` | ~160 | Windows WIC decoder; non-Windows branch delegates to `png_decoder.c` |
| `png_decoder.c / .h` | ~250 | Minimal PNG decoder (8-bit RGB/RGBA/GA, non-interlaced) using miniz for inflate; shared by macOS/Linux/Web |
| `sound.c/h` | ~160 | Sample playback |
| `resource.c/h` | ~500 | RESOURCE.MAP/001 parsing, per-type decoders |
| `uncompress.c/h` | ~160 | RLE + LZW decoders |
| `zipvfs.c/h` | 134 + 50 | miniz wrapper (fopen/read/exists/shutdown) |

**Platform:**
| File | LOC | Role |
|---|---|---|
| `platform.h` | 162 | Abstraction interface |
| `platform_linux.c` | ~700 | X11 + ALSA |
| `platform_macos.m` | ~600 | Cocoa + AudioToolbox (Objective-C) |
| `platform_windows.c` | ~1050 | Win32 + WinMM + (indirectly via png_loader) WIC |
| `platform_web.c` | ~600 | Emscripten + HTML5 Canvas + Web Audio |

**Vendored:**
| File | Role |
|---|---|
| `miniz.c/h`, `miniz_common.h`, `miniz_export.h`, `miniz_tdef.c/h`, `miniz_tinfl.c/h`, `miniz_zip.c/h` | miniz single-source zip/deflate implementation |

**Data (not source):**
| File | Role |
|---|---|
| `scrantic_data.zip` | ~3.9 MB — bundled RESOURCE.MAP/001 + extracted sounds + optional HD PNG pack |
| `favicon.ico` | Web build favicon |
| `LICENSE` | GPLv3 |
| `index.html` | Web entry point with canvas + audio resume shim for Chromium autoplay policy |

---

# @TOOLS

**`tools/extract_sound.c`** — compile: `gcc extract_sound.c ../utils.c -o extract_sound`. Reads `../data/SCRANTIC.SCR`, pulls 24 WAV blobs from hard-coded offsets (0x1DC00..0x45A00 range) using `readUint16` size prefix + 8-byte header pad, writes `../data/sound1..sound24.wav`. Run via `tools/Makefile.sound`.

**`tools/extract_walk_data.c`** — compile: `gcc extract_walk_data.c -o extract_walk_data`. Reads `../data/SCRANTIC.SCR` from offset `0x188EA` to `0x19456`; each record is 3× uint16 (little-endian); format `{ flipped, x, y, spriteNo }`. Prints C initializer rows to stdout — output was hand-pasted into `walk_data.h`.

**`misc/adsbeautifier.awk`** — small AWK script for prettifying ADS dump output.

**Built-in `jc_reborn dump`** — runs without graphics; creates `dump/{ADS,BMP,SCR,TTM}/` subtrees:
- `dump/BMP/<NAME>.<NNN>.xpm` — one XPM per sub-image (16-color palette, hex nibble pairs)
- `dump/SCR/<NAME>.xpm`
- `dump/ADS/<NAME>.txt` — disassembly w/ resources + tags tables + op stream
- `dump/TTM/<NAME>.txt` — disassembly w/ tag table + op stream

---

# @DATA_FLOW_DIAGRAM

```
scrantic_data.zip
  │
  ▼
zipvfs_init()
  │
  ├─► parseResourceFiles("data/RESOURCE.MAP")
  │     │
  │     ├─► parseMapFile()                [index]
  │     └─► parseResourceFile()           [RESOURCE.001 entries]
  │           └─► uncompress() (RLE|LZW)
  │           ├─► parseAdsResource() → adsResources[]
  │           ├─► parseBmpResource() → bmpResources[]
  │           ├─► parseScrResource() → scrResources[]
  │           ├─► parseTtmResource() → ttmResources[]
  │           └─► parsePalResource() → palResources[]
  │
  ├─► graphicsInit()
  │     ├─► platformInit()
  │     ├─► grDetectHDAssets()            [reads data/hd/manifest.json]
  │     ├─► platformCreateWindow(grRenderWidth, grRenderHeight)
  │     ├─► grLoadPalette(palResources[0])
  │     └─► eventsInit()
  │
  ├─► soundInit()  [data/sound1..24.wav via zipvfs]
  │
  └─► storyPlay()
        ├─► storyUpdateCurrentDay() + storyCalculateIslandFromDateAndTime()
        ├─► finalScene = storyPickScene(FINAL)
        ├─► adsInitIsland()
        │     ├─► ttmBackgroundThread ← island SCR + sprites
        │     ├─► ttmHolidayThread (if holiday)
        │     └─► ttmCloudsThread (0..5 clouds)
        ├─► loop 6..19 × scenes:
        │     ├─► adsPlayWalk(prev→scene)
        │     └─► adsPlay(scene.adsName, scene.adsTagNo)
        │           │
        │           └─► per frame (20ms ticks):
        │                 ├─► islandAnimate (waves) every 8..12 ticks
        │                 ├─► ttmPlay(thread) per active ttmThread
        │                 │     └─► opcode dispatch:
        │                 │           ├─► LOAD_IMAGE → grLoadBmp()
        │                 │           │         └─► HD: zipvfs_read(data/hd/BMP/<name>/NNN.png)
        │                 │           │                → platformLoadPNGFromMemory()
        │                 │           │                (fallback: nibble decode × grScale upscale)
        │                 │           ├─► LOAD_SCREEN → grLoadScreen()
        │                 │           │         └─► HD: zipvfs_read(data/hd/SCR/<name>.png)
        │                 │           ├─► DRAW_SPRITE / DRAW_{LINE,RECT,CIRCLE,PIXEL}
        │                 │           ├─► SAVE_ZONE / RESTORE_ZONE / COPY_ZONE_TO_BG
        │                 │           ├─► PLAY_SAMPLE → soundPlay()
        │                 │           └─► UPDATE → yield
        │                 ├─► grUpdateDisplay() → composite → platformUpdateWindow()
        │                 └─► eventsWaitTick(min timer) [sleep + poll events]
        ├─► adsPlay(finalScene)
        ├─► grFadeOut()
        └─► (infinite; exit via ESC/QUIT → graphicsEnd + exit(255))
```

---

# @KNOWN_ISSUES_AND_GOTCHAS

- ~~**HD PNG decode is Windows-only.**~~ **RESOLVED 2026-04-20** — `png_decoder.c` (miniz-backed) added; non-Windows branch of `png_loader.c` now decodes 8-bit RGB/RGBA/GA non-interlaced PNGs. Unsupported PNG variants still return NULL → per-asset graceful fallback.
- ~~**HD_README.txt vs. zipvfs.**~~ **RESOLVED 2026-04-20** — readme rewritten to reflect zip-based layout.
- ~~**`build_web.ps1` hardcodes paths.**~~ **RESOLVED 2026-04-20** — now reads `$env:EMSDK` and `$env:JCR_BUILD_DIR` with fallback to the legacy path and script-relative build dir. Falls back to legacy hardcoded path only if EMSDK env var unset AND legacy path exists.
- **Python `tmpfile()` quirk** (actually C): on Windows, `zipvfs_fopen` uses `_tempnam + fopen(..., "w+bTD")` to avoid admin-only `tmpfile()`.
- **Sound mixing is single-voice.** `soundPlay()` replaces the current sample immediately; no overlapping samples.
- **Palette uses only 16 of 256 colors.** The engine's art is authored for a 16-color palette.
- **No dirty-rectangle optimization** — full frame compositing every tick. `grScale > 4` can become CPU-bound on older hardware.
- ~~**Fixed `SET_DELAY` minimum = 4** (in 20ms tick units? or ms?)~~ **CONFIRMED 2026-04-20**: SET_DELAY arg is in **20ms ticks** (not ms). Floor of 4 gives an **80ms floor = 12.5 FPS ceiling** per scene. This is intentional (prevents runaway frame rate) but means any TTM requesting delay<4 (intended >12.5 FPS) is silently clamped. Full chain: `ttm.c:214 ttmThread.delay = max(arg,4)` → `ads.c:812-829 grUpdateDelay = mini` → `graphics.c:306 eventsWaitTick(grUpdateDelay)` → `events.c:119 delay *= 20`.
- ~~**`isRunning` values observed:** 0/1/2/3~~ **CONFIRMED + REFACTORED 2026-04-20**: `int isRunning` replaced with `typedef enum { TTM_FREE=0, TTM_RUNNING=1, TTM_ENDING=2, TTM_STATIC_LAYER=3 } TtmRunState;` (defined in `graphics.h`). All 45+ call sites across `ads.c`, `ttm.c`, `island.c` updated to use named constants. Truthy checks (`if (thread.isRunning)`) preserved — any non-FREE state is "active" for compositing/tick purposes. Semantics: TTM_FREE = slot available, TTM_RUNNING = executing bytecode, TTM_ENDING = transient end-state (resolved same frame to RUNNING on iteration-restart or FREE via `adsStopScene` + `adsPlayTriggeredChunks`), TTM_STATIC_LAYER = used ONLY by `ttmBackgroundThread`/`ttmHolidayThread`/`ttmCloudsThread` — composited but never bytecode-executed.
- **Web audio autoplay policy** — `index.html` installs a click/keydown handler that calls `window.audioContext.resume()`; removes itself once `state === 'running'`.
- ~~**Emscripten `--embed-file` bakes `scrantic_data.zip` into the wasm.**~~ **RESOLVED 2026-04-20** — switched to `--preload-file` in CMakeLists.txt. Zip now ships as a separate `jc_reborn.data` file loaded async at startup; Emscripten waits for preload before calling `main()`, so engine code is unaffected. Web artifact tarball updated accordingly.
- **Web build executable suffix `.js`** — the resulting set is now `jc_reborn.js` + `jc_reborn.wasm` + `jc_reborn.data`, loaded by `index.html`.

---

# @QUICK_COMMAND_REFERENCE

```sh
# Native build (any of macOS / Linux / Windows local)
mkdir build && cd build && cmake .. && cmake --build .
./jc_reborn                              # play story (full screen)
./jc_reborn window                       # windowed
./jc_reborn nosound                      # silent
./jc_reborn island ads FISHING 3         # play FISHING.ADS tag 3 with island bg
./jc_reborn window ttm JOHNNY            # single TTM
./jc_reborn bench                        # FPS benchmark
./jc_reborn dump                         # resource dump to ./dump/
./jc_reborn debug hotkeys ads ACTIVITY 1 # with debug + ESC/SPACE/M/ALT+RET hotkeys
./jc_reborn christmas                    # force Christmas decorations
./jc_reborn holiday random               # random holiday once
./jc_reborn minimize                     # (Windows) start with console minimized

# Cross-compile to Windows (Linux/macOS host):
mkdir build-windows && cd build-windows && cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-mingw.cmake .. && cmake --build .

# Web build (Emscripten):
source /path/to/emsdk/emsdk_env.sh
mkdir build-web && cd build-web && emcmake cmake .. && cmake --build .
# Serve: python3 -m http.server 8000
# Open http://localhost:8000/jc_reborn.html   (or index.html)

# Hotkeys (in game, if `hotkeys` passed):
# ESC = quit | SPACE = pause | M = max speed | ALT+RET = toggle fullscreen | RET (paused) = step frame
```
