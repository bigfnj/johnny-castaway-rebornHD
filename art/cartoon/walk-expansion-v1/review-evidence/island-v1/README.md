# Native island review evidence

The exact displayed page was
`http://127.0.0.1:8932/rear-cartoon-island-v1/review.html`, with HTML SHA256
`2a787afd1d2ee0c41a1113652cb5c05634bf593d1b302986e97f42d9ffa16df8`.
Human acceptance is recorded separately. These files preserve the technical
candidate and observations that preceded any production promotion.

The left panel used the existing HD walking sprites on the current Cartoon
island. The right panel changed only the six rear travel sprites. This was a
Linux API-driver capture, not an original-executable rendering or a composition
of the supplied-original reference PNGs. Cloud assets can remain HD fallback.

The saved executable SHA256 is
`831a6ada20ac1e1d68d822e325b2a664ec5a1ca22522b82d3fff7e01aaacc2b8`.
`baseline-build.json` retains its exact GCC arguments, wrapper/engine source
hashes and fresh-build timestamp. The driver calls the unchanged
`adsPlayWalk(1,3,0,3)` after finding the direct B,A,UNDEF path. Island seed 11 and
path seed 2 are Linux-specific selections, with loaded dependencies recorded.

There are 23 travel poses and the final HD arrival pose 018. The full timeline
contains 47 presented states, including background updates and a zero-duration
completion witness at 4360 ms. Travel uses 120 ms pose intervals; arrival holds
for 1600 ms. The observer calls the real timing/presentation functions and
excludes event-driven X11 expose repaints. It changes no route or resource data.

## Checks and limits

- The unchanged-archive control reproduced all 47 saved baseline images exactly.
- Candidate smoke ran before the full route. All timestamps, stored rows, draw
  coordinates and loaded dependencies matched, apart from the six intended
  style-resolution paths. Every travel image differed only within the current
  Johnny canvas. All arrival images matched the baseline completely.
- The private archive preserved all 2572 existing members and added exactly six
  paths. Its `RESOURCE.MAP`, `RESOURCE.001`, old style sprites and manifest were
  unchanged. The production ZIP was not written by these helpers.
- Chromium smoke preceded the timed playback checks. All 47 recorded times and
  94 full native canvas pixel hashes matched. Full-island and close-up controls,
  pose 8-to-9 stepping, arrival, repeat and 1280/1600-width layout passed.
- Four bounded helper mutations and two served-browser mutations fired with
  exact executed-source or response/script identity witnesses. They exercise
  source identity, swapped same-size poses, preview-only refusal, pixels outside
  Johnny, stopped playback and wrong rendered pixels. They are not exhaustive
  malformed-input coverage.

All six source-center and filtered-alpha-8 bounds fit their runtime canvases.
This does not claim that every lower-alpha filter fringe is absent. Physical
wall-clock speed, original-executable parity and anatomical correctness are not
established by the technical checks.

## Reproduction inputs and commands

The helper snapshots in `helpers/` are intended to be copied unchanged into
an isolated checkout's `build/rear-native-capture/` directory. That location is
part of their scratch path convention. `route_driver.c` and `run_baseline.py`
retain the complete initial build and capture process, including the real calls
and observation filters. No saved binary or large native PNG set is duplicated
in this folder.

The baseline used source checkout `10672766e0534350f76db53c743002acf9ab1d8b`.
For a later reproduction, use a separate checkout of that source snapshot and
the original baseline archive named by `baseline-build.json`, not a subsequently
promoted production archive. Supply the six raw source files and reference/tool
files named by this folder's exact recipe from the authoring records. The
capture runner verifies all recorded protected source/archive hashes before
using the saved binary.

Export the recipe from the repository root, using Pillow 12.3.0:

```sh
python -B art/cartoon/walk-expansion-v1/export.py --recipe art/cartoon/walk-expansion-v1/review-evidence/island-v1/recipe.json --output build/cartoon-production-reference/runtime-candidate-v1
python -B build/rear-native-capture/prepare_candidate.py --exports build/cartoon-production-reference/runtime-candidate-v1 --output build/rear-native-capture/candidate-v1
```

The actual Linux image was
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
The existing saved `baseline-v2/rear_route_probe` was reused without rebuilding.
With the checkout mounted read-only at `/source` and its private capture
directory mounted at `/out`, run:

```sh
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/run_candidate.py --candidate /out/candidate-v1
```

The enclosing Docker invocation needs `--init` in this environment. For a fresh
baseline, the same mounts/image run `/out/run_baseline.py`; it refuses an existing
`baseline-v2` directory. The saved build command specifies every production
translation unit and the two observation-only linker wrappers. A fresh build
must retain its own toolchain/executable identity rather than assume the old
binary hash applies.

After a passing candidate smoke and full route:

```sh
python -B build/rear-native-capture/build_review.py --candidate build/rear-native-capture/candidate-v1 --output build/rear-native-capture/island-review-v2
python -B build/rear-native-capture/check_review.py --review build/rear-native-capture/island-review-v2
```

Serve `review.html` and its `images/` directory over localhost. The browser
checker uses its own temporary HTTP server so canvas inspection observes the
same origin policy as the shared preview. Image files are exact lossless
serializations of the native RGB captures. `review-record.json` retains their
94 PNG hashes, while the full capture reports retain timing and RGB hashes.
Existing output directories are preserved rather than silently overwritten.
