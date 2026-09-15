# Cartoon delivery post-merge audit

Completed 2026-09-14 Pacific after [PR #1](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/1)
merged to main as `83597663014f8a933173ce1af45dc6082d17e388`.
Its tree matches the tested feature commit `3d57308230a2a8947e43809f16d32cfa7dfcc96b`.
The follow-up documentation correction changes no executable code, tests or assets.

## Delivery and validation

| Area | Result and scope |
| --- | --- |
| Approved artwork | The partial Cartoon preview ships six walking poses and 15 island assets. The user's "approved, it looks great" is recorded in [scene acceptance](../art/cartoon/island-pilot-v1/acceptance.json). Uncovered artwork retains the existing fallback. |
| Source preservation | All 21 production PNGs match their accepted hashes. All 2,550 original archive members remain byte-identical to pre-feature main. Selected raw images, used ancestors, prompts, references and export recipes are tracked; [image authoring lessons](art-style-learnings.md) is the entrypoint for the next pack. |
| Main checkout build | `pwsh -NoProfile -ExecutionPolicy Bypass -File gate.ps1` completed with exit code 0 after merging, with no compiler warnings. Smoke preceded regression. Native smoke: 27; screensaver/settings: 27; art smoke: 2; wave and palm smoke: one each. Regression: 31 art, 7 wave, 8 palm, 20 authoring tests and all 2,452 golden files passed. |
| Deployed archive | The source archive and the rebuilt main checkout's `build/Release/scrantic_data.zip` both hash to `fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`. |
| Main CI | [Run 34920868412](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34920868412) passed all four jobs on the exact merge commit: Windows MSVC, Linux GCC, macOS Clang and Web Emscripten. Linux/macOS CI validates builds and decode parity; it does not exercise native graphical rendering. |

The post-merge gate used independent HD/fallback pixel controls. It did not repeat
the optional historical executable comparisons or code mutations. Those results
remain in the earlier [review evidence](../art/cartoon/island-pilot-v1/README.md).
The earlier final production checks also passed under Windows PowerShell 5.1;
[final-gates.json](../art/cartoon/island-pilot-v1/review-evidence/final-gates.json)
states exactly which logs were preserved.

## Independent code and record review

Three parallel reviewers checked the merged engine/resource lifecycle, authoring
and packaging, and platform/build paths. Review covered renderer callsites,
ownership and release, source-atop clipping and premultiplied blending, wave
background invalidation, settings and CLI/Web selection, preserved source ancestry,
release wiring, unused helpers and optimization opportunities.

No additional art integration regression was found. The audit does not establish
exhaustive leak freedom or visual acceptance of unreviewed scenes. Existing
findings retain their evidence levels in [BACKLOG.md](../BACKLOG.md): malformed
legacy decompression was reproduced; benchmark end-of-process retention and Linux
audio worker ownership were source-confirmed; build/release and dead-code items
have their specific limits stated. No performance saving is claimed.

The final documentation pass corrected the walking READMEs' stale pending
promotion language and the backlog's blanket reproduction claim. It also records
that archive-only native changes need the normal build or the explicit
`jc_runtime_data` target. Hashed historical evidence remains unchanged.

| Next work | Recommendation |
| --- | --- |
| Wider Cartoon coverage | Extend one complete motion or environment family at a time, using original coordinates and timing, then smoke, regression and human motion review. |
| Next art style | Reuse the preserved reference and export workflow. Establish a new approved identity and directional key before generating a family; Cartoon's drawing scale is not a universal preset. |
| Maintenance follow-ups | Keep the decoder, teardown, archive-refresh and build/release corrections in the separate backlog pass described by their evidence. Confirm package architecture before cutting the next macOS release. |
