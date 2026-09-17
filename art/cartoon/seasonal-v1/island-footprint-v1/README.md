# Island footprint diagnostic

The Cartoon island has lost some lower shoreline ground that was part of the original wave drawings. This is the main reason the unchanged HD clovers stand over water in the current high-tide scene. The base sand sprite is only slightly smaller; changing holiday coordinates did not cause this difference.

`matched-island.png` and `matched-clover-detail.png` compare actual native renders at the same positions and captured high-tide state. The left uses the supplied original resource pair with all image overrides removed, then restores only the exact existing HD clover PNG. The right uses the current production Cartoon island and that same HD clover PNG. Neither panel uses the new seasonal clover.

| Measurement at 1280 x 960 | Original / HD island | Cartoon island |
| --- | --- | --- |
| Base sand alpha-mask area | 40,384 / 40,372 pixels | 39,357 pixels |
| Base sand visible bounds, local | `[0,0,558,104]` | `[4,1,551,103]` |
| Maximum base-only retreat at the 15 sampled clover endpoints | Reference | 1 pixel |
| Composed lower sand at x=680 | y=649 | y=636 |
| Composed lower sand at x=784 | y=655 | y=650 |
| Composed lower sand at x=894 | y=665 | y=655 |
| Composed lower sand at x=856 / 860, tree / pumpkin center | y=663 | y=655 |
| Sampled stem endpoints below the classified high-tide sand | 1 of 15 | 6 of 15 |

The existing sand recipe uses scale 0.49 instead of 0.5, explaining a modest overall reduction. At the sampled clover endpoints that base change is at most one pixel. The larger local retreat comes from the composed scene: the original wave frames contain opaque yellow/olive ground, while the Cartoon wave prompts explicitly remove the old yellow/gray sand and retain transparent foam. The base sprite alone therefore understates the original island's usable ground.

Holiday 001 remains at logical `(333,286)`, with a `240 x 94` runtime canvas at scale 2. Base sand remains at logical `(288,279)`, with a `560 x 104` runtime canvas. The diagnostic driver changes art selection and tide state, not engine coordinates or rendering. Its holiday overlay is drawn last. These captures bypass calendar/story selection and do not test cargo suppression policy.

The appropriate follow-up is a focused review of shoreline ground coverage, including the opaque ground formerly carried in the wave family. Uniformly enlarging the entire island or moving every future prop would not address the demonstrated local cause. No production artwork, archive, engine source or coordinates were changed by this diagnostic.

## Limits

This is original artwork rendered by the port, not a capture of the original executable. The supplied source pair and decoded-reference archive are hash-bound in `source-identity.json`; the original diagnostic palette is not an original-executable color-parity claim. Both matched panels use the same HD clover to isolate the island difference.

The native stills use Linux/Xvfb, platform seed 11, OCEAN02, day, zero island offset and no raft. The comparison is one deterministic captured wave state; the wave frame tuple was not instrumented. The 12 earlier stills also include explicit low tide. Low tide has additional shore/rock and different wave resources, so its larger shore is a separate case. `measurements.json` searches only rows 558 through 729: low-tide results reaching 729 are censored by that window and are not complete shoreline extents.

The sand measurements use documented diagnostic color predicates and conservative visible stem endpoints. Border/foam colors are excluded. They are inspectable pixel measurements for these images, not a general material classifier or proof that all plant shadows are supported. The original high-wave ground starts much lower than the prior standing-018 upper-shore foot issue, so this result must not be used as the sole explanation for that separate case.

## Retained evidence

`evidence.json` binds the selected images, measurements, source identity, helper snapshots and native records. `measurements.json` contains every sampled coordinate. `images/clover-stem-endpoints.png` shows the endpoints; `images/sand-alpha-overlay-nearest2.png` shows base-only overlap (gray), original-only alpha (pink), and Cartoon-only alpha (cyan). All copied files retain their original bytes.

Native binaries, diagnostic ZIPs, full-screen captures, PPMs and the extracted source PNG collection remain local scratch outputs. Their relevant identities are retained in the summaries. Reconstruct them using `REPRODUCE.md`; they are deliberately not duplicated here. `review.html` is a separately authored presentation and is outside this diagnostic binder.
