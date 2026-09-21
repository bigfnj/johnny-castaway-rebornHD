# SSUZY1 006 and 007 draft corrections

Use v1 for both frames in this family, pending human review. These are ordinary beach-action sprites of a fully adult visitor. The new 000 identity reference supplies red hair, turquoise sunglasses, gold jewelry, opaque pink two-piece swimwear and cartoon linework; it does not supply these body poses.

Each exact original nearest-neighbor image was inspected together with the new identity reference and the prior visitor-source-notes.md. In 006 the image-left arm bends to hold the bottle upright while the other hand rests at the raised knee. The torso is raised and mostly frontal; the second leg remains folded low across the foreground. In 007 the image-left arm lowers the held bottle toward the ground while the other forearm lifts an empty palm above the raised image-right knee. Its foreground leg folds toward image-left before the foot extends inward. Both images show two connected arms and two distinct legs.

Exact request arguments were saved before each built-in image generation call. record_output.py copied each raw result unchanged and recorded reference, request and output hashes. No artistic postprocessing was used.

| Frame | Output SHA256 | Canvas | Alpha>=8 bounds | Edge alpha maximum |
| --- | --- | --- | --- | --- |
| 006 v1 | bbfe8f0518061c68c701cb5dca1de2b9c2465e80f50f08b38434238c2d194413 | 1586x992 | 72,2,1519,980 | 6 |
| 007 v1 | e042e3b0600f864831fdc7b3749b8fb6795a8a3e4082759ffba3c7208aff564c | 1625x968 | 114,6,1537,947 | 2 |

Both are RGBA with alpha range 0 to 255. Light and dark actual-alpha composites beside the originals were inspected in build/visitor-006-007-alpha-review.png. Hair has narrow upper padding, with only faint alpha below8 touching the canvas edge; no visibly cut contour or halo was found. Pink opaque top and bottoms are present in both poses. No native fitting or animation check was performed. No generation refusal occurred.
