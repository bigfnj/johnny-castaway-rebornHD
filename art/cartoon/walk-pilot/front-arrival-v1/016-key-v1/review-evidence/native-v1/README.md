# Native front-turn016 checkpoint

The published two-direction review is
http://127.0.0.1:8932/front-turn016-v1/review.html.
Only016 is proposed artwork. Standing017 was approved separately and is exact
in both panels. Production remains unchanged.

The actual native calls are `adsPlayWalk(0,1,0,7)` and
`adsPlayWalk(0,7,0,1)`. Each has a separate native same-heading priming call so
the starting017 is visible. That call really displays017 for120ms in the port:
`adsPlayWalk` initializes its first timer to6 ticks even when `walkAnimate`
returns80 for an immediate arrival. The observer records this behavior without
changing it. This is not a synthetic hold.

| Direction | Native priming | Requested turn | Full clip |
| --- | --- | --- | --- |
| A1 to A7 | Mirrored017 for120ms | 016, unmirrored017, repeated017; returned delays6,6,80 | 18 displays,1960ms |
| A7 to A1 | Unmirrored017 for120ms | 016, mirrored017; returned delays6,80 | 16 displays,1840ms |

The fixed close-up is `[560,400,400,280]`. The actual016 origin is `(299,243)`;
its64×148 canvas occupies HD `[598,486,662,634]`. Mirrored017 is at `(293,243)`;
unmirrored017 is at `(299,243)`. Zero-duration completion witnesses are retained
at native call boundaries. The browser advances to the final native display at
a shared timestamp rather than inventing a duration for an earlier witness.
Native draw ordinals retain the repeated017 even though its pixels can match.

## Verification and retained limitations

Both baseline directions passed smoke, full route and exact fresh-process
repeat. Candidate smoke preceded full comparison in each direction. Two016
displays change per clip, entirely inside its placed canvas; all other displays,
including approved017 and background pixels, remain exact. All timestamps,
origins, flips, returned delays and dependencies match except HD016 becoming
Cartoon016. This is a technical pixel constraint, not anatomical proof.

Browser smoke passed before full native pixel and timed-boundary checks for
both directions, fixed crops, stepping, Normal/Slow and replay controls. The
published page passed69 served file identities followed by native crop/control/
timing/layout checks in both directions. Human016 approval is not recorded by
these helpers.

The first candidate packer accidentally recorded numeric frame17 for a correct
016 ZIP addition. The native comparison guard rejected that metadata before
full comparison. `candidate-v1` retains the failed preparation and helper
copies. The corrected helper and generator use numeric16; `candidate-v2`
contains the passing capture. Both private ZIPs have the same bytes because
the error affected reporting, not the packed PNG. The first post-label browser
recheck timed out before readiness; its cause was not established. A repeat with
image/request diagnostics passed. Neither failed attempt is counted as passing.

## Reproduction

The preparation checkout was
`c56f76871d9950933913912f5828c1499b1fa4a1`. Production source inputs are bound in
`baseline-v1/build.json`. Later authoring-only commits did not change them.
Use a separate checkout with the same protected source/header/build inputs and
production archive SHA256
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
Recover approved017 runtime PNG from its saved recipe at
`build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png`, SHA256
`60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1`.
The native turn preparation adds that one member in a private baseline pack.

Stage helpers under `REPRO_CHECKOUT/build/front-arrival/front-turn-v1/` so their
`parents[2]` repository assumption is correct. Recreate the previous native
driver and packer at `build/front-arrival/native/` from the preserved standing017
checkpoint first; `prepare.py` and `prepare_candidate_helper.py` read those
files. The original arrival PNG codec/player helpers and the independent
`front-arrival-v1/trace/trace.json` must also be present at their recorded paths.

Run generator/input helpers in a fresh scratch directory. Do not pre-copy
generated `route_driver.c` or `prepare_candidate.py`, baseline/candidate output
directories, or the generated review. Existing outputs are refused. The final
corrected `build_review.py` already uses Pose close-up; `finalize_label.py` is
historical and should not be rerun during fresh reconstruction.

Host preparation:

```text
python -B build/front-arrival/front-turn-v1/prepare.py
python -B build/front-arrival/front-turn-v1/prepare_candidate_helper.py
```

Use the existing Linux toolchain image `johnny-platform-cleanup:latest`, ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`, with
Docker `--rm --init --network none`. Mount the checkout read-only at `/source`
and this scratch directory writable at `/out`. The fixed aliases are used in
recorded compiler commands. No visible workstation window is needed.

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

Recover the passing016 exporter runtime PNG, SHA256
`1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92`, then run:

```text
python -B build/front-arrival/front-turn-v1/prepare_candidate.py --png build/front-arrival/export016-v2/BMP/JOHNWALK.BMP/016.png --expected-sha256 1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92 --output build/front-arrival/front-turn-v1/candidate-v2
```

In the same mounted image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py --candidate /out/candidate-v2
```

On the host with Pillow and Playwright available:

```text
python -B build/front-arrival/front-turn-v1/build_review.py
python -B build/front-arrival/front-turn-v1/check_review.py
```

`publish.py` has the original workstation's absolute server root and slug. A
fresh reconstruction needs a different publication destination/URL and new
served checks; do not overwrite the old preview. The saved HTML needs its68
native PNGs under `images/`. Binaries, archives, raw PPMs and those full PNG sets
remain local and are intentionally excluded from the small checkpoint.

These captures establish port pixels and logical maxspeed timing. They do not
establish original-executable rendering or physical wall-clock speed.
