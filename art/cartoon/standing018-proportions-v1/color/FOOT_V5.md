# Foot-v5 color replay

The selected raw `018-foot-v5.png` reaches the requested technical sole bounds:
far144.6HD and near146.1HD at the unchanged scale0.1, cap target[17,0.25] and
64x154 canvas. These source-contour measurements do not prove native contact
or approve the final motion. The raw image remains unchanged.

`correct018_foot_v5.py` is a sibling of the frozen v2 adapter. Only its input
PNG hash, opening description and preview scope differ. It imports the same
hash-pinned skin confidence, cap raster and color functions. Its fresh v5
annotation is `reference-foot-v5.json`; neither the old annotation nor old
mask is used. The near-calf median changes from[252,162,103] to the approved029
target[252,148,88]. The pass changes1736RGB pixels and preserves every v5 alpha
value, canvas position, outside-mask pixel and protected cap pixel.

`check_foot_v5.py` imports the byte-unchanged `test_color018.py`, injecting the
explicit v5 adapter before import. Its existing assertions,14 negative controls,
fresh-process replay and two no-op controls execute unchanged. The inherited
test's v2 scope text is retained as `inherited_test_scope`; the new report scope
names the actual v5 run. Its historical `WITNESS correct018.py` label remains
the same, with the actual sibling adapter's SHA256. Reports bind both source
hashes and the new runner. This does not rewrite any v2 record.

Run from the repository root with Python3.11.15, Pillow12.3.0 and NumPy2.4.6.
Use fresh paths for STAGE, COLOR and CHECKS. Stage the selected raw with its
source hash, then replay the retained technical recipe:

```text
python -B art/cartoon/standing018-proportions-v1/export/stage.py --source art/cartoon/standing018-proportions-v1/018-foot-v5.png --source-sha256 97922bacf481925f29640606e305ba1747b7de5fb1b01439e4fcdaf8e2621c5e --work STAGE
python -B STAGE/authoring/export.py --recipe art/cartoon/standing018-proportions-v1/export/trials-foot-v5/runtime/recipe.json --output STAGE/runtime
python -B art/cartoon/standing018-proportions-v1/color/correct018_foot_v5.py --runtime STAGE/runtime --annotations art/cartoon/standing018-proportions-v1/color/reference-foot-v5.json --annotations-sha256 e1bde6bf34f91a5d81a308187a305b7344d31e8acf5f2a51fab6afc29406acf1 --output COLOR
python -B art/cartoon/standing018-proportions-v1/color/check_foot_v5.py --export COLOR --output CHECKS --phase smoke
python -B art/cartoon/standing018-proportions-v1/color/check_foot_v5.py --export COLOR --output CHECKS --phase regression
```

The source runtime must hash to
`183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2`.
The normalized PNG must hash to
`5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f`.
Fresh-path color recipes record those new source paths and export-report hashes,
so their full JSON hash can differ. The original run's fresh-process replay
uses identical inputs and reproduces PNG, mask, cap mask and recipe bytes.

The actual v5 authoring run passed3smoke then20regression cases. The color run
passed smoke before its regression, including14 named corruptions and the
same-base/zero-mask controls. A separate process supplied the valid historical
v2 runtime to the new adapter and received the named018 runtime-source refusal.
No new classification or fit guard was added and no old28-frame suite was rerun.

Compared with v2 before color correction, v5's upper-body and shorts alpha8
runtime bounding boxes are unchanged, but14 upper-body and15 shorts silhouette
pixels differ in the documented regions. Neutral-white cloth spans76.2 to101.5HD
versus76.1 to101.4HD. Image generation did not preserve upper-body or shorts bytes
exactly; these coarse measurements do not establish anatomical identity.
`export/trials-foot-v5/measurements.json` retains the expressions and source hashes.

`evidence-foot-v5/` preserves the exact output, masks, recipe, source export and
test reports. Its manifest binds these files, this document, the unchanged tests,
the new adapter/runner, fresh annotation and source comparison. Color alpha
identity applies to v5 only. The other27 Johnny outputs remain the earlier
approved color exports; the previous v2 standing study stays historical.
