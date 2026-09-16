# Independent protected material samples

`protected-landmarks-v2.json` is the current independent material witness manifest. It contains 222 points and 84 small regions across 28 sprites. `protected-landmarks-v1.json` is retained unchanged as earlier semantic evidence with three rejected coordinate labels, explained below. The input RGBA expectations were selected before reading the correction implementation, its masks, or any corrected export. The coordinates were proposed from the frozen images using broad appearance and position rules, then inspected visually on seven enlarged, numbered contact sheets covering all 28 sprites. Several initial gold proposals landed on eyebrows; visual review moved these to the actual hat band before freezing v1. Bright brown beard/hair samples and visible lower hair supplement the darker interior samples.

Coordinates use the original, unmirrored runtime PNG canvas, with zero-based x and y. Each sprite binds its frozen input file SHA256. Each point stores its original RGBA value. The small regions around interior hat white, hair/beard and shorts white store SHA256 of the decoded row-major RGBA bytes. Eye white and eye ink are sampled only when visible; the nine rear-view sprites explicitly record those roles as hidden.

These samples provide independent witnesses for material that must remain unchanged. They are deliberately sparse and do not prove that every protected pixel is unchanged. Whole-canvas alpha equality, equality outside the correction mask, independent mask inspection, and review of the corrected motion complement them. A failing protected sample must be reported against the unchanged manifest, not relocated to accommodate an implementation.

The ignored preparation contact sheets and proposal helper live under `build/skin-tone/protected-review-v1/`. The manifest's source hashes and exact expected pixels are sufficient to reproduce the protection comparisons without those scratch files.

## Documented semantic corrections

The first export changed three v1 samples labeled chest hair. A fresh inspection of the original images on pixel grids showed these coordinates were skin beside the hair, rather than protected hair. All 17 lower-hair samples were rechecked at that scale. V1 remains byte-identical; v2 records each old and new coordinate and original RGBA value. The points were not moved based on whether they passed a correction mask.

| Frame | Rejected v1 coordinate | Hair coordinate in v2 | Original-image finding |
| --- | --- | --- | --- |
| 004 | 55,54 | 54,54 | The old point sits on lighter mixed skin beside the brown strand. |
| 005 | 63,54 | 61,54 | The old point sits on shaded skin beside the brown strand. |
| 008 | 51,53 | 49,54 | The old point sits on torso-edge skin above and right of the strand. |

The other 14 coordinates remain unchanged. The role is now `lower-hair` for all 17 because several samples lie in the lower beard rather than chest hair. Other protected roles and every region remain unchanged. The retained input hashes and explicit coordinates allow this semantic decision to be reviewed directly from originals.

## Cap exclusion annotation

`protected-cap-polygons-v1.json` separately records a hand-traced lower cap boundary for every original sprite. All 28 boundary overlays were visually inspected against the frozen inputs. The protected area runs from the top of the canvas to this boundary and includes the white crown, gold band, anchor, dark brim, transparent space and a small adjoining hair/ink margin. It leaves the forehead below the boundary. Pixel-edge coordinates and a strict pixel-center membership rule avoid ambiguous inclusive polygon rasterization. Each row records the exact resulting binary-mask byte hash.

The corrector may use these polygons as explicit exclusions. Once used that way, cap-region equality verifies compliance with the specified exclusion; it is not independent proof that the contour selected the right material. The separately selected original-material points and visual contour review supply that independent evidence. No corrected output or correction implementation was read while drawing these boundaries.
