# Profile arm cycle: revised direction

Recorded 2026-09-16, before the next arm checkpoint. The user said "the background arm there fits" about 006-v1 and requested a background arm on the 008 stride too, adding "maybe we need to revisit the arm on these walking poses". Retain 006-v1's visible rear arm. 006-v2 was an arm-removal experiment and is not the selected direction. The request overrides the earlier blanket instructions to hide the far arm in every strict profile pose.

This document records visual recommendations, not new artwork acceptance. Root is preparing a forward far-arm revision from 008-v2 for human review. No result of that revision is assumed here. The existing 003-v2 approval remains the accepted static tucked-foot checkpoint; its exact file SHA256 is `7e177359c1b20c185050e7c7ee9f3bef18bba1190751cf4f47bd54fc97d47f5f`. This document does not separately approve 001, the other complete poses, native motion or production promotion.

## Evidence and interpretation

The original 001-008 native and nearest8 references establish the dominant visible arm's screen-space swing: behind the shorts in 001/002, near vertical in 003, ahead in 004/005/006, near vertical again in 007, behind in 008. At the original scale, overlap and diagnostic checker colors do not unambiguously identify a separate far hand in every pose. An indistinct original silhouette is not evidence that Johnny has no far arm, nor that a more detailed drawing must hide it completely.

The proposed far-arm visibility below is an artistic continuity judgment guided by the user's preference and opposing arm swing. It is not a claim to have recovered hidden original anatomy. "Near" and "far" describe drawing layers; neither identifies anatomical left or right. All directions below refer to the unflipped, screen-right-facing image. The whole sprite is mirrored by the engine for travel left.

## Review table

| Pose inspected | Original dominant-arm phase | Current draft | Recommendation and basis |
|---|---|---|---|
|001-v2 | Behind the shorts at the wide-stride extreme. | One visible arm reaches back; no clear forward far hand. | Show a forward far forearm/hand around the front of the torso/shorts. This should be the clearest forward reveal in this half-cycle. Artistic continuity from the requested008 change, not an original-pixel mandate. |
|002-v1 | Behind the shorts, returning toward the middle phase. | Rearward near arm; far arm hidden. | Show a smaller forward portion than001, returning toward the torso. Avoid a large isolated hand that disappears abruptly in003. Artistic interpolation between still poses, without adding animation frames. |
|003-v2 | Arm low beside/over the shorts, near the passing phase. | Near arm hangs down; far arm is occluded. | Keep the approved pose initially. Near/full far-arm occlusion is plausible at this phase. Only expose a small edge if full-cycle motion shows an abrupt disappearance. Any later pixel revision requires its own record and review. |
|004-v2 | Hand ahead of the shorts as the forward swing opens. | Forward near hand; no distinct rear far elbow or hand. | Add a modest rear far-arm portion, establishing its emergence before005. A narrow edge can suffice; there is no need for two fully exposed hands. Artistic continuity toward retained006. |
|005-v3 | Clearest forward near-arm swing. | Forward hand well ahead of the body; far arm hidden. | Show the clearest rear far-arm reveal of this half-cycle, with a natural elbow and partial forearm/hand as occlusion permits. Removing it entirely here but revealing it in006 risks a visible one-frame appearance. Artistic continuity judgment. |
|006-v1 | Near arm still forward, returning from005. | Rear far elbow/arm arc is visible behind the back; near hand remains forward. | Retain this direction as requested by the user. Use its limb thickness, layering and warm shading to guide the smaller004 reveal and larger005 reveal. User-directed preference; no full-cycle approval implied. |
|007-v1 | Arm lowers beside the body as the swing crosses the middle. | Near hand hangs beside the shorts; far arm mostly hidden. | Full or nearly full occlusion is plausible. Start with this pose unchanged, then inspect006-to007-to008 so the far arm passes behind the torso rather than seeming to vanish. Do not force an extra hand merely for frame-by-frame completeness. |
|008-v2 | Near hand behind the shorts as the rearward swing opens. | Rearward near arm; no forward far arm. | Add the forward far forearm/hand requested by the user, smaller than or approaching001's reveal. Show a believable connection from the hidden far shoulder, behind torso/near arm, emerging toward screen-right. This is the next human checkpoint. |

Far-arm exposure should follow a continuous sequence: forward reveal around 008/001/002, occlusion near 003, rear reveal around 004/005/006, occlusion near 007. Its silhouette should not be copied identically across frames. The torso can conceal the upper arm while a forearm or hand becomes visible beyond its outline. Keep a continuous two-arm construction without adding a detached hand, shoulder bump, third arm or a hole through the torso.

## Scope of edits and review

Use the retained 006-v1 arm as the preferred layering example and the upcoming 008 revision as the forward-arm checkpoint. Keep the originals authoritative for the existing near-arm phase and pose, and preserve the established leg geometry, shorts, character identity and uniform drawing scale during targeted edits. Do not claim that a prompt preserved other pixels exactly; measure and compare each resulting image and re-export it at the fixed original-derived placement.

After the user accepts the arm treatment, prioritize the missing counter-swing in 001 and 005, then the smaller 002/004 transitions. 003/007 can remain occluded unless the actual cycle shows a visible discontinuity. Review the native sequence, including the 008-to-001 wrap and 006-to-007-to-008 transition, at Normal speed before deciding whether extra exposure is needed. A static judgment alone cannot establish smooth arm motion.

## Inspected snapshot

Paths are relative to this bundle. These hashes identify the drafts reviewed, not final selections or acceptance. Original reference authority is `reference/source-index.json`, SHA256 `7173a1cbe9412e65f79e574589b3d83e05af506d55082cf465f6d813bc99c460`.

| File | SHA256 |
|---|---|
|001-profile-v2.png |`ad08c3484d41f200efac23f788d6744742d21efb0108950fa69c604e33b4cf80` |
|002-profile-v1.png |`71696dff24446e6615ed254e29450f9385d0e264270f4865bc700619eea9a90b` |
|003-profile-v2.png |`1bb60fad5ec369fd5f5f097d98e3d5b57ee81d6766f2ecdb6b2f75f681719d9e` |
|004-profile-v2.png |`d2630646f56767513200841bc6c4c266fe8728bf8637dca53c335b4b0884fe93` |
|005-profile-v3.png |`8a1e821727d7343b22fd93b3a64d55118bef7f641f6f0617e155e3003a387cdd` |
|006-profile-v1.png |`90627d13750610cd7433e698a0cd186692fd23d7ded762ec73ae9dde36acd067` |
|007-profile-v1.png |`5df49fcd711c6a88400cba7e0fd475ed3549e19ac2fda9989a8361c99f9e675c` |
|008-profile-v2.png |`173e012121ef09775114e9aaa3bc72c45946b574d50c484a781b84917e6aaebf` |
|006-profile-v2.png, removal experiment not selected |`ce67c620e40b74f6c0f152c69e9d443276bd58d27c243772339204d2571ba8d4` |

Earlier call files retain their actual prompts, including the now-superseded far-arm hiding instructions. No historical approval, prompt, source reference, candidate PNG or production file was changed for this review.
