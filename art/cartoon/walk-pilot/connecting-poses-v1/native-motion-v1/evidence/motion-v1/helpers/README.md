# Connecting-pose native review

This comparison uses the current 40-asset Cartoon pack, with HD fallback for
009/010/012, on the left. The right adds only the three selected Cartoon poses.
It is a native capture of this port, not a capture of the original executable.
The six clips retain each real display, timestamp, mirror flag and origin.
Each clip has one fixed camera containing every complete sprite canvas in both
panels; Full island shows the entire 1280 x960 capture. Pose stepping preserves
repeated draws. Normal playback chooses the last display at a shared timestamp.
No hold, interpolated step or camera motion is added.

The selected input is `../candidate-selection-v2.json`, using raw 009-v1,
010-v5 and 012-v1. Candidate-v1 and the earlier selection are superseded
technical evidence and remain intact. Human approval of 009's still pose and
010 Face-v1's gaze does not approve the complete motion sequence. Any later
motion approval is a separate record.

## Reconstruct in an isolated checkout

Use a new worktree at baseline commit
`3af0242a74f234aab231d9203b48f78ca8e5c1b4`, then copy the complete connecting
bundle from the evidence commit into its original repository-relative path.
Keep the historical evidence folders and binders intact. The baseline archive
must have SHA256
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`:
40 Cartoon PNGs, 2591 total named payloads. A later promoted archive is a
different input and is deliberately refused; do not replace a working
installation's assets to reproduce this comparison.

Run commands from that checkout's root. Python 3 and Pillow 12.3.0 reproduce
the exact PNG bytes. The browser checker also uses Playwright with Chromium.
On this workstation, `$env:TOOLBOX_PYTHON` supplies those dependencies. The
native Linux capture uses the existing Docker image pinned in `BASELINE.md`;
this repository does not distribute that image. If it is absent, reconstruct
the documented Linux build dependencies before attempting capture.

Start with new ignored `build/connecting-analysis` export outputs and a new
`build/connecting-poses/native-motion-v1` capture root. Never delete historical
tracked evidence to make a helper rerun. Retain failed attempts separately.

### Reproduce the selected runtime PNGs

009 and 012 retain the original `export.py`. 010 requires the distinct
`export_v2.py`: the exact same scale 0.1 and filter, with its explicit cap Y
registration margin 0.10 HD instead of 0.25. This is a uniform translation,
not a smaller drawing, changed fit threshold or anatomy adjustment. Do not
reproduce 010-v5 with the old exporter. The selection binds each frame's
exporter, recipe and tests independently.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/export.py --frame 9 --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/009-v1/recipe.json --output build/connecting-analysis/export009-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/export_v2.py --frame 10 --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/010-v5/recipe.json --output build/connecting-analysis/export010-v5
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/export.py --frame 12 --recipe art/cartoon/walk-pilot/connecting-poses-v1/exports/012-v1/recipe.json --output build/connecting-analysis/export012-v1
```

These output paths reproduce the ignored PNG locations pinned in the selection.
Use a fresh checkout if they already exist. Run each corresponding test tool's
`--phase smoke` before `--phase regression`, with the same frame and recipe and
a new per-frame test output. 010 uses `test_export_v2.py`; 009/012 use
`test_export.py`. [Export details](../EXPORT.md) explain the test switches and
preserved historical checks. Replayed test results belong in scratch; do not
replace the historical records bound by the selection.

### Capture the native baseline and candidate

Follow [BASELINE.md](BASELINE.md) steps 1 through 3: preparation, the independent
compiled trace, six smoke captures before full captures and fresh repeats,
then baseline negative controls. Use the literal `/source` read-only and `/out`
scratch Docker mounts shown there. Skip its historical preservation step 4.

