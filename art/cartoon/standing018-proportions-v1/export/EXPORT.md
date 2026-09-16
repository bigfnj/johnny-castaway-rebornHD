# Standing018 export staging

`stage.py` copies the unchanged arrival-pilot-v1 exporter and tests, their four
original reference files and one explicitly hash-bound raw PNG into a fresh
ignored authoring folder. It does not edit image pixels or copy anything into
the historical authoring folder. The exporter remains SHA256
`c382582ad113c917ee8b5f8e0ebda392ceb5f746bdb4be9982b7a51f04418c63`.

The contract remains scale0.1, cap target[17,0.25], runtime64x154, premultiplied
RGBa bicubic at8x followed by Lanczos, and64HD padding. Alpha>=8 source centers
must fit the fixed runtime canvas. Padded output retains filter fringe. No
per-pose scaling or anatomy adjustment occurs in this adapter.

Run from the repository root with the toolbox Python and Pillow12.3.0. Replace
SOURCE and SHA with the selected raw file and its actual hash; use a new WORK
path below build for each attempt:

```text
python -B art/cartoon/standing018-proportions-v1/export/stage.py --source SOURCE --source-sha256 SHA --work WORK
python -B WORK/authoring/export.py --prepare --source BASENAME.png --output WORK/preview --preview-only
```

Inspect preview/export-report.json first. If source centers fit, reproduce that
exact recipe into a separate runtime directory, then run smoke before regression:

```text
python -B WORK/authoring/export.py --recipe WORK/preview/recipe.json --output WORK/runtime
python -B WORK/authoring/test_export.py --phase smoke --recipe WORK/runtime/recipe.json --output WORK/tests --export WORK/authoring/export.py --legacy art/cartoon/walk-expansion-v1/export.py
python -B WORK/authoring/test_export.py --phase regression --recipe WORK/runtime/recipe.json --output WORK/tests --export WORK/authoring/export.py --legacy art/cartoon/walk-expansion-v1/export.py
```

The existing tests check exact original reference replication, repeated output
bytes, fixed placement, source identity, overhang refusal and established filter
parity. Their16 identity/contract guards and four positive cases run in separate
processes. The adapter and original tools preserve all prior sources and recipes.
Technical fit does not approve anatomy, ground contact or color. A new generated
pose needs separate palette calibration if its source colors differ.

## Executed trials

Both v1 and v2 fit at the unchanged registration. V1 passed the existing three
smoke and20 regression cases. V2 was exported/measured for a proportion review;
the full authoring suite was not repeated for that interim draft. The staging
adapter separately passed positive checks before/after seven damaged-input
refusals and seven executed guard removals, each losing the intended refusal.
The original exporter was never modified by those controls.

`trials-v1/` preserves exact recipes, reports and measurements. Foot values are
source pixel-center bounds within the documented foot regions; garment values
are neutral-white cloth interiors rather than exact black outlines:

| Draft | Near sole HD | Far sole HD | Separation HD | Cloth vertical range HD |
|---|---:|---:|---:|---|
| V1 |145.6|136.4|9.2|72.5 to97.5|
| V2 |146.0|138.5|7.5|76.1 to101.4|

Raw alpha ranges0..254 with transparent corners in both drafts; the unchanged
filter produces RGBA runtime alpha0..255. Neither result assigns pose approval.
The preserved measurement/staging probes are snapshots of ignored build scripts;
to rerun them, restore each to its `source` path recorded in the evidence manifest.
