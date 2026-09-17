# Raft construction art draft

The user approved the appearance of all five selected MRAFT.BMP construction drawings in the [combined prop review](../props-batch-v1/acceptance/appearance-v1.json), including 002-v2. They are not exported, packaged, or approved for native placement. Production assets and runtime sources are unchanged. Native construction-state continuity and the bulk verification milestone remain pending.

Selected raw drafts are `generation/000-generated-v1.png`, `001-generated-v1.png`, `002-generated-v2.png`, `003-generated-v1.png`, and `004-generated-v1.png`. Each is an untouched 1536 by 1024 RGBA output from built-in imagegen. Exact prompts and ordered input paths are saved in the matching request JSON files. `generation/record.json` records output hashes, actual alpha bounds, reference hashes, and the selected draft files.

Completed004 was generated first, using exact original geometry and the approved Cartoon palm trunk and island as style references. The other stages used004 for consistent honey-brown wood, tan rope, dark outlines, and grain. The first002 draft had seven visible near log ends, while003 and004 had six. A single targeted edit produced002-v2 with six ends and retained its unfinished notch. The previous002 and the original generation record remain unchanged as history.

The generator did not preserve the requested guide positions exactly. These are raw art drafts, so original canvas registration must be established during export. Low-alpha residue outside the visible objects is preserved; alpha8 bounds are recorded only for inspection and have not been used to trim or change pixels. The finished004 was also inspected over a neutral background; its dramatic dark-matte glow is largely hidden RGB, rather than the visible sprite appearance.

## Original references

`reference/source.json` records the exact source archives, frame PNGs, dimensions, and style-reference identities. `reference/original-contact-sheet.png` is the existing original atlas. Individual originals and current HD proxies are copied byte-for-byte. Enlarged geometry guides use nearest-neighbor replication and transparent padding only. The diagnostic original red and yellow are not color targets or proof of original executable palette parity.

| Frame | Original canvas | Ordinary HD canvas | Scope |
| --- | --- | --- | --- |
| 000 | 72 by 39 | 144 by 78 | Earliest construction state |
| 001 | 88 by 39 | 176 by 78 | Early unfinished state |
| 002 | 128 by 39 | 256 by 78 | Broad unfinished state |
| 003 | 128 by 39 | 256 by 78 | Nearly complete state |
| 004 | 128 by 39 | 256 by 78 | Complete raft |

Frames005 and006 are excluded one-row placeholders. No Johnny, vehicle occupant, or other character appears in000 through004.

`src/engine/island.c:180` loads MRAFT.BMP. Its raft-state switch maps states1 through5 to frames000 through004 at logical512,266 in high tide or529,281 in low tide, before the island background pieces are drawn. Existing scene-map attribution also links004 to SJMSUZY.TTM tags3,4,7 and SUZY.ADS#2, JOHN MEETS SUZY. These are source and static-script observations; no new execution or timing claim is made.

No tests or native captures were run for this draft, following the art-first workflow.
