# Image authoring lessons for future style packs

This is the reusable record from the Cartoon pilot. Keep it with the exact art
sources and acceptance ledgers below. Update it when new evidence changes the
workflow. A prompt is not a reproducible image; the saved source PNG and its
documented export identify the actual artwork. Open engineering work belongs
in `BACKLOG.md`.

## Evidence and source records

| Record | Knowledge preserved |
|---|---|
| [Runtime and packaging](cartoon-art.md) | PNG support, coverage, fallback, inventory and candidate building |
| [Character guide](../art/cartoon/character.md) | Approved identity, beard and brimmed-cap corrections |
| [Character design history](../art/cartoon/character-history-v1/README.md) | All five exact prompts, four used ancestor sheets, original poses and the user's cap reference |
| [Motion review](../art/cartoon/motion-review.md) | Body-pop diagnosis, direction, leg order and review chronology |
| [Rejected profile cycle](../art/cartoon/walk-pilot/README.md) | Failed approach, used source ancestry and reproducible exports |
| [Directional cycle](../art/cartoon/walk-pilot/directional-cycle-v1/README.md) | Exact prompts, ordered references, transform recipe and validation |
| [Motion acceptance](../art/cartoon/walk-pilot/directional-cycle-v1/acceptance.json) | Six exact exported PNGs approved in the full 23-position preview |
| [Island concept](../art/cartoon/island-concept-v1/README.md) | Environment direction and actual generation prompt |
| [Island implementation plan](../art/cartoon/island-concept-v1/implementation-plan.md) | Layer geometry, controlled state and integration checks |
| [Layered island pilot](../art/cartoon/island-pilot-v1/README.md) | All 15 island assets, source bundles, technical verification and scene review status |
| [Scene acceptance](../art/cartoon/island-pilot-v1/acceptance.json) | The exact 21 assets and preserved motion preview approved with "approved, it looks great" |
| [Static island sources](../art/cartoon/island-pilot-v1/palm-sand-cloud/README.md) | Palm, sand and cloud prompts, selected ancestry, failed edits and verified exports |
| [Front walk refresh lessons](art-style-learnings-front-refresh.md) | Hip and shorts connection, far-arm occlusion, original shadows versus foot contact, and preserved approval history |
| [Front walk refresh bundle](../art/cartoon/walk-pilot/front-refresh-v1/README.md) | Exact 028/029 drafts and prompts, retained 024-027, frozen comparison inputs and separate approvals of standalone motion and the native island scene |

## Engine constraints that every style inherits

The current inventory has 2,401 style slots: 2,391 BMP frames and ten SCR
backgrounds. There are 2,131 distinct sprite PNG byte sequences and 119 blank
placeholders. Including the ten screens gives 2,141 distinct PNG byte sequences.
Re-run inventory against the archive in use. Identical bytes and blanks do not
make their runtime slots disposable.

The current render scale is 2 while logical animation coordinates remain 640x480.
Keep each replacement's exact corresponding PNG canvas. Padding, flips, draw
order, original trajectory and timing are part of the animation. Use original
frames for geometry and the selected style guide for appearance. Enlarged
nearest-neighbor references help read tiny poses; record the exact scale and
padding so source positions remain recoverable.

Sprites need explicit straight alpha and supported 8-bit noninterlaced PNGs;
screen backgrounds must be opaque. The documented portable path supports RGB,
RGBA and grayscale-alpha. Do not use the legacy magenta key for a new style.
Opaque magenta is valid in a true-alpha replacement.

The runtime catalog and builder currently register HD and Cartoon. In particular,
`tools/art_pack.py` validates `runtime.id == "cartoon"`. Adding a Noir directory
alone does not create a working selection. Extend catalog, authoring validation,
settings, CLI/UI choices and their tests when adding a style. This authoring
workflow is reusable; style registration still requires deliberate code work.

## Identity, pose and approval are different things

The useful Cartoon identity cues were a lean body, expressive face, ragged white
shorts, a full scruffy beard and a white sailor cap with a projecting dark brim,
narrow gold band and anchor. Stubble did not replace the beard; a bowl-like cap
did not replace the brimmed sailor design. The user's reference and original
hat-playing animation clarified the intended object.

Keep a canonical appearance sheet fixed across frame calls. A selected adjacent
frame can reinforce continuity, but should not silently become the only identity
reference. A new style needs its own appearance review while retaining Johnny's
identity cues; Cartoon approval does not approve another style's character.

Tell reviewers exactly what they are judging: appearance, a directional key,
complete motion or a composed scene. Record the response, shown artifact and
selected hashes. The full-walk response "looks good" accepted the six displayed
poses and their higher foot lifts, superseding earlier limited key/registration
approvals for that preview. Do not leave a human-approved gait marked rejected.
Unseen directions or interactions remain separate review work.

## What the walking loop taught us

