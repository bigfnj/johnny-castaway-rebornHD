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
