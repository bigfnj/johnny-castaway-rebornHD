# First Cartoon island scene

The six directional walking poses and the scene concept are approved. The user
replied "its wonderful" to the environment palette and drawing-style review. Keep the
accepted walking PNGs unchanged throughout this scene phase.

## Authoring order

1. After concept review, generate the ocean background and independent sand,
   trunk, canopy, shadow and cloud sprites. Use original assets for geometry and
   the selected concept for style. Register and export at their original sizes.
2. Review a composed static scene with the approved Johnny at native scale.
   Check horizon, ground contact, trunk/canopy join and layer boundaries.
3. Generate all nine high-tide shore frames as separate assets. Their three
   families advance independently, so a three-frame whole-shore animation is
   not a substitute. Test each family cycle and overlapping foam.
4. Package an isolated partial candidate. Run native smoke first, then original
   archive preservation and golden regression. Review the complete scene in
   motion with the actual renderer.
5. Exercise real D-to-E and E-to-D walking, cloud movement, tide/offset fallback
   and island teardown/reinitialization. Run smoke followed by regression for
   each implementation change. Broader environments and animations remain
   separate authoring phases.

## Fixed scene geometry

This first scene is daytime, high tide, no raft or holiday decoration, with
zero island offset, OCEAN02 and cloud 015. Seed 9 selects that state in the
current Windows build; do not assume the same C random sequence on other
platforms. All table measurements are HD pixels on a 1280 by 960 canvas.

| Asset | Origin | PNG size |
|---|---|---|
| SCR/OCEAN02.SCR.png | 0,0 | 1280 x 960 |
| BMP/BACKGRND.BMP/000.png, sand | 576,558 | 560 x 104 |
| BMP/BACKGRND.BMP/013.png, trunk | 884,296 | 48 x 290 |
| BMP/BACKGRND.BMP/012.png, canopy | 730,244 | 304 x 138 |
| BMP/BACKGRND.BMP/014.png, shadow | 792,558 | 208 x 56 |
| BMP/BACKGRND.BMP/015.png, cloud | first reference capture 624,116 | 256 x 72 |
| BMP/BACKGRND.BMP/003-005.png, left waves | 540,612 | 144 x 58 each |
| BMP/BACKGRND.BMP/006-008.png, center waves | 728,638 | 320 x 50 each |
| BMP/BACKGRND.BMP/009-011.png, right waves | 1036,606 | 144 x 64 each |

The ocean contains only sky and sea, with the horizon near y300. Preserve the
shallow sand footprint and its rear crest at y558. Keep cloud, foam, tree and
shadow separate. Occluded areas need independent clean artwork, not crops from
the flattened concept. Sprites use straight alpha; the ocean must be opaque.

Wave families update in separate 160 ms background steps. Center/right
rectangles overlap at (1036,638)-(1048,670), and the most recently updated
family appears on top. Review the actual changing silhouettes and retained
transparency with the corrected clean-background wave compositor.

The engine reuses trunk and canopy as foreground masks during D/E walking.
The duplicate alpha blend was reproduced and fixed during this scene phase:
selected Cartoon palm replacements use premultiplied source-atop on Johnny's
layer. This retains his coverage while placing tree color in front of him,
without repainting the background-only tree. HD and partial packs without palm
replacements retain their existing path. See the verified checkpoint below.

## Scope and acceptance

This is 15 background assets plus six approved walking assets, not full Cartoon
coverage. Shared sand and palm replacements can also appear in other tide,
ocean, holiday and nighttime states. Review those fallbacks explicitly before
shipping a partial pack. PNG colors are unrestricted, but palette-drawn TTM
effects retain their original colors. Night does not automatically recolor
replacement sprites.

Human review supplies artistic acceptance. Asset hashes, smoke and golden
regression establish reproducible inputs and integration. Keep both records.
Production promotion, merge to main and the requested post-merge audit follow
completed implementation and scene checks, not concept approval alone.

## Historical reference preparation checkpoint

The current Windows executable (SHA-256 starting `96ad3efb`) passed eight fresh
normal-CLI full-scene captures: HD and the accepted walking pack at frame budgets
1, 5, 11 and 13. All captures used the verified OCEAN02/cloud015 setup, exited
cleanly at 1280 by 960, and Cartoon differences stayed inside the active Johnny
canvas. The candidate preserved all 2,550 original archive members. After those
smoke captures passed, golden regression matched all 2,452 dump files.

These runs contain original island artwork plus the approved walking sprites.
They establish the baseline for the next assets; they do not validate the
generated island concept as runtime art. The original full scene, accepted-walk
full scene, layer guide and 15 byte-exact source PNGs are available locally under
`build/art-work/island-scene-pilot/reference-v1`, with recorded hashes and setup
in `reference-report.json`. Those captures did not execute behind-palm walking.
The golden regression result was captured in tool session 82686; no separate
persistent regression log was saved by that helper.

The extra palm API probe was compiled but not executed at that checkpoint.
Inspection found that its ignored harness compares a path terminator to -1;
the later probe corrected it to `UNDEF_NODE` (6) and rebuilt before execution.

## Static scene and palm correction verified

The rebuilt actual D-to-E and E-to-D API probe reproduced the double blend:
an alpha-128 red trunk over black changed from red 128 to red 192 outside
Johnny's canvas. An opaque control remained 255. The correction keeps that
background pixel at 128 and also passes a tree-over-Johnny color oracle where
both sprites are partially transparent. This evidence exercises the real
`walk.c` paths through a test driver; it does not claim that the normal story
scheduler selected those paths.

Eight focused palm checks, four full-frame historical parity checks and five
rebuilt code mutations passed. Each mutant produced its expected failure after
the changed driver was rebuilt and executed. The full Windows gate then passed
under both PowerShell 5.1 and 7, with smoke before regression. No new allocation
or retained surface was introduced by the palm correction.

The first 12-asset candidate combined six static island layers with the six
unchanged approved walking poses. Normal CLI captures at frame budgets 1 and 13
and actual D/E API captures passed smoke, followed by all 2,452 golden files.
All 2,550 original archive members were preserved. Its SHA-256 is
`d228cacf63cb7b381dd67b73e71038877b66173bdaa76c645bada16265256ad3`.
The executable used for that checkpoint has SHA-256
`f907574c4863ee45603f17e675218f145e758c2d1f34d519d0a362b91c6686d0`.

Those static captures still contain the nine original high-tide wave sprites.
The complete 21-asset scene must replace those waves and pass its own motion
review. Human runtime scene approval and production promotion remain pending.

The 21-asset candidate subsequently passed fresh normal CLI smoke and all 2,452
golden files, preserving all 2,550 original members. Its exact inputs and SHA-256
are in [the complete native validation record](../island-pilot-v1/review-evidence/complete-native-validation.json).
The static candidate's D/E evidence remains applicable after checking that its
12 PNGs and executable bytes are unchanged. The nine new waves do not intersect
the palm test region. Full-scene motion and human review remain separate checks.

## Complete scene approved

The native motion review captured every display update across the 23-position
walk and its endpoint hold. All nine independently advancing wave phases were
checked against the exact shoreline compositor. Browser controls preserved the
120 ms walking cadence and the separate 160 ms background updates.

The user reviewed that scene and replied "approved, it looks great". This closes
the full-scene visual review for the exact 21 selected assets. The separate
[acceptance ledger](../island-pilot-v1/acceptance.json) identifies the hashes and
preserved full-color poster and GIF. Earlier pending statuses above and in
immutable technical reports describe their historical checkpoints.
