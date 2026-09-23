# Current 004 and 005 candidate comparison

## September 22: inward belly curve

The current 004 candidate is [composite v3](direct-composite-004-v3/004-composite-v3.png). After reviewing v2, the user requested that the circled skin protrusion under the forearm become an inward-curved belly. V3 changes only this local join, with all other pixels identical to v2. See the [request](direct-composite-004-v3/request.json) and [record](direct-composite-004-v3/record.json). This refinement awaits review.

## September 22: 004 stacked-leg correction

The preceding [004 direct composite v2](direct-composite-004-v2/004-composite-v2.png) supplied the approved 003 hip-and-leg arrangement and 004 v2's upper body. Both remain at native scale; the lower body is translated (-140,+20) and the short waist join is repaired. See its [request](direct-composite-004-v2/request.json) and [provenance](direct-composite-004-v2/record.json). The 005 color candidate remains the same v2 PNG. Approved imported selections remain separate.

The sequence still has 26 updates and nominal 5840 ms timing. This targeted update changes only the displayed 004 candidate and its review labels. The unfinished 003/009/010 bottle viewer correction has not been included. The [still review](../mermaid-expression-corrections-v1/review.html#frame-SSUZY1.BMP-004) also presents the composite.

## September 21 color pass, retained history

The September 21 [sequence viewer](color-sequence-review.html) defaulted to regenerated 004 and 005 v2 color candidates. The following records describe that earlier color pass. Switch "Compare drawings" to "Approved selections" to show the unchanged imported PNGs. The toggle changes only these two drawings, including their neighboring color cards and exact PNG links.

The same 26 source updates, coordinates, tag 3 repetition, and nominal 5840 ms timing apply in both modes. Display scaling is comparison-only. No approval or production selection was changed, and no PNG was edited.

| Frame | Candidate | Exact request | Generation record |
| --- | --- | --- | --- |
| 004 | [v2 PNG](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/004-generated-v2.png) | [004 v2 request](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/004-v2-request.json) | [004 v2 record](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/004-record-v2.json) |
| 005 | [v2 PNG](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/005-generated-v2.png) | [005 v2 request](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/005-v2-request.json) | [005 v2 record](../mermaid-expression-corrections-v1/generation/SSUZY1.BMP/005-record-v2.json) |

Candidate output hashes:

- 004: `f09937bbfa7f6c5e0ff0d34ccc5cacf04a456eb6f0a9b5ff0f50cabf42a7c173`
- 005: `beeebb3388ba6ab44fc52fbd824aac464158570f6bb0e4d71e0e675b1199b5de`

The builder verifies these outputs and their saved request hashes through the generation records. Approved import pins remain in `sprites[4].cartoon` and `sprites[5].cartoon`; the new drawings are separate `candidate` entries with null appearance approval. The viewer preloads both sets, pauses when switching mode, and retains the same current source update.
