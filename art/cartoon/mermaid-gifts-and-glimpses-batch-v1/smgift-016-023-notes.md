# SMGIFT 016–023 authoring notes

Eight distinct frame candidates returned from eight built-in image generation calls, plus one targeted 020 retry. There were no tool blocks. Exact requests, untouched PNGs and provenance records are saved under `generation/SMGIFT.BMP/`. No selector, gallery or production asset was changed by this subtask.

The exact nearest8 original for every frame was inspected before generation. The established `SBREAKUP.BMP/000-generated-v1.png` supplied identity and rendering style only. Source stippling was interpreted as skin, and submerged anatomy remained hidden. Every returned drawing was inspected against its source.

| Frame | Review preference | Visual observations |
| --- | --- | --- |
| 016 | v1 | Low, bowed head; both shoulders visible; central hand close to chin; hair spreads on both sides of the water. Compact pose and hidden lower body retained. |
| 017 | v1 | Head angles down and right; shoulders sit low; hands stay submerged; broad hair fan lies at the waterline. |
| 018 | v1 | Upright right-facing profile; long hair trails left; near shoulder visible while arms remain submerged. |
| 019 | v1 | Raised chin and two distinct arm phases: near forearm low across the front, far hand extending forward higher. |
| 020 | v1, with visible-pose exception | v1 is the complete silhouette, but hides the low near hand behind the ripple instead of letting it hang over the front waterline. v2 fixes the hand direction but crops the fingertips at the bottom edge, so v2 is not recommended as the selected display asset. |
| 021 | v1 | Right-facing profile with near upper arm descending into water and the far forearm held upright in front. |
| 022 | v1 | Near arm bends low across the front then reaches right; far hand is closer to the chest. Exactly two arms and two hands are visible. |
| 023 | v1 | Near bent arm reaches forward; the far arm stays largely hidden; head, hair and waterline retain the source's orientation. |

All v1 outputs are RGBA with alpha spanning 0–255 and padded visible silhouettes. 017 and 020 v1 each have maximum edge alpha 1 from faint generated edge pixels; their alpha>=8 silhouettes remain inside the canvas. The other six v1 outputs have fully transparent outer edges.

020 v2 is an unsuccessful targeted correction because the generated fingertips touch and cross the bottom canvas boundary. Its 1727×911 canvas has alpha>=8 bounds ending at y=911 and maximum edge alpha 254. Preserve it as an unselected correction reference, not a complete replacement. Its output SHA256 is `d96f2df86bf1a5cef2458a9d08fb123cce5b90d692b2b15abe9cf48dfa5609b8`.

These are appearance-review candidates, not user-approved drawings. Native placement and motion validation remain deferred under the art-first workflow.
