# Original walking reference

These are technical references, not Cartoon replacements or approvals.
`source.json` binds the supplied-original resource distribution, the dump engine,
all 36 original XPM hashes and the compiled walk table. `metadata.json` records
native canvases, visible bounds, encoded uses and the complete B-to-A route.
Original indices use the port dump palette and index-0 transparency; original
executable palette/compositing is not yet verified. The independent decoder
comparison is documented in [the knowledge base](../../../../docs/knowledge-base/original-image-comparison.md).

The only retained raster references are frame 011 at its native 32 by 78 canvas
and an exact 8-times nearest enlargement. Their RGBA content is reconstructed
from the source XPM; no retouching, smoothing, body fitting or color adjustment
occurs. Both were reproduced byte-for-byte using Pillow 12.3.0. Other frames and
contact sheets are generated locally under `build/`.

From the repository root:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-expansion-v1/reference/extract.py --dump-root <original-dump-root> --output build/cartoon-production-reference/reproduced
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-expansion-v1/reference/test_reference.py --dump-root <original-dump-root> --output build/cartoon-production-reference/verification
```

The dump root contains `report.json` and `dump/BMP/JOHNWALK.BMP.000.xpm` through
`035.xpm`. The current local input lives in the maintenance worktree's
`build/maintenance/original-pixel-reference/`. The original installed resource
files are not reread during ordinary reference reproduction. The externally
created dump's identity and every used XPM byte are checked against the preserved
record before writing output. The generator requires this repository and Pillow;
it imports existing XPM and text-fingerprint helpers rather than duplicating
their validation policy.

Text fingerprints use strict UTF-8 and normalize CRLF and lone CR to LF, while
preserving BOM, whitespace and other characters. Source XPM identity is raw-byte
identity and deliberately does not normalize line endings. Regression checks
include LF, CRLF and lone-CR walk tables and a refused raw-XPM newline change.

The first production expansion is the six-frame `011,019,020,021,022,023` cycle.
Visual inspection of supplied-original pixels shows a rear-oblique torso facing
screen-left. Opposite travel uses encoded horizontal flips. The 23 B-to-A route
draws are all unflipped, at heading 3. Their x coordinates already include the
engine's stored-x-minus-one adjustment; island offsets and render scale are
applied afterward. `120 ms` describes the port's six-tick cadence, not measured
original-executable timing. Background animation may introduce intervening
display captures. The route ends in waiting sprite 018, which is outside this
six-frame artwork family.

For actual motion review, adapt the existing test-only palm API driver to call
unchanged `adsPlayWalk(1,3,0,3)` after selecting and recording a `calcPath` seed
that yields direct `B,A,UNDEF`. This reference work has not executed that capture.
The ordinary `ads` and `ttm` CLI modes do not directly request a walk-table route.

Do not derive foot contact from nontransparent bounds: the original sprites
include a gray ground shadow. The shared cap-top span is only a measured pixel
feature. Anatomical left/right limb identity and precise contact landmarks for
the next family remain unannotated. Frames 033-035 visually form a frontal group
with 010, but they do not occur in the compiled walk table; their complete TTM
sequence and timing remain to be established. Frame 013 is an 8 by 1 canvas with
one visible gray pixel, not a full-body walking pose.

`verification.json` records two smoke checks, ten regression checks and three
isolated guard-removal mutations. Each fresh Python process prints its exact
executed source hash. Each removed guard makes one named refusal check fail;
the normal source is then restored and reproduced. No compiled runtime or
graphical engine test is claimed by this authoring check.
