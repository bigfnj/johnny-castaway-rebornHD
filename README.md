# Johnny Reborn

Johnny Reborn is an open source engine for the classic Johnny Castaway screen saver, developed by Dynamix for Windows 3.x and published by Sierra, back in 1992.

It is written in C and has been refactored to use platform-native APIs instead of SDL2, providing better integration with each operating system.

## Supported Platforms

| Platform | Backend | Built in CI | Decoders verified | Rendering verified |
|---|---|---|---|---|
| **Windows** | Win32 + WinMM (waveOut) | yes | yes | yes, automated |
| **Linux** | X11 + ALSA | yes | yes | X11 resized-client pixels under Xvfb |
| **Web** | HTML5 Canvas + Web Audio (Emscripten) | yes | yes | yes, automated |
| **macOS** | Cocoa + AudioToolbox | yes | yes | yes, manual Sequoia review (2026-09-14) |

CI builds all four platforms on main pushes and pull requests. Windows, Linux
and macOS compare all 2,452 original-resource dumps against the golden corpus.
Web checks startup, rendering, responsiveness, audio scheduling and style controls
in Chromium. A headless dump verifies decoding without drawing a window.

Linux presentation tests inspect real X11 windows after resize; desktop
fullscreen negotiation and physical audio still need a desktop test. macOS
orientation, colors, audio, input, fullscreen and resize were reviewed manually
on Sequoia. Its automated backend probes cover allocation and event handling.
See [BACKLOG.md](BACKLOG.md) for remaining checks and [build validation](tests/BUILD_VALIDATION.md)
for the maintained test commands.

For a macOS build without CMake, use `bash tools/build-macos.sh` with the Xcode
Command Line Tools. CI exercises that direct-Clang path as well as CMake.


## How to install

This fork loads all game data from a single zip archive, `scrantic_data.zip`,
which must live in the same directory as the executable (`jc_reborn` /
`jc_reborn.exe`). A ready-to-use `scrantic_data.zip` is provided under `assets/`.

The archive contains the original game data and the pre-extracted sound files:

    data/RESOURCE.MAP
    data/RESOURCE.001
    data/sound0.wav .. sound24.wav   (23 files: 11 and 13 do not exist)

It may also contain optional HD (PNG) replacement assets under `data/hd/`.
See `docs/HD_README.md` for the full zip layout and HD details.

Normal playback uses the bundled WAVs and needs no extraction. CMake also builds
`extract_sound` and `extract_walk_data`, with explicit input/output arguments.
Both check I/O and preserve existing output files. The sound helper retains an
explicitly named historical layout whose length and numbering rules do not
recreate the supplied original's audio correctly. It safely refuses an
out-of-bounds span in that executable. Do not use it to rebuild the runtime ZIP;
see the [original extraction comparison](docs/knowledge-base/original-extractor-reference.md).
The walk helper has exact 489-record parity with the inspected original.


## Building

### Prerequisites

Native CMake builds require CMake 3.19 or newer. The test suites also use Python 3.
Linux platform tests require Xvfb and xauth in addition to the build libraries.

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install CMake (via Homebrew)
brew install cmake
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libx11-dev libasound2-dev
```

#### Windows
- Install Visual Studio 2019 or later with C++ support
- Install CMake from https://cmake.org/download/
- Or use MinGW-w64 with CMake

The CMake build works with any of those. The hand-maintained solution under
`vs/` is a separate thing and pins the **v145** toolset, which needs Visual
Studio 2026 - open it with anything older and it will not load. `cmake -S . -B
build` is the supported path and is what CI and `gate.ps1` use.

#### Web (Emscripten)

Use Python 3 and Docker for the same pinned Emscripten 6.0.9 build as CI.
An existing local 6.0.9 SDK remains usable for direct `emcmake` builds.

### Build Instructions

#### macOS, Linux, Windows

```bash
# Create build directory
mkdir build
cd build

# Configure
cmake ..

# Build
cmake --build .

