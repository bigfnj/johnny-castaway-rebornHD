# Shoreline and scenery authoring lessons

The Cartoon seasonal pass exposed a geometry defect that isolated sprite
reviews had missed. Full-size clovers revealed missing sand around the island.
This record distinguishes the approved visual direction, completed native
checks and remaining human placement review.

## What the original layers actually contain

Original BACKGRND000 is not the whole island. Original high-tide wave sprites
003-011 also contain ground. The first Cartoon wave prompts removed solid
sand as well as water, leaving a smaller usable beach when those pieces were
composed. Do not infer a sprite's material role from its name alone. Inspect
the original layers together before deciding what each replacement contains.

The geometry guide uses authentic decoded source pixels at their recorded
positions. Its yellow/olive sand and blue/white waves use diagnostic colors,
not a verified original-executable palette. Keep that distinction in review
labels. Never generate an imitation of the original to serve as evidence.

## Preserve feature placement, not only general character

The user wanted a broader smooth coast with the original's two inward inlets.
A left-hand outward jut and an inward notch are different features. The first
revision restored a generic left jut but put its inlet too far left and omitted
the second inlet. The user's arrows resolved the intended geometry: roughly
29% and 67% across the original sand width.

Measure the deepest point of an inlet, not the steep return beside it. A prompt
can request a position while generation leaves it elsewhere. The first two-inlet
attempt still placed the left inlet around 22% across. A local edit moved it to
about 27%; the user approved the resulting complete silhouette. The exact
outputs, ordered references, prompts, comparison transform and approval are in
[smooth-shore-v3](../art/cartoon/shoreline-repair-v1/smooth-shore-v3/README.md).

The user rejected repeated small scallops and supports shaped around individual
prop feet. Preserve a few meaningful coastal features and use broad continuous
curves between them. Review the whole outline beside the original.

## Full-size props and ownership

Shrinking or raising a prop can conceal missing scenery. Restore the intended
prop size and position before deciding where the ground needs correction.
The seasonal V5 recipe retains the approved red-eyed, sharp-toothed, slightly
rotting pumpkin and restores the intended sizes for all four decorations.

A shared ground drawing avoids incompatible joins between separately generated
strips. Assign every ground pixel to one rendered surface. Repeating partial
alpha ground in both the static base and animated waves darkens it and can
make the shoreline change as phases advance.

The approved shape exceeds the original canvas union. Do not shrink it or cut
off the lower coast to satisfy the old rectangle. The integration candidate
uses a larger static canvas with an explicit local offset, preserving logical
scene coordinates. Its native contract and checks must pass before promotion.

## Foam and acceptance boundaries

The original water washes onto sand. Original center phases 006, 007 and 008
progressively reduce exposed sand overall, then phase 006 restores it. Local
water boundaries move unevenly, commonly by 2 to 8 HD pixels. The left and right
families are staggered rather than advancing together. Inspect all original
phases before describing their motion in a generation prompt.

An inverse-ground alpha mask was useful for diagnosing the first offshore-only
proposal, but it erases the intended incoming wash. Do not treat all foam over
sand as a defect. Incoming wave overlays must cross the coast; restore the
unchanged static background before redrawing the current waves so the sand
reappears on retreat without accumulating translucent water.

The [three-way clover study](../art/cartoon/shoreline-repair-v1/integrated-shore-v1/wave-approaches-v1/README.md)
keeps the original source cycle, offshore proposal and incoming-water proposal
separate. Both Cartoon variants retain identical approved sand, full-size
clovers and side waves. This isolates the center-wave decision. Do not infer
approval of either animation from approval of the sand silhouette.

The subsequent explicit choice was "Cartoon: offshore ripples is the winner".
That selects the offshore look and displayed motion for this Cartoon pack.
Original behavior remains useful evidence, but it does not override a reviewed
artistic choice. Keep the wash-over-sand study as an unselected reference and
do not automatically convert the approved ripples back into incoming water.
The [selection record](../art/cartoon/shoreline-repair-v1/integrated-shore-v1/wave-approaches-v1/selection.json)
binds this decision to the actual page, export and native capture hashes.

Prompted phase order is not evidence of actual motion. The incoming drafts
needed reassignment after crest measurements. Compare water coverage as well
as crest height: the lower crest can still have a broader translucent ribbon.
Preserve those limitations in the review rather than claiming exact parity.

Generated PNG viewers may expose RGB under zero alpha as a glow. Inspect a
composite and alpha values before calling that a background defect. The selected
raw ground reaches alpha 254; preserve the actual source and document technical
filtering rather than silently forcing opacity or clearing faint pixels.

