# Cartoon shoreline enlargement draft

The user requested local island enlargement so the seasonal props can return
to their intended size and placement. Shrinking and raising those props had
compensated for missing shoreline ground. This work corrects the scenery;
the original engine draw origins and sprite canvases remain fixed.

This is an authoring checkpoint. No production asset has changed and there is
no human approval for the new island yet. Serve this folder and open
`review.html` for the matched native comparison. Both panels use the
same restored-size V5 props, not the earlier reduced decorations.

## Restored props

`../seasonal-v1/recipe-v5.json` restores the original V1 transforms. It uses the
latest approved slightly rotting pumpkin source and exact V1 clover/tree/banner
bytes. Scale and ground anchors are not adjusted to accommodate the new sand.
The exporter reuses the original technical filter directly, avoiding a chain
through the compensating V2-V4 recipes. Its smoke, fresh replay and exercised
rejection controls are preserved in the seasonal folder.

## Rejected separate-strip prototype

`reference/` preserves original geometry, current foam and scene-context guides
for003/007/009. The first003 generation enlarged the drawing relative to its
guide and was replaced by003-v2. `generation.json` records exact prompts,
ordered references and raw outputs. `recipe-v1.json` and `candidates/v1/`
preserve the fixed exports, including cropped alpha rather than hiding it with
a smaller scale. In007,320 meaningful cropped pixels belong to the upper sand
join and57 to the bottom foam. That bottom crop needs correction if this source
is ever reused; it is not an accepted runtime asset.

The actual native observer proved final frames003/007/009 after ordinary
island initialization and the existing same-heading wait. Eight smoke renders
preceded eight exact fresh repeats. The full-size clovers contacted sand, but
visual review rejected obvious joins. At the left piece's x684 canvas edge,
the coast jumped from y651 to y638; the original stays at y649 on both sides.
The center had a straight top join, and the right had a second coastline beyond
the existing outline. This demonstrated that base000 and its ground-bearing
wave pieces must agree as one surface. A technical PASS did not approve the art.

The exact small native records are in `native/evidence-v1/`. Large local captures
remain under `build/shoreline-repair-v1/native-v1/`. No broad glow appeared in
those composites: the apparent raw-image halo was predominantly RGB beneath
zero alpha. Never infer visible haze from the raw viewer alone.

## One continuous ground source

`reference-master/` composes original000/009/003/007 at observed positions and
the equivalent existing Cartoon art. The original guide defines land geometry;
its diagnostic colors are not an original-executable palette reference. The
existing Cartoon guide defines appearance. Both are placed on1536x1024 at an
exact integer scale. The reference contract records the small omitted lower
wave-only fringe, which contains no original yellow/olive sand.

`generation-ground-master.json` retains both built-in image-generation calls.
The first master was too large at its nominal registration and was rejected.
The second put the original geometry first in the reference order, with the
Cartoon image supplying style only. `raw/ground-master-v2.png` is the selected
ground-only draft. It contains no tree, shadow, props or baked foam.

The shared-master export resamples this drawing once at the reference's fixed
mapping. Rectangular crop ownership assigns each ground pixel to000 or one
wave family, avoiding repeated alpha blending. The existing approved Cartoon
foam is retained at its original phase, size and position. Every phase in a
family receives the same ground region, so the restored sand does not disappear
when the foam advances. This is a stable-ground interpretation for the Cartoon
pack; it does not reproduce each original wave's varying painted sand boundary.
No new contour is drawn or thresholded in code.

`shared-master/` records the exact packing recipe and output measurements.
`native-v2/` compares the ten selected replacements,000 and003-011, with the
same V5 props over the earlier island. Production and character PNGs remain
unchanged. Its native observer preserves the engine's actual phase/timing.

The selected master passed eight native smoke captures followed by eight
fresh-process repeats for no decoration, clovers, pumpkin and Christmas tree.
The package changes exactly ten background PNGs; all 2,588 other baseline
payloads, including the full-size decorations, are unchanged. The captured
wave frames are 003/007/009. This verifies the selected still state, not the
other six wave phases. The separate-strip seams are absent in this composite.

`review-images/source.json` binds the eight cropped review images to those
native outputs. The browser loaded both images for all four decoration choices;
the pumpkin, tree and clover comparisons were visually inspected. The page
starts on clovers and shows the same V5 props on both sides. The user called
this draft close and marked five remaining trouble spots. This was not final
approval. [Contact refinement](foam-contact-v2/README.md) preserves the marked
image, identifies old foam over sand and two clover contact-pad intersections,
and prepares the next review without shrinking the props.

The shared-master measurements disclose four source pixels outside the union
of original runtime canvases, with only one at alpha 8 or higher (alpha 74).
They are recorded without shrinking the drawing. Representable ground pixels
reconstruct exactly, and a partial-alpha witness confirms they are composited
once. These measurements do not replace the visual shoreline review.

## Review boundary and next work

Judge the whole island silhouette, continuous sand appearance and full-size
prop contact in the composed scene. A static approval must remain distinct
from complete animated-scene acceptance. Before production, review every wave
phase, low-tide scenery, shifted/night scenes and Johnny's previously approved
standing/walking contacts on the new base. Original low-tide shore001,rock002
and waves030-041 still use HD fallback, so the changed000 boundary needs a
separate low-tide check.

Lessons for later style packs: inspect material content across adjacent sprite
layers before authoring; keep original prop registration as the target; use a
shared drawing where layers form one surface; preserve alpha by assigning each
ground region once; and review the native composite before accepting separate
sprites. An independently attractive strip is not necessarily a compatible
island edge.
