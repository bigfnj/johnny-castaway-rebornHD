# Prop authoring lessons

The user requested batches of at least24 drawings per art review on2026-09-17. Keep full smoke/regression for the combined asset delivery, retain original comparisons and collect individual frame corrections together. [Current workflow](cartoon-art-build-workflow.md).

## Shared style with original geometry

Use one family key for material consistency, while passing each original frame separately for its geometry. The raft's finished004 supplies wood and rope appearance; the original incomplete frames control the open sections. A draft002 added a seventh log before later six-log stages, so a targeted second generation corrected that visible continuity error. Preserve both outputs and the exact request rather than replacing the discarded draft.

The sandcastle's complete000 supplies warm sand colors, outlines and lighting. Partial walls, ruined arches and airborne sand need their own original references; a complete-castle prompt alone does not establish those different silhouettes. Generated character-free props can still depend on Johnny's interaction and layering during runtime review.

## Transparency observations

Raw-image viewers may expose RGB color stored in fully transparent pixels. The idea-symbol exclamation001-v1 appeared to have a brown haze in the tool view, but sampled broad-haze pixels were alpha0. The browser review on its actual checkerboard showed clean transparent gaps with no visible brown cloud. A targeted v2 was already running when this was discovered. It remains an unselected alternative, and no halo fix is claimed. Judge the actual composited appearance before requesting another art edit.

Very faint alpha also makes any-alpha bounds unreliable for registration. The boat's raw any-alpha bounds are(90,71)-(1895,766), while alpha>=8 gives(92,197)-(1893,613). These are measured image bounds, not alternate export recipes. Preserve the raw image and register against original geometry; do not shrink a drawing because nearly transparent specks expand its bounding box. Technical export and any required edge handling remain integration work.

## Review and acceptance

Actual generated dimensions can differ from requested dimensions. Record returned canvas, alpha and hashes. The complete raw preview is for design approval; uniform-scale export, original registration and native motion are later work. A question naming four coconut orientations approves those four, without silently approving hidden shadow drafts or claiming production acceptance.

## Ship-family findings

The user's "all approved, nice job, please continue" response approved all24 selected drawings in the first combined prop gallery. The acceptance record binds the exact displayed versions, including MRAFT002-v2 and SANDCAST009/010-v2. Unselected alternatives remain separate.

Inspect the actual pixels before turning an inventory count into a drawing count. SHIPS010-013 are four identical8x1 originals, each containing one black pixel. Their `not_johnny` classification does not establish that they are visible props or unused placeholders. Keep the exact source pixels and record their unresolved role. The37-slot ship batch therefore contains33 newly drawn assets and four unchanged source slots.

Resource frames can be joined parts. Existing GJLILIPU draw coordinates place SHIPS007 above003, then cycle004-006 beneath it. SHIPS007 is an upper ship section and003-006 are lower hull/water strips. SHIPS008 supplies a complete ship identity for those parts. GJPROW000/001 are cropped red hull panels, with an anchor on000 only. Do not redraw any of these as independent complete boats. Final joins and registration remain bulk integration work.

A single end-on style key can pull other tanker angles toward its camera and invent a long gantry crossbeam. Use the clearer side-view key to resolve the compact deck structure, while keeping each original's foreshortening authoritative. Store rejected rotations instead of overwriting them. Appearance approval does not establish smooth yaw between independent drafts.

Water palette consistency matters within a frame family. Diagnostic source-blue is not an approved Cartoon color. Compare lower-hull phases against the same turquoise-water key before review; correct visible color drift without changing the ship geometry. A brown halo seen in the raw SHIPS007 viewer was hidden RGB at alpha0 and vanished on a real neutral composite. Inspect alpha before requesting another edit.

The first tanker animation request exposed a limitation of the still gallery. The actual GJVIS6 tag 9 sequence has 76 draws, repeated frames and four mirrored/unmirrored runs; it is not a 000-013 loop. Use those source commands for a lightweight motion review when perspective is disputed. The first isolated comparison showed that its Cartoon end-on drawings were too shallow and 006 too flat. That feedback drove the later correction pass. The user approved the other 19 drawings separately; that earlier approval did not include the tanker.

