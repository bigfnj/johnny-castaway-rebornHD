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
