# Rear walking direction: reusable image lessons

This adds to [the original lessons](art-style-learnings.md) and
[Calm focus lessons](art-style-learnings-calm-focus.md). It records the current
rear-walk authoring experience. The user accepted the native island review with
"Yes, keep this walk", including the 8-to-9 transition and the disclosed HD
standing pose. These six additions bring the pack to 27 accepted assets.

## Review joints and transitions together

The first six-pose review exposed weak knee bends and the wrong leg bearing
weight in 020 and 021. Those sprites repeat at displayed positions 9/10,
15/16 and 21/22. Always translate a review position into its actual resource
frame before editing, and preserve the user's exact observations.

Naming a left or right foot alone is insufficient for an oblique character.
Describe which shorts opening the thigh leaves, trace it through the knee and
ankle, and specify which leg overlaps the other. Use the original pose as
geometry authority and the preceding corrected Cartoon pose as a separate
continuity reference. A nice-looking foot attached to the wrong thigh still
changes the gait.

After the knee corrections, the user liked the overall walk but noticed the
raised foot's drop between positions 8 and 9 read differently from the
original. A still-frame improvement does not prove a correct transition.
Track the same anatomical foot through neighboring poses, then assess the
whole sequence at normal cadence. The agreed next step was to retain the
reviewed baseline and check it on the island before changing the gait again.
The user then accepted that in-scene result without another gait edit. Preserve
the observation and this disposition together; acceptance is not established
original-motion parity.

## Remove artifacts without carrying them into the next pose

The revised 020 had small toe-like protrusions along the side of its hanging
foot. The user circled them. A targeted edit removed those bumps while keeping
the intended distal toe group and bent-knee pose. Use a smooth side/heel outline
and one distal toe group as explicit constraints in related prompts. Keep the
annotation and rejected ancestor so the reason for the correction remains clear.

The clean 020 was then a continuity reference for 021. This is actual ancestry,
not a claim that all earlier attempts were used. Exact prompts and ordered
references are in the [authoring bundle](../art/cartoon/walk-expansion-v1/README.md).

## Preserve scale while solving small fit problems

Padded reviews showed the complete sprites even where 020's outer heel and
022's outside foot contours exceeded their runtime canvases. The normal export
refused those drafts. Narrow image edits brought only those foot outlines inward,
after which all six passed the source-center fit check and their filtered
alpha-8 bounds were inside their runtime canvases.

The common scale stayed 0.1, with the same measured cap-registration rule for
every frame. This does not mean generated edits preserved every other pixel:
remeasure registration and inspect identity, body placement and surrounding
poses after every returned image. Preserve both source-center and filtered-edge
results. Neither says the faintest alpha is zero outside the canvas.

## Keep the review itself trustworthy

The original fixed zoom hid part of a pose in narrower browser windows. The
second preview defaults to Fit and was checked at 1280 and 1600 pixels wide.
Full visibility is required before asking someone to judge gait or clipping.

The 23-position diagnostic follows the port's stored route, but it omits the
subsequent waiting frame 018. A native island capture should include that
arrival and its hold, as the accepted review did; 018 is still HD fallback. Separate direction approval,
provisional motion approval, technical fit and actual scene acceptance.

Keep earlier previews, recipes and rejection records immutable. Store later
feedback separately, especially when praise is followed by a specific concern.
Exact PNGs and reproducible exports preserve the result; rerunning an identical
image-generation prompt does not promise identical artwork.
