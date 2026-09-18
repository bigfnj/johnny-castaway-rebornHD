# Recommended next batch: 25 food, boot and raft drawings

Prepared on 2026-09-18 after the FIRE1 appearance review. This is a source-based recommendation, not artwork approval or runtime acceptance.

Recommend 25 drawable slots across FIRE2, FIRE5 and SRAFT. The first two continue the campfire food/boot material family; the bare raft and paddle provide two standalone companions and can reuse the approved MRAFT material style. All 30 original slots in these three resources were visually inspected from the retained original PNG archive. The 25 proposed drawings contain no visible person. Two additional slots are character grip overlays and three are marker placeholders; neither group should receive new prop artwork.

| Resource and exact frames | Drawable count | Source content |
| --- | ---: | --- |
| FIRE2.BMP 001, 002, 012, 013, 014, 017, 018, 020 | 8 | Seven whole-fish poses and a tail-only piece, 018 |
| FIRE2.BMP 004, 005, 009, 015, 016, 019, 022, 023 | 8 | Rotated, folded and upright boot states; 019 is toe/sole-only |
| FIRE2.BMP 006, 007, 021, 024 | 4 | Red cephalopod poses and compact cooking/eating states |
| FIRE5.BMP 000, 001, 002 | 3 | Cephalopod, boot and fish companions |
| SRAFT.BMP 000, 001 | 2 | Rope-bound log raft and separate long paddle |
| Total | 25 | Includes two known mirrored companion slots |

## Preserve the five excluded FIRE2 slots

FIRE2 000, 003 and 008 are identical 8x1 marker images, each with original PNG SHA-256 `ce67ab53d15a75966b00793da79ca4329be8b39565ebd8dc8c05c44f59d19f99`. Preserve the exact source slots; do not turn them into drawings or silently omit them.

FIRE2 010 and 011 are small grip/hand overlays, not generic food fragments. The existing inventory labels them `not_johnny`; this recommendation explicitly corrects that interpretation without editing the inventory. In MJFIRE.TTM tag 47, boot 023 is drawn at (428,265), offset 4236, then 010 at (438,264), offset 4246. Tag 49 draws fish 013 at (436,267), offset 3434, then 010 at (437,263), offset 3454. The same overlay accompanies squid in tag 48. An original-pixel composite with the mirrored JOHNWALK body shows the patch completing Johnny's grip over the prop. Frame 011 is the smaller companion grip used during the fish arrival. Keep both with the character carrying action as source references only. A later inventory correction should retain this scene evidence.

Thus the review can show 25 proposed drawings plus clearly labeled source-only placeholders and grips if useful. It should not claim 30 new prop drawings.

## Identity and authoring guidance

The fish is a stylized round-headed, large-eyed fish with a forked tail, a small dorsal fin and broad patterned fins. No real species can be established from these pixels. Preserve each original angle, mouth direction, curve and tail separation. Original 018 is only a detached tail, not an incomplete full fish to repair. A shared green fish with warm yellow/orange fins and a cream-white eye is a reasonable proposed palette, but the original diagnostic green/red/yellow colors are not calibrated original-executable color evidence.

The red animal is a cephalopod. Source labels call the carrying/cooking action squid and the eating action octopus. Use one round-headed, large-eyed red/orange identity with curled tentacles; do not redraw its segmented compact forms as fish bones. FIRE2 006 is a useful whole-animal key. FIRE2 021 and 024 are part of this same animal's action.

Use FIRE2 023 as the upright boot key: chunky rounded toe, dark charcoal upper, cuff/lining, short shaft and small fastening details. The diagnostic art has a red cuff, yellow fastening dots and gray highlights. Preserve rotations and the folded/flattened states without inserting a foot or leg. FIRE5 001 faces the other way. The exact visible alpha-bbox pixels of FIRE5 001 mirror FIRE2 023; FIRE5 000 similarly mirrors FIRE2 024. Full PNG bytes and canvas padding are different. Keep these two pairs visually identical apart from the authored reflection and source registration. FIRE5 002 is a distinct fish drawing, not a copy of FIRE2 020.

