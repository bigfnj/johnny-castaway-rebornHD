# Mermaid departure and date drawings

The user authorized the next several dozen drawings after approving the previous corrections. This batch contains 72 distinct source drawings. Each new drawing uses one built-in image generation request with its exact original as the pose reference and established cartoon artwork as the style reference.

On September 25, 2026, the user approved SLEVEJM2 009 v8 and SLEVEJM3 004 Eye A v7 with "these two are approved" and a screenshot identifying those cards. Both are now selected and appearance approved. The exact approval and hashes of the two PNGs, requests and generation records are saved in [the acceptance record](acceptance/appearance-round5-2026-09-25.json). This approval covers those two images only; production integration and native motion remain deferred.

All 72 selected slots have returned drawings. The root [focused six-card round 5 review](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review.html) shows the two approved selections and four unselected SLEVEJM3 004 alternatives, Eyes B through E, v8 through v11. The [prior two-card review](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review-round4.html), [prior eight-card review](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review-round3.html), and [full 72-frame archive](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review-full.html) remain available. The other 70 selected drawings in this batch still await appearance approval.

Before the September 25 approval, the round 5 exact verifier proved one selected change, 71 unchanged selections, and five complete candidate output, request, and generation-record triples. That correction pass left SLEVEJM3 004 at v6 for the user's choice; the acceptance above selects Eye A v7.

Browser validation for the round 5 review loaded exactly six focused cards, all 12 cartoon and original canvases, and all 12 request and record links without page, request, HTTP, console, or canvas errors. The forced seventh-card mutation failed on the intended count and exact-key checks. The full archive loaded 72 cards and 144 nonblank canvases. See `browser-review-round5-focused.json`, `browser-review-round5-focused-negative-control.json`, and `browser-review-round5-full-archive.json`.

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
