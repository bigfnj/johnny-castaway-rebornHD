# Character authoring playbook

Use this handoff for character inventory and later style work. The current task
classifies and extracts references; it does not authorize bulk regeneration.
Original pixels establish pose geometry. Approved styled art establishes
appearance. Native captures establish the displayed motion and contacts. JSON
records connect those sources and decisions; they do not replace the images.

## Current Cartoon choices

Production has 43 accepted assets: 28 Johnny poses and 15 island assets.
The Johnny subset is `JOHNWALK.BMP` frames 000-012 and 015-029. This is not all
character artwork, all 36 JOHNWALK slots, or every story use of those poses.
Use the [current catalog](knowledge-base/cartoon-production-catalog.md) and
[aggregate acceptance](../art/cartoon/skin-tone-v1/production-acceptance.json)
for current coverage; older bundle counts and pending statuses describe their
historical checkpoints.

The [complete extracted character worklist](../art/cartoon/character-inventory-v1/README.md)
now covers every supplied-original BMP/SCR slot. It retains1,002 outstanding
confirmed Johnny slots and84 uncertain app slots, including separate body parts
and combined character/prop drawings. This inventory lets character production
pause while independent scenery/prop work proceeds; it does not mark those
remaining drawings as completed.

| Cartoon decision | Carry forward deliberately |
|---|---|
| Identity | Lean body, long rounded nose, shaggy hair, full scruffy beard, ragged white shorts, white sailor cap with projecting dark brim, narrow gold band and anchor. Stubble and a bowl-shaped cap were rejected. |
| Walking expression | The user chose Calm focus over the raised-eyebrow alternative. Avoid a downcast gaze. The approved 010 Face v1 resolves its cross-eyed appearance; transfer the pupil relationship without enlarging the head. Story actions may need their own original expressions. |
| Skin palette | The user chose the lighter 029 skin reference. Its inspected flat calibration patch is RGB 252,148,88. That is a material reference, not a flat fill for every skin pixel or a palette requirement for Noir/anime. |
| Standing 018 | Current production uses normalized foot-v5. Longer lower torso and lower shorts were accepted before the final smaller-foot correction. Preserve the separate proportion, color and contact decisions. |

The [character sheet and history](../art/cartoon/character-history-v1/README.md)
explain the design. Later walking keys, gaze and palette decisions refine it.
A new style needs its own appearance approval. Do not copy Cartoon's exact
scale, palette or arm interpretation as universal requirements.

## Inventory before generation

Use resource name plus frame index as the slot identity. Count source slots,
unique encoded images, unique decoded pixels and reviewed motion families
separately. Identical images can have different timing, mirrors, contacts or
script uses. Blank HD proxies and placeholders retain their runtime paths.
An HD proxy's blank/duplicate status is not a supplied-original fact.

Classify visible content, with uncertainty recorded: Johnny, another character,
character with prop/effect, non-character, blank/placeholder or unresolved.
Resource filenames alone cannot establish that every frame contains Johnny.
Do not turn a generated face, a cropped contact sheet or an uninspected resource
into a confirmed classification. Keep mixed frames visible in the worklist.

Extract exact supplied-original frames where available, with source resource
hashes, decoder identity, native canvas and transparency/palette caveats. Store
native pixels and a documented nearest-neighbor enlargement. Keep supplied
originals, bundled originals and HD proxies distinctly labeled. Neither a
diagnostic-palette export nor original artwork rendered by our port is a capture
of the original executable.

Join frames to actual script loads/draws and compiled walking tables. Record
neighbors, full-canvas mirrors, origins, holds and shared uses. Ordinary turn003
also belongs to profile walking001-008; a turn-only replacement would interrupt
that cycle. Static TTM occurrences identify review targets, not executed scenes
or distinct outcomes. Unreferenced variants are not automatically missing scenes.

## Build one coherent family

