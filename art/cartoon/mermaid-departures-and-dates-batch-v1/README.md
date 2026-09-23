# Mermaid departure and date drawings

The user authorized the next several dozen drawings after approving the previous corrections. This batch contains 72 distinct source drawings. Each new drawing uses one built-in image generation request with its exact original as the pose reference and established cartoon artwork as the style reference.

All 72 selected slots now have returned drawings. Open [the review gallery](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review.html) to compare each against its original. Appearance approval is pending.

The user corrected the departure animal's identity: it is the established gray shark with razor teeth and a sneaky demeanor. The gallery now selects [27 shark corrections](http://127.0.0.1:8941/shark-identity-corrections-v1/review.html), retaining the other 45 selected drawings. shark-correction-overrides.json supplies the latest correction versions and notes after historical group notes are merged. Earlier dolphin drawings remain preserved as superseded candidates.

| Resource | Selected original frames | New drawings |
| --- | --- | ---: |
| SLEVEJM1 | 000-010 | 11 |
| SLEVEJM2 | 000-005, 009-020 | 18 |
| SLEVEJM3 | 000-007 | 8 |
| SMDATE1 | 000-016 | 17 |
| SMDATE6 | 000-006, 018-021, 027-028, 031 | 14 |
| SMDATE10 | 004-006 | 3 |
| SMDATE11 | 004 | 1 |

The built-in image generator was used once per distinct request, with additional targeted correction requests where needed. Exact prompts and reference paths are in generation/RESOURCE/FRAME-vN-request.json. Returned PNGs and their hash records sit beside each request. Each review card links the selected request and generation record. Superseded versions remain available; selected-versions.json defines the current candidates.

The source record pins the exact originals. The duplicate audit records exclusions and earlier coverage. Inspection notes identify partial components and specific pose details to compare. Production fitting, component placement and native motion checks remain deferred under the established art workflow.
