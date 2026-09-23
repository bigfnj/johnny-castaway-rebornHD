# Earlier mermaid expression pass

Historical generation notes: the user has since clarified that SBREAKUP is intended to be sad and requested all its previous drawings restored. The happy variants below remain archived and are not selected in the current gallery.

31 earlier mermaid-family entries were inventoried: 22 SBREAKUP frames and 9 SMGFTWAV frames. Johnny-only SBREAKUP021-033 are excluded. Original selectors and appearance approvals were not changed.

15 entries have at least some visible facial expression. 13 returned revised images; 2 have no returned image after an uncertain concurrent-group failure. All new drawings await user appearance approval.

## Revised candidates

Use version 1 for SBREAKUP000, 001, 002, 003, 004, 005, 009, 010, 013, 014, 015 and 019. Use version 2 for SBREAKUP006.

| Frames | Visual result |
| --- | --- |
| 000-002 | Soft smiles; bowed or downward head angles preserved. |
| 003-005 | Cheerful smiles and relaxed brows; reaching arms, hands and waterline preserved. |
| 006 | Friendly smile. Version 1 retained the older diffuse halo at the canvas edges. Version 2 removes that halo through alpha while preserving the solid character and crisp ripples. A dark-background proof confirms the clean edges. |
| 009 | Upward gaze and hand pose retained with a happy open-mouth expression. |
| 010 | Hands and hair still hide the mouth and most of the face. Only the visible eyelid/cheek reads as a giggle. |
| 013 | Tears removed; relaxed closed eyes and a small happy smile. Hands remain on the cheeks. |
| 014-015 | Cheerful visible eyes/brows and the already visible portion of the lips. The heads stay low and no additional submerged face/body is revealed. |
| 019 | Small playful smile with the resting arms, hair, tail and waterline preserved. |

All 13 recommended candidates are RGBA with transparent pixels and alpha>=8 bounds strictly inside the canvas. The smallest alpha>=8 margin is 17 pixels on 009. The 006 v2 alpha range is 0-254 and its edge alpha is zero; the other recommended candidates range from 0-255. A few have only alpha1 at the outer edge, not clipped visible artwork.

Each successful output has a byte-exact saved PNG, exact request JSON, reference/output hashes and a record produced by record_output.py. No image was repainted or composited after generation. earlier-006-v2-proof.png is only a diagnostic display on a solid background, not a candidate.

## No returned image

SBREAKUP007 and 008 were sent in one concurrent group with 006. 006 returned successfully. The group then terminated on an output-stage moderation rejection, category sexual, request ID f465dbb3-eff8-458b-9e90-ede8b1bdb326. Neither 007 nor 008 had returned a saved image before termination. The wrapper did not identify which individual request was rejected; the per-frame failure records explicitly preserve this uncertainty. Do not label both as confirmed moderation blocks. No retry was made for this group.

## Retained unchanged

SBREAKUP011, 012, 016, 017, 018, 020 and 034: covered/rear-facing heads, submerged/tail-only phases, or a castle prop with no visible facial expression. No hidden faces were revealed.

SMGFTWAV000-008: all nine entries show tails/fins without a visible face.

The inventory binds each retained entry to its latest previous selected image. Existing approval metadata was incomplete, so the inventory does not invent a prior approval. The current request includes earlier artwork regardless of its prior approval status. Only SMGIFT006/007 in the newer family are explicit sad-expression exceptions; that exception does not apply to SBREAKUP006/007.

This pass performs appearance review only. No production integration, native motion check, broad repository test or historic hash audit was run.
