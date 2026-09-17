# Seasonal reference images

These are the four supplied-original HOLIDAY.BMP frames and their current HD
counterparts. Source PNGs are exact archive members. The original colors come
from the port diagnostic dump palette, not a calibrated original-executable
capture. Neither reference set is approved new Cartoon art.

| Frame | Drawing | Native canvas | Runtime canvas | Guide canvas | Offset | Original scale |
|---|---|---|---|---|---|---|
| 000 | Pumpkin | 40x34 | 80x68 | 1024x1024 | 352,376 | 8 |
| 001 | Clovers | 120x47 | 240x94 | 1536x1024 | 288,324 | 8 |
| 002 | Christmas tree | 56x65 | 112x130 | 1024x1024 | 288,252 | 8 |
| 003 | New Year banner | 152x47 | 304x94 | 1536x1024 | 160,324 | 8 |

`NNN-original-native.png` retains the exact original PNG; `-original-nearest8`
is an unpadded nearest-neighbor enlargement. `-original-guide` places that
enlargement on the transparent guide canvas. Native pixel edges map to
`offset + 8 * [x,y]`. Nothing is fitted to its visible silhouette.

`NNN-hd-native.png` retains the exact production HD PNG. Its guide uses nearest
4x at the same placement and physical size as the original. Only the HD guide
and contact sheet apply the runtime's opaque RGB168,0,168 transparency key;
the archived HD-native files remain untouched. Gray shadow pixels are retained.

The contact sheet shows originals at 4x and HD at 2x on a neutral background.
The larger individual guides are the inputs intended for image inspection.

Reproduce with Python 3.11 and Pillow 12.3.0 from the repository root:

```text
python -B art/cartoon/seasonal-v1/prepare_references.py --output build/seasonal/references
python -B art/cartoon/seasonal-v1/prepare_references.py --check
python -B art/cartoon/seasonal-v1/reference/test_references.py --phase smoke
python -B art/cartoon/seasonal-v1/reference/test_references.py --phase regression
```

The preparation command refuses an existing output. `source.json` binds the
source index, reference archive and current production archive. If production
later changes, recover the historical ZIP from Git and pass its location with
`--production`; its exact hash must still match the recorded input. Reference
PNG and decoder ancestry remain in the complete character inventory bundle.

The regression independently checks every nearest8 source-pixel replication and
guide registration, rejects a wrong source archive and altered guide, then runs
a copied helper with the output identity guard removed. The same damaged guide
passes only that executed mutant. The real references and helper stay unchanged.
