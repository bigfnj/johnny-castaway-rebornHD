# Cartoon high-tide side waves: scene-review candidates

This is the historical export checkpoint. The later full scene was approved;
see [the current acceptance record](../acceptance.json) for its exact scope.

These six transparent foam sprites are technically exported and awaiting the combined island scene review. The concept was approved with "its wonderful". That approval does not cover runtime layer placement or wave motion. Production assets are unchanged.

The source bundle contains only the six selected generated PNGs. Each was generated from its exact original geometry reference and the approved island concept. No generated ancestors were used. The rejected first 003 attempt is described in provenance, with its exact prompt and source hash; its unused raw binary is omitted.

The source references are untouched nearest enlargements with transparent padding. Sparse 4x padding led the first generation to enlarge the foam; 8x improved the treatment, and 10x made placement more predictable. Numeric prompts still did not lock the curve endpoints.

The left family uses one uniform 0.097 transform and the right family one uniform 0.09 transform, both around their fixed padded-canvas center. This is a deliberate family placement choice for review. It is not automatic fitting, per-frame scaling or character registration. Every alpha>=8 source stroke fits its original runtime canvas. Raw alpha 1-7 exterior residue is retained wherever the finite output canvas includes it. No synthetic keying, alpha painting or background removal was applied.

The white-foam extent differs from the originals, especially the high tip in 005 and longer left tail in 009. The combined scene must establish whether the strokes follow the sand edge and whether the phase changes read naturally.

Run `python -B art/cartoon/island-pilot-v1/side-waves/export.py --output <new-directory>` from the repository root. Pillow is required. The helper reports its installed version and checks every recorded PNG hash in memory before writing any output. It writes six PNGs only, with no archive repacking or production promotion. Original geometry bytes are verified against the existing shared archive. The recorded outputs and source hashes are authoritative; no reproducible image-generation seed or model identifier was exposed.

`review-evidence/verification.json` records byte-exact positive reproduction, original-reference reconstruction and isolated refusal mutations. It is technical evidence, not human scene acceptance.
