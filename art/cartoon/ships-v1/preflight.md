# SHIPS reference grouping

All 21 original slots and their existing HD counterparts are copied exactly under `reference/original/` and `reference/hd/`. `reference/nearest8/` contains nearest-neighbor enlargements, and the original and HD contact sheets preserve full canvases. `reference/source.json` records archive, individual PNG, guide, source-index, scene-map and approved BOAT000 style identities. Original diagnostic colors are geometry cues, not verified original-executable colors.

| Frames | Original canvas | Visual subject and constraint |
| --- | --- | --- |
| 000 | 32 by 8 | Tiny asymmetric stepped silhouette, thin projection left and broad end right; exact subject remains uncertain |
| 001 | 24 by 8 | Related small silhouette with a narrow light vertical band |
| 002 | 32 by 10 | Related notched silhouette with a narrow light vertical band |
| 003 through 006 | 160 by 34 | Matching lower hull and water strips, stern left and pointed bow right, changing water phase |
| 007 | 168 by 102 | Upper sailing-ship component, three masts, rigging and sails, ending at a deliberate lower cut |
| 008 and009 | 168 by 136 | Complete bow-right sailing ship and water, distinct sail states |
| 010 through 013 | 8 by1 | Each contains exactly one opaque black pixel at0,0 and seven transparent pixels |
| 014 | 16 by 12 | Small warm burst |
| 015 and016 | 16 by 10 | Two distinct burst shapes |
| 017 | 24 by 17 | Lobed pale smoke with gaps |
| 018 | 8 by 4 | Tiny dark mark; preserve its sparse extent |
| 019 | 16 by 15 | Larger dark near-round projectile-like form with a highlight |
| 020 | 8 by 8 | Smaller dark rounded projectile-like form |

The existing inventory classifies these as not_johnny, and the inspected originals show no identifiable Johnny or other occupant. That classification does not prove that each slot is executed or independent of other scene layers.

The saved static map links 003 through 008 to GJLILIPU.TTM tag 18 and MJSAND.TTM tag 35, LILIPUTS SAIL IN. It links 009 through 013 and 018 to rowing-related actions, and009 plus 014 through 018 to cannon actions. Frames 000 through 002 and 019 through 020 lack unique-slot action attribution. The map records 200 ambiguous draw sites for the resource and leaves runtime reachability unproven.

The saved static draw-site table shows that 007 and the lower strips are coupled components. For example, GJLILIPU.TTM tag 18 draws 007 at logical minus66,243 at decoded offset 412, then 003 at minus95,339 at offset 422. The strip begins 96 logical rows below the upper component; later rows cycle 004,005,006 alongside007. These are source observations, not a newly executed timing or alignment proof. The parts must be registered together during integration, rather than independently fitted as unrelated boats.

Frames 010 through 013 are retained byte-for-byte in `source-preserved/` with a separate record: source-preserved 1-pixel slots; runtime role unproven. They are not labeled proven unused or proven placeholders, and no image generation is performed for them.

The copied approved BOAT000 image is a contour/color style reference only. Its motorboat geometry must not replace the original sailing vessel. Water, direction, mast tips, empty rigging gaps and the component cut need to survive later export. No tests, native capture, runtime edits or production-package changes were part of this reference preparation.
