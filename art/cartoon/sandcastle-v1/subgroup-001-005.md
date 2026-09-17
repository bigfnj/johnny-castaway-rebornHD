# Sandcastle stages 001-005

Five independent built-in imagegen calls produced the raw drafts in `generation/001-generated-v1.png` through `005-generated-v1.png`. Each call used its own exact original nearest-8 guide first and the shared `000-generated-v1.png` second. Original references and the shared key are unchanged. Exact requests and per-frame records are saved beside the raw outputs; no CLI fallback was used.

The intended tower-count progression is visible: frame 001 has four towers, 002 has three, 003 has the outer pair, 004 has only the left tower, and 005 has no isolated towers. Warm cream/gold sand and brown outlines follow the shared key. These drafts do not establish exact original geometry: some doorway, window and crenellation details change between frames, and their subject silhouettes are wider relative to height than the originals. Frame 003 is the clearest wide/flat departure. Human review and final registration are pending; no deformation or fitting has been performed to hide these differences.

| Frame | Actual raw canvas | Alpha range | Main review limit |
| --- | --- | --- | --- |
| 001 | 1503 x 1047 RGBA | 0-255 | Four towers; side windows differ from 002 and the shared key |
| 002 | 1503 x 1047 RGBA | 0-255 | Three towers; relative wall and doorway proportions differ |
| 003 | 1647 x 955 RGBA | 0-255 | Two towers; visibly wider/flatter than the original |
| 004 | 1536 x 1024 RGBA | 0-254 | One tower; left battlements and front wall redrawn |
| 005 | 1428 x 1101 RGBA | 0-255 | No towers; rear wall is more regularly stepped |

The apparent brown halo in the raw viewer for 004 has alpha 0 at the sampled surrounding and doorway positions recorded in `004-record.json`. No visible-halo defect or correction is claimed. All generated alpha is preserved, including faint alpha 1 touching an image edge in 001, 002 and 005. Alpha-8 bounds are measurements only. The requested canvas and padding were not consistently returned.

This subgroup supplies artwork for the combined 24-item review. Basic visual inspection and dimension/mode/hash/alpha readback are the entire verification scope. No human question, runtime export, tests, native capture, production edit, staging or commit was performed here.
