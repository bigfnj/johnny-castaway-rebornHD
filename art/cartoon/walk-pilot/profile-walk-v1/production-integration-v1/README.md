# Approved profile-family integration

`rebuild.py` adapts the earlier standing-family integration helper. It invokes the
unchanged per-family exporter and `tools/art_pack.py`; it does not introduce another
rendering or ZIP-writing implementation. `inputs.json` pins the frozen prior32-row
ledger, integrated40-row ledger, approval records, reviewed recipes, source images,
reference records and exporter identities. `runtime-sources.json` lists frames001-008.

The new `runtime-recipe-v1.json` copies add only canonical asset paths, reviewed PNG
hashes and the original recipe binding. The helper removes those annotations and
compares the remaining JSON to the frozen reviewed recipe before reproducing it.
All eight runtime and padded images must reproduce exactly with Pillow12.3.0.

The executed run used Python3.11.15/Pillow12.3.0, the baseline archive SHA256
`096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`, and the reviewed
private candidate SHA256
`d476a447f84dcb996c0ef2e229a18ca5e2b0ad03de57cc538b6933a42318d82c`.
The standard builder produces a different ZIP envelope while every named payload
matches that private candidate. All2583 existing payloads and32 prior ledger rows
are preserved; only the eight approved Cartoon profile members are added.

## Reproduce

From the repository root, use a Python interpreter with Pillow12.3.0 and a fresh
output directory. The baseline archive can be recovered from Git commit
`e09123e375ea1004a09fa3540097cff2ac8963ea` at `assets/scrantic_data.zip` using a
binary-safe extraction. Do not redirect binary Git output through Windows
PowerShell5.1 text output. The helper checks the recovered archive's exact hash.

```text
python -B art/cartoon/walk-pilot/profile-walk-v1/production-integration-v1/rebuild.py --repo . --baseline PATH_TO_PINNED_BASELINE.zip --private-candidate PATH_TO_REVIEWED_PRIVATE.zip --output build/profile-walk/replay-profile-v1
```

The private archive is local scratch evidence, not a tracked full-archive copy.
When unavailable, omit `--private-candidate`: baseline/member identities and all
eight reproductions still run, but the helper explicitly reports that independent
private-archive comparison was not repeated. The executed delivery run included it.

Default operation builds a separate candidate. `--promote` was used only after
smoke and regression passed; it requires the production archive still match the
baseline and the maintained ledger still equal the frozen40-row snapshot. A later
replay after promotion should omit it.

## Preserved evidence

`verification.json` is the byte-identical report from the executed promotion.
Its logged command paths describe that run's ignored build directory. The stdout
and stderr files named by that report are copied byte-identically into `evidence/`.
`authoring/` retains catalog regeneration and smoke-before-regression logs and its
own verification report. `evidence-manifest.json` binds these copies.

The Windows authoring inventory regression discovered11 cases:9 passed and the
file/directory symlink cases were explicitly skipped with WinError1314 (the process
lacked symlink privilege). Hardlink coverage ran and passed. Inventory smoke3,
history smoke1/regression22, pilot smoke2/regression60, production smoke3/regression63
and pack-tools regression20 passed. Both generated catalog checks passed. The raw
inventory log preserves the two skip messages; this run does not claim symlink
execution coverage.

The package helper executed a fresh process against an archive with only001
corrupted, required its exact helper witness, and required exactly one named
member-content failure. The damaged scratch archive was removed; the candidate
remained unchanged. Existing authoring tests separately exercise same-path,
duplicate-frame, hash, dimensions and ledger refusal behavior. No maintained guard
changed, so the older exporter mutation proofs were retained without rerunning them.

Human approval covers the two shown profile routes, arms and standing connections,
plus the two ordinary003 departure probes. This packaging evidence does not extend
that approval to unseen003 story contexts or establish original-executable parity.
