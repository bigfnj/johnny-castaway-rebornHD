# Low-tide post-merge audit

Reviewed main `024c9943a08ede16cfa24ed37aa768cf1f020b63` after
[PR18](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/18) was merged
and pushed. The approved low-tide spacing and artwork are retained. This
delivery adds assets and authoring records; runtime code is unchanged.

| Area | Result and scope |
| --- | --- |
| Main package | 61 Cartoon assets and2,612 ZIP members. All2,598 prior payloads and47 inherited ledger rows remain unchanged. The production ZIP matches the reviewed candidate exactly. |
| Cross-platform CI | Windows, Linux, macOS and Web passed on merged024c994 in [run35262765261](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35262765261). The PR's four jobs also passed before merge. |
| Local main build | The full Windows smoke-then-regression gate passed on the one retry, with all2,452 golden files matching. Source and deployed ZIP hashes match the approved package. The input desktop stayed active. Two known Windows symlink-privilege fixtures were explicitly skipped. |
| First local attempt | The launcher stopped at `gate-child-became-foreground` during Python approval-history regression, after renderer checks. It did not retain the failing PID/creation time, so the cause remains undetermined. The unchanged launcher passed its next run with an added exception observer. This is not evidence of a repaired engine defect. |
| Core audit | Freshly read all37 files under `src`: renderer and fallback, ownership and teardown, resource/decoder paths, scene dispatch, story, walking, configuration and audio. No new concrete blocker found. Existing incomplete commands, malformed-input cases, process-owned resource storage and unreachable decoder-null checks remain in BACKLOG. |
| Platform audit | Freshly reviewed all four backends, presentation, input, audio, PNG/ZIP, Web and deployment paths. No new confirmed platform defect was found. Existing input cleanup, audio-error handling and Web fullscreen issues remain in BACKLOG. No new performance or physical-device result is claimed. |
| Authoring and durable evidence | Three fresh metadata/inventory `--check` commands passed without regeneration. All245 copied evidence files match committed bytes. The325-path readback distinguishes exact immutable files from four documented text line-ending differences. |
| Documentation and follow-up | Corrected planning text that still listed delivered connecting poses and low-tide scenery as pending. Documented historical native replay's baseline requirement and the capture launcher's missing failure identity. Both tooling opportunities are in BACKLOG. |

The [core review](../art/cartoon/low-tide-v1/integration-v1/post-merge-v1/core-review.md),
[platform review](../art/cartoon/low-tide-v1/integration-v1/post-merge-v1/platform/platform-review.md)
and [authoring review](../art/cartoon/low-tide-v1/integration-v1/post-merge-v1/authoring-review.md)
describe their source-reading and execution limits. The
[package readback](../art/cartoon/low-tide-v1/integration-v1/post-merge-v1/package-readback.json)
retains exact member and evidence identities. Earlier feature smoke, native
scene captures and exporter reproduction remain historical results with their
original scope; they are not relabeled as fresh main runs.

No new memory-profiler, race-detector, physical-audio, desktop-Linux fullscreen
or exhaustive original-executable parity result is claimed. No measured
optimization is proposed. The unrelated pre-existing untracked `-e` file in
the primary checkout was left untouched.

| Decision | Next action |
| --- | --- |
| Keep the accepted low-tide gaps | The user withdrew the visual objection. Do not bridge them in a later cleanup without a new art review. |
| Preserve the current61-asset partial pack | Existing Johnny, high-tide and seasonal drawings remain byte-identical. |
| Continue with clouds | This audit initially named CLOUDS000-003. The later [runtime preflight](../art/cartoon/clouds-v1/preflight/runtime.md) established that ordinary moving clouds are BACKGRND015-017; CLOUDS reachability remains unproven. The [cloud delivery](cartoon-clouds-verification.md) completes the active group. Night and alternate oceans remain next before independent props and vehicles. |
| Reuse the saved image lessons | Follow [low-tide guidance](art-style-learnings-low-tide.md) for unmasked source reuse, family transforms, white-phase selection, native timing and scoped approvals. |
