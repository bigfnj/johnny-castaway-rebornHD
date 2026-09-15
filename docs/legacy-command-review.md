# Legacy commands requiring behavior investigation

Baseline: `55b864b8ef54a5c700138e16b74e8d5d62a5d305`, using the unchanged native
`dump` command and original RESOURCE members. These are encoded occurrences in
the 41 disassembled TTM resources, not a count of runtime executions.

| Opcode | Current name | Encoded occurrences / resources | Current implementation |
| --- | --- | --- | --- |
| `0x0080` | DRAW_BACKGROUND | 190 / 36 | Logs only; a comment suggests image-slot reclamation, which is not established behavior. |
| `0x2012` | SET_FRAME1 | 52 / 23 | Logs only. |
| `0xB606` | DRAW_SCREEN | 6 / 4 | Logs only; its six arguments have no implemented effect. |
| `0x4214` | SAVE_IMAGE1 | 60 / 40 | Calls `grSaveImage1`, which is empty. |
| `0xA054` | SAVE_ZONE | 1 / 1 | Calls `grSaveZone`, which is empty. |
| `0xA064` | RESTORE_ZONE | 1 / 1 | Releases the complete saved-zone layer, ignoring the supplied rectangle. |
| `0x1061` | SET_PALETTE_SLOT | 41 / 41 | Logs only; the resource loader supports one palette. |
| `0xF05F` | LOAD_PALETTE | 41 / 41 | Logs only; the resource loader supports one palette. |
| `0x1121` | TTM_UNKNOWN_1 | 61 / 40 | Logs only; a comment associates its argument with saved-image identifiers. |

The actual values for SAVE_IMAGE1, SAVE_ZONE and RESTORE_ZONE correct the stale
opcode numbers in the older backlog. Dispatch is in `src/engine/ttm.c`; graphics
helpers are in `src/engine/graphics.c`. Their current names and comments do not
prove the original engine's semantics.

The sole SAVE_ZONE and RESTORE_ZONE occur in `GJGULIVR.TTM`. A DRAW_SCREEN follows
the SAVE_ZONE. Other DRAW_SCREEN uses occur in `MJSAND.TTM` (three),
`SASKDATE.TTM` and `SBREAKUP.TTM`. These make useful focused review scenes.
The `0x1121`/SAVE_IMAGE1/CLEAR_SCREEN sequence in `WOULDBE.TTM` is another useful
candidate for investigating saved-image identifiers.

## Follow-up method

Keep these dispatch cases reachable. First select a concrete original scene and
capture its behavior alongside an original-engine reference. Establish what each
argument means, which pixels or resources change, and the lifetime of any saved
region. Then construct a bounded native test with independent expected pixels or
ownership counts. Only implement a behavior change when that evidence supports it.

Single-palette evidence applies to the palette commands. It does not establish
that DRAW_BACKGROUND, DRAW_SCREEN or saved-region operations are unnecessary.
Likewise, an empty helper is not safe to remove solely because it has no effect:
its callers still define a compatibility path that future implementation needs.

This cleanup separates explicit saved-layer teardown from the legacy
RESTORE_ZONE wrapper. That ownership correction does not assign new rectangle
semantics to the opcode. The source artwork, original bytecode and accepted motion
remain unchanged.

The local disassembly and complete occurrence inventory are under
`build/cleanup/command-inventory` (ignored). The original archive and golden
manifest can reproduce that disassembly without storing another copy here.
