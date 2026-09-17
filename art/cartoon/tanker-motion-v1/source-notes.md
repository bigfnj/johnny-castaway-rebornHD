# Tanker source sequence

The comparison input is [source-sequence.json](source-sequence.json): 76 ordered draws from `GJVIS6.TTM` tag 9, "voldeez wanders". Each row retains the signed logical x/y, frame, whole-canvas flip, command offset, following UPDATE offset and nominal delay. [context.json](context.json) preserves the complete tag commands, the tag 4 resource loads and the relevant `VISITOR.ADS` tag 3 context. This is source-derived animation guidance, not a native capture.

The actual four runs are:

| Run | Mirror | Frame order, with repeated draws counted |
| --- | --- | --- |
| 1 | Yes | 010 x6, 011, 012, 013, 012, 011 x2, 010, 009 x2, 008, 007, 006, 005, 004, 003, 002, 001, 000 |
| 2 | No | 001, 002, 003, 004, 005, 006, 007, 008, 009, 010 x2, 011 x2, 012 x2, 013 x2 |
| 3 | Yes | 012 x2, 011 x2, 010 x2, 009, 008, 007, 005, 004, 003, 002, 001, 000 |
| 4 | No | 001, 002, 003, 004, 005, 006, 007, 008 x2, 009 x2, 010 x4, 009 x2, 010 x3 |

Frame 006 is intentionally absent from the third run. This is not an ascending 000-013 loop. It starts at logical (-53,171), turns through mirrored 000 at (156,175), changes to unmirrored 001 at (158,176), turns again through 013, and eventually exits left at (-52,185). Both comparison panels must use the same row and mirror state. A centered view may remove translation for inspection but should retain this source order and the mirror changes.

`SET_DELAY 4` occurs at decoded TTM offset 594, after the first draw and before its first UPDATE. There is one UPDATE per draw. The port implements delay at `src/engine/ttm.c:309` and yields at `src/engine/ttm.c:304`; `src/engine/events.c:217` converts a tick to 20 ms. Thus each draw has nominal 80 ms and the pass totals 6,080 ms. Concurrent threads can cause extra display updates, and speed controls or rendering time can affect playback. These are not measured original-executable or native-capture durations.

The normal caller is `VISITOR.ADS` tag 3, offset 276: `ADD_SCENE [3,9,0,1]`. Slot 3 binds `GJVIS6.TTM`; its load tag 4 binds `TANKER.BMP` to BMP slot 2 at offset 122. Johnny tag 5 runs alongside the tanker, then tag 6; completion of tanker tag 9 stops tag 6 and starts tag 7, followed by tag 8's close-up arrival. There are no random or branch commands inside tag 9 and no RANDOM commands in this ADS tag 3. The outer story choice remains contextual. The final PURGE at offset 1798 ends this normal one-pass call: scene timer and iteration state start at zero (`src/engine/ads.c:322`), and PURGE checks the timer (`src/engine/ttm.c:296`). A different arbitrary caller could request timed repetition, which is not the normal call recorded here.

Coordinates are native logical pixels before `ttmDx/ttmDy` and render scale. Normal draw handling is `src/engine/ttm.c:438`; flip dispatch is `src/engine/ttm.c:448`. `src/engine/graphics.c:679` applies placement and scale, then `src/engine/graphics.c:688` mirrors the complete canvas at the same top-left. It does not substitute a different frame. The long horizontal structure is visible in the original 000-002 references, but identifying it more specifically than the drawn ship structure is an art interpretation. Source rotation should decide whether its generated shape and perspective are convincing.

The current archive's `GJVIS6.TTM` payload SHA is `d7818136022ddbe3d7f6f5ae10b0aa7bc701403ae4e2d25d574e44fc163e89d7`; decoded SHA is `1870f2813862ed07dc5ecd9d6396c20793b0150c84b550e6963e0393ac8f1b8d`. Both equal the preserved supplied-original catalog identities. Current `VISITOR.ADS` payload also matches the existing decoded-source cache. The exact current archive, parser, source-map, catalog and relevant engine file hashes are bound in the sequence JSON. No artwork, runtime or package was modified, and no native playback was launched for this readback.