The user explicitly rejected the long bar in TANKER000-002. It is the elevated red horizontal span on either side of the white cabin, with tall red/white outer support posts. Remove that entire structure together; unsupported posts would still flash against 003. Keep low deck bollards and vents distinct from the rejected structure. Targeted built-in image edits produced three v2 drafts with the bar removed, preserving raw alpha and separate review provenance. That localized removal was not a complete rotation correction: at that stage the broad stepped cabin in 002 still changed to the compact tower arrangement in 003, and the end-on depth and 006 perspective still required the subsequent rotation pass.

The 2026-09-18 reply "looks good, continue" approved the bar removal. The subsequent rotation pass treats 000 as stern-on, 006 as a slight stern-quarter, 007 as the broadside pivot, 009 as bow-quarter and 013 as bow-on. These are visual readings of the original silhouettes, not documented exact yaw degrees. Use a shared stern key plus a broadside structure reference so cabin overlap changes with the angle rather than swapping ship identity. Compare adjacent frames in both the original travel sequence and an unmirrored still gallery.

Measure meaningful alpha bounds when checking proportions. Original 000 is about 2.08 times as wide as tall versus the earlier draft's 3.22; original 007 is 2.80 versus 4.02. Uniform fitting exposed those differences, it did not create them. A numeric ratio in a generation prompt is not a reliable geometric constraint: some targeted drafts overshot from too wide to too narrow. Preserve the attempts, inspect the rendered silhouette and use a narrowly described hull-width correction when the angle is already useful. Do not stretch pixels or silently mark approximate geometry accepted. The third motion review retains original, earlier and revised versions together so the user can judge the result.

For 012, a full camera/proportion revision overshot from a narrow 1.49 ratio to 2.41, then an angle correction returned to 1.54. A final request kept that useful angle and cabin while widening only the foreground hull, producing 1.93 against the original 2.00. These are alpha-at-least-8 bounding-box observations, not an exact contour or pixel-preservation proof. Narrow the requested edit when a broad redesign keeps disturbing a part that already works.

On 2026-09-18 the user said "approved, continue please" at the [third tanker review](../art/cartoon/tanker-motion-v3/README.md). [Acceptance](../art/cartoon/tanker-motion-v3/acceptance/appearance-rotation-v1.json) covers appearance and isolated source-replay rotation for all 14 selected views, including 11 updated 000-009/012 and unchanged 010/011/013. This human decision, rather than a ratio threshold, establishes the scoped acceptance. Preserve the earlier bar-removal approval and rejected drafts as history. Native export sizing, original-canvas registration, scene motion and bulk integration remain pending.

## Campfire family findings

FIRE1 has separate wood, smoke and flame layers. Keep logs out of flame-generation prompts. The first 000 draft interpreted isolated red source marks as floating wood fragments; a targeted edit removed those before establishing the wood reference. Shared flame013 and smoke001 references keep material and linework consistent while each exact original supplies its own phase geometry.

Review joined layers early even when full testing is deferred. FIRE1 000 v2's shallow silhouette left a visible gap below the flames under uniform original-bounds fitting. V3 restores taller connected central sticks, retaining almost the same width and changing its meaningful width/height ratio from 2.681 to 1.575. The preview keeps the original script coordinates instead of hiding the shape mismatch with a position offset. Late 023/024 also need visibly fewer sticks, not just a smaller copy of the initial pile.

Do not infer an animation from consecutive filenames. The medium fire uses 009, 011, 010, 012, and four phases in the five normal effect groups put the wood on top of the effect. Preserve the actual draw order and positions. Normal groups use nominal port timing of 140 ms per phase, but repeating them in an isolated review is an editorial choice, not a claim about the complete story or original executable timing. The retained [phase evidence](../art/cartoon/fire-v1/reference/phase-sequences.json) also documents the dying-fire and clipped ember sequences for integration.