| Reference role | What to establish |
|---|---|
| Original pose | Body yaw, shoulders/hips, hands leaving or returning to pockets, limb overlaps, support/lift, prop contact, canvas and native placement. Keep diagnostic color and gray shadow separate from anatomy. |
| Approved identity | Cap, beard, face, clothing and drawing language. State which input controls each feature; an adjacent frame should not silently become the only character reference. |
| Neighbors and props | Arm phase, fabric continuity and shared contacts through the complete sequence. A mixed character/prop frame may need coordinated artwork for both; do not crop away a baked-in prop or assume the engine can separate it. |

Map a review's displayed position back to its resource frame before editing.
Trace a limb from the shorts opening through knee, ankle and foot. Screen-left
does not prove anatomical left; use visible overlap and qualified near/far
descriptions when small original pixels are ambiguous. Check bent knees, raised
heels and one distal toe group, including the transition into the next pose.

Far-arm visibility depends on view and phase. Hiding it in oblique front028/029
was approved; hiding it throughout the profile cycle was wrong. The accepted
profile swing reveals it forward through 008/001/002, backward through 004/005/006,
with passing-pose occlusion near 003/007. Review appearance/disappearance in motion.

Keep a shared drawing scale and a consistently defined registration landmark
within a family. Record raw coordinates, pixel-edge conventions, enlargement,
affine transform, runtime canvas and library version. Cap-based alignment removed
the earlier body pop and sideways recoil. Do not fit each silhouette, align each
sole independently, recenter the camera, stretch limbs or change the native route
to conceal a mismatch. Yaw can come from shoulders, hips and limb overlap even
when the original head stays steady.

A documented engineering margin can change without changing anatomy: selected
010 uses a versioned cap Y of 0.10 instead of 0.25 HD pixels, with unchanged fit
checks and scale. This specific correction does not license arbitrary offsets.
Preserve old exporters and failed recipes; measure both source-cell containment
and filtered edges. A padded review can expose a whole foot that the runtime
canvas would clip.

Ground contact needs the actual island position and mirror. For 018, matching
cap height alone retained shorts too high; simply lengthening shins would have
kept the wrong garment proportions. Later, the smaller foot reached one shore
position but hovered at another mirrored arrival. Compare the original at the
same origin and inspect clean sand beneath the foot. The original opaque gray
shadow is not a sole landmark. Cartoon may need a different visible sole extent
when it omits that shadow; approve the composed result rather than copying its
bounding-box bottom. Keep neighboring waist/hem transitions visible.

Use one asset or targeted edit per image call. Preserve reference order and roles.
Numeric movement, output-size and "keep everything else" instructions are
requests, not guarantees: foot edits repeatedly undershot, pupil edits overshot,
and arm edits moved caps. Recheck the entire returned image. If edits repeatedly
retain the wrong structure, restart from a suitable approved ancestor with the
original pose first. Do not carry rejected shorts or leg anatomy forward by habit.

## Alpha and materials after every edit

Inspect actual alpha and composite against light/dark backgrounds. RGB under
alpha 0 can look like a matte while remaining invisible; nonzero-alpha corners
are real contamination. State measurement thresholds. Alpha>=8 bounds do not
prove that faint fringe is absent or interiors are fully opaque. Preserve the
established premultiplied resampling and export supported straight-alpha PNGs;
do not silently harden edges or apply a magenta key.

Review skin, cloth, beard, hair, eyes, ink and cap as consistent materials across
the whole family. Hash equality proves reproduction, not good palette matching.
The 024-to-029 color jump existed in accepted raw artwork and was faithfully
rendered. The user's explicit code-color authorization allowed a deterministic
post-export skin correction while keeping alpha, canvas and position exact.
Anatomy/contour revisions still use image generation.

