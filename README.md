# Johnny Reborn

Johnny Reborn is an open source engine for the classic Johnny Castaway screen saver, developed by Dynamix for Windows 3.x and published by Sierra, back in 1992.

It is written in C and has been refactored to use platform-native APIs instead of SDL2, providing better integration with each operating system.

## Supported Platforms

| Platform | Backend | Built in CI | Decoders verified | Rendering verified |
|---|---|---|---|---|
| **Windows** | Win32 + WinMM (waveOut) | yes | yes | yes, automated |
| **Linux** | X11 + ALSA | yes | yes | **no** |
| **Web** | HTML5 Canvas + Web Audio (Emscripten) | yes | yes | yes, automated |
| **macOS** | Cocoa + CoreAudio | yes | yes | yes, by eye (2026-09-14) |

All four build on every push, and all four produce decode output byte-identical
to the Windows golden corpus, 2,452 files.

**Rendering is the column to read carefully.** The cross-platform CI check runs
`dump`, which never opens a window, so it proves the decoders agree and says
nothing about drawing. Windows and Web have automated rendering assertions.
macOS was confirmed by building it on Sequoia and looking at the window: correct
orientation, correct colours. Linux has had neither, so its windowing and
blitting code compiles on every push and is never executed.

**Building on macOS:** use `tools/build-macos.sh`, which needs only the Xcode
Command Line Tools. Homebrew now refuses to install on Intel Macs, and CMake on
macOS usually arrives through Homebrew, so the script uses `clang` directly. CI
runs it on every push, so it stays working.

Audio and input on macOS were confirmed in the same session: the `AudioQueue`
path produces sound, Esc quits, and the close button exits cleanly. That last one
took a fix — the window had no delegate, so clicking the red button destroyed it
underneath the running engine and left the process suspended. Fullscreen there is
still unexercised. See `BACKLOG.md` for exactly what is and is not proven.


## How to install

This fork loads all game data from a single zip archive, `scrantic_data.zip`,
which must live in the same directory as the executable (`jc_reborn` /
`jc_reborn.exe`). A ready-to-use `scrantic_data.zip` is provided under `assets/`.

The archive contains the original game data and the pre-extracted sound files:

    data/RESOURCE.MAP
    data/RESOURCE.001
    data/sound0.wav .. sound24.wav   (23 files: 11 and 13 do not exist,
                                      and 0 ships but is never loaded)

It may also contain optional HD (PNG) replacement assets under `data/hd/`.
See `docs/HD_README.md` for the full zip layout and HD details.

The `tools/extract_sound` helper (built via `make -f Makefile.sound` in `tools/`)
can dump the audio files from the original `SCRANTIC.SCR`; the WAVs it produces
are already bundled inside `scrantic_data.zip`, so this step is only needed when
rebuilding the data archive from the original software.


## Building

### Prerequisites

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
```bash
# Install Emscripten SDK
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

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
# Make sure Emscripten is activated
source /path/to/emsdk/emsdk_env.sh

emcmake cmake -S . -B build_web -DCMAKE_BUILD_TYPE=Release
cmake --build build_web -j

# index.html and favicon.ico are SOURCES, not build output, and nothing in the
# build copies them. Without this step build_web/ is not servable.
cp index.html favicon.ico build_web/

cd build_web && python3 -m http.server 8000
# then open http://localhost:8000/
```

The build produces `jc_reborn.js`, `jc_reborn.wasm` and `jc_reborn.data`; the
page is `index.html`. (Earlier revisions of this README told you to open
`jc_reborn.html`, which this build has never produced, and used a `build-web`
directory that does not match the one `scripts/build_web.ps1` creates.)

No Emscripten install? The whole thing builds in a container:

```bash
docker run --rm -v "$PWD:/src" emscripten/emsdk:latest bash -c \
  'cd /src && emcmake cmake -S . -B build_web -DCMAKE_BUILD_TYPE=Release \
   && cmake --build build_web -j4 && cp index.html favicon.ico build_web/'
```

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
frames <n>             - stop cleanly after n frames, exit code 0
maxspeed               - run unthrottled from the start (as <M> does)
```

The last five are additive and off by default; shipping behaviour is unchanged.

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
click. It does **not** yet exit on losing focus: no Win32 focus message is
handled at all, which is a gap rather than a decision. In `/p` preview mode it
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

Where it stands as of 2026-09-12: version 0.9.0, a real Windows `.scr` with `/s`,
`/c` and `/p`, HD PNG assets on all four backends, real Web audio, and CI building
and testing Windows, Linux and Web on every push. macOS is the gap.

### Short version
Currently, Johnny reborn is in "work in progress" state. Every scene works with only some inaccuracies here and there.

That means that the engine globally works in an acceptable way, but more needs to be done to fully understand a number of details and faithfully reproduce the behaviour of the original engine.

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
