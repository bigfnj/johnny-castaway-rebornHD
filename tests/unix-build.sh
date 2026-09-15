#!/usr/bin/env bash
#
#  Build jc_reborn on Linux/macOS, run portable and backend smoke/regression,
#  then compare original-resource decoder output with the Windows corpus.
#
#  Intended to run inside a container, e.g.
#    docker run --rm -v <repo>:/src:ro ubuntu:24.04 bash /src/tests/unix-build.sh
#  or directly on a macOS runner, where the toolchain is already present.
#
#  WHY THIS IS WORTH DOING AT ALL. `dump` never calls graphicsInit and touches no
#  RNG, so it runs headless with no X server and decodes every BMP, SCR, ADS and
#  TTM resource in the archive. That makes the golden manifest generated on
#  Windows directly comparable here: any hash that differs is a real
#  cross-platform decode defect - endianness, struct packing, signed char,
#  undefined shifts - and not a rendering difference or a timing artefact.
#
#  Backend probes exercise real platform code separately from decode parity;
#  their device and presentation coverage is documented in platform-cleanup.md.
set -euo pipefail

SRC=${SRC:-/src}
WORK=${WORK:-/work}

#  Platform shims. Kept together and named, rather than scattered inline, so the
#  next person can see at a glance what actually differs between the two hosts.
case "$(uname -s)" in
    Darwin)
        OSNAME=macOS
        ncpu() { sysctl -n hw.ncpu; }
        sha256() { shasum -a 256 "$1" | cut -d' ' -f1; }
        ;;
    *)
        OSNAME=Linux
        ncpu() { nproc; }
        sha256() { sha256sum "$1" | cut -d' ' -f1; }
        ;;
esac

echo "== toolchain ($OSNAME) =="
if ! command -v cmake >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1 ||
    { [ "$OSNAME" = Linux ] && ! command -v xvfb-run >/dev/null 2>&1; }; then
    if [ "$OSNAME" = macOS ]; then
        # Every GitHub macOS runner ships cmake and the Xcode command line tools.
        # If it is missing we are somewhere unexpected, and guessing at a package
        # manager would hide that rather than report it.
        echo "FAIL cmake or python3 not found on a macOS host; install the build/test prerequisites"
        exit 1
    fi
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq build-essential cmake python3 libx11-dev libasound2-dev xvfb xauth >/dev/null
fi
cc --version | head -1
cmake --version | head -1

# Copy out of the read-only mount so the build cannot touch the repo, and so
# Windows build trees are not dragged into this configure.
rm -rf "$WORK"
mkdir -p "$WORK"
cp -r "$SRC"/. "$WORK"/
rm -rf "$WORK"/build "$WORK"/build-asan "$WORK"/build-unix "$WORK"/build-linux "$WORK"/.git
cd "$WORK"

echo
echo "== build =="
cmake -S . -B build-unix -DCMAKE_BUILD_TYPE=Release >/dev/null
if cmake --build build-unix -j"$(ncpu)" > /tmp/build.log 2>&1; then
    # No diagnostic matches is a successful, warning-free build.
    grep -E 'error|warning' /tmp/build.log || true
else
    build_status=$?
    cat /tmp/build.log
    echo "FAIL tests/unix-build.sh: CMake build failed (status $build_status; /tmp/build.log)"
    exit "$build_status"
fi

if ! [ -x build-unix/jc_reborn ]; then
    echo "FAIL no binary produced"
    exit 1
fi
echo "OK   built build-unix/jc_reborn"

echo
echo "== portable PNG smoke: soft alpha reaches the real decoder =="
"$WORK"/build-unix/jc_png_test

echo
echo "== RESOURCE decoder smoke =="
python3 "$WORK/tests/test_uncompress.py" --probe "$WORK/build-unix/jc_uncompress_test" --engine "$WORK/build-unix/jc_reborn" --phase smoke

echo
echo "== frame limits smoke =="
python3 "$WORK/tests/test_frame_limits.py" --exe "$WORK/build-unix/jc_reborn" --probe "$WORK/build-unix/jc_frame_test" --phase smoke

if [ "$OSNAME" = macOS ]; then
    PLATFORM_TEST="$WORK/tests/run_macos_platform.sh"
else
    PLATFORM_TEST="$WORK/tests/run_linux_platform.sh"
fi
echo
echo "== native platform smoke =="
SRC="$WORK" OUT="$WORK/build-unix/platform-tests" bash "$PLATFORM_TEST" --phase smoke

if [ "$OSNAME" = Linux ]; then
    echo
    echo "== drawing and packed-screen smoke =="
    python3 "$WORK/tests/test_drawing_bounds.py" --output "$WORK/build-unix/drawing-tests" --phase smoke
fi

echo
echo "== RESOURCE decoder regression =="
python3 "$WORK/tests/test_uncompress.py" --probe "$WORK/build-unix/jc_uncompress_test" --engine "$WORK/build-unix/jc_reborn"

echo
echo "== frame limits regression =="
python3 "$WORK/tests/test_frame_limits.py" --exe "$WORK/build-unix/jc_reborn" --probe "$WORK/build-unix/jc_frame_test" --phase regression

echo
echo "== native platform regression =="
SRC="$WORK" OUT="$WORK/build-unix/platform-tests" bash "$PLATFORM_TEST" --phase regression

if [ "$OSNAME" = Linux ]; then
    echo
    echo "== required graphics-surface failure regression =="
    python3 "$WORK/tests/test_graphics_alloc.py" --output "$WORK/build-unix/graphics-tests"

    echo
    echo "== drawing and packed-screen regression =="
    python3 "$WORK/tests/test_drawing_bounds.py" --output "$WORK/build-unix/drawing-tests" --phase regression
fi

echo
echo "== dump, headless, no window server =="
RUN=/tmp/jcr-run
rm -rf "$RUN"; mkdir -p "$RUN"; cd "$RUN"
# No zip here on purpose: this also exercises the executable-directory search.
"$WORK"/build-unix/jc_reborn dump > /tmp/dump.log 2>&1
echo "OK   dump exited 0"

echo
echo "== compare against the Windows golden corpus =="
GOLDEN="$WORK/tests/golden-dump.sha256"
[ -f "$GOLDEN" ] || { echo "FAIL no golden manifest"; exit 1; }

cd "$RUN/dump"
# Same shape as the PowerShell side: lowercase hash, two spaces, relative path
# with forward slashes, sorted.
find . -type f | sed 's|^\./||' | sort | while read -r f; do
    printf '%s  %s\n' "$(sha256 "$f")" "$f"
done > /tmp/unix-dump.sha256

# tr: macOS `wc -l` right-pads its count with spaces, Linux does not.
want=$(wc -l < "$GOLDEN" | tr -d '[:space:]')
got=$(wc -l < /tmp/unix-dump.sha256 | tr -d '[:space:]')
echo "windows: $want file(s)    $OSNAME: $got file(s)"

if diff -q <(sort "$GOLDEN") <(sort /tmp/unix-dump.sha256) >/dev/null; then
    echo "OK   every one of the $got decoded files is byte-identical to Windows"
    exit 0
fi

echo "FAIL decoder output differs between Windows and $OSNAME"
diff <(sort "$GOLDEN") <(sort /tmp/unix-dump.sha256) | head -40
exit 1
