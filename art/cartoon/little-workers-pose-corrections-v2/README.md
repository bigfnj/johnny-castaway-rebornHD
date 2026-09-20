# Little-worker pose corrections

[Open the 18-frame review](http://127.0.0.1:8941/little-workers-pose-corrections-v2/review.html). Each row shows the exact original, the previous Cartoon and the corrected Cartoon. Frame search and light/dark checkerboards are available.

These revisions follow the user's feedback on the [72-drawing LILIPUTS batch](../little-workers-batch-v1/README.md). All 18 corrected selections await appearance review. The prior artwork is preserved.

| Frames | Requested change |
| --- | --- |
| 002, 013, 014 | Left leg advances, with the correct near/far hip overlap; 014 extends the step from013. |
| 016, 017 | Right foot starts a low forward step, then completes the step. |
| 020, 021 | Finish the preceding stride without crossed shins, then lean forward into running. |
| 026 | Hide the rear arm completely behind the body. |
| 029 | Near/right arm reaches image-left; far/left arm is slightly forward. |
| 032 | Remove the extra sleeve/arm shape; show two coherent arms. |
| 036, 037, 039 | Far/left arm crosses in front of the face or body; preserve the nearer arm's role. |
| 040, 054 | Bring the far/left arm forward; in054 it reaches farther than the near arm. |
| 046, 047 | Add a slight bend to the near/right elbow. |
| 063 | Keep the gaze right while both arms gesture behind toward image-left. |

The selected versions are v2 for013,014,039 and040, and v1 for the other14 frames. All22 generated attempts remain available. `selected-versions.json` is the selector; `feedback.json` preserves the user's request and12 supplied screenshots.

Artwork was edited with the built-in `image_gen.imagegen` tool. Exact per-image prompts are in `generation/LILIPUTS.BMP/*-request.json`, beside byte-exact output PNGs and provenance records. No artistic postprocessing was applied. `review-record.json` binds the selected PNGs, exact original and prior inputs, gallery helpers and generation records by SHA-256.

Run `build_review.py` with the toolbox Python to rebuild the gallery from the selected versions. `prepare_feedback.py` is the initial scaffold and resets selectors; do not rerun it after choosing revisions.

The focused check covers all18 frame IDs, source/output hashes, raw tool copies, selected RGBA transparency and gallery loading. Native animation timing and original-canvas fitting are deferred under the art-first workflow. Production remains63 PNGs and the archive is unchanged at `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d`.
