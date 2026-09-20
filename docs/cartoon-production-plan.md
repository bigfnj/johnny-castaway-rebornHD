# Cartoon production: catalog and walking expansion

Current workflow: the user requested [art construction first, bulk verification later](cartoon-art-build-workflow.md) on 2026-09-17. That instruction supersedes the per-family test and audit cadence documented below. Preserve visual approvals and source records as each family is completed; run full smoke, regression and final code audit at the combined delivery milestone.

The default new-art review size is now 60-72 drawings, per the user's 2026-09-19 instruction to deliver five or six dozen per run. Target about 66 where complete families fit. Keep targeted corrections separate from that count and use parallel work across compatible resource groups.

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
remaining ordinary daytime oceans have [visual approval and saved exports](../art/cartoon/environment-v1/README.md), pending bulk integration. Four [coconut orientations](../art/cartoon/coconuts-v1/README.md) have scoped appearance approval; their shadow drafts and runtime fit remain pending. The user approved the entire [24-drawing prop batch](../art/cartoon/props-batch-v1/README.md) with "all approved, nice job, please continue": one boat, five raft construction pieces, fifteen sandcastle stages/effects and three idea symbols. These selected drawings await bulk sizing and integration, separately from the 63 production assets.

The subsequent [37-slot ship batch](../art/cartoon/ships-batch-v1/README.md) contains 33 new drawings and four one-pixel original slots retained unchanged after direct inspection. The user approved the 19 non-tanker drawings, then separately approved removal of the long bar in TANKER000-002. On 2026-09-18, "approved, continue please" at the [third motion review](../art/cartoon/tanker-motion-v3/README.md) approved the appearance and isolated source-replay rotation of all 14 selected tanker views: 11 updated 000-009/012 and unchanged 010/011/013. The [acceptance record](../art/cartoon/tanker-motion-v3/acceptance/appearance-rotation-v1.json) binds the exact selections, shown page and 76 decoded source draws with their coordinates, repeats and flips. Earlier reviews retain their original scope. This is an isolated comparison at port nominal timing, not native integration approval; final export sizing, registration, scene motion, joining edges and bulk smoke/regression remain pending.

The user approved the complete 28-drawing [FIRE1.BMP000-027 group](../art/cartoon/fire-v1/README.md) on 2026-09-18 with "excellent, approved". [Acceptance](../art/cartoon/fire-v1/acceptance/appearance-v1.json) binds all selected raw versions and the shown gallery with five isolated source-derived phase comparisons. The wood/ember stages, flames, smoke and fire-pop graphic retain separate raw outputs and prompts. Final native registration, complete dying-fire/ember scenes and Johnny's interactions remain bulk integration work. Other characters, action scenes and code-drawn effects remain later work. Existing engine maintenance findings stay in [BACKLOG.md](../BACKLOG.md); address a reproduced blocker when its affected scene enters review.

The next [25-drawing prop review](../art/cartoon/campfire-props-v1/README.md) covers nine fish/tail drawings, nine boot/toe drawings, five squid drawings and a separate raft/paddle. It awaits appearance approval. Three FIRE2 marker slots remain exact originals; two hand/grip overlays stay deferred with Johnny's action work. The original inventory classification needs that correction during regeneration. FIRE5 source variants have no proven TTM load. Full hand/mouth/raft joins, native registration and motion remain bulk integration work.

The user's 2026-09-18 review rejected 13 facing/eye interpretations in that group. [The direction-correction review](../art/cartoon/campfire-props-direction-v2/README.md) revises fish 012/013/014, boots 005/009/015/019/022 and all five squid drawings, showing originals and earlier drafts beside the replacements. It awaits human acceptance. The other 12 drawings remain unchanged without implied approval; preserve the initial review as rejected-pose history, not pose authority for future packs.

The subsequent [six-drawing refinement](../art/cartoon/campfire-props-bend-v3/README.md) addresses the marked sole/cuff bends in 005/022, upper eye placement in 006, and rounded head/appendage corrections in 021/024/FIRE5 000. User annotations are retained with the generation records. Earlier comparison pages remain intact; unmentioned frames have no new acceptance implied by this request. Full scene testing remains deferred.

