# Connecting-pose technical export

This family tool supports only 009, 010 and 012. It copies the fixed filter and
refusal contract from `../profile-walk-v1/export.py`; that historical exporter
and its recipes remain unchanged. The render, source, reference, cap-measurement
and guard functions have identical Python ASTs. The new configuration supplies
these original-derived canvases and cap targets:

| Frame | Original canvas | Runtime canvas | Cap target HD |
|---|---|---|---|
| 009 | 40 x 74 | 80 x 148 | [54, 0.25] |
| 010 | 40 x 74 | 80 x 148 | [35, 0.25] |
| 012 | 40 x 73 | 80 x 146 | [39, 0.25] |

Use Pillow 12.3.0 and a 1024 x 1536 RGBA source PNG. Each frame uses scale 0.1
and translation only. X registration doubles the original first opaque row's
pixel-edge midpoint; Y=0.25 is the inherited deliberate filter margin. The raw
art cap measurement uses its first alpha >=128 row. These outline observations
are not anatomical or engine anchors.

Filtering is unchanged: premultiplied RGBa, 8x BICUBIC affine sampling, LANCZOS
downsampling, RGBA PNG at compression 9. The padded diagnostic retains 64 HD
pixels on each side. Alpha >=8 source centers must fit the original canvas at 2x.
Low-alpha filter fringe is reported separately. No fitting, body normalization,
hard alpha mask or pose warp is applied. `--preview-only` permits an overhanging
diagnostic and writes no runtime sprite.

Run from the repository root using fresh output directories:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/export.py --frame 9 --prepare --source 009-connecting-v1.png --output build/connecting-analysis/export009-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/export.py --frame 9 --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/009-v1/recipe.json --output build/connecting-analysis/reproduce009-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/test_export.py --frame 9 --phase smoke --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/009-v1/recipe.json --output build/connecting-analysis/tests009-new
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/test_export.py --frame 9 --phase regression --mutation-check --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/009-v1/recipe.json --output build/connecting-analysis/tests009-new
```

Each of 009-v1, 010-v1 and 012-v1 passed 3 smoke checks and 24 regressions. The
unchanged exporter and tests passed 19 executed mutations on 009-v1. Those
mutations were not rerun for 010/012; their reports explicitly retain this
scope and bind the earlier results. Each mutant
runs in a fresh Python process, prints its actual exporter SHA and produces
exactly one named unittest failure. A run without mutation checking explicitly
reports that omission. Tests independently measure all three original cap
targets, exercise synthetic geometry for all three frames, reject excluded 011
and cross-frame recipes, and compare premultiplied output bytes with the frozen
017 implementation using opaque, partial-alpha and transparent fixture pixels.

The raw 009-v1 cap is [650,28]. Its alpha >=8 transformed source-center bounds are
[6.55,0.20,71.75,145.60], within the 80 x148 canvas. The runtime PNG SHA256 is
`4d9584133241db74595d657a68482e73c91a486a605247ce04aa7b0cd35e7311`.
Exact recipe and report bytes are under `exports/009-v1/`; smoke, regression,
mutation and input/output identities are under `review-evidence/export-009-v1/`.
Runtime and padded PNGs remain in ignored build output and can be reproduced.

010-v1 and 012-v1 were then exported with the same unchanged tool and placement
contract. Their exact recipe/report pairs are under `exports/010-v1/` and
`exports/012-v1/`. Their smoke, regression and verification records are under
`review-evidence/export-010-v1/` and `review-evidence/export-012-v1/`.
For reproduction and tests, substitute frame 10 or 12 and its explicit recipe in
the commands above, using fresh per-frame output directories.

| Candidate | Alpha >=8 source-center bounds HD | Runtime PNG SHA256 |
|---|---|---|
| 010-v1 | [4.60,0.20,65.70,147.90] | `076b7ec10dfb9d62092097285804cc14d1867c2224e1db34fb36417ed81c051b` |
| 012-v1 | [9.70,0.20,67.00,145.80] | `2c07b88265d354106debba83507ba676fd2b82ac64ede4f5634c10f187ed3624` |

All three candidates fit. The 010/012 bottom source-center margins are 0.10/0.20
HD pixels respectively. Their filtered alpha >=8 bounds remain inside the fixed
canvases; padding separately retains any lower-alpha filter fringe. These checks
do not grant anatomy, motion or human approval. The tool never writes the
production ZIP, approval ledger or older evidence.

The nine per-frame reference files are exact copies of
`../front-arrival-v1/ordinary-turns-v1/reference/`. `reference/source-index.json`
binds their origins and copied bytes. Preparation checked the pinned source,
all 36 metadata and trace identities, exact frame rows, native PNG/RGBA hashes,
and original registration. All nearest8 decoded bytes matched independent
row-major 8 x8 pixel replication.

Suggested approved appearance references are 017-foot-depth-v3 for 009,
016-key-v1/016-toe-fit-v2 for 010, and remaining-waits-v1/015-rear-v1 for 012,
all under `../front-arrival-v1/`. The original connecting pose determines the
limbs and stance. 009 is 2 HD pixels shorter with its cap 4 HD pixels left of 017;
010 is 16 HD pixels wider than 016; 012 has the same canvas as 015 with its cap 4 HD
pixels right. Do not copy a waiting pose's transform.

009 is a front-oblique step with hands lowered from the pockets stance and is
used both mirrored and unmirrored. 010 faces forward with a bent/lifted
screen-right leg. 012 faces away with lowered hands and an asymmetric step.
Use screen positions rather than inventing anatomical side labels. Source
visible bounds include ground shadow, so they do not establish foot contact.
Original diagnostic colors do not replace the approved Cartoon palette.

The source records retain their historical preparation-only wording. Standing
000/015/016/017 and the shared 003 profile slot were approved subsequently and
are already in the current pack. 009/010/012 remain pending candidates. Keep 003
byte-identical while reviewing their transitions. No original executable was
run; original color, compositing and timing parity remain outside these checks.
