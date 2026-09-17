# Low-tide supplied-original preflight

Read-only investigation at main `da787d63279ea91bd6c637e02133821339470bfc` on 2026-09-17. Only this report was written. No extraction, generation, native launch or production change was performed.

## Authentic source and usable files

Use the committed `art/cartoon/character-inventory-v1/reference-originals.zip`, SHA256 `b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912`. The desired entries are `native/BMP/BACKGRND.BMP/001.png`, `002.png` and `030.png` through `041.png`. These are decoded supplied-original pixels, not the `data/hd/` proxies.

`art/cartoon/character-inventory-v1/source/frame-index.json`, SHA256 `04f63230a01b94b90fa632c68b8d12ab27840eb6462d32719ae8d0ddf73cced2`, records their original canvases, XPM hashes, index-plane hashes, decoded RGBA hashes, PNG hashes and corresponding HD identities. This investigation reread all 14 ZIP PNGs and verified their file and decoded-RGBA hashes against that index. All 14 surviving sibling copies under `D:/.ai-work/worktrees/johnny-seasonal-decorations/build/seasonal-v1/island-footprint/images/original-BACKGRND-NNN.png` are exact byte matches.

The actual supplied pair still exists at `C:/JohnCast/SIERRA/SCRANTIC/` and was freshly rehashed:

| Input | SHA256 |
|---|---|
| RESOURCE.MAP | `3d9ec330aab96bbe5a44ce34f5945703862e82b195088590b7adfef5d7345da7` |
| RESOURCE.001 | `df9c2213f7c0abacf4e302cb53a476f9f220579c07ba350b167e351eed548eae` |

Original BACKGRND resource payload SHA256 is `dc444f2c9c82cdda1830a91de93de274dd3e67715de2ddfb2424b3cdc6080644`; the bundled resource payload is different, `f5bb7859eb58e244f6f4b3dd817020ba582abc73f47cd045c902deca073068fd`. The earlier executed independent decoder comparison covers all 42 BACKGRND frames and found differences between every supplied/bundled frame. See `docs/knowledge-base/original-image-comparison.md`. Do not silently substitute the bundled RESOURCE or HD PNGs for this reference.

## Geometry and material ownership

Origins below are the unchanged port's logical 640x480 coordinates at zero island offset, from `src/engine/island.c:45-50,242-262`. Multiply coordinates and canvases by two for the current 1280x960 presentation; no low-tide footprint offset is registered.

| Frames | Native canvas | Logical origin | Meaning visible in original art |
|---|---|---|---|
| 001 | 384x69 | 249,303 | Exposed beach face/apron laid over the base island, including dark rock/sand shading, left red starfish and two small right-side shore objects. |
| 002 | 64x30 | 150,328 | Separate foreground rock left of the beach. |
| 030,032 | 120x48 | 233,323 | Left beach surf family, including painted shore material. |
| 031 | 128x48 | 233,323 | Middle phase of the same family; its full canvas is eight native pixels wider despite the same 120-pixel visible right bound. Preserve that padding. |
| 033-035 | 176x28 | 367,356 | Front/bottom beach surf family, with a broad painted sand strip above the water. |
| 036-038 | 88x48 | 558,323 | Right beach surf family, including painted shore material. |
| 039-041 | 104x29 | 129,340 | Surf surrounding the separate rock, with an open upper center around the rock. |

At HD scale the full canvases are respectively 768x138, 128x60, 240x96 (031:256x96), 352x56, 176x96 and 208x58. The far-right family extends to logical x646; the normal 640-wide view clips the last six canvas columns. The source canvas is still required for shifted scenes. Frame001's full canvas ends at x633 and its visible alpha ends at local x380; do not mistake the visible bound for the source canvas.

The draw order is base000, trunk013, leaves012, palm shadow014, then low-tide001 and002, then animated low-tide waves. High-tide003-011 are not the active wave family in this state. The low-tide beach therefore is an overlapping scene assembly, not just twelve detachable white foam drawings.

Conservative native-pixel counts of opaque diagnostic yellow/olive in wave frames confirm non-water material: 030/031/032 = 270/183/216; 033/034/035 = 823/950/1026; 036/037/038 = 250/158/164. The rock family has only two such pixels in each phase. These are palette witnesses, not a complete semantic sand mask; gray, black and white pixels can also belong to shore/rock details. Do not drop all painted ground simply because the resource is animated.

