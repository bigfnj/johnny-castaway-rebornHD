# Original arrival 018 reference

These two PNGs preserve the exact reviewed extraction bytes for original
`JOHNWALK.BMP/018`. Native RGBA is 32 by 77; the larger PNG replicates each pixel
into an 8 by 8 block with nearest-neighbor sampling. Neither is the HD proxy.
The diagnostic palette and index-0 transparency come from the decoder; original
executable colors and compositing remain unverified.

[source.json](source.json) binds the files to the original RESOURCE hashes,
reviewed decoder identity and frozen [walking reference](../../walk-expansion-v1/reference/source.json).
[metadata.json](metadata.json) preserves the original frame facts. The existing
extraction was verified and copied; commercial RESOURCE files were not reread for
this copy. All reference hashes cover exact bytes.

The first opaque row is y=0 and spans x=[6,11), whose pixel-edge midpoint is 8.5.
Doubling gives the same x=17 runtime cap target as the accepted rear family.
The y=0.25 target remains a deliberate small filtering margin, not an original
anatomical landmark. Runtime canvas is 64 by 154. Keep the established uniform
0.1 source scale; do not fit the body or align bottoms to the taller 023 canvas.

Original 018 and original 023 have identical first 23 decoded RGBA rows. This
compares original pixels, not original 018 against the approved Cartoon 023.
Visually, 018 is a rear-oblique stationary pose facing screen-left, with bent
elbows and hands at the shorts/pocket area. The compiled walker calls these wait
poses "hands in pockets". The approved Cartoon 023 supplies style guidance, but
its lowered near hand and lifted trailing foot are movement features to change
for arrival. No anatomical left/right identity is assigned here.

In the reviewed direct B-to-A route, final 022 draws at (302,244), then 018 at
(298,240) in native coordinates. The (-4,-4) shift is encoded in the original
walk data. Excluding pixels whose alpha is zero and exact gray shadow pixels
RGBA=(128,128,128,255), the last remaining visible row is 70 for 022 and 73 for
018. Their global row positions are therefore 314 and 313. This qualified
pixel/outline observation does not establish an anatomical sole or ground line.

Frame 018 appears in all six wait blocks at NW heading 3, and flipped at NE
heading 5. Its matching turn image is 023. Completing 018 alone does not complete
the other wait/turn directions or any entire scripted story scene. See the
[original image comparison](../../../../docs/knowledge-base/original-image-comparison.md)
for decoder evidence and its limits.
