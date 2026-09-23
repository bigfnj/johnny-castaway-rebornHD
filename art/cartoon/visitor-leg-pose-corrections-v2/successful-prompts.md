# Successful prompts

The latest 004 v10 request reuses the successful 005 action with approved 003 as the lowered-leg reference. It returned no image. [Exact latest request](generation/SSUZY1.BMP/004-v10-request.json) · [Recorded response](generation/SSUZY1.BMP/004-v10-failure.json). The returned prompts and images below remain historical.

The current returned edit is 005 v2, with a bent elbow and the sunblock bottle moved above the other cupped palm. [Exact prompt and ordered references](generation/SSUZY1.BMP/005-v2-request.json) · [Returned image](generation/SSUZY1.BMP/005-generated-v2.png). It is a partial correction: the elbow remains too high to read as supporting her weight. The focused v3 elbow edit returned no image. 004 v9 also returned no image, leaving the [direct composite](direct-composite-004-v1/004-composite-v1.png) as the prior reference with its torso proportion unresolved. The successful generator prompts below are retained as history.

These are the complete, verbatim arguments.prompt strings from six saved built-in image-generation requests. Reference order is the original submitted order. Links point to the existing exact images; no new image copies are made. Returned output does not by itself imply appearance approval. The user rejected 004 v2's leg overlap; 004 v3 below replaces that candidate.

## 004 v3: right leg beneath left

[Exact request JSON](generation/SSUZY1.BMP/004-v3-request.json) · [Returned image](generation/SSUZY1.BMP/004-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/004-record-v3.json)

Request SHA256: `4cff0bd1f710e7d56da550baef09763886be5f607b36f73c6c350c7c49cdf3bd`

1. [Edit target: 004 v2](generation/SSUZY1.BMP/004-generated-v2.png)
2. [Approved leg pose: 003 v2](generation/SSUZY1.BMP/003-generated-v2.png)
3. [Original 004 for overlap](../workers-and-mermaids-batch-v1/reference/original/SSUZY1.BMP/004.png)

```text
Edit image 1, the adult redheaded cartoon woman wearing pink swimwear and holding a lotion bottle. Change only the legs. Use the reclining leg pose in image 2 (approved frame 003): her LEFT leg is uppermost, bent at a low knee, with its lower leg folding back toward the right. Her RIGHT leg rests slightly UNDER the left leg, with its calf and foot visible just below the overlapping left lower leg. Keep the two legs close together in a relaxed side-resting pose; the left shin should slope upward toward the right as in image 2, rather than both shins running separately side by side as in image 1. Image 3 is the original frame 004 and clarifies the small overlap. Preserve image 1's entire upper body, both hands on the bottle, face, red hair, sunglasses, earrings, bracelets, opaque pink swimsuit, cartoon linework, colors and shading. Keep two naturally connected legs and two distinct feet. Full character, transparent background, no text.
```

## 003 v2

[Exact request JSON](generation/SSUZY1.BMP/003-v2-request.json) · [Returned image](generation/SSUZY1.BMP/003-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/003-record-v2.json)

Request SHA256: `ed4ba936f829cf0351995f9ca54f9a1d92377da65927b6f2081234accd39d1d0`

1. [Edit target and complete pose: earlier 001](../workers-and-mermaids-batch-v1/generation/SSUZY1.BMP/001-generated-v1.png)

```text
Edit this adult redheaded cartoon woman in opaque pink swimwear. Remove the separate lotion bottle and the loose cap in her raised hand, then bring that now-empty forearm a little inward toward her supporting hand. Keep her existing pose, both legs and feet, face, hair, sunglasses, jewelry, swimsuit coverage, proportions and drawing style unchanged. Preserve the transparent background and the complete uncropped silhouette.
```

## 004 v2

[Exact request JSON](generation/SSUZY1.BMP/004-v2-request.json) · [Returned image](generation/SSUZY1.BMP/004-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/004-record-v2.json)

Request SHA256: `40a390033f257dfae743d67e875fd9272ea9ff4538ec8d1ab11e388027cbb8c3`

1. [Edit target: previous 004](../worker-visitor-mermaid-fixes-v1/generation/SSUZY1.BMP/004-generated-v1.png)
2. [Leg-pose reference only: earlier 001](../workers-and-mermaids-batch-v1/generation/SSUZY1.BMP/001-generated-v1.png)

