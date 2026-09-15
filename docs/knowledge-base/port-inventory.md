# Port resource and scene inventory

This inventory separates resource presence, static scheduler eligibility, and proven rendering behavior. It compares the bundled archive with the user-provided local original RESOURCE.MAP and RESOURCE.001. It does not execute or redistribute the original binary, and does not claim visual parity with it.

The reproducible facts are in [port-inventory.json](port-inventory.json). Full decoded script bodies and binary assets are not stored in this report.

## What is present

| Resource kind | Port | Local original |
|---|---:|---:|
| ADS | 10 | 10 |
| BMP | 116 | 117 |
| PAL | 1 | 1 |
| SCR | 10 | 10 |
| TTM | 41 | 41 |
| VIN | 1 | 1 |

Original resource names absent from the port: `SA_DEMO.BMP`. The role of an omitted resource is not established by its name alone. A resource omission does not establish a missing animation.

The port contains 2,391 legacy bitmap frames and 10 packed screens. The fresh headless production dump matched all 2,452 checked-in golden hashes. These hashes establish port decoder regression coverage, not original rendering equivalence.

Decoded streams identical to the original: 10 of 10 ADS; 40 of 41 TTM. The JSON compares each script's tag descriptions and resource bindings separately. Changed decoded command sequences follow; differences exclude offsets shifted by another edit.

- `SJLEAVES.TTM` delete: original: SET_DELAY [0] at byte 5786 (tag 3).

The inventory makes no claim about why a script was changed.

Raw image payloads differ between distributions. The JSON records hashes and screen dimensions; compressed-payload differences alone do not establish pixel differences.

