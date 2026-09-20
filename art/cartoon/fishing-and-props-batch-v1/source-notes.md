# Source interpretation for 64 drawings

This batch contains 42 fishing catches, gear and water effects plus 22 aircraft, flags and scene effects. These notes describe the original reference; they do not grant appearance approval or establish native timing.

## Fishing group

| Resource | Selected frames | Count |
| --- | --- | ---: |
| MJFISH3.BMP | 000, 002-011, 013-022, 024-025, 031-032, 037 | 26 |
| MJFISH1.BMP | 022-026 | 5 |
| GJCATCH1.BMP | 007, 013-014, 016, 018-020 | 7 |
| GJCATCH2.BMP | 005-006, 010-011 | 4 |

Every selected source was visually inspected in an original contact sheet. All are independent objects, creatures or effects, with no visible Johnny anatomy. The set spans fishing catches and their support layers rather than a single invented animation loop. Source associations in selection.json are static map facts, not native timing or proof of unused frames.

MJFISH3 contains a crab (000), caught green fish (002-004,008-010,031-032), rotating starfish (005-007), lifebelts (011,022), a plank/board in six rotations (013-018), three dangling octopus poses (019-021), splash effects (024-025) and a boot orientation (037). MJFISH.TTM tag36 names the board and tag35 the preserver. The board is not a red animal or tentacle. Retain the split/chipped ends and each rotation. The long patterned appendages on fish002-004 are the fish tail/fins, not human hands; keep each fish silhouette and visible eye count. MJFISH3 031/032 have no unique-slot static attribution in the retained map, which does not prove they are unused.

MJFISH1 022/023 and GJCATCH1 007/013/016/018 plus GJCATCH2 010 are fishing rods/rod-and-line poses. Preserve reel position, bend, line and source clipping boundaries without adding an attached hand. The remaining MJFISH1 images are subtle water rings. GJCATCH1 014 is surface foam and 019/020 are partial surfacing shark fins, not incomplete Johnny anatomy. Reuse the approved shark material identity while preserving the visible fin-only extent. GJCATCH2 005/006/011 are splash/ripple phases; use the clean white and pale cyan water style and retain their sparse droplets and open spaces.

No selected slot already has a generated or production counterpart. Exact visible RGBA crop comparisons, also mirrored horizontally, found no collisions within this selection or against the drafted/production/current36 source slots. This is not a claim that no asset has a similar pose or a differently scaled counterpart. All extracted PNGs matched their preserved original archive hashes. Original colors are the port's diagnostic palette, not calibrated original colors.

Explicit exclusions: GJCATCH2 002 exactly repeats the visible source crop of drafted LILFISH008; MJFISH3 023 repeats FIRE2 023 and mirrors FIRE5 001. GJCATCH2 023 is only a black motion streak. MJFISH2 023 is a tiny separate clothing/cap-like shape best left with its character assembly. GJCATCH3 001/002 are small green fragments and the rest of that family is deferred as a group. Johnny composites, body pieces and markers from all six examined families stay excluded.


The dangling cephalopods at MJFISH3 019-021 show two white eye clusters, with a smaller partly hidden far eye. The first prompts missed that small cluster; selected v2 edits restore it while retaining the original arm poses. Fish 009's selected revision also restores the eye to the source's right side. Source fishing-line fragments are thin. MJFISH3 004 v2 retains a thread touching the top canvas edge; the fish and fins are complete. A discarded endpoint-only v3 still touched that edge. Line attachment and native registration remain for integration.

## Aircraft and flags

- GJBIPLAN.BMP 000-009, 020-023: 14 drawings. Navigation groups: Biplane views (000-006), Flying flags (007-009), Raising flag (020-023).
- GJVIS52.BMP 000, 004-007, 010, 016, 017: 8 drawings. Navigation group: Plane and crash effects.

Exact originals were read from the pinned reference archive, with every PNG hash verified. Existing production, prior generated slots, current marine slots and the queued 42 were excluded. The selected 22 have no exact visible-crop or horizontal-mirror match against those exclusions or within the examined candidate pool. This detects exact reuse, not all semantic similarity.

The source palette is diagnostic. Preserve each plane's direction, bank and visible body parts; no selected source shows a person to be invented. GJBIPLAN 007-009 are flags: inventory static attribution is MJSAND.TTM tag 46, FLAGS FLY. 020-022 are flag-raising phases; 023 is the bare pole. GJVIS52 004 is an abstract projectile/motion trail with two long diagonal strands and a loose circular arc at the upper right, with red/white accents. A neutral-background source inspection superseded the initial detached-propeller interpretation; do not invent a metal shaft or whole aircraft. The inventory calls it a projectile trail and associates it with GJVIS5 tag 3. 005-007 are burning aircraft views, 010 the water-entry/crash layer, 016 a separate splash and 017 a distant plane. These pieces have scene assembly dependencies and are not all interchangeable complete aircraft.

Uncertain aircraft occupants, placeholders, bottle fragments with baked blue backplates, exact duplicate bottles and all four CLOUDS slots were excluded from this 64-drawing selection. Static script attribution is source context only, not a native-motion verification.

Exact originals and nearest-neighbor enlargements are saved under reference/original and reference/nearest8. reference/source.json binds their archive member paths, hashes and static frame associations.
