# Connecting poses: preserve motion context and reference roles

This records the delivered 009, 010 and 012 poses, their corrected skin palette,
and lessons from the standing018 contact correction. The user accepted the poses,
then the matched lighter colors, and finally the foot correction. The combined
package is on main through [PR #15](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/15).
Keep those scoped approvals separate and preserve earlier pending-at-capture
records. The [delivery verification](cartoon-connecting-poses-verification.md)
identifies the current production outputs.

## Separate geometry from identity

Each image request used its own supplied-original pose first, an approved Cartoon
view second and an adjacent accepted Cartoon pose third. The original controls
body orientation, support and raised-foot assignment, arm placement and relative
foot depth. Approved Cartoon art controls the cap, expression, beard, shorts and
body proportions. Diagnostic red/white pixel colors and gray ground shadows must
not become skin patterns or anatomical landmarks.

For 009 the identity references were approved 017 and 003. For 010 they were 016
and the accepted 009 draft; for 012 they were 015 and 009. Merely editing a standing
view risks retaining its hands-on-hips pose. State that hands must leave the hips,
and describe their height and depth from the original connecting frame.

## Static approval has a limited scope

The user accepted 009 with "Yes, keep this pose" in the original-versus-Cartoon
comparison. Its exact source, runtime image and page are bound in
`art/cartoon/walk-pilot/connecting-poses-v1/human-pose009-v1.json`.
That approval does not approve the later 010/012 drawings or the complete turns.
Do not rewrite the pending-at-capture evidence after a later approval.

Independent inspection found 010's raised foot somewhat higher relative to the
supporting foot than the original. Correct screen-side assignment alone does not
prove matching step height. Review the complete transition before deciding on a
targeted edit. 012 has subtle rear-view knee and heel asymmetry; inspect its
neighbors instead of forcing artificial bilateral symmetry.

## Registration and transparency

All three generated images are raw RGBA1024x1536 outputs with transparent corners,
retained exactly alongside the actual ordered requests. The established fixed0.1
scale fits each original-derived canvas. Frame010 and012 have small lower-edge
source-center margins, so inspect their soles in actual composition. Neither
per-frame resizing nor hard alpha removal is needed to satisfy the fit contract.
Alpha thresholds measure the contour; the exported alpha retains low-opacity
fringe through premultiplied filtering.

## Eye corrections need their own review scale

The user found the front view cross-eyed. Several full-body requests produced
only subtle pupil movement. An enlarged face study made the gaze easier to
compare. A subsequent request to move each pupil outward by half its width
overshot. The user selected the earlier Face v1 instead, with "faCE v1 is good".
Preserve that exact reference and selection, not the more recent rejected study.
The prepared Face v3 request was never submitted.

Transfer only the approved pupil relationship back to the full sprite; an
enlarged face study is not permission to enlarge the head. Recheck actual output
dimensions, alpha and geometry after every image edit. The study was 1254x1254,
not the requested 1024x1024. Full-body v5's toe drift was enough to fail a tight
registration margin. A requested 15-pixel sole correction in v6 shortened the
shin far more and introduced nontransparent corners. Its restoration in v7 did
not solve the fit. These are preserved rejected attempts, not production art.

Neither a prompt's numeric instruction nor an apparently unchanged silhouette
proves a precise edit. Use measured source bounds and the native motion preview
to validate the actual result. Do not repeatedly alter anatomy to satisfy a
registration offset without first checking whether that offset is an adjustable
engineering margin.

For v5, Y=0.25 was exactly such a deliberate filtering margin. Independent
measurement found an unchanged-fit-guard interval of `-0.05 <= Y < 0.15`.
Selecting Y=0.10 instead moves the entire drawing upward by 0.15 HD pixels;
the complete alpha>=8 source cells and filtered contour fit. This is an explicit
versioned registration decision, not per-frame scaling or a relaxed clipping
check. Preserve the original exporter and failed recipe beside the new version.
The faint remaining alpha1-4 filter fringe stays in padding, as the previous
contract already allowed. Never call this lossless containment of all alpha.

## A turn is not one universal animation

The ordinary ring uses 010,009m,003m,023,012,023m,003,009. Same-spot waiting turns
use different sprites. Review ordinary departures and intermediate waypoints
through the real engine. Do not substitute the earlier standing-ring preview.

Endpoint names do not identify the selected route: seed2 D-toF selects DCF. The
engine's first timer and positive/negative turn traversal are also asymmetric.
Preserve the actual selected path, frame sequence, full-canvas mirroring and
display timestamps. The source interpreter's match with retained C traces is
preparation evidence; independent compiled observation and native captures remain
the runtime checks. Original-binary timing parity is a separate question.

Fifteen statically attributed TTM draws reuse these sprites. Their script contacts
and outcomes remain a separate review surface from the six native walking clips.
See the source bundle's `reference/routes-v1/route-plan.md` for exact sites and
the original SJLEAVES delay caveat.

## Faithful rendering does not prove consistent artwork

The user caught a visible skin-color jump between frames024 and029 of the same
front stride. Both files were already committed. Exact source/export/package
identity checks and a correct renderer preserved the defect; none established
cross-frame material consistency. Do not describe those technical passes as
proof that an animation's colors are artistically correct.

Independent reconstruction matched all28 current/draft Johnny sprites to their
raw generation and historical recipes. Native opaque-pixel comparison found
no unexplained runtime tint. Full-scene matching identified screenshot1 as024
and screenshot2 as029. The user chose the latter's lighter skin tone and
explicitly authorized correction in code while accepting the existing poses.

The [color-correction bundle](../art/cartoon/skin-tone-v1/README.md) preserves
frozen inputs, ancestry and the exact user decision. Correct exported RGB
through a reviewed skin mask, retaining every alpha byte and pixel position.
Use fixed flat-skin sample patches; changing shadow coverage must not change
the calibration. Preserve relative shading and independently check hat, hair,
beard, shorts, eyes and ink. Keep029 as a true unchanged reference control.

Palette consistency belongs in both future generation references and motion
review. A reference image in a prompt is not a color guarantee. Original art
controls pose, support and timing; the chosen Cartoon material reference
controls the Cartoon palette. Color-only edits need new scoped acceptance,
while the earlier anatomy and motion judgments remain useful ancestry.

A skin-color classifier can include antialiased gold cap edges even when the
large mask preview looks reasonable. The first correction draft did this;
explicit original-only cap boundaries fixed it without changing the color
reference. Keep a true unchanged reference case and verify the entire cap,
not only its white center or one gold-band sample.

Independent material annotations can also be wrong. Three initially labeled
chest-hair pixels proved to be neighboring shaded skin at enlarged original
pixel scale. Preserve the failed annotation version and exact coordinate
corrections; do not silently move test samples or relax tolerances to make an
implementation pass. Separate annotations used by the algorithm from independent
test witnesses, and state sparse-sample coverage limits.