The left red starfish in001 is clear. At right, the pale ribbed object reads as shell-like. The red/white object could be another shell or a can, but its native pixels do not support a confident name. Both are baked into001, with no separate object IDs in `island.c`. Preserve their visible placement and shapes instead of inventing an object label.

`islandAnimate` advances one of four families per call, with three phases per family. The selected static counters persist between island initializations; a fresh original reference must record actual calls/phase state rather than assume all phase-zero images are the captured tuple. The old static capture below did not instrument the wave tuple and cannot stand in for a complete animation reference.

## Best existing composed reference

Visually inspected and hash-verified:

`D:/.ai-work/worktrees/johnny-seasonal-decorations/build/seasonal-v1/island-footprint/native/original/low/none/final.png`

SHA256 `c32522bd86888d17c6c09419f4276ce805e8e0a076cde9810dc74b49389a97cb`.

This 1280x960 native composite shows the complete supplied-original base, low beach, separate rock and four surf regions together. It is the best existing material/placement reference. "None" means no holiday decoration; Johnny016 and the palm are still present. The companion original-clover scene is at `native/original/low/clover/final.png`, SHA256 `1042e94c4e2f6cd9db6062c026152909540375702b82492c56f1086c4e42f801`.

The retained main report `art/cartoon/seasonal-v1/island-footprint-v1/native/original/low/none/report.json` binds the first PNG. The package used the supplied resource pair with every HD/Cartoon PNG override removed, while retaining scale2. Command arguments were `seasonal_probe 0 0 0 0 hd 1`: day, no holiday, zero shift, low tide. Seed11 chose OCEAN02. The driver performed an actual finite same-heading wait after island initialization. Its label should be "Supplied-original artwork rendered by the port, diagnostic palette", not "original executable screenshot".

For all-frame inspection, the existing atlas is `D:/.ai-work/worktrees/johnny-character-inventory/build/character-inventory/atlas-v1/BACKGRND.BMP-01.png`, SHA256 `4cca1b16c33b33135a9332c2d15a369688d060f09f3b3dd67defb395ddbd624c`. It was visually inspected here, but each tile has its own display scale; use the indexed native PNGs for registration.

## Extraction and reconstruction entry points

For the new batch, the smallest source operation is copying the fourteen exact ZIP members above to fresh reference paths and retaining their frame-index pins. No decompressor rerun is needed.

The complete existing converter is `art/cartoon/character-inventory-v1/source/prepare.py`. It reads the historical dump at `D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference`, the supplied resource pair, and an explicit `--archive` for HD mapping only. Its `--phase prepare`, then `--phase smoke`, then `--phase regression` interfaces and fresh-output requirement are documented in `source/README.md`; `source/test_prepare.py` owns the existing source-damage controls. Byte-identical PNG reproduction requires Pillow12.3.0. A new index using today's archive/tool hashes is new provenance, not the old frozen index byte-for-byte.

The historical dump's `report.json` is present and retains SHA256 `1983679cff95f0abfd00d21451c46d905506c44ef7edad66f0accead749fcc73`; its recorded native executable is `6ac61dc53dc926a311d89fcf2e27ff7cefbbac7f4c60e2491f69114230400865`. The maintained parsing entry points are `tools/inventory_scenes.py:resource_catalog/metadata` and `tools/art_review_metadata.py:original_canvas/xpm_facts`.

For native reconstruction, `art/cartoon/seasonal-v1/island-footprint-v1/REPRODUCE.md` explicitly requires restoring frozen helpers into `build/seasonal-v1/island-footprint/` at that exact depth in a disposable checkout with the pinned old archive/source. Do not run its preserved `helpers/prepare.py` directly from the evidence directory or against today's production archive. For a new low-tide capture, adapt the observation driver and preserve fresh identities. The old twelve stills establish one composed state, not all-phase timing or original executable parity.

All source PNGs use the port diagnostic dump palette with BMP index0 transparent. Yellow/olive, bright blue and gray are useful material/index clues, not original executable color calibration. Preserve geometry and material relationships while using the approved Cartoon scene separately as the style reference.
