# Independent native adapter review

Read-only review of `capture.py`, `driver.c` and `run.py`, their retained compiler/capture/parser dependencies, and the current engine cloud/draw scheduler. No concrete launch blocker was found. This is a code review, not an executed native result or human art approval.

The three fixtures use valid initial native states: 015 at (40,25), speed 1; 016 at (230,55), speed 2; 017 at (375,30), speed 1. All fall within `island.c:204-236` selection ranges. The explicit three-cloud or zero-cloud replacement happens after ordinary island initialization and before capture. `adsPlayWalk` services the zero cloud timer before its first display, so `islandAnimateClouds` clears the old randomized cloud layer first. The fixture is correctly labeled explicit state, not a naturally selected seed outcome.

Drawing and timing remain native. The observer wraps calls without replacing rendering, observes both normal and column-wise mirrored blits, and logs actual displays after `eventsWaitTick`. `verify` checks each movement step against the source algorithm, full sprite dimensions, direction, island offset and submitted blit union. Every display carries the latest actual cloud state. Inherited parsing uses requested native ticks multiplied by 20, with equal baseline/candidate clocks, calls, returns, Johnny state and background phases. This is logical playback timing, not a wall-clock benchmark.

The logged cloud bounds are the native submitted blit union before platform clipping. They are not the visible alpha bounds. This distinction matters when 017 moves past the right edge or shifted 015 crosses the left edge. The pixel comparator correctly intersects allowed 016/017 rectangles with 1280x960 and requires every other pixel unchanged. The zero-cloud case is a non-degenerate exact control. Full traversal/wrap is explicitly outside this short review's scope.

Package validation pins the current `a8987430...` baseline, exact candidate archive hash, all 2,612 retained payloads and exactly two additions with their original 2x canvases. The same final ground/side/center placement contract is intentionally applied to both packages, since both inherit the already integrated shoreline. The loaded paths distinguish baseline HD 016/017 from candidate Cartoon 016/017 while preserving 015. Historical package-building entry points are not invoked.

The launcher uses a fresh named scratch child, network-disabled Docker/Xvfb and a read-only source mount. The compiler records a fresh executable and source hashes. All eight paired case smokes must finish before any of the eight fresh process repeats. Repeats compare full display/pixel records and native calls; final checks rehash protected source, helpers and archives. Failed capture logs remain in scratch. The three planned damaged-data controls target actual 016 placement, a pixel outside the cloud canvases and an incorrect 016 canvas, each requiring its named refusal and restored positive. Their execution remains pending.

Reviewed SHA-256 values:

```text
capture.py 902e613aeec8daf4a2ec79bc468c66fd80920e76b66c641fe50807a2fddbc29c
driver.c 19d9438ae787ce958757975a3cdc2ba43aae55bb29608a5486d417ba1f1f1e6f
run.py f0b0646d52dcbc038acd022024d428d58648dc11ce77ba6b1497f2a111d4bc3c
retained native-final/contract.py 81369ccb3fbb7620221e41367ce6a010aaa1eca05ffee126b00d43cf27984cbb
retained integrated-shore-v1/native/capture.py f2e0684f6726ce53951988b5d44c101d3efe44f07e6b3b66277499a9f12a1bae
retained integrated-shore-v1/native/driver.c beb8beae0c3b54562fe51285d184d55ccd2b185fe34cf97b7801d2536abd1b59
```

No captures, tests or source edits were performed by this reviewer. Successful launch, all observed pixels, cleanup and negative-control outcomes must be established by the owner's upcoming run.
