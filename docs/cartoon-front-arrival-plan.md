# Cartoon arrival and standing family

Branch `art/cartoon-front-arrival-family` starts at main `707a20b`.
The complete accepted front and rear walks remain unchanged. This delivery adds
the four missing standing slots: 000,015,016,017. Existing Cartoon018 completes
the five unique drawings used by all eight standing directions.

The initial scope included all eight missing wait/turn slots. The complete
dependency trace showed003 recurring inside the HD profile cycle001-008.
Promoting it alone would mix styles within that cycle. Ordinary turns003,009,
010,012 are therefore deferred to a complete profile-walk/context batch;
their supplied-original references and dependency records are preserved, with
no new artwork generated or approved. Existing Cartoon023 remains unchanged.

## Sequence and review checkpoints

| Stage | Work and review |
|---|---|
| Trace | Verify original walk rows and actual C route behavior; separate shared story uses from the walk-table family. Completed: 489 rows, 116 compiled cases and all41 original/41 port TTM identities. |
| Front arrival017 | Approved: original pose plus Calm focus identity; static/fit checks and the actual E-to-A walk into its mirrored standing pose. User: "looks good, proceed". |
| Front waiting turn | Approved:016 exported and native-checked in both same-spot1-to7 and7-to1 turns with017. User: "Yes, keep this turn" at front-turn016-v1. Preserve the original120ms intermediate frames and1600ms final hold. |
| Remaining waiting directions | Approved with "excellent, proceed" at standing-ring-v1:000/015 alongside016/017/018 through all eight headings in both native orders. Export and native smoke/regression passed; original placement, reflections and timing are retained. |
| Deferred ordinary turns | Preserve original-only003,009,010,012 preparation. Begin the next batch with complete001-008 profile dependencies before generating shared003; then review009/010/012 in actual departure/waypoint and story contexts. |
| Integration | Promote only reviewed assets with explicit inherited approvals, reproducible export recipes, unchanged prior PNGs and smoke before regression. Merge after the agreed family review; run the post-merge audit and update BACKLOG. |

Immediate E-to-A uses23 walking positions, then mirrored017 at logical
origin(293,243), following027 at(300,242). Arrival hold is1600ms. Same-spot
heading1-to7 uses016 for120ms,017 for120ms, then017 for1600ms;7-to1 uses016
for120ms then mirrored017 for1600ms. These are actual C observations rather
than invented in-between animation. The complete same-spot direction-ring
diagnostic additionally exposes an existing scheduler asymmetry: its decreasing
order lasts13880ms and increasing order1080ms in captured nominal wait requests.
The preview preserves those native times and defaults to the longer direction.
This art delivery does not change engine timing; comparison against the
windowed original is recorded separately in BACKLOG.md.

017 also occurs in31 static TTM draws across eight resources, including17 in
SJLEAVES. Walk-family review does not approve those story interactions. Preserve
that remaining coverage in the backlog rather than equating PNG coverage with
complete scene parity.

## Decisions

| Decision | Basis |
|---|---|
| Start with017 | It is the visible HD interruption immediately following the newly approved front walk. |
| Generate stored screen-right orientation | The native route mirrors017; a mirrored current-character reference avoids accidental double reflection. |
| Retain0.1 common scale and cap registration | Original017 is40x75; runtime80x150. Its top-row pixel-edge midpoint29 maps to58HD, with the inherited0.25HD filter margin vertically. |
| Correct excessive far-foot lift in generation | The first draft's projected colored-foot gap was about19.3HD versus6HD in the original. Measurement guides the edit but does not prove anatomical contact. No limb warp or independent per-pose scaling is used. |
| Human review before generating the remaining poses | This standing key establishes the new family's pose treatment; a valid PNG and matching hashes do not establish artistic acceptance. |
| Deliver the complete standing family before ordinary turns |003 has19 route-table rows across11 groups as well as12 turn rows. Its repeated profile-walk use requires review of001-008 together. The original-only dependency records distinguish route, turn and TTM occurrences. |
| Preserve timing findings separately from artwork approval | The first-terminal-pose scheduler behavior predates this branch. The direction-ring review preserves current timing; no original-binary parity or runtime correction is claimed. |

The [authoring bundle](../art/cartoon/walk-pilot/front-arrival-v1/README.md)
retains prompts, used outputs, original references and technical evidence.
