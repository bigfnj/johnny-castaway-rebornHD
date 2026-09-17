# Seasonal draft verification

The current human-review candidate is export v3, with the pumpkin appearance
approved in the inline generated image. Production remains unchanged.
The diagnostic ZIP is
`3dea2b6e0a1435ae286dac964ab7e68e5a72efb0c364d57753d9225c9e8abcdb`.

| Phase | Result |
|---|---|
| Original references | Extraction smoke, complete pixel reproduction, named damaged-input and guard-removal controls passed. See reference/verification files. |
| Export v1 | Smoke then fresh replay passed; ten named negative controls plus an executed registration-guard removal passed. Hidden-alpha0 RGB changes did not affect premultiplied output. |
| Export v2 | Smoke then fresh replay/regression passed. Original v1 evidence and banner remain exact. All filtered alpha>=8 fits inside the runtime canvases. |
| Native baseline | 30 finite native runs: five cases each in day/night/offset, smoke before exact fresh repeats. Twelve named input/log/pixel controls passed. |
| Native v1 | Same30-run coverage passed technically. Visual inspection rejected water-overlapping ground registration. Retained as a failed visual placement, not acceptance. |
| Native v2 | Same30-run coverage and30 cross-package image comparisons passed. Three native negatives, two cross-package altered-pixel negatives and one export-binding negative fired; restored positives passed. |
| Package identity | All2594 existing production members preserved. Exactly four additions, with all four native-selected hashes equal to the v2 exported PNGs. |
| Scene isolation | Day/night/offset no-holiday scenes are exact against baseline. Other differences stay within the selected decoration canvas. Native banner captures equal v1. |
| Existing art tools | Two smoke tests then20 regressions passed. |
| Existing inventory CLI | Three smokes then11 tests passed with two Windows symlink cases explicitly skipped for unavailable privilege. Hardlink and other identity cases passed. |
| Production catalog | Three smokes then63 regressions passed. |
| Pilot history | One smoke then22 regressions passed, including its nested84-test future-promotion check. |
| Browser | All four selections and both view modes route to the intended v2 files. All five images loaded in each close-up. Native scene and sprite comparisons visually inspected. No warning/error entries returned by the browser log query. |

The initial generic unittest calls were inappropriate for the catalog/history
suites, whose main functions initialize their target modules. They failed with
import/uninitialized-module errors. The documented direct script entry points
were then used for the passing smoke/regression runs above. No production code
was changed to accommodate the mistaken invocation.

Version2 native evidence binder:
`native/evidence-candidate-v2/evidence.json`, SHA256
`664b82ccb576a43afc27aba5e8db2bb1d8428eb5c976d0452f0befdf6221b002`.
It preserves52 files including30 reports and five primary capture logs; other
full logs and executables remain in ignored build output. All task containers
were removed. Captures ran in Xvfb without opening desktop windows.

The review page uses the actual native day captures, not a browser reconstruction
of the engine. Its crops are identically positioned before/after and preserve
pixels. Native full-size images are available through View: Full scene.

## Review boundary

Human approval is pending for appearance, scale and scene contact. v2 resolved
the obvious water overlap in inspected day captures. It does not establish
calendar-trigger coverage, cargo suppression, every island/tide state or full
story interaction. Keep these limits when integrating and planning later scene
coverage; technical PASS must never be copied into an art acceptance field.

## Approved pumpkin revision, export v3

The user approved the revised red eyes and sharp-toothed grin with "so much
yes" after seeing the actual generated source. The original source, exact edit
prompt and that scoped response are preserved in `generation-pumpkin-v2.json`.

The thin v3 exporter reuses the frozen v2 filter. It retains the same pumpkin
scale/translation and copies001-003 byte-for-byte. Export smoke preceded a
fresh replay/regression. Meaningful filtered alpha stays inside the canvas;
the maximum fringe outside is3/255 and is retained in padded output. Hidden
alpha0 RGB changes leave the export exact. Two altered recipe inputs failed
with the expected label; an executed selection-guard-removal control wrote a
different PNG, then the restored original passed.

All30 native v3 captures/repeats and30 production-baseline comparisons passed.
The v2-to-v3 ZIP comparison found only000 changed, with2597 other members exact.
Twenty-four no-holiday/other-holiday captures match v2 exactly; six pumpkin
captures differ only inside its canvas. Day/night and shifted-placement
captures retain correct ground contact. The red eyes and pointed teeth were
visually inspected at game size. Existing native, comparison and export-binding
negative controls passed, and the capture container stopped.

Version3 evidence is `native/evidence-candidate-v3/evidence.json`, SHA256
`56ed88eec05ec4774d936e73c4c4b8ce80af3dcdba4422584fb342a4dea66a7a`.
It preserves54 exact files. The refreshed browser loaded all five pumpkin
comparison images from the intended v3 paths, displayed the new face and
returned no warning/error entries. The other decorations remain pending their
own visual approval. No runtime code or production archive changed.
