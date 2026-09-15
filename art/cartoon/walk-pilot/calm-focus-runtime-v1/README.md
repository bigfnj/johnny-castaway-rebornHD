# Calm focus runtime candidate v1

## Current production acceptance

On 2026-09-15 the user approved the actual Linux island comparison with
"looks good". [production-acceptance.json](production-acceptance.json) records
the exact six walking exports and inherited 15 island assets, the reviewed
HTML/native capture evidence, and the retained original-leg difference.
These six sprites are now selected in the production Cartoon pack. The pack
remains partial; this approval does not cover unseen animation states.

The production archive changed only the six walking PNG members. All 2,550
non-style members, including normal `RESOURCE.MAP` and `RESOURCE.001`, and all
15 island PNGs are unchanged. No diagnostic route script was promoted.

The exporter reports its own scope: it reproduces recorded bytes, does not
evaluate human acceptance, and does not modify the production archive.
Historical exporter hashes and guard results in `provenance.json` and
`export-verification.json` refer to the candidate checkpoint at commit
`efb63b2`. Only its docstring and result labels changed after approval;
registration, resampling, source checks and output PNG hashes did not.

## Historical candidate notes

The following notes preserve the pre-approval checkpoint. Its pending-review
record remains historical; the separate production acceptance above is current.

This is a technical candidate bundle. The two new toe-clearance edits and the
resulting in-scene motion await human review. [pending-review.json](pending-review.json)
records the exact current six sources with `accepted: false`. Nothing here
promotes the production archive.

The earlier [standalone walking motion](../original-pose-corrections-v1/standalone-motion-acceptance.json)
was accepted with its reviewed original-leg mismatch retained. That preview
used different raw PNGs for 028 and 029. Its approval does not silently approve
these later toe edits or their runtime exports.

## Sources and registration

[source-images.zip](source-images.zip) contains six exact returned PNGs, sorted
by name with fixed archive timestamps and metadata. Frames 024 through 027 are
byte-identical copies of the earlier standalone sources. Frames 028 and 029
are new single-reference toe-clearance edits. Their input ancestors remain in
the sibling source/history folder, linked by hashes in [provenance.json](provenance.json).
There are no extra copies of the six raw PNGs outside this ZIP.

[prompts.json](prompts.json) preserves the exact two calls, ordered references
and returned output hints. [recipe.json](recipe.json) records source hashes,
original frame IDs, runtime canvases and candidate output hashes.

| Frame | Runtime canvas | Fixed forward affine: scale, x translation, y translation |
|---|---|---|
| 024 | 64 x 150 | 0.1, -21.0, -3.95 |
| 025 | 80 x 148 | 0.1, -15.0, -3.95 |
| 026 | 80 x 146 | 0.1, -13.0, -3.95 |
| 027 | 64 x 144 | 0.1, -21.0, -3.95 |
| 028 | 64 x 144 | 0.1, -21.3, -3.75 |
| 029 | 64 x 150 | 0.1, -21.0, -3.95 |

Both axes use scale 0.1 with no skew. The cap observations and targets are
inherited unchanged from the [directional recipe](../directional-cycle-v1/recipe.json).
They are chosen registration observations, not newly measured engine anchors.
There is no per-image bounds fitting, family shrink, translation adjustment,
pixel painting or alpha cleanup.

## Reproduce the candidate PNGs

Use a Python environment with Pillow 12.3.0, from the repository root:

```text
python art/cartoon/walk-pilot/calm-focus-runtime-v1/export.py --output build/calm-focus-runtime-export
```

The output directory must be new. The exporter checks the source bundle,
member identities, fixed recipe contract, source canvases, registration and
alpha-8 source-center bounds. It resamples in premultiplied `RGBa`: an 8x
oversampled bicubic affine, followed by Lanczos downsampling, then `RGBA` PNG
encoding at compression level 9. It renders and verifies all six expected PNG
hashes before creating the output directory.

The files are written under `BMP/JOHNWALK.BMP/024.png` through `029.png`.
Expected hashes came from the independent root export recorded in
[export-report.json](review-evidence/export-report.json). Reproducing these
bytes establishes the candidate's technical identity, not human acceptance.

## Measured limits

All six candidates have zero alpha-8 source pixel centers outside their
existing runtime canvases. This does not mean zero filtered clipping. The
[independent comparison](review-evidence/independent-validation.json) found
small cap-edge differences between direct export and an export with extra
padding: white-background channel differences of 10 through 12 on five or six
cap pixels per frame, and blue-background differences at most 7. Frame 029
has two filtered fringe pixels just above the canvas at alpha 12 and 8.
These limits are retained for in-scene review without moving the cap anchors.

The maximum straight-RGBA difference of 255 in frame 028 occurs at alpha 1
and corresponds to a premultiplied difference of 1. It is not evidence of a
255-level visible change. The independent report includes an alpha-zero RGB
negative control and an opaque one-unit RGB positive control.

The toe-edit prompts requested unchanged upper bodies, but their returned
pixels were redrawn. Independent alpha-8 silhouette comparisons above raw
y900 stayed within two raw pixels per axis, which is 0.2 HD pixels at the
fixed scale. The same diagnostic bands contained 221,804 and 210,820 changed
visible RGBA pixels for 028 and 029. These are fixed image bands, not anatomical
masks, and they do not establish pixel identity.

## Workflow observations

The narrow single-reference toe-clearance requests brought the source
centers inside the existing canvases after the broader shorts/leg prompts
failed. This is a result for these candidates, not a guarantee of local-only
redraw or correct anatomy. The original-leg mismatch remains part of the
previously reviewed motion direction.

Keep the family scale and cap registration stable while fixing local toe
overhang. Check filtered edges separately from raw bounds, and use
premultiplied or composited comparisons when alpha is small. Candidate export
and human in-scene acceptance are separate checkpoints.

The [export verification](review-evidence/export-verification.json) records
smoke before reproduction regression, named invalid-input refusals, executed
guard-removal mutations and restored six-PNG reproduction. The retained
independent report also records three wrong-input controls. Neither report
claims native-engine playback or human approval of the new toe edits.

The separate [Linux scene evidence](review-evidence/linux-scene-validation.json)
records 42 actual displays for each of the current and candidate styles, their
PNG hashes and matching times, and the exact Linux executable/source hashes.
Seed 11 selected the approved ocean in this Linux build. The temporary
diagnostic script hosted the 23-position E-to-A route and endpoint hold.
All changed pixels stayed inside Johnny's placed canvas; the 15 island assets
were shared. Both normal archives retained all 2,452 golden decoder matches.
The served comparison passed 8 browser smoke and 52 regression checks.
These technical results do not approve the new toe edits or in-scene motion.
