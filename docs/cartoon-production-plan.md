# Cartoon production: catalog and walking expansion

Current workflow: the user requested [art construction first, bulk verification later](cartoon-art-build-workflow.md) on 2026-09-17. That instruction supersedes the per-family test and audit cadence documented below. Preserve visual approvals and source records as each family is completed; run full smoke, regression and final code audit at the combined delivery milestone.

The user approved this bounded start on 2026-09-15: establish the production
catalog, then expand Johnny's walking directions before undertaking the full
application. Work starts from `0f7d7fd` on `art/cartoon-production-foundation`.

Current delivery: the [cloud group](cartoon-clouds-verification.md) brings
production to63 accepted PNGs. The original scope and phase table below remain
the workflow history; coverage advances are recorded in the linked deliveries.

## Scope and sequence

| Phase | Deliverable | Completion evidence |
|---|---|---|
| Production catalog | Every shipped BMP/SCR slot, its resource family, coverage, reference identity, duplicate relationship and blank status | Smoke checks followed by regression tests; executed mutations for new checks; deterministic regeneration |
| Continuous checks | Existing pilot metadata and the new catalog checked once in Linux CI | Run the actual CI commands locally and demonstrate failures on damaged inputs |
| Original walking reference | All 36 JOHNWALK frames, actual route membership, flip convention and original source provenance | Compare source table records and supplied-original decoded pixels; preserve coordinate mappings |
| Next walking family | A new directional key followed by its complete motion family | Human direction/identity review before expansion, then motion and actual scene review |
| Walking completion | Remaining cycles, turns and waiting poses required by the original walk table | Each family passes export smoke and regression checks before human review; transitions also reviewed |
| Delivery | Accepted assets only, updated evidence and coverage, merged work and audit | Preserve previous art; native smoke then regression; inspect the final merged code and document remaining issues |

The full catalog is preparation, not permission to generate every resource at
once. The original 21 approved assets were the starting baseline. The rear walk,
its arrival, and the completed standing family now bring production coverage to
32. The approved [profile-walk batch](cartoon-profile-walk-plan.md) adds eight
poses together and brings the pack to 40 assets.
Drafts have separate source records and do not acquire acceptance from similar
poses, shared bytes or approval of a different direction.

## Reference and implementation choices

| Decision | Reason |
|---|---|
| Add a complete production catalog beside the existing pilot metadata | Preserve the original-first pilot evidence and its historical approval scopes while giving future work a complete slot ledger |
| Start with resource families; refine walking groups from source records | Filenames and adjacent indices alone do not prove a complete animation family |
| Treat HD PNGs as proxies | The supplied original and bundled resources have documented differences; duplicate or blank HD bytes are not proof about original anatomy |
| Preserve every runtime slot | Duplicate and blank slots still have paths required by scripts and the pack contract |
| Use the approved Calm focus key for walking identity | The new direction must retain Johnny's beard, brimmed cap, shorts and proportions; other actions will retain their own expressions |
| Produce one new directional key before expanding that family | A rear or side view can reveal a design mismatch that a correct front-facing character cannot settle |
| Retain original coordinates, flips, timing and draw order | Artwork changes must not conceal pose errors by changing the engine's route |
| Use one documented drawing scale within each coherent family | Per-frame silhouette fitting previously caused body popping and sideways motion |
| Keep PNG production separate from code-drawn effects | Palette-driven lines, circles, rectangles, pixels and fades require their own scene review during later coverage work |

## Review contract

Use the original decoded frame to establish pose geometry and the approved
Cartoon key to establish identity. Original colors shown using the port's
diagnostic dump palette are not verified original-executable colors. Store the
exact inputs, prompts, returned images, registration recipe and review scope.

A directional-key approval establishes appearance from that angle. It does not
approve unseen steps. A motion approval covers the displayed images and
sequence. Runtime acceptance additionally requires actual canvas fit and an
in-scene review, including background overlap and transitions.

Technical exports may apply documented uniform resampling and translation.
Artistic changes use image generation. Preserve alpha and inspect composited
edges. Do not warp limbs, paint over feet, invent in-between frames or change
the original walk table to disguise a mismatch.

## Verification and remaining scope

During art construction, use lightweight export and preview checks. Full smoke
checks, then regressions and the final audit are deferred to the bulk delivery
under the current workflow. Test actual engine or tooling changes according to
their scope; do not run the entire suite for every approved drawing. Historical
test and approval records below retain their original scope.

The rear-three-quarter key was approved with "looks good yes". Its complete
six-pose walk was subsequently approved in the native island review with
"Yes, keep this walk". The user then approved standing arrival 018 with
"nailed it, proceed", completing that displayed rear arrival in Cartoon.
The front walk refresh and all standing directions have since been accepted,
with explicit inheritance of earlier approvals. Profile walking 001-008, including
shared ordinary-turn 003, is now approved in both native directions and its
reviewed ordinary departure contexts. Ordinary connecting poses009/010/012
were subsequently [accepted and integrated](cartoon-connecting-poses-verification.md),
including the lighter skin palette and corrected018 contact. All28 delivered
Johnny drawings retain those scoped approvals.
Other placements and story uses of the standing art remain outside its reviewed
arrival/direction-ring contexts. Seasonal decorations and the high/low-tide
environment groups and ordinary moving clouds are now delivered. NIGHT and the
remaining ordinary daytime oceans have [visual approval and saved exports](../art/cartoon/environment-v1/README.md), pending bulk integration. Four [coconut orientations](../art/cartoon/coconuts-v1/README.md) have scoped appearance approval; their shadow drafts and runtime fit remain pending. The user approved the entire [24-drawing prop batch](../art/cartoon/props-batch-v1/README.md) with "all approved, nice job, please continue": one boat, five raft construction pieces, fifteen sandcastle stages/effects and three idea symbols. These selected drawings await bulk sizing and integration, separately from the63 production assets. The next batch covers all37 TANKER, GJPROW and SHIPS slots in one review. Other characters, action scenes and code-drawn
effects remain later work. The [ship batch](../art/cartoon/ships-batch-v1/README.md) contains 33 new drawings and four one-pixel original slots retained unchanged after direct inspection. The user approved the 19 non-tanker drawings; all 14 TANKER drawings await the requested [motion review](../art/cartoon/tanker-motion-v1/README.md), which replays the 76 decoded source draws with their coordinates, repeats and flips. This is an isolated comparison at port nominal timing, not a native capture. Campfire resource FIRE1000-027 is queued as the next 28-drawing group. Existing engine maintenance findings stay
in [BACKLOG.md](../BACKLOG.md); address a reproduced blocker when its affected
scene enters review.

The workflow builds on [the original lessons](art-style-learnings.md),
[the Calm focus addendum](art-style-learnings-calm-focus.md), and
[the approved runtime record](../art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json).
