# Shoreline geometry and style references

These are deterministic reference preparations for BACKGRND 003, 007 and 009. No drawing, material removal, recoloring, alpha cleanup or production replacement was performed. All guides are transparent `1536 x 1024` PNGs; black areas in a viewer may represent transparency.

| Frame | Runtime canvas | Runtime origin | Guide offset | Nominal guide-to-runtime transform |
| --- | --- | --- | --- | --- |
| 003 | 144 x 58 | 540,612 | 480,396 | scale .25, translate -120,-99 |
| 007 | 320 x 50 | 728,638 | 128,412 | scale .25, translate -32,-103 |
| 009 | 144 x 64 | 1036,606 | 480,384 | scale .25, translate -120,-96 |

Each frame has four files:

- `original-native-geometry.png`: supplied original resource decode at nearest 8x, equivalent to the native canvas doubled to runtime and then enlarged 4x. Use this for original shapes and ground coverage.
- `original-hd-geometry.png`: existing HD PNG at nearest 4x. This retains its exact colors/alpha and allows comparison with the current HD fallback.
- `cartoon-geometry.png`: current Cartoon wave PNG at nearest 4x. This is the current foam style reference; the absent sand is the defect being repaired.
- `cartoon-scene-context.png`: actual current Cartoon island crop, with 32 runtime pixels around the wave canvas, enlarged nearest 4x and centered. This shows the desired sand/sea appearance. It is style context, not proof that the captured phase equals the filename's frame. That phase was not instrumented in the source capture.

Both original geometry guides deliberately retain the original yellow/olive sand, blue water, gray edge and foam. Those colors come from the port's decoded diagnostic palette and are not desired Cartoon colors. The sand area must not be discarded again during generation. Match the current warm sand and sea appearance using the context image while preserving the original placement envelope. Source alpha and diagnostic colors remain unchanged in these guides.

`source.json` pins the source archives, current native capture, all guide files, exact nearest scale/offset, and the executed builder. It records 12 exact pixel replication/padding checks, two damaged-image controls with the expected named failures, and a restored positive. `build.py` reproduces the guides from a checkout containing the pinned production archive and the reconstructed island-footprint scratch capture. It refuses overwriting existing guide files; run it in a disposable checkout/reference directory when reproducing. Do not overwrite historical evidence.

The source coverage audit counted only opaque original yellow/olive pixels, excluding ambiguous gray/white. Extra native ground pixels outside base000 are 003:211, 004:181, 005:156; 006:396, 007:288, 008:162; 009:63, 010:46, 011:43. The combined per-source ground union reaches world bounds `[285,279,569,334)` compared with base-only `[288,279,567,331)`. This supports local sand-bearing wave corrections within their existing canvases; a base000-only expansion cannot include that union while retaining its original canvas and origin. Per-source unions do not claim every phase is simultaneously visible or establish the original executable's timing.
