#!/usr/bin/env bash
set -euo pipefail
SRC=${SRC:-/src}
OUT=${OUT:-/work/web-platform-tests}
phase=${2:-all}
if [[ $# -gt 0 && $1 != --phase ]] || [[ $phase != smoke && $phase != regression && $phase != all ]]; then
    echo "usage: run_web_platform.sh [--phase smoke|regression|all]" >&2; exit 2
fi
mkdir -p "$OUT"
for driver in test_platform_alloc test_web_audio; do
    emcc -std=gnu11 -DPLATFORM_WEB -Wall -Wextra -Wno-unused-parameter \
        -I"$SRC/platform" -I"$SRC/src/engine" "$SRC/tests/$driver.c" \
        -sENVIRONMENT=node -sASYNCIFY -sALLOW_MEMORY_GROWTH -sSAFE_HEAP=1 -o "$OUT/$driver.js"
done
alloc_cases='success surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3'
audio_cases='mono stereo format'
if [[ $phase == smoke ]]; then
    alloc_cases=success; audio_cases=mono
elif [[ $phase == regression ]]; then
    alloc_cases='surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3'; audio_cases='stereo format'
fi
for case in $alloc_cases; do
    node "$OUT/test_platform_alloc.js" "$case"
done
for case in $audio_cases; do
    node "$OUT/test_web_audio.js" "$case"
done
