# Profile-walk post-merge audit

PR14 merged the approved eight-pose profile family into main as
`c903fb57ce5c4224dede16992288c70f47a7a3d7`. Its complete tree matches tested
feature head `3295acc1d8b4979b14891cbb2bac82b4dfd2c149`. The primary checkout
fast-forwarded to that merge before this fresh audit began.

[Feature CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35109871512)
passed Windows, Linux, macOS and Web. The
[merged-main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35110533235)
also passed all four platforms on `c903fb5`. The
[delivery record](cartoon-profile-walk-verification.md) preserves scoped user
approval, authoring checks, native previews and the full local Windows gate.
Runtime/platform source, maintained tools/tests, build and workflow files remain
unchanged from pre-batch main `00f1ba7`. New code is confined to offline art
authoring and review; Python is not an application dependency.

## Fresh audit coverage

| Area | Review and result |
|---|---|
| Core engine | Fresh review of 32 files covering startup/configuration, ADS/TTM, walking/story paths, resource decoding, graphics, sound, events, dumps and native extractors found no newly established actionable defect or dead/nonoperable call path. Bounded walking/path table analyses passed. |
| Platforms, rendering and deployment | Fresh review across 23 platform/build/rendering paths found no new concrete defect. Runtime archive refresh retained all ten existing binary hashes and modification times; fresh smoke then 31 art regressions passed. |
| Authoring | Reviewed 24 code paths, verified all 21 generated-image ancestry records, reproduced the exact production ZIP and every selected runtime/padded output, and passed both catalog checks. One historical static replay limitation is documented below. |
| Application Web page | Fresh review of URL/style arguments, selector reload, toolbar key isolation, log retention, fatal state and audio-resume listener lifetime found no new confirmed issue. |
| Native review page | Controls, timestamp selection, full-canvas mirroring, fixed cameras and bounded image cache reviewed. Loading/redraw efficiency is a future measurement opportunity below. |

The application review does not establish absence of all leaks or validate
physical audio. No new heap/race detector or performance benchmark was run.
Reachable unfinished scene commands remain compatibility work; do not remove
them as dead code. Existing source-established issues remain in BACKLOG.

The authoring audit reproduced one historical replay limitation in isolated
scratch: the first static preview builder overwrites its existing review record
using the current archive hash. The old 32-asset baseline reproduces its frozen
record exactly; the promoted 40-asset archive changes that one field while
leaving HTML identical. No primary evidence was overwritten. The current source
README and delivery guide now explain isolation and pinned inputs. BACKLOG keeps
the successor's configurable-output and refusal work. The frozen historical
helper remains unchanged so the accepted checkpoint remains reproducible.

## Local installation and evidence

The core report is retained at `build/profile-postmerge-audit/core.json`, SHA256
`f7c6b4517ca885f634329cfdecc5ee5de87131231a3328e07eec28d590111a0c`.
Its read-only table analysis covered all 36 source/destination path pairs
(at most five paths and six nodes), 22 walking links and six turn groups.
These are bounded source/table checks, not new compiled runtime probes.
The report fingerprints files at review time; BACKLOG was subsequently updated
with the findings from the parallel authoring and Web reviews.

The deployed runtime archive now matches production SHA256
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`.
The refresh changed the data archive only. Fresh full smoke passed before all
31 art-style regressions passed on inactive desktops. Protected inputs and the
user's active desktop stayed unchanged. The platform/build report is retained at
`build/profile-postmerge-audit/platform-build.json`, SHA256
`cb4f4a87eb2a8a319bf9c12dcc74eb9ab97946a5b851154d1b2faab878768a24`.
It binds the inspected files and runtime checks. Existing Windows raw-input
cleanup, post-open audio error handling and failed-capture retention items remain
in BACKLOG; the audit did not establish a new recurring allocation leak.

Fresh authoring validation passed 9 smoke checks before 174 executed regressions.
Two Windows symlink cases explicitly skipped for missing privilege; both catalog
reproduction checks passed. The preserved standard helper reproduced the complete
production ZIP byte-for-byte, including all 2591 member payloads, with the named
001 corruption control firing as intended. All 2583 old payloads stayed exact.
The local report is `build/profile-postmerge-audit/authoring.json`, SHA256
`8ce3851db88bb157c987ab43fdf647f285250aee2c65edf717ed497c7255ff30`.
It also binds the isolated historical-replay positive control and changed-archive
probe; no primary historical record was overwritten.

Fresh root Web notes are retained locally at
`build/profile-postmerge-audit/root-web.json`, SHA256
`75ae4fffbd41b40664d1fee340815bf72a03c33f32f28ab0e9f35dfb62fc3952`.
They bind the inspected source files and published-review manifest. The viewer
has 234 unique full-scene images. Its cache is bounded by those images and ends
with the page; this source review does not establish an accumulating memory leak.
It redraws and resets both canvases each playing animation tick, including ticks
within the same recorded pose. Before longer reviews, measure a shared successor
that loads images as needed and redraws only when necessary. Preserve exact
capture pixels and accepted historical helper bytes. No speed or memory saving
is claimed without a measured comparison.

## Next work

| Work | Recommendation |
|---|---|
| Connecting poses | Next author ordinary 009/010/012 with their complete route and story contexts. Shared 003 is now covered by the accepted profile family. |
| Story coverage | Review unseen script placements and contacts separately. Approved walking routes do not approve every occurrence of the same sprite. |
| Tooling | Reuse the saved image lessons and explicit frame/recipe binding. Measure shared review loading/redraw changes before larger scene batches. |
| Existing code issues | Keep the concrete engine/platform follow-ups in BACKLOG; fix a reproduced blocker when its affected scene enters review. |

The new review-tool opportunity and remaining work are recorded in
[BACKLOG](../BACKLOG.md). Generation ancestry and human acceptance remain intact.
