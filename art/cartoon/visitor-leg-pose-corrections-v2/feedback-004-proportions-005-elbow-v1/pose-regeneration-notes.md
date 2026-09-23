# Pose regeneration notes

The calls below returned images using concise, literal edit descriptions and explicitly assigned reference roles. They preserve the adult visitor's established clothing coverage and cartoon identity. This records what was submitted; it does not establish why earlier attempts were blocked or guarantee future results.

## Latest 004 direct composite

The latest user instruction replaces the hip-redraw approach with an exact two-source combination: retain 004 v3's head, upper body, arms, hands and bottle; use approved 003 v2's waist, hips and both complete legs. After the built-in v8 attempt returned no image, the user explicitly authorized directly combining the PNGs.

The [direct composite](direct-composite-004-v1/004-composite-v1.png) was created with ImageMagick, not generation. Both sources remain at native scale with no rotation or limb deformation. The intact 003 lower portion is translated (-120,+68); the join lies behind 004's foreground arm. Alpha masks remove the old waist and donor forearm fringe while preserving the bracelet. Visible pixel checks for retained head/body and donor hip/leg regions match the sources exactly. [Provenance](direct-composite-004-v1/record.json).

This candidate awaits user appearance review. All six previously approved drawings remain unchanged.

## Earlier 004 hip-to-leg correction

The user rejected 004 v3's hip integration. The pelvis must turn more toward the viewer, with the front thigh overlapping and hiding the lower swimsuit panel and the entire rear upper thigh. Only a slim part of the rear lower leg should emerge underneath and extend beyond the front leg. The green and blue paths on the user's annotated original are the current pose authority. Do not preserve v3's side-facing hip, exposed lower-hip wedge or separate rear-thigh triangle.

Built-in attempts v4, v5, v6 and v7 returned no image; their request and failure records are saved. Two local 004 trials returned RGB images but both failed the hip/leg correction and are not selected. This earlier approach remains historical. [Attempt notes](004-hip-attempts.md).

## Earlier approval and 004 overlap correction

The user approved 003 v2, 005 v1, 006 v3, 008 v2, 009 v3 and 010 v2, rejecting only 004 v2. For 004, use approved 003 as the leg-pose guide. The left bent leg lies uppermost and its shin slopes up toward screen-right. The right calf and foot rest slightly underneath. Preserve 004's bottle and upper body. Do not interpret this as two separate parallel shins, which was the rejected v2 arrangement.

004 v3 implemented the earlier lower-leg overlap change but was subsequently rejected for its hip-to-leg connection. Its output is a byte-exact transparent image from the built-in tool and is retained as rejected history.

[Exact request](generation/SSUZY1.BMP/004-v3-request.json) · [Output](generation/SSUZY1.BMP/004-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/004-record-v3.json)

## 003 v2

Use the successful 001 drawing as the entire edit target. Remove the bottle and cap, then bring the empty forearm inward. The existing pose and both legs remain the reference.

[Exact request](generation/SSUZY1.BMP/003-v2-request.json) · [Output](generation/SSUZY1.BMP/003-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/003-record-v2.json)

1. [Edit target and complete pose: earlier 001](../workers-and-mermaids-batch-v1/generation/SSUZY1.BMP/001-generated-v1.png)

## 004 v2

Use previous 004 as the edit target and earlier 001 only for the side-resting leg arrangement. Keep 004's upper body, hands and bottle.

[Exact request](generation/SSUZY1.BMP/004-v2-request.json) · [Output](generation/SSUZY1.BMP/004-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/004-record-v2.json)

1. [Edit target: previous 004](../worker-visitor-mermaid-fixes-v1/generation/SSUZY1.BMP/004-generated-v1.png)
2. [Leg-pose reference only: earlier 001](../workers-and-mermaids-batch-v1/generation/SSUZY1.BMP/001-generated-v1.png)

## 006 v3

Use current 006 v1 as the target and exact original 006 as the folded-leg guide. Place the foreground knee directly below the belly-button area, with a short thigh descending down-left and a distinct shin returning down-right. Preserve the other raised knee.

[Exact request](generation/SSUZY1.BMP/006-v3-request.json) · [Output](generation/SSUZY1.BMP/006-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/006-record-v3.json)

1. [Edit target: current 006 v1](generation/SSUZY1.BMP/006-generated-v1.png)
2. [Folded-leg reference: exact original 006, enlarged nearest-neighbor](../workers-and-mermaids-batch-v1/reference/nearest8/SSUZY1.BMP/006.png)

## 009 v3

Start from 008 v2, whose leg join the user accepted. Keep that folded leg and hip attachment; use 009 v1 only for the next hand/action pose, and remove the bottle.

[Exact request](generation/SSUZY1.BMP/009-v3-request.json) · [Output](generation/SSUZY1.BMP/009-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/009-record-v3.json)

1. [Edit target and accepted leg join: 008 v2](generation/SSUZY1.BMP/008-generated-v2.png)
2. [Hand/action guide only: 009 v1](generation/SSUZY1.BMP/009-generated-v1.png)

## 010 v2

Start from successful 009 v3 to retain its corrected leg anatomy. Use previous 010 only for the farther forward lean and hand reaching to the ankle.

[Exact request](generation/SSUZY1.BMP/010-v2-request.json) · [Output](generation/SSUZY1.BMP/010-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/010-record-v2.json)

1. [Edit target and leg anatomy: successful 009 v3](generation/SSUZY1.BMP/009-generated-v3.png)
2. [Forward-lean and ankle-reaching action guide only: previous 010](../worker-visitor-mermaid-fixes-v1/generation/SSUZY1.BMP/010-generated-v1.png)

The earlier acceptance of 008 v2's leg join supplied the anatomy reference for the 009-to-010 progression. The specific correction for 006 places the foreground knee below the belly rather than far to the right. The latest user message now approves all selected frames except 004. No native fitting or motion acceptance is recorded here.

[Successful prompts](successful-prompts.md) reproduces the complete request strings. Earlier failures and the [local handoff ZIP](local-generation-handoff.zip) remain unchanged as historical evidence; that ZIP predates these five successful calls.
