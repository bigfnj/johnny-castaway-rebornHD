# Profile walk native review plan

Source investigation: 2026-09-15, main
`00f1ba7148043079321c95e22d4f527b2e3aa575`. This is a route plan, not a
captured motion result or artwork approval. No new native capture was run.

## Main clips

Use separate clips so each starts with an actual standing call at its own
departure spot. Headings 6 and 2 are right-facing and left-facing profile.
Reset `srand(2)` immediately before **each** `adsPlayWalk` call, including
priming. Preserve the original rows, their repeated poses, and their origins.

| Clip | Actual priming call | Travel call | Travel frames in order | Flip | Source-derived duration including prime |
|---|---|---|---|---|---|
| Right-facing F-to-C | `adsPlayWalk(5,6,5,6)` | `adsPlayWalk(5,6,2,6)` | `003 004 005 006 007 008 001 002 003 004 006 007 008` | 0 throughout | 120 + 13*120 + 1600 = 3280 ms |
| Left-facing C-to-A | `adsPlayWalk(2,2,2,2)` | `adsPlayWalk(2,2,0,2)` | `(004 005 006 007 008 001 002 003)` repeated three times, then `004 005 005 006 007 008 001 002` | 1 throughout | 120 + 32*120 + 1600 = 5560 ms |

Both clips contain every profile asset 001-008 and finish with standing 000.
F-to-C's partial second cycle omits 005. C-to-A repeats 005 at identical
coordinates in its tail. Do not normalize either sequence into an ideal loop.
A-to-C is unsuitable as the primary pure-profile clip: after 24 profile
poses, it changes to rear-oblique frames 011, 019, 020, 021 and 022.

Travel and ordinary-turn draws return 6 ticks; the final arrival returns 80;
the next `walkAnimate` call returns 0. One tick is 20 ms. The public wrapper
initializes its first timer to 6 even when the first returned delay is 80,
so same-heading priming is 120 ms, not a fabricated 1600 ms hold. Keep this
known behavior unchanged. The durations above are derived segment budgets;
capture must separately record every actual display timestamp, including
zero-duration boundaries and background-driven displays. Pose count is not
display count.

## Route selection and proof scope

An in-memory enumeration following `calcPathRecurse` produced, in selection
order, F-to-C paths `FC`, `FEABC`, `FEAC`; C-to-A paths `CA`, `CBA`, `CDEA`.
The existing Linux image's glibc probe returned 1505335290 as the first
`rand()` after `srand(2)`, selecting direct path index 0 of 3. Its next value,
1738766719, selects index 1. Priming itself consumes a random result, so
seeding only once would take a detour. Assert the actual chosen-path log in
the future capture; do not assume the same RNG sequence on another runtime.

The preserved `front-arrival-v1/trace/trace.json` matched all 489 walk rows
against the supplied original executable at offset `0x188EA`. Its normalized
table SHA256 is
`3b387634d62a915cdf308c1e370eea7a70aa07bc361eb19de70ff4931aa2ad70`.
This supports original table geometry and frame order. The port's
`calcpath.c:86` explicitly says its path-selection algorithm is not exact
original reconstruction. Neither the prior trace nor this plan proves
original-binary timing or route-choice parity. These are original table rows
executed through the current port's public API.

## Standing, ordinary 003, and mirroring

The walk renderer uses native draw origin `(stored_x - 1, stored_y)`.
F heading 6 standing 000 and its first travel 003 share `(439,226)`, giving
an exact 000-to-003 departure comparison. F-to-C finishes 008-to-000 at C
heading 6. C-to-A starts 000-to-004 and finishes 002-to-000 at A heading 2.

Same-spot waits use the hands-in-pockets block and do not exercise ordinary
turn 003. Add these narrowly scoped departure probes after the main gait:

