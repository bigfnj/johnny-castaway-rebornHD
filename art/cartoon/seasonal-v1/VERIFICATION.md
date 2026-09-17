# Seasonal draft verification

The current human-review candidate is export v2. Production remains unchanged.
The diagnostic ZIP is
`ed399c7b6cd9f0d2d4b3f24dc1811892709294afb9448bf6684b3a1b536906e4`.

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

Final native evidence binder:
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
