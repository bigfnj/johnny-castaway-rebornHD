# Integrated shoreline native observer

This version keeps all sand in one static `BACKGRND.BMP/000` surface. It observes the real surface destination as well as the logical engine origin. Native island and walking code is compiled from the selected worktree without text replacement. The observer selects a state and calls public `adsPlayWalk`; it does not set wave counters or invent animation holds.

The initial package uses the approved smooth island shape with old masked foam. Its five day still comparisons are diagnostic only: center phase 008 has no pixels with alpha at least 8. The user then requested comparison of offshore ripples against water washing onto sand, beside the original source animation. After viewing it, the user selected "Cartoon: offshore ripples". The [selection record](../wave-approaches-v1/selection.json) binds the winning package; broader scene checks and production integration remain separate. Original incoming-wave behavior is still correctly documented, but does not override this reviewed Cartoon preference.

## Commands

Run from the repository root with the existing Python and pinned Docker image. Use fresh output names for every attempt. `prepare.py` preserves all full-size V5 holiday payloads and every other archive member except the ten selected background PNGs. Production is never replaced.

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/prepare.py --baseline build/shoreline-repair-v1/selected-v1/baseline.zip --runtime-root art/cartoon/shoreline-repair-v1/integrated-shore-v1/candidates/v1 --output build/shoreline-repair-v1/integrated-selected-v1
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/run.py --baseline build/shoreline-repair-v1/selected-v1/baseline.zip --candidate build/shoreline-repair-v1/integrated-selected-v1/candidate.zip --output build/shoreline-repair-v1/integrated-native-v1 --phase initial
```

Those output directories already exist as the first diagnostic checkpoint. Reproduction must substitute new scratch output names. Its exact historical helper bytes are retained in the output's `helper-snapshot` directory; the current observer adds real surface-placement checks for the later extended center foam and is intentionally not a byte-for-byte replay of the earlier observer.

Use `--phase full` with a newly prepared complete art selection. Full mode runs all smoke cases first, then a fresh-process exact repeat of each case. The cases are five initial holiday states, high-tide cycles without and with clovers, low-tide cycles without and with clovers, a combined night/shift clover diagnostic, and front/rear Johnny waypoint routes. A successful technical run is not an assertion that the inherited low-tide artwork visually matches the enlarged island.

`--phase cycle` captures only the high-tide clover comparison with twenty genuine same-heading waits, smoke then fresh repeat. Both Cartoon variants must retain the same approved static ground and full-size clovers. Extended center artwork uses the explicit `384x256` registered canvas with HD offset `[-32,-90]`. Legacy center foam remains `320x50` with no offset; intermediate discarded canvas proposals are not accepted.

The original source reference command is:

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/run_original.py --archive build/seasonal-v1/island-footprint/original-full.zip --output build/shoreline-repair-v1/original-cycle-v1
```

Again, choose a fresh output directory when reproducing. The source package is pinned to SHA256 `4301aad91184789727688cb3dac9ade7a8f04152cbde056a29396c9bfaeeac8f`, contains the supplied original resource pair and has no HD or Cartoon PNG overrides. Its original clovers and waves render through the port's legacy path at nearest2x. Original smoke and fresh-repeat reports are byte-identical: 51 display records over 2400 ms, all nine high-tide phases, and three executed negative controls. The colors are diagnostic; this does not claim original-executable palette or timing parity.

## Recorded behavior

The selected offshore package completed the full matrix: 24 smoke captures
passed before 24 exact fresh-process repeats, and all six existing negative
controls fired. Protected runtime inputs and the production archive were
unchanged, and the isolated Docker container was removed. The compact retained
record is [offshore-full-evidence-v1](offshore-full-evidence-v1/README.md).
The [scene review](../offshore-scene-review-v1/README.md) shows the actual native
pixels and timing. Human seasonal placement approval remains separate from
these technical results.

Every window update is captured after the real native display call. Identical images within a clip share a PNG while all display timestamps and repeated frames remain in its report. `time_ms` uses the port's observed 20 ms logical ticks. The display sequence retains the actual first-frame delay behavior of repeated native waits. This is not an original-executable timing comparison.

Long wave clips use repeated same-heading waits at A. Background timers persist across those calls. High tide must display all frames 003–011; low tide must display all frames 030–041. The two Johnny clips use the existing D→C→F and B→A→E calls, including their real waypoint turns and arrivals. Both archive variants must have identical display times, phase tuples and Johnny draw records.

`run.py` launches Linux/Xvfb inside the existing pinned Docker image, with the worktree mounted read-only and an explicit scratch output mount. It removes only its uniquely named container and verifies it is absent. No native window is opened on the workstation. The direct driver bypasses calendar holiday selection, random tide selection and cargo-story suppression; these policy paths are outside this art review.
