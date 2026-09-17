# Shoreline and scenery authoring lessons

The Cartoon seasonal pass exposed a geometry defect that isolated sprite
reviews had missed. Full-size clovers revealed missing sand around the island.
This record separates the approved visual direction from pending native work.

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

Prompted phase order is not evidence of actual motion. The incoming drafts
needed reassignment after crest measurements. Compare water coverage as well
as crest height: the lower crest can still have a broader translucent ribbon.
Preserve those limitations in the review rather than claiming exact parity.

Generated PNG viewers may expose RGB under zero alpha as a glow. Inspect a
composite and alpha values before calling that a background defect. The selected
raw ground reaches alpha 254; preserve the actual source and document technical
filtering rather than silently forcing opacity or clearing faint pixels.

Shape approval is separate from approval of the native scene. The approved V3
outline still requires checks with full-size decorations, fitted waves, low
tide, night and shifted scenes, and Johnny's previously accepted contacts.
Keep historical previews immutable so an earlier approval remains traceable.
