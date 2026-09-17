# Independent static shoreline review

The shared-master candidate resolves the obvious seams found in the earlier three-piece prototype. The native no-prop scene reads as one continuous sand surface. Full-size clover bases visibly contact the beach, including the front row that previously stood over water. The excessive rightward sand extension is gone. There is no obvious static visual blocker in these two inspected candidate captures.

This is an independent visual assessment of one captured high-tide state, not human artwork acceptance, animation approval, low-tide approval or production promotion. The native reports identify the displayed wave pieces as 003, 007 and 009 at their normal origins. No art, capture or production files were changed during this review.

## Comparison with the rejected prototype

The earlier prototype had a squared left cutoff at the exact 003 canvas boundary, a straight top join on the center strip, and an old black coastline visibly remaining inside the added right strip. Those obvious defects are absent from the shared-master scene. A preliminary concern about a glow in the raw RGBA viewer was not borne out by native composition; hidden RGB alone was not evidence of visible haze.

The shared-master no-prop and clover scenes were inspected at their native 1280 x 960 size. Additional nearest-scaled, in-memory crops of the clovers and left-center shoreline helped inspect contacts and joins. These crops were not saved as separate artifacts and did not modify the source captures.

## Original contour comparison

The following samples use world coordinates in the 1280 x 960 render. Values are the lowest classified sand row in each selected column, excluding gray borders and foam. The original uses the supplied resource artwork rendered by the port, not the original executable. Its diagnostic yellow/olive colors and the Cartoon warm sand colors require different documented predicates, so these are approximate material-boundary comparisons rather than pixel-identical shape requirements.

| World x | Supplied-original scene | Rejected separate pieces | Shared master |
| --- | --- | --- | --- |
| 683 | 649 | 651 | 650 |
| 684 | 649 | 638 | 650 |
| 730 | 649 | 645 | 639 |
| 784 | 655 | 659 | 654 |
| 856 | 663 | 666 | 662 |
| 894 | 665 | 669 | 665 |
| 1000 | 659 | 662 | 664 |
| 1137 | 615 | 631 | 620 |
| 1140 | No classified sand | 629 | No classified sand |
| 1150 | No classified sand | 621 | No classified sand |

The abrupt 13-pixel step between x683 and x684 is resolved. Representative front-edge columns are now close to the original footprint. The contour remains stylized: the notch near x730 is about 10 pixels higher, and some right-center samples are 3 to 5 pixels lower than the original. These differences did not create an obvious visual blocker in the inspected stills. They are not evidence that every possible prop placement or animation contact is correct.

The measurement method matches the earlier island-footprint diagnostic: inspect no-prop captures, search rows 606 through 689, classify original sand with `r >= 120, g >= 120, b < 128`, and Cartoon sand with `r >= 95, g >= 65, r > 1.25*b, g > 1.08*b`. This is a bounded diagnostic classifier, not a universal material mask. There was no new native capture or broad test run for this visual review.

## Exact inspected inputs

Paths below are repository-relative. The native captures are local scratch outputs whose identities are retained here and by the native evidence records.

| Input | SHA256 |
| --- | --- |
| `build/shoreline-repair-v1/native-master-v1/captures/candidate/none/smoke/final.png` | `12c9b7fffa7b34242ed8636217ca97c2f9ec55c3a6f852c44825fb4c3fe46f3f` |
| `build/shoreline-repair-v1/native-master-v1/captures/candidate/clover/smoke/final.png` | `924dfbd22488db1fac6fb4390c0976f88c85069cdffdca4c592cfea0c58e35cc` |
| `build/shoreline-repair-v1/native-v1/captures/candidate/none/smoke/final.png` | `fb56818f2007a3665955684591455be000dd15dd759e70759dfbb9dcdd4d78f8` |
| `build/shoreline-repair-v1/native-v1/captures/candidate/clover/smoke/final.png` | `4972e153bf127b6416b98edb5b3c5874abd8a66bd36099c30b3e96bc3c9303eb` |
| `build/shoreline-repair-v1/native-v1/captures/baseline/none/smoke/final.png` | `6e1349d3d299172ced4c48d6502b7b629b0450b0d2dc1202ca4960b654e7813e` |
| `build/shoreline-repair-v1/native-v1/captures/baseline/clover/smoke/final.png` | `b88aaaea269f54b361e814e5e595355a114050d4542bafadf966e4836cbfd406` |
| `build/seasonal-v1/island-footprint/native/original/high/none/final.png` (original contour measurements) | `3b184816e9def71b36d65a57fc5135f7176efebc44959cb79a7236fb99cdad3a` |

The before and after clover captures use the same full-size V5 seasonal props. The review therefore attributes their improved support to the shoreline correction rather than moving or shrinking the clovers. Full wave-cycle continuity and alternate tide/offset states remain outside this static assessment.
