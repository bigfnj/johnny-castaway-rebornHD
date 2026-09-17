# Coconut prop reference preflight

This is lightweight art-preview preparation for COCONUTS.BMP 000-006. The existing visual inventory classifies all seven as non-Johnny: four coconut orientations and three independent cast shadows. No character or vehicle artwork is part of this resource. No generation, runtime/package changes, captures or full validation were performed.

Exact original PNGs are `reference/original-000.png` through `original-006.png`; exact current HD proxies are `reference/hd-000.png` through `hd-006.png`. `original-contact-sheet.png` is copied from the previously reviewed inventory atlas. `original-vs-hd.png` compares original x8 with HD x4 at equal displayed geometry scale, retaining complete canvas boundaries. The original and HD colors shown there are geometry references, not a natural coconut-color target.

Use `reference/approved-palm012-runtime.png` for the approved coconut material and brown palette already present in the Cartoon palm. It is the exact 304 x 138 BACKGRND012 production PNG, SHA256 `701fc7909c3cc150ece7125c04f493f27da75d07446cc43cc6acae70fde1aa18`. `000-original-guide.png` is an exact nearest-neighbor enlargement of original 000 at 32x, placed at (256,224) on a transparent 1024 square. The original 16 x 18 canvas becomes 512 x 576. Its nominal guide-to-HD mapping is scale 1/16 with translation (-16,-14); this describes the guide, not a fit approval for an unseen generated image.

| Frames | Role | Original canvas | Runtime canvas |
| --- | --- | --- | --- |
| 000,001 | Coconut orientations | 16 x 18 | 32 x 36 |
| 002,003 | Coconut orientations | 24 x 16 | 48 x 32 |
| 004 | Small cast shadow | 16 x 5 | 32 x 10 |
| 005 | Medium cast shadow | 16 x 7 | 32 x 14 |
| 006 | Wide cast shadow | 24 x 7 | 48 x 14 |

Preserve the complete original canvas and origin for every frame. In particular, 002/003 have visible content only through logical x18 inside a 24-wide canvas; those six right-hand columns are intentional registration space. Do not crop or auto-center the silhouette. The standard 2x sprite path supplies these fixed runtime canvases with no special footprint or offset. Keep each shadow a separate transparent drawing; do not bake a ground shadow into 000-003 or move the scripted positions.

The retained scene map attributes COCONUTS.BMP to script slot 3 in MJCOCO.TTM. Tag 18, "falling coconut", uses 000/004/005/006; tag 19, "coconut to the left", uses 000/001/002/003/005/006; tag 20, "coconut bounce right", uses 000/001/002/003/005. These tags are referenced by VISITOR.ADS#4, "COCONUT DROP L & R", in `src/data/story_data.h:138`. Tags 23 and 34 also use the family for chase/360 actions. MJREAD.TTM has separate coconut shake/drop uses.

The source has explicit independent coordinates. At MJCOCO.TTM offsets 284/294, tag 18 draws coconut 000 at logical (423,148) and shadow 004 at (431,290). The next coconut position is (423,165) while the shadow stays (431,290). Tag 19 begins with coconut 002 at (418,263) and shadow 005 at (421,289), offsets 524/534. These examples establish separate falling/bouncing and ground-shadow motion. The recorded SET_DELAY instructions are local script facts, not a measured executed duration.

A later bounded motion preview can use falling plus left/right bounce to cover all seven drawings, retaining existing scene actors. The current records establish static unique-slot script attribution; they do not claim a newly executed sequence or complete story reachability proof.

`reference/source.json` binds all copied PNGs, the original frame/index/XPM identities, current archive and source scene-map files. Originals come from the retained supplied-original PNG archive. They use the port diagnostic palette with BMP index0 transparent; original-executable colors and compositing are not established. The approved palm reference, rather than the diagnostic red pixels, sets the new coconut material.