```text
Edit the adult redheaded cartoon woman in pink swimwear in image 1. Keep her upper body, hands holding the lotion bottle, face, hair and jewelry unchanged. Change only her legs to the relaxed side-resting arrangement in image 2: the nearer leg bends to a low knee, with its shin returning toward the right, while the other leg extends right behind it. Keep two naturally connected legs and two feet without the current unnatural crossing. Preserve the opaque swimsuit coverage, proportions, drawing style, complete silhouette and transparent background.
```

## 006 v3

[Exact request JSON](generation/SSUZY1.BMP/006-v3-request.json) · [Returned image](generation/SSUZY1.BMP/006-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/006-record-v3.json)

Request SHA256: `eacf4f6aff906dd602118e03d6f9c6ed2f718afc1a8b02075d3d6634560f46bb`

1. [Edit target: current 006 v1](generation/SSUZY1.BMP/006-generated-v1.png)
2. [Folded-leg reference: exact original 006, enlarged nearest-neighbor](../workers-and-mermaids-batch-v1/reference/nearest8/SSUZY1.BMP/006.png)

```text
Edit the first image of an adult red-haired woman in an opaque pink swimsuit, turquoise sunglasses and gold jewelry. Correct only the foreground leg: its knee belongs directly below the belly-button area near the lower-left outline, not far to the right. Make a short foreshortened upper thigh slope down-left from the hip to that knee, then a distinct bend with a slimmer lower leg extending down-right toward the existing foot. Use the second image only for this folded-leg pose. Keep the upper body, other raised knee, bottle, hands, swimsuit coverage and crisp cartoon style unchanged. An ordinary seated beach pose with two anatomically coherent legs, genuine transparency and clear margins.
```

## 009 v3

[Exact request JSON](generation/SSUZY1.BMP/009-v3-request.json) · [Returned image](generation/SSUZY1.BMP/009-generated-v3.png) · [Generation record](generation/SSUZY1.BMP/009-record-v3.json)

Request SHA256: `e2be9e7adaef560adddc5a03a5d084b610eaf39ed59dfe95856f7386fe71b18b`

1. [Edit target and accepted leg join: 008 v2](generation/SSUZY1.BMP/008-generated-v2.png)
2. [Hand/action guide only: 009 v1](generation/SSUZY1.BMP/009-generated-v1.png)

```text
Edit the first image, an adult red-haired woman in an opaque pink two-piece swimsuit, turquoise sunglasses and gold jewelry. Keep its corrected folded foreground right leg and its attachment to the hip unchanged. For the next animation pose, extend the other leg a little farther toward screen-right and move the hand from the knee to just below the knee, as in the second image. The second image is only a hand/action guide, not a replacement for the first image's leg anatomy. Remove the separate bottle. Preserve the supporting hand, face, clothing coverage, colors and crisp cartoon style. Ordinary seated beach pose, two coherent legs, genuine transparent background, full figure with clear margins.
```

## 010 v2

[Exact request JSON](generation/SSUZY1.BMP/010-v2-request.json) · [Returned image](generation/SSUZY1.BMP/010-generated-v2.png) · [Generation record](generation/SSUZY1.BMP/010-record-v2.json)

Request SHA256: `40db99d99a17675811e09aa53c152c387e434fc148fa8385dedc27ad081e6af0`

1. [Edit target and leg anatomy: successful 009 v3](generation/SSUZY1.BMP/009-generated-v3.png)
2. [Forward-lean and ankle-reaching action guide only: previous 010](../worker-visitor-mermaid-fixes-v1/generation/SSUZY1.BMP/010-generated-v1.png)

```text
Edit the first image for the next animation pose. Keep this adult red-haired woman's corrected folded foreground leg and its hip attachment unchanged. Lean her torso a little farther forward and move her reaching hand down from the shin to the ankle, following the action in the second image. The second image is an action guide only; preserve the first image's leg anatomy and supporting hand. Keep the opaque pink swimsuit coverage, turquoise sunglasses, gold jewelry, red hair and crisp cartoon style. Ordinary seated beach pose, no bottle, genuine transparent background and clear margins around the complete figure.
```

The earlier [handoff ZIP](local-generation-handoff.zip) is unchanged. Its blocked and unsubmitted statuses describe the snapshot taken before these calls.
