# SSUZY004 and005: read-only color analysis

The imported004 and005 drawings are noticeably less vivid than the approved003 and006 references. Their skin hue and saturation already agree closely. The largest differences are the darker, less saturated red hair and magenta swimsuit. A restrained color pass can improve consistency while preserving the exact poses, silhouettes and existing detail. No art was modified and no inference was run for this analysis.

## Inputs

Paths below are relative to art/cartoon/visitor-leg-pose-corrections-v2.

| Role | PNG | Size |
| --- | --- | --- |
| Selected004 | imported-004-v1/004-transparent-v1.png | 490 x304 |
| Selected005 | imported-005-v1/005-transparent-v1.png | 349 x206 |
| Approved003 | generation/SSUZY1.BMP/003-generated-v2.png | 1724 x912 |
| Approved006 | generation/SSUZY1.BMP/006-generated-v3.png | 1584 x993 |

All four are RGBA with alpha ranging from0 to255. The comparison excluded transparent pixels and the one-pixel silhouette boundary. Broad HSV material masks measured opaque interior colors. These are descriptive palette samples, not exact corresponding anatomical patches. Shading, pose, resolution and the different amount of each material affect the medians. Full numbers and masks are saved in ssuzy-color-statistics.json and analyze-ssuzy-color.py.

| Interior material | 004 HSV median | 005 HSV median | 003 HSV median | 006 HSV median |
| --- | --- | --- | --- | --- |
| Skin | 24deg /66% /93% | 24deg /66% /94% | 25deg /66% /98% | 27deg /66% /98% |
| Red hair | 1deg /83% /77% | 1deg /83% /76% | 0deg /92% /95% | 3deg /90% /94% |
| Magenta suit | 313deg /80% /70% | 318deg /80% /79% | 315deg /94% /95% | 304deg /92% /96% |
| Cyan glasses | 185deg /90% /61% | 182deg /82% /64% | 185deg /99% /76% | 186deg /98% /75% |

Skin median RGB is237/145/78 for004 and239/146/78 for005, compared with250/156/84 for003 and251/162/85 for006. The skin discrepancy is principally a small brightness lift, not a new skin color.

## Recommended deterministic adjustment

Use a new derivative of each selected PNG, preserve the pixel dimensions and every alpha byte, and apply only pointwise RGB transforms. Do not move pixels, resample, blur, alter the alpha outline, warp, redraw or run global histogram matching. Use smooth material-color weights, not binary masks with visible thresholds. Keep the original multilevel shading by transforming rather than replacing colors.

| Material | Conservative starting adjustment |
| --- | --- |
| Skin | Lift value about4%; shift hue only1-2deg toward golden orange if needed. Keep saturation essentially unchanged. Leave cream and gold outside this mask. |
| Hair | Lift value about12-16% and saturation about8-10%. Preserve the current red hue and dark red shading. Cap gently so bright highlights do not flatten to a single clipped red. |
| Suit004 | Lift value about12-16% and saturation about10-12%. Keep the hue close to approved003, roughly313-315deg. |
| Suit005 | Lift value about8-12% and saturation about10-12%. A small2-3deg shift away from red toward magenta can bring it closer to003. |
| Glasses | Lift value about5-8%, saturation about5% for004 and8% for005. Keep the existing cyan highlights and dark lens shading. |
| Gold jewelry, bottle and lotion | Preserve their color unless the side-by-side proof shows an obvious need. The tiny cream stream and dollop must remain intact. |

These ranges deliberately stop short of forcing every median onto the high-resolution reference. The reference suits themselves differ by roughly11deg of hue, so forcing both imports to006 would introduce an arbitrary color change.003 is the closer suit reference for these two imported drawings.

Do not apply a global saturation increase: the skin already matches and the bright cream/gold accents are easy to damage. Do not deepen all dark colors based on HSV value alone: dark red hair and warm skin shadows would be mistaken for outlines. If additional line contrast is needed, use only a modest low-luminance curve after checking at native size. Preserve colored shadow detail, especially fingers, sunglasses and the bottle nozzle.

## Limits of cleanup at this resolution

Color correction can preserve every current detail and make the small sprites more consistent with the pack. It cannot restore the high-resolution linework or missing small highlights from the larger references.004 is490x304 and005 is349x206; thin fingers, jewelry, lotion and outlines are already only a few pixels wide. Sharpening risks ringing and thicker or jagged contours, so I would omit it in the first candidate.

An alpha-preserving color pass also cannot remove any actual silhouette fringe or checkerboard residue by changing alpha. Removing such a defect would be a separate, localized edge edit and would no longer preserve the alpha byte-for-byte. The existing transparency imports should be retained for this first color candidate. Diagnostic flattening onto dark and light backgrounds can check the edge appearance without changing the candidate PNG.

If direct cleanup is authorized, verify the two source hashes are unchanged, each derivative has identical dimensions and alpha to its own source, the red-dot repair in005 remains intact, and the bottle/cream/fingers remain readable at native size. Compare next to003 and006 at the same displayed height. No broad repository or native-motion tests are needed for this reversible color-only review pass.
