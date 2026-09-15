# Reproducing the rear-direction review

These tools produce a diagnostic comparison using the port's B-to-A table,
not a native capture or an art acceptance decision. Production assets are not
modified. Human review records and exact generation calls are separate files
in this folder.

Run from the repository root with Python, Pillow 12.3.0 and, for browser tests,
Playwright Chromium. On the authoring Windows machine the configured interpreter
is `$env:TOOLBOX_PYTHON`; the commands below use `python` as a portable shorthand.

## Inputs and registration

`reference/extract.py` reads the previously decoded supplied-original XPM dump.
It checks the recorded resource identities and pixel facts, then writes all 36
native and nearest-neighbor reference PNGs under the requested build directory.
See [reference/NOTES.md](reference/NOTES.md) for the source and decoder limits.
The original indices use the port dump palette and index-0 transparency; this
does not establish original executable colors or compositing.

Each generated source stays at common scale 0.1. Registration uses the first
alpha-128 row's horizontal pixel-edge midpoint as a repeatable cap-outline
observation. The target `(17, 0.25)` is in HD units. Its horizontal component
comes from the original cap span; the vertical margin is a design choice.
This is not an anatomical or engine anchor. No silhouette normalization,
warping, per-frame scale fitting or artistic pixel editing occurs.

`export.py` converts to premultiplied RGBa, applies the recorded affine at 8x
working resolution with BICUBIC, downsamples with LANCZOS, and saves RGBA PNGs.
The 64-HD-pixel padding keeps the reviewed overhang visible. Source alpha-8
pixel centers must fit before ordinary runtime-canvas export is allowed.
That check does not prove zero loss of filtered low-alpha fringes.

## Reproduce a recorded version

Use a new output directory for each export. `--preview-only` writes padded
images and reports, never runtime-canvas sprite paths.

```sh
python -B art/cartoon/walk-expansion-v1/reference/extract.py --dump-root ORIGINAL_DUMP_ROOT --output build/rear-original-reference
python -B art/cartoon/walk-expansion-v1/export.py --recipe art/cartoon/walk-expansion-v1/review-evidence/motion-v2/recipe.json --preview-only --output build/rear-review-v2
python -B art/cartoon/walk-expansion-v1/review.py --exports build/rear-review-v2 --original-native build/rear-original-reference/native --template art/cartoon/walk-expansion-v1/review-evidence/motion-v2/template.html --output build/rear-review-v2/review.html
```

The frozen template preserves the displayed version even if the current review
tool's UI changes. The report binds original-reference and padded PNG hashes;
the builder verifies both before embedding images. `preview-record.json`
records the expected HTML hash. For motion-v1, replace both `motion-v2` paths
with `motion-v1` and use a separate output directory.

The route has 23 discrete draws, nominally 120 ms each, at the port's exact
stored coordinates with its x-minus-one adjustment. Both images use the same
logical placement, doubled to HD units. Repeating jumps back to the first
draw. The route's subsequent waiting frame 018 is not included. Fit scales
the complete comparison canvas to each panel; larger explicit zooms can scroll.

## Verification scope

Reference extraction passed two smoke checks, ten regressions and three
executed-source guard mutations. Its report lives in `reference/verification.json`.
The narrow Git attributes rule was checked through a real staging-tree checkout:
removing only that rule caused one named byte-preservation failure, while the
outside-scope normalization control changed in both runs.

The exporter foundation passed two smoke checks, eleven regressions and eight
executed-source mutations. `test_export.py` uses the historical motion-v1 recipe
whose only source-center overhang is frame 022. Its fitting positive control is
explicitly synthetic. It must not be interpreted as a numerical acceptance test
for every later artwork selection.

```sh
python -B art/cartoon/walk-expansion-v1/test_export.py --recipe art/cartoon/walk-expansion-v1/review-evidence/motion-v1/recipe.json --output build/rear-export-tests
python -B art/cartoon/walk-expansion-v1/test_review.py --exports build/rear-review-v2 --original-native build/rear-original-reference/native --output build/rear-browser-tests
```

The Fit UI suite passed two smoke checks, ten regressions and six source
mutations, including all 23 full-buffer original pixel-placement comparisons.
Browser mutations verify the loaded script identity and exercise wrong draw
coordinates, a stopped timer and the old overflowing zoom. Builder mutations
exercise reference, family and PNG identity refusals in fresh Python processes.
This does not claim every possible malformed input branch is covered.

The new motion-v2 selection received a separate actual Chromium check after
the edge-note wording changed: controls, all 23 frame mappings, default
Normal/Fit settings, and subject visibility at 1280 and 1600 widths. Its full
x/y pixel extents also fit the comparison canvas. Compact evidence is in
`review-evidence/motion-v2`; earlier source/test hashes remain historical.

Motion-v2 still has source-center overhang at 020's right foot (0.65 HD px)
and 022's two side edges (0.20 HD px each). Its normal runtime export is blocked.
The padded page deliberately shows these pixels for human motion assessment.
