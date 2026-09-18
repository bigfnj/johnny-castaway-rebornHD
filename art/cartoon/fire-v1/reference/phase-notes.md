# FIRE1 original phase guidance

[phase-sequences.json](phase-sequences.json) records eight source sequences and 67 UPDATE phases, with exact draw order, logical coordinates, frame numbers, mirroring, command offsets and nominal port delays. It also retains relevant command order, source identities and all 28 original PNG bindings. Use it for an isolated original/candidate comparison, not as evidence of native playback or final fit.

| Group | MJFIRE tag | Phase order | Logical effect positions, in phase order |
| --- | ---: | --- | --- |
| Smoke | 39 | 001, 002, 003, 004 | (306,280), (306,278), (306,280), (305,280) |
| Small flame | 41 | 005, 006, 007, 008 | (302,281), (306,290), (305,286), (305,286) |
| Medium flame | 42 | 009, 011, 010, 012 | (302,284), (306,289), (302,284), (304,283) |
| Large flame | 43 | 013, 014, 015, 016 | (306,272), (307,271), (306,269), (306,271) |
| Very large flame | 44 | 017, 018, 019, 020 | (303,262), (304,264), (303,261), (302,264) |

All five groups use SET_DELAY 7 before the first UPDATE: nominal 140 ms per phase and 560 ms per pass. No draw is mirrored. Log frame 000 is separately drawn at (297,298) in every phase. It follows the effect draw for smoke 004, small 005, medium 012 and very large 020; in the other listed phases the log draw precedes the effect. Preserve that order and each phase's own position. Do not center every flame independently or bake the logs into its artwork.

Frame 027 is a fire-centered burst/pop mark. The exact 40x22 source contains a white central puff/flash and radial strokes, with no text or speech tail. In tag 77, "disappointed", Johnny FIRE.BMP/009 appears at (317,263), FIRE1/000 at (297,298), and then FIRE1/027 at (292,287) in the second phase. The source draws the mark above the firewood, not beside Johnny's mouth. "Fire burst / pop in disappointed action" is a descriptive label; a precise sound or physical interpretation is not proven. PLAY_SAMPLE 24 precedes TIMER [60,120]. This port uses the integer mean, 90 ticks or nominal 1,800 ms per phase; do not describe that timer as a measured random duration.

The bases are independent sprites. Dying-fire tag 82 has 38 updates at eight ticks and changes the wood/ember base through 000, 026, 021, 022, 023 and 024 while separately drawing shrinking flame and smoke phases. Frame 025 has no uniquely attributed draw site in the retained static map; that does not prove it is unused in every possible runtime path. Retain it as a source drawing. Ember tag 83 draws 024 at (307,307), with smoke order 003,002,001,004,003,002,001 at eight ticks, then GOTO_TAG 83. Its first phase draws both sprites before setting clip [304,303,324,317]; later draws use the clip. The JSON preserves this command order rather than flattening it into a blanket first-frame crop.

BUILDING.ADS tags 5 and 7 bind MJFIRE in slot 3 and include random branches and timed scene calls. PURGE can repeat a tag while its scene timer is active. Repeating a four-phase group in an appearance player is therefore an editorial comparison mode, not a claim that the complete game always cycles through the five groups in sequence. The dying sequence and burst are not endless four-frame cycles. Background, cloud and Johnny threads can add display updates that are absent from an isolated preview.

The current MJFIRE.TTM payload and decoded identities match both the existing decode cache and the supplied-original catalog: payload SHA-256 `6b72333247ea690ad5cf2c4919eae4322c47de630a63c6c496c76b5f1f18b01c`, decoded SHA-256 `9af97c8523448a062193b2d5202eeb51e42f9be139c871fc500cf5ddb6805a11`. FIRE.TTM and BUILDING.ADS identities are also recorded and matched. The original PNG archive, per-frame source index, current production archive, maintained parser and relevant engine files are hash-bound. Relevant commands are embedded in the JSON, so playback does not require the historical scratch decode path.

Source coordinates are native logical pixels before ttmDx/ttmDy and render scale. The original reference colors use the port diagnostic palette, not calibrated original-executable colors. Timing uses the current port's 20 ms tick and is not a capture measurement. No original pixels, generated art, runtime files or packages were modified. No tests or native captures were run for this source record.
