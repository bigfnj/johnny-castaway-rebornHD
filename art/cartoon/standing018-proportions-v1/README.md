# Standing018 proportions

Current status: foot-v5 is approved and delivered on main through
[PR #15](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/15).
Production uses the normalized PNG with SHA256
`5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f`.
The [delivery verification](../../../docs/cartoon-connecting-poses-verification.md)
records the combined 43-asset package and tests. The notes below preserve the
earlier checkpoints in order, including pending decisions that were later
resolved. They are not outstanding requests for another art approval.

The user identified a hovering foot in the Front turn color preview, then
proposed a longer torso and lower shorts after comparing the original pose:
"should we re-render with a longer torso and bring the shorts more in-line w/ the original?"

Source-only inspection supports that change. The current Cartoon waistband is
around HD67–70 and the hem around94–95, while original-based targets are80–83
and104–106. Near/far sole bottoms are141/131 versus original147/143. These are
visible garment/outline observations with ambiguous knee anatomy, not a
complete anatomical annotation. Lengthening both exposed legs would retain the
high waistband and can make the near leg disproportionately long.

The edit keeps cap/head/shoulder registration, extends the lower torso, lowers
the shorts and reconnects the pocketed hands and legs to grounded feet. All
anatomy edits use built-in image generation. The existing export keeps fixed0.1
scale and cap target[17,0.25] on the64x154 runtime canvas. No whole-sprite shift
or independent scaling hides the contact problem.

Exact prompts and raw generated outputs are preserved in the versioned
generation-request/result files. V1 moved the waistband and feet in the requested
direction but undershot: near/far source-derived bottoms145.6/136.4HD retain too
much depth separation. V2 moves the neutral cloth interior to76.1–101.4HD and the
near/far soles to146.0/138.5HD. It remains higher than the original garment targets,
but the first native smoke shows the smaller foot reaching the shoreline edge
and the nearer foot on sand. The user accepted these still proportions after
palette matching with "much better proceed". The separate
`human-proportion-approval-v1.json` binds that decision. Transition review and
production integration remain pending. The earlier
skin-color approval remains valid for the unchanged28-pose correction bundle;
the revised018 needs its own color and geometry checks.

The [published still review](http://127.0.0.1:8932/cartoon-standing018-proportions-v2/review.html)
shows original geometry, earlier Cartoon and revised Cartoon at the exact same
native origin. The revised skin base is restored to252,148,88 through a newly
reviewed mask; alpha and geometry are unchanged by that color step. Native Front
turn smoke, full and fresh repeat passed, with2 changed018 displays and34
identical other displays. Local and served viewer checks passed. The exact
question and reviewed artifact identities are in
`human-proportion-review-request-v1.json`; the later approval is recorded separately
above. Native verification now covers the actual front departure,
same-position023 arrival and mirrored rear arrival:164 displays across three
clips,28 scoped018 changes and136 identical other displays. Both new arrival
clips passed smoke, full comparison and fresh repeat; the earlier departure
evidence is reused unchanged. Two altered-pixel controls failed as intended and
restored inputs passed. See `native-review/motion-v1/`.

Visual motion approval remains separate. The waist/hem visibly lower between
walking023 and the new pocketed018 at the same origin. The shorter foot also
appears above the sand in the mirrored rear arrival, a different placement from
the approved still. Neither observation is hidden by camera movement or timing
changes. The new [motion review](http://127.0.0.1:8932/standing018-motion-v1/review.html)
passed local and served smoke/regression; its exact human waist-transition
question is in `human-motion-review-request-v1.json`.

A subsequent supplied-original comparison at the exact mirrored origin
`[1,394,209,18]` confirms that the original foot reaches the shoreline/contact
shadow while the revised smaller foot remains higher. The original includes a
gray shadow that the Cartoon does not; retain that qualification and diagnostic
color limitation. Across the74-display route, all pixels outside018's placed
canvas match. The smaller original foot ends at runtime row143/global561;
the revised foot ends at138/global556,5HD pixels higher. The original gray
shadow is separate contact artwork. Exact captures and qualified measurements
are retained in `native-review/original-mirror-v1/evidence-v1/`.
This contact finding remains open even if the user accepts the waist transition.
Preserve the selected torso and cap registration when correcting the smaller
foot; do not hide the gap by shifting the whole sprite.

The next user feedback confirms that split: "still standing on water, the shorts
look fine though". `human-motion-feedback-v1.json` and
`user-contact-feedback-v1.png` preserve that response. The repeated identical
message is one review event. It accepts the shorts, not every motion context.

Three localized imagegen edits retain the selected torso/shorts and progressively
lower the smaller foot. Fixed-scale source-center measurements are:

| Draft | Smaller sole HD | Larger sole HD | Decision |
|---|---:|---:|---|
| Foot v3 |140.4|146.0|Still too high; retain as draft.|
| Foot v4 |143.1|146.1|Still above clean-sand target; retain as draft.|
| Foot v5 |144.6|146.1|Selected for native contact and color verification.|

The target144–145 allows the Cartoon foot to reach visible sand without relying
on the original gray shadow. V5 keeps the original cap registration and fixed
scale. As with every generative edit, preservation requests do not imply byte
identity outside the edited area: compare the resulting silhouette and motion.
Exact prompts, ordered inputs and raw output hashes are in
`generation-inputs-foot-v1.json`. V5 passed3 export smoke checks and20 regressions.
The freshly annotated color pass restores the selected skin target, with14
negative controls and an exact fresh-process replay. Its alpha remains identical
to the new v5 export, not the superseded v2 geometry.

Raw and final-color native captures now show both feet meeting the shoreline in
the reported front and mirrored positions. All three normalized clips passed
smoke, full capture and fresh repeat:164 displays,28 scoped018 changes and136
identical other displays. Two altered-buffer controls failed as intended and
restored inputs passed. Evidence is in `native-review/foot-v5/evidence-v1/`.
The new candidate archive changes only018 relative to v2; all2593 other payloads
are identical. `preintegration-foot-v5-addendum.json` binds that composition.
The [new foot-contact review](http://127.0.0.1:8932/standing018-contact-v3/review.html)
is published and verified. It opens on the exact mirrored arrival, showing
Original pose, Previous version and Corrected foot with enlarged foot details.
The prominent motion link compares the latter two through all three clips.
Contact crop/link regression, reused164-display motion regression, four focused
source/view negative controls and two stale-HTML publication controls passed;
all208 served files matched. The in-app browser loaded the completed panels.
`human-foot-review-request-v1.json` preserves the scoped question and exact
contact/motion page, record, runtime and candidate hashes. The user subsequently
accepted the correction with "much better proceed". The separate
`human-foot-approval-v1.json` records that decision without rewriting the request
or claiming which individual clip was viewed. Production integration is now in
progress; see the [delivery verification](../../../docs/cartoon-connecting-poses-verification.md).

The new subtree preserves hashed text bytes through Git checkout. A fresh-index
check passed with the attribute, failed specifically on generation-request-v2.json
when that rule was removed, and passed after restoration. Evidence is in
`review-evidence/checkout-v1/`. Record this mutation result in the eventual commit
message; no commit or production promotion has occurred at this checkpoint.
