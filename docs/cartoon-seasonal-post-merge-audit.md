# Cartoon seasonal and shoreline post-merge audit

Reviewed main `9b0a4ed1fb5920faf426c4d3aa89e45afadebf07` after
[PR 17](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/17) was merged
and pushed. The approved art is integrated. Fresh core, platform and authoring
reviews found no new code blocker in their stated scopes. Existing issues remain
in [BACKLOG.md](../BACKLOG.md); this is not a claim that the original engine is
fully implemented or that every scene and device has been tested.

## Fresh-main checks

| Check | Result |
| --- | --- |
| Production package | 47 Cartoon assets, 2,598 archive members. Compared with the prior package: ten shoreline replacements, four holiday additions, 2,584 unchanged members, no removals. All 28 accepted Johnny drawings remain unchanged. |
| Windows smoke then regression | The full maintained gate passed on an inactive desktop. All 2,452 golden dump files matched. Art loading, footprint drawing, wave/palm capture, screensaver, lifecycle and other gate checks passed. The workstation's input desktop stayed active. |
| Deployment | Fresh main executable and screensaver were built together with the approved archive. The archive beside them matches production SHA256 `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`. |
| Cross-platform CI | All four jobs passed on the merge commit: Linux, macOS, Windows and Web. [Run 35204147277](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35204147277). |
| Durable evidence | Fresh main passed all 627 selected Git-index bindings. A removed record and a changed indexed blob each caused exactly one failure naming that record; the real index was unchanged. The audit follow-up extends the same specification to its own copied records. |

The [Windows result](../art/cartoon/shoreline-repair-v1/integration-v1/windows-final/main-v1/result.json)
retains the gate and capture identities. The
[post-merge binder](../art/cartoon/shoreline-repair-v1/integration-v1/post-merge-v1/evidence.json)
preserves the package comparison, CI response, deployment identities, fresh index
result and all three source review reports. Bulk native frames and local binaries
remain build outputs, with relevant identities recorded.

Earlier native scene, authoring, reproduction and promotion controls retain their
original execution dates and scope in the [delivery record](cartoon-seasonal-verification.md).
They are not relabeled as new post-merge runs. Ordinary Windows text checkout
conversion accounts for the recorded CRLF differences in three source files and
the production ledger; the Git source and parsed ledger agree. Frozen evidence
keeps its original bytes.

## Review findings

| Review | Finding and action |
| --- | --- |
| Core runtime | Read all 37 files under `src`, including compiled data tables. The exact frame/canvas guards, normal/atop/mirrored offsets and wave restoration bounds agree. New wave storage is released at scene teardown and is not allocated each animation tick. No new ownership imbalance was found. |
| Platforms and active calls | Read all four backends and shared input, presentation, audio, PNG/ZIP and Web paths. No introduced inoperable path or accumulating leak was established. Existing Windows raw-input cleanup, common-audio startup, post-open audio failures and Web fullscreen state issues remain in BACKLOG. |
| Incomplete and dead code | Reachable TTM drawing/save stubs remain unfinished behavior requiring original-engine comparison. They must not be removed as dead code. Redundant decoder-null checks remain the separately recorded cleanup item. Process-lifetime resource storage still needs an ownership design before live restart or pack switching. |
| Authoring and build | Reviewed maintained pack/catalog tools, changed tests, footprint probes, build flows and integration helpers. V2 exception rollback and indexed-byte validation match their documented scope. The ledger, catalog and inventory agree on the 47-asset delivery. |
| Documentation | Two versioned shoreline READMEs describe production and revisions as pending at their historical checkpoints. The maintained art index now explicitly directs readers to the completed delivery and this audit. Prior approval and capture records stay intact. |
| Optimization | No new performance saving was measured. Existing flip/full-frame profiling candidates stay in BACKLOG; no speculative rewrite is included. |

The three detailed reports distinguish source-established issues, historical
probes and fresh execution. Some authoring code was reviewed by its original
author; the index and V2 transaction helpers received a separate author's review.
No new physical-audio, desktop-Linux fullscreen, exhaustive original-binary story
parity, race-detector or memory-profiler result is claimed.

## Decisions and next work

| Decision | Reason or next action |
| --- | --- |
| Keep the selected offshore ripples | This is the user's chosen direction. Incoming sand wash remains an unselected study. All complete wave strokes and the white center phase are preserved. |
| Combine the separate banner approval explicitly | The approved wave comparison still contained the older banner. Production uses the accepted inset banner and verifies the complete resulting member map. |
| Preserve existing character art | This delivery changes the scenery and decorations; accepted Johnny geometry, lighter skin tone and contacts remain unchanged. |
| Keep Cartoon marked as a preview | Low-tide beach, rocks, waves, clouds, night and most story art still use fallback assets. |
| Next art group: low-tide environment | Review the lower beach, rocks and low-tide waves together against original composition, then continue independent props and vehicle directions. This avoids placing new props against scenery still awaiting its own contact review. |
| Generalize evidence tooling later | The delivery-specific index check is proven; automatic binder selection for future packs remains a maintained-tooling backlog item. |

The [shoreline lessons](art-style-learnings-shoreline.md) and
[character playbook](cartoon-character-playbook.md) retain the source-first geometry,
animation, palette, transparency and approval lessons for the next style pack.
