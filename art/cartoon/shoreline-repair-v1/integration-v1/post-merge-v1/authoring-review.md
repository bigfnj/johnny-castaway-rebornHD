# Fresh main authoring and delivery code review

Reviewed on 2026-09-17 in `D:/.ai-work/projects/johnny-castaway-rebornHD`, at verified main commit `9b0a4ed1fb5920faf426c4d3aa89e45afadebf07`. The checkout was clean at the start. The comparison base was the merge's first parent, `397edf8e4b34191ade4be13bc93a215f73b0c631`.

No new executable-path blocker was found in the reviewed scope. This was a fresh read-only code and data review, not a replay of earlier audit conclusions. No tracked files, production data or shared test sources were changed. No builds, mutation matrices, artwork generation or native captures were run by this reviewer.

## Findings

Two entry READMEs retain obsolete current-status prose. `art/cartoon/shoreline-repair-v1/README.md:8-10` says production is unchanged and native integration remains pending. `art/cartoon/shoreline-repair-v1/integrated-shore-v1/README.md:22-26` says production is unchanged and banner/wave revisions remain pending. The actual aggregate acceptance and production ledger record the completed 47-asset integration. Add a current-delivery pointer outside any immutable historical text after checking its bindings; do not rewrite prior approval or capture records. This is a documentation follow-up, not a rendering or package defect.

No other actionable new defect was identified. Historical pending statements inside versioned generation/review records describe those checkpoints and were not treated as failed current approval claims.

## Code and data reviewed

- Maintained authoring: `tools/art_common.py`, `art_pack.py`, `art_production_catalog.py`, `art_review_metadata.py`; changed sections of `tests/test_art_tools.py`, `test_art_production_catalog.py`, `test_art_pilot_history.py`, and `Test-ArtMutations.ps1`. The four footprint declarations remain specific to named BACKGRND frames, original dimensions, exact expanded canvases and scale 2. Missing declarations use the original doubled canvas. Pack validation, active recipe/ledger linkage and current catalog geometry agree; historical pilot source and registration facts remain separate.
- Compiled probe and build entry points: `tests/test_art_footprint.c`, `test_art_footprint.py`, `tests/unix-build.sh`, `test_unix_build_flow.py`, `gate.ps1`, `CMakeLists.txt`, `cmake/RuntimeData.cmake`, `.github/workflows/ci.yml`, `scripts/build_web.ps1`, `scripts/build_web_local.ps1`, and `tools/build_web.py`. CMake, workflow, gate, runtime-data module and Web builders did not change in this merge. The Unix addition executes footprint smoke before regression; the flow fixture covers both new failure boundaries. Mutation probes compile copied sources, check fresh binary identity/timestamp and require execution witnesses. Surface fixtures release pixel allocations through the actual `releaseLoadedSurface` helper. ZIP operations use context managers, failed candidate construction removes only its own output, and inspected subprocess calls are waited for. No new orphan process or resource-lifetime problem was found.
- Integration: `integration-v1/prepare.py`, `integrate.py`, `promote.py`, `promote_v2.py`, `test_promote.py`, `test_promote_v2.py`, `REPRODUCE.md`, `PROMOTION.md`, and the current records. Source replay uses a pinned Git archive in a fresh scratch tree, with the old production ZIP installed only there. It validates all 14 selected outputs, preserves 33 inherited ledger rows and compares the complete named-member map. The absent private ZIP mode prints an explicit limitation and uses the bound map; it does not silently claim a private-archive read.
- V2 promotion: report directory preparation precedes production writes; ZIP, ledger, their readback and atomic report write/readback share the exception/rollback scope. The selected helper restores both prior files and removes a partial report after an ordinary write/readback exception. The retained tests inject actual report-write failures before and after the report replacement in a disposable repository, prove both production files had changed first, and execute a rollback-removal mutant followed by a restored success. This is exception rollback, not an assertion of crash-atomic replacement of two files. V1 remains explicitly historical. The transaction test intentionally consumes the previous disposable preflight fixture; it is not a self-contained fresh-checkout test entry point.
- Index delivery: `integration-v1/index-final/check.py` and `spec.json`. The checker hashes each declared binder, resolves the selected copied/external fields against its declared base, rejects conflicting identities, looks up stage-0 membership and hashes actual indexed blob bytes through `git cat-file --batch`. A worktree-only file cannot pass. Missing-file and wrong-blob controls use a separate index, assert one exact failure, then verify the real index did not change. Scope is the explicit specification, not automatic discovery of every historical/external/scratch reference. The existing BACKLOG item for a maintained general copied-evidence check is therefore not automatically closed by this scoped delivery helper.

