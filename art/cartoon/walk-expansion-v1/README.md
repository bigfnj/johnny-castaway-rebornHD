# Walking expansion: rear direction

This begins the bounded [production plan](../../../docs/cartoon-production-plan.md).
The production pack now contains 27 approved assets, including this six-pose
family. Raw images and earlier drafts remain authoring inputs; only the six
recorded runtime exports are installed. Their
[production acceptance](production-acceptance.json) preserves the exact review.

The first new family uses `JOHNWALK.BMP` frames 011 and 019 through 023. In the
original B-to-A route, these form 23 unflipped draw positions. Johnny shows his
back and outer shoulder while walking toward screen-left, with a different
body direction from the accepted front-oblique 024 through 029 cycle.

## Directional key

`011-direction-key-v1.png` was generated on 2026-09-15 with the built-in image
tool. The [exact prompt and ordered references](prompts.json) preserve the
supplied-original pose input and the accepted Calm focus character key.

The user approved the cap, beard and body direction on 2026-09-15 with
"looks good yes". Foot placement, complete gait, canvas fit and in-scene
rendering remain separate work. Do not infer acceptance of other poses from
this directional-key review.

The returned image is preserved unchanged, SHA256
`c3e2caba0cb2692cc9845c5f72fa69fa20f264d12552b692e41b5d4425b5a407`.
It is 1024 by 1536 RGBA. Its alpha ranges from 0 to 254; the alpha-8 silhouette
fits within (312,45)-(729,1476), while fainter alpha extends farther and reaches
the bottom edge. There is no exported runtime sprite or chosen affine yet.
The gray review image is a technical alpha composite, not an edited source.

Independent visual inspection finds the rear-oblique direction coherent, but
the generated lifted foot is higher and farther from the planted foot than
original 011's small tucked lift. Keep that discrepancy explicit when preparing
the actual cycle. Directional-key approval would not resolve this pose issue.

Original reference images use the port's diagnostic dump palette and index 0
transparency. They preserve decoded original geometry but do not establish
original-executable color or timing parity. In particular, the original frame
contains a gray ground shadow, so its lowest nontransparent pixel is not
automatically the foot-contact location.

Keep the approved Calm focus artwork and its documented reversed-leg artistic
difference intact. Any corresponding difference in this new direction must be
reviewed separately; historical acceptance does not transfer to unseen images.

## Subsequent motion and runtime preparation

The key review above is historical. The six-pose family now has a common-scale
export recipe and two preserved motion previews. The first motion review was
rejected for the leg arrangement and insufficient knee bend in 020 and 021,
which repeat at review positions 9/10, 15/16 and 21/22. Exact feedback is in
[motion-review-v1.json](motion-review-v1.json).

The next pass corrected the knee bends and removed extra toe-like bumps from
the side of 020's raised foot using the user's annotated crop. The second
preview was retained as the provisional motion baseline for an island review. The
user subsequently noted that the foot's downward movement from positions 8 to
9 reads differently from the original. We agreed to assess that transition in
the island scene before redesigning the gait. See
[motion-review-v2.json](motion-review-v2.json), which preserves that interim decision.

The current runtime candidate uses `020-heel-fit-v5.png` and
`022-foot-fit-v4.png` for tiny foot-edge corrections to that baseline. The other
four sources are unchanged. All six pass source-center canvas fit and have
filtered alpha-8 bounds inside their canvases at the common scale 0.1. These
technical results alone do not approve animation or ground contact. The user
then reviewed the native island sequence, including the 8-to-9 transition, and
answered "Yes, keep this walk". That final decision is recorded separately in
[production-acceptance.json](production-acceptance.json). Waiting frame 018 is
outside this family and remains HD fallback, as disclosed in the review.

Generation history is split into the original [key prompt](prompts.json),
[first cycle](cycle-prompts.json), [knee and toe corrections](knee-correction-prompts.json)
and [canvas-fit corrections](fit-correction-prompts.json). The returned source
PNGs are kept unchanged. [Tooling notes](tooling-notes.md) explain reproduction
and preserve the earlier preview-only overhang results. Useful lessons for the
next style are in [the rear-walk record](../../../docs/art-style-learnings-rear-walk.md).
