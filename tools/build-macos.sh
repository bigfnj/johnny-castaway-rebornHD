#!/usr/bin/env bash
#
#  Build jc_reborn on macOS with NOTHING but the Xcode Command Line Tools.
#
#  WHY THIS EXISTS. The normal path is CMake, and CMake on macOS normally arrives
#  via Homebrew - which as of 2026 refuses to install on Intel Macs at all:
#
#      Homebrew on macOS is only supported on Apple Silicon processors!
#
#  Every Mac with the Command Line Tools already has clang, so this remains
#  a build path without CMake or a package manager.
#
#  This mirrors exactly what CMakeLists.txt does for APPLE: the same sources, the
#  same four include directories, PLATFORM_MACOS, -x objective-c for the single
#  .m file, and the Cocoa + AudioToolbox frameworks. If the two ever drift, the
#  macOS CI job runs BOTH, so the drift is a build failure rather than a surprise
#  for whoever is trying to help.
#
#  Usage, from the repository root:
#      bash tools/build-macos.sh
#      ./jc_reborn window nosound hotkeys
#
set -euo pipefail

cd "$(dirname "$0")/.."

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This script is for macOS. On Linux or Windows use CMake:"
    echo "    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build"
    exit 1
fi

if ! command -v clang >/dev/null 2>&1; then
    echo "FAIL clang not found. Install the Command Line Tools first:"
    echo "    xcode-select --install"
    exit 1
fi

#  The version comes from CMakeLists.txt rather than being typed here, for the
#  same reason the .rc gets it from there: one source of truth. release.yml
#  refuses to publish when the git tag disagrees with that number, so anything
#  that hard-codes it somewhere else will eventually be wrong.
VERSION=$(sed -n 's/^project(jc_reborn VERSION \([0-9.]*\).*/\1/p' CMakeLists.txt)
[ -n "$VERSION" ] || { echo "FAIL could not read the version from CMakeLists.txt"; exit 1; }
echo "== jc_reborn $VERSION, clang $(clang --version | head -1 | sed 's/.*version //') =="

OUT=jc_reborn
rm -f "$OUT"

clang -O2 -o "$OUT" \
    -Isrc/engine -Isrc/data -Iplatform -Ithird_party/miniz \
    -DPLATFORM_MACOS -DJC_VERSION="\"$VERSION\"" \
    src/engine/*.c \
    platform/png_loader.c platform/png_decoder.c platform/zipvfs.c \
    third_party/miniz/*.c \
    -x objective-c platform/platform_macos.m \
    -framework Cocoa -framework AudioToolbox

[ -x "$OUT" ] || { echo "FAIL no binary produced"; exit 1; }

#  The archive must sit where the engine looks for it, which is the working
#  directory or beside the executable. Without this the build succeeds and the
#  program dies on startup, which is exactly how this project shipped for a
#  while and is a miserable first impression.
cp -f assets/scrantic_data.zip ./scrantic_data.zip

echo
echo "OK   built ./$OUT"
echo
echo "Run it windowed:"
echo "    ./$OUT window nosound hotkeys"
echo
echo "Esc quits. Rendering, colour, audio and input were checked by hand on"
echo "Sequoia on 2026-09-14. See BACKLOG.md for remaining platform checks."
