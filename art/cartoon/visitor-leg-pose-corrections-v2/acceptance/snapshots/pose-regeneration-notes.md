# Pose regeneration notes

The five calls below returned images using concise, literal edit descriptions and explicitly assigned reference roles. They preserve the adult visitor's established clothing coverage and Cartoon identity. This records what was submitted; it does not establish why earlier attempts were blocked or guarantee future results.

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

The user's acceptance of 008 v2 concerns its leg join; it supplied the anatomy reference for the 009-to-010 progression. The specific correction for 006 places the foreground knee below the belly rather than far to the right. These five new results still require their own appearance review; no native fitting or motion acceptance is recorded here.

[Successful prompts](successful-prompts.md) reproduces the complete request strings. Earlier failures and the [local handoff ZIP](local-generation-handoff.zip) remain unchanged as historical evidence; that ZIP predates these five successful calls.
