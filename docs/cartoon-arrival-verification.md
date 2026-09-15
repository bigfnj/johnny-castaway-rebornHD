# Cartoon arrival verification

The user approved standing JOHNWALK 018 with "nailed it, proceed" after viewing
the actual rear walk settle into it on the Cartoon island. The pack now has 28
approved assets: twelve walking poses, one standing pose and fifteen island
layers. The [acceptance](../art/cartoon/arrival-pilot-v1/production-acceptance.json)
records the exact review and inherits the previous 27 approvals.

## Package and scope

The production ZIP SHA256 is
`0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd`.
All 2,578 prior entries are unchanged. The only added member is
`data/styles/cartoon/BMP/JOHNWALK.BMP/018.png`, SHA256
`5ab7fb306a39eab69d419f3602101a72e3cca30d15e6432c58a6beaf975e9190`.
All 2,579 uncompressed members match the private reviewed candidate, whose
container SHA256 is
`bc47235fbb12ed5c2a080471a556e4e61e41e4e4c886de94fd02dd7591d6386d`.
The existing production builder changes ZIP layout but preserves member bytes.
The style manifest, original resources and all 27 previous ledger rows remain
unchanged. [Package evidence](../art/cartoon/arrival-pilot-v1/production-verification.json)
records this independent readback after package validation passed.

The displayed route uses the real `adsPlayWalk(1,3,0,3)` with Linux island seed
11 and path seed 2. Its 23 walking poses remain unchanged; standing 018 replaces
HD during the subsequent 1,600 ms hold. The native origin shift from (302,244)
to (298,240) remains visible through a fixed camera. User approval includes
the smaller foot's contact appearance. Its pixel-region depth differs from
the original reference; anatomical parity and unseen routes/story uses are
not established. The [arrival lessons](art-style-learnings-arrival.md) preserve
that distinction and the exact export dependency, Pillow 12.2.0.

## Verification before delivery

| Area | Evidence |
| --- | --- |
| Export | 3 smoke checks, then 20 regressions and 17 witnessed source mutants passed; the candidate recipe and raw artwork remained exact |
| Native Linux review | Baseline smoke preceded its 47-display regression; candidate smoke preceded its 47-display regression. All walking pixels stayed identical, with differences confined to the arrival canvas |
| Browser review | 2 smoke checks, then 4 grouped regressions covered all 47 times and 94 canvas hashes, stepping, repeat and both camera views; served HTML and PNG bytes matched |
| Review controls | 4 Python helper mutations, 2 served-browser mutations and 1 changed-walking-pixel replay mutation produced named failures with execution witnesses |
| Git byte preservation | Normal checkout smoke passed; removing the arrival attribute produced one named byte-preservation failure; outside text and PNG controls behaved as expected |
| Production package | 28 accepted PNGs passed validation before build; independent readback preserved all old members and equaled the reviewed candidate |
| Pilot metadata | 2 smoke checks, then 60 regressions and 56 executed source mutants passed; the new arrival-prefix removal caused one named failure |
| Full catalog | 3 smoke checks, then 63 regressions passed; both metadata reproduction checks passed on the frozen 28-asset inputs |
| Existing art tools | 20 regressions passed after package and metadata smoke |
| Windows native delivery | The complete unchanged rerun passed: 27 smoke, 27 screensaver, 31 style checks and all 2,452 golden hashes, with the remaining full-gate suites green |

Compact native evidence is [preserved here](../art/cartoon/arrival-pilot-v1/review-evidence/native-v1/README.md).
It pins the saved Linux observer, 59 source/build inputs and all reports. Full
capture sets and binaries stay in ignored local build folders. This evidence
does not claim a fresh engine rebuild or original-executable parity.

[Final metadata evidence](../art/cartoon/arrival-pilot-v1/review-evidence/metadata-v1/verification.json)
preserves command order and source identities. The pilot retains its original
21 assets. The full catalog reports 28 accepted and 2,373 pending slots;
its 51 supplied-original evidence slots remain unchanged. A separate
[integration audit](../art/cartoon/arrival-pilot-v1/review-evidence/integration-v1.json)
verified the complete approval chain and reproduced 018 under Pillow 12.2.0.

## Windows delivery and retained failure

The first full Windows gate passed smoke and the style suites, then failed a
palm capture-marker assertion. Its child exited 0, but stdout ended mid asset
log. This assertion checks the completion marker before opening the PPM; the
test then removed its temporary directory. The existence and content of that
first PPM are unknown. The exact gate output remains locally preserved.

With code and archive unchanged, a fresh inactive-desktop control passed palm
smoke before all eight palm cases. Explicit work directories retained its logs
and images. The subsequent full gate passed. This is an intermittent diagnostic
failure with an unresolved cause, not evidence of a missing image or a repaired
renderer. A backlog item now requests retaining these artifacts on failure.

[Windows evidence](../art/cartoon/arrival-pilot-v1/review-evidence/windows-v1.json)
records all three runs. The successful full-run log SHA256 is
`c08b0fa322fd8c932c8f22f08087053f56d1ffb1b21b52849187cda7dd060185`.
Its 278 desktop observations confirmed the input desktop remained unchanged;
runtime inputs and the deployed production archive stayed exact. Local full
logs remain under `build/windows-gates/arrival-promotion-v1/`,
`arrival-palm-control-v1/` and `arrival-promotion-v2/`.

