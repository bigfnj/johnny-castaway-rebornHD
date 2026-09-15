# Cartoon walking review

The character design and the six-pose directional E-to-A walking pilot are
approved. After reviewing the full `extended-cartoon-direction-v1` comparison
on 2026-09-14, the user replied "looks good". This accepts the motion and foot
lifts as displayed. The exact six export hashes are recorded in
[`walk-pilot/directional-cycle-v1/acceptance.json`](walk-pilot/directional-cycle-v1/acceptance.json).
Other directions, broader scene contact and production promotion remain pending.

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

## Frame 024 foot-contact revision

The original planted foot faces toward the viewer, with its ankle near
(38, 128), toe near (33, 143), and black sole at y144-145 in the HD canvas.
The first generated pose used a long left-facing profile foot. Correct its
projection rather than lengthening the leg or lowering the approved torso.

The first foot edit improved orientation but left the sole approximately eight
HD pixels too high. A second targeted imagegen edit used the same image with
120 transparent rows added below. That reference retained every existing RGBA
pixel at its original location.

The tool returned the 929-by-1813 reference as an 898-by-1752 image. The diagnostic
export restores the known canvas scale uniformly by 929/898, then applies the
existing 137/1590 drawing scale and approved cap anchor. It does not fit a body
bounding box or stretch limbs. Comparison of the head and torso supported the
same upper-body scale after this correction; regenerated interior lines are
not claimed to be pixel-identical. Canvas dimensions alone would not establish
that an arbitrary future output was uniformly resized.

This revision places the sole near y142.69. A new motion candidate changes only
frame 024; the other five revision-2 images stay byte-identical. At this checkpoint,
foot-contact and motion acceptance were pending. The subsequent direction and
limb-order feedback rejected this profile candidate.

## Direction and limb-order correction

After the foot preview, the user said "well done", then identified a separate
problem in pose 3 of the extended route (sprite 024 at logical 384,216): the
Cartoon places the opposite leg in front and stays too firmly in left profile.
The original presents more of the front of the body and changes its apparent
yaw through the walk. The positive response is not recorded as full motion
approval. At that point only the earlier correction for added body movement
was approved.

The next step was to rebuild the cycle around the original directional poses
and near/far limb relationships, starting with a three-quarter key pose. Original
shoulders, chest, hips and limb occlusions supplied the pose references; the
approved character sheet supplied appearance. A foot-only change could not
repair the incorrect torso angle or limb order. The artwork revisions preserved
the original route and timing.

Inspection of all six original frames found the top 38 HD rows pixel-identical
after their existing horizontal offsets are removed. The route travels (-94,+30)
logical pixels with no flip or camera change. Preserve this steady head direction;
the missing three-quarter presentation is chiefly in the torso, hips and limbs.
In frame 024 the leg descending from the screen-right shorts opening stays in
front at the crossing. The far leg comes from the screen-left opening and its
small foot is mostly hidden just screen-left of the planted ankle/foot.

A fresh directional key was generated from the original 024 pose and the approved
character sheet without referencing the rejected profile drawing. Directional
revisions 4 through 6 establish a front-three-quarter chest/hips and reverse the
incorrect leg overlap. Two targeted edits move the exposed rear foot down and
behind the planted leg. Its clearance still exceeded the original, so that
still comparison asked only for body direction and leg-order review. The revised
six-pose cycle had not yet been accepted or added to production at that checkpoint.

The directional still uses a fixed uniform 0.1 display scale and a measured cap
anchor, not the older generated canvas's 137/1590 scale. This is a new drawing
family, not a normalization inferred from canvas dimensions. The subsequent cycle
uses one documented common drawing scale and preserves the approved absence
of added body popping. The source images carry RGB values under zero alpha that
look like a dark backdrop in the raw image preview; standard alpha composition
shows a clean neutral background without removing or painting source pixels.

After the user asked what to inspect, the review was explicitly narrowed to the
right-hand directional key's front-three-quarter chest and planted-leg overlap.
The user replied "well done". This is recorded as approval of that direction and
leg order, with rear-foot height explicitly excluded from the check. It authorizes
building the six-pose directional cycle, not full motion or production acceptance.

## Directional cycle and full motion approval

