# Independent static low-tide draft review

Reviewed `art/cartoon/low-tide-v1/export_draft.py`, `build/low-tide-v1/static-export-v2/export.json`, the selected close-up, the previous close-up and `reference/original-static-crop.png`. This is a technical/static review before native and human scene review. No runtime/art edits, new gates, bulk suites or GUI launches were performed. Only this report was written.

The raised beach lip closes the three substantial ocean-colored seam holes visible in the preceding draft. The selected package and exports also match their declared inputs. No technical blocker was found for native review. This does not approve the artwork or prove its interaction with the twelve future waves.

## Package and export readback

The candidate is `build/low-tide-v1/static-candidate-v2.zip`, SHA256 `f46e5cac5508b00cc7a675be4eaf843029cebfeabe80c849c8fa5f311813b92b`.

Independent ZIP member/payload comparison found 2,600 unique members. All 2,598 production members retain exact bytes, including accepted000, high-tide waves, seasonal props and the existing manifest. The only additions are `data/styles/cartoon/BMP/BACKGRND.BMP/001.png` and `002.png`. No member was removed. Production archive SHA256 is `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`.

The exporter imports the existing seasonal premultiplied filter. It applies one uniform affine per raw source, then crops the declared canvas. It performs no contour painting, independent X/Y scaling or alpha thresholding. Both source hashes and runtime hashes match the report and candidate ZIP. An independent in-memory call through that same pinned filter reproduced both PNG byte streams exactly; no output was overwritten.

| Slot | Source and transform | Canvas and runtime alpha>=8 bounds | Cropped alpha |
| --- | --- | --- | --- |
| 001 | `shore-raw-v3.png`; scale0.525, translation(-24.7125,-202.175) | 768x138; [2,7,766,138] | Zero alpha>=8 pixels. 129 nonzero fringe pixels, maximum alpha4. |
| 002 | `rock-raw-v2.png`; scale0.164, translation(-60.066,-58.188) | 128x60; [0,1,128,60] | Zero alpha>=8 pixels. 36 nonzero fringe pixels, maximum alpha4. |

Bounds are right/bottom exclusive. The source alpha>=8 bounding rectangles map completely within their target canvases: beach [2.0625,7.3,765.9375,137.5], rock [0.614,1.344,127.386,59.4]. Fresh padded resampling independently confirms the crop counts above. This establishes meaningful-alpha fit, not lossless retention of every faint fringe pixel.

Runtime001 SHA256: `f2692720e9604e08ffdf65b850008d06a289c1775a97dfd68f513ab8e7ed62e7`.

Runtime002 SHA256: `a2eb23271a9429753873a86294c2f5db3f42f797eac586e74b53b5efa5541f5d`.

## Raised seam coverage

Visually, the prior draft exposed blue holes beneath the accepted upper island's dark outline. In the selected draft those locations contain beach material and the outline no longer encloses visible ocean gaps. The starfish, two shells and separate rock remain present, matching the original reference's object grouping. Original reference colors are diagnostic and are not a calibrated material-color target.

For an independent geometry check, I composited only the unchanged000 alpha and each version's001 alpha at their exact runtime origins, onto transparent memory surfaces. I found enclosed regions below alpha8 and measured the selected draft at the old gaps. This excludes ocean pixels and therefore cannot mistake a blue-painted or shaded material for actual missing coverage.

| Prior gap, world HD bounds | Pixels below alpha8 in prior gap | Selected combined alpha on those pixels | Exact witness, old to new alpha |
| --- | ---: | --- | --- |
| [684,654,731,661] | 173 | 251-253; none remain below8 | (705,657):0 to252 |
| [1034,672,1050,677] | 34 | 251-253; none remain below8 | (1040,675):2 to252 |
| [925,677,962,684] | 149 | 251-253; none remain below8 | (947,680):0 to253 |

The selected combined ground has no enclosed alpha<8 component of ten pixels or more. This is the measured threshold and area scope, not a claim about every possible subpixel edge or final native composition. The visible dark left/front boundary and bright sand bands are now painted material transitions rather than these former ocean holes.

## Remaining responsibilities before wave generation

- Static001 must own the raised upper join, exposed beach, front-bank material, starfish and shells. Keep accepted000 unchanged. Its overlap with001 intentionally hides the old upper-island contour; recreating that contour inside wave art would reopen the visual seam.
- Original low-wave frames contain changing sand/water/crest together. Decide what remains static in001 and what changes in each family before drawing the waves. If the new art is water/foam-only, leave the new beach underneath and preserve intentional wash over it. Do not apply an inverse-land-alpha mask by default, and do not duplicate semitransparent ground into every wave.
- Generate and inspect each family against these exact exported static PNGs at its actual origin. Preserve the distinct four-family timing and existing phase031's wider canvas. Native review must show every phase against the beach edge, not only a contact sheet of isolated waves.
- The separate rock's current alpha>=8 span is128 HD pixels versus114 HD pixels for the original doubled alpha footprint. Its canvas and left draw origin are correct, but its visible right extent is about14 HD pixels farther right. The039-041 ring therefore needs to be authored against the selected rock, including the right foot/contact, rather than assuming the original inner opening fits it. This is a geometry difference for review, not an export clipping failure.

The technical static composition deliberately omits waves, clouds, Johnny and holidays. Native capture must check the beach/rock contacts with existing waves first, then the candidate full cycle after generation. The unchanged high-tide view remains a useful exact control because this package adds only the two low-only slots.

## Inspected artifact identities

```text
art/cartoon/low-tide-v1/export_draft.py
260cfc364821aa04ff2529130142ea6dda4a7a76c8c35ffa69e4f3e66a2658fb
build/low-tide-v1/static-export-v2/export.json
a662ceb81d5aeea0cdccf23b3f47db46e3812188fc6488906d0885ad609b80a5
build/low-tide-v1/static-export-v2/static-closeup.png
45c3224e1c3948b5c1ad5e1c6604f4bfe9bee15c84549de1a6d0047d1a1d2056
art/cartoon/low-tide-v1/reference/original-static-crop.png
0a0c7a02ec18d85e29aa64a76752f41cb4d028de6bcf6ec88f0cbffcfb956aee
build/low-tide-v1/static-export-v1/static-closeup.png
2b645b16c535c8ffac17816011b013f5eeff9b161f4de5560647cca02da91c63
```
