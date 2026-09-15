# Ocean, shadow and center-wave authoring checkpoint

This is the historical export checkpoint. The later full scene was approved;
see [the current acceptance record](../acceptance.json) for its exact scope.

This bundle preserves five selected independent assets for technical scene
preview. Full human runtime scene approval and production promotion remain
pending. The user's "its wonderful" approved the separate island concept.

`source-images.zip` holds the exact ocean, shadow v1 and center-wave 006/007/008
raw PNGs. Each selected image used original geometry and/or the approved concept;
none used another generated asset as a reference. The unused shadow v2 is
excluded from the binary bundle. Its exact prompt, source hash, measured alpha,
actual input order and rejection reason remain in `provenance.json`. Its first
reference was selected shadow v1, which is preserved. The six exact tool strings
are in `prompts/`; no final newline was added to those tool strings.

| Asset | Source and output canvases | Fixed transform |
| --- | --- | --- |
| Ocean OCEAN02 | 1448 x 1086 RGB -> 1280 x 960 RGB | Whole frame resized uniformly by 160/181; no crop |
| Shadow 014 | 1536 x 1024 RGBA -> 208 x 56 RGBA | Scale 0.235; guide center/top (768,400) -> (104,0.5) |
| Center waves 006, 007, 008 | Each 1536 x 1024 RGBA -> 320 x 50 RGBA | Common scale 0.249; guide center (768,512) -> (160,25) |

`recipe.json` records the source hashes, full affine matrices, original scene
origins and exact exported PNG hashes. The opaque ocean retained the concept's
4:3 frame and horizon near 31.25% after removal of all land, tree, shadow, cloud
and character objects. Resizing the complete frame is deliberate and does not
fit an arbitrary silhouette.

Shadow v1's raw alpha peaks at 133, above the prompt's requested 25-30% opacity.
The later contour edit produced broader alpha contamination, so v1 was retained.
Its fixed 0.235 scale makes the footprint 6% smaller than the initial 0.25 plan,
with the original guide's horizontal center and upper contact preserved. This
keeps its meaningful contour inside the original canvas without nonuniform
scaling, painting, alpha cleanup or clipping visible lobes.

The wave phases share one transform and use their corresponding original phase
as the first reference. At the initial 0.25 scale, frame 006 exceeded each side
by one quarter of an HD pixel. The complete center family received the same
0.4% reduction to 0.249 about its common center. No phase was independently fit,
moved, keyed or painted. Original solid sand and blue water are absent from
these foam layers; only delicate light curves and adjacent pale-cyan accents
remain. Judge phase rhythm, shoreline overlap and contact in the actual engine.

Run the exporter from the repository root with a new destination:

```powershell
python.exe -B art/cartoon/island-pilot-v1/ocean-shadow-center-waves/export.py --output build/art-work/ocean-shadow-center-reproduction
```

All five sources, original geometry members and expected output hashes are
checked before the first output is written. The helper does not package or edit
`assets/scrantic_data.zip`. Original exports used Pillow 12.3.0. The exporter
prints its actual Pillow version, and exact-byte comparisons decide whether
that runtime reproduces the record; `review-evidence/verification.json` lists
tested versions and isolated failure checks.

The ocean uses RGB Lanczos resampling. Transparent sprites use premultiplied
`RGBa`, an 8x bicubic affine transform, Lanczos reduction and straight RGBA output.
These recorded PNGs use compression level 6. Some raw alpha 1-7 exterior residue
is excluded by the finite output canvas; alpha 8 is only an inspection threshold.
No pixel values were artificially keyed, thresholded or made opaque. Inspect
numerical alpha and a colored composite before treating apparent raw-view glow
as a real background.

Original padded references are reproducible from the specified unchanged
members of the game archive. Convert to RGBA, repeat every pixel with the
recorded integer nearest-neighbor scale, paste without a mask onto the specified
transparent canvas, then save at PNG compression level 6. Their original and
reference hashes are in the recipe. The concept already exists in its own
tracked folder. Historical absolute paths preserve actual tool input/output
locations, while the exporter uses portable repository-relative paths.
