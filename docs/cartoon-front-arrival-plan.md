# Cartoon arrival and wait/turn batch

Branch `art/cartoon-front-arrival-family` starts at main `707a20b`.
The complete accepted front and rear walks remain unchanged. The new batch
targets the eight missing wait/turn slots: 000,003,009,010,012,015,016,017.
Existing Cartoon018 and023 complete the ten unique table assets.

## Sequence and review checkpoints

| Stage | Work and review |
|---|---|
| Trace | Verify original walk rows and actual C route behavior; separate shared story uses from the walk-table family. Completed: 489 rows, 116 compiled cases and all41 original/41 port TTM identities. |
| Front arrival017 | Approved: original pose plus Calm focus identity; static/fit checks and the actual E-to-A walk into its mirrored standing pose. User: "looks good, proceed". |
| Front waiting turn | Add016 and review both same-spot1-to7 and7-to1 turns with017. Preserve the original120ms intermediate frames and1600ms final hold. |
| Remaining waiting directions | Add000 and015, retaining018. Review original heading order, both reflected uses, stance and continuity. |
| Ordinary turning poses | Add003,009,010,012, retaining023. Review actual departure/waypoint paths, with clearly disclosed HD walking fallback outside the accepted front/rear cycles. |
| Integration | Promote only reviewed assets with explicit inherited approvals, reproducible export recipes, unchanged prior PNGs and smoke before regression. Merge after the agreed family review; run the post-merge audit and update BACKLOG. |

Immediate E-to-A uses23 walking positions, then mirrored017 at logical
origin(293,243), following027 at(300,242). Arrival hold is1600ms. Same-spot
heading1-to7 uses016 for120ms,017 for120ms, then017 for1600ms;7-to1 uses016
for120ms then mirrored017 for1600ms. These are actual C observations rather
than invented in-between animation.

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

The [authoring bundle](../art/cartoon/walk-pilot/front-arrival-v1/README.md)
retains prompts, used outputs, original references and technical evidence.