# Run
./jc_reborn
```

#### For Release builds (optimized):
```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
```

#### Web (Emscripten)

```bash
python3 tools/build_web.py
python3 -m http.server 8000 --directory build_web
# then open http://localhost:8000/
```

The wrapper compiles with the official SDK container pinned by digest, verifies
the actual compiler and preload archive, and copies the page assets. The output
contains `jc_reborn.js`, `jc_reborn.wasm`, `jc_reborn.data` and `index.html`.
On Windows, use `python` if that is the installed command name.

On Windows, `scripts/build_web.ps1 -Backend Container` uses this same builder.
`-Backend Local -Sdk <emsdk-directory>` activates an installed Emscripten 6.0.9
SDK in a child shell. `Auto` uses `EMSDK` when configured and otherwise selects
the container. `-OutputDirectory` or `JCR_BUILD_DIR` selects the destination;
relative wrapper paths retain their meaning relative to the invoking directory.
The caller's directory and environment remain unchanged. Use a fresh output
directory when changing backend; incompatible CMake caches are preserved and
reported rather than deleted.

**Options in the browser.** The page reads them from the query string, so
`index.html?args=window+nosound+seed+9+frames+400` passes `window nosound seed 9
frames 400` to the engine exactly as a command line would.

`tests/web-smoke.py` loads the built page in headless Chromium and checks that it
paints, that the tab stays responsive while the engine runs, and that audio is
actually scheduled. It runs in CI.

## Usage

By default, the engine runs full screen and plays the life of Johnny on his island, as the original did.

```
jc_reborn
jc_reborn help
jc_reborn version
jc_reborn dump
jc_reborn [<options>] bench
jc_reborn [<options>] ttm <TTM name>
jc_reborn [<options>] ads <ADS name> <ADS tag no>
```

### Available options

```
window                 - play in windowed mode
minimize               - start with the console window minimized (Windows)
nosound                - quiet mode
island                 - display the island as background for ADS play
debug                  - print some debug info on stdout
hotkeys                - enable hot keys
holiday <name>         - force holiday decorations (see below)
night                  - force the night backdrop (NIGHT.SCR)
day                    - force daytime, ignoring the clock
seed <n>               - fix the random seed, for reproducible runs
frames <n>             - stop cleanly after n frames (1..4294967295), exit code 0
style <id>             - select hd or cartoon for this run
setstyle <id>          - save the style and exit without advancing the story
capture <file.ppm>     - save the final composed frame on clean shutdown
maxspeed               - run unthrottled from the start (as <M> does)
```

Playback options apply only to the current run. `setstyle` explicitly saves a
preference for future runs.

`night` and `day` exist because the night backdrop is otherwise reachable only
between 21:00 and 05:59, so an entire rendering path with its own HD artwork
could not be looked at during the day without changing the system clock.

`seed`, `frames` and `maxspeed` are what make the engine testable. Every random
choice (scene selection, cloud count and placement, ocean backdrop, low tide,
path finding) comes off one stream seeded from the clock, and `storyPlay()` never
returns, so before these a test could only kill the process and guess whether it
had been healthy. Note that the story day persists to `~/.jc_reborn` and also
selects which scenes are eligible, so a fully reproducible run needs a fresh
profile as well as a fixed seed; `tests/Invoke-SmokeTests.ps1` points `HOME` at a
throwaway directory for exactly that reason.

### Art styles

HD is the default. `jc_reborn window style cartoon` selects Cartoon for one run;
`jc_reborn setstyle cartoon` saves it in the existing `.jc_reborn` profile while
retaining the story day and date. Use `setstyle hd` to restore the default.
Windows Screen Saver Settings opens the same choice through the `.scr` file's
Settings button (`/c`). A change takes effect the next time playback starts.

The browser's Art style selector remembers its choice in local storage and
reloads the scene. An explicit URL argument, such as
`?args=window+style+hd`, overrides that saved browser choice for the current run.

The bundled Cartoon preview contains 27 approved assets: twelve walking poses and
15 island layers, including one ocean and all nine high-tide shore-foam frames.
It is a partial style pack. Other animations and environment states use HD or
original artwork, so the full story can mix the two styles. The settings label
is "Cartoon (preview)" until wider artwork coverage is ready.

Cartoon assets live under `data/styles/cartoon/` inside `scrantic_data.zip`.
Selecting Cartoon with an older archive that lacks the pack reports a
missing-pack error. The [approved island](art/cartoon/island-pilot-v1/README.md)
and [Calm focus walking revision](art/cartoon/walk-pilot/calm-focus-runtime-v1/README.md)
record their exact scope. The [rear walking family](art/cartoon/walk-expansion-v1/README.md)
adds six poses; its final standing pose still uses HD artwork.
See [Cartoon art production](docs/cartoon-art.md) for
packaging, [image authoring lessons](docs/art-style-learnings.md) and
[the walking revision lessons](docs/art-style-learnings-calm-focus.md) before
creating the next style.

`capture` writes a PPM image of the final composed frame, for example:

```text
jc_reborn window nosound day seed 9 frames 400 style hd capture frame.ppm
```

It captures playback rather than resource-decoder output. Keep the same profile,
seed and frame limit when comparing styles.

### Holiday option

The `holiday` option controls seasonal decorations on the island. By default (`auto`), the engine reads the system date and activates the appropriate holiday during the following windows:

| Holiday       | Dates          |
|---------------|----------------|
| Halloween     | Oct 29 – Oct 31 |
| St. Patrick's | Mar 15 – Mar 17 |
| Christmas     | Dec 23 – Dec 25 |
| New Year      | Dec 29 – Jan 1  |

You can override the automatic detection by passing a name after `holiday`:

```
jc_reborn holiday halloween
jc_reborn holiday stpatricks
jc_reborn holiday christmas
jc_reborn holiday newyear
jc_reborn holiday random      # pick one at random on startup
jc_reborn holiday none        # disable decorations entirely
jc_reborn holiday auto        # use system date (default)
```

As a shorthand the holiday name can be given directly without the `holiday` keyword:

```
jc_reborn halloween
jc_reborn christmas
jc_reborn random
```

### While-playing hot-keys (if `hotkeys` is enabled)

```
Esc        - Terminate immediately
Alt+Return - Toggle full screen / windowed mode
Space      - Toggle pause / unpause
Return     - When paused, advance one frame
<M>        - Toggle max / normal speed
```

Without `hotkeys`, pressing any key terminates the screensaver (normal screensaver behaviour).

## Installing it as a Windows screensaver

The Windows build produces two binaries from the same sources: `jc_reborn.exe`,
a console program, and `jc_reborn.scr`, a real screensaver built
`/SUBSYSTEM:WINDOWS`. Only the second one can be selected in Settings.

```
copy build\Release\jc_reborn.scr      %WINDIR%\System32\
copy build\Release\scrantic_data.zip  %WINDIR%\System32\
```

Then pick **Johnny Reborn** in Settings → Personalisation → Lock screen →
Screen saver. (Right-clicking the `.scr` and choosing **Install** does the same
thing.)

**Copy the data archive too.** Windows launches a screensaver with `System32` as
the working directory, and the engine looks for `scrantic_data.zip` beside the
binary. Without it the screensaver starts and immediately reports that it cannot
find its data.

`jc_reborn.scr` implements the three switches Windows passes:

```
/s          - run full screen (what the screen saver actually does)
/c          - show the settings dialog
/p <hwnd>   - draw the preview inside the small monitor in the Settings dialog
/a          - password change on very old Windows; accepted and ignored, so the
              shell never sees an error