| Observed failure | Cause or useful correction |
|---|---|
| Whole-body popping | Mixed sole and cap registration introduced vertical offsets; frame 024's cap was 8.26 HD pixels below 025. Use a stable upper-body landmark. |
| Sideways recoil | Frame 026 used a foot-based horizontal anchor instead of the cap, shifting its crest 8.89 HD pixels. Keep a consistent landmark definition. |
| Better foot, wrong leg | Follow each leg from its shorts opening through the crossing; a toe's final position alone does not establish near/far order. |
| Fixed left profile on a diagonal route | Original shoulders, hips, arms and limb occlusion supply the three-quarter cue. Foot edits cannot correct torso direction. |
| Unnecessary head yaw | The original six frames' upper 38 HD rows were identical after horizontal offsets. The missing direction cue was chiefly below the head. |
| Repeated foot edits made little progress | Fresh original-pose-first generation sometimes helped more, but still needed a full motion review. Do not hide anatomy errors with code warps. |

The reviewed E-to-A route has 23 original positions at 120 ms per pose, travels
(-94,+30) logical pixels, and has no camera or flip change. Its endpoint is not
a perfectly repeating six-frame loop. Preserve the native sequence. The review's
extra one-second endpoint hold is explicitly diagnostic, not new interpolation.

Use one deliberate drawing scale for a coherent character family and explicit
per-frame landmarks. The accepted family uses 0.1 and cap registration; that
constant belongs to those sources, not every future image. Never infer body size
from output canvas dimensions alone or fit every pose's silhouette independently.
Pose-dependent fitting creates changing head/body size. Original sole readings
were approximate, about two HD pixels uncertain, not engine anchors.

Technical export may use documented uniform resampling, translation and removal
of unused padding. Artistic pose/contour changes belong in image generation.
Do not stretch limbs, crop meaningful art, move the native route or add invented
frames to conceal a mismatch.

Static scenery has a different continuity constraint from an animated body.
A small, explicitly chosen uniform asset-scale change can be reasonable if it
preserves semantic ground/joint anchors and the full scene is reviewed. It is
not permission to normalize every animation frame. Exact runtime canvas sizes
remain mandatory, but an original decorative silhouette need not be traced
pixel for pixel. Avoid endless generation over tiny fringe differences when a
documented static composition choice can be evaluated directly.

## Prompting and iteration

Use built-in image generation for artistic work. Give every input a role and
record its actual order. Original pose/geometry first and style guide second is
a useful starting tactic, not a universal guarantee. Request one independent
runtime asset or targeted revision per call. Generated contact sheets are
concepts, not reliable frame-count/order/registration contracts.

Make a targeted revision for a specific failure, repeating the invariants, then
inspect the whole result. Correcting 024's foot did not repair its body direction.
Fixing 028's toe boundary introduced real alpha contamination; a later background
extraction cleared it but shifted a cap feature roughly 1-2 raw pixels. Re-check
landmarks after every generation. Do not claim untouched regions are byte-identical.

If repeated edits preserve the wrong shape, change the reference hierarchy or
try a fresh pose-driven image before increasing volume. Stronger pose guides or
a character rig are possible future options if large frame families remain
unreliable; neither is implemented by the present image pipeline.

The first island layers used padded original canvases with known enlargement
and fixed export transforms. Results sometimes retained canvas dimensions but
moved or enlarged the silhouette. Dimension checks alone cannot establish correct
placement. Preserve failed attempts' measurements and reasons even when their
unused binary images are not kept in the durable bundle.

Sparse padded references can invite the generator to enlarge a tiny subject.
For the side waves, a larger nearest-neighbor geometry reference made the curve
easier to follow, but did not guarantee its size. Measure the returned silhouette
in the recorded coordinate system. Choose a single documented transform for an
entire phase family, inspect every phase and their composed shoreline, and reject
a family if the resulting placement fails. Do not fit each phase independently.

## Transparency and composition

Inspect alpha values and composite against contrasting backgrounds. Colored RGB
under alpha 0 can look like a glow or dark matte in a raw image preview while
remaining invisible in actual composition. Do not erase it based on that preview.
By contrast, alpha 78/92 in supposedly empty corners is real contamination.

Generated interiors may peak at 254, with alpha 1-7 residue outside the visible
shape. Report ranges and bounds at stated thresholds. An alpha>=8 silhouette
does not prove all exterior pixels are zero. Inspect native-size edges and
fixed canvas boundaries; do not silently harden alpha, color-key it or paint
it away. A requested opacity is also not a measurement of returned opacity.

Use premultiplied colors internally when resampling transparent art, then export
straight-alpha PNGs. This keeps hidden RGB from bleeding into edges. Record the
library version, exact transform and hashes when byte reproduction matters.

True alpha exposed rendering behavior hidden by the binary-alpha originals:

* Waves accumulated color on the persistent background (128,192,224...) until
  a clean region was restored and current families redrawn in update order.
  Test frame disappearance, phase overlap and untouched HD behavior.
