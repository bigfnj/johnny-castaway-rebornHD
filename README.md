# Johnny Reborn

Johnny Reborn is an open source engine for the classic Johnny Castaway screen saver, developed by Dynamix for Windows 3.x and published by Sierra, back in 1992.

It is written in C and has been refactored to use platform-native APIs instead of SDL2, providing better integration with each operating system.

## Supported Platforms

- **macOS**: Uses Cocoa for graphics and CoreAudio for sound
- **Linux**: Uses X11 for graphics and ALSA for sound  
- **Windows**: Uses Win32 API for graphics and WinMM (waveOut) for sound
- **Web**: Uses HTML5 Canvas and Web Audio API (via Emscripten)


## How to install

This fork loads all game data from a single zip archive, `scrantic_data.zip`,
which must live in the same directory as the executable (`jc_reborn` /
`jc_reborn.exe`). A ready-to-use `scrantic_data.zip` is provided under `assets/`.

The archive contains the original game data and the pre-extracted sound files:

    data/RESOURCE.MAP
    data/RESOURCE.001
    data/sound0.wav .. sound24.wav

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

# Create build directory
mkdir build-web
cd build-web

# Configure with Emscripten
emcmake cmake ..

# Build
cmake --build .

# Serve locally
python3 -m http.server 8000

# Open browser to http://localhost:8000/jc_reborn.html
```

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
```

### Holiday option

The `holiday` option controls seasonal decorations on the island. By default (`auto`), the engine reads the system date and activates the appropriate holiday during the following windows:

| Holiday       | Dates          |
|---------------|----------------|
| Halloween     | Oct 28 – Oct 31 |
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

## State persistence

The engine tracks story progress across runs in a small config file:

- **Linux / macOS:** `~/.jc_reborn`
- **Windows:** `%USERPROFILE%\.jc_reborn`

It stores the current in-story day (1–11) and the last-run calendar date. When a new calendar day is detected the story day advances automatically; after day 11 it loops back to 1. Delete the file to reset to day 1.


## Current status

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
