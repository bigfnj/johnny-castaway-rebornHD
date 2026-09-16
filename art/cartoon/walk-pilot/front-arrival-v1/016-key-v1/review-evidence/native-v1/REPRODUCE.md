# Reconstructing the two-direction016 checkpoint

This package preserves57 hash-bound small helpers/reports/logs/HTML files plus
their exact `evidence.json` binder. This note is separate from those frozen
bytes. Statements that016 approval was pending describe the capture stage;
the later human decision is recorded separately by the authoring review record.

The published HTML identity is
`6705ac2d85d4a99bfb2c6be0d5cdbf432c8d94ac641edb7e3168d10f17c591d2`.
The new016 runtime identity is
`1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92`.
Both native directions, their separate priming calls and exact original draw
positions/timestamps are retained. The page needs68 native PNGs under `images/`;
these full images, raw PPMs, private ZIPs and native executable remain local
scratch artifacts and are not included here.

## Production base and approved017 stage

Use a separate checkout of the preparation commit
`c56f76871d9950933913912f5828c1499b1fa4a1`, or a checkout whose protected
production source/header/build identities exactly match `baseline-v1/build.json`.
The production archive must remain SHA256
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
Do not replace a later current archive in place merely to recreate this review.

First recover approved017 from its retained authoring recipe to
`build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png`. Its SHA256 is
`60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1`.
The standing017 native checkpoint is at
`art/cartoon/walk-pilot/front-arrival-v1/review-evidence/native-v1`.
Follow its `REPRODUCE.md` to stage/recreate the prior observer and packer at
`build/front-arrival/native/`. The turn preparation reads the prior
`route_driver.c` and `prepare_candidate.py` from that scratch location.

The new016 authoring inputs were added after the preparation commit. Copy this
retained016 authoring bundle into the separate checkout when necessary without
changing protected production inputs. Its exporter/recipe and original
reference inputs must reproduce the runtime hash above. The recipe SHA256 is
`47806f8ae481735023238a0afa341eff393169cb4fb2134005ff55ecf4382bca`.
The recorded exporter requires Pillow12.3.0.

`prepare.py` creates a private baseline ZIP by adding only approved017 to the
production archive. All2,579 production members remain unchanged. That private
baseline has SHA256
`795c2ad7fda8586f68d07714e36dc85ec3d2954fd25cd8b3d1c52d94dc55327b`.
The new016 candidate adds one more member, preserving all2,580 baseline members.
The passing candidate ZIP has SHA256
`16421422b99f7573c005b9525c62364bc7072e6e0008292d062f9ac1a9d0ac0a`.

## Scratch placement and command order

The host helpers infer the repository via `Path(__file__).parent.parents[2]`.
Use a fresh directory at this exact depth:

```text
REPRO_CHECKOUT/build/front-arrival/front-turn-v1/
```

Stage `prepare.py`, `capture.py`, `prepare_candidate_helper.py`,
`capture_candidate.py`, `build_review.py`, and `check_review.py` from this package.
Keep the complete frozen package elsewhere for comparisons. Do not pre-copy
generated `route_driver.c` or `prepare_candidate.py`; their generators refuse
existing targets. Do not copy baseline/candidate/review output directories into
the new scratch directory. All capture outputs are deliberately preserved on
failure, and fresh runs must use fresh output locations.

Host commands:

```text
python -B build/front-arrival/front-turn-v1/prepare.py
python -B build/front-arrival/front-turn-v1/prepare_candidate_helper.py
```

Use the existing Linux toolchain image `johnny-platform-cleanup:latest`, ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
This was locally available at capture time; permanent or remote availability is
not implied. Compiler/libc versions, full GCC arguments and all protected
source identities are in `baseline-v1/build.json`. A changed toolchain or
executable requires new capture evidence, not an assertion that it is the saved
binary.

Run Docker with `--rm --init --network none`. Mount the checkout read-only at
`/source` and the new scratch directory writable at `/out`. Those absolute mount
aliases are hardcoded by the capture scripts and are part of the recorded
compiler command. Use Xvfb so no workstation window opens.

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

This runs smoke, full capture and a fresh-process exact repeat separately for
A1-to-A7 and A7-to-A1. It observes actual native calls, not synthetic poses.
Each native priming call lasts120ms in the port. The requested turns then last
1840ms and1720ms respectively; the former repeats017 before its final hold.

Reproduce016 with the retained exporter, for example:

```text
python -B art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/candidate-recipe-v1.json --output build/front-arrival/export016-v2
```

Verify the exact runtime and recipe hashes, then prepare the private candidate:

```text
python -B build/front-arrival/front-turn-v1/prepare_candidate.py --png build/front-arrival/export016-v2/BMP/JOHNWALK.BMP/016.png --expected-sha256 1cb3d6249486eeecec29ff2040c452c28d14ff8a6f2d79d265e0f17ef2e38d92 --output build/front-arrival/front-turn-v1/candidate-v2
```

Inside the same mounted image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py --candidate /out/candidate-v2
```

The corrected generator now records numeric frame16. The original failed
`candidate-v1` metadata recorded17 despite packing the correct016 bytes; its
guard failure and original helpers remain frozen here as diagnostics. Do not
reintroduce that mistake to reproduce the passing candidate-v2 run.

On the host with Pillow and Playwright available:

```text
python -B build/front-arrival/front-turn-v1/build_review.py
python -B build/front-arrival/front-turn-v1/check_review.py
```

The current builder already uses "Pose close-up". `finalize_label.py` and
`pre-label-review/` document the earlier label correction and should not be run
or copied as new outputs during reconstruction. The first post-label browser
load timed out without a known cause; its diagnostic is retained. The later
instrumented bounded checks passed and are the validation bound to publication.

## Publication and evidence limits

The frozen `publish.py` contains the original absolute workstation server root
and `front-turn016-v1` slug. It refuses an existing destination. A future
publication needs a separately adapted new destination/URL and fresh served
checks; do not overwrite this preview. Publish only `review.html` and `images/`,
excluding deliberately broken/history artifacts and reports.

`finish.py` is a historical binder for the exact scratch layout, including the
retained failed candidate and pre-label artifacts. It is not needed for native
capture reconstruction. A fresh run that omits those historical stages should
write a new binder for the files actually produced instead of fabricating
history to satisfy the old binder.

The fixed native close-up `[560,400,400,280]` includes complete placed canvases.
Two displays per direction differ only inside016; approved017 and all other
pixels remain exact. This establishes technical isolation of the new artwork,
not anatomical correctness or original-executable parity. Human approval belongs
to the separate review decision.
