# Provisional front-walk native review

This is an unpublished technical checkpoint for candidate frames 028 and 029.
It records no human approval and does not promote artwork into production.
The final standing pose remains the existing mirrored HD017 artwork.

The actual engine call is `adsPlayWalk(4,1,0,1)`, direct E-to-A, with island seed
11 and observed Linux path seed 2. Native observation found 23 travel poses at
120 ms, then a 1600 ms arrival hold: 47 displays over 4360 ms including background
updates and the completion witness. The last walking origin is (300,242); arrival
is (293,243). Fixed close-up [560,400,400,280] contains the entire native canvas
union [586,424,852,636], including the caps and feet.

Baseline smoke, full route, and a fresh-process repeat passed. Candidate smoke
then full regression passed: 12 displays differ only inside the placed 028/029
canvases, while 35 are pixel-identical, including all HD017 arrival states.
Every timestamp, actual draw/flip call, walking delay and loaded dependency
matched. Exactly 2 of 2579 ZIP members were replaced; the other 2577 kept their
bytes. Six mask controls and an executed, rebuilt mask-removal mutation passed.
Browser smoke passed before four grouped regressions and two browser mutations.

## Retained and local artifacts

This package preserves the observer, helpers, compiler command and versions,
all 60 protected source/helper/archive identities, actual capture logs and
per-display reports, candidate preparation/recipe/export records, review HTML,
94 exact image hashes, browser validation, and mutation evidence. `evidence.json`
binds every retained file. The broad `art/cartoon/walk-pilot/** -text` attribute
preserves their raw bytes through Git checkout.

The complete local runnable page is
`build/front-native-review/island-review-v1/review.html` in the active worktree.
Its 94 PNGs occupy 125,386,801 bytes and remain in that local directory. They are
not duplicated here. This retained HTML is an exact snapshot and needs those
`images/` files beside it to run. The raw PNG/PPM captures, executable and private
ZIP also remain under `build/front-native-review/`; no full archive or binary
copy is included in this Git package. Copy only `review.html` and `images/` for
later publication, excluding deliberately broken browser-test HTML files.

## Reconstructing after a future art promotion

The baseline archive is recoverable from Git commit
`4551081495eee81e5e5bf2d8b5f00a5619a176a2:assets/scrantic_data.zip`, SHA256
`0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd`.
Use a separate detached worktree at that commit, rather than replacing the
current project's archive. Its production C/header/build inputs must match
every fingerprint in `baseline-v1/build.json` before adopting this capture's
source identity. The candidate's two runtime PNG identities, recipe and export
report are recorded under `candidate-v1/`; recover the matching six-frame export
from the sibling `motion-v1/export` retained with this front-refresh pilot.

Create a new `build/front-native-review/` scratch directory in the detached
worktree. Copy only these nine generator/input helpers from `helpers/`:
`prepare.py`, `capture.py`, `prepare_candidate.py`, `capture_candidate.py`,
`check_candidate_guards.py`, `build_review.py`, `finish.py`, `finish_review.py`,
and `preserve.py`. Do not copy the retained generated outputs `route_driver.c`
or `check_review.py`: `prepare.py` creates the former and `build_review.py`
creates the latter, and both generators refuse an existing output.

`prepare.py` reads the preserved arrival helper and creates the new observer.
Use the established Linux toolchain image with the detached
worktree read-only at `/source` and that new scratch directory writable at
`/out`. The image was available locally as `johnny-platform-cleanup:latest`, ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Its local availability at capture time does not imply a remotely distributed
or permanently available image. Compiler/libc versions and full arguments are
retained; a different toolchain or rebuilt executable needs new identity and
capture evidence, not an assertion that it is the saved binary.

Run preparation, then `xvfb-run -a -s "-screen 0 1280x960x24" python3 -B
/out/capture.py`. This runs baseline smoke before full/repeat. Prepare the private
candidate with `prepare_candidate.py --exports PATH_TO_MATCHING_MOTION_EXPORT`,
then run `capture_candidate.py` under the same Xvfb/container mounts. Run
`check_candidate_guards.py`, then use the toolbox Python with Pillow/Playwright
for `build_review.py` and `check_review.py --review PATH_TO_ISLAND_REVIEW`.
The detailed commands and original artifact identities are in
`scratch-reproduction.md`. Existing output paths are refused to preserve prior
evidence; choose a fresh scratch directory for each reconstruction.

These captures represent port rendering and logical timing under maxspeed.
They do not establish original-executable pixels, physical wall-clock playback,
or a human judgment that the provisional gait should replace the approved art.
