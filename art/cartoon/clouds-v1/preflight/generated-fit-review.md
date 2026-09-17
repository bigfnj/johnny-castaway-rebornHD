# Generated cloud fit review

Both v2 drawings are suitable for the proposed native inspection. Neither loses source content at alpha >= 8 under the requested fixed transforms. This is a diagnostic measurement, not an alpha threshold applied to an image. No images were edited, exported or resampled in this review.

Inspected all four `generation/016-generated-v{1,2}.png` and `017-generated-v{1,2}.png`, the two original nearest-neighbor guides, approved015 raw and runtime art. The white lobes, pale blue lower shading and dark outline are consistent with approved015. The 017-v2 drawing preserves the distinctive detached upper-right streak and internal opening; v1 is too tall and wide for this registration. The 016-v2 revision is visibly flatter than both v1 and the original. Its silhouette area is about 11.3% smaller than the original, so the reduced lower mass should remain visible for human judgment in the native scene.

Measurements use source pixel-edge bounds, mapped uniformly by the supplied transforms: 016 scale21/64, translation[-63.3125,-111.546875]; 017 scale25/64, translation[-37.28125,-130.640625]. Bounds are exclusive at right/bottom. Original comparison area is the original alpha>=8 count multiplied by4 for its exact2x logical canvas.

| Drawing | Mapped alpha>=8 bounds in runtime pixels | Area versus original | Source alpha>=8 cells crossing canvas |
| --- | --- | --- | --- |
| 016-v1 | [-1.297,-2.938,379.000,114.203] | 98.93% | 749; outside alpha reaches254 |
| 016-v2 | [1.000,1.000,379.328,105.016] | 88.70% | 0 |
| 017-v1 | [-9.547,-14.234,534.594,156.078] | 118.39% | 8,083; outside alpha reaches254 |
| 017-v2 | [1.000,1.000,524.828,145.922] | 99.75% | 0 |

Original016 occupies bounds[0,0,384,114], area23,728 HD pixel equivalents. Original017 occupies[0,0,524,152], area44,988. Selected016-v2 occupies378.328x104.016 within384x114, leaving approximately9 pixels below;017-v2 occupies523.828x144.922 within528x152, leaving approximately6.08 pixels below. The v2 area comparison is21,046.445 and44,875.793 HD pixel equivalents respectively. Bounding boxes describe extent, not identical contour or original-engine appearance.

There is sparse lower-alpha source residue outside the destination: 213 source pixel cells for016-v2, maximum alpha2;83 for017-v2, maximum alpha1. No alpha>=8 content crosses a boundary. The large glow visible when inspecting raw hidden RGB should not be treated as an opaque halo: actual alpha determines visibility. These measurements do not authorize thresholding, color-keying or trimming. The actual premultiplied export must still measure its filtered fringe and disclose any cropped nonzero alpha; a source-edge calculation does not prove exact post-filter bounds.

Source SHA-256 values:

```text
016-generated-v1.png ac050efc79af1738c1ee848bf3f7d522f8eae0fface6906bfd022a77552da22d
016-generated-v2.png f16bd7802c23c3dd6040e8d5ddd181ad880e87ecf23e071bb004b9690a52be4e
017-generated-v1.png 5e09450ceb5568446a3a3400592aead9e6e10526b871afccf675ac6900e8a70f
017-generated-v2.png c9343aa097d1700cb736287e2e9af36ceaf6affec799913368171fb85c987a58
```

The recommendation is technical readiness for native review, not human approval. Check both wind orientations and the nighttime backdrop alongside unchanged015, especially016's flatter lower contour and the transparency around017's separated streak.
