# Shoreline foam contact correction

The user reviewed the continuous-ground draft and marked remaining trouble
spots at the two tips, around front-row clovers and at the lower-right shore.
`user-annotations.png` preserves that feedback. The prior draft was close,
but this was not approval of the finished shoreline.

Layer inspection found retained white foam covering the new sand. Examples
include world HD coordinates 1036,659 (ground alpha 253, foam alpha 255) and
1136,613 (ground alpha 252, foam alpha 255). The ground existed at these spots;
the white marks did not establish that the island needed another enlargement.
The two clover marks have a separate cause. At 757,646 and 785,656 the clover
sprite's own pale contact pads cross the shoreline; the sampled foam alpha is
zero. These require local ground support in addition to the foam correction.

The foam-only V2 draft changes technical layer packing. Its generated ground master,
original registration, ground ownership and full-size V5 decorations stay
fixed. Original foam colors and positions are retained. Its visibility alpha
is multiplied by the uncovered fraction of the ground at the same world pixel:

`visible_foam_alpha = round(original_foam_alpha * (255 - ground_alpha) / 255)`

Opaque ground hides the foam; fully transparent ground leaves it unchanged.
Partial coverage attenuates it continuously, without a hard alpha cutoff.
The packed result is still drawn over the existing ground. This visibility
mask is not an exact equivalence to globally drawing translucent ground over
all foam layers; partial-edge blending changes. Native visual review is needed.
The foam-only V2 trial does not repaint, stretch or shrink source artwork.
No runtime engine change is included.

The subsequent V3 trial pairs that visibility correction with an image-generated
local extension beneath the two clover bases. `generation.json` and the exact
prompt preserve the built-in image edit, its original ground reference and the
user's annotations. The new raw uses the same fixed registration and canvas.
The props retain every pixel and their original positions. V2 stays frozen as
the separate foam-only comparison, so the effect of the local ground edit can
be inspected independently.

V3 moved the coast below the first pad, but the samples at 785,656 and 787,658
still lay on its dark outline. V4 uses one further built-in image edit in that
same small area. `generation-v4.json` and `ground-contact-v4-prompt.txt` record
the second edit. Its raw contact samples are now golden sand; native captures
determine whether that support reads correctly in the scene. Both generated
trials use the unchanged fixed mapping, without fitting or shrinking.

The static comparison is the previous enlarged-island draft versus this foam
correction, with matching full-size decorations. It does not establish approval
of the complete animation, other tides, offsets or character contact.

## Selected V4 review and checks

The current `review.html` compares the first shared-master native draft with
V4. `review-images/source.json` binds each shoreline close-up to its actual
native capture. Both browser images loaded for every decoration choice; the
page was left on clovers for review. All four seasonal PNGs are byte-identical
between the before/after packages, so no decoration was scaled or moved.

In the captured state, the left tip at 569,623 retains its dark shoreline.
The former white cuts at 1036,659 and 1136,613 now show sand. The clover contact
patches at 757,646 and 785,656 now sit over golden sand rather than the dark
coast. Independent visual review found a continuous broader front curve,
without a cut, join or isolated pad-shaped bump. Human approval is pending.

Each version passed exporter smoke before fresh-process replay. V2's executed
wrong-cutoff mutation failed at alpha 253 (expected remaining foam alpha 2,
incorrect threshold yielded 0). V3 and V4 reuse that tested mask and the pinned
fixed-map crop helper. The final native run passed eight smokes followed by
eight exact fresh repeats and three named input controls. Sixty protected
inputs remained unchanged; the isolated capture container was removed.
`native-evidence-v4/evidence.json` preserves the final native records.

The V4 export reports, rather than conceals, 230 nonzero filtered pixels
outside the fixed master crop (72 at alpha 8 or above, maximum 146) and seven
nonzero pixels outside the original sprite-canvas union (three at alpha 8 or
above, maximum 184). No registration adjustment was used to hide that fringe.
The scene review above covers the visible captured result. Every wave phase,
low tide and character contact still need review before production.

Lesson: a larger continuous ground drawing alone cannot fix contact when old
foam still crosses it or a prop contains its own painted ground patch. Inspect
the contributing layers at the marked coordinates before redrawing or resizing.