Fresh data readback found 47 pack entries, 14 newly accepted assets, 33 inherited assets, 14 runtime-recipe rows and 10 declared shoreline footprints. The pilot history declares 16 replacements, comprising the six previous Johnny replacements and ten shoreline slots. The generated production catalog has 2,401 slots, 47 accepted and 2,354 pending. The character inventory records 2,402 original slots, 2,401 port slots, 28 accepted Johnny frames and 1,002 outstanding Johnny frames. Its regenerated file SHA256 is `20026a83577fd0f3d64a1b4292c68a94b76d3cf804451dfebae2311d94bc0ee1`.

The live ledger parses identically to `integration-v1/integrated-pack.json`. Its main Windows checkout uses CRLF: working SHA256 `0adecc18f8efc7c719a191b6c085cee9379d2b34c8b9a15fc768f53d1aef444a`; LF-normalized and Git-blob SHA256 `1d920d4f97fd4294a14f0d36af97fb6c48882a5bceb49f2a9418cef1f8c1bd8f`. This expected text conversion is not a production-ledger change. The production catalog similarly matches its Git bytes after LF normalization. The immutable acceptance and runtime recipe retain exact SHA256 `73355f3a2d1a82b814d39feb46bfb9b052fc72ec32106f96e86b845adfdf476d` and `bee8cd194ad8bf8d745635740fb4a0de944212807cc027399862823535690c08`.

## Validation boundary

Root separately reported the fresh-main full Windows gate, all four main CI jobs and the 627-binding index check with real missing/wrong-byte controls passed. Those executions were not duplicated here and are not claimed as this reviewer's runs. Retained pre-merge source-replay, authoring and transaction evidence was read for its actual scope, not relabeled as new execution.

This review does not establish exhaustive story/native timing parity, original-executable equivalence or physical platform presentation. Existing fallback low-tide ground, rock, waves, clouds and night-art coverage remains in BACKLOG. No new runtime backlog issue was inferred from those unchanged assets. Source replay still needs the documented Git objects, Python/Pillow version and fresh output directories; historical preparation writers are not current regeneration commands.

Some side-footprint and pilot-history code was originally authored by this reviewer; fresh main readback is not an independent second-author review of that code. The index checker and V2 transaction logic were authored by root and were reviewed independently here. No useful performance improvement was substantiated by this bounded audit, and no unmeasured saving is claimed.

## Selected working-byte source pins

These are bytes read in this Windows checkout. The main commit identifies the remaining reviewed source files; ordinary text checkout hashes can differ from LF Git blobs.

| File | SHA256 |
|---|---|
| `tools/art_common.py` | `2e003886e3504f6af4725eaf875c3d793542dc0efd4ccf45042d670c96f6e914` |
| `tools/art_pack.py` | `4dd755019d6d203574e003d83913313eb17aa35288b5543844b76d679c721fd6` |
| `tools/art_production_catalog.py` | `b6eae10f72a50745d8ed9c465d649fd88623de5bdf56de1a21f5ed37ea246f50` |
| `tools/art_review_metadata.py` | `f5fb1aa8aea584cc9f4a97d84d92a55e6d2dee6dcc430136629962e106b61378` |
| `tests/test_art_footprint.c` | `94cf5dcc662f433e9f14202c27f50ee26b4f608f54c25d052b397251c3a18af5` |
| `tests/test_art_footprint.py` | `eff2b8f6f17627713a793bf7bbead83fc20e4e741b0f907f3a97ba942c7296ef` |
| `tests/test_art_pilot_history.py` | `bfb73029ef913f5b4b92717a5cebc260eca0e00eebd5bf75f07b6c47b8225f04` |
| `tests/unix-build.sh` | `4b58c0471aa9ea5d2008e103fb990ed618a92a0eb6cad16a0d89c7d294042dd7` |
| `art/cartoon/shoreline-repair-v1/integration-v1/integrate.py` | `473a54c720178ce23319a5c16c3376ce7786cfcc86dca7a47a3da985f11e4cb0` |
| `art/cartoon/shoreline-repair-v1/integration-v1/promote_v2.py` | `dc3f29b56bd984bdf299fa0ce4551c5e4717b53b73fcb51666205ad1deb34b8f` |
| `art/cartoon/shoreline-repair-v1/integration-v1/test_promote_v2.py` | `05b79d6e71d0ac37527de92dd852740f2858577ca809e321bfd3d38440c5b377` |
| `art/cartoon/shoreline-repair-v1/integration-v1/index-final/check.py` | `d3e417297d70617b947365fb3de0fd6a0ccf2f8fcb5daee732a909fd19dbd5a6` |
