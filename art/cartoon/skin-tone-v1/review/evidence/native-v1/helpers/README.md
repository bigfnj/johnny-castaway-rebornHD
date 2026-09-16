# Skin-color diagnostics

These helpers create a local still-pose review from an explicit correction export. They copy the28 before/after sprites and masks exactly, verify input/recipe/output hashes and unchanged alpha, and label029 as the unchanged color reference. Seven contact sheets show four poses each at one3x nearest-neighbor scale, with earlier colors, matched colors and mask overlays. Magenta marks mask strength, not actual changed pixels;029 can have a highlighted mask even though its output is unchanged.

Run from the repository root with the toolbox Python, Pillow, NumPy and its existing Playwright Chromium:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/build_diagnostics.py --export build/skin-tone/export-v1 --output build/skin-tone/diagnostics-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/check_diagnostics.py --review build/skin-tone/diagnostics-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/negative_diagnostics.py --export build/skin-tone/export-v1 --output build/skin-tone/diagnostic-negatives-v1
```

The checker runs browser smoke before its all-pose regression checks. The negative controls execute fresh builder processes with a changed valid024 sprite, a changed valid024 mask and an occupied output folder. Each must fail once with its intended label; restored positive runs bracket the controls.

Each output path must be new. Use a new diagnostic version for subsequent export versions and do not overwrite earlier evidence. `review-record.json` binds the exact recipe, copied inputs, generated contact sheets, overlay PNGs and HTML. Browser results bind the actual served HTML and112 image files. This still review does not assert native motion parity, color approval or production promotion and does not publish a site.

## Native color comparison

The native helpers in `../native-review/` prepare and capture the unchanged earlier-color selection and the corrected selection. After their complete baseline and candidate reports are ready, build a new page from those reports and a matching checked still review:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/build_native.py --candidate build/skin-tone/native-review/candidate-v2 --stills build/skin-tone/diagnostics-v2 --output build/skin-tone/native-review/review-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/check_native.py --review build/skin-tone/native-review/review-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/negative_native_browser.py --review build/skin-tone/native-review/review-v1 --output build/skin-tone/native-review/negative-controls/browser-v1
```

These commands select correction export-v2 through its captured recipe hash. Candidate-v2 is the successful native handoff with predecoded grayscale masks; candidate-v1's failed launch is earlier technical evidence, not a different art selection. Native reconstruction prerequisites and the exact baseline archive are documented in `../native-review/README.md`.

The page defaults to Front waypoint at Normal speed, matching the user's screenshot sequence. It retains exact display timestamps, full sprite canvases, one fixed camera per clip and full-island view. Six movement clips and015/016 waiting calls cover all28 selected sprites. Both sides include the same009/010/012 poses. Unchanged029 is labeled as the color reference; the linked still review includes all28 individual poses.

Only the selected clip's image objects remain in the viewer's cache. Switching clips clears prior references and cancels obsolete loads; playback controls stay disabled while images load. The browser checker verifies exact active-clip cache membership after every switch, alongside every native display, timestamp boundary and pose crop. This is a bound on application-held references, not a measured browser-process memory saving. The browser controls deliberately select the wrong pose, disable old-cache release and alter served HTML. Each must execute and fail its named assertion.

`publish_native.py` is separate from local preparation. It requires the exact browser control record, final native timestamp/pixel controls and final input/mask-handoff controls; verifies their recipe/archive/helper identities; checks all local and served bytes; then reruns browser smoke and regressions at the served URL. The immutable slug is `cartoon-skin-tone-v1`. Publication is held until the root task completes its technical and visual review. For future reconstruction, use new output directories and a new publication slug rather than overwriting the historical checkpoint.

The initial native browser regression's readiness wait used Playwright's default animation-frame polling while the timing test deliberately paused that clock. Its90-second timeout and original checker are retained in `evidence/native-browser-first-attempt/`. The corrected checker uses explicit timer polling to await asynchronous clip loads. This changes the test harness, not the viewer, its timing, artwork or capture bytes.

After publication, run the focused readback controls against copied files:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review/check_publication_readback.py --review build/skin-tone/native-review/review-v1 --output build/skin-tone/native-review/negative-controls/publication-readback-v1
```

These controls change valid HTML, candidate-preparation JSON and one native-report JSON in a private fixture. Each change must be refused; restoring it must pass. `preserve_browser.py` then creates a new browser checkpoint, copies the small browser records/helpers/proofs exactly and links the separate native evidence binder plus its independent readback. It rechecks the publication's HTML, recipe, preparations and native report hashes before and after copying. The native binder preserves the native adapters, helpers, reports, logs and retained candidate-v1 launch failure without duplicating them in the browser bundle. Preservation is a one-time evidence write; skip it when replaying the captures or browser checks, and never write into an existing historical evidence directory.
