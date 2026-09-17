# Native cloud review

Native review completed for BACKGRND 016 and 017 beside the unchanged approved 015. CLOUDS.BMP is a separate resource whose runtime reachability remains unproven; see `../preflight/runtime.md`.

The baseline must be the exact current 61-asset production archive `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`. A candidate adds only Cartoon 016 (384x114) and 017 (528x152), preserving all 2,612 baseline payloads. No renderer, original coordinates, cloud schedule, palette or footprint contract changes are permitted by this review. This adapter is not the historical shoreline or low-tide package validator.

The small C adapter includes the frozen shoreline observer. It replaces the randomized cloud state after native initialization with three explicit valid shape/position/speed entries, then uses normal `adsPlayWalk(0,0,0,0)` waits. Native timer-zero handling clears the initial random cloud layer before any captured display. Day left/right and shifted-night right cases each request twenty waits, nominally 2,400 ms. A zero-cloud case is an exact whole-scene control. These fixtures exercise both mirror paths and both speeds without claiming natural random-state selection or a complete offscreen traversal/wrap.

The observer records every native display and requested tick, cloud draw/flip, actual submitted blit bounds (including the mirrored column blits), wave phase, selected asset path and public wait call. Submitted bounds precede platform clipping; the pixel scope intersects them with the visible canvas. Both archives have the same draw states and timings. Only the actually displayed 016/017 rectangles differ; all other pixels remain exact.

Candidate `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d` passed all eight smoke processes before eight new exact repeat processes. Each moving case contains 51 displays over 2,400 requested ms; the zero-cloud control contains three displays over 120 ms and is whole-scene identical. The focused controls damaged actual 016 placement, an outside pixel, and 016 package dimensions; all three produced their intended single failure and restored positives passed. Compiler stderr is empty, and the native logs have no warning/error/failed/ALSA/segmentation matches. The launcher found no surviving task container. This checks logical timing and pixels, not real-time performance.

Run only after the selected candidate and its SHA256 are supplied:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/native-v1/run.py --candidate <candidate.zip> --candidate-sha256 <SHA256> --output build/clouds-v1/native-v1/review-v1
```

The output must be a fresh named child. The default baseline is `assets/scrantic_data.zip`; after a future promotion, supply `--baseline <retained-a8987430.zip>` and reconstruct the recorded baseline checkout before replay because the protected live archive is also pinned. The existing Docker image, read-only source mount, disabled network, hidden host subprocess and Xvfb avoid workstation display takeover. No tool installation is required.

Reports/images are at `captures/<case>/<baseline|candidate>/<smoke|repeat>/`. Each `report.json` references deduplicated native PNGs and the full actual timeline. The viewer uses the same pixels for a full 1280x960 scene and sky crop `[0,0,1280,340]`; this includes shifted-night clouds. Cropping is a presentation option, not a new rendered scene. Do not use an island-only crop for cloud judgment.

The exact run is retained in `build/clouds-v1/native-v1/review-v1`. Build a fresh viewer with:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/native-v1/build_review.py --captures build/clouds-v1/native-v1/review-v1/captures --output build/clouds-v1/review-v1
```

The current build reconstructs all 96 unique native RGB images exactly from five lossless PNG atlases totaling 11,633,274 bytes. It retains actual timestamps, starts paused at Normal speed, and has manual Replay, frame stepping, both wind directions and night. Changed report-case and reconstruction-identity controls each fired with the expected message, then restored positives passed. Browser interaction QA and human art acceptance are separate records.

`inputs.json` binds the complete runtime source/header/build-input hashes and all imported helper paths. `build.json` binds compiler command, fresh executable, C driver and compiled sources. `launch.json` records source commit `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc` and the pinned image. `summary.json` is written only after comparison, fresh repeats, controls and input readback pass. Existing observer, contract, codec and seasonal helper files are imported unchanged and hash-bound. Replay uses that recorded engine checkout plus the exact new cloud adapter files, which were uncommitted during capture. Bulk PPMs and executables stay in ignored scratch. The compact evidence binder retains reports/logs and the lossless page; it references existing source hashes instead of copying the whole source tree. Do not rerun its one-time writer into an existing binder.

Night uses the existing NIGHT.SCR and native cloud layer without special PNG tint. Review authored brightness and transparent fringes there. These are port-rendered diagnostic states, not original executable or calendar/story coverage.