The latest [005/022 angle review](../art/cartoon/boot-angle-v4/README.md) follows the user's manually rotated boot cutouts. Preserve the natural internal bend while matching the indicated tilt. The page compares the source, the user cutout and the new output; earlier pose reviews remain historical evidence, not acceptance.

The user approved those two selected boot drawings with "perfect" and asked to proceed with 36-48 drawings per review. [The scoped acceptance](../art/cartoon/boot-angle-v4/acceptance/appearance-v1.json) binds 005 v2 and 022 v2; it does not approve unseen or unmentioned campfire drawings. The next [42-drawing wildlife batch](../art/cartoon/gulls-fish-batch-v1/README.md) covers complete GJGULL1 and LILFISH families, with shared gull/nest style references and per-frame source references. All remain drafts until reviewed.

On 2026-09-19, the user said "approved, lets start the next batch" at the [shark fin-correction review](../art/cartoon/shark-fin-corrections-v2/README.md). Its [acceptance record](../art/cartoon/shark-fin-corrections-v2/acceptance/appearance-v1.json) approves only GJFFFOOD026 v1 and 035 v1 appearance. The other 37 drawings in the earlier shark gallery gain no implied approval. Native registration, water layering, motion and bulk integration remain pending. The next [39-drawing GJGULL2 batch](../art/cartoon/gull-clothes-batch-v1/README.md) covers clothes-carrying, preening and settling, with source markers 006-015 preserved. Its original-versus-Cartoon gallery awaits appearance review; full testing remains deferred.

The user then requested [ten GJGULL2 corrections](../art/cartoon/gull-clothes-corrections-v2/README.md). Five gull drawings are rear views with hidden eyes, four clothing piles require black belts and supported folds, and stick 000 needs one continuous curve. The comparison keeps originals and earlier drafts visible beside the revised art. On 2026-09-19, "approved, lets start on the next set" approved only selected 000 v2 and 004/016/034/037/040/045/046/047/048 v1, bound in [scoped acceptance](../art/cartoon/gull-clothes-corrections-v2/acceptance/appearance-v1.json). The other 29 drawings gain no approval from that response. Native integration and full tests remain deferred.

The next [36-drawing marine set](../art/cartoon/marine-scenes-batch-v1/README.md) contains 17 GJCATCH2 octopus poses, 12 GJDIVE animal judges with blank scorecards and seven SPLASH effects. Each exact original remains visible beside the new art. Starfish, crab, round fish and gull are separate judge designs; numeric score overlays and shadow planes are excluded from the drawing count. Appearance review is pending, with native registration and bulk testing deferred.

The user approved the [four judge corrections](../art/cartoon/marine-judges-corrections-v2/acceptance/appearance-v1.json) on 2026-09-19: GJDIVE 025 v1 restores the partly hidden far eye, and 027 v2 with 028/029 v1 show a chest-forward gull using both wings to hold its card. The rear feather fan is the tail. These source interpretations supersede the earlier notes. The other 32 marine drawings gain no implied approval. Native integration and full testing remain deferred.

The next [64-drawing fishing, prop and aircraft review](../art/cartoon/fishing-and-props-batch-v1/README.md) follows the new 60-72 default. It contains 42 fishing catches, rotating props, rods and water effects, plus 22 aircraft, flag and associated effect drawings. Exact original references determine orientation and visible anatomy. Appearance approval, native canvas registration and bulk smoke tests remain separate steps.

The subsequent [fish-scene and flag correction review](../art/cartoon/fishing-scene-and-flag-v2/README.md) addresses the user's request to see MJFISH3 008-010 in the fishing scene before changing their colors. Their Cartoon drawings remain unchanged. GJBIPLAN 021 now depicts the long cloth from 022 hanging freely from its upper connection. These targeted changes do not imply approval of the remaining batch or completion of bulk integration.

The workflow builds on [the original lessons](art-style-learnings.md),
[the Calm focus addendum](art-style-learnings-calm-focus.md), and
[the approved runtime record](../art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json).