Every newly generated geometry needs a fresh mask and material review. Calibrate
from fixed flat-skin patches, preserve relative shading and retain 029 as a true
unchanged control. Protect the entire cap, including antialiased gold edges;
skin classification initially leaked there. Use independent material witnesses
as well as algorithm annotations. When a witness is mislabeled, preserve the
failed annotation and correct its coordinates explicitly. Sparse samples do not
prove perfect segmentation. Recheck palette even after an apparently local foot
edit:018's calf color drifted and needed fresh normalization.

## Review and preserve the actual result

Start with a clear scoped question, then expand from key pose to complete family
and native scene. Show full canvases at matched scale, Normal speed, fixed camera,
actual timestamps and lossless captures, with pause/step and arrival/departure
access. Check both directions and relevant ground/prop/foreground contacts.
An HD fallback pose or prop between Cartoon frames is an explicit seam to review,
not evidence that its artwork is complete. Missing scene composition can make a
diagnostic ocean black without establishing a bad ocean asset.

Technical checks should precede human review: selected frame/source/recipe/output
bindings, fit, archive preservation, actual draw/timing comparison, smoke then
regression, and a named failing control for a new guard. Keep unchanged controls
alongside changed ones. Do not repair unexpected engine timing inside an art
preview; record it separately for original-executable comparison.

Append the exact human question/answer and shown artifact hashes. Appearance,
gaze, arm direction, colors, gait, contact and production integration can have
different scopes. Accepted artistic differences remain accepted differences,
not claimed anatomical parity. Later context-specific feedback can expose a new
problem without invalidating the earlier review. Do not infer which clips the
user watched or approval of unseen story placements.

Preserve selected raw PNGs, all generated ancestors actually used, exact calls,
ordered references, original-source identities, rejected-attempt reasons,
export/filter versions and scoped decisions. A rejected drawing used as an input
is still an ancestor; an unused later attempt is not. Record unsubmitted requests
as unsubmitted. Do not invent generator seeds, model IDs or explicit path order
for calls that used recent conversation images.

Keep historical approvals, pending-at-capture reports and recipes immutable.
Verify working bytes, staged bytes and **index completeness**: every declared
copied evidence file must be in Git with the expected hash. PR15 omitted three
correct local records inside an ignored nested `build/` directory. Checking only
existing staged files missed them. Separate copied durable evidence from
intentional external originals and scratch captures; exercise an omitted-file
control when adding the maintained check. See the
[post-merge finding](cartoon-connecting-poses-post-merge-audit.md).

## What "finished" means

| Claim | Required evidence and limit |
|---|---|
| Character inventory complete | Every slot in the declared source universe has a classification or explicit unresolved disposition; resource/frame identity, duplicate/blank distinctions and source confidence are preserved. No new art implied. |
| References extracted | Declared frames have native images, documented enlargement, source hashes and an index whose entries resolve. Extraction is not artistic approval. |
| Family ready to author | Complete motion/shared-use dependencies, mixed props, required directions, appearance references and review scope are identified. Unresolved source questions remain named. |
| Family technically ready | Selected generated sources reproduce exact exports, fit their canvases and pass scoped smoke/regression checks. This is not human acceptance. |
| Family accepted and integrated | Scoped human decisions bind the displayed outputs; the production ledger/package preserves prior ancestry and passes integration checks. |
| Story contexts tested | Named actual scenes, branches, placements and outcomes were executed and reviewed. Static references, extracted frames and walking approvals do not supply this status. |

The present pass can finish its inventory and extraction scope while generation,
approval and story testing remain pending. "All character art complete" requires
a separately defined coverage target and evidence across those states.

For details, retain the family records: [Calm focus](art-style-learnings-calm-focus.md),
[rear walk](art-style-learnings-rear-walk.md),
[front refresh](art-style-learnings-front-refresh.md),
[arrival/contact](art-style-learnings-arrival.md),
[profile arms](art-style-learnings-profile-walk.md), and
[connecting poses/palette](art-style-learnings-connecting-poses.md).
