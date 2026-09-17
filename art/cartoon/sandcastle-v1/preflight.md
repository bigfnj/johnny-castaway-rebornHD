# Sandcastle reference preparation

All 15 `SANDCAST.BMP` slots are included. The existing visual inventory classifies the complete resource as `not_johnny`: castle stages, collapse piles, and airborne sand. These sprites accompany character actions but contain no Johnny. This preparation extracts references and static script associations only. No game capture, production change, or validation gate was run.

Frame **000** is the best complete key: the five-tower castle with its pointed central roof and front arch. Match the approved Cartoon island's warm sand, shading, and dark outline while retaining this original structure and perspective. Use `reference/nearest8/000.png` for geometry and `reference/approved-island-000.png` for style. The root-owned aliases `reference/original-000.png` and `reference/approved-island000-runtime.png` contain the same source bytes and are bound in `reference/source.json`.

The diagnostic contact sheet is `reference/original-contact.png`. It shows each full original canvas at nearest-neighbor 2x on a dark background. Individual nearest-neighbor 8x guides are in `reference/nearest8/`; exact PNG members are in `reference/original/` and `reference/hd/`. Original diagnostic yellow/dithered colors are not the canonical palette.

| Frame | Original canvas | Existing HD canvas | Visible subject |
| --- | --- | --- | --- |
| 000 | 72x57 | 144x114 | Complete five-tower castle |
| 001 | 72x48 | 144x96 | Castle without central pointed tower |
| 002 | 72x48 | 144x96 | Lower tower stage |
| 003 | 72x40 | 144x80 | Two towers and front wall |
| 004 | 64x39 | 128x78 | One tower and front wall |
| 005 | 48x37 | 96x74 | Front wall and arch |
| 006 | 120x40 | 240x80 | Sparse airborne sand |
| 007 | 104x47 | 208x94 | Curved airborne sand trail |
| 008 | 176x105 | 352x210 | Broad airborne sand spray |
| 009 | 128x95 | 256x190 | Tall airborne sand spray |
| 010 | 80x48 | 160x96 | Castle beginning to slump |
| 011 | 56x29 | 112x58 | Rounded collapse pile with arch remnant |
| 012 | 48x21 | 96x42 | Smaller mound |
| 013 | 40x11 | 80x22 | Low flattened mound |
| 014 | 80x37 | 160x74 | Wider collapsed castle with right debris |

For three review groups of five, use **000–004**, **005–009**, and **010–014**. For parallel authoring after the common 000 key is available, use **001–005** for construction, **006–010** for airborne sand and first collapse, and **011–014** for the remaining collapse states. The root owns the shared key. This avoids regenerating it in each group.

Keep each slot's full canvas and original registration. In particular, 008 has transparent top and left padding; its visible bounds are `[7,13,151,94]` inside the 176x105 original canvas. Airborne effects must remain detached particles and trails, not become a second castle or a solid mound. Construction and collapse variants should inherit the same sand material and surviving architectural details from 000.

## Static action references

The preserved script map associates this resource with `MJSAND.TTM`, used by `BUILDING.ADS#1` and `BUILDING.ADS#2` (`src/data/story_data.h:83` and `:86`). This is static attribution, not proof that every frame executes in either story. All 33 attributed draw sites, their logical coordinates, nearby delay instructions, and original source hashes are retained in `reference/static-actions.json`.

| Tag | Action label in source | Attributed sandcastle frames |
| --- | --- | --- |
| 3 | build castle | 008, 009 |
| 5 | castle grows | 000–005, 012, 013 |
| 7 | johnny kicks castle | 006, 009, 011, 014 |
| 8 | johnny stomps castle | 006, 009 |
| 10 | castle dissolves | 011–013 |
| 13 | castle built at A | 000 |
| 14 | johnny pause with ca | 000 |
| 15 | castle wilts | 000, 010, 014 |
| 17 | from castle to A | 006, 008, 009 |
| 40 | SANDCASTLE KNEE TO S | 000 |
| 41 | PAUSE WITH SHIP | 000 |

The linear tag-5 draw order is 013, 012, 005, 004, 003, 002, 001, 000, with differing per-frame positions. The completed castle draw is at logical `(297,256)`. Tag 15 draws 010 at `(297,264)` and 014 at `(297,275)`, preserving the ground level through collapse. Do not bottom-align or center all canvases independently during export. Frame 007 has no unique-slot draw attribution in the existing map; it remains in the requested 15-frame art pass.

## Source identity and limits

`reference/source.json` binds every exact copied original and HD PNG, all dimensions and visible bounds, the nearest-neighbor guides, the contact sheet, the approved style image, and the source metadata. The original and HD copies agree with all 15 historical inventory hashes.

| Input | SHA-256 |
| --- | --- |
| `character-inventory-v1/reference-originals.zip` | `b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912` |
| Current `assets/scrantic_data.zip` | `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d` |
| Original frame index | `04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2` |
| Complete original 000 PNG | `acbabcb5b597ba01bd6211783e8ec4fe90d4c61f3843228cc0a2a5b497ceb2b7` |
| Approved Cartoon island 000 PNG | `22b426952abb1877e7c77111da0f4f0826dc86ff7a993c4390156c0f55166d9d` |

The supplied-original index planes were previously rendered with the port diagnostic dump palette, with BMP index 0 transparent. This preparation reuses those PNGs. It does not rerun the original executable or establish original palette, compositing, runtime reachability, or timing parity. The current 640x180 Cartoon island image is a style reference only; its footprint and shape do not define the sandcastle exports.

Reference preparation can be reproduced with toolbox Python and `reference/prepare.py`. It reads the named local archives and metadata, writes only its owned reference outputs, and leaves the root-owned aliases unchanged. Bulk smoke, regression, and story review remain deferred under the current art-first workflow.
