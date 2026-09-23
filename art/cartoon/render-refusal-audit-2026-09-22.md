# Rendering refusal audit, September 22

No active missing-render item was found in the retained generation-failure records after the user's approval of SMGLIMSE 013 v5. Earlier failed attempts either have successful later drawings or were closed by the user's selection of an existing drawing. Pending appearance review and later native integration are separate from missing renders.

The audit searched generation error/status JSON for failures and moderation blocks, then compared the affected resource/frame identities with current review data, selections and approval records. Selected files were checked on disk; SSUZY1 003 v3 and the retained SBREAKUP 007/008 files were also checked against their recorded hashes.

| Earlier failed requests | Current disposition | Evidence |
| --- | --- | --- |
| SSUZY1 000, 001, 002 | Successful selected drawings exist. 001 intentionally retains its earlier drawing. | [Worker/visitor review data](worker-visitor-mermaid-fixes-v1/review-data.json) |
| SSUZY1 003 | The bottle-in-hand v3 rendered successfully and awaits appearance review. The old original-only backlog sentence was stale. | [Selected versions](visitor-leg-pose-corrections-v2/selected-versions.json), [v3 record](visitor-leg-pose-corrections-v2/generation/SSUZY1.BMP/003-record-v3.json) |
| SSUZY1 004, 005, 009, 010 | Selected drawings exist. 004's corrected belly and upright bottle are approved; 005 uses the selected partial v2. 009 v3 and 010 v2 are approved. | [Selected versions](visitor-leg-pose-corrections-v2/selected-versions.json), [current checkpoint](current-review-checkpoint.md) |
| SBREAKUP 007, 008 | The requested happy-expression revisions were withdrawn. The user chose to retain the sad drawings; both exist. | [Gesture/fin decisions](mermaid-expression-corrections-v1/gesture-and-fin-pass.md), [current review data](mermaid-expression-corrections-v1/review-data.json) |
| SBREAKUP 015, 016 | Successful later renders and head-only corrections exist. | [Mermaid notes](worker-visitor-mermaid-fixes-v1/mermaid-notes.md), [current review data](mermaid-expression-corrections-v1/review-data.json) |
| SMGIFT 014; SMGLIMSE 012, 013, 014 | Successful corrections are now appearance approved. | [Focused review data](review-corrections-2026-09-22/review-data.json), [013 acceptance](review-corrections-2026-09-22/acceptance/appearance-glimpse013-v5.json) |

The earlier SBREAKUP 007/008 concurrent failure did not identify which individual request was blocked. Preserve that uncertainty in its history.

SSUZY1 003 v3 is a saved PNG with SHA-256 `6246fa75a8b379d541e8725f0020d529eee38e481a663e0fa6ddf773bd19c56a`. The separate remaining Suzy task is to review it in the sunscreen sequence and restore the ground-bottle layer through 009/010 at 008's fixed position. This does not require recovering a missing image.

All 12 corrections in the focused September 22 review are appearance approved, and 005 remains the selected partial v2. Ordinary new-art reviews retain the requested 60-72 drawing cadence. Native registration, scene assembly and bulk validation retain their existing deferred status.
