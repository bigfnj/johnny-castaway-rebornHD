# Front refresh technical export and standalone review

`export.py` accepts exactly six explicit selections for the pre-promotion
Calm-focus baseline. Use `FRAME=approved` to retain that frame's exact baseline
runtime PNG bytes, or `FRAME=RAW.png` for a new source relative to this folder.
No automatic candidate choice or approval occurs.
The provisional motion-v1 selection retains 024–027 and uses
`028-occluded-arm-v4.png` and `029-heel-fit-v2.png`.

The existing Windows toolbox Python has Pillow 12.3.0, which was used for this
candidate. The saved recipe requires its recorded version. Playwright and its
Chromium installation are needed for the browser tests. No new tool installation
is required.

The original preparation command, run before promotion from the repository
root, was:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-refresh-v1/export.py --source 024=approved --source 025=approved --source 026=approved --source 027=approved --source 028=028-occluded-arm-v4.png --source 029=029-heel-fit-v2.png --output build/front-refresh/candidate-motion-v1
```

Use a new output directory for every attempt. `--preview-only` explicitly
permits inspection of an overhanging source and withholds every runtime sprite.
It does not crop the source to make the fit pass.

After 028/029 promotion, this `--source` command intentionally refuses the changed
live baseline with `approved-runtime-identity:028`. It does not silently call the
new production artwork the old approved source. Use `--recipe` below to reproduce
motion-v1 after promotion. A later art family needs its own explicit baseline;
this historical exporter is not a general current-production editing tool.

## Frozen inputs and registration

The exporter checks the reference record, original RGBA pixels, prior recipe,
approved source bundle, and exact baseline runtime PNG hashes. Each output
retains these selected input bytes under `inputs/`, along with the current
original-derived walk table. Reproduction therefore does not depend on the
production ZIP remaining unchanged after an eventual promotion.

Retained frames are never resampled from raw art. Their padded diagnostic PNGs
place the exact existing runtime RGBA pixels on a transparent margin. Generated
frames use one uniform 0.1 scale. The first row containing alpha at least 128
provides a cap-outline observation, mapped to that frame's old cap target. The
measurement is not an engine anchor or anatomical landmark. Registration has
no silhouette fitting, separate foot scale, or per-frame body normalization.

The new sources use premultiplied RGBa, an 8× bicubic affine and Lanczos
downsampling, then straight RGBA and PNG compression level 9. The runtime
candidate is cropped from this padded technical render. Source alpha-8 centers
must fit the original doubled canvas unless preview-only mode is explicit.
The report also records filtered alpha-8 bounds; neither check promises the
absence of every low-alpha fringe.

The saved motion-v1 sources fit. New runtime PNG identities are:

| Frame | SHA256 |
|---|---|
| 028 | `5b645ae3003c54dc65946118999f0f3906ca0f7fa47a10fa61c60ba10b46e3f4` |
| 029 | `8a33597aaba9206ff8ff98bad24bd12a52142eac0bdd56c92cbf4b7de798017a` |

To reproduce a frozen candidate into a new directory:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-refresh-v1/export.py --recipe art/cartoon/walk-pilot/front-refresh-v1/review-evidence/motion-v1/export/recipe.json --output build/front-refresh/reproduced-motion-v1
```

The Python API is `prepare(sources, preview_only=False)` or
`reproduce(recipe_path)`. Both return `(recipe, inputs, images, report)`.
`render(recipe, inputs)` checks the frozen recipe and reproduces all recorded
PNG hashes. `write_output(output, *result)` refuses an existing directory.