The pre-commit Git-index audit verified all 55 then-staged arrival files against
their working bytes, including all 30 native evidence links and the complete
28-asset approval/archive chain. Delivery-only Windows evidence is added
separately after that audit.

## Merge and post-merge audit

Artwork commit `16f64a05291dc7dc55f583c43e34fefa6bf39c21` was merged through
[PR 11](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/11) at
`a799e087664f2ec4844dfd8c79d90ce30760aab2`.
[PR CI run 35008054223](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35008054223)
passed Windows, Linux, macOS and Web. The merged tree equals the tested branch
tree exactly. Engine/platform source, native extractors, CMake, gate and CI
wiring remain unchanged from the pre-arrival baseline.
The [merged-main CI run 35008710565](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35008710565)
also passed all four platforms on `a799e087`.

The fresh core audit read current startup/CLI and configuration, event handling,
ADS/TTM dispatch and cleanup, story/walking/path logic, benchmark, resource
parsing/decompression, dump/utilities, ZIP ownership and native extraction tools.
It found no new confirmed runtime defect. Scene-owned layers, tags and sprites
remain distinct from the decoded resource pool owned for the process lifetime.
No newly recurring memory leak or measured performance saving was established.
The known malformed-config/string/LZW, seed-range, unfinished-command and legacy
extraction items remain in BACKLOG.md. This review did not run a new sanitizer,
race detector or original-executable comparison.

Local core evidence is `build/arrival-main-audit/core.json`, SHA256
`265382ceb4edabff4fcf367353b2a09a9cd123a9a20db3b6e53791c3a34f773f`.
The source audit records 25 read files and their exact identities.

The independent platform/build audit reread all four backends and APIs,
graphics/style/island/common audio, PNG/ZIP ownership, startup/shutdown callers,
CMake deployment, native/Web builders, CI/release runners and browser runtime
JavaScript. It found no new confirmed defect or backlog omission. Existing
Windows raw-input cleanup, audio startup/post-open errors, saved-zone behavior
and primitive clipping remain documented. Backend hooks that are intentionally
empty were not classified as broken calls. Its local notes are
`build/postmerge-arrival-audit/platform-build.md`, SHA256
`eed546571c99f81f2d6dd529af53c7cc5bb671a36fd9e6b521a220cf6b6829f3`.

Fresh main authoring checks passed in order: both smoke suites, 60 pilot and
63 full-catalog regressions, 20 art-tool regressions and both reproduction
checks. The unchanged mutation matrices were not repeated. Logs are retained
under `build/arrival-postmerge-authoring/`.

The capture-harness audit found that the wave helper shares the palm helper's
failure-artifact retention weakness. BACKLOG.md now covers both. No new
runtime failure is inferred from that source observation.

The authoring review reproduced one existing CLI defect in
`tools/art_inventory.py:59-62`: using the same source and output path replaces
the ZIP with JSON while exiting 0. A distinct-output control preserved its
source. Both executions used disposable fixtures; the production archive was
untouched. The required input/output identity check is now in BACKLOG.md for
the next authoring-tool batch. This is separate from arrival rendering and
does not invalidate the package builder's validated preservation behavior.

The completed authoring audit read all five art tools, imported resource
framing/dimension readers, the 018 exporter/tests and all eleven native/browser
helper snapshots. It found no other actionable issue. All 56 arrival files
match main HEAD/index and the committed/working art branch bytes. All 30 native
evidence links and 28 accepted PNG hashes remain valid, and both 018 recipes
reproduce the exact accepted output under Pillow 12.2.0. The consolidated
local report is `build/arrival-postmerge-authoring/audit-summary.json`, SHA256
`7a17935461edcd81bd28c164a1ab2e75aa3312274ca8d3b9b20f5719410d0322`.
The saved fresh-check report SHA256 is
`a8fdb7dbe3f53018687f85bddd3acfbf99371a6daa1460f6572f76e1284d30b0`.

The primary checkout's `jc_runtime_data` target refreshed the deployed ZIP to
the approved production hash. EXE/SCR bytes and timestamps did not change.
On inactive desktops, main smoke passed before all 31 art regressions passed.
Both runs preserved the input desktop and protected runtime/test/tool inputs.
The smoke log SHA256 is
`8cb14d889dae3446ec73e595749d5ced7e80c7b578623bdc66b7f213afd6cf78`;
the art-regression log SHA256 is
`eba5f9e3cba1a4c3793718c3d66e7638c4b96e6ec6a4e8992babefe1e9684632`.
The consolidated local deployment/harness report is
`build/arrival-main-deployment/report.json`, SHA256
`931e90456a6b77bd8e61c574425e2318357e010a21775d91acafd4d3b43b59d6`.

## Decisions for the next batch

| Decision | Reason and next action |
| --- | --- |
| Keep the exact approved 018 | The user reviewed the actual arrival and foot contact; preserve its geometry and registration |
| Keep the pack partial | Eight wait/turn-table assets and most scenes still use fallback; one arrival does not complete story coverage |
| Retain both export dependency versions | Arrival uses Pillow 12.2.0 while the previous rear export used 12.3.0; reproduce each with its own recipe |
| Revisit the front walk next | Apply the rear knee/foot continuity lessons, beginning with an explicit pilot-history transition and a small review batch |
| Improve failed-capture evidence | Retain palm and wave test artifacts before changing any renderer behavior based on a missing stdout marker |
| Fix the inventory path collision | Reject output aliases of the source ZIP before the next authoring-tool expansion; retain positive and negative controls |
