# Cartoon standing family: delivery verification

This batch completes all eight standing directions with five Cartoon drawings:
new JOHNWALK000/015/016/017 and previously accepted018. The complete accepted
front024-029 and rear011/019-023 walking families remain unchanged. The style
remains a partial preview; ordinary turns, profile walking and most story art
still use fallback.

## Human decisions and scope

| Review | Decision and evidence |
| --- | --- |
| Front arrival017 | "looks good, proceed" after the actual23-position E-to-A front walk settles into mirrored017. The original origin shift and1600ms destination hold remain. |
| Front standing016 | "Yes, keep this turn" after both native front waiting turns with017. Its displayed foot geometry is accepted artistically, not asserted to match original anatomy exactly. |
| Remaining side000 and back015 | "excellent, proceed" at standing-ring-v1. The full eight-heading ring uses000/015 with approved016/017/018 in both native orders. The side pose is also reviewed reflected. |
| Delivery boundary | Ordinary003/009/010/012 are deferred.003 also repeats inside profile walking001-008; replacing it alone would mix styles within that cycle. Original-only references and route/TTM dependency records are preserved for the next batch. |
| Native timing | Preserve the source scheduler's different timing in the two adjacent-heading orders. Comparison against the windowed original is separate backlog work; this delivery changes no engine timing. |

The [authoring bundle](../art/cartoon/walk-pilot/front-arrival-v1/README.md)
retains exact prompts, ordered references, generated ancestors, raw images,
original poses, recipes and separate human responses. Earlier records keep
their original pending-at-capture wording. The new approvals append decisions
without rewriting historical evidence.

Story coverage remains separate. The retained original/port trace attributes
8 static000 draws,1 for015, none for016,31 for017 and1 for018. These are linear
script sites, not executed branches or approved scene contacts. BACKLOG keeps
their remaining review scope, including the known SJLEAVES delay distinction.

## Artwork and native evidence

All four drawings retain a common0.1 scale and explicit per-frame cap
registration into their original doubled canvases. No independent silhouette
fit or camera recentering conceals a transition.017 needed two generated
far-foot-depth corrections;016 needed a narrowly scoped toe-fit correction.
000 and015 fit on their initial generated passes. Original gray ground shadows
are not sole landmarks. The original diagnostic palette is not calibrated
original-executable color.

| Checkpoint | Verification |
| --- | --- |
|017 export |3 smoke checks,19 regressions and16 executed mutations. |
|016 export |3 smoke checks,22 regressions and18 executed mutations. The first oversized candidate is retained as a rejected fit. |
|000/015 shared export |Each frame passes3 smoke checks,23 regressions and19 executed mutations. Explicit frame identity and recipe matching retain the historical filtering for opaque, soft-alpha and transparent fixtures. |
| Native017 arrival |47 displays over4360ms of requested native waits.35 displays are identical;12 differ only within017. |
| Native016 front turns |18 displays in one direction,16 in the other. Only the two016 displays in each clip change; placement and timing match. |
| Native standing ring |Baseline smoke, full captures and fresh-process exact repeats pass. Candidate smoke precedes regression in both directions. Across130 displays per panel,81 are pixel-identical and49 differ only inside000/015 canvases. |
| Ring browser |Local smoke precedes checks of260 panel-display pixels/timestamps and all16 heading selections. Published smoke verifies148 served files before both-direction control/timing regression. No browser errors or failed requests were observed. |
| Ring negative controls |Unchanged recorded-capture replay passes. A changed timestamp and one changed approved016 pixel are rejected. The unchanged browser checker rejects a shifted heading mapping after smoke; publication refuses altered HTML. These are recorded-input/browser controls, not rebuilt engine mutations. |

The complete ring's decreasing order lasts13880ms across108 display records;
the increasing order lasts1080ms across22. These durations sum native requested
waits, not wall-clock playback measurements. The source scheduler starts with
a six-tick timer and initially stores the first `walkAnimate` result only in
delay. A first terminal80-tick pose therefore follows a different path from
a6-then80 transition. The review preserves those results, defaults to the
longer direction and offers direct heading selection. Source/table reachability
is documented in BACKLOG; no random-story reproduction or original-binary
timing equivalence is claimed.

The ring [evidence binder](../art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/review-evidence/native-v1/evidence.json)
has SHA256`825f8fb28544f58bdfcc0d396ea5025c58494dd46003805e60019ffa6ec26ed1`.
Its63 exact bound files were independently read back. Large captures and native
binaries remain local; the preserved instructions identify the inputs needed
for reconstruction. The accepted private32-asset archive is
`ee180c8b6aa1e07024132bae808fc4d2fcc136714dd12152468a3c9fc511aa2c`.

