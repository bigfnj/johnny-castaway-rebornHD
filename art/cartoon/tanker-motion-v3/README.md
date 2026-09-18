# Tanker angle revision review

This page compares original artwork, the earlier Cartoon selection from `tanker-motion-v2/sprites.json`, and the revised Cartoon yaw drafts. The revised drawings await human review. Earlier pages, source images and production assets remain unchanged.

Open [review.html](review.html) through the existing local review server. It starts centered at half speed. The same 76 source draws, positions, whole-canvas horizontal flips and nominal 80 ms durations drive all three columns. The path camera is fixed and includes the complete source route. Repeat is a review convenience; the saved normal ADS call makes one pass. Frame buttons pause at an unmirrored occurrence when available. The separate still gallery displays all 14 angles unmirrored with the same three image bindings and fit as the centered replay.

This is an isolated source-script replay from `GJVIS6.TTM` tag 9, not a native capture or an original-executable timing claim. Original colors are diagnostic. Concurrent scene layers and scheduler updates are not reproduced. Each Cartoon image is uniformly fitted inside the original alpha-at-least-8 visible bounds, centered horizontally and bottom registered. The complete PNG is drawn, preserving its alpha; the diagnostic threshold does not remove pixels. Final runtime sizing, registration and motion remain pending.

`build_review.py` has an explicit `REVISED` version dictionary. After every selected PNG exists, run from the repository root:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/tanker-motion-v3/build_review.py
```

It refuses missing selected files and verifies the earlier image hashes before writing `sprites.json` and `ratio-diagnostics.json`. It does not substitute an older version. `sprites.json` binds all source paths, byte hashes, actual canvases, alpha extrema and visible bounds, plus the unchanged source sequence and earlier selection. The ratio file is descriptive evidence for visual review, not a test, approval or threshold gate. It reports visible width/height, relative ratios and the display fit for each column.

No PNG editing, runtime exports, package changes, bulk tests or native captures are part of this page build.

Browser check on 2026-09-18 loaded all three motion columns without a page error, enabled playback and exposed all 14 angle choices. Direct jumps reached 006 at step 30, 009 at step 33 and 012 at step 38, unmirrored. Screenshots showed the selected revised drawings. The gallery rendered 14 labeled triples with 42 canvases. Path selection and return to centered playback worked; Restart advanced from step 1 to step 2. The review was left centered and playing at half speed. This is a lightweight preview check, not bulk/native validation or human acceptance.

Review attention: judge the whole rotation, especially 006-009 and 011-013. Proportions are closer overall but remain approximate; 008 is still relatively wide, 009 is more foreshortened than the source ratio, and 012 reads close to head-on. Those observations are preserved for human review rather than counted as resolved by numeric fitting.
