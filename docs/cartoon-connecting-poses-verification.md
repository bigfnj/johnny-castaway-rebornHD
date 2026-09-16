# Cartoon connecting poses, colors and foot contact

The approved artwork is integrated into the 43-asset production package. Local
delivery checks passed. Platform CI, main integration and the final audit will
be recorded below when complete.

The user accepted the connecting poses, selected the lighter 029 skin reference,
approved the matched colors, and accepted the revised 018 foot with "much better
proceed". The new
[foot approval](../art/cartoon/standing018-proportions-v1/human-foot-approval-v1.json)
binds the final reviewed artwork. It does not claim which individual clip the
user viewed or complete original-executable/story parity.

## Selected artwork

The combined pack contains 28 Johnny poses and 15 unchanged island assets.
Connecting 009/010/012 are new slots. The existing walking and standing poses get
the approved lighter skin palette; 029 remains byte-identical. Standing 018 also
receives the separately reviewed longer torso/lower shorts and smaller-foot
correction. This delivery includes geometry and color changes.

The original 28-pose color bundle stays frozen, including its superseded 018.
Production selects 27 outputs from that bundle and the new 018 from
`standing018-proportions-v1/color/evidence-foot-v5`. The latter's color step
preserves its own new alpha exactly; image generation did not preserve all
upper-body/shorts bytes. Its fixed bounds and actual transitions were checked.

| Review | Evidence |
|---|---|
| Connecting geometry | Selected 009, 010-v5 and 012 exports; six native clips with 288 displays, 14 scoped new-pose displays and 274 identical others. Poses were accepted before the palette correction. |
| Skin palette | Canonical 029 RGB 252,148,88. Twenty-eight corrected sprites checked against 222 independent material points and 84 regions; 14 negative controls, including executed cap/gain changes, and exact replay. Eight native clips contain 298 displays, 286 skin-mask-only changes and 12 identical 029 displays. |
| Original 018 contact | Supplied-original geometry at the exact mirrored origin confirms the previous foot ended 5 HD pixels higher. Diagnostic colors and the original gray contact shadow are distinguished from original-executable presentation. |
| Selected foot-v5 | Fixed scale 0.1 and 64x154 canvas; smaller/larger sole bounds 144.6/146.1 HD. Three export smoke checks and 20 regressions. Fresh color annotations and 14 negative controls preserve new alpha and protected materials. |
| Final native motion | Front departure, same-origin 023 arrival and mirrored 022 arrival all passed smoke, full comparison and fresh repeat. Across 164 displays, 28 changes stay inside 018 and 136 other displays remain identical. Exact timing and placement are retained. |
| Browser | Three original/previous/corrected stills at one fixed camera, plus synchronized previous/corrected motion. Crop/link and three-clip regressions, four focused source/view controls and two stale-HTML controls passed; 208 served files matched. |

The accepted private package is
`561edb2c9b4b4857b723af1505ce8d2654616aae2942325389604a4d88804521`.
Its selected 018 PNG is
`5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f`.
All 2,593 other private-package members match the prior reviewed 018-v2 package.
The [integration addendum](../art/cartoon/standing018-proportions-v1/preintegration-foot-v5-addendum.json)
retains the full composition/source audit.

## Integration and delivery

The maintained pack builder produced production ZIP
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.
Independent comparison checked every one of its 2,594 member payloads against the
approved private package. ZIP container bytes differ, but all named payloads
match. Relative to the prior production package, there are three added members,
24 changed Johnny PNGs and 2,567 unchanged existing members. Nothing was removed.
All 2,550 original archive members and all 15 island assets remain exact.

The [combined acceptance](../art/cartoon/skin-tone-v1/production-acceptance.json)
accepts 28 Johnny sprites and inherits only the 15 island approvals. Pilot
replacement history includes 024-029; unchanged 029 has new review/recipe
provenance. Source replay reconstructs the selected raw ancestry, exports and
color corrections before comparison with the retained runtime PNGs.

| Delivery check | Result |
|---|---|
| Package and source replay | All 43 accepted slots validate. Raw ancestry, color replay, fixed 018 export and complete package comparison pass. A corrupted 018 produces exactly one named refusal; an executed copy with the guard removed accepts that same corruption, and the restored helper passes the clean candidate. [Evidence](../art/cartoon/skin-tone-v1/integration-v1/evidence.json). |
| Maintained authoring | Nine smoke cases pass before regression suites: inventory 11 cases with two explicit Windows symlink-privilege skips, history 22, metadata 60, catalog 63 and art tools 20. Both generated catalogs reproduce. Windows hardlink controls pass. [Evidence](../art/cartoon/skin-tone-v1/integration-v1/authoring-v1/evidence.json). |
| Windows full gate | Fresh Release build has no compiler warnings. All smoke stages pass before regressions; 2,452 golden files match. Source and deployed archives both match the production SHA. All 32 retained renderer captures are complete. The inactive desktop preserves the user's input desktop. [Evidence](../art/cartoon/skin-tone-v1/integration-v1/windows-v1/evidence.json). |
| Checkout preservation | Removing the standing-source `-text` rule changes the named prompt bytes in an actual autocrlf checkout; restoring it preserves the recorded SHA. Frozen whitespace-control fixtures retain their exact bytes through narrowly scoped attributes. |
| Platform CI and main | Pending branch CI and authorized merge, followed by a fresh audit of main. |

No runtime C, platform backend, maintained authoring tool or test implementation
changes are part of this delivery. Cartoon remains partial while other scenery,
story uses and alternate states receive art review. Historical README status
snapshots and earlier approvals stay frozen; this document describes the current
delivery.

## Decisions

| Decision | Reason |
|---|---|
| Keep the chosen shorts and torso | The user accepted them while identifying the remaining foot gap separately. |
| Generate the foot correction; normalize colors in code | Image generation supplies anatomy. The user explicitly authorized code color correction, with geometry and alpha protected during that step. |
| Keep fixed placement and actual timing | Moving the whole sprite or smoothing playback would hide the contact/transition issue. |
| Inherit only 15 island approvals | Every Johnny ledger entry now points to the new combined acceptance, including 029 whose pixels stay unchanged. Historical approvals remain ancestry. |
| Keep scene parity separate | Native walking coverage and static TTM references do not prove all story branches or original-binary behavior. |
