# Arrival production metadata validation

[verification.json](verification.json) records the frozen 28-asset archive,
approval/recipe/tool identities, commands in execution order and generated file
hashes. Both smoke suites ran before regeneration and regression.

The pilot passed 2 smoke checks and 60 regressions; all 56 executed-source
mutants produced their intended single named test failure. The full catalog
passed 3 smoke checks and 63 regressions. The existing art-tool suite passed
20 tests, then both generators passed `--check`.

The added condition preserves exact file-byte hashes for the immutable arrival
subtree. Its fixture loads valid arrival acceptance records with LF, CRLF and
lone-CR newlines: pilot assets remain identical while all three raw hashes
differ. Removing only the arrival prefix produced one failure naming
`art/cartoon/arrival-pilot-v1/production-acceptance.json`. Existing maintained-text
normalization controls also passed. This is the mutation result to retain in
the delivery commit message.

All 433 protected inputs were unchanged across the ordered run. Full local logs
and the before/after input manifest remain under ignored
`build/arrival-metadata-final/`; their hashes and scope are recorded in the JSON.
Generated catalogs report 21 pilot assets and 28 total accepted slots, with
2,373 pending. This authoring validation does not replace the separate native
capture or establish original-executable rendering parity.
