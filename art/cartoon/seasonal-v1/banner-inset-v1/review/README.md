# Inset banner attachment review

The latest user instruction asks to bring the banner inward or extend the palm fronds. This trial chooses a small, uniform banner inset and preserves the palm. It supersedes the tie-only draft without overwriting that draft, its source, page or evidence. `../user-direction-v1.json` preserves the wording and scope. Human appearance approval is separate from these technical checks.

The original untied `seasonal-v1/raw/003-v1.png` is unchanged. Its scale is 0.2116, an 8% reduction from 0.23. The fixed affine is `[0.2116,0,-10.932,0,0.2116,-68.0552]`; the runtime remains 304×94 at logical origin 361,155. The span is centered at HD x874. The two upper cloth tips map near HD [739.32,310.40] and [1009.11,312.51]. `../measurements-v1.json` records why 5% leaves the left corner on the outer edge while 8% reaches green frond pixels. `evidence/corner-observation.json` binds the resulting actual native corner samples.

The existing premultiplied RGBa bicubic 8×/Lanczos filter and meaningful-fit rules are reused by hash. No color, shape, alpha masking or palm painting was introduced. The export has no cropped alpha≥8 pixels; the reported discarded filter fringe has maximum alpha4. Smoke passed the exact canvas/affine/source, fit and other-prop identity checks. A fresh exporter process reproduced every output exactly; three wrong scale/anchor/affine controls fired the inherited named recipe refusal before the original positive was restored.

Runtime003 SHA256: `e36e103027d2eee53c58c903cd397770a66e5ffce2683e9c0c8ce6e2d988ff92`. Before ZIP, the reviewed tied draft: `507dac5b524b08450d14119443f19a370b790e1bcd198ec6144563ef2a7f2233`. New inset ZIP: `06ab52ed52fd0cf1249bf5cb14d89da95d31263b482137a021c136063e26e5e0`. Exactly one of 2,598 member payloads changes, HOLIDAY003; all 2,597 others remain identical.

Day, night and shifted-day each passed a before/after native smoke pair, then a fresh exact repeat for both variants. The frozen real observer records 51 displays over 2,400 ms per capture. Paired actual timing, Johnny positions and wave phases match, and every pixel outside the placed banner canvas is identical. The outside-canvas damaged-pixel control fired its named refusal and the restored positive passed. Exact runtime source snapshots and small records were frozen under `../native/evidence-v1/` before later footprint code could be imported. The baseline-selection wrappers and their frozen dependencies are explicitly retained.

The page defaults to both cloth corners and palm fronds. It also offers whole-island, wave-closeup and full-scene views. Both panels retain the previous waves, including their prior center appearance; wave correction is reviewed separately. Playback uses actual recorded timestamps and repeats the first 1,440 ms. The wave phase tuple returns to its first state, but the complete scene need not have identical endpoint pixels. No invented animation or endpoint hold is added.

The existing browser checker verifies exact reconstructed native pixels from lossless atlases, all three cases, all four views, timestamps, Normal/Slow controls, stepping, loop behavior and hidden-tab reset. The inherited builder's wrong-case, damaged-PNG, wrong-loop and existing-output controls were re-executed. Page/media publication is immutable, with exact served bytes and a served browser smoke check. These checks do not decide whether the attachment looks right.

## Reproduction

Run from the repository root using Toolbox Python and fresh output directories. The native run used the source snapshot in `../native/evidence-v1/source/`. Reconstruct those sources in a separate checkout for an exact replay after later runtime changes. Do not overwrite the live source or a historical binder.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-inset-v1/export.py --recipe art/cartoon/seasonal-v1/banner-inset-v1/recipe-v1.json --output art/cartoon/seasonal-v1/banner-inset-v1/candidates/v1 --check
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-inset-v1/prepare.py --baseline build/banner-attachment-v1/selected-v3/candidate.zip --runtime art/cartoon/seasonal-v1/banner-inset-v1/candidates/v1/BMP/HOLIDAY.BMP/003.png --runtime-sha256 e36e103027d2eee53c58c903cd397770a66e5ffce2683e9c0c8ce6e2d988ff92 --output build/banner-inset-v1/selected-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-inset-v1/native/run.py --baseline build/banner-attachment-v1/selected-v3/candidate.zip --candidate build/banner-inset-v1/selected-v1/candidate.zip --output build/banner-inset-v1/native-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-inset-v1/review/build_review.py --captures build/banner-inset-v1/native-v1/captures --output build/banner-inset-v1/review-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_review.py --review build/banner-inset-v1/review-v1 --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_review.py --review build/banner-inset-v1/review-v1 --phase regression
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_inputs.py --captures build/banner-inset-v1/native-v1/captures --work build/banner-inset-v1/review-controls-v1
```

These are the actual original run names; use new names on replay. The `preserve.py` scripts are one-time historical writers and must be skipped when replaying. The earlier tied private ZIP can be reconstructed using its own preparation and selected offshore baseline instructions. ZIPs, executables and bulk PPMs are not copied into this tracked evidence.