## Standalone motion scope

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-refresh-v1/review.py --export build/front-refresh/candidate-motion-v1 --output art/cartoon/walk-pilot/front-refresh-v1/review-evidence/motion-v1
```

This creates an unpublished page, paired image files, a compact review record,
and an independently reproducible export with its inputs. The three panels are
the supplied original reference, current approved Cartoon, and revised candidate.
Original colors remain the diagnostic decoder palette.

Motion-v1 also retains byte-identical `export.py` and `review.py` snapshots under
`review-evidence/motion-v1/helpers/`. Their reproduction commands use the frozen
recipe and inputs, not `--source` preparation. Those snapshots reproduced all
20 review image/HTML/data files and the complete review record byte-for-byte in
`build/front-refresh/reproduced-review-v1/`.

Use that frozen `helpers/review.py` to reproduce motion-v1's exact HTML. The live
`review.py` now describes any explicitly selected set of revised frames without
assuming 024–027 are retained, and can build later candidates. Its generated
HTML therefore intentionally differs from the frozen motion-v1 page. That page
accurately describes its own 028/029-only revision and remains unchanged.

The viewer uses all 23 stored E-to-A travel rows, each at 120 ms. The last
transition remains 025→027. An explicitly labeled diagnostic 1000 ms pause holds
that last walking pose; it does not substitute for native standing frame 017.
The review is a composition, not an actual engine capture. A later native review
must validate actual island placement, background updates and the real arrival.

One fixed camera encloses the union of visible alpha bounds across every pose
and all three panels, including the original shadow and candidate filtering
fringes, with an eight-HD-pixel margin. It never recenters individual poses.
Motion-v1's camera is `[592,414,269,224]`. At 1280×900, each panel occupies about
403×335 CSS pixels, and all panels and controls fit in the visible page.

## Verification

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-refresh-v1/test_tools.py --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-refresh-v1/test_tools.py --phase regression --mutations
```

Two smoke checks precede 15 regressions. The browser uses a temporary loopback
server and a controlled animation-frame clock to exercise the actual page's
normal and slow timing, pause, stepping, endpoint hold and repeat controls.
The unchanged control also compares rendered current/revised pixels.

Twelve executed-source mutations cover input/source identity, registration,
original canvas, Pillow contract, runtime overhang, recorded outputs, retained
PNG preservation, the original route, stopped browser timing, and a false
retained-frame label, and accidental coupling to promoted production PNGs.
The label control actually selects new test pixels for
024 with 025–029 retained, then reads the rendered browser text. Each mutant must
produce exactly one named failure with the executed helper's SHA256 witness.

Historical authoring tests create a disposable six-frame asset ZIP from
`motion-v1/export/inputs/baseline/`, alongside the frozen prior recipe, original
catalog, and walk table. The retained old raw source bundle remains hash-pinned
by that recipe. No test replaces production files. A promotion-isolation control
serves the real new 028/029 candidate bytes to any accidental live archive read,
then confirms preparation still returns all six historical PNGs. Its mutation
forces the exporter back to the live root and must produce exactly one named
failure. These historical tests do not validate the active production pack;
the separate `tools/art_production_catalog.py --check` and
`tools/art_review_metadata.py --check` gates retain that responsibility.

The promotion-isolation update passed two smoke checks, then 15 regressions and
all 12 executed mutations on 2026-09-15. The test driver SHA256 was
`2cbf75c5ab8a7ef194fc0b706c980cf818dc11ec8c14022de29966528cca24af`.
The new live-root mutant's executed source SHA256 was
`618d0aee148d17fcd1edf93fb0e4206dea2097f5168e2592c2eafc0f6101aff8`;
`test_historical_fixture_after_promotion` failed exactly once as required.
The live exporter and both frozen motion-v1 helpers were unchanged.

Motion-v1's preserved `tool-verification.json` records the earlier two smoke,
13-regression, ten-mutation run. The later label fix and expanded test run are
recorded separately in `review-evidence/tooling-label-fix-v1.json`; they do not
rewrite the published page or its historical verification.

The separate `review-evidence/motion-v1/candidate-browser-check.json` records
the actual provisional page at 1280×900. All 23 travel states and the diagnostic
hold loaded without JavaScript errors. Current/revised pixels match for retained
024–027 and differ for the selected 028/029. The scratch screenshot is
`build/front-refresh/candidate-1280x900.png`. These checks do not assign human
approval or establish anatomical parity.

The immutable copy is now served at
`http://127.0.0.1:8932/front-refresh-motion-v1/review.html`.
`served-review-verification.json` records 20 exact served file hashes, browser
smoke before regression, all 24 states, normal/slow timing, pause, stepping,
diagnostic hold, repeat-off stopping, repeat-on wrapping, and the 1280×900 layout.
The one-off publisher and checker is retained as
`review-evidence/motion-v1/helpers/publish_motion_v1.py`; it refuses to overwrite
the already published version. That publication did not change production assets.
