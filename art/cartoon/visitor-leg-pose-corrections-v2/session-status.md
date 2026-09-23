# Visitor correction pass: local-generation handoff

## Current status

All seven visitor drawings are selected for appearance. The user supplied the finished elbow-corrected 005 and requested removal of an accidental red dot. The selected file is `imported-005-v1/005-transparent-v1.png`, a 349 by 206 RGBA cutout. A 21-pixel local repair removes the dot; the checkerboard and small enclosed background gap are transparent. The original screenshot is preserved. Other retained drawing pixels, including the elbow pose, legs and white sunblock, are unchanged. [Selection](feedback-imported-005-v1.json) · [Cleanup provenance](imported-005-v1/record.json). The other six frame entries are unchanged. Built-in 005 v4 returned no image and is historical. Native integration has not been performed.

## Previous 004 selection

The user selected the right-hand screenshot drawing for 004 and requested removal of the checkerboard. The selected file is now `imported-004-v1/004-transparent-v1.png`, a 490 by 304 RGBA cutout with transparent edges. All 45,145 retained drawing RGB pixels match the screenshot crop. The opaque crop and original screenshot remain historical sources. [Selection](feedback-imported-004-transparent-v1.json) · [Cutout provenance](imported-004-v1/transparent-record.json). 005 and the other five frame selections remain unchanged. Built-in v10 is historical; native integration has not been performed.

## Previous 004 generation direction

Latest 004 direction: use the successful 005 v2 prompt and upper-body sunblock action, lowering the raised leg to approved 003 v2's reclining leg arrangement. Built-in v10 returned no image at output moderation. The review shows 005 v2 as the starting drawing and links approved 003 v2 as the leg reference. No new 004 was produced. [Exact feedback](feedback-004-from005-v10.json) · [Request](generation/SSUZY1.BMP/004-v10-request.json) · [Recorded response](generation/SSUZY1.BMP/004-v10-failure.json). 005 and all five approved frame selections remain exactly unchanged by this latest attempt.

## Previous 004 and 005 pass

The user reopened 005 to correct the elbow support and bottle action, and requested another 004 generation because the direct composite's stomach section was overly elongated. Built-in 004 v9 returned no image at output moderation; its stomach proportions remain unresolved and the previous composite is shown for comparison. Built-in 005 v2 returned a transparent image with the elbow bent, the inverted bottle moved to that raised hand, and the other palm cupped underneath. The elbow remains too high relative to the resting hip and legs to read as supporting her weight. A focused 005 v3 edit returned no image, so v2 remains displayed as a partial correction, not an approved or complete fix. The 005 v1 approval is preserved historically. 003 v2, 006 v3, 008 v2, 009 v3 and 010 v2 remain approved and unchanged. [Exact feedback](feedback-004-proportions-005-elbow-v1.json) and [outcomes](004-proportions-005-elbow-outcomes.json) bind the current pass. The selected-version records are authoritative. Production assets remain unchanged.

The earlier ImageMagick composite at `direct-composite-004-v1/004-composite-v1.png` combines 004 v3's head/upper body/hands/bottle with approved 003 v2's hips and both legs. It uses the original source pixels at native scale, with translation and waist alpha-mask adjustments. It remains the head-and-leg reference for 004, with its torso proportions requiring correction.

The shorter, accurate edit requests for 003, 004, 006, 009 and 010 all returned images. 009 uses accepted 008 as its primary image, and 010 continues from successful 009. 006 now places the foreground knee beneath the belly area before the shin extends right. The exact successful prompts and references are in `successful-prompts.md`.

Five local FLUX.2 [klein] 4B tests completed across both passes. Both 006 variants kept the wrong knee location. The 009 trial removed the bottle and kept the good leg connection, with less distinct pose changes than the approved built-in image. Both latest 004 variants kept the wrong hip integration. These RGB trials are documented in `local-generation-test/`. All inference processes exited; GPU usage returned near the prior desktop baseline with about 21 GB free.

The initial handoff ZIP and the following chronological record describe an earlier blocked stage. Those failures remain historical. Later 004 failed generations and local trials are preserved in `004-hip-attempts.md`; no returned drawing corrected the latest torso-proportion request.

## Earlier handoff stage

2026-09-21. The user requested the exact prompts and reference images to try locally, asked which backend generated the images, and offered the installed local image tools. Built-in generation is paused while this handoff is prepared. This does not approve any new artwork.

The public OpenAI documentation identifies built-in Codex image generation as `gpt-image-2`: https://learn.chatgpt.com/docs/image-generation . The callable interface is `image_gen.imagegen`; its arguments and saved results do not expose a per-call backend model identifier.

Current outcomes:

- 003 v1: no output, output moderation block.
- 004 v1: no output. An unchanged retry returned an output moderation block. The first call's rejection detail was not captured.
- 005 v1: candidate ready for appearance review, not approved.
- 006 v1: inadequate leg correction. The saved v2 request was not submitted.
- 008 v2: improved hip join, still requires anatomy review. v1 is retained for history.
- 009 v1: inadequate correction. v2 returned an output moderation block.
- 010 v1: no output, output moderation block.

The blocked request records contain the tool's full responses and request IDs. No blocked attempt returned an inspectable drawing. Do not infer what unseen output looked like.

At the prior committed baseline, only 003 remained unresolved from earlier refusal records. Today's blocks are new events and are not included in the baseline audit. See `prior-refusal-audit.json` and `refusal-audit-notes.md`.

The local handoff preserves exact prompt text, ordered byte-identical input PNGs, and submission status. No local inference was run as part of packaging. After the assistant recommended FLUX.2 [klein]4B and described its published approximately13 GB VRAM requirement, the user explicitly authorized: "you have my huggingface API key if you need it, go ahead and build the .venv and run your tests". That authorizes the isolated environment, official model download using the existing credential, and local test inference. Do not ask for the same authorization again. First-run/download duration is unknown; measure the trial and release its GPU allocation afterwards.

Production assets and the previous review remain unchanged. The seven-frame correction task remains unfinished. Local test inputs/results and environment/model records belong in `local-generation-test/`, separate from the historical built-in requests and the handoff snapshot.