* The real D/E palm route redrew the tree over a background already containing
  it. An alpha 128 red trunk became 192 above Johnny; opaque 255 remained 255.
  Keep a character-overlap color oracle so disabling tree drawing cannot pass
  as a fix. The correction uses premultiplied source-atop on Johnny's layer,
  preserving his coverage and adding the tree color. The focused real-route
  tests and both Windows gates passed, including five rebuilt mutants and HD
  parity. See [the implementation](../src/engine/graphics.c) and
  [palm tests](../tests/test_palm_renderer.py); preserve that evidence with the
  scene record. Merely lowering Johnny's alpha is not equivalent at translucent
  overlaps because it also changes the already-painted tree contribution.

The black ocean in a standalone sandcastle diagnostic came from missing composed
background setup, not a black full-scene ocean asset. Unusual source palette
colors likewise require direct asset/palette comparison before assigning blame
to new art or the renderer.

## Independent scene layers and state coverage

A flattened concept is the style/composition guide, not a production atlas.
Hidden areas cannot all be recovered by cropping. Generate clean independent
ocean, sand, palm, shadow, cloud and foam layers. Moving clouds and shore foam
must not be baked into the ocean; tree and cast shadow must not be baked into
sand. Tree sprites are reused for foreground occlusion.

The first scene has horizon near HD y300 and a shallow sand footprint beginning
at y558. Making the island a taller mound moves its visible ground away from
fixed walking coordinates. Preserve ground contact and trunk/canopy overlap;
use the exact sizes/origins in the island plan, not guessed concept measurements.

High-tide frames 003-011 form three independently advancing wave families with
overlapping rectangles, not one synchronized three-frame shoreline. Author and
review complete active groups. Other tides, oceans, clouds, offsets, rafts,
holidays and night need explicit coverage or reviewed fallback. Shared sand/palm
replacements can appear in those unstyled states. Night does not automatically
recolor sprites, and palette-drawn TTM effects keep original colors.

Windows seed 9/day/no-holiday is a verified baseline, not a cross-platform promise.
C random sequences vary by platform. Confirm actual selected state in logs and
captures. A normal ADS scene and an API test driver establish different coverage;
the E-to-A diagnostic does not execute real D/E palm masking.

## Review, testing and durable records

Use composed native captures at actual scale and cadence. Stills can approve
identity while missing gait defects; short loops can hide route/endpoint issues.
Synchronized comparisons and frame stepping made these differences reviewable.
A GIF is convenient but palette-converted; full-color PNG captures remain the
reference. Compilation or decoder CI alone does not prove correct presentation.

After a major integration change, smoke test first, then regression. Confirm
selected asset paths, native coordinates, clean exit, original archive-member
preservation and golden output. Human review supplies artistic acceptance;
passing loaders and hashes does not. Store persistent reports for useful evidence.

Keep selected raw PNGs, used generated ancestors, exact prompts and actual ordered
references. Include original reference hashes, export math, known tool/library
versions, selected output hashes, validation and scoped human decisions. Keep
rejection reasons for unused variants. Never invent a model identifier or seed
the generator did not expose.

Preserve hashed historical records when appending later acceptance. Git newline
normalization can invalidate byte-hashed prompts/reports: use an explicit
byte-preservation rule for such bundles, or a documented decoded prompt-string
hash independent of JSON newlines. Verify staged bytes as well as working files.
Generated-image caches, ignored experiments and localhost previews are not the
durable record. Save selected art and useful learning in Git before closing a
phase, without duplicating the original resource archive into every style pack.

Source storage needs attention before scaling: the first directional source
bundle alone is about 14.7 MB for eleven used generated PNGs. Preserve reproducible
exports and decision history while keeping source bundles separate from shipped
runtime art. Do not assume a repeated prompt will regenerate identical pixels.

One local Windows tooling failure is also worth preserving: `rg` resolved to a
`rg.cmd` wrapper, and a quoted pattern containing `>` was reinterpreted as shell
redirection. A search overwrote one C file with its results. The file had no
uncommitted edits and was restored from the branch before building; its diff
was verified clean. Use the available `rg.exe` directly on this machine when
searching patterns with shell metacharacters.

Generation-reference mechanisms also matter. A call using recent conversation
images does not have an explicit list of local file paths. Record the actual
mechanism and the roles stated in its prompt; mark any unresolved correspondence
rather than rewriting the historical request as a confidently ordered path list.

## Next style

The [post-merge audit](cartoon-post-merge-audit.md) records delivery verification,
the remaining maintenance findings and the scope of the approved scene.

Reuse the geometry and workflow, not unreviewed Cartoon-specific scales or visual
choices. Establish identity and one directional key, then a complete native-timed
loop and layered scene. Register the style deliberately and label partial coverage
until its intended scene families and alternate states have been reviewed.

The user's Noir direction means film noir: strong shadows, monochrome or muted
colors. Anime and a Cuphead-like classic-cartoon direction remain future ideas,
not approved designs or implemented packs. They inherit the same canvas, alpha,
motion and contact checks.
