# SSUZY bottle continuity correction

The latest user feedback restores the sunblock bottle in frame 003's hand and requires the ground bottle to remain in exactly the same position through 009 and 010. This supersedes the earlier request to remove the bottle from 003.

## Frame 003

Built-in imagegen returned [003 v3](generation/SSUZY1.BMP/003-generated-v3.png). It restores the small amber bottle with yellow nozzle in the low hand near the resting foreground forearm. The selected face, reclining body, overlapping legs and palette are retained closely. The returned image is a 1724 by 912 RGBA PNG with alpha 0 to 255 and fully transparent canvas edges. The exact [request](generation/SSUZY1.BMP/003-v3-request.json) and [record](generation/SSUZY1.BMP/003-record-v3.json) preserve both input references and the unmodified output hash.

This is a new candidate awaiting appearance review. The prior v2 approval remains linked to the exact previous output, and other selected images are unchanged. The [appearance sheet](review.html#frame-SSUZY1.BMP-003) compares the earlier bottle-free v2 with the new v3.

## Frames 008, 009 and 010

Original 008 already contains the ground bottle inside the body sprite. The original animation draws a separate SSUZY2.BMP frame 001 bottle at scene coordinates (173, 297) for 009 and 010. The prior comparison viewer omitted supplementary props, creating the visible disappearance. The archived prop's 118 nontransparent pixels match its embedded copy in original 008 exactly.

The unfinished builder prepares metadata to restore this separate layer in Original and reuse the existing bottle from cartoon 008 at its same displayed position for 009 and 010. The intended drawing is a reused canvas source region, not a regenerated prop or a change to the body PNGs. Production runtime integration remains separate from this review viewer.

September 23 checkpoint verification: the served [animation comparison](color-sequence-review.html) still has schema-2 data with no `ground_bottle` entry or rendering, and does not include 003 v3. The ground-bottle fix and 003 candidate still need to be connected to that viewer. Preserve the approved upright-bottle 004 and the user's exact selected partial 005 v2; the later 005 color candidate is superseded.
