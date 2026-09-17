# Proposed next standalone-prop batch

Queue **37 transport and ship slots** after the current 24-item review is approved. This keeps three complete resource families together and supplies a coherent vessel/material pass without adding Johnny or unresolved occupants. This is a queue recommendation, not artwork approval or authorization to promote assets.

| Resource | Exact frames, inclusive | Count | Existing inventory finding |
| --- | --- | ---: | --- |
| `TANKER.BMP` | `000-013` | 14 | Ship directions; all classified `not_johnny` |
| `GJPROW.BMP` | `000-001` | 2 | Ship bow/hull pieces, including an anchor emblem; all `not_johnny` |
| `SHIPS.BMP` | `000-020` | 21 | Distant vessels, sailing ship, projectiles and bursts; all `not_johnny` |
| Total | 37 distinct resource/frame slots | 37 | No uncertain, placeholder or Johnny-classified slots |

The tanker and bow pieces share the visitor-ship sequence, so their hull identity should be designed together. The complete SHIPS family keeps sailing/rowing forms and their small projectile/effect companions in one review. Tiny effects remain real source slots; do not replace them with extra ships or discard them as unused. None of these 37 paths is present in the current Cartoon pack ledger. The inventory's `excluded` status means excluded from the Johnny-drawing inventory, not already authored or proven unused.

This selection excludes the current BOAT, MRAFT, SANDCAST and idea-symbol batch, the separately approved coconut drawings, and mixed aircraft resources such as GJBIPLAN/GJVIS3 with unresolved occupants. It also leaves other character families, even those classified as non-Johnny, outside this standalone-prop pass.

## Existing runtime attribution and its limits

The [static resource map](../character-inventory-v1/scene-map/resource-map.json) attributes all TANKER frames to `GJVIS6.TTM` tag 9, "voldeez wanders", and both GJPROW frames to tag 8, "tanker arrives". The associated story is `VISITOR.ADS#3`, "VISITOR 6". These two resources have zero ambiguous draw sites in that saved analysis.

For SHIPS, the same map resolves sailing frames `003-008`, rowing-related frames `009-013,018`, and cannon/effect frames `009,014-018` through actions in `GJLILIPU.TTM` and `MJSAND.TTM`. It also records 200 ambiguous draw sites for this resource. Frames `000-002,019-020` have no unique-slot action attribution in that report; retain them for complete-family artwork, without claiming they are executed or unused. Resource-level links to sleeping/Lilliput stories do not prove that every frame plays there.

These are existing static associations, not new native captures. The map explicitly leaves runtime reachability unproven. Original canvas registration, waterlines, direction/mirroring, scale changes, effect timing and attachment to surrounding scenes still need checking at bulk integration. A complete visual family does not establish a complete executed sequence.

## Selection sources

The selection reuses [the current inventory](../character-inventory-v1/inventory.json) and the saved [root](../character-inventory-v1/classification/root-family.json), [GJ](../character-inventory-v1/classification/gj-family.json) and [S](../character-inventory-v1/classification/s-family.json) classifications. Their reviewed atlas pages are `TANKER.BMP-01.png`, `GJPROW.BMP-01.png` and `SHIPS.BMP-01.png`; no new visual classification was performed for this proposal.

Exact originals are retained in `character-inventory-v1/reference-originals.zip` at `native/BMP/<resource>/<NNN>.png`, with per-frame identities in `source/frame-index.json`. Their diagnostic palette establishes geometry, not verified original-executable colors. The read inventory SHA256 is `4689731fa6b2e4a734864a173f5dc5c1d932b5fbf94b91c054404e1d87881576`; the static resource-map SHA256 is `fc68bf58c57e8a70702654878cc7b42db667592c64cd1216a9e78199ec979ca3`.

Only this recommendation file was created. No images, exports, tests, package changes or commits were produced.
