# Campfire prop direction corrections

The user rejected 13 pose interpretations in the 25-drawing review on 2026-09-18. This follow-up corrects those drawings and retains the earlier review unchanged as history. It awaits human review; none of the unmentioned drawings are silently marked approved.

[Open the comparison](http://127.0.0.1:8941/campfire-props-direction-v2/review.html). Each row shows the original, the earlier Cartoon interpretation and the revision. The other 12 drawings remain available in [the earlier batch](../campfire-props-v1/README.md).

| Frames | Requested correction |
| --- | --- |
| FIRE2 012/013 | Fish belly-up, eye below body, head left and tail right |
| FIRE2 014 | Belly-up fish with both eyes visible |
| FIRE2 005 | Boot nearly vertical and toe down; laces and red opening to the right |
| FIRE2 009/015 | Boot seen from behind, walking away; heel/back seam toward camera |
| FIRE2 019 | Upside-down remaining piece, sole above and connection below |
| FIRE2 022 | Toe down with foreshortened laced portion and opening toward the viewer |
| FIRE2 006 | Two visible eyes |
| FIRE2 007 | Left-facing squid with aggressive gaze |
| FIRE2 021 | Two eyes looking curiously left |
| FIRE2 024 | Two eyes looking curiously down and right |
| FIRE5 000 | Existing diagonal retained; two eyes looking curiously down and left |

## Why the earlier pass failed

The shared generated keys were useful for colors and materials, but their eye placement and facing were incorrectly reused as pose guidance. The original tiny white patches and black silhouettes contain important eye-count and depth cues. Matching broad silhouette or aspect ratio did not establish whether a boot faced toward or away from the viewer. Earlier boot corrections shortened a front-facing shaft when the required view was the back of the boot.

For the fish, upside-down means a roll of the body while retaining the leftward head/rightward tail trajectory. Moving an eye below an otherwise upright fish is insufficient; belly and dorsal-fin placement must agree with the inversion. Likewise, adding a second squid eye alone does not establish gaze. Pupil direction and where the face sits relative to the mantle and arms must follow the specific phase.

[feedback.json](feedback.json) records the requested semantics per frame. [User screenshots](reference/user-feedback/) preserve the supplied comparisons. [Generation files](generation/) retain exact built-in image-generation requests, untouched raw PNGs and per-version reference/output records. These revisions use the built-in tool, not geometric warping or manual pixel painting. Earlier attempts remain retained.

## Frame 019 and scene limits

[The static scene excerpt](reference/boot019-scene-context.json) places frame 019 last in MJFIRE tag 72, labeled `J eats boot`, after prop frames 022/005/004/016/016. The surrounding draws use Johnny's action frames. This supports interpreting 019 as a remaining boot piece; it does not prove a simultaneous join to another boot sprite. Preserve the southward connection identified by the user and verify its interaction with Johnny during integration. The saved script map also records reused resource slots, so this is static evidence rather than a claim of executed playback.

The page enlarges each drawing independently and preserves raw alpha. The original palette is diagnostic. Scene registration, hand/mouth contact, native timing and full smoke/regression remain deferred to the user's bulk integration milestone. The production archive is unchanged.