SRAFT 000 is a 128x39 bare raft of lashed logs; 001 is a separate 112x19 paddle. No occupant, sail, mast or scenery is present. Use [the approved MRAFT drawings](../raft-v1/README.md) as material/style context, while retaining these exact original silhouettes, log bindings and paddle angle. The earlier MRAFT approval does not approve these new SRAFT drawings.

## Scene attribution and integration limits

FIRE2 is loaded into MJFIRE.TTM slot 5 at offsets 3300, 4118 and 4900 in tags 49, 47 and 48, labeled brings fish, brings boot and brings squid. The saved map records 134 ambiguous draw sites because that script also reuses slot 5 for FIRE3. The same-tag loads and original-pixel compositions support the grip interpretation above; the generic resource map alone is not an executed frame trace.

The saved static commands give these prop orders, with separate Johnny drawings interspersed:

| MJFIRE tag | Source label | Slot-5 prop frame order |
| --- | --- | --- |
| 70 | J EATS FISH | 020, 020, 001, 017, 013, 018 |
| 72 | J eats boot | 022, 005, 004, 016, 016, 019 |
| 78 | eats octopus | 021, 021, 024 |

Do not turn numeric frame order into a loop. FIRE2's loaded action is associated with BUILDING.ADS #5 and #7 through MJFIRE.TTM. FIRE5 has no TTM load or native draw association in the retained map; that is an attribution limit, not proof it is unused. SRAFT belongs to SJLEAVES.TTM tags 1-4, associated with MARY.ADS #5, JOHNNY LEAVES. Its paddle and raft require their separate native origins and layer order.

Final fits must preserve each original full canvas and transparency, including tiny tail/toe fragments and the two mirrored companions' different padding. Prop placement must still meet the source-only grip overlays. Native scene registration, scale, layering, timing and bulk integration remain pending. No production art, archive, runtime, approval record or classification file was changed for this recommendation.

The earlier aircraft alternative was visually inspected but deferred: it splits across uncertain pilots/crews and mixed scene resources. This food/boot batch plus the two raft companions is the more coherent immediate follow-up.

## Exact source bindings

All original members use `native/BMP/RESOURCE.BMP/NNN.png` in the pinned archive below. Per-frame PNG and RGBA identities and source canvases are recorded in the pinned frame index/inventory. All 25 proposed IDs are absent from the current 63-asset pack. The production archive remains `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d`.

| Input under character-inventory-v1 | SHA-256 |
| --- | --- |
| `reference-originals.zip` | `b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912` |
| `source/frame-index.json` | `04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2` |
| `inventory.json` | `4689731fa6b2e4a734864a173f5dc5c1d932b5fbf94b91c054404e1d87881576` |
| `classification/root-family.json` | `fd28ab80af7e34714999109f98330bb95f00270f7d246b31c835c2b5db83f690` |
| `classification/s-family.json` | `1d8f89faa9925344f55fd89395f043da83ac9951592e598aac101fd94e9b306a` |
| `scene-map/resource-map.json` | `fc68bf58c57e8a70702654878cc7b42db667592c64cd1216a9e78199ec979ca3` |
| `scene-map/static-draw-sites.json` | `2892a584a1816bf70c41c2d0ecb934f2a22e071dbda5629cfe54f185af0acaad` |
| Current `art/cartoon/pack.json` | `0dee75befeaa36abfab1952fb737392d18c50ad037fe85c2143583da4215c795` |

Original resource payload SHA-256 values from the retained source map:

- FIRE2.BMP: `717714036513faa09e649c016b4b33faaee5b032e997fad82c41180b38a5d422`.
- FIRE5.BMP: `9c25c60bfa02eb792bfe39cf652dd7a6556cbe588e3ed784931a83213261a7c4`.
- SRAFT.BMP: `c6f02bbb0b18cf53b4b7794c0a18e92491c06cc1b04c58990541555b21f7440d`.

MJFIRE.TTM decoded source SHA-256 is `9af97c8523448a062193b2d5202eeb51e42f9be139c871fc500cf5ddb6805a11`; SJLEAVES.TTM is `8cc3614d050e901d88a15845073386f77906dbb4be764498be922751385fbfa8`.

Disposable original-pixel contact sheets and the grip comparison are in `build/fire-next-batch/`. They use nearest-neighbor display only and are not drawing or export inputs. No generation, full tests, staging or commits were performed.
