# Front walk refresh: delivery verification

The complete reviewed front-oblique walk is delivered: all six Cartoon drawings
JOHNWALK 024-029 play across the 23 stored walking positions. This latest pass
replaces 028/029 and retains the earlier Cartoon work in 024-027 exactly. The
final standing drawing 017 remains HD. The production archive contains 28
accepted Cartoon assets; the other 26 retain their earlier asset approvals.

PR [12](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/12) merged branch
`art/cartoon-front-walk-refresh`, based on `4551081`, into main as
`71f3e5f8d158e4d6a7315fe633d3c9944a4b21e5`. Its tree matches tested feature
head `513398e33cd48954736c3130b2b2cb77356a3858` exactly.

## Decisions

| Decision | Reason and review scope |
|---|---|
| Start with 028 | Its known hip-to-forward-foot mismatch tests the hardest pose problem before creating more frames. |
| Retain approved Cartoon 024-027 | Current 024 already has the improved trailing-foot angle. The user approved the complete six-drawing motion and native island preview after the 028/029 corrections. |
| Preserve the earlier Calm focus design | The user's prior expression choice remains the character reference. |
| Hide the far arm in 028 and 029 | The user preferred the new 028 draft but explicitly said the far/background arm would be occluded at that angle. |
| Keep scale 0.1 and cap registration | Independent silhouette fitting caused body popping earlier. New art is inspected and corrected within the existing frame canvases. |
| Use original pose geometry and retain its diagnostic palette caveat | Original resource indices establish the reference; their dump palette is not verified original-executable color. Gray shadows are not sole-contact landmarks. |
| Separate static, motion and native review | Static approval alone did not approve the cycle. The later standalone and native decisions explicitly approve the displayed complete walk and its existing HD 017 arrival transition. |
| Freeze historical test inputs | Both pilot suites must survive later front/island replacements without rewriting old expectations or requiring Git history, network access or a historical Pillow environment. |

## Tooling prerequisites

Commit `44de89e` is pushed to the feature branch. The inventory guard refuses
output/source aliases before parsing or export.
Its [verification](art-inventory-identity-verification.md) records Windows/Linux
smoke, regression, compiled mutations and gate-order execution under both
PowerShell versions. Approval-history support uses the existing full-catalog
inheritance resolver; [its declaration](cartoon-pilot-history.md) keeps original
facts and approvals separate from later production mappings.

Independent review found no approval bypass in pending-parent, changed inherited
PNG and omitted newly-accepted-complement probes. It did find schema1-only test
assumptions. The fixture correction exercises a simulated accepted 028 schema 2
promotion without modifying actual production artwork.

## Art checkpoints

The [authoring bundle](../art/cartoon/walk-pilot/front-refresh-v1/README.md)
preserves all generated outputs and used references, exact prompts, discarded
attempts, human feedback and technical previews. Six returned images have been
checked against their cache originals byte-for-byte; all eight distinct input
references resolve to retained repository files or ZIP members. Six original
reference images match the tracked decoded RGBA facts.

The first static browser comparison passed 3 smoke checks, then 36 regression
checks covering served HTML, image composition, controls, aspect ratio and
visibility at 700, 1280 and 1600 pixels. The user preferred the new 028 draft and
requested far-arm removal. The historical static page remains unchanged;
the subsequent arm-hidden 028 and adjacent 029 became the reviewed motion sources.

The standalone comparison now contains all 23 stored travel poses. Frames
024-027 keep exact approved runtime PNG bytes; new 028/029 use the common 0.1
scale, existing per-frame cap targets and original doubled canvases. All six
alpha-8 source bounds fit. The camera is fixed across the entire route, with
an explicit diagnostic endpoint hold. The user approved this motion with
"much better proceed"; `motion-acceptance-v1.json` preserves the exact response
and the accepted preview and runtime PNG identities.

The standalone tools passed 2 smoke checks followed by 15 regressions and 12
executed-source mutations. The extra browser control selects a revised 024 and
proves that future previews cannot claim 024-027 are always retained. The
published motion-v1 remains byte-identical to its frozen builder and inputs.
Served-page checks verified its 20 HTML/data/image files and all 24 states,
including speed, stepping, pause, repeat and the diagnostic hold.

A private Linux/Xvfb capture replaces only the two selected PNG members; 2577
other archive members remain byte-identical. The actual E-to-A route has 47
display records spanning 4360 ms. Twelve displays change only inside the
placed 028/029 canvases; the other 35 displays, including every HD 017 arrival
state, match the baseline. Draw dependencies and display times match. These
checks establish implementation isolation, not human approval of the gait.
The [native evidence](../art/cartoon/walk-pilot/front-refresh-v1/review-evidence/native-island-v1/README.md)
preserves capture helpers, identities, per-display reports and 94 image hashes.
The full runnable image bundle remains local. Its mask-removal, stopped-timer
and incorrect candidate-pixel controls all produced witnessed failures.

## Native approval and integration

