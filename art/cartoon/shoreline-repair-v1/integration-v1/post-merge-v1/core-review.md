# Seasonal post-merge core review

Reviewed primary checkout `D:/.ai-work/projects/johnny-castaway-rebornHD` on 2026-09-17. HEAD was verified before and after review as `9b0a4ed1fb5920faf426c4d3aa89e45afadebf07`. This is a source audit, not a new test run. No tracked file was changed.

No concrete introduced defect was found in the reviewed runtime changes. This does not establish complete story parity, absence of all leaks, physical audio correctness or coverage of every malformed resource. Existing BACKLOG findings remain open.

## Scope and method

Read all 17 C implementation files and all 20 headers under `src/`, including the three compiled data tables. Followed startup/CLI dispatch, ADS/TTM execution and teardown, resource and sprite ownership, graphics clipping/composition, walking, island animation, configuration, dump I/O, decompression and common audio. Also read `platform/platform.h` for the borrowed-surface and audio contracts. Platform implementations and the full Windows gate belong to the parallel audit; no duplicate native suite or broad fault-injection run was launched here.

Compared current source against the merge's first parent, `397edf8e4b34191ade4be13bc93a215f73b0c631`. The initial review used earlier baseline `0e520ee`; a follow-up diff confirmed that `src/` is identical between that baseline and the first parent. Both comparisons therefore show only `src/engine/art_style.c`, `art_style.h`, `graphics.c` and `island.c` changed: 81 insertions and five deletions. The remaining 33 files are unchanged. A final `git diff HEAD -- src` was empty. Current code was read rather than assuming that unchanged code was correct. The source hash inventory below records the exact worktree bytes inspected.

The data review covered table structure, routing/heading/bookmark use and their relationships to the current consumers. It did not independently replay every story entry or recalibrate the original executable's behavior. `BACKLOG.md` open work and prior rejected claims were checked before classifying findings.

## Merged footprint and rendering paths

| Area | Current evidence and conclusion |
| --- | --- |
| Named asset exceptions | `art_style.c:305-323` restricts expanded canvases to BACKGRND frame 000, center 006-008, left 003-005 and right 009-011. `art_style.c:378-389` also requires a selected Cartoon replacement, scale 2, the corresponding original resource dimensions and the exact approved canvas. Other wrong-size Cartoon PNGs still fail by path; mismatched HD fallbacks are rejected before original decoding. No generic arbitrary-size bypass was added. |
| Position and reflection | `art_style.c:325-350` gives normal offsets ground (-36,-10), center (-32,-90), left (-6,0), right (0,0). Reflected X offsets are -44, -32, 0 and -10, preserving the original logical anchor. `graphics.c:610`, `630` and `684` apply the same helper once in normal, source-atop and reflected paths. Legacy dimensions and other styles retain zero offsets. Style selection is documented as a startup operation in `art_style.h:21`; live style switching was not added. |
| Restoration coverage | `island.c:62-114` takes the union of actual phase surface dimensions plus the same asset offsets, clips that union to the background and saves its pixels once. `island.c:116-149` restores it before redrawing the currently visible wave families in preserved order. The expanded center and side rectangles are included; the fixed static ground is not accidentally redrawn as part of the waves. Low-tide families use their existing dimensions and zero offsets. |
| Ownership | `island.c:55-59` releases and clears the saved wave buffer. Scene initialization and background release both call that idempotent function (`island.c:154`, `graphics.c:67`). The new paths add no allocation per animation tick. Loader error paths release decoded pixels and their borrowed surface wrapper. No new ownership imbalance was found in these changes. |

## Existing issues confirmed, not new regressions

These are source confirmations of already recorded issues. Prior probe results are not presented as freshly executed results.

