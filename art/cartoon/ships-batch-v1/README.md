# Ships and vessel effects, combined art review

This batch follows the user's approval of all24 drawings in `props-batch-v1` and the request to continue in batches of at least24. It covers37 source slots: TANKER000-013, GJPROW000-001 and SHIPS000-020.

The user approved the **19 non-tanker drawings** with "the rest look fine btw." after asking for tanker animation and questioning TANKER000-002 and 006-007. This accepts the appearance of GJPROW000-001 and the 17 generated SHIPS drawings at the versions shown in the gallery. All 14 TANKER drawings remain pending motion review. The [scoped approval](acceptance/appearance-nontanker-v1.json) binds the exact selected PNGs, gallery HTML, and an immutable byte-for-byte copy of the review record before its status update.

Inspection of the exact originals found that SHIPS010-013 are identical8x1 canvases containing one opaque black pixel and seven transparent pixels. Retain these four source slots unchanged, with their runtime role unproven. The batch therefore requests33 new drawings and includes four source-preserved slots, rather than inventing visible ships for those pixels.

Original references guide geometry and orientation. Their diagnostic palette does not prove original-executable colors. Generated artwork uses the approved Cartoon rendering style. Exact requests, raw outputs and reference hashes are retained in `tanker-v1` and `ships-v1`.

This is an art construction batch. Original-canvas fitting, scene registration, native animation and full smoke/regression checks remain part of bulk integration. No production archive update is made here.

Open [the combined gallery](http://127.0.0.1:8941/ships-batch-v1/review.html). It provides frame labels, full-image links, original comparisons and light/dark checkerboards. Raw files and exact requests are in [tanker-v1](../tanker-v1/) and [ships-v1](../ships-v1/). Artwork was generated with the built-in ImageGen tool. `review-record.json` binds the selected versions and their reference files.

The sailing ship's separate upper and lower images still need an integrated join check. TANKER views still need motion and original-canvas fitting. These limits do not require another full software gate during art construction.

The four source-preserved SHIPS010-013 files remain unchanged and require no generated-art approval. The non-tanker decision is appearance approval only; it does not approve native placement, joined-section fit, animation, export, or production integration.

The [next batch](next-batch.md) is the complete28-frame FIRE1 family, selected after visual inspection of every original.