For sound payload coverage, see the separately reproduced [original NE audio comparison](original-ne-audio.json) and [original reference](original-reference.md#complete-embedded-audio-comparison). All 23 declared original RIFF payloads match bundled WAV prefixes. The original PLAY_SAMPLE identifier mapping remains unresolved; filename gaps such as 11 and 13 do not establish lost audio.

## Scheduler eligibility

There are 66 ADS tag records and 63 direct story entries. The table entries are statically eligible on their stated story days. A scene eligible for selection is not guaranteed to be chosen during any finite run.

For each story sequence, the scheduler first chooses a FINAL entry. Unless that entry also has FIRST, it chooses ordinary lead-in scenes filtered by tide, island movement, day, and FIRST status. The lead-in loop re-evaluates its random bound on each iteration. Story day advances once when the saved calendar day differs from today, then wraps after day 11; it does not advance once per scene. Night changes the backdrop between 21:00 and 05:59; it is not an ADS selection flag. See [story.c](../../src/engine/story.c) and [story_data.h](../../src/data/story_data.h).

Each JSON story entry includes a constructive static predecessor for non-final scenes. The predecessor can use high tide and an unmoved island, imposing no extra eligibility flags. This is a source-based eligibility witness, not an original scheduler comparison or a playback trace.

| Story day | Day-specific scene | Original tag description |
|---:|---|---|
| 1 | `MARY.ADS#2` | JOHNNY GLIMPLSE MARY |
| 2 | `JOHNNY.ADS#2` | JOHN'S 1ST MESSAGE |
| 3 | `SUZY.ADS#1` | SUZY CITY DWELLER |
| 4 | `MARY.ADS#3` | JOHNNY ASKS FOR DATE |
| 5 | `MARY.ADS#1` | THE DATE |
| 6 | `JOHNNY.ADS#3` | JOHN FINAL MESSAGE |
| 7 | `MARY.ADS#4` | JOHN & MARY BREAK UP |
| 8 | `MARY.ADS#5` | JOHNNY LEAVES |
| 9 | `SUZY.ADS#2` | JOHN MEETS SUZY |
| 10 | `JOHNNY.ADS#6` | JOHN AT WORK |
| 11 | `JOHNNY.ADS#1` | THE END |

`BUILDING.ADS#9` (FIRE (NIGHT)) is command-for-command identical to #5; `BUILDING.ADS#8` (EAT (NIGHT)) is identical to #7. The scheduler comments out those aliases. `STAND.ADS#14` (STAND INIT) is invoked through GOSUB_TAG and is not a missing standalone scene.

## ADS scene catalog

Descriptions below come from original resource metadata. TTM references include explicit ADD_SCENE and ADD_SCENE_LOCAL operations plus transitive ADS GOSUB helpers. They are a conservative dependency inventory; conditions and random branches are not claimed to execute on every visit.

| ADS tag | Description | Story day / role | TTM dependencies |
|---|---|---|---|
| `ACTIVITY.ADS#1` | GAG DIVES | any day / final | `GJDIVE.TTM`, `MJDIVE.TTM` |
| `ACTIVITY.ADS#4` | MUNDANE DIVE | any day / lead-in | `MJDIVE.TTM` |
| `ACTIVITY.ADS#5` | NATIVE 1 | any day / final | `GJNAT1.TTM` |
| `ACTIVITY.ADS#6` | GAG JOHN READ | any day / final | `MJREAD.TTM` |
| `ACTIVITY.ADS#7` | MUNDANE JOHN READ | any day / lead-in | `MJREAD.TTM` |
| `ACTIVITY.ADS#8` | JOHN BATH | any day / lead-in | `MJBATH.TTM` |
| `ACTIVITY.ADS#9` | NATIVE 3 | any day / final | `GJNAT1.TTM`, `GJNAT3.TTM` |
| `ACTIVITY.ADS#10` | GULL 1 READING | any day / final | `MJREAD.TTM` |
| `ACTIVITY.ADS#11` | GULL 2 BATHING | any day / final | `MJBATH.TTM` |
| `ACTIVITY.ADS#12` | GULL 3 STILL READING | any day / final | `MJREAD.TTM` |
| `BUILDING.ADS#1` | MJSAND | any day / lead-in | `MJSAND.TTM` |
| `BUILDING.ADS#2` | LILIPUT 2 | any day / final | `MJSAND.TTM` |
| `BUILDING.ADS#3` | MUNDANE SLEEP | any day / lead-in | `GJGULIVR.TTM` |
| `BUILDING.ADS#4` | LILIPUT 1 | any day / final | `GJGULIVR.TTM` |
| `BUILDING.ADS#5` | JOHN BUILDS FIRE | any day / lead-in | `MJFIRE.TTM` |
| `BUILDING.ADS#6` | LILIPUT 3 NIGHT | any day / final | `GJGULIVR.TTM` |
| `BUILDING.ADS#7` | EAT | any day / lead-in | `MJFIRE.TTM` |
| `BUILDING.ADS#8` | EAT (NIGHT) | not_selected_by_story | `MJFIRE.TTM` |
| `BUILDING.ADS#9` | FIRE (NIGHT) | not_selected_by_story | `MJFIRE.TTM` |
| `FISHING.ADS#1` | FISH AT A (JUNK) | any day / lead-in | `MJFISH.TTM` |
| `FISHING.ADS#2` | FISH AT A KEEPERS | any day / lead-in | `MJFISH.TTM` |
| `FISHING.ADS#3` | EIGHT ARM MENACE | any day / final | `GJCATCH2.TTM`, `MJFISH.TTM` |
| `FISHING.ADS#4` | CATCH 1 | any day / final | `MJFISHC.TTM` |
| `FISHING.ADS#5` | FISH EATS FOUL FOOD | any day / final | `FISHWALK.TTM`, `GFFFOOD.TTM` |
| `FISHING.ADS#6` | CATCH 3 | any day / final | `MJFISH.TTM` |
| `FISHING.ADS#7` | FISH AT C FOR JUNK | any day / lead-in | `MJFISHC.TTM` |
| `FISHING.ADS#8` | FISH AT KEEPERS | any day / lead-in | `MJFISHC.TTM` |
| `JOHNNY.ADS#1` | THE END | day 11 / final | `MEANWHIL.TTM`, `THEEND.TTM` |
| `JOHNNY.ADS#2` | JOHN'S 1ST MESSAGE | day 2 / final | `SJMSSGE.TTM` |
| `JOHNNY.ADS#3` | JOHN FINAL MESSAGE | day 6 / lead-in | `SJMSSGE.TTM` |
| `JOHNNY.ADS#4` | BOTTLE (FIND) | any day / lead-in | `SJMSSGE.TTM` |
| `JOHNNY.ADS#5` | BOTTLE (THROW) | any day / lead-in | `SJMSSGE.TTM` |
| `JOHNNY.ADS#6` | JOHN AT WORK | day 10 / final | `MEANWHIL.TTM`, `SJWORK.TTM` |
| `MARY.ADS#1` | THE DATE | day 5 / final | `SMDATE.TTM` |
| `MARY.ADS#2` | JOHNNY GLIMPLSE MARY | day 1 / final | `SJGLIMPS.TTM` |
| `MARY.ADS#3` | JOHNNY ASKS FOR DATE | day 4 / final | `SASKDATE.TTM` |
| `MARY.ADS#4` | JOHN & MARY BREAK UP | day 7 / final | `SBREAKUP.TTM` |
| `MARY.ADS#5` | JOHNNY LEAVES | day 8 / final | `SJLEAVES.TTM` |
| `MISCGAG.ADS#1` | HOT SUMMER DAYS | any day / final | `GJHOT.TTM` |
| `MISCGAG.ADS#2` | SHARK1 | any day / final | `SHARK1.TTM` |
| `STAND.ADS#1` | MUN. AMB. POS.A  SW | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#2` | MUN AMB POS.A W | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#3` | MUN AMB POS.A NW | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#4` | MUN AMB POS.B SW | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#5` | MUN AMB POS.B S | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#6` | MUN AMB POS.B SE | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#7` | MUN AMB POS.C NE | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#8` | MUN AMB POS.C E | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#9` | MUN AMB POS.D  NW | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#10` | MUN AMB POS.D NE | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#11` | MUN AMB POS.E NW | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#12` | MUN AMB POS.F NE | any day / lead-in | `MJAMBWLK.TTM` |
| `STAND.ADS#14` | STAND INIT | helper_via_gosub | `MJAMBWLK.TTM` |
| `STAND.ADS#15` | TELESCOPE POS. A | any day / lead-in | `MJTELE.TTM` |
| `STAND.ADS#16` | TELESCOPE POS C | any day / lead-in | `MJTELE.TTM` |
| `SUZY.ADS#1` | SUZY CITY DWELLER | day 3 / final | `MEANWHIL.TTM`, `SUZYCITY.TTM` |
| `SUZY.ADS#2` | JOHN MEETS SUZY | day 9 / final | `MEANWHIL.TTM`, `SJMSUZY.TTM` |
| `VISITOR.ADS#1` | VISITOR 3 | any day / lead-in | `GJVIS3.TTM` |
| `VISITOR.ADS#3` | VISITOR 6 | any day / final | `GJVIS6.TTM` |
| `VISITOR.ADS#4` | COCONUT DROP L & R | any day / lead-in | `MJCOCO.TTM` |
| `VISITOR.ADS#5` | COCONUT VISITOR 5  | any day / final | `GJVIS5.TTM` |
| `VISITOR.ADS#6` | COCONUT 360 | any day / lead-in | `MJCOCO.TTM` |
| `VISITOR.ADS#7` | COCONUT CHASE | any day / lead-in | `MJCOCO.TTM` |
| `WALKSTUF.ADS#1` | WOULDBEAS | any day / final | `WOULDBE.TTM` |
| `WALKSTUF.ADS#2` | MJ RAFT | any day / lead-in | `MJRAFT.TTM` |
| `WALKSTUF.ADS#3` | JOG | any day / lead-in | `MJJOG.TTM` |

## TTM resource inventory

Declared tag records can describe local labels as well as global entry points. `SASKDATE.TTM` has 40 declared records, including five local labels (129, 133, 140, 146, 151), and 35 global tags. Those local labels are present; they must not be classified as missing animation tags.

| TTM | Declared pages | Global / local labels | Story ADS dependency | Original decoded bytes |
|---|---:|---:|---|---|
| `FIRE.TTM` | 41 | 13 / 0 | none | identical |
| `FISHWALK.TTM` | 23 | 1 / 0 | `FISHING.ADS#5` | identical |
| `GFFFOOD.TTM` | 48 | 1 / 0 | `FISHING.ADS#5` | identical |
| `GJCATCH2.TTM` | 62 | 2 / 0 | `FISHING.ADS#3` | identical |
| `GJDIVE.TTM` | 119 | 7 / 0 | `ACTIVITY.ADS#1` | identical |
| `GJGULIVR.TTM` | 473 | 27 / 0 | `BUILDING.ADS#4`, `BUILDING.ADS#3`, `BUILDING.ADS#6` | identical |
| `GJGULL1.TTM` | 110 | 13 / 0 | none | identical |
| `GJHOT.TTM` | 90 | 7 / 0 | `MISCGAG.ADS#1` | identical |
| `GJLILIPU.TTM` | 101 | 7 / 0 | none | identical |
| `GJNAT1.TTM` | 181 | 15 / 0 | `ACTIVITY.ADS#5`, `ACTIVITY.ADS#9` | identical |
| `GJNAT3.TTM` | 208 | 10 / 0 | `ACTIVITY.ADS#9` | identical |
| `GJVIS3.TTM` | 203 | 11 / 0 | `VISITOR.ADS#1` | identical |
| `GJVIS5.TTM` | 192 | 7 / 0 | `VISITOR.ADS#5` | identical |
| `GJVIS5W.TTM` | 135 | 3 / 0 | none | identical |
| `GJVIS6.TTM` | 156 | 7 / 0 | `VISITOR.ADS#3` | identical |
| `MEANWHIL.TTM` | 50 | 1 / 0 | `JOHNNY.ADS#1`, `JOHNNY.ADS#6`, `SUZY.ADS#1`, `SUZY.ADS#2` | identical |
| `MJAMBWLK.TTM` | 275 | 61 / 0 | `STAND.ADS#1`, `STAND.ADS#2`, `STAND.ADS#3`, `STAND.ADS#4`, `STAND.ADS#5`, `STAND.ADS#6`, `STAND.ADS#7`, `STAND.ADS#8`, `STAND.ADS#9`, `STAND.ADS#10`, `STAND.ADS#11`, `STAND.ADS#12` | identical |
| `MJBATH.TTM` | 201 | 35 / 0 | `ACTIVITY.ADS#11`, `ACTIVITY.ADS#8` | identical |
| `MJCOCO.TTM` | 146 | 11 / 0 | `VISITOR.ADS#4`, `VISITOR.ADS#6`, `VISITOR.ADS#7` | identical |
| `MJCOCO1.TTM` | 125 | 16 / 0 | none | identical |
| `MJDIVE.TTM` | 94 | 3 / 0 | `ACTIVITY.ADS#1`, `ACTIVITY.ADS#4` | identical |
| `MJFIRE.TTM` | 333 | 40 / 0 | `BUILDING.ADS#5`, `BUILDING.ADS#7` | identical |
| `MJFISH.TTM` | 374 | 34 / 0 | `FISHING.ADS#1`, `FISHING.ADS#2`, `FISHING.ADS#3`, `FISHING.ADS#6` | identical |
| `MJFISHC.TTM` | 257 | 25 / 0 | `FISHING.ADS#4`, `FISHING.ADS#7`, `FISHING.ADS#8` | identical |
| `MJJOG.TTM` | 225 | 13 / 0 | `WALKSTUF.ADS#3` | identical |
| `MJRAFT.TTM` | 36 | 8 / 0 | `WALKSTUF.ADS#2` | identical |
| `MJREAD.TTM` | 301 | 38 / 0 | `ACTIVITY.ADS#12`, `ACTIVITY.ADS#10`, `ACTIVITY.ADS#6`, `ACTIVITY.ADS#7` | identical |
| `MJSAND.TTM` | 298 | 46 / 0 | `BUILDING.ADS#1`, `BUILDING.ADS#2` | identical |
| `MJTELE.TTM` | 124 | 15 / 0 | `STAND.ADS#15`, `STAND.ADS#16` | identical |
| `SASKDATE.TTM` | 213 | 35 / 5 | `MARY.ADS#3` | identical |
| `SBREAKUP.TTM` | 141 | 11 / 0 | `MARY.ADS#4` | identical |
| `SHARK1.TTM` | 79 | 3 / 0 | `MISCGAG.ADS#2` | identical |
| `SJGLIMPS.TTM` | 203 | 7 / 0 | `MARY.ADS#2` | identical |
| `SJLEAVES.TTM` | 152 | 4 / 0 | `MARY.ADS#5` | differs; see JSON |
| `SJMSSGE.TTM` | 151 | 23 / 0 | `JOHNNY.ADS#2`, `JOHNNY.ADS#3`, `JOHNNY.ADS#4`, `JOHNNY.ADS#5` | identical |
| `SJMSUZY.TTM` | 86 | 4 / 0 | `SUZY.ADS#2` | identical |
| `SJWORK.TTM` | 27 | 5 / 0 | `JOHNNY.ADS#6` | identical |
| `SMDATE.TTM` | 195 | 10 / 0 | `MARY.ADS#1` | identical |
| `SUZYCITY.TTM` | 99 | 11 / 0 | `SUZY.ADS#1` | identical |
| `THEEND.TTM` | 76 | 7 / 0 | `JOHNNY.ADS#1` | identical |
| `WOULDBE.TTM` | 228 | 14 / 0 | `WALKSTUF.ADS#1` | identical |

TTM files not referenced by the active story ADS dependency graph: `FIRE.TTM`, `GJGULL1.TTM`, `GJLILIPU.TTM`, `GJVIS5W.TTM`, `MJCOCO1.TTM`. They remain addressable with the direct `ttm` CLI mode. Their presence in the original archive does not prove the original scheduler used them. Similar actions are named in active scripts (fire in MJFIRE, reading gulls in MJREAD, tiny-islander scenes in MJSAND/GJGULIVR, the aircraft encounter in GJVIS5, and coconuts in MJCOCO). Treat these as unused resource variants until the original control flow or a reliable scene observation proves a distinct omission.

## Concrete implementation gaps

The following commands actually occur in shipped scripts and have omitted, simplified, or uncertain semantics in the port. Counts are static occurrences across all 41 TTM or 10 ADS resources. A command gap is evidence of incomplete interpreter behavior; it does not by itself prove that a particular visible gag is absent.

| Language / command | Occurrences | Current behavior | Source |
|---|---:|---|---|
| ADS `IF_UNKNOWN_1` | 55 | Condition is read and logged but not evaluated. | [src/engine/ads.c:583](../../src/engine/ads.c#L583) |
| ADS `AND` | 47 | Logged only; surrounding condition handling is specialized. | [src/engine/ads.c:617](../../src/engine/ads.c#L617) |
| ADS `UNKNOWN_6` | 4 | Three arguments are read but have no playback effect. | [src/engine/ads.c:701](../../src/engine/ads.c#L701) |
| ADS `FADE_OUT` | 67 | Script fade command logs only; story-level fades are a separate path. | [src/engine/ads.c:706](../../src/engine/ads.c#L706) |
| TTM `DRAW_BACKGROUND` | 190 | Playback logs only; no draw or image-slot release. | [src/engine/ttm.c:290](../../src/engine/ttm.c#L290) |
| TTM `SET_DELAY` | 1147 | Values below four ticks are clamped to four. | [src/engine/ttm.c:308](../../src/engine/ttm.c#L308) |
| TTM `SET_PALETTE_SLOT` | 41 | Palette slot argument has no effect. | [src/engine/ttm.c:324](../../src/engine/ttm.c#L324) |
| TTM `TTM_UNKNOWN_1` | 61 | Region identifier is read but not stored. | [src/engine/ttm.c:336](../../src/engine/ttm.c#L336) |
| TTM `SET_FRAME1` | 52 | Arguments are read and logged only. | [src/engine/ttm.c:355](../../src/engine/ttm.c#L355) |
| TTM `TIMER` | 152 | Uses the arithmetic mean of both arguments; source explicitly questions this formula. | [src/engine/ttm.c:361](../../src/engine/ttm.c#L361) |
| TTM `SAVE_IMAGE1` | 60 | Playback calls grSaveImage1, whose body does not save anything. | [src/engine/graphics.c:385](../../src/engine/graphics.c#L385) |
| TTM `SAVE_ZONE` | 1 | grSaveZone does not save the requested zone. | [src/engine/graphics.c:399](../../src/engine/graphics.c#L399) |
| TTM `RESTORE_ZONE` | 1 | Drops the entire saved layer rather than restoring the requested rectangle. | [src/engine/graphics.c:411](../../src/engine/graphics.c#L411) |
| TTM `CLEAR_SCREEN` | 6814 | Clears the full layer; ignores the supplied saved-region identifier. | [src/engine/ttm.c:457](../../src/engine/ttm.c#L457) |
| TTM `DRAW_SCREEN` | 6 | Six arguments are read and logged without drawing. | [src/engine/ttm.c:463](../../src/engine/ttm.c#L463) |
| TTM `LOAD_PALETTE` | 41 | Palette filename is read and logged only. | [src/engine/ttm.c:482](../../src/engine/ttm.c#L482) |

Narrow animation investigations supported by these facts:

- `GJGULIVR.TTM` contains the only SAVE_ZONE and RESTORE_ZONE pair. Saving is a stub and restoration drops the whole saved layer, so region restoration needs original-frame comparison.
- Six DRAW_SCREEN operations are ignored: three in MJSAND and one each in GJGULIVR, SASKDATE, and SBREAKUP. The JSON records their containing tags. These are specific candidates for incomplete visual operations.
- Script fades, palette selection, saved-region identifiers, and image-save requests have no equivalent operation at their command sites. The separate story transition and initial palette paths must not be confused with those command implementations.
- TIMER uses an explicitly uncertain averaging formula, while SET_DELAY clamps short delays. Timing parity remains unproven even when every sprite and script resource is present.

Known opcode names with no shipped occurrence are included in JSON with total zero. They are not evidence of missing shipped animation behavior.

## Fan catalog crosswalk

The [fan catalog](scene-catalog.md) records secondary observations, not a complete original specification. The JSON associates its stable IDs with scene families and explicit resource-tag evidence. A family match establishes an investigation starting point; it does not validate every object, action, outcome or timing detail mentioned by the fan. No named chapter in the eleven-day fan sequence lacks a corresponding scheduler day entry, but chapter presence does not prove all variants.

| Association | Fan observations |
|---|---:|
| calendar_source_alignment | 4 |
| candidate_family | 126 |
| context_source | 14 |
| story_day_alignment | 11 |
| unverified_legacy_fault | 18 |
| unmapped | 3 |

| Candidate family | ADS scene identifiers | Observation count |
|---|---|---:|
| sleep | `BUILDING.ADS#3`, `BUILDING.ADS#4`, `BUILDING.ADS#6` | 2 |
| fishing | `FISHING.ADS#1`, `FISHING.ADS#2`, `FISHING.ADS#7`, `FISHING.ADS#8` | 2 |
| food | `BUILDING.ADS#7` | 4 |
| reading | `ACTIVITY.ADS#6`, `ACTIVITY.ADS#7` | 3 |
| washing | `ACTIVITY.ADS#8` | 7 |
| jogging | `WALKSTUF.ADS#3` | 1 |
| sand-building | `BUILDING.ADS#1` | 1 |
| raft-building | `WALKSTUF.ADS#2` | 1 |
| fire-variants | `BUILDING.ADS#5` | 4 |
| coconut-bounces | `VISITOR.ADS#4` | 2 |
| coconut-spin | `VISITOR.ADS#6` | 1 |
| coconut-food | `VISITOR.ADS#7` | 1 |
| messages | `JOHNNY.ADS#2`, `JOHNNY.ADS#3`, `JOHNNY.ADS#4`, `JOHNNY.ADS#5` | 9 |
| fishing-catches | `FISHING.ADS#1`, `FISHING.ADS#2`, `FISHING.ADS#4`, `FISHING.ADS#6`, `FISHING.ADS#7`, `FISHING.ADS#8` | 14 |
| large-octopus | `FISHING.ADS#3` | 3 |
| diving | `ACTIVITY.ADS#1`, `ACTIVITY.ADS#4` | 4 |
| clothes-gull | `ACTIVITY.ADS#11` | 3 |
| bathing-shark | `MISCGAG.ADS#2` | 3 |
| reading-gull | `ACTIVITY.ADS#10`, `ACTIVITY.ADS#12` | 4 |
| pirate-gull | `BUILDING.ADS#4`, `BUILDING.ADS#6` | 5 |
| mary-glimpse | `MARY.ADS#2` | 4 |
| mary-invitation | `MARY.ADS#3` | 4 |
| mary-date | `MARY.ADS#1` | 3 |
| mary-breakup | `MARY.ADS#4` | 2 |
| mary-farewell | `MARY.ADS#5` | 3 |
| office | `JOHNNY.ADS#6` | 2 |
| castle-pirates | `BUILDING.ADS#2` | 5 |
| suzy-bottle | `SUZY.ADS#1` | 2 |
| suzy-reunion | `SUZY.ADS#2` | 7 |
| telescope | `STAND.ADS#15`, `STAND.ADS#16`, `VISITOR.ADS#1` | 1 |
| passing-travelers | `VISITOR.ADS#1` | 8 |
| party-boat | `WALKSTUF.ADS#1` | 2 |
| cargo-ship | `VISITOR.ADS#3` | 3 |
| coconut-aircraft | `VISITOR.ADS#5` | 2 |
| rain-dance-visitors | `ACTIVITY.ADS#9` | 1 |
| rain-dance | `ACTIVITY.ADS#5`, `ACTIVITY.ADS#9` | 1 |
| melting | `MISCGAG.ADS#1` | 1 |
| ending | `JOHNNY.ADS#1` | 1 |

Unmapped individual observations: `fan:unusual:duplicate-fight`, `fan:unusual:shark-swallow`, `fan:unusual:silver-shapes`.

These unresolved IDs are identification work, not confirmed missing animations. Exact fire-rubbing counts, night-specific gull outcomes, unusual catch artifacts, detailed reunion variants, and the Christmas octopus outcome also remain unverified within their candidate families. The eighteen legacy fault reports are kept separate from required animation behavior. All four fan calendar windows match the manually reviewed port date conditions; decorative rendering parity remains unproven.

## What testing proves

The golden dump covers decoded port assets and textual scripts. Rendering tests exercise selected sprite, screen, wave, palm, alpha, clipping, and fallback paths. Browser audio timing uses the shipped GJHOT sample sequence. None of those is an exhaustive original-versus-port scene-frame oracle. All scene records therefore leave original_render_parity_proven false. See [tests/BUILD_VALIDATION.md](../../tests/BUILD_VALIDATION.md), [Invoke-ArtStyleTests.ps1](../../tests/Invoke-ArtStyleTests.ps1), [test_wave_renderer.py](../../tests/test_wave_renderer.py), [test_palm_renderer.py](../../tests/test_palm_renderer.py), and [web-audio-timing.py](../../tests/web-audio-timing.py).

## Reproduce

Build the current production executable and decompressor probe, then run locally:

```powershell
python -B tools/inventory_scenes.py `
  --probe build/Release/jc_uncompress_test.exe `
  --exe build/Release/jc_reborn.exe `
  --original-dir C:/JohnCast/SIERRA/SCRANTIC `
  --output docs/knowledge-base/port-inventory.json
```

The command writes this Markdown companion and JSON metadata. It reads the original resource pair without copying it into the repository. It uses the real production decompressor, splits large RLE inputs only at packet boundaries to fit Windows argv limits, and creates a temporary headless dump of the port archive for comparison with every golden hash. Input and executable hashes are recorded in JSON; tool and source changes require regeneration.

The command-support explanations and scheduler interpretation are manually reviewed source assessments, not semantic proofs derived from matching a switch label. Re-review these assessments when their recorded source hashes change. Run the focused fixture and mutation checks with `python -B tests/test_scene_inventory.py --mutations`.