| Existing BACKLOG item | Fresh source evidence and scope |
| --- | --- |
| Common audio startup | `sound.c:158-165` opens audio before an unlocked reset of `currentRemaining`; the callback reads/writes that value under the platform lock at `sound.c:67-84`. The silence branch at line 79 can call `memcpy` with a null source and zero length. This remains a startup synchronization/contract issue, not newly measured audible corruption. `sound.c:188-205` closes the worker before freeing WAV buffers and clears playback aliases; the earlier failed-open WAV cleanup remains present. |
| Malformed saved day and seed parsing | `story.c:102` increments before the clamp; `config.c:139-142` still uses unchecked `atoi`. `jc_reborn.c:430` still parses seed with `strtol` without the frame option's range/errno checks. The existing malformed-config and overflow-seed backlog entries remain applicable. Ordinary small-seed captures are not implicated by this source review. |
| Reachable unfinished commands | `ttm.c:290-292` dispatches DRAW_BACKGROUND to a no-op. `ttm.c:386` and `397` call `grSaveImage1` and `grSaveZone`; their incomplete implementations remain at `graphics.c:385` and `399`. These calls are reachable, not dead code to delete. Original-engine comparison remains necessary before assigning their intended semantics. |
| Primitive clipping | `graphics.c` pixel/line/circle and rectangle paths still differ from sprite active-zone clipping. The existing SBREAKUP/context investigation remains appropriate; static command occurrence alone is not a visible scene failure. |
| Malformed bytecode and decompression | `ttm.c:64-80` can fail to advance for a matching zero-offset tag; missing tag entries at line 171 leave offsets unset. String readers at `ttm.c:246` and `dump.c:383` stop copying at 255 characters before treating the next byte as a terminator. `uncompress.c:134-137` still accepts the first LZW code without the broader EOF/literal validation listed in BACKLOG. No shipped-scene failure was newly observed. |
| Dump output errors | `dump.c:169`, `235`, `321` and `570` ignore final close failures, as before. Existing write-error work remains open. This review did not repeat the historical `/dev/full` probe. |
| Waiting and persistent state | `ads.c:1110-1114` retains the six-tick first timer while updating only delay from the first walking result. `island.c:268-282` uses persistent wave counters. The recorded direction/wait comparison and optional deterministic scene-seeking work remain unchanged. |
| Process lifetime versus scene lifetime | Resources parsed in `resource.c` retain their map names, decoded buffers and metadata for the process lifetime. Slots borrow resource data, while slot tags and sprite allocations are released by `ttmResetSlot` (`ttm.c:188-212`). `adsStopScene` (`ads.c:349-360`), repeated ADS initialization (`510-515`) and island release (`1074-1092`) release their owned layers. A complete resource unload is still needed before any future live restart/pack switching, but the current startup-only parser is not evidence of a growing per-scene leak. |
| Unreachable defensive branches | `resource.c:117`, `189`, `282` and `336` still test decoder results for null, although current decoders return allocated data or terminate. This existing cleanup item is distinct from reachable TTM stubs. |

CLI startup and completion paths were followed through `jc_reborn.c`, including version/help and saved-style handling, dump, benchmark, standalone TTM/ADS, play-all and ordinary story dispatch. Event-driven and bounded exits call sound teardown before graphics teardown (`events.c:107-108`, `244-245`); no new inoperable CLI path was identified. This is not a claim that every original script operation is implemented.

## Optimization and proposed backlog delta

No new backlog entry is proposed from this review. Preserve all current items above. Existing `grDrawSpriteFlip` column blits (`graphics.c:689-695`) and full-frame composition are possible profiling targets already recorded in BACKLOG. Wave restoration also copies its union and repaints current phases on each update (`island.c:133-149`), but that work supplies the required alpha restoration. No cold interleaved benchmark was performed, so this report claims no time or memory saving and does not recommend replacing it on an unmeasured assumption.

## Exact inspected source hashes

SHA-256 of worktree bytes, including their current line endings:

