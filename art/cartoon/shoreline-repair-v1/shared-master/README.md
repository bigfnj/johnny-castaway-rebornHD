# Shared ground master diagnostic

`export.py` reads `raw/ground-master-v2.png` and the pinned master reference from
the parent directory. It calls the frozen seasonal V1 premultiplied filter once
with affine `[0.5, 0, -64, 0, 0.5, -192]`. The world crop is
`[540, 558, 1180, 686]`. It applies no fitting, material mask, alpha threshold or
color edit.

Ground comes from disjoint rectangular crops of that single result. Sprite 000
owns its original rectangle. Left, center and right wave families own the
remaining rectangles; the center owns the overlap outside 000. All three phases
in each family use the same ground pixels. The unchanged production foam PNGs
are inputs to source-over composition, so the final wave PNGs are new files.
Their final alpha naturally combines ground and foam alpha.

The ten runtime PNGs are under `candidates/v1/BMP/BACKGRND.BMP/`. Intermediate
ground layers, the master and its padded image are retained beside them.
`recipe-v1.json` pins the raw, reference, archive, foam members and transform;
`candidates/v1/export-report.json` records the actual outputs and clipping.

## Reproduce

Run from the repository root with Python and Pillow 12.3.0. The toolbox interpreter
on this workstation is available through `$env:TOOLBOX_PYTHON`.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/shared-master/export.py --check
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/shared-master/export.py --output build/shoreline-repair-v1/shared-master-replay
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/shared-master/test_export.py --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/shared-master/test_export.py --phase regression
```

The replay output directory must be new. Use the existing recipe; `--prepare`
refuses to overwrite it. Tests rewrite their current verification summaries and
use temporary directories for damaged inputs. Preserve frozen summaries before
re-running them for a later checkpoint.

## Measured limits

The 72,392 pixels inside the original sprite rectangles reconstruct with exact
RGBA values from the actual ground crops. This does not mean the entire generated
master is preserved in the runtime assets. Four master pixels lie outside that
union and cannot be represented in the original canvases:

| World coordinate | Master RGBA |
|---|---|
|1136,603 |63,63,0,4 |
|1137,604 |63,63,0,4 |
|1136,605 |127,79,20,74 |
|1138,605 |85,85,0,3 |

Those pixels remain in `master-ground.png`; the per-sprite outputs omit them.
The fixed master crop also omits 200 filtered nonzero-alpha pixels, including 55
at alpha 8 or greater, with maximum alpha 69. The padded master retains that local
fringe. Raw source pixels outside the crop are measured separately. No scale or
translation was changed to conceal either loss.

Two actual crop-path witnesses at world 860,650 and 1040,666 preserve alpha 128.
A duplicate-draw control produces 192. Opaque and transparent controls also pass.
Source-over preserves all alpha and nonzero-alpha RGBA in the representable
ground; it normalizes 303 invisible RGB values at alpha 0. Exact rectangular crops
retain those hidden values. The initial test confused these two forms of
reconstruction; `verification-attempt-1.json` preserves that finding and the
corrected oracle's scope.

The executed missing-row mutation fails the union-coverage check. Removing that
check admits the missing row and changes sprite 006; a duplicate-ownership case
also fails by name. Fresh replay reproduces every saved output exactly.

This remains unapproved scene artwork. Visual inspection found no foam baked into
the raw ground, but that is not an automatic material classifier. Native family
order can change overlapping foam, and low tide uses other shore sprites. These
checks do not establish tide continuity, contact or human approval.
