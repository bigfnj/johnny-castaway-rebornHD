# Supplied-original 017 and wait/turn reference

Use `arrival017-source.json` for this batch's facts and hashes. The inherited
`metadata.json` covers all 36 frames and retains the older rear-walk extraction
scope; its recommended rear anchor and selected B-to-A route do not select this
new front-arrival batch.

The raw XPMs were recovered from the preserved `johnny-maintenance` worktree's
`build/maintenance/original-pixel-reference` dump. The existing extractor checked
the original report's source RESOURCE hashes, decoder identity and successful
exit, all 36 exact XPM hashes, and the normalized 489-row walk-table fingerprint
against `art/cartoon/walk-expansion-v1/reference/source.json`. The supplied
commercial RESOURCE pair was not read again and no original executable ran.

The diagnostic palette is the port dump palette. Index 0 is transparent. Original
executable color, compositing and timing parity are unverified. These pictures
are original-index references, not HD proxy geometry.

| View | Size | Transformation |
|---|---|---|
| `native/017.png` | 40×75 | Original RGBA pixels, unflipped |
| `nearest8/017.png` | 320×600 | Exact 8× nearest pixel replication |
| `017-mirrored-native.png` | 40×75 | Exact horizontal reflection |
| `017-mirrored-nearest8.png` | 320×600 | Reflection followed by exact 8× nearest replication |

The previous E-to-A arrival displays the mirrored view. Runtime scale 2 gives an
80×150 canvas. Unflipped first visible row y=0 spans x=[27,31), midpoint 29; mirrored
it spans [9,13), midpoint 11. These are measured cap-outline pixel features, not
engine or anatomical anchors. Gray shadow pixels contribute to the visible
bounds and bottom row, so the canvas bottom is not a foot-contact measurement.

Visual observations: unflipped 017 faces screen-right with a front-oblique chest;
the mirrored view faces screen-left. The elbows extend outward and hands meet
the waist/shorts area. The walker calls its wait drawings "hands in pockets".
The feet are separated in a stationary stance. Do not copy a walking stride,
raised foot or lowered swinging arm from the approved motion drawings. No hidden
anatomical left/right limb identity has been assigned.

`original-wait-turn-family.png` pairs five unique standing views with their
matching turn drawings: 16/10, 17/9, 0/3, 18/23, 15/12. The originals are shown
unflipped, 4× nearest, on a diagnostic background. Mirrored headings are reused by
the table. This lists reference drawings, not a claim that all transitions or
story placements have been traced.

`original017-vs-approved-style-context.png` shows mirrored original 017 beside
exact approved Cartoon 024/028/029 PNGs. The original is 8× native and Cartoon
is 4× runtime, so both use 8× logical scale. Canvases share a top row only; there is
no body fitting or foot normalization. Use the Cartoon pictures for established
style and expression, and the original for this pose's orientation and stance.

Validation passed after extraction: 13 selected original fact rows equal the
preserved metadata; their native RGBA hashes match; each enlarged pixel exactly
replicates its source in an 8×8 block; 017 reflection is exact; all three Cartoon
context PNGs match the current pack hashes without any artwork edits. Output
PNG and decoded RGBA hashes are in `arrival017-source.json`.
