# Cartoon walking review

The character design in `character.md` is approved. The walking animation is
still under review; character approval does not approve these runtime poses.

On 2026-09-14 the user requested a longer comparison after the initial seven-pose
preview. The extended comparison uses 23 positions from the original E-to-A
walking route, with 120 ms per pose and a one-second final hold. Both styles use
the same engine executable, script coordinates and timing. The longer route is
hosted in an isolated diagnostic archive and does not change the shipped story.

The user rejected the first motion candidate because Johnny's whole body pops
upward during the gait while the original upper body stays steadier.

## First candidate diagnosis

All six generated drawings use one uniform export scale, 137/1590, but the first
registration mixed sole alignment and cap alignment. The original six frames
have their cap top at the canvas top. Generated frame 024 instead placed its cap
8.26 HD pixels below that point, followed by frame 025 at zero. Frames 028 and
029 added smaller vertical offsets of 2.76 and 4.17 pixels. This added movement
to the original scripted motion.

Source sole landmarks were visual estimates with approximately two HD pixels
of uncertainty. They must not be treated as exact engine anchors or used to
justify moving the whole torso between otherwise matching poses.

Frame 026 also used a foot-based horizontal anchor while other frames used the
cap crest. Its cap crest sat 8.89 HD pixels to the right of its original
counterpart, introducing a sideways recoil during the step.

## Registration revision 2

The second diagnostic export keeps the same six generated images and uniform
scale. Every frame now aligns its cap crest and top to the corresponding
original landmarks, with a shared offset of (-0.5, +0.25) HD pixels to retain
antialiased edges. It changes placement only. The original candidate remains
intact for comparison.

This removes the inconsistent anchor offsets, but does not correct pose
geometry. Relative to the approximate original sole positions, the revised
frame 024 sole is about eight HD pixels higher and frame 029 about four pixels
higher; frame 025 is about three pixels lower. These differences need contact
review in the scene.

The user reviewed the synchronized original/previous/revised comparison and
confirmed "The body pop looks resolved" on 2026-09-14. This approves the alignment
correction, not the remaining foot-contact geometry or the full production
animation. Preserve this upper-body registration in subsequent revisions.

The revised candidate passed native smoke checks with six loaded assets,
23 original draw positions and clean bounded playback. All 2,550 original ZIP
members remained unchanged and all 2,452 golden dump hashes matched. Viewer
pairing, equal scale, timing and pause/step controls were checked separately.

## Correction and acceptance

Use a consistent upper-body reference across the cycle and review the feet
against the original ground contacts. Keep one uniform scale and the original
canvas sizes. If the pose cannot satisfy both upper-body continuity and foot
contact through translation, correct the artwork through imagegen. Do not
stretch a frame, crop meaningful art, change the engine's original trajectory,
or add interpolated frames to hide the mismatch.

Compare the original, rejected candidate and revision at equal display scale
with synchronized playback and frame stepping. Inspect cap, face, shoulders,
waist, planted feet and the loop transition. Human motion approval is required
before expanding character production.

| Decision | Reason |
|---|---|
| Keep the approved character design | The user approved the appearance; the rejection concerns movement |
| Reject the first motion candidate | The longer sequence exposes added whole-body movement |
| Correct registration before redrawing | Existing poses may be usable with consistent placement |
| Check ground contact after alignment | A steady torso alone does not establish a correct walk |
| Keep previews separate from shipping art | No walking candidate has human motion approval yet |
