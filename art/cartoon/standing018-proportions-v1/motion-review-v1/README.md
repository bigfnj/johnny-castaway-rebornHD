# Standing018 motion review

This checkpoint compares Earlier Cartoon with Revised Cartoon at the same approved lighter skin target. Only018 changes. It opens the real D-via-C-to-F clip at Normal speed. The final023 and018 share native origin(433,225); the second arrival is mirrored at E. Front turn retains the reported shoreline placement and018 departure.

The browser preserves all164 captured displays across three complete clips. Normal uses recorded timestamps, including the native final wait. No hold, interpolation, scale change, recentering or pose geometry repair is added. All-pose stepping retains distinct native draws even when the PNG repeats. The018 selector lists every018 occurrence; in the mirrored-arrival clip its first018 is an unmirrored priming pose, so use Show arrival or the last018 option for the actual mirrored arrival.

## Review controls and visual limits

- Same-position arrival is the default clip. Compare023 with018 using Previous pose after Show arrival, or watch the full clip.
- Departure from018 starts with the reported D standing placement, then the real turn through003.
- Mirrored arrival contains a different shoreline placement. Show arrival selects its mirrored018; this does not imply that correcting one placement fixes contact everywhere.
- Normal/Slow, Pause, previous/next pose, Replay, Repeat and Full island use the same source captures. Route close-up uses one fixed full-canvas union camera on both panels.

The lower waistband and hem are visibly different from walking023 while the cap stays aligned. Whether this reads as settling or a torso-length snap is a human motion judgment. At mirrored arrival the shorter foot can still appear near or above the local shoreline. Technical PASS is not visual approval. The screenshots do not establish original-executable timing.

## Exact inputs and reconstruction

The baseline is the private43-asset,28-frame color-corrected ZIP with SHA256 `bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf`. The revised ZIP is `7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52`, with018 runtime PNG `21cf94cd90d369b20b6d3b8ef60b7cc2848f919ff828578320502aec9a17c55b`. The other2593 payloads are exact baseline bytes. These are historical inputs, not whichever production ZIP happens to be current after promotion.

First reconstruct the color/export/native prerequisites using `../color/COLOR.md`, `../export/EXPORT.md` and `../native-review/motion-v1/README.md`. Their fixed scratch paths must exist inside a separate checkout at the documented base. `build_review.py` consumes:

- `build/skin-tone/native-review/candidate-v2/<clip>/full` for Earlier Cartoon.
- `build/standing018-proportions/native-review/color-v2/front_arc` for the exact reused front-turn smoke/full/repeat evidence and private ZIP.
- `build/standing018-proportions/motion-v1` for the new arrival smoke/full/repeat reports, preparation, summary and native negative controls.

Then, from the repository root, use the toolbox Python with `-B`:

```text
python -B art/cartoon/standing018-proportions-v1/motion-review-v1/build_review.py --output build/standing018-proportions/motion-review-recreated
python -B art/cartoon/standing018-proportions-v1/motion-review-v1/check_review.py --review build/standing018-proportions/motion-review-recreated
python -B art/cartoon/standing018-proportions-v1/motion-review-v1/negative_controls.py --review build/standing018-proportions/motion-review-recreated --output build/standing018-proportions/motion-negatives-recreated
```

On this workstation `python` in those examples means the executable selected by `$env:TOOLBOX_PYTHON`, invoked with `& $env:TOOLBOX_PYTHON`. The browser checker runs real-timer smoke first, then deterministic regression. It validates all native display pixels, timestamp boundaries, full-canvas crops, every pose and018 occurrence, arrival/departure, stepping, replay, Slow, Repeat, cache release and1280x900 visibility.

Seven fresh-process negatives cover wrong native clip/archive/time, altered viewer time/camera/image-side binding and incorrect018 selector wiring. Each invokes the real helper and requires its named witness/failure. The publication helper also executes three altered-metadata controls for tested HTML, checker and review bindings, with restored positives.

Do not rerun `publish.py` or `preserve.py` against their historical destinations. They preserve an immutable local-server slug and evidence directory. Publishing another candidate needs a new reviewed version and slug, not modification of this checkpoint. Publication itself runs served-file readback, a fresh browser smoke, then full focused browser regression. The published URL is `http://127.0.0.1:8932/standing018-motion-v1/review.html`.

The first publication completed all served checks but its optional screenshot pass timed out: that helper froze requestAnimationFrame yet used Playwright's default animation-frame readiness polling. The retained failed helper documents this inspection-only issue. Explicit50ms polling fixed it. A one-time `--finish-existing` invocation verified the same published bytes and already-passed browser result, then captured the final018 occurrence in each clip. It did not republish, change the page, or repeat the unchanged regression. The ordinary command refuses an existing slug; this recovery switch is only for a byte-identical incomplete publication with its successful served browser report present.

`evidence-v1` retains the exact HTML, reports, helper snapshots, selected screenshots and negative-control logs. Full capture PNGs, executables and private ZIPs remain local-only. Recreate those native captures before serving the retained HTML. The separate binder links the already-frozen native and color evidence, without rewriting their earlier pending-review statements. Human motion approval is recorded separately by the parent workflow.
