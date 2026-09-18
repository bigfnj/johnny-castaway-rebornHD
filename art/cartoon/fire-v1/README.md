# Cartoon campfire family

The 28 FIRE1.BMP drawings are a single appearance-review batch. They are not exported into the application yet. The user's current workflow is to approve large groups of artwork first, then perform bulk smoke and regression testing during integration.

Open [the review](http://127.0.0.1:8941/fire-v1/review.html). It includes all 28 drawings, original references and five isolated animated comparisons. Approval is pending.

| Frames | Purpose |
| --- | --- |
| 000, 021-026 | Wood and ember stages |
| 001-004 | Smoke wisps |
| 005-008 | Small flames |
| 009-012 | Medium flames |
| 013-016 | Large flames |
| 017-020 | Very large flames |
| 027 | Fire-centered pop/burst graphic |

The precise source-derived phase orders, positions, layering and timing evidence are in [phase-sequences.json](reference/phase-sequences.json) and [phase-notes.md](reference/phase-notes.md). The medium group uses 009, 011, 010, 012. Frame 027 has no speech tail or text and is placed over the fire in the disappointed action. Frame 025 is retained despite lacking a uniquely attributed draw site in the saved static map.

The five animated comparisons use original coordinates and draw order with nominal port timing of 140 ms per phase. Repeating these passes is an editorial review choice. They do not reproduce the complete BUILDING story, its random branches, the dying-fire sequence, clipped embers, Johnny or the original executable's measured timing.

For this preview only, each raw Cartoon alpha8 bounding box is uniformly fitted within the original occupied bounds, centered horizontally and aligned at the bottom. The browser draws the full raw PNG, including faint alpha outside those alignment bounds. No anisotropic stretch, engine coordinate changes, or raw PNG rewriting occurs. Native fit remains unapproved. The original sprite's complete canvas is retained on the source side. Enlarged gallery drawings are intended for appearance review, not a comparison of runtime sizes.

## Retained evidence

- Exact original PNG bytes, current HD copies and nearest-neighbor diagnostic references are under `reference/`; `source.json` binds their origins and hashes.
- Built-in image generation requests, exact raw PNGs and per-output records are under `generation/`. Every distinct asset uses its own generation call. Selected versions are 000 v3; 001, 013, 015 and 023 v2; the other 23 use v1. Earlier attempts remain retained. Frame 023 v2 reduces the pile to a few remaining sticks, making the late dying-fire stages visually distinct. Frame 015 v2 completes the lower tip with transparent clearance; this was an image edit with slight reframing, not pixel-identical canvas padding.
- `review-record.json` binds selected raw assets, prompts, records, source references, page and browser script. Its status is appearance review pending, with production acceptance false.
- `review-data.json` provides the source phase records and reversible browser-only fitting. It does not become a runtime pack manifest.

Some generated PNGs store colored RGB values in fully transparent pixels. Inspect their alpha or composite over a checkerboard before interpreting an apparent glow in a tool thumbnail as visible artwork. Preserve the generated alpha. The smoke001 and flame013 v2 requests were started after reading the raw viewer too literally; later sampled halo positions were alpha0. No visible-halo repair is established by those requests. The first wood draft did have floating wood fragments; v2 removes those fragments before it is used as the shared wood reference. The first composed preview then exposed a shallow base that left a gap beneath the flames. Selected 000 v3 restores taller connected central sticks while retaining the width, changing its meaningful width/height ratio from 2.681 to 1.575. It changes the art, not the source draw coordinates.

Build the review with the toolbox Python and `build_review.py` after all generation files are present. It reads the raw PNGs and writes only the review HTML/data/record. `prepare_references.py` extracts reference copies; it does not modify the source archive. `finalize_keys.py` records the four root-owned keys and their earlier versions.

Pending bulk work: native sizing/registration, layered fire-to-log contact, all dying-fire and ember phases, Johnny's interactions, full scene motion and smoke/regression checks. Production archive, runtime acceptance ledger and application code remain untouched by this batch.

Acceptance recorded 2026-09-18: the user said exactly "excellent, approved" at fire-v1/review.html#motion. This approves the appearance of all 28 selected FIRE1.BMP drawings with the five shown isolated phase comparisons. [Exact acceptance](acceptance/appearance-v1.json) binds the page, browser script, source metadata and selected raw hashes: 000 v3; 001, 013, 015 and 023 v2; all others v1. This dated decision follows the historical pending-review wording above. Native export sizing and registration, integrated fire-to-log contact, dying-fire and clipped ember scenes, Johnny interactions, full scene timing and bulk smoke/regression remain pending.