The [published 23-position comparison](http://127.0.0.1:8932/front-refresh-motion-v1/review.html)
has human motion approval. The user then approved the native route and its
existing HD 017 arrival with "pass- proceed".
The [published native comparison](http://127.0.0.1:8932/front-refresh-island-v1/review.html)
preserves all 95 HTML/image identities. Publication smoke passed before checks
of all 47 display times, 94 rendered RGBA images, exact close-up pixels and
1280px layout. The final original HD standing pose remains unchanged.
The [production acceptance](../art/cartoon/walk-pilot/front-refresh-v1/production-acceptance.json)
records that separate decision and inherits the other 26 assets from the
previous arrival acceptance. The explicit pilot-history declaration keeps the
original 21-slot approval intact: 19 mappings are retained and two are replaced.

Production archive SHA256 is
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`,
identical to the native-reviewed private archive. Package smoke passed before
independent readback of all 2579 members. Only 028/029 differ from the previous
archive; all other 2577 members, including original resources, HD artwork,
other Cartoon assets and the runtime manifest, are unchanged. A deliberately
corrupted 028 produced exactly one named comparison failure.

The live preview test suite initially also depended on the old production
sprites. Its test fixture now uses the retained historical inputs so promotion
cannot invalidate historical authoring tests. Live production catalog checks
remain separate. The new isolation control supplies the actual new 028/029
bytes for an accidental live-archive read; a mutant that redirected preparation
to that live archive produced exactly one named failure. Platform checks and
delivery results follow below.

All authoring smoke suites passed before regression: inventory 3, history 1,
historical pilot 2 and full catalog 3. Regression passed 9 inventory controls
with 2 explicit Windows symlink-privilege skips, 22 history checks, 60 pilot
checks and 63 production-catalog checks. History regression also executes the
84-test future-promotion replay. Both maintained catalogs reproduce; original
pose facts, historical recipe mappings and human judgments remain unchanged.

The first local Windows gate passed every smoke stage and all regression
groups except a palm capture-marker check. Its HD child exited 0 but lacked
the required stdout marker, matching the previously documented intermittent
test symptom. No missing image is inferred: the default temporary directory
was cleaned before its contents could be inspected. The original gate log is
retained under `build/windows-gates/front-promotion-v1/`; its SHA256 is
`7aadb21f8c0cfd6086082a19380f48563ab72cfc455c17af34c3f545f8a3fac7`.
Focused retained diagnostics and a fresh full gate are separate checks.

The focused diagnostic passed smoke followed by all eight palm checks. All 17
captures contained complete 1280x960 PPM images and their required stdout
markers. The previously failing HD E-to-D case passed twice with identical
image SHA256 `f8c5ec8e39758d5ec35c4167f7760bd24c99ea606df86be41ac59a6aa3eb4515`.
Its result SHA256 is
`2660dfc91b14829cbdc3e60320402ad1871ce695ad70b108dd8b78c273143379`.
The original failure remains undiagnosed.

The separate fresh full Windows gate passed, with smoke preceding regression
and all 2,452 golden dump files byte-identical. Its log under
`build/windows-gates/front-promotion-v2/` has SHA256
`e69b67b35f919c4ced200ad62c1bef02cde2c7b0adcc217c7d41383f559b8595`.
Tests ran on an inactive desktop and preserved the interactive desktop.
The [feature CI run](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35027930677)
passed Windows, Linux, macOS and Web at the exact feature head above. Windows
inventory regression explicitly skipped two symlink controls because the
process lacked symlink privilege; Linux exercised all eleven controls.

## CI correction

The initial art commit changed the image-learning index without regenerating
its normalized fingerprint in the maintained pilot catalog. Linux CI detected
that stale record. Regenerating the catalog corrected it; 2 pilot smoke checks,
60 regressions and both catalog reproduction checks passed. The motion approval
updates the same index, so its fingerprint is regenerated with this checkpoint.

## Merged local deployment

Main was fast-forwarded to the merge commit, and the CMake `jc_runtime_data`
target updated `build/Release/scrantic_data.zip` to the exact approved archive.
The EXE and SCR bytes and timestamps remained unchanged; this art delivery
changes no engine, platform, vendored library or CMake source. The local
deployment record is `build/front-main-deployment/refresh.json`.

The deployed build passed the complete `gate.ps1 -NoBuild -SmokeOnly` sequence,
then all 31 native art-style regression checks under Windows PowerShell 5.1.
Both ran on inactive desktops and preserved the user's interactive desktop.
The smoke log SHA256 is
`e926ee99b52cfd023f423b896559bd3df230a871329f2d96832e942379ff3c03`;
the regression log SHA256 is
`eba5f9e3cba1a4c3793718c3d66e7638c4b96e6ec6a4e8992babefe1e9684632`.
These local checks verify deployed asset selection, fallback and settings;
they supplement the full fresh-build feature gate and merged-main CI.

The [merged-main CI run](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35028462790)
passed all four platforms. The [fresh post-merge audit](front-refresh-post-merge-audit.md)
records source coverage, repeated authoring checks, exact six-drawing/frozen
preview reproduction and three newly documented existing edge-case defects.
All findings and the repeated capture-artifact retention issue are in
[BACKLOG.md](../BACKLOG.md). No new art-integration blocker was found in the
reviewed paths; known code and visual-coverage limits remain explicit.
