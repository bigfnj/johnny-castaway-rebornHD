# Independent material review reconstruction

`evidence.json` binds the exact report, export recipe, executed scratch helpers and retained diagnostic images. The four annotation/input files are referenced relative to this directory and also hash-bound. The binder deliberately excludes this explanatory file. The original source PNGs remain under `../../inputs/` and are individually bound by `input-index.json` and the landmark manifests. Corrected sprites and soft masks remain local build outputs; no archive or native capture is copied here.

The numerical readback inspected all 28 final sprites, every alpha byte, the full cap exclusion, all pixels outside the soft mask, 222 independently chosen material points and 84 small RGBA regions. All passed. Twenty-seven sprites changed and 029 remained identical. Visual review covered every head/cap/mask pair, plus the six whole-body examples named in the report. The checks do not claim exhaustive semantic labeling of every antialiased edge pixel.

## Recreate the export and numerical comparisons

Use a fresh checkout or worktree containing the bound inputs, annotations and `correct.py` matching `export-recipe.json`. The reviewed algorithm SHA256 is `70be24d13eb34317f602b0b66f952a4d3dbe8e29935b4f6c8353f15c8e9d3534`. Run the normal corrector smoke checks before this reconstruction according to the bundle's maintained instructions. With Pillow and NumPy available, from the repository root:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/correct.py --output build/skin-tone/export-v2
```

The destination must be fresh. Verify its recipe SHA256 equals `material-review.json`'s `recipe_sha256` before comparing. Do not overwrite the original reviewed export in the working task.

`helpers/inspect_outputs.py` is the exact executed diagnostic helper. Its original location was `build/skin-tone/protected-review-v1/inspect_outputs.py`; it finds the repository via `parents[3]` and reads the fixed `build/skin-tone/export-v2` destination. In the fresh reconstruction checkout, create that scratch directory and copy the helper there unchanged before running it:

```powershell
New-Item -ItemType Directory -Path build/skin-tone/protected-review-v1
Copy-Item -LiteralPath art/cartoon/skin-tone-v1/review-evidence/material-v2/helpers/inspect_outputs.py -Destination build/skin-tone/protected-review-v1/inspect_outputs.py
& $env:TOOLBOX_PYTHON -B build/skin-tone/protected-review-v1/inspect_outputs.py
```

Expected terminal summary: 28 frames, zero protected failures, 27 nonidentity sprites and no geometry/mask failures. `export-v2-readback.json` matches the retained `raw-readback.json`. The helper also creates the seven head/mask sheets; their original rendering used Windows Consolas at `C:/Windows/Fonts/consola.ttf`. A different font or Pillow version may change diagnostic-image bytes without changing the sprite comparisons. `material-review.json` adds the recorded visual assessment to the raw readback; do not regenerate that human-readable assessment as if it were an automated result.

## Review the three coordinate corrections

The retained original-only grids `original-grids/chest004-grid.png`, `chest005-grid.png` and `chest008-grid.png` show the rejected v1 points with red borders. The old coordinates sit on skin next to the strand. The correct hair coordinates are 004 at 54,54; 005 at 61,54; and 008 at 49,54. `chest-all-0.png` and `chest-all-1.png` cover the reinspection of all 17 lower-hair samples. The v2 JSON embeds the old/new coordinates and source RGBA values, while v1 remains unchanged. See `../../PROTECTED-LANDMARKS.md` for the semantic decision and its limits.

To recreate the three local pixel grids directly, open the frozen input as RGBA, crop `(old_x-8, old_y-8, old_x+9, old_y+9)`, and enlarge each source pixel to a 30x30 square with nearest-neighbor sampling. The source crops are therefore 17x17. The retained images place that crop at 50,40 on a 580x580 `#3a4550` background, draw coordinate grid lines, and outline the center source pixel in red. The two overview sheets use 15x15 crops around every v1 lower-hair point with 20x nearest-neighbor enlargement. These are display aids only; all verification reads original RGBA bytes directly.

`helpers/select_landmarks.py`, `freeze_landmarks.py` and `revise_landmarks.py` are historical provenance, not routine validation entry points. Do not run the annotation writers over either retained manifest. Their original scratch depth and auxiliary proposals were part of the earlier selection workflow. Likewise, cap annotations are algorithm exclusions rather than independent evidence that their own contours are correct; the original-only overlays in `original-grids/cap-boundaries-*.png` document the separate visual contour inspection.
