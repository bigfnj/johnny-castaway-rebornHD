# Sandcastle frames006 through010

Five separate built-in imagegen calls produced the untouched draft files `generation/006-generated-v1.png` through `010-generated-v1.png`. Two requested targeted edits then produced009-v2 and010-v2. The selected draft set is006,007,008 v1 plus009 and010 v2. Each output is1536 by1024RGBA with alpha ranging from0 to254. Matching request and per-frame record JSON files preserve the complete prompt, ordered input hashes, exact raw hash, actual dimensions, and alpha measurements. All first versions remain unchanged.

The exact original and nearest8 reference for each frame were inspected before generation. The shared castle key was also inspected and matched its supplied SHA256 `d2314cc0259424837ca8d895c1a91a25d992761b083efe898fd144429f25a1ef`. It supplies the cream/gold material and restrained Cartoon shading. Original diagnostic yellow and gray are geometry cues, not intended colors.

| Frame | Original canvas | Draft content | Alpha8 bounds, exclusive right/bottom |
| --- | --- | --- | --- |
| 006 | 120 by40 | Sparse wide sand scatter, upper-middle and right clusters | 25,197 to1501,806 |
| 007 | 104 by47 | Loose rising arc of separate grains | 36,170 to1511,903 |
| 008 | 176 by105 | Two upper sprays and a denser lower-center cluster | 38,114 to1451,894 |
| 009 v2 | 128 by95 | Taller diffuse spray, denser toward the bottom, with complete lower grains | 67,50 to1407,1011 |
| 010 v2 | 80 by48 | First collapse state with restored brown contour and crease lines | 24,98 to1514,935 |

Frame009-v1 has29 pixels with alpha at least8 on its bottom edge, with maximum alpha245. Lower grains were visibly cut by that boundary. The requested009-v2 edit removes that meaningful clipping: it has no alpha8 pixels on any edge, and its meaningful bottom bound is1011, leaving13 rows. The padding is smaller than requested but the visible particles are complete. Only alpha1 residue reaches its bottom edge. The other selected frames also have no alpha8 pixels on any canvas edge;008 has only alpha1 residue at its bottom edge.

Frame010-v1 looked softly painted beside the outlined castle family. Its requested v2 adds warm dark-brown outer contours and selected interior crease lines while retaining the recognizable jagged collapse form, holes, palette, and debris tail. These are generated edits, so no claim of exact pixel preservation outside the requested change is made.

The grain drawings are fuller and rounder than the original one-pixel particles, and the generated layouts do not exactly obey the requested occupied boxes. This is visual draft art, not a verified particle-coordinate replacement. Frame010 preserves an irregular tall collapse silhouette rather than turning into a smooth final pile. No new character or intact castle was added to006 through009.

A temporary neutral-background inspection of008 showed separated grains and transparent gaps. The large gold cloud visible in the raw dark-matte display is chiefly hidden RGB. Low-alpha residue is still present and has not been removed. The original RGBA bytes are retained exactly; alpha8 is only an inspection measurement, not a threshold or crop applied to output pixels.

No export, package, native review, tests, runtime changes, or approval claims are included in this subgroup. All five selected files are ready for draft family review; native scale, registration, and sequence continuity remain deferred.
