# Original ordinary-turn references

Status: ORIGINAL-ONLY PREPARATION. This pack prepares supplied-original 003, 009, 010 and 012 geometry only. It contains no generated turn artwork and grants no appearance, native motion or production approval. Each per-frame source record binds exact native and nearest-neighbor 8x PNG copies, original index/RGBA metadata, registration measurements and the existing compiled trace. The commercial RESOURCE files and original executable were not reread here.

Original index 0 is transparent. Visible colors use the port dump diagnostic palette, not a verified original-executable display palette. Original gray ground shadows contribute to the canvas and visible bounds; neither is a foot-contact measurement. Directions and screen-side descriptions below come from original pixels. They do not assign obscured anatomical limb identity.

## Changes from the corresponding waiting poses

| Original pair | Facing and arm/hand difference | Leg/foot difference | Runtime canvas | Suggested cap target |
| --- | --- | --- | --- | --- |
| 000 to 003 | Same strict screen-right profile. Visible arm/hand drops from the waist toward the side of the shorts; retain far-side occlusion. | One bent leg/foot is raised behind the longer planted profile leg. This is a stepping pose, not the overlapping two-planted-foot wait. | 80x152 | [54,0.25] |
| 017 to 009 | Same front-oblique screen-right view. Both hands lower away from the pockets, with the arms looser at the sides. | Staggered, bent-leg stepping pose instead of the relaxed separated waiting stance. Preserve the source foot angle and overlap rather than transferring 017 feet unchanged. | 80x148 | [54,0.25] |
| 016 to 010 | Same direct front view. Hands lower to the sides instead of resting at the waist with elbows out. | The screen-right leg is visibly bent and lifted; the screen-left leg extends toward the lower foot. These are source-image positions, not anatomical left/right labels. | 80x148 | [35,0.25] |
| 015 to 012 | Same direct rear view, face hidden. Hands sit lower and farther from the waist; arms remain slightly bent but leave the tight hands-at-waist pose. | Asymmetric stepping stance instead of the relaxed rear wait. Read the back of calves and feet from original 012, without inventing a frontal toe row. | 80x146 | [39,0.25] |

The native canvases are respectively 40x76, 40x74, 40x74 and 40x73. Original row-0 pixel-edge spans are x[26,28), x[25,29), x[15,20) and x[18,21). Each cap X target is the midpoint of its own span doubled. Y=0.25 is the inherited filter margin, not an original anatomical or engine anchor. The prospective generated-art scale remains uniform 1/10.

Do not blindly reuse a waiting export transform: 009 is two HD pixels shorter than 017 and its cap target is four HD pixels farther left; 010 has a wider native canvas than 016; 012's cap target is four HD pixels farther right than 015. Native draw origins also vary. Foot continuity must be judged after each fixed registration and actual draw origin, including the encoded mirroring.

## Encoded directions

At each of nodes A through F, the ordinary-turn block uses 010 for heading 0/S; 009 mirrored for 1/SW and unflipped for 7/SE; 003 mirrored for 2/W and unflipped for 6/E; and 012 unflipped for 4/N. Existing 023 supplies the two rear-oblique headings 3/NW and 5/NE.

The stored same-spot A-turn cases use waiting-family sprites, not these four ordinary-turn sprites. Matching compiled moving-route draws use six port ticks (120ms at 20ms/tick). Table rows, observed compiled draws and static script sites are distinct evidence; one does not establish approval of the others.

## Motion dependencies and batch boundary

`dependency-summary.json` provides the machine-readable counts, input hashes, route sequences, evidence links and recommended batch boundary. `dependencies.json` retains the complete relevant route frame sequences, selected source rows and matching compiled draws. It also retains original and port static TTM sites separately, including command offsets, tags, bitmap slots and preceding linear delay observations.

| Frame | Direct route-table rows / groups | Ordinary-turn rows | Static TTM sites, port / original | Consequence |
| --- | --- | --- | --- | --- |
| 003 | 19 / 11 | 12 | 37 / 37 | Repeated 002-003-004 transitions are part of profile walking 001-008. Promoting only 003 would insert a Cartoon drawing into the remaining HD profile cycle. |
| 009 | 4 / 3 | 12 | 5 / 5 | Direct route uses are C-to-B twice, D-to-F once and E-to-C once. The rows bridge 009-to-028, 027-to-009 and 025-to-009-to-003. |
| 010 | 0 / 0 | 6 | 8 / 8 | Compiled moving routes insert it as an ordinary turn. MJDIVE tag 2 contains five static sites, so the water-exit motion needs tracing before treating 010 as an isolated replacement. |
| 012 | 0 / 0 | 6 | 2 / 2 | Compiled A-to-E inserts it. Static script sites are GJVIS5 tag 10 and SJLEAVES tag 3; the latter has the already-recorded original/port delay-command difference. |

003's direct route groups are A-to-F(1), A-to-C(3), A-to-B(1), C-to-A(3), C-to-E(1), C-to-F(1), D-to-E(1), E-to-C(2), E-to-D(2), F-to-A(2) and F-to-C(2). These are table occurrences, not runtime frequencies. The stored compiled cases contain 003 in A-to-E(5) and E-to-F(4); 009 in A-to-E(1), C-to-B(2) and E-to-F(2); 010 in A-to-E(1) and E-to-F(1); and 012 in A-to-E(1). Compiled routes can traverse multiple encoded route groups.

The five 009 script sites are MJFIRE tags 140 and 139, GJDIVE tag 13, MJDIVE tag 1 and GJGULIVR tag 11. The eight 010 sites are SJMSSGE tag 28, MJCOCO1 tag 24, MJDIVE tag 2 five times and MJCOCO tag 23. 003's 37 sites are listed individually in `dependencies.json` rather than abbreviated as scene coverage.

Complete and approve the standing-direction family 000/015/016/017 with the existing approved 018 as its own batch. Leave ordinary-turn production sprites unchanged for that delivery. Pair eventual 003 work with the full 001-008 profile walk, then review 009/010/012 in their actual route and script contexts. An eight-new-drawing wait/turn list is not a self-contained complete motion family.

Static TTM attribution follows linear decoded command order, including bitmap-slot bindings; it does not execute every branch or prove a complete scene. Original and port TTM records are separate, especially for SJLEAVES. No full front-walking sequence is inferred merely from 010's repeated script sites.

## Appearance references and approval boundary

At this preparation checkpoint, the new 000/015 standing drawings remain pending human review and are not approval inputs for ordinary turns. Their original waiting pixels are comparison references only. Accepted front identity is available from:

- 016: `art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/016-toe-fit-v2.png`, SHA-256 `d89066217905e3e1a2fa509f1f9d6cfecbb084cb7fba50844a32a9d8c181c052`. `016-key-v1/approval-v1.json` accepts the shown front waiting turns, with its stated exclusions.
- 017: `art/cartoon/walk-pilot/front-arrival-v1/017-foot-depth-v3.png`, SHA-256 `d1fab951de823fc5612860a5fac48bd586a533177a3e5e26d2605f41d4272c1d`. `front-arrival-v1/approval017-v1.json` accepts that appearance and the shown E-to-A arrival, with its stated exclusions.

These accepted drawings supply character identity, beard, cap and shorts treatment. They do not replace original turn geometry or grant approval to new poses, unseen story contexts or production promotion.