The new six-pose family uses the approved directional key as its appearance and
head-placement reference, with each corresponding original sprite supplying the
pose. All selected generated canvases are 1024 by 1536 and use one uniform 0.1
drawing scale. Five retain the visual cap feature at raw (385,42). Frame 028's
last generation moved that feature slightly; its inspected raw (388,40) feature
maps to the same original-frame target. No bounds fitting or foot-based body
alignment is applied.

Targeted foot edits did not reliably produce the requested geometry. Fresh
pose-first generations improved frames 026 and 027, but their approximate rear
foot clearances remain about 11.6 and 11 HD pixels respectively, versus about
four in the originals. Frame 029 retains a larger lift too; a fresh alternative
changed the head and was rejected. These differences were visible in the full
comparison. The user's later "looks good" accepts the foot lifts as seen in this
route; they are no longer an open rejection of the approved gait.

Frame 028's toe initially crossed the original canvas boundary. A focused
foreshortening edit fixed that contour but introduced actual nonzero-alpha
background contamination. A subsequent imagegen background extraction produced
a visually clean candidate with its alpha>=8 silhouette inside the fixed
canvas. Generated alpha is preserved; this does not claim every exterior pixel
is exactly zero or that the character interior reaches alpha 255.

The combined static comparison first cleared these six selected bytes for
isolated native motion testing. The later full comparison received human motion
approval. The existing E-to-A route, 23 poses, camera and 120 ms cadence remain
unchanged. Production promotion is still pending. See
`walk-pilot/directional-cycle-v1` for selected sources, ancestry and the separate
acceptance record, and `BACKLOG.md` for broader scene work.

The selected directional candidate passed native capture smoke on the saved
visual-comparison executable: all six paths loaded, all 23 original draws and
120 ms intervals matched, and playback exited cleanly. Subsequent preservation
checks retained all 2,550 original archive members and matched all 2,452 golden
dump files. The viewer's 69 cropped images, controls, timing and load-failure
feedback passed their checks. A two-panel looping GIF carries the same 23
captures and cadence; its palette conversion is a presentation export, while
the HTML viewer retains the full-color frame stepping.

The current branch executable was checked separately with the normal candidate
archive. Its bounded smoke loaded all six paths, matched the seven original
MJREAD walking draws and exited after 13 frames. Only after that smoke passed,
its golden regression matched all 2,452 files. Production asset bytes remain
unchanged. These results verify integration and preservation; the user's
subsequent full-preview decision supplies the artistic acceptance.

The exact accepted selection is 024v7, 025v2, 026v3-fresh, 027v3-fresh,
028v4-transparent and 029v2 at the recorded uniform 0.1 scale and cap anchors.
The response "looks good" applies to those six exported PNG hashes in the
23-position E-to-A preview. It does not approve other walking directions,
unseen scene interactions or a production archive update. Historical hashed
recipe, provenance and technical evidence keep their original checkpoint status;
the new `acceptance.json` records the later decision without changing their bytes.

## Next scene contact check

After the next island artwork is selected, replay the accepted PNGs unchanged at
their original coordinates against the new sand and tree layers. Inspect planted
feet against the ground, shoreline clearance and intended foreground occlusion
in the real renderer. This is a new scene-integration check, not a reopening of
the user's approved foot lifts or gait.

For future poses, use the established upper-body reference and original ground
contacts. Keep one uniform scale and the original canvas sizes. If a new pose
cannot satisfy upper-body continuity and scene contact through translation,
correct the artwork through imagegen. Do not stretch a frame, crop meaningful
art, change the original trajectory or add interpolated frames to hide a mismatch.

Future motion reviews should retain equal display scale, synchronized playback
and frame stepping. The current six-pose review is complete; broader directions
and animation families require their own checks.

| Decision | Reason |
|---|---|
| Keep the approved character design | The user approved the appearance; the rejection concerns movement |
| Reject the first motion candidate | The longer sequence exposes added whole-body movement |
| Correct registration before redrawing | Existing poses may be usable with consistent placement |
| Check ground contact after alignment | A steady torso alone does not establish a correct walk |
| Accept the directional E-to-A pilot | The user reviewed the full comparison and said "looks good", including the displayed foot lifts |
| Keep scene checks and production promotion separate | Motion approval covers these six PNGs on the reviewed route; broader integration is not yet validated |
