# SMGIFT 024–046 generation notes

All 23 assigned frames returned an image. There were 28 built-in image-generation calls: one for each frame, plus one targeted quality retry each for 027, 031, 034, 044 and 045. There were no blocked calls in this subgroup. Outputs were copied byte-for-byte with `record_output.py`; no generated image was resized, repainted or postprocessed.

These are appearance candidates only. No user approval, native registration, animation timing or production integration is claimed.

## References and pose interpretation

Both contact sheets and every individual nearest-neighbor source image were inspected before generation. The source sprite controls visible anatomy, orientation, arm overlap, prop contact and waterline. The shared [mermaid style reference](../workers-and-mermaids-batch-v1/generation/SBREAKUP.BMP/000-generated-v1.png) controls the adult blonde character, turquoise headband, tan skin, opaque green swimsuit top, outlines and cel shading. Every submitted request is saved beside its output.

025 exposes only a hair crown and headband. 026–027 use the hanging pink/green lei and its distinct hand positions. 037–043 depict a white oval ring/seat-like prop, without claiming its narrative identity from these static images. 039–040 hide most of the mermaid; 041 and 043 are prop-only. The source prop's dark interior is opaque black, not an alpha hole. 045 is a standalone traffic signal. 046 is only a flat bright-green effect silhouette; its narrative meaning is not inferred, and no mermaid or object was added to it.

## Preferred candidates

Use v2 for 027, 031, 034 and 044. Use v1 for every other assigned frame, including 045.

