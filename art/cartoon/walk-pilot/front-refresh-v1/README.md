# Front-oblique walk refresh

This batch revisits JOHNWALK 024-029 using the approved rear walk's joint,
contact and clothing lessons. The user approved revised 028/029 in standalone
motion and on the native island. Frames 024-027 retain their exact earlier
Calm focus runtime PNGs. The production acceptance records the two replacements
and inherits the other 26 assets' earlier approvals.

The user preferred the third 028 draft and requested complete occlusion of its
far/background arm. [The exact feedback](feedback-key-v1.json) is retained.
`028-occluded-arm-v4.png` carries that correction into `029-heel-fit-v2.png`.
[Continuation provenance](continuation-provenance-v1.json) records all three
follow-up calls and their exact outputs. The user approved the six-pose motion
comparison with "much better proceed"; [the motion acceptance](motion-acceptance-v1.json)
pins its exact drawings and preview. The subsequent native island and arrival
review was approved with "pass- proceed".
The earlier static page is a preserved historical view of draft v3.

## First pose: 028

The original 028 defines the pose; the exact approved raw 024 supplies character
identity and Calm focus expression. The first call deliberately starts from
that design reference rather than inheriting the old 028 leg connection.

The first draft retained side-by-side shorts openings and the earlier leg
connection. The second call changes the near hip, shorts and upper-thigh
overlap. Independent visual review found a more plausible near-hip-to-forward-
thigh connection and ordinary turned shorts, without establishing anatomical
parity. The third call requests a compact forward toe contour for canvas fit.

The third output also moves the heel and redraws pixels outside the requested
foot region. Keep it as a new candidate, not a pixel-preserving edit. The smaller
trailing foot remains a point for human review against original contact depth.

The original's red/white/yellow colors come from the diagnostic dump palette.
Its gray shadow is opaque source artwork, not a reliable sole-contact landmark.
Each of the six retained reference PNGs matches the tracked original-reference
catalog's decoded RGBA hash. Raw Cartoon inputs match the accepted source ZIP.

## Review and export

[The static comparison](review-evidence/key-v1/review.html) presents original,
current production and draft 028 with a whole-pose and lower-body view. All
panels preserve aspect ratio. This does not represent a revised motion family.

That static draft uses the common 0.1 scale, cap-top registration at HD (17.5,0.25),
and the unchanged 64x144 frame canvas. The measured cap is raw (388,40), giving
the same affine as existing 028. Pillow 12.3.0 performs premultiplied-alpha
BICUBIC/LANCZOS filtering. Both alpha-8 source centers and filtered bounds fit;
this does not assert zero faint-alpha fringe. Technical preview PNGs have eight
HD pixels of padding and are not installed in the production archive.

Exact calls, ordered references and output hashes are recorded in
[provenance.json](provenance.json). Generated PNGs are retained byte-for-byte.
Use the recorded Pillow version to reproduce the static review with
`review-evidence/key-v1/helpers/build_key_review.py`. It reads this checkout's
production archive, whose identity must match the recorded baseline when
reproducing this historical comparison.

## Motion review

The [motion comparison](review-evidence/motion-v1/review.html) keeps 024-027's
approved runtime PNG bytes and replaces only 028/029 with provisional exports
of `028-occluded-arm-v4.png` and `029-heel-fit-v2.png`. The far arm is hidden in
both. Each new export uses scale 0.1 and its measured cap outline mapped to the
earlier frame's cap target; no independent silhouette sizing is applied.
Both new drawings fit their original doubled runtime canvases at alpha 8.

The review has one fixed camera spanning every visible pose. The 23 travel
positions end in a clearly labeled 1000 ms diagnostic hold of walking 027.
That hold is separate from the actual native arrival described below. Exact
inputs, runtime/padded PNGs, transforms and hashes are frozen with the page.
Review the larger Cartoon lift in 026/027 against original motion as an
existing accepted artistic difference, not an automatically rejected defect.

Use actual `adsPlayWalk(4,1,0,1)` with direct E-to-A path selection. The 23
travel poses start 028,029,024,025,026,027 and finish 024,025,027; the final skip
is part of the original-derived table. Port cadence is 120 ms per travel pose.
The actual HD standing arrival is mirrored frame 017 at logical (293,243), held
1600 ms, after walking 027 at (300,242). Rear arrival 018 does not apply here.
An E-to-F route exercises the mirrored family. Neither route timing nor this
still reference establishes original-executable playback parity.

## Accepted production scope

[Production acceptance](production-acceptance.json) records the exact island
response, preserves the motion approval and native capture identities, and
lists only 028/029 as newly accepted. The standing arrival remains existing HD
017. The approval covers the displayed E-to-A scene; it does not establish
original anatomical parity or approval of every mirrored route and story use.
Earlier pending-review records and preview pages remain unchanged history.