```

Mouse movement past an 8-pixel dead zone ends it, as does any key or a mouse
click. In `/s` mode it also exits when another application takes activation.
Ordinary windowed runs ignore that deactivation event. In `/p` preview mode it
draws as a child of the supplied window and never takes the foreground.

Because it is the same binary, every option above still works for debugging:

```
jc_reborn.scr /s window nosound frames 200
```

## State persistence

The engine tracks story progress across runs in a small config file:

- **Linux / macOS:** `~/.jc_reborn`
- **Windows:** `%USERPROFILE%\.jc_reborn`

It stores the current in-story day (1–11) and the last-run calendar date. When a new calendar day is detected the story day advances automatically; after day 11 it loops back to 1. Delete the file to reset to day 1.


## Current status

**`BACKLOG.md` is the state of record.** It lists the open items with their
reachability stated per item, and records findings that were investigated and
rejected, so they do not get raised twice. The two sections below describe engine
accuracy and are inherited from the upstream project; they predate the screensaver,
the HD assets, the test suite and CI, so read them as history rather than status.

Current delivery includes the Windows screensaver, HD and the approved partial
Cartoon style, four-platform CI, and the legacy cleanup documented in the backlog.
Original-engine behavior still needs investigation for the reachable unfinished
commands recorded in [the command review](docs/legacy-command-review.md).

### Short version
The port has all ADS and TTM resource names present in the supplied original,
and its story table schedules 63 entries. Complete branch, timing and visual
parity still require reference observation, especially for reachable unfinished
commands. The [knowledge base](docs/knowledge-base/README.md) records 176 public
guide observations, exact original-resource comparisons and the remaining
questions without treating catalog counts as proof of animation completeness.

### Long version

Some great work was already made by Hans Milling for "Johnny Castaway Open Source" (JCOS), back in 2015. This includes:
  - the parsing and decoding of all the data files
  - the understanding of many instructions which constitute TTM and ADS scripts

What Johnny Reborn brings is:
  - the understanding of nearly every TTM and ADS instruction, and their parameters
  - the algorithm for Johnny to transitionnaly walk from scene to scene was implemented. Accuracy is not bad though not perfect.
  - the same can be said about the algorithm which randomly chooses scenes to be played.
  - as well as the algorithm which draws the island at a random place, clouds, etc.
  - all the work was made by observing the behaviour of the original software and trying to reproduce it as accurately as possible. For a better result, a complete disassembly of the original exe may be necessary - but wasn't done to this point.


## Thanks

I never would have been able to write Johnny Reborn without, directly or indirectly, all the people listed below. Many thanks to them.

  - Hans Milling aka nivs1978, author of the JCOS project - my main source of info for my first lines of the Johnny Reborn code
    - https://github.com/nivs1978/Johnny-Castaway-Open-Source
    - http://nivs.dk/jc/
  - Alexandre Fontoura aka xesf, author of castaway project - similar to Johnny Reborn, but in Javascript
    - https://github.com/xesf/castaway
    - https://castaway.xesf.net/viewer/
  - The Sierra Chest website, which has a nice section about Johnny Castaway, with many screenshots and video captures. Those turned out to be quite helpful:
    - http://sierrachest.com/index.php?a=games&id=255&title=johnny-castaway

Hans Milling thanks a number of people for giving him (or helping him find) some info about the original engine. They should not be forgotten, and I thank them - indirectly - as well:

  - Jeff Tunnel - For helping getting in contact with some of the original developers
  - Kevin and Liam Ryan - Assisting with information about the resource files
  - Jaap - Helping in finding the format of the resource files
  - Gregori - Assisting with the Lempel-Ziv decompression
  - Guido - The author of the xBaK project that led to understanding the TTM and ADS commands.
