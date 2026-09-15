# Cartoon production foundation verification

This change adds a full asset worklist and original walking references while
preserving the production archive and existing artwork. The source baseline is
`0f7d7fd`; work is on `art/cartoon-production-foundation`.

## Catalog and continuous checks

| Check | Result |
|---|---|
| Existing pilot metadata baseline | 2 smoke checks passed before 45 regressions; the three existing Git newline-rule mutations fired |
| Existing art tooling | 20 regression checks passed |
| New production catalog | 2 smoke checks passed before 44 regressions; all 40 executed-source guard mutations fired a named failure |
| Catalog reproduction | Generated JSON and Markdown pass the read-only reproduction check |
| Original walking reference | 2 smoke checks, then 10 regressions and 3 witnessed guard-removal mutations passed; selected PNGs reproduce exactly |
| Actual Linux authoring CI commands | Both smoke suites passed before both regression suites, then both generators passed `--check` |
| CI failure propagation | A damaged pack approval pointer and missing command path stopped subsequent commands; an isolated suppressed-exit mutation triggered the ordering oracle |
| Authoring file preservation | Actual Git checkout preserved the new subtree's exact bytes; removing its scoped rule caused one named failure while an outside-scope newline control still changed |

The catalog contains 2,401 slots: 21 accepted and 2,380 pending. It records 2,141
distinct encoded HD PNGs, 260 duplicate slots and 119 blank HD proxies. Stored
supplied-original evidence is available for 51 slots, consisting of all 36
walking frames and the previous 15 island assets. Duplicate and blank proxy
facts do not imply original-pixel equality or visual acceptance.

The CI rehearsal ran the exact six YAML commands in Linux bash with failure
propagation. It used existing image
`sha256:96617f27fe16421588241def73908fd348a7f9d260440ed0d00b36dcf7a063cc`,
with Python 3.12.3 and Git 2.43.0. All 362 copied input hashes matched the
live inputs and were restored after mutations. An earlier native-build-image
attempt correctly stopped when Git was unavailable; that failure remains in
local evidence. No dependency was installed and no check was weakened.

Detailed local evidence is retained under `build/catalog-validation/` and
`build/cartoon-ci-wiring/`. The compact original-reference verification is
tracked beside its inputs at
`art/cartoon/walk-expansion-v1/reference/verification.json`.

## Preservation and art review

Independent review found that the new catalog initially checked an added
original-frame XPM hash for valid syntax without comparing it to the existing
source record. The check now binds each frame to that record's exact hash.
A nonoverlapping-frame mismatch fixture and an executed guard-removal mutation
verify the correction. The valid generated catalog did not change.

The production ZIP remains SHA256
`1336db8396e5464f5cd133c8f2dee81235dff7731b216175c1cd041ebc7c8ac3`.
The historical original reference and pilot catalogs also remain unchanged.
There are no engine, platform, runtime-gate or deployed-art changes in the
foundation. Native runtime checks still run through the existing CI jobs.

The user approved the rear-three-quarter direction key with "looks good yes".
That review covers character identity and body angle only. Complete motion,
individual foot placement and runtime fit remain separate checks. New source
drawings are retained as drafts; their presence does not increase the accepted
production count.

## Delivery and audit

Local foundation checks are complete. Commit, remote CI, merge and the
post-merge audit will be recorded here when completed. Remaining work belongs
in [BACKLOG.md](../BACKLOG.md), including the frontal 033-035 sequence, remaining
walking states, later artwork and code-drawn scene effects.
