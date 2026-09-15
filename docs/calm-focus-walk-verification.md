# Calm focus walking revision verification

Baseline: main `d1a8ffae7ac71e52acb4c7070be7d61e1633623f`.
The user approved the actual island preview on 2026-09-15 with "looks good".
The [production acceptance](../art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json)
records the exact sources, exported sprites, scene evidence and review scope.

## Delivered scope

The production archive replaces Cartoon walking frames 024 through 029 with the
reviewed Calm focus family. Its SHA256 is
`1336db8396e5464f5cd133c8f2dee81235dff7731b216175c1cd041ebc7c8ac3`, identical to
the normal candidate archive associated with the reviewed Linux scene. The
diagnostic route and endpoint hold were not installed in production.

The pack remains partial: six walking poses and 15 island assets. Other poses
and scene states retain HD/original fallback. The accepted leg-order difference
and displayed foot lift remain artistic decisions, not claims of original
anatomical parity. Original reference observations remain unchanged.

## Art and packaging checks

| Phase | Evidence |
| --- | --- |
| Candidate export | Two smoke checks, then 30 regressions and 15 executed guard-removal mutations. Restored exporter reproduced all six PNG hashes. The later docstring/result-label edit also reproduced those six hashes without changing registration or filtering. |
| Actual scene | Current and candidate Linux routes each covered 42 displays and 23 positions. Every pair agreed outside Johnny's placed canvas. Both normal archives matched all 2,452 golden decoded files. |
| Served review | All 84 actual capture PNGs loaded from the review server. Eight smoke checks passed before 52 timing/control regressions. The user then accepted the scene, including the two toe-clearance edits. |
| Promotion | Export smoke preceded pack validation/build and all 20 existing art-tool tests. Exactly six archive members changed; 15 island PNGs and all 2,550 non-style members were preserved. |
| Independent integration review | Repeated the complete archive-member comparison and checked all 21 ledger hashes. All 190 selected existing art/source/reference files matched the clean baseline byte-for-byte; local documentation links resolved. |
| Authoring metadata | Two smoke checks, then 45 regressions and 42 executed-source mutations passed. All three real Git newline-rule mutations fired. Final regeneration/reproduction passed; original-reference JSON remained byte-identical. |

The metadata generator now refuses stale acceptance, recipe and asset-review
pointers instead of accepting correct image hashes with obsolete provenance.
Pending human acceptance is refused explicitly. Current artwork uses the new
recipe; earlier route/cadence records and approximate foot-clearance measurements
retain their older artwork identity.

## Native integration

The unmodified Linux gate (`tests/unix-build.sh`) passed its complete smoke and
regression phases, including all 2,452 golden files, on an isolated source
snapshot containing the promoted archive. Snapshot inputs were hashed before
execution. The existing Docker image ran with Xvfb and no visible desktop.

The first isolated Windows PowerShell 5.1 attempt built without warnings, then
stopped before smoke because an inherited PowerShell 7 module path hid the
Windows `Get-FileHash` cmdlet. An inactive-desktop control reproduced that
environment failure; removing the inherited `PSModulePath` restored PowerShell
5.1's defaults and a real SHA256 command succeeded. The gate and runtime sources
were not changed. Both controls and the failed attempt are retained locally.

With the corrected child environment, the unmodified Windows PowerShell 5.1
gate passed with a warning-free build, all smoke before regression, and all
2,452 golden files equal. The inactive-desktop monitor observed 258 windows
and performed 253 input-desktop checks without a desktop switch. Logs are in
`windows-ps51-clean-env/`; the Linux results are in `linux/` under the integration
evidence directory. Log SHA256 values are, respectively,
`2132f2afcf1aaff4293ff1f50ae4fd960a562e0a16a446bb8fdeef9e3ed29b25` and
`7a50e84f2641f00b22318209cd040357712c5d82fbe7ff517619f10051d1178a`.

All 151 snapshot inputs remained unchanged. The only later live-input difference
was the independently tested metadata generator update; runtime sources,
archive, native tests and gate inputs still matched the tested snapshot.

The exporter only reproduces recorded bytes; it does not assign human approval
or change the production archive. Historical pending records remain alongside
the new acceptance. Exact prompts, used source ancestors, failed visual attempts
and the [image lessons](art-style-learnings-calm-focus.md) are retained for later
style work.

Local detailed evidence is under `build/original-pose-review/`,
`build/calm-promotion-independent.json` and `build/integration-gates/calm-focus-v1/`.
Compact export/native evidence is tracked with the accepted art recipe. These
checks do not establish physical audio output, Linux desktop fullscreen
behavior or complete original-executable scene parity.
