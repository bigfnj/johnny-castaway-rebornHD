# New Year banner attachment draft

Status: superseded draft. After reviewing the native scene, the user preferred
bringing the banner ends inward or extending the palm fronds. The next candidate
uses the original clean banner at a measured 8% smaller uniform scale so its
cloth corners overlap the existing leaves. See `../banner-inset-v1/`. This tied
draft and its frozen evidence remain available for comparison, not approval.

The user accepted the pumpkin and Christmas tree placements in the offshore
scene review. The banner alone needed revision: its two ends looked suspended
in open air. Their marked screenshot is retained as `user-feedback.png`.

The built-in image generator added short inward rope ties intended to overlap
the existing palm fronds. Ordered references, exact prompts and untouched raw
outputs are in `generation-v1.json` and `generation-v2.json`. The full native
reference image is retained. No palm or island pixels were generated into the
banner sprite.

The first edit extended above the existing sprite boundary. The second folded
the pointed tips down, but its fixed-registration export still clipped a few
left and bottom pixels. Both rejected exports retain padded diagnostics and
measurements. The selected technical export is `recipe-v3.json`, using raw V2
at the existing uniform 0.23 scale with a deliberate registration change of
2 HD pixels right and 0.3 HD pixels up. The 304 by 94 runtime canvas contains
every filtered pixel with alpha at least 8; the omitted fringe has maximum
alpha 4, matching the previous export's fringe severity. The padded result
preserves those faint pixels for inspection. No shrink was used to fit it.

The candidate is `candidates/v3/BMP/HOLIDAY.BMP/003.png`. The other three holiday
assets remain byte-identical to V5. This numbered export recipe is not a third
image generation. Prompted preservation does not establish byte-identical
cloth or lettering; the actual result must be judged in the scene.

Export smoke passed before fresh byte-exact replay and regression. The original
V5 source also reproduces its historical padded and runtime pixels. A changed
registration is rejected with the frame name; an executed scratch copy with
that guard removed accepts different banner pixels, then the restored check
passes. The verification files preserve this evidence.

The native comparison described in `scene-plan.md` uses the selected offshore
package on both sides and changes only HOLIDAY003. It checks day, night and a
shifted camera before human review. The wave placement investigation is a
separate draft under `shoreline-repair-v1/integrated-shore-v1/side-fit-v1`.
Production and historical review pages remain unchanged.
