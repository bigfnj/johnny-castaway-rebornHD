# Rear arrival: reusable image lessons

The user approved JOHNWALK 018 in the native island review with "nailed it,
proceed". This adds one standing frame after the approved rear walk. Read the
[rear walking lessons](art-style-learnings-rear-walk.md) alongside this record.
Exact prompts, references and approval are in the
[arrival bundle](../art/cartoon/arrival-pilot-v1/README.md).

## Separate pose geometry from character identity

The supplied-original 018 defines the pose. Approved Cartoon 023 supplies the
cap, beard, proportions and shorts design. The original 018 and 023 happen to
share their first 23 RGBA rows exactly; that supports a head-design reference,
not interchangeability of their arms or stance. Preserve the original visible
elbow bending outward and the hand returning toward the shorts/pocket. Do not
invent an anatomical side for the obscured hand.

The two resting feet are at different depths. Do not flatten them onto one
horizontal line. Original diagnostic imagery includes an opaque gray shadow,
so its bounding-box bottom is not a sole-contact landmark. Pixel-region
comparisons found greater vertical foot separation in the generated drawing;
we disclosed that observation and reviewed contact on the actual island.
The user accepted the displayed result. Keep both observation and disposition;
approval does not turn a pixel-region estimate into anatomical parity.

## Keep the actual arrival transition

The route changes Johnny's native draw origin from (302,244) on walking 022 to
(298,240) on standing 018. The review preserves this shift, its 1,600 ms hold,
background updates and completion witness. A fixed close-up camera makes the
shift visible. No per-frame camera recentering, independent foot offset or
synthetic turn duration should hide a transition issue.

Original 018 serves northwest heading 3 and mirrored northeast heading 5 at
all six island spots. The story also uses it in SJLEAVES. One reviewed arrival
does not approve every mirrored placement, turn or story interaction. Track
those uses before broadening the review scope.

## Pin the export and preserve the human decision

The 1024-by-1536 returned drawing is retained untouched. Export uses the same
uniform 0.1 scale and cap-registration rule as the rear family, with a
64-by-154 runtime canvas. Premultiplied-alpha resampling prevents hidden RGB
outside transparency from contaminating edges. Raw-image viewers can display
those hidden colors misleadingly; inspect alpha and actual composition before
calling them an opaque black background.

The reviewed export used Pillow 12.2.0. The prior rear export used 12.3.0.
Choose the interpreter from the recipe, verify its version and reproduce the
accepted PNG hash. An interpreter alias or updated toolbox is not a version
pin. Do not change the recipe to whatever happens to be installed.

Generation provenance and pending review requests remain immutable snapshots.
The later acceptance records the exact question and response and inherits
the earlier 27 approvals explicitly. Candidate recipe bytes remain separate
from production metadata additions. Preserve text bytes before hash linking,
including on Windows checkout; the new arrival subtree has an explicit Git
attribute for this purpose.

## Recheck contact at shoreline placements

During the later skin-color review, the user identified the smaller screen-right
foot of018 hovering over water at the initial Front turn placement. This is a
different location from the approved rear arrival: actual native draw `(478,216)`,
unmirrored, rather than `(298,240)`. The color correction retained every alpha
byte and pixel position, so it did not introduce this geometry difference.
The user approved the new colors separately; production promotion is held while
the newly raised contact issue is resolved.

At 2x scale, visible-pixel measurements excluding the original gray shadow put
the original feet's bottom rows at147 and143. Cartoon alpha>=8 gives141 and131.
These are qualified pixel-region observations, not anatomical annotations. The
smaller foot is higher, and its separation from the nearer foot is greater.
Retain the previous approval alongside this later context-specific finding.

For the comparison, use the exact native origin, a fixed camera, and the actual
scene palette. The stored original018 reference uses diagnostic colors and is
useful for geometry, not a faithful game screenshot. Show original artwork on
the original island and on the Cartoon island to separate pose contact from
shoreline shape. Label port-rendered original artwork accurately; it is not a
capture of the original executable. A pose approval at one arrival does not
establish ground contact at every island position or mirrored use.

The new diagnostic captures use the supplied-original RESOURCE pair in private
packages. They confirm that original018 meets the sand on the unchanged Cartoon
island; no pixel outside018's placed canvas differs from the current Cartoon
capture. Each diagnostic passed a native smoke capture, full route and fresh
repeat with identical draw origins and timing. The fallback renderer still uses
diagnostic colors, so these panels establish geometry, not original-executable
color or compositing parity. Preserve that limitation rather than inventing a
palette to make the source look familiar.

The user's next observation located the mismatch higher in the body: original
shorts sit lower. Measuring the waistband and hem showed that simply lengthening
both shins would preserve the wrong proportions. Cartoon waistband/hem were
about67–70/94–95HD versus original80–83/104–106. Extend the lower torso and lower
the shorts first, then reconnect hands and legs to the intended contacts while
keeping cap/head/shoulders registered. The near exposed leg can become shorter
proportionally even as its foot reaches farther down the canvas.

The [proportion study](../art/cartoon/standing018-proportions-v1/README.md)
retains two generated drafts and their exact prompts. Both undershot the numeric
instructions, despite moving in the requested direction. Measure each result
and check native placement before assigning success. V2 reaches the shoreline
edge in the native smoke; the user accepted its still proportions with "much
better proceed". The subsequent motion review remains separate. Newly generated
geometry also needs newly reviewed color masks
and material samples; an older018 mask cannot be transferred blindly.

Use a same-origin walking-to-standing transition to expose a proportion change.
The revised018 keeps its cap registered, but its lower waist/hem differ visibly
from walking023. A technically exact renderer comparison cannot decide whether
that reads naturally at Normal speed. Mirroring can also expose a contact issue
at a different shoreline position even after the unmirrored still is approved.
Keep both views in the motion review and compare the original at the same draw
origin before attributing a remaining gap to the new anatomy or the engine.

The exact mirrored018 comparison now confirms a5HD-pixel smaller-foot height
difference: original skin ends at runtime143/global561 versus revised138/global556.
The original gray shadow is separate artwork. All74 displays retain identical
timing and placement, and every pixel outside018's canvas matches. Keep this
contact correction separate from the pending waist-transition judgment.
Evidence is retained under the proportion study's
`native-review/original-mirror-v1/evidence-v1/`.

The user accepted the shorts while rejecting the mirrored foot contact. Keep
those decisions separate. The foot-only edits repeatedly undershot numeric
instructions: the first50-raw-pixel request moved the smaller sole only19raw
pixels. A relative instruction bringing both soles almost onto the same ground
line produced successive improvements. Preserve each draft, measure at the fixed
runtime scale, and check the actual shoreline before another human review.
For a sprite without the original contact shadow, reaching the original skin's
last row may still leave a visible gap; inspect clean sand under the foot too.

Even this localized foot edit shifted the uncorrected near-calf base from
252,154,94 to252,162,103. Its fresh color pass returns that sample to the chosen
252,148,88 and preserves the new sprite's alpha exactly. A request to keep the
rest unchanged is not evidence of RGB or silhouette identity. Check the selected
result against the approved source and retain qualified differences; v5's
upper-body and shorts bounds stay fixed but their edge pixels are not identical.
