# Frame 016 technical export

The selected candidate uses `016-toe-fit-v2.png`, SHA256
`d89066217905e3e1a2fa509f1f9d6cfecbb084cb7fba50844a32a9d8c181c052`.
It exports to the original frame's doubled **64 x 148** runtime canvas at uniform
scale **0.1**, with cap target **[35, 0.25]** and 64-pixel diagnostic padding.
X comes from the original top-row pixel-edge midpoint; Y is the inherited
filter margin. Neither is an anatomical anchor.

Use **Pillow 12.3.0**. The recipe pins that version, source bytes, reference bytes,
canvas and affine transform. The exporter preserves the frozen 017 premultiplied
RGBa, 8x BICUBIC, then LANCZOS filtering and does not warp poses, threshold alpha,
independently fit dimensions or promote assets.

Run from the repository root in PowerShell with the toolbox Python. Output
directories must not already exist. Reproduce the exact retained recipe:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/candidate-recipe-v1.json --output build/front-arrival/export016-reproduced-v2
```

To measure this same source and prepare a new technical recipe explicitly:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/export.py --prepare --source 016-toe-fit-v2.png --output build/front-arrival/export016-prepared-v2
```

The expected runtime `BMP/JOHNWALK.BMP/016.png` SHA256 is
`1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92`.
The retained recipe SHA256 is
`47806f8ae481735023238a0afa341eff393169cb4fb2134005ff55ecf4382bca`.
Source alpha >= 8 centers fit the canvas; the filtered alpha >= 8 bounds are
`[6, 0, 63, 147]`. Low-alpha filter fringes remain in `padded/016.png`.

Run smoke first, then regression and executed mutations using the same fresh
test output directory and recipe:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/test_export.py --phase smoke --recipe art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/candidate-recipe-v1.json --output build/front-arrival/export016-reproduced-tests
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/test_export.py --phase regression --mutation-check --recipe art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/candidate-recipe-v1.json --output build/front-arrival/export016-reproduced-tests
```

The retained results are 3 smoke checks, 22 behavioral regressions and 18
executed mutations. Each mutant produced one named failure and an executed
source SHA witness. Checks include original reference identity, explicit input
selection, original-pixel cap registration, fixed placement, fit, recipe-byte
preservation and parity with frozen 017 filtering. These are technical checks,
not anatomical, motion or native-rendering acceptance.

`review-evidence/rejected-fit-v1/` preserves the first drawing's preview recipe
and report. Its rightmost alpha >= 8 source center mapped to 64.05 against the
exclusive width 64, so the runtime exporter rejected it before writing a
sprite. The diagnostic preview retained the overhang. The selected v2 drawing
was edited through image generation; the export policy remained unchanged.
