# SMGIFT 000-021 expression pass

Prepared for appearance review. No new image is marked appearance-approved or production-integrated.

## Scope and retained drawings

Changed frames: 000, 001, 002, 003, 004, 005, 008, 009, 010, 011, 012, 013, 014, 015, 016, 017, 018, 019, 020, 021.

Retained 006 and 007 unchanged from mermaid-gifts-and-glimpses-batch-v1. The user explicitly approved their sad expressions. No new request, output, or record was created for either frame.

The edit inputs are each selected cartoon from the prior batch and its exact nearest8 original. Prior selected v2 is used for 011 and 014 so their earlier hand corrections remain in the input. All other inputs are prior v1.

## Results and version preferences

All 20 requested frames returned an image on their first call. No failed, blocked, or missing output in this subgroup. No targeted retry was needed. Prefer the new v1 candidate for every changed frame, subject to user appearance review.

| Frames | Visual inspection |
| --- | --- |
| 000-001 | Cheerful smiles, relaxed brows, existing speaking and cheek-resting hand poses retained. |
| 002 | Bashful giggle. Near hand is open and partly covers the mouth rather than supporting the face as a fist. |
| 003 | Happy giggle. Raised far hand presents the inner palm upward with a natural wrist. |
| 004-005 | Happy conversational/playful smiles; existing hand and body arrangements retained. |
| 008 | Happy giggle. Outer hand beside the face now presents its inner palm, with open relaxed fingers and a natural thumb. |
| 009-011 | Smiling expressions retain head direction and hands. 011 retains the previously restored low near hand and separate raised far forearm. |
| 012-014 | Friendly conversational smiles for casually explaining. Existing body and hand geometry preserved, including the low near hand in 014. |
| 015 | Playful smile with both existing hand positions. |
| 016-018 | Happy playful faces turned sufficiently toward the viewer to show both open blue eyes. Existing torso, shoulders, submerged anatomy, hair silhouette and waterline retained. |
| 019-021 | Relaxed happy smiles with their existing right-facing head angles and arm positions. |

## File checks

Each exact request was saved before its tool call as generation/SMGIFT.BMP/NNN-v1-request.json, using schema_version/tool/mode/arguments fields. Every generated PNG is a byte-exact copy of the built-in image_gen result, with its matching NNN-record-v1.json.

Validated 20 records, all 80 SHA-256 request/reference/output pins, and byte equality against the raw tool outputs. Every output is RGBA with alpha reaching zero and canvas-edge alpha no greater than 1. No postprocessing, repainting or manual compositing was applied.

004's raw RGB view shows colored haze outside the drawing, but sampled haze positions have alpha zero, including (300,300), (600,20), (1300,300), (100,850), (750,990), and (1450,700). The hidden RGB is not evidence of an opaque background; preserve the original RGBA file.

Global gallery and selectors are owned by the coordinating agent and were not edited here.
