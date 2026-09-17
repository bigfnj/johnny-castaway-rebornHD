# Cartoon low-tide artwork: first static review

This branch covers the14-asset low-tide group: exposed beach BACKGRND001, offshore rock002 and twelve waves030-041. Static beach/rock appearance is approved; the combined wave candidate is ready for motion review in `motion-review-v1/review.html`. It reuses all nine approved island wave drawings and adds three matching rock-ring drawings. No production asset, runtime source or production acceptance ledger has changed. Main starts at `da787d63279ea91bd6c637e02133821339470bfc`.

Selected studies are `shore-raw-v3.png` and `rock-raw-v2.png`. The user subsequently approved their static appearance with "looks good"; `static-shape-approval.json` records the exact exports and review page. Wave artwork and combined motion remain pending. Open `review/review.html` through a local HTTP server. Start with Earlier Cartoon, then Original shape. Existing-wave and clover views expose the remaining fallback overlays; they do not represent completed low-tide art.

## Decisions and lessons

| Finding | Decision or next action |
| --- | --- |
| Low tide has a separate beach layer and rock, not a scaled copy of high tide. | Retain the approved upper island and existing draw origins. |
| Original001 includes a red starfish and two small right-hand shore objects. | Retain that grouping. The red/white object's precise identity is uncertain; the draft interprets it as a shell. Human review can correct that interpretation. |
| First beach was too deep; second exposed three blue seam gaps beneath the upper island. | Retain both ancestors. The third image raises the upper overlap edge and covers the measured gaps. |
| The generator changed raw scale despite instructions to preserve padding. | Register with one uniform scale and translation. Do not distort individual axes or assume requested image bounds were obeyed. |
| Dark RGB beneath transparent pixels looked like a halo in raw inspection. | Judge premultiplied compositing and actual alpha. No arbitrary alpha/color cleanup was applied. |
| The exported rock extends about14 HD pixels farther right than the original visible footprint. | Review its size, then author the ring039-041 against the actual selected export. |
| Original low-wave sprites contain changing beach material as well as water. | Establish material ownership before drawing. Do not erase all ground or duplicate the static beach into every wave. |
| Frame031 is wider than030/032. | Preserve its256x96 canvas; the neighbors are240x96. |
| Four staggered three-frame wave families recur every1920ms. | Final motion review must show every family and several full recurrences. The initial2880ms native captures cover all phases, not two full cycles. |
| The tide is selected when a scene is initialized. | Test high and low states separately. There is no existing animated tide-rise transition to demonstrate. |

## Reproduction and evidence

`generation-index.json` binds all five raw outputs to their exact prompts and ordered references. The used seam-defect reference is preserved as `reference/shore-v2-join-defect.png`. No raw ancestor was overwritten.

`static-v2/` contains the selected exported PNGs and export report. Export with the project's Python/Pillow environment:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/export_draft.py --output build/low-tide-replay --candidate build/low-tide-replay.zip
```

Use new output paths. The exporter pins the current production archive SHA256 `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`. It uses the existing seasonal premultiplied resampler with uniform transforms. Meaningful alpha>=8 is not clipped; the cropped faint fringe has maximum alpha4, recorded in the report.

The private candidate SHA256 is `f46e5cac5508b00cc7a675be4eaf843029cebfeabe80c849c8fa5f311813b92b`. It adds only001/002 and preserves all2598 previous ZIP members exactly. First export passed the existing PNG validation; the fresh repeat reproduced all output bytes and the entire candidate ZIP. `preflight/export-repeat.json` records that comparison. `preflight/static-review.md` contains the independent readback and seam measurements.

`native-v1/README.md` describes the native smoke-then-repeat runs and their limits. The no-decoration and clover cases pass with unchanged calls/timing and unchanged pixels outside the two new sprite rectangles. Both real pre-wave backgrounds were captured after002 through a scratch-only observer; its later displayed frames match the ordinary observer's prefix. These are background surfaces before clouds, Johnny and holidays, not complete scene captures. Full scene captures keep the old wave artwork visibly intact.

`prepare_review.py` is the authoring-session preservation helper. It copies completed scratch exports and reports into this durable folder and prepares review image copies. Its input scratch locations need the recorded runs; it is not an independent replay of native captures. The review uses preserved PNGs and needs no build tooling. The original-shape image is a technical composite in diagnostic colors, not a DOSBox/original executable screenshot.

## Pending

Static shapes are approved. The user then asked to reuse the already approved new waves. Re-register the nine island wave drawings from their unmasked ancestors against the low-tide shore, retaining the corrected white center phase. Fit three rock-ring phases in the same style to the separate rock geometry. Repeat native smoke and regression checks, review combined motion with clovers and raft positions, update the art inventory and lessons, and complete production integration and the post-merge audit. Approval of the static page alone does not approve the final combined motion.