## Integration and delivery

The standard pack builder produced archive SHA256
`096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.
All2579 prior members retain their exact payloads. Only000/015/016/017 are added,
giving2583 total members and32 Cartoon assets. The runtime manifest, original
resources, HD art, earlier28 ledger rows and pilot-history declaration remain
unchanged. All2583 member payloads equal the reviewed private archive.

The first packaging attempt incorrectly required equality of entire ZIP files.
Member comparison passed, but the standard builder sorts Cartoon entries while
the private review appended them. That layout-only assertion failed and its
evidence is retained. The final package uses the standard builder; there is no
custom ZIP-envelope reconstruction. The production and private archive hashes
are recorded separately from their verified member equality.

All four annotated runtime recipes reproduce the reviewed PNG and padded bytes
under Pillow12.3.0. Package smoke validates32 assets before the complete member
regression. An executed copy with corrupted000 produces exactly one named
comparison failure and a witness identifying the helper that actually ran.
The corrupt scratch archive is removed; the approved candidate is unchanged.

All authoring smoke suites passed before regression: inventory3, history1,
historical pilot2 and full catalog3. Inventory regression ran11 controls with
2 explicit Windows symlink-privilege skips; the hardlink guard passed. History
passed22 checks, including its84-test future-promotion replay; pilot metadata
passed60, full catalog63 and art tools20. Both regenerated catalogs reproduce.
They report32 accepted slots,2369 pending and51 with supplied-original evidence;
historical pose facts remain unchanged. No maintained tool/test logic changed.

The independent [integration audit](../art/cartoon/walk-pilot/front-arrival-v1/review-evidence/integration-audit-v1.json)
checked all old ledger/archive entries, full private-candidate member equality,
four annotation-only recipes, all approvals,63 bound native ring files,
113 protected integration inputs and59 native source inputs. It found no
discrepancy. Its SHA256 is
`014996e4af77a1c45057be4cd87ab2d06925edcceb52e6751994c07d920c87f2`.

The final local Windows gate passed. [PR13](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/13)
merged feature head`edc4adc86b43d11e273a50cde5d6375f27ea1cdc` as main
`fecfdb3498ccd35fa0bba49762f024d98ececb10`. Their complete Git trees are identical.
[Final feature CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35037737373)
passed Windows, Linux, macOS and Web. The primary checkout fast-forwarded to
that merge. [Merged-main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35038114051)
also passed all four platforms on`fecfdb3`. The
[post-merge audit](cartoon-standing-post-merge-audit.md) records fresh core,
platform and authoring review, a successful main data refresh, smoke followed
by31 art regressions, and exact package reconstruction. It found no new
actionable defect; existing issues remain in BACKLOG.

Engine/platform source, maintained tools/tests, CMake, gate and workflow files
remain unchanged from the pre-batch main`707a20b`. New code is confined to the
offline authoring/review bundle; Python is not a runtime dependency.

## Retained Windows capture failure

The first complete Windows gate built without warnings and passed every smoke
stage, but its palm outside-alpha regression failed a required capture-marker
assertion for `current-cartoon-none`. The child exited0 and stdout ended partway
through an asset path. The gate remained failed even though the other suites,
including all2452 golden hashes, passed.

For this delivery, an exact scratch copy of the gate changes only the repository
root and adds four distinct existing `--work` arguments to preserve wave/palm
smoke and regression artifacts. Test assertions and ordering remain unchanged.
The standard tracked gate is unchanged. Native tests run on an inactive desktop.

The retained failed PPM contains the complete1280x960 image with3686400 RGB bytes,
SHA256`292be7327fc8e3031ae65b3c74e3790356acc514b23c42f48577f3982e8f1d68`.
Its outside-alpha sample at900,350 has the expected RGB128,0,0. A fresh unchanged
focused run passed smoke then all8 palm cases, with all17 captures complete
and their required markers present. Its matching image is byte-identical to
the failed run. The cause of the missing marker remains unknown; no renderer
fix or weakened assertion is claimed.

The fresh full retained gate passed in138.398 seconds: build, all smoke stages,
every regression suite and all2452 golden hashes. The successful full log has
SHA256`9b346750fac54834886fa6ee63db3b865764f0f04e2c877695dcffd101531984`.
Source and deployed archives both remained
`096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.
Protected source/test/tool inputs stayed unchanged, and265 observations
confirmed the interactive desktop was preserved. The32 retained wave/palm PPMs
are complete. The [Windows evidence](../art/cartoon/walk-pilot/front-arrival-v1/review-evidence/windows-v1.json)
records the failed gate, focused control and successful full rerun separately.
