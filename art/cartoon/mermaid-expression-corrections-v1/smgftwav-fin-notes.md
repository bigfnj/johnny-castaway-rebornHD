# SMGFTWAV003 and007 fin underside correction

The user identified the green areas as the undersides of the fins entering the ocean. Earlier drawings misread them as bulky raised tail branches with scale patches and an exposed central stalk.

Exact original003 was inspected with neighboring002/004 and the selected drawings. Original007 was inspected with006/008 and the selected drawings. Original000/001/005 were also checked to understand the exposure sequence. The originals control the phase; neighboring cartoon drawings supply palette context only. No animation timing was inferred from consecutive filenames.

Both frames received a built-in image_gen edit followed by one focused anatomy repair. All four requests and successful outputs were saved, with exact references and byte hashes in record_output.py records. No generation was blocked. No artwork was postprocessed. No gallery, selector, SBREAKUP drawing or approval was changed here.

## Candidates for review

| Frame | Preferred candidate | Visual assessment |
| --- | --- | --- |
| SMGFTWAV003 | generation/SMGFTWAV.BMP/003-generated-v2.png | Broad darker ribbed underside is now visible under the nearer folded fin; the nearer tip dips into the water and the farther lobe curls away. Scale patches are removed and the right rim is lower than v1. It remains a stylized, broad arch with two visible water contacts. That interpretation needs user review against the tiny original; do not label the geometry conclusively approved. |
| SMGFTWAV007 | generation/SMGFTWAV.BMP/007-generated-v2.png | The two curled rims sit over a joined broad fin underside, with no separate long cylindrical stalk. Dark green membrane planes and rays read more clearly than the bulky prior lobes. The lower fin surface is occluded by the water-contact edge. Ready for user comparison, not approved. |

v1 outputs remain as history.003 v1 raised the farther lobe too high and both v1 drawings still suggested narrow stalks. The targeted v2 requests explicitly prioritized the exact original silhouette and a submerged shaft.

## Image checks

003 v2 is1536x1024 RGBA, alpha0-254, alpha>=8 bounds[131,287,1460,785], edge alpha0. Its raw RGB contains glow outside the sprite, but that area is transparent. smgftwav-003-v2-proof.png confirms the composited result has clean edges on a dark solid background; the proof is diagnostic only.

007 v2 is1642x958 RGBA, alpha0-255, alpha>=8 bounds[372,229,1293,810], edge alpha0. Both candidates have clear visible margins and preserve lime/emerald green fins with white/cyan water contact. Production placement, native animation and user approval remain separate.
