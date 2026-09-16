# Cartoon skin-tone consistency

The user reported a skin-shade jump in the connecting-pose preview and separately
accepted the poses: "while you work on that, the actual poses are accurate and well done."
The exact palette selection and code-edit authorization are preserved in
`human-palette-reference-v1.json`.

The second screenshot is mirrored JOHNWALK029 in the Front waypoint clip.
The first is mirrored024 later in that same stride. The color difference is
already present in their committed source artwork. Frame029 is the canonical
skin-tone reference for this correction, not a newly generated pose.

The [published color review](http://127.0.0.1:8932/cartoon-skin-tone-v1/review.html)
received the user's approval: "Yes, keep these colors".
`human-color-review-request-v1.json` binds the exact question, selected outputs
and reviewed page; `human-color-approval-v1.json` records the later answer.
The user then requested an original-art comparison for standing018 because its
smaller foot appears over the water in Front turn. Production promotion is held
for that contact review. The skin-color approval remains intact.

The [standing018 comparison](http://127.0.0.1:8932/cartoon-contact018-v1/review.html)
shows supplied-original pose geometry on both islands beside the current
Cartoon. At the identical native draw position, the original smaller foot meets
the Cartoon sand and Cartoon018's foot is raised above it. Surrounding scene
pixels match outside018's canvas. Original panels use the port's diagnostic
palette, so they establish placement rather than original color appearance.
Native smoke, full and fresh-repeat captures passed. No pose correction or
production promotion has been made.

Scope: color-only post-export correction of the 28 current/draft Johnny walk and
standing sprites. Preserve every alpha byte, canvas dimension and pixel position.
Protect hat, hair, beard, shorts, eyes and ink. Keep the 15 island assets unchanged.
Keep all old raw art, recipes and scoped approvals as ancestors; the corrected
colors require a new motion review before production promotion.

Plan: freeze exact runtime inputs and their ancestry; establish reference skin
swatches and reviewed masks; produce deterministic corrections; run smoke then
regression including changed and unchanged controls; review all character poses
and native transitions; integrate only after human color review. New acceptance
must describe revised colors without claiming new original-engine scene parity.

## Reproduction

`input-index.json` pins all 28 untouched runtime inputs. `ancestry.json` traces
each to the original generated source and historical export, including ZIP
members for older sources. The screenshot-match evidence identifies the actual
reference pose and records the indistinguishable029 display timestamps.

Run `python correct.py --output <new-output-directory> --frames 24 29` for the
focused changed/unchanged smoke, then omit `--frames` for all 28. The tool writes
sprites, grayscale skin-confidence masks and a hash-bound recipe to the chosen
output directory. It does not modify the application archive. The output remains
a review draft until a new human color decision is recorded.

`calibration-v1.json` fixes visually inspected 3x3 lower-leg skin patches. Their
near-opaque median gives canonical 029 RGB 252,148,88. Each frame gets fixed RGB
channel gains through a conservative, softly weighted skin mask. Relative
shading remains; canvas, position and alpha are exact. Frame 029 retains its complete
original PNG bytes. Calibration does not refit a whole-body histogram.

An initial separate-head calibration experiment was rejected: some automatic
head proposals landed on shoulders, while actual nose samples were close to
each frame's body base. One transform per frame avoids an unnecessary artificial
neck boundary. The chromatic mask is a practical classifier, not a claim of
perfect semantic segmentation. Independent material landmarks and visual mask
review are needed alongside exact outside-mask and alpha comparisons.

## Correction checkpoint v2

`exports-v2/` retains the 28 corrected PNGs, masks and exact recipe. The first
mask draft admitted several cap-edge pixels and was rejected before human
review. Its corrector and findings remain in `review-evidence/mask-v1/`.
The final mask explicitly excludes the complete cap using original-only traced
pixel-edge boundaries in `protected-cap-polygons-v1.json`.

The independent material annotations preserve their own revision history.
Three original v1 chest-hair sample coordinates were found to be mixed or
shaded skin during enlarged original-pixel review. V2 moves those samples onto
the actual visible strands; v1 remains unchanged. This is documented annotation
correction, not a relaxed color tolerance. See `PROTECTED-LANDMARKS.md`.

Focused 024/029 smoke passed, then all 28 sprite regressions passed against 222
independent material points and 84 interior regions. All alpha/canvas values,
full cap regions and outside-mask colors remain exact. The flat calibration
patch in each sprite is now RGB 252,148,88. The other 27 sprites change, while 029
retains its original file bytes. A fresh exporter run reproduces every PNG,
mask and recipe exactly.

Fourteen executed negative controls cover alpha, protected materials,
outside-mask pixels, wrong skin base, changing the reference, disabling the
cap exclusion and disabling color gains. Each fails its intended named
condition; restored positives pass. The two changed-source runs bind the actual
executed script hash and 28-frame execution witness. Evidence and exact commands
are in `review-evidence/export-v2/manifest.json`.

These checks protect the color-only edit contract. They do not replace human
judgment of color consistency in native motion, and they do not establish
original-executable timing parity or review every story use of these sprites.

## Native motion checkpoint

The separate [native review](native-review/README.md) uses the same 28 poses on
both sides, including the accepted connecting drafts. Six walking/turning clips
plus two actual same-heading waiting calls exercise all 28. Every clip passed
smoke before full capture and a fresh repeat. Across 298 displays, 286 differ
only inside the placed skin masks and 12 reference-029 displays are identical.
Timing, origins, full-canvas flips and surrounding scene pixels remain exact.

The Linux capture image lacked Pillow. The failed first candidate launch is
retained; the successor passes already decoded, hash-bound mask bytes from host
preparation to a standard-library reader. It uses the same PNGs and archive.
No artwork change or additional dependency installation was needed.

The new browser comparison begins on Front waypoint at Normal speed. It labels
the panels Earlier colors and Matched colors and links a still comparison of
all 28 poses. It loads one clip at a time, with verified release of previous
image references. No memory-saving number is claimed. Human color approval
is recorded separately above; the application archive and production ledger
remain unchanged pending the newly requested standing018 contact comparison.
