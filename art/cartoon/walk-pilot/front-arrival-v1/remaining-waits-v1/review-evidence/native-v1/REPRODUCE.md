# Recreate the complete waiting-ring checkpoint

This note is separate from the byte-bound `README.md`. The 64 retained files
were copied exactly from the completed scratch checkpoint. `evidence.json`
has SHA256 `825f8fb28544f58bdfcc0d396ea5025c58494dd46003805e60019ffa6ec26ed1`;
its `files_sha256` map binds the other 63 files. Human approval is recorded
separately by the enclosing art batch. Hashes establish identity, not approval.

## Source and baseline

Use a separate checkout at recorded source commit
`6c0828eba11ada22b7eab1800bee9475cf04d608`. Compare every source identity with
`baseline-v1/build.json` instead of substituting the earlier `707a20b` art-family
base solely because it predates these drawings. The
production archive must be exactly
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
Do not run preparation against a later archive containing the promoted waits.

Copy the enclosing tracked art references, raw sources, saved export recipes
and exporter helpers into this reproduction checkout when they are absent
from the base commit. Preserve their recorded source/reference hashes. With
Pillow 12.3.0, reproduce the saved recipes into the following fresh scratch
directories. Run each command separately from the checkout root:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/candidate-recipe-v1.json --output build/front-arrival/export-v3
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/candidate-recipe-v1.json --output build/front-arrival/export016-v2
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 0 --recipe art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/exports/000/recipe.json --output build/front-arrival/waits000-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/export.py --frame 15 --recipe art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/exports/015/recipe.json --output build/front-arrival/waits015-v1
```

The prior approved PNGs must match `config.APPROVED`: 017 is `60e3a77a...`
and 016 is `1cb3d624...`. New000 and015 must match `candidate-selection.json`:
`9fef4cef...` and `c74f85cd...`. Those files contain the complete hashes.
Preparation creates a private approved baseline above the old production
archive. Candidate preparation adds only000 and015, leaving every other
member exact. Neither step writes production.

## Scratch staging and command order

The helper root calculation assumes the actual directory layout
`REPRO_CHECKOUT/build/front-arrival/waits-ring-v1/`. Running the helpers
directly from this tracked evidence directory resolves the wrong repository
root. Copy these helpers into that new empty scratch directory:

`config.py`, `prepare.py`, `capture.py`, `candidate-selection.json`,
`prepare_candidate.py`, `capture_candidate.py`, `review-template.html`,
`build_review.py`, `check_review.py`, `negative_native.py`,
`negative_browser.py`, `publish.py`, `finish.py` and `README.md`.

Do not pre-copy generated `native_core.py`, `route_driver.c`, build/capture
folders, private archives, `review-v1`, negative-control outputs, publication
reports or binders. Each stage refuses existing output to preserve evidence.
`prepare.py` generates the first two helpers and the private baseline archive.
It reads the exact prior016 `route_driver.c` and `capture.py`; copy these from
`016-key-v1/review-evidence/native-v1/` into the sibling scratch directory
`build/front-arrival/front-turn-v1/` first. The recorded hashes are in
`preparation.json`. The earlier016 captures and executable are not needed.

Retain the original source trace at
`art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json` and the shared codec
at `art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py`.
Their identities are pinned in the route contract and native build report.

Run host `prepare.py`, then Linux `capture.py`. Baseline capture performs smoke,
full capture and a fresh-process repeat for each direction. Then run host
`prepare_candidate.py`, followed by Linux `capture_candidate.py`, which performs
smoke before full comparison for each direction. Run host `build_review.py`
and then `check_review.py` with Pillow and Playwright. This is the same order
as the commands in the immutable README.

Linux capture uses the existing image `johnny-platform-cleanup:latest`, pinned
by image ID `sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Mount the checkout read-only at `/source` and only the ring scratch directory
writable at `/out`. These are absolute helper assumptions, not optional aliases.
Use `docker run --rm --init --network none`, with the selected command inside:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py
```

The build report retains compiler/libc versions, arguments, native executable
hash and the fresh-build timestamp witness. This note does not promise the
Docker image remains available. No capture opens a workstation window.

## Timing, controls and negative tests

The driver retains a separate `adsPlayWalk(0,0,0,0)` priming call followed by
eight adjacent-heading API calls. The long decreasing-heading ring has108
displays over13,880ms; the short increasing ring has22 displays over1,080ms.
The public wrapper's first timer is6 ticks even when the initial animation
return is80. No timing normalization or original-binary parity is claimed.
Driver, route contract, source trace identity, returned delays, actual times,
origins, flips and every display record are retained here for the timing backlog.

After positive checks, run `negative_native.py` in the same Docker mounts
(plain `python3 -B /out/negative_native.py`; Xvfb is unnecessary). It replays
recorded native outputs through unchanged Python guards, first unchanged,
then with one timestamp and one approved016 pixel changed. These are parser
and comparison guard tests, not a rebuild or rerun of mutated engine code.
Run `negative_browser.py` on the host: it creates a scratch page with the
heading selector shifted one step and runs the exact original browser checker.
Smoke passes before its one expected heading-state failure. The scripts use
hard links for unchanged image data and never mutate the linked bytes.

Expected negative failures, helper execution hashes and retained logs are in
`negative-controls/`. There were no unexpected failures in this ring batch.
The publisher's changed-HTML identity negative is recorded in `publication.json`.

## Publication and omitted large artifacts

The original published page is
`http://127.0.0.1:8932/standing-ring-v1/review.html`, HTML SHA256
`03dee9b661da7dd724bdd652656dc587851a038ad723261d9eb4e3b077152df9`.
The frozen publisher contains that workstation's absolute server root and
refuses to replace its existing slug. A new reconstruction must adapt a copy
to a new destination/URL and rerun served smoke and regression. The original
`--verify-only` checks the existing publication without copying files.

Run `finish.py` after publication and negative tests only while the production
base and source fingerprints are still unchanged. Adapting publication changes
the new binder as expected; it does not rewrite this historical checkpoint.

Full native PNG/PPM captures,147 unique viewer images, private ZIPs, executable
and screenshots remain local under `build/front-arrival/waits-ring-v1/`. They
are intentionally not duplicated here. Recreate them using the steps above;
compare their recorded identities. The reviewed private candidate ZIP hash is
`ee180c8b6aa1e07024132bae808fc4d2fcc136714dd12152468a3c9fc511aa2c`, while
the approved016/017 baseline ZIP is
`16421422b99f7573c005b9525c62364bc7072e6e0008292d062f9ac1a9d0ac0a`.
The binder includes all147 native PNG hashes and all published screenshot hashes.