```text
src/engine/ads.c c4d53220327f62676a159f1b3651626a8dabafdfa5bf625b5e94d443280eb4f6
src/engine/art_style.c f6519bfbb7fb9af09ae19b3d41b546bb644dda1952160eef1956ad7466051513
src/engine/bench.c ca747e19369cd2b57e547393ec4b63cefe3ff1f6a95d4d30fd22b218228ed03c
src/engine/calcpath.c 8035aef05017584b5e7e5db1dcac898ba3f51efe444efc072705d5f0523cfacb
src/engine/config.c a87b4e3d050912d7a82f3efa2d681be2ac20a72cadca3581dffa6d7e572bba58
src/engine/dump.c b2e46c22fa854bbc0d75413b441f4afc0afb10d42b6ead737e70bc5d7e92babd
src/engine/events.c 041ac9fce76af2c3e1fc2eeef56ea9b92b45e1a4adc0087d5318720ccc2d57d2
src/engine/graphics.c fded8d14dbfa432242170e0a16010cb882d02f437d31e5a317bfe2baafcee392
src/engine/island.c 78795472d233c9b54bcd8ff32e032358e5e19434e4de7d2fdb26f521d6600737
src/engine/jc_reborn.c 50d9904cffd7c3cba9877ecec383370c612622ccd31a5a013e77755903c358c4
src/engine/resource.c 8b60a6d5936dd67ca014aaedde799e8b6f0a567ac482c836bd922a4fa93c6f43
src/engine/sound.c eec8a1b43e33eccbd4e7f835ca55b7d9ab952818f2093f6a996d69d1ce6a91ee
src/engine/story.c b503cca4115b5852f4ed9cdc02c5aef77498c793bac9fdb2b517b19cd8c4b9a4
src/engine/ttm.c f74b812e1279847cad9d2af9ff55792e9b5a852e204424ced5410a7cd00509f6
src/engine/uncompress.c c8c0483ef3ae43e242ecbfff622c4735aef6f330ebce04f4cda8b43bfbba6b15
src/engine/utils.c c50c4ae6de6a59e4fbd1a169592eb920778449f8c000175cb55d66595343c10f
src/engine/walk.c d6b88ef1e16a2ad10944ce520485a472d4b13d53fd744087e9c5e573e1908f9d
src/data/calcpath_data.h fdaf8cc409388b1425485801597b272105c6a788eb30825b74441e21f5041237
src/data/story_data.h 0f7d6cbd9a37b411839a2a9376c15e035388d00cb0f8cbf4b898dcc93eaff6f6
src/data/walk_data.h 142a0f9df8dd4ac0703b41f96df124284d2a9957904d7743ee9283f607498769
src/engine/ads.h fbe0925205b5b0ed225152d5892a5aef72e215c1d68e5f94476ddeb66c7996a1
src/engine/art_style.h 5e12338406ceec466fc678e63f5e8019c7bebf3ff60fc8068293d3f9d917c897
src/engine/bench.h e7ff059877a2c4a747c3675767da29b01f167989f8a2ba9a57d45e47cfcbf3ad
src/engine/calcpath.h 4b5c614adc8a960e1bbab746aa159c4c908e3377d38a2d3c0f353ae0726d915d
src/engine/config.h ef00caffb5bba8c4de0e8b09e84911c4c1563fb6d6e5986f3e935e54b0dfcf46
src/engine/dump.h 27ad235d4b052886c296999aae65f8604b6b668b3428860db0aea561827226df
src/engine/events.h 7b73c8f46c470f325fb6b49093cbdc9b4f3c3da598be900d37244bd98bf9ea54
src/engine/graphics.h e2b388c6e9edfac3237c88467ba38117c4b1918b2a56f4a4d9dcd635e6fd9ecf
src/engine/island.h 78da2a0bcc15e38636aa8ca7d1f9c1fb7fc48b49bf44a8afd895f3b76b3bef58
src/engine/mytypes.h cd9d251a4025cb9894b3d13dfb0c05568eadd53b7c15ee16f2af49b6c07cad84
src/engine/resource.h dfb8a1c118fb69a515931b939e7a32e05cc05688b2c09875b496211dcac412af
src/engine/sound.h 36bf9900ea05f164190b042905e1d5b5e163015055fa1f9f5cd9ec15c54a1e47
src/engine/story.h e2bc55888fa518bbac1566f059111e2b4e278a986639cb825dd28a8677663e0c
src/engine/ttm.h 7a6a8d40da48f8316d204cc4a8bb664e7cf3950dde0a75f79c0a6bf8b080e48d
src/engine/uncompress.h c58f198f9dad5e00ac344925a0a9c45087253d6c6c950bd06cbc701c906c2148
src/engine/utils.h 9e6fb0678b6c62c63bea5f58f1772cf02aa7510809639f4984e94d0fa3d43104
src/engine/walk.h cd828778b83c73428ba9d7897a87aa7254b7d2d54eb1eb3f31a1ed625cbf5a91
```
