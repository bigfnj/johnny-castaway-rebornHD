#!/usr/bin/env bash
set -euo pipefail
SRC=${SRC:-/src}
OUT=${OUT:-/work/platform-tests}
phase=${2:-all}
if [[ $# -gt 0 && $1 != --phase ]] || [[ $phase != smoke && $phase != regression && $phase != all ]]; then
    echo "usage: run_linux_platform.sh [--phase smoke|regression|all]" >&2; exit 2
fi
mkdir -p "$OUT"
cc -std=c11 -D_DEFAULT_SOURCE -DPLATFORM_LINUX -Wall -Wextra -Werror \
    -I"$SRC/platform" -I"$SRC/src/engine" \
    "$SRC/tests/test_linux_audio.c" -o "$OUT/test_linux_audio" -lX11 -lasound -pthread
audio_cases='normal-reopen worker-error create-failure allocation-failure parameter-failure join-failure'
alloc_cases='success surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3'
window_cases='pixels presentation-failure events gc-failure image-failure window-failure'
if [[ $phase == smoke ]]; then
    audio_cases=normal-reopen; alloc_cases=success; window_cases=pixels
elif [[ $phase == regression ]]; then
    audio_cases='worker-error create-failure allocation-failure parameter-failure join-failure'
    alloc_cases='surface-struct surface-pixels borrowed-wrapper window-1 window-2 window-3'
    window_cases='presentation-failure events gc-failure image-failure window-failure'
fi
for case in $audio_cases; do
    timeout 10 "$OUT/test_linux_audio" "$case"
done
cc -std=c11 -D_DEFAULT_SOURCE -DPLATFORM_LINUX -Wall -Wextra -Werror \
    -I"$SRC/platform" -I"$SRC/src/engine" \
    "$SRC/tests/test_platform_alloc.c" -o "$OUT/test_platform_alloc" -lX11 -lasound -pthread
for case in $alloc_cases; do
    xvfb-run -a timeout 10 "$OUT/test_platform_alloc" "$case"
done
cc -std=c11 -D_DEFAULT_SOURCE -DPLATFORM_LINUX -Wall -Wextra -Werror \
    -I"$SRC/platform" -I"$SRC/src/engine" \
    "$SRC/tests/test_linux_window.c" -o "$OUT/test_linux_window" -lX11 -lasound -pthread
for case in $window_cases; do
    xvfb-run -a timeout 10 "$OUT/test_linux_window" "$case"
done
