# Workers and mermaids, batch 1

60 new Cartoon drawings are ready for appearance review in [the gallery](review.html). Every card shows the selected drawing above its exact original. Use the resource/frame filter or group links, and switch between light and dark checkerboards to inspect transparency.

| Resource | Frames | Drawings |
| --- | --- | ---: |
| LILIPUTS.BMP | 072-100 | 29 |
| SBREAKUP.BMP | 000-020 and 034 | 22 |
| SMGFTWAV.BMP | 000-008 | 9 |

Your approval of the previous 18 worker corrections is saved in [their acceptance record](../little-workers-pose-corrections-v2/acceptance/appearance-v1.json). The accumulated corrections are now [standing pose and action notes](../../../docs/art-style-learnings-pose-and-action.md). They cover limb ownership, walking phases, hidden body parts, prop contact, book damage, spinning blades, slack parachute cords, and source-specific accessories.

Originals and neighboring frames govern each new pose. Cartoon references govern character identity and materials. The worker review pays particular attention to both hands gripping tools or rope, crossing arms, head direction and complete rope endpoints. Mermaid poses retain source waterline occlusion and rear-facing hair. The tail sequence preserves separate exposure, bend and submersion states. LILIPUTS 101 is excluded because its visible original duplicates 080. SBREAKUP 021-033 are Johnny drawings and are outside this batch.

The built-in image generation tool produced every drawing individually. Exact prompts are saved as `generation/<resource>/<frame>-v<version>-request.json`; corresponding `*-generated-v<version>.png` files preserve the tool output bytes and alpha without artistic postprocessing. Per-output records bind prompts, references and images by SHA-256. [selected-versions.json](selected-versions.json) identifies revisions selected over version 1. Earlier drafts remain available.

The reclining visitor family was deferred after repeated image-tool output moderation failures. Its partial drafts and unused requests are preserved in [the deferred record](deferred/SSUZY1-status.json) and do not count toward these 60 drawings.

These drawings await your appearance review. Native canvas placement, sequence timing and production integration remain later work. The production archive is unchanged, and no full regression suite was run for this art review.
