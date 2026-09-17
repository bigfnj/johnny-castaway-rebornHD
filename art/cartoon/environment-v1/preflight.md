# Environment backdrop preview preflight

Preview preparation at merged baseline `a0c2d03`. No tests, full audit, captures or runtime/package changes were performed. `reference/source.json` records the exact copied image bytes, source archives and dimensions.

The smallest coherent remaining ordinary-island group is NIGHT.SCR, OCEAN00.SCR and OCEAN01.SCR, with accepted OCEAN02.SCR retained as the style and comparison reference. All four originals are 640 x 480; all Cartoon runtime canvases are 1280 x 960 at screen origin zero. The other six SCR resources are story/title screens, not alternatives selected by the ordinary island initializer.

`src/engine/island.c:151-170` selects NIGHT when `islandState.night` is true and otherwise selects OCEAN00, OCEAN01 or OCEAN02 with `rand() % 3`. These are static alternative backgrounds, not successive animation frames. `src/engine/story.c:119-127` derives night from local hours 21:00 through 05:59 unless an explicit override is active. Tide does not select a different SCR.

The initializer loads the backdrop before drawing the raft, island, palm, shadow and optional low-tide shore/rock, then saves the wave-restoration background and initializes shore waves (`island.c:178-263`). Final composition is background, moving clouds, saved zones, story layers and holiday layer (`graphics.c:282-325`). The screen does not move with island offsets. Do not bake land, Johnny, shoreline foam or moving clouds into these screen images.

`graphics.c:711-787` first uses the style PNG loader, then falls back to decoded original indices. Selected Cartoon screens require the exact 2x canvas; there is no screen-offset exception (`art_style.c:350-388`). Keep the full screen opaque. Original fallback pixels use the current port palette and alpha255, while loaded PNGs preserve authored RGB. Loading NIGHT does not tint existing clouds, Johnny, sand or foam. Script LOAD_PALETTE is currently logged without applying a palette (`ttm.c:482-484`); the existing fade is a geometric window wipe, not a PNG-driven crossfade. No palette or fade code change is needed for this preview.

The copied original NIGHT visibly places its horizon around logical y205, HD410, with a moon near logical (165,85), stars and a reflection on the left. Daytime originals place the horizon around logical y150, HD300, or 31.25 percent of screen height. Preserve this intentional night composition instead of silently imposing the daytime horizon. OCEAN00 and OCEAN01 differ in their static ocean pattern; keep their original broad arrangement while matching approved OCEAN02's restrained blue-green drawing style.

The fundamental art choice is a readable moonlit backdrop that still works with the already approved, unchanged bright foreground and cloud colors. Start with one NIGHT draft in that real scene context, then make the two daytime companions from the approved OCEAN02 style. A useful bounded visual page shows NIGHT, OCEAN00 and OCEAN01 alongside unchanged OCEAN02, with the same foreground state and a low-tide option. Full smoke/regression/audit work belongs at the user's later bulk milestone.

Exact ImageGen-ready references are in `reference/`:

| File | Canvas | Use |
| --- | --- | --- |
| NIGHT-original.png | 640 x 480 | Night composition, moon/reflection and horizon geometry |
| OCEAN00-original.png | 640 x 480 | Alternate daytime ocean arrangement |
| OCEAN01-original.png | 640 x 480 | Alternate daytime ocean arrangement |
| OCEAN02-approved-raw.png | 1448 x 1086 RGB | Approved generated palette and drawing style |
| OCEAN02-approved-runtime.png | 1280 x 960 RGB | Exact shipped backdrop and native-scale composition |

The original PNGs come from `art/cartoon/character-inventory-v1/reference-originals.zip`, members `native/SCR/<name>.SCR.png`, with identities in the retained frame index/source records. They render supplied-original index planes using the port's diagnostic palette; they are geometry references, not verified original-executable color captures. All SCR indices are opaque. The supplied original files are the recorded RESOURCE.MAP and RESOURCE.001 pair under `C:/JohnCast/SIERRA/SCRANTIC`.

The approved raw comes from `art/cartoon/island-pilot-v1/ocean-shadow-center-waves/source-images.zip`, member `ocean-generated-v1.png`. Its original recipe uniformly resized the complete 4:3 raw by 160/181, without cropping. The runtime copy comes from `assets/scrantic_data.zip`, member `data/styles/cartoon/SCR/OCEAN02.SCR.png`, SHA256 `099249884c73c863436983ec4d4f5650e77e6e5748ef65bf417d0785b1acf294`. Historical recipe approval fields are superseded by the active pack's inherited acceptance; no old evidence was rewritten.
