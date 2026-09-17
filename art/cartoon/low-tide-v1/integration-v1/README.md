# Accepted low-tide integration

The user accepted the beach and rock at the static checkpoint, requested reuse
of the approved Cartoon waves, then accepted the combined low-tide composition
at port8937. The final response withdrew the concern about ripple-family gaps:
"oh, the low-tide does it, nm, its fine." Keep that spacing.

`production-acceptance.json` binds the exact viewer, manifest, native evidence,
static approval and fourteen selected PNGs. It inherits all47 prior approvals.
Earlier pending language in the frozen authoring and review records describes
their historical checkpoints; this aggregate records the subsequent decision.

The final archive SHA256 is
`a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`.
It is byte-identical to the human-reviewed private package. Production has61
Cartoon PNGs and2612 ZIP members. All2598 previous payloads, including the
runtime manifest, remain unchanged. No runtime, footprint, timing or placement
code changes are required. Cartoon remains a partial preview.

## Reproduction

Run these from the repository root with the toolbox Python and Pillow12.3.0.
Use a fresh output directory each time.

```text
python -B art/cartoon/low-tide-v1/integration-v1/replay.py --output build/low-tide-v1/replay-fresh
python -B art/cartoon/low-tide-v1/integration-v1/prepare.py --output build/low-tide-v1/package-fresh --reviewed-candidate PATH_TO_REVIEWED_ZIP
```

The replay recovers the exact source snapshot at9e2f061 and its older baseline
archive into isolated scratch. It runs static smoke first, then the island and
rock exporters. `replay-result.json` records all14 exact reproduced PNGs and
the snapshot file hashes. It never replaces the live production archive.

Preparation validates all61 PNGs using the maintained pack validator, rebuilds
the archive, and compares its exact bytes and full member map with the reviewed
candidate. It also writes the aggregate authoring records in this directory;
use an isolated checkout when reproducing historical records. It does not
promote the archive. The original preparation retained its pre-promotion status
in `package-verification.json`; the later production copy is checked separately.
Its `member_negative_control` is only an in-memory map diagnostic for one
changed034 entry, not a corrupt-ZIP refusal or source-guard mutation test.

Native scene evidence is inherited only after exact package/runtime bindings
are checked. It covers no decoration, clovers, shifted night, raft stages1/5,
front/rear Johnny routes and a high-tide control. Full Windows and maintained
authoring results are recorded in their adjacent integration folders. Current
delivery status and limitations are in the
[verification](../../../../docs/cartoon-low-tide-verification.md).
