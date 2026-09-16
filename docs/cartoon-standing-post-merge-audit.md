# Standing-family post-merge audit

This fresh audit follows PR13's merge to main
`fecfdb3498ccd35fa0bba49762f024d98ececb10`. The merge tree equals the tested
feature head exactly. Engine/platform code, maintained tools/tests, CMake,
gate and workflow files are unchanged from pre-batch main `707a20b`.
The new authoring/review code and four added PNGs are included in the review.

[Feature CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35037737373)
and [merged-main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35038114051)
both passed Windows, Linux, macOS and Web. The
[delivery verification](cartoon-standing-verification.md) preserves the separate
human approvals, package reproduction and initial Windows capture-marker
failure alongside its successful unchanged controls.

## Coverage and findings

| Area | Fresh review and result |
| --- | --- |
| Core engine | Startup/CLI/config, ADS/TTM dispatch and cleanup, walking/path/story control, resource/decompression, dump/utilities/benchmark and native extractors. No new actionable defect established. |
| Platform, rendering and build | All four backends, graphics/style/island/common audio, startup/shutdown callers, PNG/ZIP ownership, CMake deployment, native/Web builders and CI/release wiring. No newly introduced regression or concrete operational blocker established. |
| Web page | Style arguments, selector reload/storage handling, bounded diagnostics and audio-resume listener lifetime. No new confirmed issue; known fullscreen synchronization remains in BACKLOG. |
| Authoring | All four exporters, maintained art tools, approval ancestry, recipe annotations, catalog logic and documented native reconstruction paths reviewed. No new finding. Fresh smoke/regression and package reconstruction pass; immutable source/evidence bytes match Git. |

Parsed resource arrays remain process-owned and are distinct from scene-owned
layers, slot tags and sprites. A full resource unload API is future work for
live restart/pack switching; this application still starts once per process.
No new recurring allocation leak was established. This audit did not run a new
heap/race detector, measure a performance saving, or validate physical audio.

Reachable unfinished TTM drawing/saved-zone operations remain compatibility
work, not removable dead code. The already documented redundant decoder-result
NULL checks remain maintenance candidates. Existing malformed-config, LZW,
TTM string/tag, seed-range and dump-error issues stay in BACKLOG. The platform
review reconfirmed Windows raw-input cleanup, common audio startup ordering,
active audio return handling, Web fullscreen state, primitive clipping and
persistent wave phase as the previously recorded follow-ups.

## Bounded pathfinder check

A fresh headless MSVC probe compiled the actual `calcpath.c` and enumerated all
36 source/destination pairs. All 98 paths have valid endpoints, adjacency and
terminators. The largest pair has five choices against the 50-path capacity;
the longest path has six nodes. The apparent write-before-count-check concern
is unreachable with the shipped fixed graph. This is not a test of a modified
graph or invalid caller indices, and no new pathfinder bug is recorded.

The local core report is `build/standing-postmerge-audit/core.json`, SHA256
`22d52391a3b104b5c4ba7ea57bd957492fb9752aeed47e3b1e4af400bf1f4f3f`.
It identifies the inspected source spans and exact hashes, compiler invocation
and probe output. Local root Web notes are `root-web.json`, SHA256
`f8e67214a5c6101009469774ab170ea79c73084a57f0d3149c85f234eff56710`.

## Main installation

The primary checkout's existing `jc_runtime_data` target refreshed only the
runtime archive. All ten native binaries retained their bytes and timestamps.
Source and deployed ZIPs both have SHA256
`096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.
On an inactive desktop, the full smoke gate passed before all 31 art-style
regressions passed. The interactive desktop and protected inputs stayed intact.

The main smoke log SHA256 is
`be6a2a63427aaf67c4099cc06970c4221f058308a6259b250e661f3856366e9f`;
the art regression log SHA256 is
`834929acab08f1c840d45a7bfbce11e9d9049143baca2b45ea0f9c9d39ee959d`.
Runtime refresh, deployment logs and source-audit reports remain under the
ignored local `build/standing-postmerge-audit/` directory. They are identified
here without claiming bulk local captures are shipped repository artifacts.

The platform/build report is `platform-build.json`, SHA256
`83c00d66523e04106a56e48792ddcf349cba42b429803a854abd80d105d16e8d`.
It binds 24 inspected source/build files, the reviewed backlog, the data refresh
and both deployment checks. Its BACKLOG hash identifies the reviewed working copy;
the separate Git identity denotes merged HEAD. Only the audit documentation
changed concurrently, and the engine/build inputs remained unchanged.

## Recommendations

| Work | Recommendation |
| --- | --- |
| Next art family | Review complete profile walking 001-008 before replacing shared turn003; then address ordinary009/010/012 in their route and story contexts. |
| Standing story coverage | Preserve the accepted native standing family, then review its shared script placements separately. PNG coverage does not establish every scene's contacts or behavior. |
| Waiting timing | Compare same-heading and both adjacent-heading cases against the windowed original before changing the existing scheduler. |
| Capture diagnostics | Implement permanent failed-artifact retention in the maintained palm/wave helpers. The retained complete image and identical successful control narrow this occurrence, but do not identify the missing-stdout cause. |

These items and the existing code findings are retained in [BACKLOG](../BACKLOG.md).

## Authoring readback

Fresh merged-main checks passed 17 smoke checks before 210 regressions: 87
exporter checks, 63 full-catalog checks and 60 pilot metadata checks. Both
catalogs reproduce. The complete standing package reproduces byte-for-byte;
its built-in corrupted-member control produces the expected witnessed failure.
The optional private preview ZIP was omitted during this reconstruction, and
the helper explicitly reported that the independent private-ZIP comparison
was not rerun. Approved member identities and the produced archive remain exact.

The readback verified all 32 runtime/source hashes, all 2,579 retained payloads,
three native evidence binders with 163 bound files, and 218 immutable
Git/working files. Historical scratch paths and publisher assumptions have
documented reconstruction mappings. No fresh native/browser capture or new
mutation matrix is claimed for this source audit.

The local report is `build/standing-postmerge-audit/authoring/result.json`,
SHA256 `08cdc6b93c4f56e2052d4140edfd13f26b937323584d9a655588911cd9873828`.
Its companion files retain ordered checks, read coverage and integrity checks.
An initial audit-runner refusal due to concurrent documentation edits is kept
separately; after narrowing that scratch check to authoring/runtime inputs,
the checks executed successfully. This was a harness precondition, not an
application or art-test failure.