Shape approval is separate from approval of the native scene. The selected
offshore package passed native checks with full-size decorations, fitted waves,
low tide, night and shifted scenes, and Johnny's previously accepted contacts:
24 smoke captures followed by 24 exact fresh-process repeats and six negative
controls. The user subsequently accepted the pumpkin and tree placements;
the banner required an attachment correction, then its inset version was approved.
Keep historical previews immutable so an earlier approval remains traceable.

The wider offshore checks also expose existing unstyled low-tide assets:
BACKGRND 001/002 and wave families 030-041. Compare against the earlier Cartoon
scene before calling mixed styles a regression. They already coexist with the
Cartoon top beach; the visible pixelated cloud is also unchanged fallback.
Plan the lower beach and low-tide waves together rather than stretching the
approved high-tide art to cover a different scene state.

## Recheck neighboring layers after enlarging scenery

Pixel identity between two recent previews proves that their assets did not
change; it does not prove those assets still fit an enlarged neighboring layer.
The user correctly questioned the side-wave placement. Those drawings retained
the small island's registration, and the enlarged sand mask removed substantial
parts of their strokes. The newly generated center waves have a separate
registration. Review each family against the final shoreline before applying
one global adjustment.

Reposition the full unmasked source drawing, then recompute its visibility.
Moving an already-masked PNG cannot recover the strokes that were removed.
Use consistent family transforms and enough canvas to retain the complete
drawing. Keep the sand and the approved wave style fixed during that comparison.
The first side-family placement draft required a separate human motion review.
The final combined review received "Looks good, proceed" after the white-foam
appearance and inset banner were approved separately. Its
[selection record](../art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/selection.json)
binds the displayed page and actual native captures. The wave comparison kept
the older banner to isolate the wave decision; combine its selected waves with
the separately approved inset banner when building production.

Match the presentation when comparing motion. The earlier wave review looped
at a close scale; the later decoration review held still images and ended its
motion on a thinner wave phase. Those presentation differences can obscure a
real geometry issue, so check both the pixels and their placement.

Small attachment details also need scene context. A banner end can match the
original sprite rectangle yet appear to float beside a differently drawn palm.
Place ties using actual leaf pixels, inspect the connections at game scale,
and measure generated bounds before export. The banner edit needed a second
generation plus a documented small registration adjustment; a prompt asking
for unchanged geometry was not sufficient proof of fit.

The tie-only banner edit did not settle that visual connection for the user.
They explicitly preferred bringing the banner inward or extending its fronds.
A measured 8% uniform reduction of the original clean banner places both cloth
corners inside existing green leaf pixels, without altering the palm. This is
a requested attachment adjustment, separate from shrinking props to disguise
missing ground. The user approved that inset banner in its native scene review.

Check visible RGB and alpha together across every animation phase. The user
spotted a dark flash in center wave 007: its raw contained 123,597 pixels with
alpha at least 8 and all RGB channels below 100, while neighboring 006 and 008
contained none. Raw preview glow alone cannot establish this distinction.
The generated shading correction contains none of those dark visible pixels.
Preserve its raw output and fixed export transform, then review the full cycle
to verify that the correction fits the adjacent phases.

When reusing an export recipe for edited art, update its raw-source identity
and inherited byte-identity claims as well as the runtime PNG hash. The combined
wave draft initially retained the older 007 ancestry annotation even though
its actual corrected PNG was bound correctly. Preserve the captured historical
input, then explicitly bind corrected metadata to the same unchanged pixels.
Likewise, serialize hash-bound JSON with explicit LF bytes on Windows; a
canonical-content hash and a file-byte hash must not be mislabeled as equal.

## Integrate reviewed components without losing their scope

Several independently approved reviews can share most of a private package yet
disagree on one unrelated asset. Compare named archive members when composing
the final build. A wave review does not silently override a later banner choice.
Keep both decisions, build through the standard art pack tool, and compare the
entire member map to the explicit combined selection. Preserve original HD
`source_sha256` facts separately from raw-generation and accepted-PNG identities.

Reproduce old exports against their recorded input archive. A historical helper
that reads `assets/scrantic_data.zip` implicitly may consume newly promoted art
and produce misleading evidence. Recover the pinned baseline into an isolated
scratch tree instead of replacing the live archive. Final production also needs
the renderer that understands the registered canvases; deploy code and art as a
pair and validate the installed archive beside the executable.
