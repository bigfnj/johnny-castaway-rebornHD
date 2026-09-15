# First Cartoon island scene

The six directional walking poses are approved. The scene concept is awaiting
human review of its environment palette, linework and visual balance. Keep the
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
Broad translucent leaf or wood interiors may blend twice because the tree is
already in the background. Prefer solid interiors and narrow antialiased edges,
then inspect real occlusion captures before deciding whether code needs a fix.

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

## Reference preparation completed

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
in `reference-report.json`. True behind-palm coverage is recorded separately.
