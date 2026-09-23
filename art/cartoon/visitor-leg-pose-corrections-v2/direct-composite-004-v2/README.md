# SSUZY 004 stacked-leg composite

[Final transparent candidate](004-composite-v2.png), awaiting appearance review.

The user authorized directly combining approved 003's hips and legs with current 004's upper body, emphasizing human proportions. Both sources retain native scale. The donor moves (-140,+20) without rotation or limb deformation. A short waist join below the foreground forearm is repaired in the existing palette and outline. The original upper-body pixels, including the sunscreen action, are preserved wherever the retained upper mask has visible alpha.

The final uses a 1592 by 988 RGBA canvas. It has transparent margins and was inspected on [light](004-composite-v2-light.jpg) and [dark](004-composite-v2-dark.jpg) backgrounds. Earlier draft layouts and grid images are working references, not selected outputs.

[Request and authorization](request.json), [source pins and pixel checks](record.json), and [reproducible build](build-composite.py) are saved together. This is direct PNG editing with Pillow, not a generated image. The small waist patch is documented separately from the unchanged donor limbs.

`publish_review.py` places this candidate in the existing animation and still reviews while retaining 005 and all approved selection pins. It does not run the unfinished bottle-continuity sequence builder. No production integration or native animation validation is claimed.

For later still-review rebuilds, pass this directory's `record.json` to `mermaid-expression-corrections-v1/build_review.py --direct-composite-004`. The publisher supplies that argument. A bare invocation of the older generation-only workflow does not select this direct composite.
