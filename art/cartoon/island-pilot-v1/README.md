# First layered Cartoon island pilot

The approved island concept has been translated into 15 independent runtime
assets: ocean, sand, palm trunk and canopy, shadow, cloud and nine high-tide wave
frames. The pilot combines those with the six unchanged approved walking poses.
The user approved the full scene with "approved, it looks great". The exact
21 assets and shown motion artifact are identified in [acceptance.json](acceptance.json).
The approved pack is integrated into `assets/scrantic_data.zip` as a partial
preview. [Production validation](review-evidence/production-validation.json)
records the final archive and executable hashes, exact candidate-frame parity,
and smoke followed by the golden regression.

Start with [the reusable image lessons](../../../docs/art-style-learnings.md).
The [scene plan](../island-concept-v1/implementation-plan.md) records fixed layer
geometry and the controlled daytime state. The three source bundles preserve
selected drawings, actual prompts and reference roles, rejected-attempt lessons,
uniform export transforms and exact output hashes:

| Bundle | Runtime assets | Review focus |
| --- | --- | --- |
| [Palm, sand and cloud](palm-sand-cloud/README.md) | 000, 012, 013, 015 | Rear ground crest, palm joint, cloud silhouette |
| [Ocean, shadow and center waves](ocean-shadow-center-waves/README.md) | OCEAN02, 014, 006-008 | Horizon, shadow contact, central shoreline |
| [Side waves](side-waves/README.md) | 003-005, 009-011 | Complete phase families, curve placement and overlap |

Each bundle can reproduce its selected PNGs into a new directory. These are
authoring records, not a production archive. The six accepted walking assets
retain their recorded hashes in
[the motion acceptance ledger](../walk-pilot/directional-cycle-v1/acceptance.json).

The normal 21-asset candidate passed native Windows smoke before the 2,452-file
golden regression and preserved all 2,550 original archive members. Actual D/E
palm routes were exercised separately through a native API driver. Review
evidence distinguishes those routes from the E-to-A diagnostic motion sequence.
Other oceans, tides, clouds, holidays and walking directions remain outside this
artwork selection; shared scenery also appears in fallback states.

The preserved [technical checkpoint](review-evidence/checkpoint.json) identifies
the native candidate reports, palm reproduction and mutation evidence, complete
Windows gate logs and Git byte-preservation proof. Those reports retain the
historical local paths used during validation; the bundled sources and exporters
above provide portable inputs for the next authoring session.

[Final gates](review-evidence/final-gates.json) passed under PowerShell 5.1 and 7.
The [fallback matrix](review-evidence/fallback-api-validation.json) exercised ten
states in both styles and five initialization/release cycles per style. That is
bounded lifecycle evidence, not proof that every engine path is leak-free.
The [gallery](review-evidence/fallback-state-comparison.png) shows the expected
mixture of Cartoon and HD where artwork coverage is incomplete.

| Decision | Reason and next step |
| --- | --- |
| Preserve the accepted character and six walk PNGs | Environment generation must not reopen approved identity or registration |
| Generate independent scene layers | Clouds, foam and foreground occlusion need their own runtime behavior |
| Use one fixed transform per wave family | Keep phase size consistent; judge curves in native motion |
| Preserve selected raw sources and used ancestors | Prompts alone cannot reproduce the same pixels |
| Keep concept and runtime acceptance separate | Both are now approved, with separate exact records and review scopes |
