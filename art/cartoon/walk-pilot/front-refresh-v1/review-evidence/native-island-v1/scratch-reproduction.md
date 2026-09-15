# Front route native review, provisional 028/029

This directory is ignored scratch evidence. Production source and
`assets/scrantic_data.zip` were not changed. No candidate was published or accepted
by a human here.

The observer is adapted from the preserved arrival observer. It calls the real
`adsPlayWalk(4,1,0,1)` and wraps completed waits, window updates, walking delay
returns, and actual sprite draw/flip calls without changing their arguments.
The direct E-to-A route selected path seed 2 in the existing Linux image, with
island seed 11. The seed is an observation of this glibc environment, not a
cross-platform random-number promise.

The 23 travel poses return 6 ticks each, then mirrored HD017 at logical draw
origin (293,243) returns 80 ticks. The final travel pose is 027 at (300,242).
The first travel pose is 028 at (394,212). Native capture observed 47 displays
over 4360 ms, including background updates and the zero-duration completion
witness. The count was obtained from actual captures and completed waits rather
than imposed from the previous rear-route review.

The full canvas union is HD [586,424,852,636]. Both panels use fixed close-up
[560,400,400,280], including room above the caps and below the feet. Native
maxspeed execution records logical delays; the browser replays those delays.
This does not establish original-binary pixel or physical wall-clock parity.

## Identities

| Input | Identity |
| --- | --- |
| Source commit | `4551081495eee81e5e5bf2d8b5f00a5619a176a2` |
| Existing Linux image | `sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72` |
| New native observer | `ac2b28b83dfa7d4b32d2f90b2ae37ab6f82ce4491eac5d5ed1bddce03c8ec947` |
| Production28 archive | `0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd` |
| Private candidate archive | `1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63` |
| Provisional 028 runtime PNG | `5b645ae3003c54dc65946118999f0f3906ca0f7fa47a10fa61c60ba10b46e3f4` |
| Provisional 029 runtime PNG | `8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a` |

`preparation.json` records the exact preserved driver input and its adaptations.
`baseline-v1/build.json` records compiler arguments, versions, executable
timestamp advancement, and 60 protected source/helper/archive fingerprints.
The build emitted no warnings or errors. The prior arrival helpers were only
read, and all protected inputs were unchanged after native execution.

## Verification

Baseline smoke passed before full-route validation. A fresh native process then
replayed the baseline: all 47 RGB and PNG hashes, timestamps, actual draw calls,
and loaded art dependencies matched. This is a comparison of two executions,
not a new golden array copied from the implementation. Travel geometry is read
from the source table and checked against real draw dispatch.

The private candidate replaces exactly 2 of 2579 ZIP members. All other 2577
members retain their bytes, including original resource data, other artwork,
and manifests. Exported 024-027 also matched production bytes before packing.

Candidate smoke passed before full-route regression. All 47 logical timestamps,
draw/flip calls, delay returns, and dependencies matched the baseline. Twelve
displays differ only inside the actual placed 028/029 canvases. Thirty-five
displays are pixel-identical, including every mirrored HD017 arrival display.
There is no rear018-only mask or replacement in this comparison.

The actual mask helper passed six controls using saved, hash-bound native
pixels: current candidate, allowed inside change, and disallowed changes on
each of four outer sides. A copied helper with the mask removed was compiled
to fresh bytecode; timestamp advancement and an execution witness preceded one
named rejection failure. This is comparison-helper verification, not another
native execution. See `candidate-v1/mask-guard-verification.json`.

`island-review-v1` contains 94 unchanged native PNGs and an adapted copy of the
existing arrival player. Chromium smoke passed before four grouped regressions:
all 47 timestamps and 94 full-canvas pixel hashes; exact close-up pixels and
pose/playback controls; fitted 1280/1600 layouts; and missing-image diagnostics.
The stopped-timer and wrong-candidate-pixels browser mutations both fired with
verified served HTML and loaded script identities.

## Commands and artifacts

These commands were used in order. Preparation and capture refuse an existing
target; use a new versioned scratch directory for another run.

When reconstructing from the retained package, copy only these nine files from
`helpers/` into the fresh scratch directory: `prepare.py`, `capture.py`,
`prepare_candidate.py`, `capture_candidate.py`, `check_candidate_guards.py`,
`build_review.py`, `finish.py`, `finish_review.py`, and `preserve.py`. Leave out
the retained generated `route_driver.c` and `check_review.py`. They are created
by `prepare.py` and `build_review.py`, respectively; copying them first makes
those generators correctly refuse to overwrite existing evidence.

```powershell
python -B build/front-native-review/prepare.py
```

Run the existing Linux image with the checkout read-only at `/source`, this
scratch directory writable at `/out`, and `--init`:

```sh
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

```powershell
python -B build/front-native-review/prepare_candidate.py --exports build/front-refresh/candidate-motion-v1
```

```sh
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py
python3 -B /out/check_candidate_guards.py
```

The following checks use the toolbox Python with Pillow and Playwright:

```powershell
python -B build/front-native-review/build_review.py
python -B build/front-native-review/check_review.py --review build/front-native-review/island-review-v1
```

For a later review publication, copy only `review.html` and `images/` from
`island-review-v1`. The browser checker also writes deliberately broken control
HTML files and screenshots there; those are verification artifacts.

Each native `report.json` binds its capture log, every display's pixels/PNG,
logical timing, draw arguments, and actual dependencies. The final manifest
binds the small helper and report files. Large executable, ZIP, and PPM/PNG
capture sets remain local scratch evidence for reproducibility.
