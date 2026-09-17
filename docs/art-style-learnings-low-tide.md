# Low-tide art lessons

The [accepted low-tide composition](../art/cartoon/low-tide-v1/integration-v1/production-acceptance.json)
adds the exposed beach, detached rock and all twelve low-tide wave frames.
The static shapes and combined motion have separate review records. The user
withdrew a concern about broad gaps between ripple families after recognizing
the low-tide behavior. Keep the accepted spacing; do not bridge those gaps based
on the earlier marked screenshot alone.

| Lesson | Apply it to the next style pack |
| --- | --- |
| Identify the active tide before judging the artwork | Low tide uses BACKGRND001/002 and030-041. High tide uses000 and003-011. A legacy low-tide fallback comparison is not the approved Cartoon high-tide wave set. Label the comparison precisely. |
| Reuse the unmasked approved sources | Recover complete foam strokes before fitting them to a different shore. Reusing previously masked output would retain holes caused by the old ground. The nine island waves reuse approved sources; the separate rock required three new ring drawings. |
| Fit the whole family together | Use one uniform transform per three-phase family. Inspect every phase and the full transformed source bounds. The selected center family uses92% of its former displayed scale to fit the fixed56-pixel height; this is a recorded family choice, not per-frame normalization. |
| Preserve the white wave revision | The accepted center source is foam-shading-v1/007-raw-v1.png. The older rejected007 source contains dark shading. Similar filenames and prior approval of a different phase do not establish the selected source. |
| Keep shore ownership explicit | Static ground supplies the sand and rock. The existing visibility mask keeps the pure-foam layers offshore. That artistic choice does not reproduce the original sand-bearing incoming wash. Partial-alpha masking is an approximation, documented in the export reports. |
| Review the real staggered updates | Four low-tide families update at160ms intervals; each family advances every640ms and the phase pattern recurs every1920ms. A strip of three synchronized composites does not reproduce this sequence. Native clips retain actual display times. |
| Scope the technical evidence accurately | All nine island exports preserve every filtered nonzero-alpha pixel before ground masking. Static exports lose only recorded alpha<=4 fringes; rock040 loses five alpha<=3 fringe pixels. Those bounds do not prove visual approval or exhaustive scene coverage. |
| Separate historical recipes from current acceptance | Draft files keep their original pending status. A new acceptance binds the exact reviewed ZIP, viewer, native evidence and selected PNGs. Inherit earlier47 approvals without rewriting them. |
| Replay with the historical baseline | Frozen exporters pin the old production ZIP. Recover their source snapshot and baseline into isolated scratch. Do not replace the live promoted archive just to run an old exporter. |

The [native review](../art/cartoon/low-tide-v1/motion-review-v1/README.md)
includes no-decoration and clover clips. Extended checks include night with an
offset, two raft stages, front/rear Johnny routes and an unchanged high-tide
control. These selected cases do not establish parity with every original
story or replace human review of future props.