027 is a white fire-centered pop/burst graphic in the disappointed action, with radial strokes and no speech tail or text. 025 lacks a uniquely attributed draw site in the saved map; retain its drawing without claiming it is unused. The user approved [all 28 selected drawings](../art/cartoon/fire-v1/README.md) on 2026-09-18 with "excellent, approved". [Exact acceptance](../art/cartoon/fire-v1/acceptance/appearance-v1.json) records the displayed gallery and isolated phase comparison; bulk scene integration remains pending.

## Food, boots and small-raft authoring

The [25-drawing follow-up](../art/cartoon/campfire-props-v1/README.md) uses one shared identity key per animal/material, then each exact original frame as the pose authority. Distorted, inverted and edge-on boot states need their original geometry, not a repeated upright boot. FIRE2 018 is a tail-only piece; 019 is a toe/sole-only piece. The compact red shapes 021/024 belong to squid cooking/eating, not fish bones.

Resource classification alone is insufficient to separate Johnny from props. FIRE2 010/011 are small grip overlays despite the old `not_johnny` labels. [Same-tag resource loads and original-pixel composites](../art/cartoon/fire-v1/next-batch.md) resolve their role. Slot 5 is reused across FIRE2/FIRE3, so an ambiguous static draw list must not be treated as an executed resource trace. Retain those two grips with the character action and fix the inventory during its next regeneration.

FIRE5 000/001 are reflected source companions of FIRE2 024/023 with different canvas padding. Preserve the shared identity and reflection in new art, and reserve exact fitting for integration. No runtime load is proved for FIRE5, and 002 is a distinct fish variant. Separate SRAFT 000/001 contain only a raft and paddle; borrow the approved MRAFT wood/rope style, not its geometry or approval.

Use alpha bounds only to size review cards, drawing the full raw image. Preserve unmodified output bytes and actual transparency. RGB color beneath alpha zero can look like a glow in a raw viewer; a light/dark browser composite is the meaningful appearance check. Gallery scale does not establish hand contact, mouth contact or native registration.

## Direction and eyes take precedence over shape ratios

The user's [13-frame correction](../art/cartoon/campfire-props-direction-v2/README.md) exposed an authoring error in the initial food/boot batch. FIRE2 fish 012/013/014 are upside-down, with their eyes below the body; 014 shows both eyes. Boot 009/015 are rear views walking away, not front views that need a shorter shaft. Boot 005/022 are toe-down and foreshortened. The 019 fragment is upside-down with the connection below, not an upright shoe torn at its right end. FIRE2 squid 006/021/024 and FIRE5 000 require two eyes; phase-specific left/down-left/down-right gaze matters, and 007 must look aggressively left.

Treat shared generated keys as material/identity references only when their pose differs from the source. Before generation, write down facing, visible eye count, eye location, gaze, top/bottom surfaces and the direction of any connection. Inspect black source shapes on a light background. A bounds ratio can diagnose stretching but cannot validate any of those pose facts. Do not fix an eye location while leaving belly/dorsal anatomy upright, or mistake a boot's heel for its toe. Preserve rejected interpretations with an explicit correction record so future packs do not inherit their misleading pose descriptions.

The user's [next annotated correction](../art/cartoon/campfire-props-bend-v3/README.md) separates whole-object orientation from internal bending. Boot 005 needs a curved sole; 022 is almost on its side with its cuff bending down toward the toe's ground plane. The latest green marks for squid 006 put both eyes on the upper-facing head surface with an upward gaze, superseding the lower-face interpretation. Squid 021 retains its rounded head but loses the stray head appendage and looks down-left. Carry that rounded head into 024 and FIRE5 000 while preserving their already-correct body and eye directions. The user permits a mirrored pair; independent generated edits must not be described as exact pixel mirrors without checking. Save the actual annotations because a phrase such as "two eyes" does not specify their anatomical placement.
