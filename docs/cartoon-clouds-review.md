# Cartoon cloud review checkpoint

The user subsequently approved this checkpoint with "Yes, keep these clouds".
See [the delivery verification](cartoon-clouds-verification.md) for integration.
The table below records the earlier review state and its evidence limits.

At this checkpoint, two draft clouds, BACKGRND016 and017, were ready for human
review. Production remained at 61 approved Cartoon assets; the private review
archive had 63. Application source, the shipped archive and production ledger
were unchanged.

| Item | Evidence and decision |
| --- | --- |
| Scope | Complete the ordinary BACKGRND015-017 moving cloud family. Approved015 stays exact. CLOUDS.BMP is a separate resource with unproven runtime reachability, recorded in BACKLOG.md. |
| Art | Built-in image generation produced separate016/017 drawings and targeted revisions. Selected v2 PNGs, ancestors, exact prompts and ordered references are retained in the authoring directory. |
| Fit | Fixed uniform transforms into384x114 and528x152 canvases. No meaningful alpha-8 silhouette clipping. Very faint filtered fringe outside the runtime crop is disclosed in the export report. The medium cloud is flatter than the original and needs visual judgment. |
| Maintained tools | Two focused smoke tests passed, then all28 test_art_tools regression tests passed. |
| Export replay | Pixel/package replay and a fresh relocated-checkout replay passed. Historical prompt paths resolve within the current checkout; invalid source, registration, baseline and escaping-reference controls were rejected. |
| Native rendering | Eight smoke processes passed before eight fresh repeats. Day left/right and shifted night each contain51 native displays over2,400ms; the no-cloud control is pixel exact. Changed pixels stay within the actually drawn016/017 canvases. |
| Negative controls | Damaged016 native placement, an outside-cloud pixel and wrong016 dimensions each produced their specific expected failure, followed by restored positives. The compiled probe and source identities are retained in native evidence. |
| Preservation | All2,612 baseline ZIP payloads, including the approved island, waves and015, remain exact in the2,614-member candidate. The hidden Docker/Xvfb run exited cleanly with no surviving task container. |
| Next decision | Review the paired motion, original shape comparison and night edges. Night's existing backdrop is still fallback; its appearance is not part of this cloud approval. |

The production baseline is commit `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc` and
archive `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`.
The private candidate archive is
`a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d`.

See [the authoring record](../art/cartoon/clouds-v1/README.md),
[runtime preflight](../art/cartoon/clouds-v1/preflight/runtime.md),
[independent adapter review](../art/cartoon/clouds-v1/native-v1/independent-review.md)
and [lessons for the next pack](art-style-learnings-clouds.md).

These checks establish the port's diagnostic rendering and package preservation.
They do not establish original-executable parity, complete cloud traversal or
wrapping, natural random selection of every fixture, or human art acceptance.
