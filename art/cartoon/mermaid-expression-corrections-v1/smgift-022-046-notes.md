# SMGIFT.BMP 022–046 expression revisions

These are appearance-review candidates from the built-in imagegen tool, not approvals or production integration. The exact request for each edited frame is saved as `generation/SMGIFT.BMP/NNN-v1-request.json`. Each request uses the prior selected cartoon as the edit target and that frame's exact nearest-neighbor original as the pose reference. Raw generated PNG bytes and alpha are preserved.

18 requested edits returned images, with no failed calls or quality retries. Preferred version is v1 for every edited frame.

| Frame | Current candidate and visual check |
| --- | --- |
| 022 | Laughing face. The smaller hand now has a distinct diagonal forearm behind the near extended arm. Its elbow and shoulder connection remain partly occluded by the near arm and torso, rather than a second hand appearing at the near wrist. |
| 023 | Laughing face with two hands clasped in front of the chest, two visible wrists and bent forearms. |
| 024 | Downward-tilted smiling face with two clasped hands and separate forearms. |
| 026 | Chin and gaze tilted upward with an excited smile. Both lei grips and falling water retained. |
| 027 | Happy face and two visible hands displaying the lei. The raised hand keeps the upper grip while the near arm bends forward to support the lower side. |
| 028 | Open smile and relaxed brows; two empty upturned palms retain their unequal heights. |
| 029 | Head tilted back, smiling upward, with both eyes visible. Existing hand-to-forearm gesture retained. |
| 030 | Giggly smile with relaxed brow; hand beside mouth and lower forearm retained. |
| 031 | Happy open smile replaces worried expression. Chest-level hand and opposite hand at water retained. |
| 032 | Happy frontal smile; shoulder-level hands retain distinct heights. |
| 033 | Happy open smile; unequal open-palmed shrug retained. |
| 034 | Happy open smile; higher two-hand shrug and torso lean retained. |
| 035 | Near arm moved from behind the hair to the front. Its connected hand is below the swimsuit top at the water, with relaxed fingers pointing down. The other raised hand, lean and existing waterline remain. No additional submerged anatomy exposed. |
| 036 | Happy face; forward lean, swept hair and two-arm gesture retained. |
| 037 | Smiling upward at the upright oval prop; both extended arms and prop contacts retained. |
| 038 | Happy upward smile; overhead oval prop and two-hand support retained. |
| 042 | Happy face looking toward the extended dripping hand; opposite hand remains at hairband. |
| 044 | Broader happy smile; raised palm, lower hand at water and established clothing retained. |

## Retained without generation

025 shows only the submerged crown and hairband. 039 and 040 hide the face behind the oval prop or water. 041 and 043 are standalone oval props, 045 is the signal, and 046 is the green effect patch. These seven frames remain the prior batch's selected images, without invented facial features.

## Verification

All 18 output records are present; all 72 saved request, reference and output SHA-256 pins matched. All outputs are RGBA with alpha spanning 0–255, and all alpha-at-least-8 content bounds remain inside the canvas. The maximum edge alpha is 5, so faint generated edge residue is preserved rather than modified. Outputs were visually inspected for the requested expression and arm changes. No native animation or production integration was performed, and user appearance review remains pending.

