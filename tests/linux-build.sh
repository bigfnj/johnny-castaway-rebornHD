#!/usr/bin/env bash
#
#  Build jc_reborn on Linux and verify its DECODER OUTPUT matches Windows.
#
#  Intended to run inside a container, e.g.
#    docker run --rm -v <repo>:/src:ro ubuntu:24.04 bash /src/tests/linux-build.sh
#
#  WHY THIS IS WORTH DOING AT ALL. `dump` never calls graphicsInit and touches no
#  RNG, so it runs headless with no X server and decodes every BMP, SCR, ADS and
#  TTM resource in the archive. That makes the golden manifest generated on
#  Windows directly comparable here: any hash that differs is a real
#  cross-platform decode defect - endianness, struct packing, signed char,
#  undefined shifts - and not a rendering difference or a timing artefact.
#
#  It is also the only automated proof that the Linux build works at all. It did
#  not: platform_linux.c used PTHREAD_MUTEX_INITIALIZER and four pthread
#  functions with no <pthread.h>, which is a hard error on GCC 14, and nothing in
#  the repository would have noticed.
set -euo pipefail

SRC=${SRC:-/src}
WORK=${WORK:-/work}

echo "== toolchain =="
if ! command -v cmake >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq build-essential cmake libx11-dev libasound2-dev >/dev/null
fi
cc --version | head -1
cmake --version | head -1

# Copy out of the read-only mount so the build cannot touch the repo, and so
# Windows build trees are not dragged into the Linux configure.
rm -rf "$WORK"
mkdir -p "$WORK"
cp -r "$SRC"/. "$WORK"/
rm -rf "$WORK"/build "$WORK"/build-asan "$WORK"/build-linux "$WORK"/.git
cd "$WORK"

echo
echo "== build =="
cmake -S . -B build-linux -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build build-linux -j"$(nproc)" 2>&1 | tee /tmp/build.log | grep -E 'error|warning' || true

if ! [ -x build-linux/jc_reborn ]; then
    echo "FAIL no binary produced"
    exit 1
fi
echo "OK   built build-linux/jc_reborn"

echo
echo "== dump, headless, no X server =="
RUN=/tmp/jcr-run
rm -rf "$RUN"; mkdir -p "$RUN"; cd "$RUN"
# No zip here on purpose: this also exercises the executable-directory search.
"$WORK"/build-linux/jc_reborn dump > /tmp/dump.log 2>&1
echo "OK   dump exited 0"

echo
echo "== compare against the Windows golden corpus =="
GOLDEN="$WORK/tests/golden-dump.sha256"
[ -f "$GOLDEN" ] || { echo "FAIL no golden manifest"; exit 1; }

cd "$RUN/dump"
# Same shape as the PowerShell side: lowercase hash, two spaces, relative path
# with forward slashes, sorted.
find . -type f | sed 's|^\./||' | sort | while read -r f; do
    printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f"
done > /tmp/linux-dump.sha256

want=$(wc -l < "$GOLDEN")
got=$(wc -l < /tmp/linux-dump.sha256)
echo "windows: $want file(s)    linux: $got file(s)"

if diff -q <(sort "$GOLDEN") <(sort /tmp/linux-dump.sha256) >/dev/null; then
    echo "OK   every one of the $got decoded files is byte-identical to Windows"
    exit 0
fi

echo "FAIL decoder output differs between Windows and Linux"
diff <(sort "$GOLDEN") <(sort /tmp/linux-dump.sha256) | head -40
exit 1
