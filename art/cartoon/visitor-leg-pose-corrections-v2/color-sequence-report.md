# SSUZY color sequence comparison

The viewer defaults to new regenerated 004 and 005 color candidates, labeled "Regenerated color candidate: awaiting review". A comparison menu switches back to the unchanged approved imported selections. Frames 000 through 010 are available, and all other frames use the same selected drawings in both modes. No PNG pixels, selectors, approval records, or production assets were modified.

Open [the comparison viewer](color-sequence-review.html). It starts paused on the new 004 candidate. Play, previous/next, a position slider, direct jumps to 004 and 005, and neighboring drawings support color review. Playback stops at the end unless the user enables the explicitly labeled review repeat option. [Candidate notes](color-sequence-candidate-notes.md) link both exact generation requests and records.

## Source evidence

The builder reads `assets/scrantic_data.zip`, parses its RESOURCE.MAP and RESOURCE.001 using the maintained inventory parser, and decodes SUZY.ADS and SUZYCITY.TTM. Both payload hashes and decoded-byte hashes are checked against `docs/knowledge-base/port-inventory.json`, which was produced using the production decompression probe. This trace uses equivalent Python RLE/LZW decoding and does not claim to be a native playback capture.

Decoded script hashes:

- SUZY.ADS: `16b62f1e8d68f57971f3c32a295b042e511f7cb744bd460d6bb61696c9b27e50`
- SUZYCITY.TTM: `4ffe7286f2f2e623ac421fdd2a1e1f18d1e8c527beed36842bc2a7cf9baa08ff`

SUZYCITY.TTM tag 1 loads SSUZY1.BMP into bitmap slot 0 at offset 34. SUZY.ADS tag 1 starts the following excerpt after MEANWHIL.TTM tag 1 finishes:

| ADS command offset | Call | Repeats | Exact SSUZY1 frame order |
| --- | --- | --- | --- |
| 36 | ADD_SCENE 1,2,0,1 | Once | 000,001,002,003,004,005,006,007,008,009 |
| 54 | ADD_SCENE 1,3,2,1 | Twice | 010,009,010,009 per pass |
| 72 | ADD_SCENE 1,5,0,1 | Once | 009,008,006,004,003,002,001,000 |

This preserves 26 source updates, including the adjacent repeated 009 at the transition from tag 3 to tag 5. It is not a filename-order loop. The following tag 6 floating-bottle action and later story are outside this focused excerpt.

## Timing

SET_DELAY 9 occurs before the first UPDATE in each included tag, at offsets 150,340,454. The port sets both delay and timer to 9 ticks. `src/engine/events.c` converts each tick to 20 ms, giving 180 ms for these updates. The ADD_SCENE handling starts fresh threads, and its positive repeat count executes tag 3 twice.

The last frame 000 in tag 5 has TIMER 45,90 at offset 580 before PURGE/UPDATE. Current `src/engine/ttm.c` uses integer `(45 + 90) / 2 = 67`, giving a 1340 ms hold. The source comment expressly says this formula is uncertain. The displayed excerpt therefore lasts 5840 ms under the current port's nominal model, not a measured original-executable duration.

The viewer does not model concurrent layers, browser scheduling overhead, outer story selection, or the original executable's timer behavior.

## Display and asset limits

Originals use exact source DRAW_SPRITE coordinates and original canvas dimensions in a shared enlarged crop. Cartoons are uniformly fitted from their alpha-at-least-8 bounding boxes into each original visible box, bottom-centered. This is a display-only normalization for color comparison, not native registration or approval of animation alignment.

SUZBEACH.SCR and the separate SSUZY2.BMP prop draws are omitted in both panels. The complete decoded commands and each supplementary draw remain in the evidence files. The adjacent color cards show each selected image independently with no pixel changes; exact PNG links are available.

004 remains the imported 490 by 304 PNG with SHA-256 `4487fe4d58e876851822a8bd943a5645730717258382b5e6bd6f769774b86e50`.

005 remains the imported 349 by 206 PNG with SHA-256 `82e70a3d6ddb7033418bbd21740fa0e81449cafbab111223df08818e5e7d6074`.

## Files and checks

- [Sequence metadata and all selected image hashes](color-sequence.json)
- [Decoded source commands](color-sequence-source-commands.json)
- [Reproducible builder](build-color-sequence.py)
- [Viewer template](color-sequence-template.html)

The builder verifies both decoded script hashes, 11 original/selected image pairs, both new candidate outputs and request hashes against their records, the 26-step order, and the 5840 ms nominal duration. It aborts if selected-image hashes disagree with their existing records. No image output is written.

Browser verification of the initial selected-import viewer passed on 2026-09-21. Jump to 005 displayed the selected imported 005 PNG; Next advanced to 006. Play progressed to source update 26, frame 000, and stopped with review repeat disabled. The browser screenshot showed the exact selected PNG color cards for 003 through 006. Browser verification of the later candidate toggle is handled separately; this update received compact data and JavaScript checks.
