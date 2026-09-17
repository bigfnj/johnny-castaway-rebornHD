# Low-tide runtime and source preflight

Read-only review of primary main `da787d63279ea91bd6c637e02133821339470bfc`. No runtime/art changes, extraction files or GUI launches. The only written file is this report. Native results cited below are retained prior evidence, not fresh captures.

## Exact placement contract

All coordinates below are unshifted. The engine uses 640x480 logical coordinates and Cartoon scale 2. For these fourteen slots, surface origin is `2 * (logical origin + islandState offset)`, with no asset-specific offset and no reflection. Every call is `grDrawSprite`, not `grDrawSpriteFlip` (`island.c:241-251`, `116-148`). Existing special footprint rules cover 000 and high-tide 003-011 only (`art_style.c:305-350`, `378-389`). A new low-tide PNG must therefore retain the exact HD canvas below unless a separate footprint contract is explicitly implemented.

| Frame(s) | Use | Logical origin | Native canvas | Required HD canvas | Default HD canvas bounds, right/bottom exclusive |
| --- | --- | --- | --- | --- | --- |
| 001 | Exposed lower beach, including starfish and shells | 249,303 | 384x69 | 768x138 | [498,606,1266,744] |
| 002 | Separate left rock | 150,328 | 64x30 | 128x60 | [300,656,428,716] |
| 030,032 | Beach left wave | 233,323 | 120x48 | 240x96 | [466,646,706,742] |
| 031 | Beach left wave, wider transparent canvas | 233,323 | 128x48 | 256x96 | [466,646,722,742] |
| 033-035 | Beach center wave | 367,356 | 176x28 | 352x56 | [734,712,1086,768] |
| 036-038 | Beach right wave | 558,323 | 88x48 | 176x96 | [1116,646,1292,742] |
| 039-041 | Ring around the separate rock | 129,340 | 104x29 | 208x58 | [258,680,466,738] |

Do not normalize 031 to the widths of 030/032. Its authentic original alpha support ends at local x120, but the original canvas is 128 wide. The right family's canvas extends 12 HD pixels beyond the default 1280-wide screen; current HD 036-038 have no nonzero alpha in that clipped padding. This does not authorize cropping newly generated artwork there. Shifted scene clipping is normal and needs separate review from source-canvas clipping.

The union of the four low-wave family canvases is [258,646,1292,768], clipped to [258,646,1280,768] at the default render size. The restoration code calculates the union from actual loaded phase sizes rather than assuming one size per family (`island.c:62-114`).

## Layer order and accepted 000

`islandInit` draws, in order: ocean/night screen; selected raft; 000 ground; trunk 013; leaves 012; palm shadow 014; low-tide beach 001; rock 002; four initial wave updates. The saved wave background is captured after 001/002 and before waves (`island.c:182-263`). Consequently 001 can cover already drawn ground, trunk or shadow where its artwork overlaps them; it is not a layer placed underneath 000.

Final screen composition is background including waves, clouds, saved-zone overlay if present, active TTM/Johnny layers, then holiday decorations (`graphics.c:282-325`). Waves are behind Johnny and the holiday layer. Low-tide raft origin is logical529,281, compared with high-tide512,266 (`island.c:186-195`); this matters at the upper-right beach join.

Accepted 000 remains the 640x180 surface at world HD [540,548,1180,728], logical asset offset [-36,-10], PNG SHA256 `22b426952abb1877e7c77111da0f4f0826dc86ff7a993c4390156c0f55166d9d`. Exact current alpha-support intersection, measured directly from production PNGs at those coordinates:

- Current 001 overlaps nonzero-alpha 000 at 13,060 HD pixel positions. These are support intersections, not a color-difference or opaque-coverage measurement.
- Current 002 and all twelve current low-wave PNGs have zero nonzero-alpha support intersection with 000. Their rectangular canvases sometimes overlap its padding, but their actual visible pixels do not.

This makes the 001 upper seam the first composition target. Preserve the accepted 000 source and placement. Design the exposed beach and its wave families together; do not move the seasonal props to compensate for a new beach outline. The current 001 contains embedded beach objects, so an apparently simple sand-only replacement would silently remove the starfish and shells.

## Tide switching and animation

