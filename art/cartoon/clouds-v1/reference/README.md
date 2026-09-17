# Original cloud references

These are technical references, not generated artwork or an approval. The six `*-original.png` files are exact PNG members from the preserved complete original inventory. Their RGBA pixels also match the selected native XPM dumps from the supplied `RESOURCE.MAP` / `RESOURCE.001` pair. Original transparent index 0 remains alpha 0; every other original pixel remains alpha 255.

The original colors use the port diagnostic palette. They do not establish the original executable's calibrated colors. The untouched `*-hd.png` files are separate appearance references and are not substitutes for original geometry. The contact sheet keys only the HD display copies' opaque magenta background.

| Slot | Original canvas | HD canvas | Guide integer scale | Guide offset in 1536 x 1024 |
| --- | --- | --- | --- | --- |
| CLOUDS 000 | 208 x 74 | 416 x 148 | 6 | 144, 290 |
| CLOUDS 001 | 104 x 34 | 208 x 68 | 12 | 144, 308 |
| CLOUDS 002 | 96 x 17 | 192 x 34 | 14 | 96, 393 |
| CLOUDS 003 | 56 x 20 | 112 x 40 | 20 | 208, 312 |
| BACKGRND 016 | 192 x 57 | 384 x 114 | 6 | 192, 341 |
| BACKGRND 017 | 264 x 76 | 528 x 152 | 5 | 108, 322 |

The guide scale differences make small originals inspectable. They are not proposed runtime transforms. `original-hd-style-contact.png` uses a common physical scale: original x2 and HD x1. The accepted BACKGRND 015 context is the exact 256 x 72 production PNG, shown x2 in the contact sheet and separately x4 in its enlarged reference. The root bundle's `style-reference/` holds its approved generated ancestor.

Visual distinctions:

- CLOUDS 000 is a broad main mass with a central high crown, trailing wisps and a lower-right opening. CLOUDS 001 is a smaller, compact triangular mound. CLOUDS 002 is a low narrow wisp; CLOUDS 003 is a small separate puff. Their canvas dimensions and original PNG identities differ.
- BACKGRND 016 is one broad mound with a thin taper to the right. BACKGRND 017 includes a wide main mass, a detached middle-right wisp and a separate lower-right puff. Preserve these separated pieces when using the original as a shape guide.
- The six current HD files are not exact nearest-neighbor replicas of the supplied originals. The measured alpha/RGB differences are retained in `verification.json`; BACKGRND 017 has identical doubled alpha but 820 visible RGB pixels differ. BACKGRND 016 has four alpha differences and 352 visible RGB differences. This is why the native originals remain the geometry authority.

Ordinary moving island clouds use BACKGRND 015, 016 and 017 in `src/engine/island.c` (`cloudNo = rand() % 3`, draw slot `15 + cloudNo`, mirrored for one wind direction). The preserved `character-inventory-v1/scene-map/resource-map.json` records no TTM load associations, native sites or proven runtime reachability for CLOUDS.BMP. This reference extraction does not claim those four CLOUDS slots are an animation or reachable story weather.

Replay from the repository root with the toolbox Python:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/reference/prepare.py --check
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/reference/verify.py
```

`prepare.py` accepts `--production`, `--original-root` and `--dump-root` for relocated pinned inputs. Its production reference is the prior `a8987430...` archive at commit `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc`. After a later production promotion, replay against a separately recovered copy of that archive with `--production`; do not replace the live production ZIP. The original ZIP and index are tracked; the supplied binary pair and historical native dump remain external and are not duplicated here. A fresh destination can be populated with `--output`; existing outputs are never overwritten by that CLI.

Verification passed fresh replay, an actual wrong-archive source-pin refusal naming the original ZIP, then a restored positive process. It independently checks every RGBA pixel cell of all six guides and all 21 PNG hashes. No engine run, decoder rerun, source-removal mutant or broader gameplay verification is claimed.
