# Static palm, sand and cloud authoring checkpoint

This is the historical export checkpoint. The later full scene was approved;
see [the current acceptance record](../acceptance.json) for its exact scope.

These four sprites are cleared for technical engine preview after inspection of
the static assembly. Full human runtime scene approval and production promotion
remain pending. The user's "its wonderful" approved the separate island concept.
It did not approve these independently generated sprites or their runtime contact.

The bundle contains four selected raw PNGs and two generated palm ancestors.
The six unchanged files total 5,899,340 bytes in `source-images.zip`. Ten exact
tool prompts, their actual ordered reference lists and every attempt's measured
geometry and alpha are preserved in `provenance.json` and `prompts/`. The four
rejected variants have no binary copy here; their prompts, source hashes,
measurements and rejection reasons remain recorded. No original-resource PNG,
duplicate concept, runtime export or game archive is included in the ZIP.

| Sprite | Selected source | Exact runtime canvas | Scale | Registered raw landmark -> local HD position |
| --- | --- | --- | --- | --- |
| Sand 000 | sand v1 | 560 x 104 | 0.49 | rear crest (811,407) -> (298.5,0) |
| Canopy 012 | canopy v2 | 304 x 138 | 0.24 | central crown (811.5,244) -> (156.25,0.5) |
| Trunk 013 | trunk v3 | 48 x 290 | 0.24 | ground tip (489,1342) -> (17.5,289) |
| Cloud 015 | cloud v1 | 256 x 72 | 0.25 | left contour/top tower (254,364) -> (0,0) |

The runtime origins and full affine matrices are in `recipe.json`. Cloud's
(624,116) scene origin describes the initial pilot capture; its runtime position
continues to move. Sand is deliberately 2% smaller than the initial 0.5 drawing
scale, and the static palm pair is 4% smaller than its initial 0.25 scale. These
choices followed measured contour overflow and explicit authorization. They are
fixed design choices for these static pieces. They do not alter the approved
walking family's registration or permit automatic fitting of arbitrary bounds.
Cloud keeps its initial scale, with a measured translation of +0.5 HD pixels
horizontally and +1 HD pixel vertically relative to the padded reference origin.

The trunk's top begins about 12 HD pixels below its canvas top at the chosen
scale. The native-size palm composition shows it concealed by the canopy's
coconut and leaf cluster, with no visible gap. Its ground tip remains registered.
The canopy's lowest meaningful contour reaches 132.5 of 138 HD rows. Sand's
meaningful shoreline is approximately 3.03 HD pixels inward at the left and
6.66 inward at the right relative to the original alpha bounds. Its rear crest
midpoint is retained, but its nearly level crest interval is narrower. Inspect
the actual route, foot contact, tree occlusion and waves before scene acceptance.

`export.py --output <new-directory>` reproduces all four recorded PNG hashes
before writing output. It reads only this source bundle and the four original
geometry members of `assets/scrantic_data.zip`; it never packages or changes the
production archive. For example, from the repository root:

```powershell
python.exe -B art/cartoon/island-pilot-v1/palm-sand-cloud/export.py --output build/art-work/static-reproduction
```

The original palm exports used Pillow 12.2.0; sand and cloud used 12.3.0. Each
asset retains that historical version in the recipe. The exporter prints its
actual runtime version, and its expected-byte checks determine whether that
runtime reproduced this record. Verification results name the versions actually
tested. Technical sampling uses premultiplied `RGBa`, an 8x bicubic affine
transform, then Lanczos reduction and straight RGBA PNG output. It applies no
artistic edits, alpha thresholding, color keying or forced opaque interiors.

The geometry references can be reconstructed from the recorded original ZIP
members: convert to RGBA, enlarge with the recorded integer nearest-neighbor
scale, paste without a mask onto the transparent padded canvas, then save a PNG
at compression level 6. The recipe records each source hash, offset, canvas and
resulting reference hash. Pixel repetition was checked against every original
RGBA pixel. Actual local tool paths are retained only as historical provenance;
reproduction uses repository-relative paths. The generator exposed no seed or
model identifier, so the saved raw PNG bytes identify the drawings.

The attempted local contour edits did not consistently stay local. Trunk v2
shifted the whole tree up; canopy v3 shortened a tip too far and added real
exterior alpha contamination. Sand v2 moved its crest in the wrong direction,
and fresh sand v3 became wider. The original-first trunk v3 recovered placement
but still exceeded the initial canvas by 0.75 HD pixels. These failures motivated
the documented static scale decisions instead of further numeric contour edits.

Displayed glow can be hidden RGB under zero alpha. Inspect alpha values and a
colored composite before requesting extraction. These selected raw interiors
peak at alpha 254, and scattered alpha 1-7 residue remains. Alpha 8 is only the
inspection threshold used for measured contour fit; no source pixels were keyed
or repainted. Finite output canvases exclude some very low-alpha exterior residue.
