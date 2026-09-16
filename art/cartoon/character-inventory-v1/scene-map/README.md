# Script and native-draw map

This is a source-derived aid to visual classification, not an executed scene inventory. It includes every BMP resource: 116 in the port and 117 in the supplied original. `SA_DEMO.BMP` is original-only. Names such as GJ, MJ and SJ do not establish whether a frame contains Johnny.

- `resource-map.json` lists resource identities, TTM load associations, story/action names and conservative frame-action groups.
- `static-draw-sites.json` contains 15,368 TTM sprite instructions. Each `draw_sites` array follows `draw_site_columns`; `draw` is `[x,y,frame,bmp_slot]`. Source offsets are decoded-script byte offsets, not source-line numbers. Metadata provides tag descriptions and decoded-script hashes.
- `native-draw-sites.json` preserves all 489 native walk table rows including terminators, their source lines, and the separately reviewed native island/benchmark resource uses.
- `remaining-walk.json` distinguishes the C-to-D group from the water-exit script and retains their neighboring poses, placement and timing instructions.

The maintained parser decodes current bundled scripts using the production decompressor probe. Every current resource payload matches the existing port catalog, even though the artwork ZIP has changed since that catalog was generated. The supplied original pair is also hash-checked against the catalog. Original and port provenance remain separate.

11,441 draw sites have one resource filename assigned anywhere to that TTM slot. This identifies a static resource/frame request conditional on the slot being populated; it does not prove the draw runs in every story that uses the TTM. At 3,908 sites a slot can hold multiple resources. Those entries keep `resource:null`, every possible filename, and an explicitly labeled preceding-load hint. Nineteen sites in GJLILIPU/GJVIS5 use slots with no LOAD_IMAGE attribution in that TTM; their resource remains unresolved. No missing animation conclusion follows from this alone.

`last_same_tag_delay_instruction` is a textual fact, not a measured duration. Inherited state, UPDATE, deferred GOTO_TAG, PURGE, ADS choices and concurrency require runtime tracing. Native walk entries use `x-1` before island offsets and scale, and mirror the full original canvas. A resource-level story association may refer only to a load/helper action. It must not be presented as proof that every frame runs in that story.

## Remaining native and scripted walk groups

The direct C-to-D table is `011,019,020,021,022,023,032,014,030,031,032,014`, all unmirrored, in `src/data/walk_data.h:224`. A minimal review call is `adsPlayWalk(2,3,3,4)` when `calcPath` chooses direct CD. Its final wait is frame015 at logical `(478,217)` after the native x-minus-one rule. Direct path selection and exact displayed timestamps still need a later native capture; this map did not choose a platform-specific random seed. Each travel result returns6 ticks, arrival returns80, and background refreshes can repeat poses. The behind-tree overlay is only applied for D↔E, not C↔D.

The same four remaining poses also occur within MJFISHC tags64 (walk c to tree),62 (boot to tree) and63 (large fish catch), with8/8/7-tick instructions in their walking portions. They are embedded in larger actions and have different positions from the native table.

Frames033–035 are used by MJDIVE tag2, "Walk out of water". Its whole static Johnny sequence includes035, then repeated010/033/034/035 steps, and finishes010/017/017. SET_DELAY10 is before the first035 UPDATE; initial setup timing is inherited. The script clips at y279, later expands to y349, and its final SET_DELAY0 is clamped to4 by the port. These drawings should be reviewed in the water-exit context, not made into a new native walk loop. All statements here concern original-derived data rendered by this port, not original-executable timing parity.

## Reproduce

From the repository root, using an existing headless production decompressor probe:

```powershell
python -B art/cartoon/character-inventory-v1/scene-map/build_scene_map.py --probe <jc_uncompress_test.exe> --original-dir <supplied-original-resource-directory>
python -B art/cartoon/character-inventory-v1/scene-map/verify.py
```

The first command reads RESOURCE.MAP/RESOURCE.001 and writes only this inventory and ignored decoded-script scratch data. It does not launch a scene. The verification runs2 smoke tests before8 regression tests, then four fresh-process source-negative controls and a restored positive regression. The controls disable current-resource identity, original-resource identity, load-slot validation, and ambiguous-slot preservation; each produces exactly one named failure. `evidence/` retains exact scripts/logs/results for those runs. Native scenes, artwork generation and production promotion were not performed.