Low tide is selected once for an island story sequence when the final scene has LOWTIDE_OK and `rand()%2` is nonzero (`story.c:159-165`, `243-255`). Intermediate scene selection requires LOWTIDE_OK when the island is low (`story.c:268-269`). It is not a continuous rising/falling water transition and has no separate tide-switch animation. A later island initialization rebuilds the background. High tide uses only003-011; low tide uses only030-041 plus001/002. Neither standard CLI mode nor the calendar selects low tide directly; deterministic inspection uses the established native driver's explicit island state.

Wave family array order is rock039, left030, center033, right036 (`island.c:45-47`). `islandAnimate` advances family before drawing and advances phase after wrapping back to family0 (`268-282`). In a fresh process, initial four draws are030,033,036,039, all phase0. Later draw order is031,034,037,040,032,035,038,041,030,033,036,039, then repeats. This is a staggered update, not one simultaneous triplet switch.

The island timer is 8 ticks (`island.c:263`), and each requested tick is 20ms (`events.c:217`). Thus one family updates every 160ms, each individual family every 640ms, and the low-wave phase state recurs every 1920ms. High tide has three families and a 1440ms recurrence. The ADS/walk scheduler shares the wave timer with other threads (`ads.c:830-839`, `887-919`, `1119-1148`), so extra displays can occur between phase changes; requested timing is not measured wall-clock playback time.

Retained final-production low-clover evidence confirms this directly: 61 displays over2880 requested milliseconds, all030-041, phase vectors in order [left,center,right,rock]:

```text
   0 [30,33,36,39]
 160 [31,33,36,39]
 320 [31,34,36,39]
 480 [31,34,37,39]
 640 [31,34,37,40]
 800 [32,34,37,40]
 960 [32,35,37,40]
1120 [32,35,38,40]
1280 [32,35,38,41]
1440 [30,35,38,41]
1600 [30,33,38,41]
1760 [30,33,36,41]
1920 [30,33,36,39]
```

This is phase-state recurrence, not proof that the whole scene including clouds, Johnny or old stamped pixels loops exactly. Static counters survive `islandRelease`/`islandInit`; fresh-process starting phases must not be promised after arbitrary prior scenes. Existing BACKLOG already records that limitation.

## Source materials are baked into the waves

Inspected all fourteen exact original PNGs in memory, enlarged only with nearest-neighbor display. The archive is `art/cartoon/character-inventory-v1/reference-originals.zip`, SHA256 `b9a906dd6508b013e860c9ca7396b21ea78776f5c7d086b71f13f1ac530bd912`; members are `native/BMP/BACKGRND.BMP/NNN.png`. These are supplied-original pixels rendered with a diagnostic palette, not calibrated original-executable color.

The beach wave sprites contain sand, water and crest/foam together. Rock-ring frames contain dark rock-edge pixels as well as water/crest. They are not interchangeable foam-only cutouts. Exact diagnostic-color counts use sand `A>0 && R==G && R>0 && B==0`, water `A>0 && R==0 && B>0`. White/gray material is deliberately unclassified because foam and substrate dithering share those colors.

| Frame | Diagnostic sand pixels | Diagnostic water pixels |
| --- | ---: | ---: |
| 001 | 7667 | 110 |
| 002 | 38 | 0 |
| 030 | 270 | 1711 |
| 031 | 183 | 1672 |
| 032 | 216 | 1590 |
| 033 | 823 | 1842 |
| 034 | 950 | 1653 |
| 035 | 1026 | 1478 |
| 036 | 250 | 1155 |
| 037 | 158 | 1134 |
| 038 | 164 | 1079 |
| 039 | 2 | 1030 |
| 040 | 2 | 1073 |
| 041 | 2 | 1056 |

The left and right sides have strongest measured sand reduction in their middle frames, followed by partial recovery. Center033-to035 instead exposes progressively more measured sand and less water before resetting. This rules out a blanket instruction that every higher frame number must wash farther inland. Local crests move irregularly; the counts are material witnesses, not complete semantic masks or a precise scalar waterline.

## Alpha and packing constraint

Production currently has no Cartoon001/002/030-041, so all fourteen use HD fallback. Their actual PNG alpha values are only0/255. With no selected-style low wave present, `islandSaveWaveBase` returns without a cache and existing wave updates stamp directly (`island.c:70-96`, `119-123`). Merely adding the first Cartoon low-wave member enables save/restore and ordered redraw for all four low families, including any remaining HD phases. Updated families become topmost, preserving drawing order rather than erasing overlapping neighbors.