After the baseline summary passes, execute the explicit v2 handoff and package:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/check_selection.py --selection art/cartoon/walk-pilot/connecting-poses-v1/candidate-selection-v2.json --candidate-version 2
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/prepare_candidate.py --selection art/cartoon/walk-pilot/connecting-poses-v1/candidate-selection-v2.json --candidate-version 2
```

In the same pinned image and mounts, replace the baseline capture command's
script with:

```text
python3 -B /source/art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/capture_candidate.py --candidate-version 2
```

Each of the six candidate clips runs smoke before full baseline comparison and
a fresh repeat. The package preserves all 2591 prior payloads and adds exactly
009/010/012. Pixel checks allow differences only inside the currently placed
new sprite canvas; retained poses and surrounding scene pixels must match.
The resulting candidate ZIP SHA256 is
`21194cf35e5b60eebfa9ba48520509ae8f86a72f26313b945f019671d1f345c5`.
This package remains private review input until separately approved/promoted.

For the complete native negative proof, run the preserved exact helper after
all six candidate full/repeat checks pass:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/evidence/motion-v1/negative-controls/repro/check_native_candidate_v2.py
```

It finds the repository from `assets` and runs directly from that preserved
location, writing a new `negative-controls/native-v2.json` in scratch. Its
controls alter display timing, a pixel outside a new pose's canvas and a
retained standing-pose pixel. The neighboring `repro/README.md` describes the
separate original staging paths of the earlier guard-removal harnesses.

### Build and check a fresh browser view

After all native summaries pass:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/build_review.py --candidate build/connecting-poses/native-motion-v1/candidate-v2 --selection art/cartoon/walk-pilot/connecting-poses-v1/candidate-selection-v2.json --output build/connecting-poses/native-motion-v1/review-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/check_review.py --review build/connecting-poses/native-motion-v1/review-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/negative_browser.py --review build/connecting-poses/native-motion-v1/review-v1
```

The checker first runs live browser smoke, then checks every displayed pixel,
timestamp boundary, complete pose crop, connecting occurrence and control in
all six clips. Its screenshots support human review. Wrong-pose selection and
changed HTTP-served HTML are executed in isolated negative pages. The builder
also binds each capture to its configured clip, phase, APIs and exact draws;
equal-duration clips cannot silently exchange labels.

If a review attempt needs correction, use a fresh `review-v2` (or later) output
and pass that exact path to builder, checker and negative runner. Neither a
previous view nor its control record is overwritten. The viewer is not a
measurement of all original-binary timing or every script placement.

## Publishing and evidence preservation

The historical publication slug is **connecting-turns-motion-v1**. It is
immutable. `publish.py` takes an explicit `--server-root`, optional `--base-url`,
`--review` and passing `--guard` records, including matching selection and
candidate-native controls. It refuses an existing slug. `--verify-only` can
finish verification of an interrupted publication with identical bytes; it is
not permission to replace a published page. A reconstruction may be inspected
locally without republishing the historical URL.

`preserve_baseline.py` and `preserve_motion.py` are **one-time evidence writers**.
Skip both when replaying this checkpoint. Their tracked binders deliberately
refuse an existing destination. Do not run them to regenerate files inside
`evidence/`. The historical reports already bind their exact source inputs,
commands, helper snapshots and outcomes. Any genuinely new checkpoint needs
new named destinations and a separate binder.

Before first preservation, `preserve_motion.py` verifies the current HTML,
selection copy and full reports against the published/checked identities.
The saved `negative-controls/repro/check_preservation_readback.py` executes
valid-but-altered HTML, selection JSON and report JSON on isolated copies;
each named refusal is followed by a restored positive. It can run directly
from its preserved location after recreating a fresh publication record.
Large capture images, native executables and private ZIPs stay local; their
hashes are retained. This prevents a later edited input from being mistaken for
the reviewed snapshot. Human motion acceptance remains separate from these
technical checks.

The preserved `helpers/host-run_browser_stage.py` is the exact command/log
wrapper used for this run. Its original location was
`build/connecting-analysis/run_browser_stage.py`; restore it there only if
replaying that wrapper. The direct commands above do not require it.
