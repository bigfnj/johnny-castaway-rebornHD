# Cartoon production foundation verification

This change adds a full asset worklist and original walking references while
preserving the production archive and existing artwork. The source baseline is
`0f7d7fd`. The foundation was merged through
[PR 9](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/9) at
`0757f6b9e9706425a2bc84cf69340b8b227740c3`.

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
live inputs and were restored after mutations in `run-2`, which passed the
then-current 43 catalog regressions. The final `run-3` repeated the six commands
after the XPM/source consistency fix: metadata 2 smoke and 45 regression checks,
catalog 2 smoke and 44 regression checks, both reproduction checks and all three
CI negative controls passed. All 368 files in that later isolated snapshot were
restored to their original hashes.

The earlier `run-1` native-build-image attempt passed both smoke suites, then
correctly stopped when the metadata regression required unavailable Git. That
environment failure remains in local evidence alongside both successful runs.
No dependency was installed and no check was weakened.

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

Both remote CI runs completed successfully in all four platform jobs: Windows,
Linux, macOS and Web. The
[PR run 34992857005](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34992857005)
tested `10672766e0534350f76db53c743002acf9ab1d8b`; the
[main run 34993827317](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34993827317)
tested the merged `0757f6b` commit. Both Linux jobs passed the new authoring step
before the native build and decode checks.

Fresh authoring execution in the main checkout also passed: pilot metadata had
2 smoke checks followed by 45 regressions, the production catalog had 2 smoke
checks followed by 44 regressions, and the existing art tools passed 20
regressions. Both generators passed `--check`. These main-checkout executions
are recorded in the work session; no separate saved main-checkout log path is
claimed. They are distinct from the saved feature-worktree Linux rehearsals.

Two fresh read-only post-merge source audits found no new confirmed runtime
issue. The core review covered startup, events, configuration, common audio,
ADS/TTM execution, resource parsing and decompression, story/island/walking and
path tables, benchmark/utilities and ZIP ownership. The second review covered
all four platform backends, the platform API and PNG loader, graphics/style,
events/island/walk/audio integration and the Web page. Runtime source, production
archive and native gate/build files match `0f7d7fd`; the merged tree also matches
the tested PR tree. Neither review introduced engine changes or reran graphical
tests.

No new recurring ownership leak, broken call target or performance improvement
was established. Existing audio startup, malformed-input, unfinished-command
and platform follow-ups remain in [BACKLOG.md](../BACKLOG.md); they are not new
foundation regressions. The audits do not establish original-engine visual
parity or physical audio behavior. Remaining art work includes the frontal
033-035 sequence, other walking states, later artwork and code-drawn scene
effects. Draft art review remains separate from this foundation delivery.