Therefore the first partial wave replacement changes the compositing path for the entire low-wave union. Compare complete cycles, including unchanged fallback neighbors. Prefer delivering the low beach and all four motion families as one reviewed group. If art uses persistent ground plus transparent water, retain intentional wash over sand. Do not copy the high-tide inverse-ground-alpha mask automatically: it would erase the incoming surf this source actually contains. If static/animated pieces share semitransparent ground pixels, assign those pixels deliberately to avoid repeated darkening; source alpha must not be thresholded as a fit workaround.

## Recommended native baseline and candidate captures

Use the current production archive, SHA256 `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`, as the immutable Cartoon baseline. Use the established observer/driver APIs from `art/cartoon/shoreline-repair-v1/integrated-shore-v1/native/driver.c` and the final-integration capture adapter as reference, in a new versioned harness. Historical helpers and their pinned archive expectations must remain unchanged.

| Capture | Explicit state and purpose |
| --- | --- |
| Default low-tide seam and full cycle | Seed11, day, offset0,0, low=1, raft=0, holiday=0. Capture immediately after initialization and after every actual display for at least32 same-heading waits. The established wait route yields3840 requested ms for32 waits, enough for two1920ms phase cycles; verify actual report timing rather than hardcoding an assumed image count. Show full scene plus beach/rock close-up at equal scale. |
| Holiday contact | Same state with holiday2 clovers; retain their accepted bytes and placement. This matches historical low-clover framing and exposes joins below the current island. |
| Shift and night | Night, offset(-80,+20), low=1, holiday2, same duration. Confirm every draw origin shifts(-160,+40) HD and the clipped union stays correct. Use a separate fresh process for each case. |
| Raft junction | Default day low-tide initialization with raft1 and raft5, capturing their fixed low-tide origin and both wave phases nearest the upper-right shore. The historical driver leaves raft at zero; a new isolated driver would set `islandState.raft` before `adsInitIsland`. This requires a small capture-adapter extension, not a runtime change or modification of the frozen driver. |
| Character and retained high-tide controls | Low-tide public walking routes D-C-F and B-A-E, preserving exact poses/origins/timing; a same-state high-tide cycle must retain the already accepted ground, nine waves and seasonal pixels. A whole-scene exact high-tide before/after comparison is appropriate if only the14 low-tide members change. |

For anatomy/material reference, retain the authentic original low-tide composition separately from current HD/Cartoon. Original versus bundled pixel differences and diagnostic palette limits remain explicit. Candidate A/B should use identical ocean, seed, tide, raft, holiday, island offset and frame timing. Verify all twelve phase IDs, repeat capture equality and intended changes within the union of001/002 and low-wave canvases, with separate allowance only if a reviewed new footprint is added. Do not permit a1440ms loop for low tide. Do not infer full story behavior from these explicit-state captures.

## Evidence identities and limits

Historical low-clover report: `art/cartoon/shoreline-repair-v1/integration-v1/native-final/evidence-v1/captures/motion/low_clover/candidate/smoke/report.json`, SHA256 `1223f46b5323bd4614fb0b46166efb0a35e057080ed8c36ced741aedd2f3981e`. It binds the current production archive and args `[2,0,0,0,1,0,24]`. This task read that report and source; it did not rerun it.

Current inspected runtime SHA256:

```text
src/engine/island.c 78795472d233c9b54bcd8ff32e032358e5e19434e4de7d2fdb26f521d6600737
src/engine/story.c b503cca4115b5852f4ed9cdc02c5aef77498c793bac9fdb2b517b19cd8c4b9a4
src/engine/ads.c c4d53220327f62676a159f1b3651626a8dabafdfa5bf625b5e94d443280eb4f6
src/engine/graphics.c fded8d14dbfa432242170e0a16010cb882d02f437d31e5a317bfe2baafcee392
src/engine/art_style.c f6519bfbb7fb9af09ae19b3d41b546bb644dda1952160eef1956ad7466051513
src/engine/events.c 041ac9fce76af2c3e1fc2eeef56ea9b92b45e1a4adc0087d5318720ccc2d57d2
```

No proposed art choice is human-approved by this preflight. No source-canvas expansion, image generation, production edit, native launch or new gate was performed.
