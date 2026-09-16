# Profile cycle: original pose guidance and approval boundary

This is authoring guidance for the remaining six drawings after the user accepted the lower tucked foot in003-v2 with "much better proceed". The exact scoped decision and its bound bytes are in `approval003-v2.json`. It authorizes expansion of the cycle; it does not independently approve001, the complete gait, transitions, native scenes or production promotion.001-v2 remains the selected checkpoint draft. All earlier generation and pending-review records remain historical.

The inspected Cartoon references are `001-profile-v2.png` (SHA256 `ad08c3484d41f200efac23f788d6744742d21efb0108950fa69c604e33b4cf80`) and accepted static `003-profile-v2.png` (SHA256 `1bb60fad5ec369fd5f5f097d98e3d5b57ee81d6766f2ecdb6b2f75f681719d9e`). They establish the selected drawing treatment and continuity targets. Each new pose still derives its leg silhouette, overlap and arm phase from its own decoded original.

## Original authority and limits

The source pack is `reference/`, whose `source-index.json` SHA256 is `7173a1cbe9412e65f79e574589b3d83e05af506d55082cf465f6d813bc99c460`. For frameNNN, inspect `NNN-original-native.png`, its exact eightfold `NNN-original-nearest8.png`, and `NNN-source.json`. The eight enlarged originals were visually inspected for these notes. No generated art, interpolation or altered source pixels enter this reference pack.

Every unflipped sprite faces screen-right. The engine supplies horizontal mirroring for the opposite travel direction. "Forward" below means screen-right in this unflipped pose; "rear" means screen-left. The dominant visible arm and overlapping leg silhouettes do not establish anatomical left/right identity. Diagnostic original colors are not the intended Cartoon palette, and gray ground-shadow pixels are not sole or contact landmarks. Contact descriptions are readings of the silhouette, not measured engine-ground events. These stills alone do not prove foot timing or pressure.

## Per-pose guidance

| Frame | Legs, feet and overlap from the original | Dominant visible arm phase |
|---|---|---|
| 001 | Wide stride. Forward heel is low and toes turn upward; the rear leg reaches diagonally back, with heel raised and toes pointing down. Preserve the separation and foot roll in selected001-v2. | Swings behind the shorts, hand on their screen-left side. |
| 002 | Forward shin is nearly upright and its long foot points right with a small toe rise. The other leg folds back: its heel is raised and the narrow foot points downward. That trailing foot clears the supporting sole visibly more than in006. Do not leave the rear foot flat or merge it with the ground shadow. | Still behind the shorts, with the hanging hand visibly screen-left. |
| 003 | Passing overlap: nearly upright support leg and long rightward sole, with a bent leg/foot tucked behind the calf and protruding screen-left above the support sole. The lowered tucked foot in003-v2 is the accepted static refinement. | Hangs low beside/over the shorts as the swing crosses its middle phase. |
| 004 | Stride begins opening after the passing overlap. A leg extends down-left to a long, low rightward-pointing foot; the other leg reaches forward with a bend and a shorter foot visibly above that lower sole. Preserve both the knee bend and the differing foot heights. | Hand forward over the screen-right side of the shorts. |
| 005 | Wide stride again, but not a copy or mirror of001. The forward shin descends to a much flatter rightward foot. The trailing foot is also flatter and more extended than001's strongly downward foot. Preserve the original overlap and toe/heel differences. | Forward swing, with the hand clearly ahead of the shorts on screen-right. |
| 006 | Broadly the same support/lift pattern as002, but the trailing downward foot reaches closer to the forward sole's height. The forward foot is long and nearly flat. Keep the small original knee/ankle differences rather than recycling002. | Forward, crossing the front of the shorts; opposite the behind-shorts arm phase in002. |
| 007 | Narrow passing overlap, within a32-pixel native canvas rather than003's40. The bent lower-leg/foot contour makes a larger curved protrusion screen-left, and the visible rightward sole is shorter than003's. Much of the second leg is obscured. Follow the original silhouette instead of assigning an unsupported anatomical side or copying003's tucked heel. | Descends close to the body and overlaps the shorts, approaching the middle of its return swing. |
| 008 | Stride opens again. The screen-left foot sits relatively high/flat while the reaching screen-right foot extends lower. This depth ordering differs from004, whose screen-right foot is above the other sole. Preserve the bend and ankle orientation through the008-to001 transition. | Behind the shorts, with the hand on screen-left; opposite004's forward hand. |

The pair distinctions are therefore visible and intentional:002/006 differ in arm phase and trailing-foot clearance;004/008 differ in arm phase and relative foot heights;003/007 differ in overlap, exposed foot shape and width. A four-frame cycle duplicated with mirroring would erase these source differences.

## Fixed placement and review sequence

Use the shared exporter with scale exactly1/10 for every generated drawing. The native canvas doubled supplies the runtime canvas. Each X target is twice the original first visible row's pixel-edge midpoint; Y0.25 is the established filter margin. These are outline registration observations, not anatomical anchors. Do not fit each full-body silhouette independently or align to the shadow bottom.

| Frame | Native canvas | Runtime canvas | Cap target HD |
|---|---|---|---|
| 001 |48x72 |96x144 |[72,0.25] |
| 002 |48x73 |96x146 |[70,0.25] |
| 003 |40x76 |80x152 |[54,0.25] |
| 004 |40x74 |80x148 |[66,0.25] |
| 005 |48x72 |96x144 |[74,0.25] |
| 006 |48x74 |96x148 |[70,0.25] |
| 007 |32x75 |64x150 |[48,0.25] |
| 008 |40x75 |80x150 |[62,0.25] |

Generate the remaining six poses with exact prompts, ordered reference paths and raw output hashes preserved. Export each at the fixed scale, run smoke before regression, and correct actual fit or silhouette problems without changing the route or inventing intermediate steps. Review the whole cycle with the real frame order, timing, coordinates, mirroring and standing connections specified in `route-plan.md`. The source family001-008 is the promotion unit because003 is also reused by ordinary turns. The current32 production assets remain unchanged until complete motion and required scene review are accepted.
