# Cartoon connecting poses: 009, 010 and 012

Draft checkpoint on `art/cartoon-connecting-poses`, starting from main `3af0242`.
The user asked to continue immediately after the profile family was delivered.
Production still contains the 40 previously approved assets.

## Current human checkpoint

The user accepted the first 009 draft with "Yes, keep this pose" in the comparison
of body orientation, relaxed arms, shorts and relative foot depth. The exact
question, answer and selected hashes are in [human-pose009-v1.json](human-pose009-v1.json).
This is a still-pose checkpoint, not native transition or production acceptance.

The user also selected enlarged `010-face-v1.png` with "faCE v1 is good" after
asking for wider pupil spacing in the front view. The exact selection is retained
in [human-face010-v1.json](human-face010-v1.json). This approves the gaze reference,
not a runtime head replacement or the complete native transitions.

The six-clip [native motion review](http://127.0.0.1:8932/connecting-turns-motion-v1/review.html)
is published. The user accepted its poses while reporting skin-color drift.
Corrected-color review and production promotion remain pending. Both local and served
browser smoke/regressions passed, with exact identities for all 291 HTML/image
files. The request and selected hashes are retained in
[human-motion-review-request-v1.json](human-motion-review-request-v1.json).
For the eyes, select Front turn and then 010 under Connecting pose.

The later feedback is preserved in `human-motion-feedback-v1.json`. Independent
matching identifies the disputed screenshots as024 and029 within one stride,
both already present in production. The user selected029's lighter tone and
authorized color-only code edits. The separate
[skin-tone correction](../../skin-tone-v1/README.md) covers all28 current/draft
Johnny sprites while retaining their accepted geometry and all alpha bytes.

The [portable comparison](review-evidence/pose009-v1/review.html) shows supplied
original 009 beside the draft on the exact doubled original canvas. It includes
mirroring and leg detail controls, with approved 017 and 003 identity references.
The local published URL is `http://127.0.0.1:8932/connecting009-v1/review.html`.
The page SHA256 is
`c6d1bd218f35cd5cbf5f8f9baec709fe1cc3c6934e32bfb106b4852fa37c5481`.

## Generation and fit

`009-connecting-v1.png` is the exact built-in image generator output, SHA256
`2ce5bb02e2f965e620a2832545dd8b49dbd2e52301830c18baca645edb48c2a6`.
[The exact request](generation/009-v1-request.json) contains the complete prompt
and actual ordered input paths. [Provenance](generation/009-v1-provenance.json)
binds the input hashes, preserved raw file and output cache identity. The original
009 controls geometry; approved Cartoon 017 and 003 control identity and style.
No model identifier or seed is claimed because the tool did not expose them.

The raw canvas is RGBA 1024x1536. Alpha ranges from 0 to 254 and all four corners
are transparent. Export uses the existing 0.1 scale, premultiplied filtering and
original-derived 80x148 runtime canvas. Cap observation [650,28] maps to
[54,0.25] HD pixels. Source centers at alpha>=8 fit within the runtime canvas.
No independent body fit, limb transform, color key or hard alpha cleanup was used.
The thresholds measure geometry only. Low-alpha fringe remains preserved.

See [export notes](EXPORT.md), [recipe](exports/009-v1/recipe.json),
[report](exports/009-v1/export-report.json) and the executed smoke/regression
records in `review-evidence/export-009-v1/`. Browser smoke precedes the whole-body,
leg-detail and mirrored pixel regressions. Replacing candidate009 with approved017
triggered the named wrong-pose failure. Served-page checks also passed against the
exact local HTML. These checks establish technical rendering, not artistic approval.

## Reconstructing the static checkpoint

Use the documented exporter to reproduce 009 into a new directory. Then run
`build_review.py --export <that-directory> --output <new-review-directory>`.
The builder requires explicit output and refuses an existing destination. Run
`check_review.py --review <new-review-directory> --phase smoke`, followed by
`--phase regression`. `--url` can verify a separately served exact copy.
Use a new directory for another review; preserve this checkpoint's evidence.
The HTML embeds all four images, so it also opens directly without a server.

## Remaining batch

The initial 010 and 012 were generated and exported at the unchanged scale. Each passed
three smoke checks and 24 regressions. The exporter remained unchanged after its
19 executed mutation checks on 009. [Candidate selection](candidate-selection.json)
binds all three raw drawings, exact recipes, reports and runtime/padded images.
That initial selection is preserved as a superseded technical attempt: the user
requested wider pupils in 010. The face study selection above guides a new
full-body transfer; all three require native transition review before promotion.

| 010 attempt | Outcome |
|---|---|
| Full-body v2/v3 | Pupil movement was too subtle; preserved ancestors. |
| Full-body v4 | User requested still wider pupils; fixed-scale export also found a 0.20 HD bottom overhang. |
| Face v1 | Enlarged gaze reference accepted by the user. Actual canvas is 1254x1254, despite the requested 1024x1024. |
| Face v2 | Outward movement overshot; not selected. |
| Face v3 request | Prepared but never submitted because the user selected Face v1. |
| Full-body v5 | Transfers the selected gaze; initial registration leaves a 0.10 HD bottom overhang. |
| Full-body v6 | Fit edit excessively shortened the shin and introduced nontransparent corners; rejected. |
| Full-body v7 | Shin restoration attempt did not solve the fit; retained but not selected. |

Every generated raw output, exact request and ordered input hash is retained in
`generation/`. Requested movement is not evidence of exact displacement. Failed
runtime exports retain padded previews and failure records, not runtime PNGs.

The selected full-body source remains v5. Its original cap Y=0.25 target is an
inherited filtering margin, not an anatomical measurement from the original.
At unchanged scale 0.1, the existing source-center fit condition permits
`-0.05 <= targetY < 0.15`. A versioned Y=0.10 registration moves the whole sprite
upward by 0.15 HD pixels and contains the complete alpha>=8 source cells. It
preserves the drawing, scale, filter and original-derived horizontal target.
Measured source centers become `[4.65,0.15,65.85,147.95]`; filtered alpha>=8 bounds
are `[4,0,66,148]`. The padded image retains 25 outside fringe pixels at alpha1-4.
This does not claim every nonzero alpha fits the runtime canvas. Keep the failed
Y=0.25 recipe and original exporter intact when reproducing historical evidence.

The selected v5 export passed 3 smoke checks, 27 regressions and 21 executed
version2 mutations. The checks reproduce both prior 009/012 outputs exactly and
independently derive the 010 margin. See
[verification](review-evidence/export-010-v5/verification.json) and
[candidate selection v2](candidate-selection-v2.json). Frame010 explicitly uses
`export_v2.py`/`test_export_v2.py`; unchanged 009/012 retain the original tools.
Runtime010 SHA256 is
`fded838277a290a3509868fe19443bd90e2b4277d2e8668ebad7683802be60d4`.

Independent visual review found no clear anatomy or identity blocker. The raised
foot in 010 is somewhat higher than the original relative to the supporting foot;
inspect its continuity in native motion. This is a review observation, not a
measured runtime defect or a reason to alter the engine's pose placement.

The [route investigation](reference/routes-v1/route-plan.md) distinguishes ordinary
departures, intermediate waypoints, travel connectors and 15 separately attributed
scripted draws. Source interpretation matched 116 preserved actual-C traces;
the twelve new prime/travel stages also matched independent compiled observation.
Six baseline native smoke checks preceded full captures and identical fresh
repeats. Their binder is `native-motion-v1/baseline-checkpoint.json`. Candidate
capture now passes for all six clips: smoke, full comparison and an
identical fresh repeat. They contain 36/38/36/50/54/74 displays respectively.
Fourteen of the 288 displays differ only inside the new pose canvases; the other
274, dependencies and timestamps remain exact. Changed-time, outside-canvas and
approved-standing-pixel controls each fail their intended condition. Local and
served browser checks also passed. The later user feedback accepts the poses
while requiring a corrected-color review before promotion.
The [native evidence binder](native-motion-v1/evidence.json) preserves 296 small
files with SHA256
`040a11a36c662cfbbdbb64013c69c5f51acaf3151480a510b792340dee48f65d`.
Its exact replay instructions are in [the native guide](native-motion-v1/README.md).
Same-spot waiting turns use
different sprites and cannot validate these new connecting poses.

The [delivery plan](../../../../docs/cartoon-connecting-poses-plan.md) retains the
remaining native review, acceptance, integration and post-merge audit phases.
No new candidate has been added to the production ZIP or approval ledger.
