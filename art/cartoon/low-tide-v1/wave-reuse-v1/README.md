# Reused approved foam for the low-tide beach

These nine PNGs are a technical proposal for BACKGRND030–038. They reuse approved white high-tide drawings without generating new artwork. Native motion and human approval remain pending. No runtime source, production archive, or pack ledger is changed here.

The source-to-runtime transforms are fixed per family:

| Low frames | Approved high sources | Uniform scale | Runtime translation | World origin | Native runtime canvas |
| --- | --- | --- | --- | --- | --- |
| 030–032 | Unmasked side-fit003–005 | 1.5 | 6, -6 | 466, 646 | 240×96, 256×96, 240×96 |
| 033–035 | Raw006, corrected white raw007, raw008 | 0.23 | 0, -90 | 734, 712 | 352×56 |
| 036–038 | Unmasked side-fit009–011 | 1.1 | -4, 8 | 1116, 646 | 176×96 |

The center is 92% of its former displayed size because the three unmasked high phases, including faint filtered alpha, exceeded the fixed low canvas height at the former 0.25 scale. All three now use one direct raw resample, with no independent phase fitting. The sides are enlarged uniformly. There is no source crop, anisotropic distortion, contour painting, RGB correction, or alpha threshold. Alpha8 is used only for reporting bounds.

`export.py` imports the hash-pinned premultiplied RGBa bicubic8x/Lanczos filter from the existing seasonal exporter. Its enlarged audit canvas covers the entire transformed source. Every filtered nonzero alpha pixel fits the final runtime canvas across all nine frames. The retained `audit/` PNGs show that result without concealing a fringe beyond the runtime crop.

The existing ground-alpha visibility helper masks the foam against the world-aligned union of accepted ground000 and approved low static001/002. It changes alpha only, using `(foam_alpha * (255 - ground_alpha) + 127) // 255`; post-resample RGB is exact. This implements the user's selected offshore direction. It does not recreate the original sand-bearing wash. Partial-edge blending inherits the documented behavior of that existing visibility helper.

The mask retains 64.22–90.61% of the left family's summed alpha, 85.00–89.25% of the center family's, and 69.23–81.26% of the right family's. Those reductions are explicit ground occlusion, not canvas loss. Unmasked runtime images are preserved beside the outputs. The substantial phase032 occlusion and changes in phase strength should be judged in actual motion.

`candidates/v1/preview/phase-0.png` through `phase-2.png` overlay the exported PNGs at exact native world coordinates on the approved native pre-wave background. `preview/phases.png` presents matching crops. They are software placement studies: matching phase indices across the three families do not assert the engine's sequential update order or timing. No rock-ring039–041 is included. Those assets and native capture are separate work.

`recipe-v1.json` pins every source/helper/static/pre-wave record, the current 47-asset archive, selected 000 member, transforms, and origins. `candidates/v1/export-report.json` binds all 31 output files and the per-frame crop/visibility measurements. The underlying source images and frozen earlier records stay in their original locations.

## Reproduction

Use the toolbox Python with Pillow 12.3.0 from the repository root. Reproduce against the recipe, without rerunning `--prepare` or overwriting historical outputs:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/wave-reuse-v1/export.py --phase smoke --output build/low-tide-v1/wave-reuse-v1/replay-smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/wave-reuse-v1/export.py --phase full --check
```

For a fresh ordered verification record, choose a new directory:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/wave-reuse-v1/verify.py --phase smoke --output build/low-tide-v1/wave-reuse-v1/verification-replay
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/wave-reuse-v1/verify.py --phase regression --output build/low-tide-v1/wave-reuse-v1/verification-replay
```

`verification-v1/` records smoke for one frame per family, then all nine exact replays, preserved/masked alpha witnesses, fixed canvases and RGB identity. Five controls reject a swapped phase source, a single-phase translation, a substituted source hash, injected filtered alpha outside the canvas, and a mask fixture that alters RGB. The last two wrap returned helper images in process; they do not modify maintained source or claim a compiled runtime mutation. After restoring the real helpers, frame030 reproduces exactly. Native animation, low-tide wave restoration, scene offset/night behavior and Johnny contact are outside this exporter verification.
