# Profile walking exporter

One shared tool exports one explicitly selected profile frame, 001 through 008.
It is adapted from `front-arrival-v1/remaining-waits-v1/export.py`; the previously
approved exporters are unchanged. The copied filter math is checked against the
frozen 017 exporter on opaque, semitransparent and transparent synthetic pixels.

| Frame | Original canvas | Runtime canvas | Cap target HD |
|---|---|---|---|
| 001 | 48 x 72 | 96 x 144 | [72, 0.25] |
| 002 | 48 x 73 | 96 x 146 | [70, 0.25] |
| 003 | 40 x 76 | 80 x 152 | [54, 0.25] |
| 004 | 40 x 74 | 80 x 148 | [66, 0.25] |
| 005 | 48 x 72 | 96 x 144 | [74, 0.25] |
| 006 | 48 x 74 | 96 x 148 | [70, 0.25] |
| 007 | 32 x 75 | 64 x 150 | [48, 0.25] |
| 008 | 40 x 75 | 80 x 150 | [62, 0.25] |

Use Pillow 12.3.0. Every source is a 1024 x 1536 RGBA PNG, selected by an explicit
basename in this authoring folder. All frames use scale 0.1, translation only,
64 HD pixels of diagnostic padding, premultiplied RGBa with 8x BICUBIC affine
resampling, then LANCZOS downsampling and straight RGBA PNG output. No body fit,
limb warp, hard alpha threshold or per-pose scaling is applied.

Each X target is twice the original first visible row's pixel-edge midpoint.
Y=0.25 is the inherited deliberate filter margin. The generated cap observation
uses its first alpha >=128 row. These are outline measurements, not anatomical
landmarks or new engine anchors. Each configuration pins its own source record
and original native/nearest8 PNG bytes. Full commercial resource files are not
read by this exporter.

Run from the repository root with fresh output directories:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 3 --prepare --source 003-profile-v1.png --output build/profile-walk/export003-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 1 --prepare --source 001-profile-v2.png --output build/profile-walk/export001-new
```

Reproduce the frozen candidates using their explicit saved recipes:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 3 --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/003-v1/recipe.json --output build/profile-walk/reproduce003-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 1 --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/001-v2/recipe.json --output build/profile-walk/reproduce001-new
```

Recipes retain their exact bytes during reproduction. Reports bind the raw PNG,
recipe, exporter, fixed geometry and all output PNG hashes. Alpha >=8 source
centers must fit the original canvas doubled; low-alpha resampling fringe is
retained in the padded output and separately reported. `--preview-only` permits
an overhanging diagnostic and writes no runtime sprite. It does not change the
registration contract or grant acceptance.

For each selected candidate, run smoke before regression with the same frame,
recipe and fresh test directory. Substitute frame 1 and its recipe to test 001:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/test_export.py --frame 3 --phase smoke --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/003-v1/recipe.json --output build/profile-walk/tests003-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/test_export.py --frame 3 --phase regression --mutation-check --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/003-v1/recipe.json --output build/profile-walk/tests003-new
```

Both 003-v1 and 001-v2 passed 3 smoke checks, 24 behavioral cases and 19 executed
mutations. Coverage includes all eight original canvases and cap targets,
explicit source/frame matching, reference identities, fixed placement, refusal
of runtime overhang, preservation of existing output, exact recipe/PNG replay,
and parity with the frozen premultiplied filter. Every mutant executes in a
fresh Python process, prints the mutated source SHA256 witness and produces one
named failure. A run without `--mutation-check` explicitly reports NOT RUN.

The first 001 draft is retained as rejected for runtime fit: its source-center
right edge is 98.75 HD against a 96-pixel canvas. Its real runtime invocation
failed `runtime-overhang:001` and created no output directory. The padded preview
and records preserve the overhang. Root's targeted image edit produced 001-v2,
which fits with bounds [7.75, 0.2, 92.95, 142.6] at the unchanged scale and target.
003-v1 fits with bounds [26.3, 0.2, 64.5, 145.7]. The recorded floating-point
values retain their original precision.

| Candidate | Runtime PNG SHA256 |
|---|---|
| 003-v1 | `5229479f15fa81c6bf3702793f3579d6fd5a39bcad24106113310b0d3e6d4b3d` |
| 001-v2 | `e6af8af8165812e4c010e738e1c5a8f9b9d37cb5d1622acb3a7ab0bb961b9af2` |

Exact final recipes/reports are under `exports/003-v1/` and `exports/001-v2/`.
Test reports and the rejected 001-v1 records are under
`review-evidence/export-tool-v1/`. Runtime PNGs remain in ignored build outputs;
the separate visual review preserves its displayed images.

These checks establish reproducible technical export, not anatomy, motion,
native playback or human approval. The shared 003 slot remains a draft until
the complete 001-008 profile family and its required transition contexts are
reviewed. This tool does not touch the production ZIP, ledger or approval chain.
