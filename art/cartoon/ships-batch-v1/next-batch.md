# Next batch started: 28 campfire drawings

Preparation for the complete **FIRE1.BMP000-027** family started on 2026-09-18 after the 37-slot ship batch (33 new drawings and four source-preserved slots). The user said "approved, continue please" at the third tanker review, completing the ship group's scoped drawing approvals: tanker appearance and isolated source-replay rotation, plus the earlier appearance approval for the other 19 drawings. [Tanker acceptance](../tanker-motion-v3/acceptance/appearance-rotation-v1.json) preserves the exact scope and selections. Native export, registration and bulk integration remain pending for the ship artwork.

FIRE1 provides 28 distinct source slots in one coherent prop/effect family. All 28 now have generated drafts in the [campfire review](../fire-v1/README.md), with appearance approval pending. The source research below remains the basis for this group. Its isolated phase comparisons preserve the actual source order and layering; they do not establish complete scene integration.

Every exact original frame was visually inspected for this recommendation, using an in-memory nearest-neighbor contact sheet from `character-inventory-v1/reference-originals.zip`. The drawings contain wood/ember piles, smoke wisps, flames and a small outlined signal/impact graphic. No visible Johnny, other person, creature, occupied vehicle, unresolved anatomy, or placeholder was found. The existing `not_johnny` classification supports this finding but was not used as a substitute for inspection.

| Drawings | Count | Keep together |
| --- | ---: | --- |
| 000, 021–026 | 7 | Wood and ember piles at different stages |
| 001–004 | 4 | Narrow smoke/heat-wisp variants with open gaps |
| 005–008 | 4 | Small flame cycle |
| 009–012 | 4 | Medium flame cycle |
| 013–016 | 4 | Large flame cycle |
| 017–020 | 4 | Very large flame cycle |
| 027 | 1 | Outlined signal/impact graphic |
| Total | 28 | All source slots retained |

Use one shared wood/ember material and a consistent fire palette and contour style across all four flame sizes. Preserve each phase's original silhouette, separated sparks, transparent spacing and full canvas. The smoke frames are sparse wisps, not solid clouds. The final graphic is a real source slot, not an extra character or a reason to omit the family. Present all 28 in one appearance review with original comparisons; still drawings do not establish flame cadence or attachment to Johnny's fire-making actions.

The current pack contains zero FIRE1 entries. This batch excludes the 63 production assets, three separately approved environment screens, coconut drawings and pending shadows, the approved 24 props, and the 37 ship-family slots whose drawing approvals are now recorded. It does not borrow isolated pieces from mixed Johnny resources such as FIRE/FIRE4 or add fish/animal families merely because they are classified `not_johnny`.

## Existing action attribution

The saved resource map links FIRE1 to `MJFIRE.TTM`, associated with `BUILDING.ADS#5` (JOHN BUILDS FIRE) and `BUILDING.ADS#7` (EAT), at `src/data/story_data.h:87` and `:89`. Tags 39 and 41–44 attribute smoke and the four flame sizes; tags 82/83 describe a dying fire and embers. Tag 77 attributes frame 027 to the action labeled "disappointed". The separate `FIRE.TTM` resource also has static frame associations.

There are no ambiguous draw sites for FIRE1 in that saved map, but runtime reachability remains unproven. Frame 025 has no unique-slot draw attribution there; retain its visible wood pile without calling it executed or unused. Original palette colors are diagnostic, not verified original-executable colors. Final positions, layering, timing and native story interaction remain deferred to bulk integration.

## Source pins

Exact source members are `native/BMP/FIRE1.BMP/000.png` through `027.png` in the retained original archive. Its SHA-256 is `b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912`. Per-frame dimensions and identities are in `source/frame-index.json`, SHA `04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2`.

The read inventory SHA is `4689731fa6b2e4a734864a173f5dc5c1d932b5fbf94b91c054404e1d87881576`; the static resource-map SHA is `fc68bf58c57e8a70702654878cc7b42db667592c64cd1216a9e78199ec979ca3`. The inspected pack ledger SHA is `0dee75befeaa36abfab1952fb737392d18c50ad037fe85c2143583da4215c795`.

The initial selection-research task wrote only this recommendation file. The 2026-09-18 continuation records tanker approval and the completed FIRE1 draft batch. No FIRE1 approval or production integration is claimed.
