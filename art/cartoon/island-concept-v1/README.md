# Cartoon island concept 1

`concept.png` is a generated environment direction for human review. It uses the
approved character's ink and cel shading with blue-green water, warm sand and
natural green palm fronds. The actual prompt, ordered references and source hash
are in `provenance.json`. Built-in image generation was used; no seed or model
identifier was exposed.

This is a flattened concept, not a runtime scene capture. It is not approved for
production. Its overall 4:3 composition follows the existing island, but exact
silhouettes and ground placement must be reconciled when authoring independent
sprites. The small Johnny in this concept was regenerated; the separately
approved six walking sprites remain unchanged.

The first controlled scene requires 15 background assets: OCEAN02, sand 000,
trunk 013, canopy 012, shadow 014, cloud 015 and high-tide waves 003 through 011.
Keep their original engine canvases and placements. Ocean contains only sky and
sea, while the other elements remain separate. Generate all nine high-tide wave
frames together as an authoring phase and review their independent family timing.

The palm is drawn again over Johnny on the actual D-to-E and E-to-D routes.
Prefer opaque leaf and trunk interiors with narrow antialiased edges, and test
those routes for contact and compositing. The approved E-to-A cycle does not
exercise this path. Other tide, cloud, ocean and nighttime states remain outside
this first scene's coverage and need explicit fallback review.
