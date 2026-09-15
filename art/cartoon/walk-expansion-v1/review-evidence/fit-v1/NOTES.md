# Rear walking fit review

The six runtime-candidate-v1 exports are ready for actual island review. This
technical review assigns no production acceptance and makes no original-engine
visual-parity claim. The [report](report.json) records input/output hashes and
the [contact sheet](comparison.png) preserves one compact comparison.

The review compared the [motion-v2 recipe](../motion-v2/recipe.json) and its
reproduced padded PNGs with the candidate exports, following the
[fit-correction prompts](../../fit-correction-prompts.json). Frames 011, 019,
021 and 023 retain exact raw and padded bytes. The corrected 020 heel and 022
outer feet are narrower. The same-coordinate raw crops and fixed-scale sheet
show no obvious torso, cap, body-yaw or knee-pose drift that blocks island review.
Small outline, shading and detail changes occur beyond the feet in both new
raws, so the prompt's preservation request was not achieved pixel-exactly.

All six runtime PNGs exactly equal their padded central crops. Every padded
pixel with alpha >= 8 survives, and the corresponding raw pixel centers fit
under the recorded 0.1 affine. Faint filter fringe at alpha 1-4 is removed:
12/15/44/12/26/12 pixels for 011/019/020/021/022/023. This includes the existing
above-cap fringe and small side fringes for 020/022. The conclusion is not that
every nonzero filtered pixel fits. Registration changes are only +0.05 runtime
pixels in x for 020 and -0.1 x/+0.1 y for 022; scale is unchanged.

The sheet uses uniform neutral-gray alpha composition, shared runtime
coordinates and 3x nearest display, with a runtime-canvas border. No artwork was
painted or cleaned. Upper and lower raw crops were also inspected at 1:1; they
remain in ignored `build/fit-review/` with the comparison helper and full report.
No new broad matte or visible background halo was seen on the neutral composite.

All 31 recorded input hashes were checked again after comparison and before
preserving this evidence. Build paths in the report identify local ignored
inputs; they are not promises of tracked files. The unchanged exporter did not
warrant another regression/mutation run. Native rendering, island compositing
and the final human review remain separate checks.
