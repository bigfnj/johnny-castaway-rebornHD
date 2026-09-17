# Banner attachment review

This separate preview changes only HOLIDAY003 over the previously selected offshore package. Pumpkin, clovers, tree, shoreline, waves, palm and Johnny payloads stay byte-identical. The baseline is a private selected-art package, not shipped production or original artwork. The user had accepted pumpkin/tree appearance; banner attachment and wave placement remained open when this evidence was frozen.

Selected banner export is `../candidates/v3/BMP/HOLIDAY.BMP/003.png`, SHA256 `c524b35d1d30d5a70aa8136e18a0ff739a3b6887673e565831d04883869d9b87`. Its 304×94 runtime canvas and 0.23 scale are unchanged; the documented fit translation is +2 HD horizontally and −0.3 HD vertically relative to V5. Diagnostic v1/v2 were rejected. The corresponding recipe and export checks are owned by the separate authoring evidence.

The baseline ZIP is `build/shoreline-repair-v1/offshore-selected-v1/candidate.zip`, SHA256 `ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac`. The banner-only ZIP is `build/banner-attachment-v1/selected-v3/candidate.zip`, SHA256 `507dac5b524b08450d14119443f19a370b790e1bcd198ec6144563ef2a7f2233`. All 2,597 other member payloads are identical.

The unchanged integrated-shore observer and driver execute real native repeated waits in Docker/Xvfb, with network disabled and no workstation display takeover. Day, night and shifted-day each passed a baseline/candidate smoke pair before six fresh exact repeats. Each capture has 51 recorded displays spanning 2,400 ms. Every paired timestamp, pose and phase matches, and every pixel outside the placed 304×94 banner is identical. The actual outside-canvas damaged-pixel control fires its named failure before the restored positive passes. Four additional package controls cover stale runtime bytes, incorrect canvas, existing output and an unauthorized wave change. Source records, logs, launch and exact runtime source snapshots are in `../native/evidence-v3/`.

The page repeats the first 1,440 ms, including the actual recorded phase transitions. Wave phase tuples close at that interval. Whole-scene hashes do not close: `evidence/loop-boundary.json` retains exact endpoint image hashes and difference bounds, all above the banner/island in these captures. This observation does not identify an animation routine. The page makes no claim that the entire scene is pixel-identical at its loop boundary.

The default camera includes both banner ends and palm fronds. Whole-island, original comparison wave-closeup coordinates and full-scene views use the same native images with no resampling. Three lossless PNG atlases contain unchanged 64×64 RGBA tiles, deduplicated by their exact pixel hashes. Every displayed native frame and timestamp, all four cameras, 1,440 ms loop, Normal/Slow timing, stepping and hidden-tab clock reset passed browser regression after smoke. Four builder controls reject a wrong case, changed native PNG, wrong loop interval and existing output without changing its sentinel.

Published page: <http://127.0.0.1:8932/banner-attachment-v1/review.html>. The publisher read every served HTML/manifest/atlas byte back; served browser smoke then passed. The `page/` copies and `evidence/` are immutable.

## Reproduction

Run from the repository root with the Toolbox Python interpreter. Use fresh output names for every replay. The live source may acquire later footprint changes; to reproduce this native run, first reconstruct its exact source snapshot from `../native/evidence-v3/source/` in a separate checkout and retain the pinned observer dependencies. Do not overwrite current sources or historical evidence.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/prepare.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --runtime art/cartoon/seasonal-v1/banner-attachment-v1/candidates/v3/BMP/HOLIDAY.BMP/003.png --runtime-sha256 c524b35d1d30d5a70aa8136e18a0ff739a3b6887673e565831d04883869d9b87 --output build/banner-attachment-v1/selected-v3
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/native/run.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --candidate build/banner-attachment-v1/selected-v3/candidate.zip --output build/banner-attachment-v1/native-v3
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/build_review.py --captures build/banner-attachment-v1/native-v3/captures --output build/banner-attachment-v1/review-v3
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_review.py --review build/banner-attachment-v1/review-v3 --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_review.py --review build/banner-attachment-v1/review-v3 --phase regression
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/review/check_inputs.py --captures build/banner-attachment-v1/native-v3/captures --work build/banner-attachment-v1/review-controls-v3
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/check_preparation.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --runtime art/cartoon/seasonal-v1/banner-attachment-v1/candidates/v3/BMP/HOLIDAY.BMP/003.png --candidate build/banner-attachment-v1/selected-v3/candidate.zip --work build/banner-attachment-v1/package-controls-v3
```

These are the executed output names, not reusable destinations. Both `preserve.py` writers are one-time historical evidence writers; skip them during replay. No binaries, ZIPs or bulk PPMs are duplicated in the tracked review.
