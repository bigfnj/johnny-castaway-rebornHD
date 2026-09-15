# Remaining standing views000 and015

These two new drawings complete the five unique assets used for eight standing
directions, alongside approved016/017 and production018. Human review of000/015
and the complete direction ring is pending. No new production assets are added.

| New pose | Original direction and treatment | Fixed runtime export |
| --- | --- | --- |
| 000 | Strict right profile, reflected for left. Near hand at the pocket; far arm and much of the far leg are occluded. |80x152, scale0.1, cap[54,0.25] |
| 015 | Direct rear view, no face or front cap emblem visible. Both hands at waist, separated planted feet seen from behind. |80x146, scale0.1, cap[35,0.25] |

`provenance-v1.json` binds both exact built-in imagegen calls, their ordered
references and raw output bytes. Original pixels define pose and occlusion;
the accepted016/017/018 references define appearance. The source originals use
a diagnostic palette; their gray shadow is not a sole anchor. Original binaries
were not reread during this reference-preparation step.

Both initial drawings fit without corrective scaling or placement changes.
The shared exporter requires an explicit frame and rejects mismatched recipes
or references. Each frame passed smoke3, regression23 and19 executed mutations.
Frozen historical exporters are untouched; the filtering matches the017
implementation for fixtures with opaque, soft-alpha and transparent pixels.

`exports/000/recipe.json` and `exports/015/recipe.json` are the preserved exact
recipes; matching reports and runtime hashes are beside them. Reproduce directly
from those paths using the explicit corresponding `--frame` described in
`EXPORT.md`. Choose a fresh output directory. The saved smoke/regression records
are under `review-evidence/export-v1/000` and `015`.

The next checkpoint runs actual same-spot adjacent-heading calls around all
eight directions at A in both orders. Existing016/017/018 PNGs must remain
identical. Original draw origins, reflections and native timing are retained;
pose stepping supports inspection without inserting artificial holds.

## Lessons for later style packs

- Pose authority and appearance references have different jobs. The direct rear
  image must not inherit a visible nose from its approved oblique reference.
- Occluded limbs matter as much as visible ones. The side pose should not gain
  an extra far-side fist or a second fully exposed front-facing leg.
- A common scale does not mean a common canvas or cap target. The original
  per-frame dimensions and offset features remain explicit recipe data.
- Use one new exporter with explicit frame settings for the new group. Keep
  historical recipes reproducible without changing their tools or approvals.
