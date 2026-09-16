# Profile walking: first pose checkpoint

Branch `art/cartoon-profile-walk` starts at production `00f1ba7`. The user asked
to continue after approving the standing direction ring. This bundle prepares
the complete 001-008 family and presents two drafts for human pose review.
No profile artwork has entered the production archive or acceptance ledger.

The user subsequently requested a slightly lower tucked foot in003. The
[revised comparison](review-evidence/pose-check-v2/review.html) uses
`003-profile-v2.png`;001-v2 is unchanged. Exact edit input and prompt are in
`provenance003-v2.json` and `003-call-v2.json`. The 45-raw-pixel lowering was a
prompt target, not an asserted exact displacement. This revision awaits human
review and does not approve either pose or the full gait.

The revised003 passed export smoke3 then regression24 with unchanged tools,
followed by browser smoke and the eight existing pixel/control cases. The
browser's wrong-pose negative control also fired. Its fixed scale/canvas stay
0.1 and80x152. The measured cap moved half a raw pixel horizontally and was
remeasured for registration; no body-normalization or artistic pixel surgery
was used. Reproduce its export with `exports/003-v2/recipe.json` into
`build/profile-walk/export003-v2`, then run `revision_v2.py build`, `smoke`,
`regression` and optionally `publish`. The initial checkpoint remains below.

| Displayed pose | Selected drawing | Purpose |
|---|---|---|
| 003 | `003-profile-v1.png` | Upright support leg, tucked lifted foot, lowered near arm; shared walking/ordinary-turn slot |
| 001 | `001-profile-v2.png` | Wide stride, forward heel contact/toes up and trailing heel lift |

The [portable review](review-evidence/pose-check-v1/review.html) embeds its exact
original and candidate PNG bytes. The original is on the left, draft on the
right. Pose selection, mirroring and leg detail are diagnostic controls, not
a simulated gait. Approved standing000 is shown separately as an appearance
reference. Its approval does not approve these new poses.

`provenance-v1.json` records all three actual image-tool calls, ordered input
paths mapped to preserved bytes, exact prompt hashes and measurements. The
first001 draft overhung its canvas by2.75 HD pixels; it remains as the used
ancestor for the targeted forward-foot edit. Version2 fits without changing
the family0.1 scale. The edit moved the measured cap midpoint from705 to704
raw pixels despite an invariant prompt, so registration was remeasured.

The original references preserve all eight geometries. Their gray ground
shadows are not soles; their diagnostic palette is not verified original
executable color. Screen-space leg/foot observations are kept separate from
unverified anatomical left/right labels.

## Reproduction and verification

Use Pillow12.3.0 and the existing toolbox Python. In a fresh checkout, reproduce
the two candidate runtime exports from their saved recipes:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 3 --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/003-v1/recipe.json --output build/profile-walk/export003-v1
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/export.py --frame 1 --recipe art/cartoon/walk-pilot/profile-walk-v1/exports/001-v2/recipe.json --output build/profile-walk/export001-v2
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/build_review.py
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/check_review.py --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/profile-walk-v1/check_review.py --phase regression
```

The exporter refuses existing output directories. `record_generation.py` is
the original provenance capture helper and requires the recorded tool-cache
and input paths; it is not needed to reproduce the exports or the review.
`publish.py` uses this workstation's existing loopback server and verifies the
served HTML bytes. Opening the portable HTML directly needs no server.

| Verification | Result |
|---|---|
| Original reference preparation |2 smoke checks followed by8 witnessed damaged-input controls |
| Each selected export |3 smoke checks, then24 behavioral regressions and19 executed mutants; every mutant produced one named failure |
| Browser viewer |Smoke passed, then8 pose/detail/mirror combinations matched both panels' pixels; substituting standing000 for003 failed `canvas-candidate-003` |
| Review builder |Wrong003 PNG and recipe inputs each caused one named refusal; the previous review and restored inputs stayed byte-identical |
| Human acceptance |Pending for these two poses; no motion or scene acceptance implied |

See [EXPORT.md](EXPORT.md) for filter/registration math, pinned identities,
fit limits, reproduction commands and output hashes. Browser comparisons allow
two channel levels for browser/Pillow alpha rounding. Screenshots show the
actual tested page. No native capture was performed in this static checkpoint.

The [route plan](route-plan.md) identifies F-to-C and C-to-A as the later native
motion clips, with exact original table orders, real transitions and separate
ordinary003 boundary probes. Complete the six remaining poses only after this
visual checkpoint. Review the full motion and scene before promoting all eight
as one family; preserve the existing32 production assets exactly.
