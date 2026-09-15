#!/usr/bin/env bash
set -euo pipefail
SRC=${SRC:-$(cd "$(dirname "$0")/.." && pwd)}
OUT=${OUT:-/tmp/johnny-platform-tests}
phase=${2:-all}
if [[ $# -gt 0 && $1 != --phase ]] || [[ $phase != smoke && $phase != regression && $phase != all ]]; then
    echo "usage: run_macos_platform.sh [--phase smoke|regression|all]" >&2; exit 2
fi
mkdir -p "$OUT"
for driver in test_platform_alloc_macos test_macos_events; do
    clang -DPLATFORM_MACOS -I"$SRC/platform" -I"$SRC/src/engine" \
        "$SRC/tests/$driver.m" -framework Cocoa -framework AudioToolbox -o "$OUT/$driver"
done
alloc_cases='success surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3 native-window native-context'
event_cases='drain delegate-quit unknown-key'
if [[ $phase == smoke ]]; then
    alloc_cases=success; event_cases=drain
elif [[ $phase == regression ]]; then
    alloc_cases='surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3 native-window native-context'
    event_cases='delegate-quit unknown-key'
fi
for case in $alloc_cases; do
    "$OUT/test_platform_alloc_macos" "$case"
done
for case in $event_cases; do
    "$OUT/test_macos_events" "$case"
done