| Frame | Candidate | Inspection | Files |
|---|---|---|---|
| 024 | v1 | Right-facing profile, bent fist, long trailing hair and waterline match the source arrangement. | [PNG](generation/SMGIFT.BMP/024-generated-v1.png) · [Request](generation/SMGIFT.BMP/024-v1-request.json) · [Record](generation/SMGIFT.BMP/024-record-v1.json) |
| 025 | v1 | Only blonde crown and turquoise band protrude from ripples; no invented face or body. | [PNG](generation/SMGIFT.BMP/025-generated-v1.png) · [Request](generation/SMGIFT.BMP/025-v1-request.json) · [Record](generation/SMGIFT.BMP/025-record-v1.json) |
| 026 | v1 | Two hands lifting dripping pink-and-green lei; source orientation and contact retained. | [PNG](generation/SMGIFT.BMP/026-generated-v1.png) · [Request](generation/SMGIFT.BMP/026-v1-request.json) · [Record](generation/SMGIFT.BMP/026-record-v1.json) |
| 027 | v2 | Targeted retry submerges the invented hip, preserving the extended arm, lei and slim waist waterline. Prefer v2. | [PNG](generation/SMGIFT.BMP/027-generated-v2.png) · [Request](generation/SMGIFT.BMP/027-v2-request.json) · [Record](generation/SMGIFT.BMP/027-record-v2.json) |
| 028 | v1 | Downward gaze, two open upturned hands at distinct heights and no lei; pose candidate for review. | [PNG](generation/SMGIFT.BMP/028-generated-v1.png) · [Request](generation/SMGIFT.BMP/028-v1-request.json) · [Record](generation/SMGIFT.BMP/028-record-v1.json) |
| 029 | v1 | Upward gaze, bent far wrist high to the right and nearer hand lower; two arms and slim waterline. | [PNG](generation/SMGIFT.BMP/029-generated-v1.png) · [Request](generation/SMGIFT.BMP/029-v1-request.json) · [Record](generation/SMGIFT.BMP/029-record-v1.json) |
| 030 | v1 | Hand near mouth and opposite forearm across lower torso match the source action. | [PNG](generation/SMGIFT.BMP/030-generated-v1.png) · [Request](generation/SMGIFT.BMP/030-v1-request.json) · [Record](generation/SMGIFT.BMP/030-record-v1.json) |
| 031 | v2 | Targeted cleanup removed the detached smear and hazy surround. Prefer v2. | [PNG](generation/SMGIFT.BMP/031-generated-v2.png) · [Request](generation/SMGIFT.BMP/031-v2-request.json) · [Record](generation/SMGIFT.BMP/031-record-v2.json) |
| 032 | v1 | Front-facing raised shoulder-level hands, open mouth and waterline match; minor thin edge wisps remain for appearance review. | [PNG](generation/SMGIFT.BMP/032-generated-v1.png) · [Request](generation/SMGIFT.BMP/032-v1-request.json) · [Record](generation/SMGIFT.BMP/032-record-v1.json) |
| 033 | v1 | Three-quarter shrug with asymmetric open palms and waist waterline follows the source. | [PNG](generation/SMGIFT.BMP/033-generated-v1.png) · [Request](generation/SMGIFT.BMP/033-v1-request.json) · [Record](generation/SMGIFT.BMP/033-record-v1.json) |
| 034 | v2 | Targeted retry removes invented vertical costume strip; matching green top, raised arms and waterline retained. Prefer v2. | [PNG](generation/SMGIFT.BMP/034-generated-v2.png) · [Request](generation/SMGIFT.BMP/034-v2-request.json) · [Record](generation/SMGIFT.BMP/034-record-v2.json) |
| 035 | v1 | Rightward lean, image-left arm behind hair and image-right hand raised; source pose retained. | [PNG](generation/SMGIFT.BMP/035-generated-v1.png) · [Request](generation/SMGIFT.BMP/035-v1-request.json) · [Record](generation/SMGIFT.BMP/035-record-v1.json) |
| 036 | v1 | Strong forward lean with streaming hair, bent near arm, farther raised hand and small green lower fragment. | [PNG](generation/SMGIFT.BMP/036-generated-v1.png) · [Request](generation/SMGIFT.BMP/036-v1-request.json) · [Record](generation/SMGIFT.BMP/036-record-v1.json) |
| 037 | v1 | Diagonal rise and both hands on upright white oval prop; retains green lower fragment and water. Dark interior matches the source's opaque black treatment. | [PNG](generation/SMGIFT.BMP/037-generated-v1.png) · [Request](generation/SMGIFT.BMP/037-v1-request.json) · [Record](generation/SMGIFT.BMP/037-record-v1.json) |
| 038 | v1 | Leaning back with both raised arms holding overhead oval prop, source orientation and hair spread. | [PNG](generation/SMGIFT.BMP/038-generated-v1.png) · [Request](generation/SMGIFT.BMP/038-v1-request.json) · [Record](generation/SMGIFT.BMP/038-record-v1.json) |
| 039 | v1 | Prop shown nearly edge-on with only small hair and central hand fragments; no invented visible face/body. | [PNG](generation/SMGIFT.BMP/039-generated-v1.png) · [Request](generation/SMGIFT.BMP/039-v1-request.json) · [Record](generation/SMGIFT.BMP/039-record-v1.json) |
| 040 | v1 | Head/face remains submerged behind hair at right, white oval prop tilted left, both hand contacts retained. | [PNG](generation/SMGIFT.BMP/040-generated-v1.png) · [Request](generation/SMGIFT.BMP/040-v1-request.json) · [Record](generation/SMGIFT.BMP/040-record-v1.json) |
| 041 | v1 | Standalone shallow diagonal white/gray oval prop with dark center and yellow rim accents; no person or water. | [PNG](generation/SMGIFT.BMP/041-generated-v1.png) · [Request](generation/SMGIFT.BMP/041-v1-request.json) · [Record](generation/SMGIFT.BMP/041-record-v1.json) |
| 042 | v1 | Correct opposite arm actions: straight reach to image-left with drips, bent arm over head touching hair. | [PNG](generation/SMGIFT.BMP/042-generated-v1.png) · [Request](generation/SMGIFT.BMP/042-v1-request.json) · [Record](generation/SMGIFT.BMP/042-record-v1.json) |
| 043 | v1 | Standalone broader oval prop, distinct perspective from 041; white rim and dark opaque center follow source. | [PNG](generation/SMGIFT.BMP/043-generated-v1.png) · [Request](generation/SMGIFT.BMP/043-v1-request.json) · [Record](generation/SMGIFT.BMP/043-record-v1.json) |
| 044 | v2 | Targeted retry removes unintended costume extensions while preserving the source arm gestures. Prefer v2. | [PNG](generation/SMGIFT.BMP/044-generated-v2.png) · [Request](generation/SMGIFT.BMP/044-v2-request.json) · [Record](generation/SMGIFT.BMP/044-record-v2.json) |
| 045 | v1 | Traffic signal and post match source, but a soft gray halo surrounds the object; cleanup requested. | [PNG](generation/SMGIFT.BMP/045-generated-v1.png) · [Request](generation/SMGIFT.BMP/045-v1-request.json) · [Record](generation/SMGIFT.BMP/045-record-v1.json) |
| 046 | v1 | Literal isolated vivid-green stepped/diagonal effect silhouette. No character, prop interpretation or extra colors were introduced; edge speckles remain for appearance review. | [PNG](generation/SMGIFT.BMP/046-generated-v1.png) · [Request](generation/SMGIFT.BMP/046-v1-request.json) · [Record](generation/SMGIFT.BMP/046-record-v1.json) |

## Targeted retry history

- 027 v1 invented a visible hip below the source waterline. v2 submerges that extra lower-body section while retaining the extended arm and lei.
- 031 v1 had a detached translucent smear beside the hair and hazy water surround. v2 removes that unintended material while keeping the pose.
- 034 and 044 v1 introduced green fabric strips extending from the top down the visible waist. Each v2 returns the top to the established costume design.
- 045 v2 was requested because the inline view appeared to show a gray glow. Subsequent read-only RGBA inspection showed the sampled exterior glow pixels have alpha 0 in both versions, with outer-side alpha no greater than 1. v2 offers no clear improvement; v1 remains preferred. The raw retry is preserved.

Fine anti-aliasing and very faint edge pixels remain in several returned assets. Their recorded alpha metadata is preserved for later native preparation; the appearance pass does not apply automatic alpha thresholding.
