# Offshore center-wave comparison

These built-in image_gen drawings implement the earlier offshore-only approach.
They are retained for the user's explicit side-by-side comparison request, not
selected as production art. Their exact prompts remain historical evidence.

The user subsequently clarified that original waves wash onto the sand. In
particular, the earlier statement that lifting foam onto the beach was wrong
applied to this proposal, and is not a rule for the original or the new incoming
water study. Blanket ground-exclusion masking cannot reproduce incoming wash.

`generation.json` and `generation-007-v2.json` preserve the prompts, references
and original PNG hashes. Phase 007 uses `007-v2-raw.png`; the first attempt is
retained. `export.py` and `recipe-v1.json` preserve the intermediate 356 by 102
draft. The comparison uses `export_v2.py`, `recipe-v2.json` and `candidates/v2`:
all center phases share a 384 by 256 canvas with offset [-32, -90]. This is the
entire source canvas at one quarter scale, with no individual fitting or crop.

The comparison keeps foam outside sand through the historical alpha visibility
mask. Ground and side-wave bytes are unchanged from the parent integrated
candidate. The incoming study uses the same registration with no such mask.
