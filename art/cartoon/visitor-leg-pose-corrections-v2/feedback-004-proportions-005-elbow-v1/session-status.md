# Visitor correction pass: local-generation handoff

## Final status

The user approved 003 v2, 005 v1, 006 v3, 008 v2, 009 v3 and 010 v2. The latest 004 instruction explicitly combines 004 v3's head/upper body/hands/bottle with approved 003 v2's hips and both legs. Built-in v8 returned no image, after which the user explicitly authorized directly combining the PNGs. The resulting ImageMagick composite is saved at `direct-composite-004-v1/004-composite-v1.png` and awaits appearance review. It uses the original source pixels at native scale, with only translation and waist alpha-mask adjustments. The six earlier approvals remain unchanged. The review's selected-version records are authoritative. Production assets remain unchanged.

The shorter, accurate edit requests for 003, 004, 006, 009 and 010 all returned images. 009 uses accepted 008 as its primary image, and 010 continues from successful 009. 006 now places the foreground knee beneath the belly area before the shin extends right. The exact successful prompts and references are in `successful-prompts.md`.

Five local FLUX.2 [klein] 4B tests completed across both passes. Both 006 variants kept the wrong knee location. The 009 trial removed the bottle and kept the good leg connection, with less distinct pose changes than the approved built-in image. Both latest 004 variants kept the wrong hip integration. These RGB trials are documented in `local-generation-test/`. All inference processes exited; GPU usage returned near the prior desktop baseline with about 21 GB free.

The initial handoff ZIP and the following chronological record describe an earlier blocked stage. Those failures remain historical. Later 004 failed generations and local trials are preserved in `004-hip-attempts.md`; the direct composite is the current candidate.

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
