# Side-wave placement and clean center phase

This comparison keeps the selected enlarged ground and full-size clovers. Six complete side drawings are repositioned without resampling; center phase007 uses the new shading correction. The two other center phases remain exact. These are private native packages, not the original artwork or the shipped production package. Human appearance approval is separate from the technical checks.

The page opens paused at the observed first frame, where both versions show center 007. Normal is the default playback speed. Whole shore closeup includes both repositioned families; Center wave detail uses the earlier comparison crop. Both panels always share one camera and clock. High tide and night repeat the actual 1440 ms phase cycle. Low tide retains its full 2880 ms sequence with all 12 phases and unchanged fallback artwork, then stops because that endpoint is mid-cycle. Johnny's complete native routes also stop at their recorded endpoints. Other scene animation can differ across the high-wave loop boundary.

The frozen atlas builder is imported by exact hash and copies native pixel tiles without resampling. The wrapper binds both selected archive hashes, seven replacement identities, source reports, repeated captures and actual phase closure. The captured selection metadata inherited an obsolete raw-source annotation for007; `native/verification-v2/metadata-clarification.json` corrects that provenance without changing the package or pixels. Both historical and corrected selection records are bound by the viewer build.

Rebuild into a fresh ignored directory with the existing Pillow environment:

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/review/build_review.py --captures build/shoreline-repair-v1/native-side-clean-v2/captures --output build/shoreline-repair-v1/waves-fit-clean-review-v1
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/review/check_review.py --review build/shoreline-repair-v1/waves-fit-clean-review-v1 --phase smoke
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/review/check_review.py --review build/shoreline-repair-v1/waves-fit-clean-review-v1 --phase regression
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/review/check_inputs.py --captures build/shoreline-repair-v1/native-side-clean-v2/captures --work build/shoreline-repair-v1/waves-fit-clean-controls-v1
```

Browser checks require the existing Playwright/Chromium toolbox. They run headlessly, smoke before regression, and compare every displayed full native frame plus all camera crops and recorded timing boundaries. The focused input controls damage package identity, the opening007 phase, the loop boundary, a case argument, one native PNG and an existing-output path. They leave captured inputs untouched.

`check_clock_control.py --review <fresh review> --work <fresh ignored control directory>` executes the actual viewer with an intentionally incorrect low-tide loop flag and verifies the named endpoint failure, plus original and restored positives. The first unpublished draft's low-tide loop was corrected before release. Its regression readiness check also needed explicit polling because the test clock intercepts animation frames; that failed attempt is retained separately.

The existing `offshore-scene-review-v1/publish.py` publishes a fresh local slug after matching browser smoke; this task also requires regression and input controls before publication. Pass the checked scratch review as `--review`, a fresh destination below the existing port 8932 server root, and its matching `--url`. Run `check_review.py --review <checked scratch review> --phase smoke --report <fresh served record> --url <published URL>` for served pixel/control verification.

`preserve.py` is a one-time historical checkpoint writer. Do not rerun it over this bundle. Reproduction uses fresh ignored directories and the linked native capture reconstruction. The durable page contains lossless atlases and source report bindings instead of duplicating every full native PNG. Root records the later human response separately.
