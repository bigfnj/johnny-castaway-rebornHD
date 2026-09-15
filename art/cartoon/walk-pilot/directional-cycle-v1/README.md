# Approved directional walking pilot

On 2026-09-14 the user reviewed the full E-to-A walking comparison and replied
"looks good". This approves the six-pose motion and foot lifts as displayed.
The selected raw images are 024v7, 025v2, 026v3-fresh, 027v3-fresh,
028v4-transparent and 029v2. [acceptance.json](acceptance.json) identifies the
exact six source and export hashes. These PNGs now ship unchanged in the
21-asset Cartoon preview; the later
[island scene acceptance](../../island-pilot-v1/acceptance.json) records the
user's approval of the complete layered scene.

The user's "well done" approved the 024v6 key's body direction and leg order in
the context of the still review. The earlier "The body pop looks resolved"
approved alignment of the preceding cycle. Those earlier statements had narrower
scope; the later "looks good" supplies full motion approval for this pilot.
The earlier profile cycle's reversed leg order and
fixed-profile direction remain recorded in provenance.

`source-images.zip` contains 11 unchanged generated PNGs: six selected poses and
five generated ancestors actually used as references. The contaminated 028v3 is
an ancestor of the built-in transparent-background revision; it is not a runtime
candidate. No original-resource PNG, external cap image, duplicate 024v6 reference,
runtime export or game archive is stored in this bundle. The source bundle is
14,738,087 bytes. Revisit source storage before scaling this process to a full pack.

`provenance.json` records exact prompt files, actual ordered reference lists,
source hashes and the existing tracked 024v6 reference bundle. All six original
pose enlargements were verified to repeat the source RGBA pixels exactly using
nearest-neighbor sampling. They can be recreated from the unchanged original
archive. The generator exposed no deterministic seed or model identifier; the
saved source PNG bytes identify these drawings.

The hashed recipe, provenance and review evidence preserve their original
pending-review status as historical checkpoints. The separate acceptance record
is the current human decision; it does not rewrite those earlier bytes.

`recipe.json` records the selected sources, original engine canvases, explicit cap
landmarks and exported PNG hashes. One uniform drawing scale of 1/10 applies to
every frame. Five frames retain cap (385,42); 028 uses its inspected cap (388,40).
Translation places those landmarks at their original canvas positions. There is
no canvas normalization, bounding-box fitting, body fitting, warping or separate
limb adjustment. The raw true-alpha source pixels are preserved. Technical
resampling uses premultiplied alpha internally and returns straight RGBA PNGs.

Run `export.py --output <new-directory>` with the recorded Pillow version to
reproduce the six approved PNGs. Its printed status retains the historical
pending-review fields; consult `acceptance.json` for the current decision.
For example, from this repository on the configured
Windows toolbox:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/directional-cycle-v1/export.py --output build/art-work/directional-reproduction
```

The helper verifies every input and all six expected PNG hashes before creating
the output directory. It does not package or update the production archive.
`review-evidence` preserves the static contact report, technical clearance
manifest and export report. Absolute paths inside those historical records name
the original work session; the portable source and export recipe is in this folder.

The higher rear-foot lifts in 026/027/029 were visible in the approved preview
and are accepted for this route. They are no longer an open gait-review item.
The 028 alpha extraction altered its contour by approximately 1-2 raw pixels;
alpha 1-7 exterior residue remains in several raw sources. Meaningful alpha bounds
fit their original canvases at the recorded transform. No alpha thresholding or
code cleanup has been applied. This walking family covers only 024-029. The
shipped preview also contains 15 island assets; uncovered application artwork
continues to use the existing fallback.

The later island review replayed these unchanged PNGs at the original route
coordinates with independently advancing shoreline animation. The user approved
the displayed scene. Native palm-occlusion and fallback checks, together with
[production validation](../../island-pilot-v1/review-evidence/production-validation.json),
record the integration evidence. This approval does not cover other walking
directions or unseen environment states. Review their contacts and occlusion in
the actual renderer as each new family is authored.
