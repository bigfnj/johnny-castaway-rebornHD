# Profile walking: arm continuity and generation lessons

This records the 001-008 authoring checkpoint on `art/cartoon-profile-walk`.
The complete native gait still requires human acceptance. Production remains
the 32-asset pack until that review and integration pass.

## Arm direction belongs to the whole cycle

The user liked 006's background arm and requested a forward background arm in 008.
They approved the 008-v3 direction with "Yes, use this arm direction". A prior
request to hide the far arm in oblique front 028 does not apply to every walk.
Occlusion depends on the view and phase. Preserve this distinction in later packs.

The far arm swings forward through 008/001/002, recedes behind the body near 003,
swings backward through 004/005/006, and passes behind the body near 007. The
dominant near-arm phase comes from the original poses. Exact far-hand anatomy
cannot be read confidently from every small original image, so the visible
reveals also reflect the user's artistic direction and require motion review.

Review neighboring drawings together before expanding a family. A correct
standalone hand can still appear abruptly, or its depth can reverse, in motion.
Strongest silhouettes belong near the stride extremes; passing poses can hide
the far arm. Do not add a visible second hand mechanically to every frame.

## Image-edit invariants must be measured

Arm-only instructions did not guarantee unchanged pixels elsewhere. 004-v3 moved
the measured cap midpoint from 669 to 686 raw pixels relative to 004-v2. Registration
therefore changed by 1.7 HD pixels at the common 0.1 scale. This is a reason to inspect
whole-body continuity in native motion, not to normalize each drawing separately.

The 008 arm edit introduced 0.65 HD pixels of right overhang despite a previously
fitting foot. A separate image-tool edit brought the forward foot inward. Preserve
both the approved arm-direction ancestor and the fit correction. The requested
20-pixel displacement is a prompt target, not a measured exact movement.

005-v2 returned material background alpha that reached the canvas edges and
corrupted the automatic cap observation. It was rejected and re-edited with the
image tool. Inspect actual alpha, corners and core bounds; a displayed glow alone
does not establish an opaque background. Low-alpha fringe is retained by the
established premultiplied filter. No hard threshold, color key or hand-painted
repair was applied. Native composition is the visual check of the final edge.

## Reusable evidence

The [source bundle](../art/cartoon/walk-pilot/profile-walk-v1/README.md) keeps all
actual raw ancestors, exact calls, ordered input identities, export recipes,
rejection reasons and scoped user decisions. The native review captures actual
route coordinates, full-canvas mirroring and observed logical times. It includes
ordinary 003 departures because 003 is shared with turns. A static 003 approval
cannot approve all of its walking or story uses.

Do not treat the original's gray ground shadow as a sole landmark or infer
anatomical left/right from screen-left/screen-right alone. New styles inherit
these reference and review methods, not automatically the Cartoon scale or arm
interpretation. Use the original to establish geometry, and approved styled art
to establish identity.
