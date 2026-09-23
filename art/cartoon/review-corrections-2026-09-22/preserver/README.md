# Life preserver corrections for review

Five built-in imagegen edits address SMGIFT 037, 038, 039, 041 and 043. They are candidates awaiting user review, with no production integration or motion approval.

The original sprites establish a white flotation ring with a yellow perimeter rope. The new design keeps a white padded ring, soft gray underside and narrow inner sidewall, a truly transparent opening, and a continuous golden-yellow twisted rope held by small attachment loops. Frame 041 established the design reference for this pass.

Frame 039 contains the ring, its rope, a single hand gripping the rim and the existing waterline. The erroneous hair and cyan hairband have been removed. No head, body or extra arm is visible.

Each numbered folder contains the exact request, candidate PNG, and a record with SHA-256 input/output pins. The manifest supplies the focused HTML review. Existing drawings were not overwritten.

All outputs were visually compared with the previous drawing and original sprite. Every output is RGBA. Actual alpha is zero at sampled interior-hole points in 037, 038, 041 and 043. Frame 037's visible alpha>=8 bounds are (37, 5, 1487, 1039) on a 1502x1047 canvas, leaving its upper rope contour visible.

`prepare.py` was the initial manifest setup and should not be rerun over completed review state. `finalize.py` records the current outputs and alpha checks without changing image pixels.
