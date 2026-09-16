# New018-v2 palette matching

The new proportions source has its own runtime PNG and annotations. This layer
uses the unchanged, hash-pinned `skin-tone-v1/correct.py` functions
`skin_confidence`, `cap_exclusion` and `recolor`. It does not load the old018
mask or old018 calibration, change alpha, move pixels or adjust anatomy.

`reference-v2.json` was independently annotated from runtime018 SHA256
`b1bf6834e30e11ccff6a4f4a66e8a0d1bd7bf3d1f5ca82eeb98d34c88b45b29f`.
Its near-calf3x3 sample at[27,112] has median[252,154,94]. The target[252,148,88]
is checked against canonical029's retained input and calibration patch. The
sloped cap exclusion protects the crown/brim/gold without covering visible ear
skin. Seven protected material points and three regions provide separate checks.

The resulting PNG SHA256 is
`21cf94cd90d369b20b6d3b8ef60b7cc2848f919ff828578320502aec9a17c55b`;
1,673 skin pixels change. Alpha,64x154 canvas, full cap, annotated materials and
all pixels outside the soft mask remain exact. These checks describe color
behavior. Revised proportions and ground contact still require the human review.

## Reproduce

Use Python3.11.15, Pillow12.3.0 and NumPy2.4.6. Recreate the source export in
`build/standing018-proportions/stage-v2/runtime` following `../export/EXPORT.md`
with raw `018-torso-v2.png` SHA256
`c170f8b6cea7c8c3c0cfcad5dea1ac5591e9d92b5de156afeee7a19c1e2ec89c`.
The copied original exporter and references remain byte-identical. V2's exact
technical recipe/report are retained under `../export/trials-v1/v2/runtime/`.
Use a fresh output directory for every color run:

```text
python -B art/cartoon/standing018-proportions-v1/color/correct018.py --runtime build/standing018-proportions/stage-v2/runtime --annotations art/cartoon/standing018-proportions-v1/color/reference-v2.json --annotations-sha256 2912b2ba7d5fd363a02e0f8955524d508f20506de90855d201ba6f9f10544efc --output build/standing018-proportions/color-v2
python -B art/cartoon/standing018-proportions-v1/color/test_color018.py --export build/standing018-proportions/color-v2 --output build/standing018-proportions/color-checks-v2 --phase smoke
python -B art/cartoon/standing018-proportions-v1/color/test_color018.py --export build/standing018-proportions/color-v2 --output build/standing018-proportions/color-checks-v2 --phase regression
```

The smoke checks the actual018 output. Regression checks the new source/mask,
all protected witnesses, a fresh-process byte-exact replay, same-base and
zero-mask no-op controls. Eleven image/mask corruptions and three stale-input
substitutions each trigger their named failure after generic output hashes are
updated as appropriate. Inputs and reviewed outputs remain untouched.

`evidence-v2/` retains exact color outputs, recipe, smoke/regression and source
export records. The evidence manifest binds these files and the actual helpers.
No original28-pose color tests or native gates are claimed to have been rerun.
