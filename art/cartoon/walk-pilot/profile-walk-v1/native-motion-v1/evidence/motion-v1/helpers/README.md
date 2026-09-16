# Profile native motion checkpoint

These helpers capture two actual public-API routes and their ordinary003
departure variants. They do not replace engine source, grant human approval,
or promote production artwork. See `../route-plan.md` for exact rows, public
calls, mirror behavior and the distinction from original-binary timing.

The preparation recorded source commit
`a7a1fc3bd6cf707616609f77a690c83f2dcb6790`. It requires the complete current
32-asset production archive, SHA256
`096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.
Candidate preparation requires all 2583 existing member payloads to remain
exact. Future
reconstruction after promotion must use a separate checkout with this pinned
baseline, plus the retained helper and candidate-input files. Do not weaken
the baseline guard or substitute a newly promoted archive.

## Locations and prerequisites

Run host commands from the reproduction checkout root. Helpers live directly
under `art/cartoon/walk-pilot/profile-walk-v1/native-motion-v1/`; they do not
require copying into scratch before execution. Host output is always
`build/profile-walk/native-motion-v1/`. In Linux, mount the checkout read-only
at `/source` and that scratch directory writable at `/out`. These are explicit
helper paths. Preparation and capture refuse existing result directories.
Keep failed attempts instead of overwriting them.

The baseline checkpoint is complete under `evidence/baseline-v1/` and bound
by `baseline-checkpoint.json`. That historical record retains the interim
arm-review hold. Work resumed with 001-v3, 002-v2, 003-v2, 004-v3, 005-v4,
006-v1, 007-v1 and 008-v4. The candidate native clips passed smoke, full
comparison and fresh-process repeat. Whole-gait approval remains separate;
the user's 008 arm-direction approval does not approve the complete motion.

The existing Docker image is `johnny-platform-cleanup:latest`, pinned by ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
The host uses toolbox Python with Pillow and Playwright. The image and local
browser installation are prerequisites, not bundled artifacts. Native
execution uses Linux/Xvfb and cannot take over the workstation desktop.

## Ordered reconstruction

1. Run `prepare.py` with toolbox Python and `-B`. It copies the exact production
   ZIP to scratch, derives the observer from the preserved ring wrappers, and
   extracts the separate C trace helper from the retained original trace code.
   `preparation.json` records helper/source identities and every prior member.
2. Run `capture.py` inside the pinned image with `xvfb-run -a -s "-screen 0
   1280x960x24" python3 -B`, using its absolute `/source/art/cartoon/walk-pilot/
   profile-walk-v1/native-motion-v1/capture.py` path. Use `docker run --rm
   --init --network none` and the mounts above. The independent compiled
   `walk.c` observer first verifies every source-table draw/delay contract;
   the full renderer then runs smoke, full capture and a fresh-process repeat
   for each of the four clips. Compilation logs and executable freshness
   witnesses remain in `baseline-v1/`.
3. Reproduce each of the eight selected runtime exports at the repo-relative
   paths in the technical `candidate-selection.json`, with the exact recorded
   recipes and source images. Their exporter smoke/regression is a prerequisite
   to this handoff. Run `check_selection.py --selection PATH` on the host
   for the positive handoff control and both same-canvas 001/005 runtime-swap
   negatives. Then run `prepare_candidate.py --selection PATH`. It binds
   each expected frame to its recipe, source and export-report output hashes,
   and checks every handoff hash and original-derived canvas before creating
   `candidate-v1/scrantic_data.zip`; production is never written.
4. Run `capture_candidate.py` in the same Docker/Xvfb configuration. Each clip
   receives a smoke run before its full comparison against the baseline and
   a fresh-process repeat.
   The executable, public calls, chosen paths, draw origins, flips and every
   observed timestamp must match. Only the eight placed profile canvases may
   differ; approved standing poses and all other pixels remain exact.
5. Run host `build_review.py`, then `check_review.py`. The browser checker
   first tests real Normal playback, then every native display's pixels and
   timestamp, every pose selector/step, fixed-camera crop, departure/arrival,
   Slow, repeat and visibility at1280x900. Screenshots support root's visual
   inspection; they do not constitute user approval.
6. Run `negative_native.py` inside the image without Xvfb and host
   `negative_browser.py`. They execute the current guards with a wrong
   selected path, changed timestamp, changed approved-standing pixel and
   wrong pose-selector mapping. These are input/browser mutations, not
   claims of a rebuilt mutated engine. Their positive controls and exact
   executed helper identities are retained under `negative-controls/`.
7. Run host `publish.py` only after local browser checks and the executed
   controls pass. It preserves an immutable new `profile-walk-motion-v1`
   slug, verifies all served bytes, then repeats browser smoke and regression
   against the served URL. Its configured server root is workstation-local.
   A later reconstruction must adapt a copy to a fresh destination and URL;
   do not overwrite the historical page or mistake its old approval for a
   new candidate's approval. Run `preserve_motion.py` after publication to
   freeze small reports/helpers while leaving bulk media in scratch.

The host command prefix is `& $env:TOOLBOX_PYTHON -B` followed by the helper's
repo-relative path. Pass each command separately. Docker mounts use the
reproduction checkout's absolute host path. No helper downloads tools.

## Baseline results and review semantics

| Clip | Native displays | Logical duration |
|---|---|---|
| Right F-to-C | 34 | 3280 ms |
| Left C-to-A | 62 | 5560 ms |
| Right ordinary003 departure | 36 | 3400 ms |
| Left ordinary003 departure | 64 | 5680 ms |

Each count includes all observed displays, including zero-duration witnesses.
The separate priming call uses the actual120ms first timer; the final000
arrival uses its observed1600ms hold. The observer records the port's logical
ticks while native execution runs accelerated. Normal browser playback uses
the recorded logical timeline, not the accelerated capture wall-clock time.

The viewer defaults to the longer left route and a fixed route-wide close-up.
Both panels share the same camera, native coordinates and full-canvas mirror
pivot. Full island remains available. Each native draw is selectable,
including repeated003 or005. Playback chooses the last display at an equal
timestamp, while pose stepping retains the separate draw calls.

Full capture PNG/PPM files, private ZIPs, executables and browser screenshots
are local scratch artifacts, not tracked in bulk. Final small reports,
helper hashes and immutable evidence bindings are preserved separately after
the candidate checkpoint finishes. Historical technical records remain
pending-at-capture even if a later, separate human record grants approval.

## Completed technical motion checkpoint

The immutable page is
`http://127.0.0.1:8932/profile-walk-motion-v1/review.html`, HTML SHA256
`09f3c4f86f4f79de53cd5fba9eb13b8be1a2012432d360ce50912317a235afbb`.
The private reviewed candidate ZIP is
`d476a447f84dcb996c0ef2e229a18ca5e2b0ad03de57cc538b6933a42318d82c`.
Production still matches the pinned32-asset baseline.

All four candidate routes passed smoke, exact comparison and fresh repeat.
Local browser smoke preceded full pixel/timing/control regression. Publication
then checked235 served files and repeated browser smoke and all four route
regressions. The shared browser checker retains its local-review console
wording when called by the publisher; `publication.json` records the actual
served URL, served identities and final publication result.

Seven deliberately broken inputs reached their named failures: both same-size
001/005 runtime swaps, wrong selected route, changed display timestamp, a
changed approved-standing pixel, wrong pose-selector mapping, and a changed
served HTML byte. Restored positive controls passed. No engine-code mutation
is claimed. The native and browser mutation artifacts remain local and their
small reports are retained in the motion binder.

Root inspected native003/004 screenshots in both orientations and found no
static clipping problem. Whole-gait quality and the updated arm cycle require
the separate human motion decision; this technical checkpoint does not grant it.
