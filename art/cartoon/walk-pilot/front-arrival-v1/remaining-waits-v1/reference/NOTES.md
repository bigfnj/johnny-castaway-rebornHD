# Original-first standing references 000 and 015

These are byte-for-byte copies of previously decoded supplied-original references, not geometry measured from HD or Cartoon artwork. Each `NNN-source.json` binds its original metadata row, original RESOURCE hashes, native PNG, exact nearest-neighbor 8x enlargement, and relevant stored wait-table observations. The original commercial inputs and executable were not reread or rerun here.

The decoded pixels use the port dump's diagnostic palette with index 0 transparent. The colored stipple is original indexed content under that palette. This does not establish original-executable color, compositing or timing parity. Original gray shadow pixels contribute to visible bounds and the canvas bottom; those bounds are not foot-contact measurements.

## Pose and registration

| Frame | Original-first visual reading | Native canvas / runtime canvas | Original cap row 0 | Runtime cap target |
| --- | --- | --- | --- | --- |
| 000 | Strict screen-right profile. Near elbow bends to the waist/pocket; far arm and much of the far leg are occluded. Both feet remain planted and overlap in profile. Do not widen this into a front-facing stance. | 40x76 / 80x152 | Pixel-edge span x[26,28), midpoint 27 | [54,0.25] |
| 015 | Direct rear view, with face hidden. Back of head/cap, elbows outward, hands at the waist sides, separated planted legs and modestly outward feet. Use the back of the cap, not a front-facing emblem or invented visible eyes/nose. | 40x73 / 80x146 | Pixel-edge span x[16,19), midpoint 17.5 | [35,0.25] |

The X targets are the measured original row-0 outline midpoint multiplied by two. Y=0.25 is the inherited deliberate filtering margin, not an original point measurement. Use the established uniform generated-art scale 1/10 and fixed translation. These cap observations are not engine or anatomical anchors. Do not normalize feet, bounding boxes or separate axes to force agreement.

## Foot observations and limits

For an indicative check excluding gray shadow and black outline, select only exact RGBA colors `(252,0,0,255)`, `(252,252,252,255)`, `(168,168,0,255)` and `(168,0,0,255)`:

- In 000, the selected region at y>=65 has combined bounding box [6,65,22,73), with exclusive upper edges. The overlapping limbs do not support two independent sole heights. Splitting this profile down the image center separates heel/toe geography, not anatomical legs.
- In 015, selected pixels at y>=60 reach y=68 in both source halves x[0,20) and x[20,40). This is a colored-pixel observation, not proof of equal sole heights, exact ground plane or anatomical left/right identity.

Assess any apparent foot-depth or size change after the fixed cap registration and native placement. Raw-image extrema, different native canvas origins and mirrored draws cannot be compared as world-space foot motion. Do not assign hidden anatomical left/right labels from screen halves.

## Encoded use and mirroring

The pinned trace is `art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json`. The per-frame source records retain every relevant wait row and its corresponding compiled C draw. This is reuse of that stored trace, not a new capture or evidence that every story interaction has been reviewed.

| Frame | Wait headings at each node A through F | Node A actual draw origin | Recorded final delay |
| --- | --- | --- | --- |
| 000 | 2/W mirrored; 6/E unflipped | Mirrored (284,241); unflipped (304,241) | 80 port ticks, 1600ms at 20ms/tick |
| 015 | 4/N unflipped | (298,241) | 80 port ticks, 1600ms at 20ms/tick |

000 has 12 wait-table uses and 015 has six. The actual coordinates vary by node; use the stored rows rather than applying Node A coordinates elsewhere. In particular E/015 uses y=214 while E/000 uses y=211. The waiting family is five original drawings covering eight headings through encoded flips; creating these two drawings does not complete every turning or walking family.

## Approved Cartoon identity references

These references provide character identity only. Original 000/015 pixels above remain the pose authority. The raw PNG hashes below were checked against the retained selected-source records.

| Identity reference | Exact selected raw source | SHA-256 | Acceptance/recipe record |
| --- | --- | --- | --- |
| Front 016 | `art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/016-toe-fit-v2.png` | `d89066217905e3e1a2fa509f1f9d6cfecbb084cb7fba50844a32a9d8c181c052` | `016-key-v1/candidate-recipe-v1.json` and `016-key-v1/approval-v1.json`; user accepted the shown front waiting turns, not production promotion or all headings. |
| Front-oblique 017 | `art/cartoon/walk-pilot/front-arrival-v1/017-foot-depth-v3.png` | `d1fab951de823fc5612860a5fac48bd586a533177a3e5e26d2605f41d4272c1d` | `front-arrival-v1/approval017-v1.json`; accepted 017 appearance and the shown native E-to-A arrival. |
| Rear-oblique 018 | `art/cartoon/arrival-pilot-v1/018-pose-v1.png` | `4ed63ba9245dd30ac414caadba1a13febac240ffcbfa767c4f939a4bd83ddab2` | `arrival-pilot-v1/runtime-recipe-v1.json` frame 18 and `production-acceptance.json`; existing production-approved arrival drawing. |

018 is useful for the established back, hair, cap and rear shorts. Its oblique head, torso and foot-depth arrangement must not replace 015's direct rear stance. 016/017 establish the front identity, scruffy beard and white shorts; 000 should retain the original side-view occlusion instead of exposing all of their visible front features.

These reference notes do not grant approval to new 000 or 015 artwork or to unseen native transitions.