| Boundary | Prime | Travel call | Actual leading poses | Total expected duration |
|---|---|---|---|---|
| Unmirrored ordinary 003 | `adsPlayWalk(5,7,5,7)` | `adsPlayWalk(5,7,2,6)` | Approved 017, ordinary 003, travel 003, then the remaining F-to-C sequence and arrival 000 | 3400 ms |
| Mirrored ordinary 003 | `adsPlayWalk(2,3,2,3)` | `adsPlayWalk(2,3,0,2)` | Approved 018, ordinary 003, then C-to-A travel 004 onward and arrival 000 | 5680 ms |

Reseed every call as above. The first probe draws ordinary and travel 003
at the same origin for two successive 6-tick intervals. Preserve both draws.
The asymmetric heading condition in `walk.c:109` means a positive adjacent
departure can skip the ordinary turn pose; the specified negative-adjacent
calls deliberately exercise it. This does not approve 003's other TTM uses.

Mirror the **full original-derived runtime canvas**, including transparent
padding. `grDrawSpriteFlip` maps source pixel column `i` to
`(draw_x + grDx)*grScale + W - 1 - i`, where `W` is the complete loaded
surface width. The pixel-center pivot is `(W-1)/2`, not the visible alpha
bounding-box center. At HD scale 2, keep the original doubled canvas and
native placement. Cropping or independently recentering the mirrored sprite
would change its apparent trajectory. A flip flag does not establish
anatomical left/right identity.

## Capture adaptation

Reuse the wrappers, codec, native build and comparison logic preserved under
`front-arrival-v1/remaining-waits-v1/review-evidence/native-v1/`, with the
scratch staging assumptions explained in its separate `REPRODUCE.md`.
Reuse the small C draw/delay observer in `front-arrival-v1/trace/trace.py`
for new independent route contracts; its old 116-case report does not
already contain these profile travel cases.

1. Generalize the segment configuration/driver from A-only headings to four
   API arguments. Retain per-call reseeding and actual draw, delay, display,
   origin and flip observation; assert the direct selected routes.
2. Baseline the current production ZIP directly, SHA256
   `096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.
   Do not use the older ring baseline or re-add already promoted waits.
   Candidate packaging may add only 001-008; retain all 32 accepted assets
   and every other named ZIP member exactly.
3. Derive one fixed camera from the route-wide union of placed original and
   candidate art, with a modest margin. The ring's stationary camera is
   unsuitable. Do not track/recenter individual poses or change world
   coordinates. Retain a whole-island view where useful.
4. Generalize allowed candidate pixel boxes to the actual placed 001-008
   canvases. Require identical native draw/timing records and unchanged
   full displays when an approved standing pose is shown. Keep the ordinary
   003 boundary role distinct from travel 003 in labels.
5. Keep Normal/Slow, play/replay and pose stepping with resource frame IDs.
   Smoke before native comparison regression; use existing relevant
   witnesses and add bounded negative controls only for changed checks.
   Run Linux/Xvfb or an inactive desktop, never a visible native window.

## Source pointers at the inspected commit

| Evidence | Repo-relative source |
|---|---|
| F-to-C 13 rows; C-to-A 32 rows | `src/data/walk_data.h:456` and `:176` |
| Start/end headings and bookmarks | `src/data/walk_data.h:504`, `:518`, `:528` |
| F right-side ordinary 003 / standing 000 | `src/data/walk_data.h:490` / `:499` |
| C left-side ordinary 003 / standing 000 | `src/data/walk_data.h:275` / `:284` |
| A standing block | `src/data/walk_data.h:113` |
| Turn dispatch, draw origin and delays | `src/engine/walk.c:109`, `:185`, `:211` |
| Public first timer and subsequent timing loop | `src/engine/ads.c:1110`, `:1131` |
| Tick conversion | `src/engine/events.c:209` |
| Full-canvas mirror placement | `src/engine/graphics.c:659` |
| Path enumeration and random selection | `src/engine/calcpath.c:52`, `:127`; `src/data/calcpath_data.h` |
| Reusable per-segment reset / wrappers | `art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/review-evidence/native-v1/route_driver.c:93` |

Only documentation was added for this checkpoint. New capture and art
acceptance remain future work; no tests were required or run for this note.
