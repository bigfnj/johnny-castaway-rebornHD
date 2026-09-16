# Remaining wait-pose exporter

One shared tool exports a single explicitly selected frame, either 000 or 015.
Other slots are intentionally unsupported. The approved 016 and 017 exporters
remain frozen. This tool retains their premultiplied RGBa, 8x BICUBIC, then
LANCZOS filtering without pose warps, alpha trimming or independent body scaling.

| Frame | Original canvas | Runtime canvas | Cap target | Source |
|---|---|---|---|---|
| 000 | 40 x 76 | 80 x 152 | [54, 0.25] | `000-profile-v1.png` |
| 015 | 40 x 73 | 80 x 146 | [35, 0.25] | `015-rear-v1.png` |

Both use uniform scale 0.1 and 64-pixel diagnostic padding. Each X target is
twice its original top-row pixel-edge midpoint. Y=0.25 is the inherited filter
margin. These measured outline observations are not anatomical or engine anchors.
Each frame pins its own original source record and native/nearest8 PNG bytes.

Use Pillow 12.3.0 and run from the repository root. Each output directory must
be fresh. Prepare the actual handed-off sources explicitly:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 0 --prepare --source 000-profile-v1.png --output build/front-arrival/waits000-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 15 --prepare --source 015-rear-v1.png --output build/front-arrival/waits015-v1
```

Reproduction requires both the saved recipe and matching explicit frame. For
example, after preparation:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 0 --recipe build/front-arrival/waits000-v1/recipe.json --output build/front-arrival/waits000-reproduced-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 15 --recipe build/front-arrival/waits015-v1/recipe.json --output build/front-arrival/waits015-reproduced-v1
```

The recipe binds source bytes, the selected original references, fixed placement,
canvas and Pillow version. A different recipe frame is refused. `--preview-only`
retains an overhanging drawing in padding and writes no runtime sprite; it does
not grant acceptance or change placement policy.

For each candidate, run smoke before regression using the same recipe, frame
and fresh test-output directory. Substitute 15 and its recipe/output paths to
check the second configuration:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/test_export.py --frame 0 --phase smoke --recipe build/front-arrival/waits000-v1/recipe.json --output build/front-arrival/waits000-tests-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/test_export.py --frame 0 --phase regression --mutation-check --recipe build/front-arrival/waits000-v1/recipe.json --output build/front-arrival/waits000-tests-v1
```

Tests cover explicit frame selection, recipe/frame mismatch, cross-frame
reference mismatch, original-pixel cap registration, fixed fit and retained
alpha filtering. Filter parity uses the frozen 017 implementation at the
selected original geometry with opaque, semitransparent and transparent pixels.
Mutants execute in fresh Python processes and must produce one named failure
plus an executed source SHA witness. These checks do not establish anatomical
correctness, native motion acceptance or original executable playback parity.

Both configurations passed 3 smoke checks, 23 behavioral cases and 19 executed
mutations, with one named failure per mutant. Results are under
`build/front-arrival/waits000-tests-v1/` and `waits015-tests-v1/`. No previous
native gate or frozen authoring suite was rerun as part of this bounded change.

| Frame | Runtime PNG SHA256 | Recipe SHA256 |
|---|---|---|
| 000 | `9fef4cef56033a7cf35c36d96a839c42e7d7d23832acf0a34ebc6ff52e040e96` | `51d119dadfb2e01329aba02e7af4ac570ddc5102b97af1913bc4b42aba9f085e` |
| 015 | `c74f85cdd79ed13f180f3cb3c8c5962ba0453d587a2c8da15c844a2c046eb5d8` | `2eb95bb64cee6053e5b6cd4a0459b41ccb9e604b23a5eb0bbb76b984eb489458` |

The handed-off source hashes are
`ae989a65335c10a24da3176ff6fd568dc4a2cb6fddda185002c60dcdae3d3a12`
for 000 and
`dbd88e081fafbe906f9a9482128bb54fad1b142d1dc18f240e099bfe7e227578`
for 015. Both pass alpha >= 8 source-center fit. Filtered alpha >= 8 bounds are
`[26, 0, 65, 147]` and `[7, 0, 63, 146]` respectively; padded images retain any
lower-alpha filter fringe.
