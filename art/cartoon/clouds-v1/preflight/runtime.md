# Cloud runtime preflight

Reviewed at `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc`. Production is the 61-asset, 2,612-member archive `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`. This is source inspection, not a new native run or original-executable comparison.

## Correct grouping

The ordinary moving sky uses **BACKGRND.BMP frames 015 through 017**, selected by `15 + cloudNo` in `src/engine/island.c:326`. The approved Cartoon 015 stays unchanged (`d7f6f6608cb18ac169b6e4378cb5c12c30a9139d7925c36e8a02f1c8eea41649`). The useful companion additions are 016 and 017.

| Frame | Original logical canvas | Cartoon canvas at scale 2 | Initial native x range | Initial native y range |
| --- | --- | --- | --- | --- |
| 015 | 128x36 | 256x72 | 0..510 | 25..88 |
| 016 | 192x57 | 384x114 | 0..447 | 25..67 |
| 017 | 264x76 | 528x152 | 0..375 | 25..48 |

The four CLOUDS.BMP slots are a separate resource, with original canvases 208x74, 104x34, 96x17 and 56x20. The complete retained script map has no TTM load association or native site for that resource, and no current source reference was found. Its runtime reachability is unproven. Do not call it the ordinary sky family or infer a storm/weather role from its filename. BACKGRND also has no TTM load association in this map; the moving-cloud use is native. See `art/cartoon/character-inventory-v1/scene-map/resource-map.json`, `static-draw-sites.json`, and `source/frame-index.json` one directory above `scene-map`.

## Placement and timing

`islandInit` (`island.c:197`) chooses zero through five clouds, one common wind direction, and an independent shape and speed of 1 or 2 for each cloud. Initial positions are in the table above. `islandAnimateClouds` clears the transparent cloud layer, updates each x coordinate, and draws the selected static shape in array order. Leftward wind uses the ordinary sprite; rightward wind mirrors the full original canvas. Each update moves 1 or 2 logical pixels, hence 2 or 4 output pixels at scale 2. All shapes use the same strict wrap checks: x greater than 904 becomes -264; x less than -264 becomes 904. The check precedes movement.

`adsInitIsland` (`ads.c:1056`) creates the cloud layer, sets its delay to 8 ticks and timer to 0, then animates once immediately. Normal ADS (`ads.c:836`) and public walking (`ads.c:1125`) call the same animator when its timer expires. The nominal interval is 160 ms at the port's 20 ms logical tick. Initialization can be followed by another timer-zero update before the first recorded display. Reviews must use actual recorded display timestamps and draws, not an invented evenly spaced sprite sequence.

The cloud routine does not reset `grDx/grDy`. The normal island/walking paths supply the island offset; actual placement is `(x + grDx, y + grDy) * scale` (`graphics.c:594`, `graphics.c:669`). No cloud-specific footprint offset exists. `graphics.c:282` composites the background first, then clouds, saved zones, story layers, and holiday layer. Normal cloud positions are high in the sky, but this is not a general promise that a cloud is behind every palm pixel.

## Day, night and fallback

Both day and night initialize and animate clouds. Day selects OCEAN00/01/02.SCR; night uses NIGHT.SCR (`island.c:161`). Day consumes an extra random number for the ocean choice, so a shared seed alone does not make day/night cloud arrangements identical. The routine has no night tint or palette switch. PNG colors remain authored colors; original-resource fallback uses the current port palette, initially the first palette resource (`graphics.c:183`). Supplied-original diagnostic reference colors are not proof of original-executable palette parity.

`art_style.c:410` tries the selected Cartoon PNG, then compatible HD artwork, then original-resource decoding. Missing 016/017 currently use fallback. Selected Cartoon clouds must have exactly the scale 2 canvases above; malformed or wrong-sized selected PNGs fail rather than silently falling back (`art_style.c:350`). No new canvas exception, draw coordinate, timing or runtime change is needed.

## Minimal native review

Use a new adapter under `native-v1/`, importing the pinned existing observer's compiler, RGB/PNG codec and process capture. The baseline is the exact current archive above, not the earlier static low-tide or shoreline packages hardcoded into historical entry points. A candidate may add only Cartoon 016 and 017 and must preserve all 2,612 baseline payloads, including 015 and every approved wave.

Use explicit three-cloud diagnostic states containing 015/016/017, both native wind directions, and a shifted night case. Each goes through the real cloud animator and public native wait calls. Label these as fixture states, not proof that the random scheduler naturally chooses this exact arrangement. A zero-cloud control must remain pixel-identical. Record shape, flip, logical origin, actual blit bounds, speed, scene offset, every native timestamp, loaded assets and fresh executable identity. Compare paired pixels only within the actually displayed 016/017 canvases; preserve everything outside them exactly. Run all smoke cases before fresh-process repeats, with small named damaged-input controls. Full scene and an unchanged sky crop should share those native pixels and timestamps.

No cloud capture has run at this preflight stage. Full traversal/wrap, natural story scheduling and original executable playback remain outside the bounded review. Existing source/helper hashes and the explicit baseline archive must accompany replay instructions; historical helper files stay immutable.
