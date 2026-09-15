# Maintenance verification

Baseline: main `c582c3e3088b1cb464a6aa19b3846af4e089e23e`.
This record separates executed checks from remaining reference work. The
[plan](maintenance-completion-plan.md) records the accepted scope; the
[knowledge base](knowledge-base/README.md) records original-engine research.

## Changes and phase checks

| Area | Executed verification |
| --- | --- |
| Frame parsing and stopping | Actual CLI range/overflow checks and a compiled events.c probe: 2 smoke, then 22 regression checks. Three rebuilt negative controls fired. Historical ordinary stopping/capture timing remained unchanged. |
| ALSA setup and pending delivery | 5 backend smoke checks, then 32 regressions with real pthreads and controlled ALSA responses. Seventeen rebuilt delivery mutations fired with the intended assertions. Tests include setup rollback, negotiated rate, partial mono/stereo tails, recovery, wait failure and concurrent close. |
| Web audio | Pinned Emscripten 6.0.9: 3 backend smoke checks, then 11 regressions. Advancing-clock controls and actual GJHOT playback preserved 9,672 sound-24 PCM bytes across ten contiguous scheduled buffers. Five compiled negative controls and a complete rebuilt browser mutant exposed the intended failures. |
| Web log retention | Actual served page: smoke, five regressions and nine served-HTML mutations. The Chromium heap oracle checks retained storage before inspecting truncated strings, so V8 substring flattening cannot hide the backing-store defect. Fatal status survives truncation and eviction. |
| Web controls | Actual browser startup, painted pixels, responsiveness, bounded exit and audio scheduling passed, followed by all ten style/keyboard controls and the existing keyboard-listener mutation. |
| Windows wrapper | Actual PowerShell 5.1 and 7 child processes cover local/container selection, paths, caller state and failure propagation. Both shells performed a real pinned container build. Four PowerShell negative controls fired; Python build/cache/output guards also fired. An installed native Windows SDK compiler was not available. |
| Extractor I/O | Windows Visual Studio and Linux Make builds each passed four smoke and 14 regression cases, 14 injected I/O controls and 15 rebuilt mutants, followed by restored controls. Integrated native CMake targets also passed smoke/regression. |
| Gate sequencing | Both PowerShell versions passed real script fixtures with deliberate smoke fail-through mutations. Unix flow passed 15 controls and ten mutations. CI/release Web command flow passed 12 controls and four mutations. |

New negative controls require the changed artifact or served page to be verified
and executed before interpreting failure. A nonzero exit or timeout alone is
not a successful mutation result. All runtime binary/source changes were made
in isolated worktrees or isolated test copies.

## Integrated local checks

The integration Windows PowerShell 7 gate completed with exit zero and no
compiler warnings. It ran all smoke before regression and matched all 2,452
golden decoded files. Full output is retained locally at
`build/cleanup/maintenance-integrated-ps7/gate.log`, with exit metadata beside it.

The integration Linux gate used a tracked export of
`2f1a958b13afc372a346aa61a49e865395ebaa39` and the existing
`johnny-platform-cleanup:latest` image on the WSL-backed Docker engine. It
completed with exit zero and all 2,452 golden files equal. The image ID was
`c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Source was mounted read-only; the isolated container exited and was removed.
The evidence directory is `build/maintenance/final-linux-2f1a958/evidence`.

That Linux build surfaced GCC's conservative `-Wclobbered` warning for a
setjmp/longjmp test expectation. The fixture variable is now volatile. A fresh
GCC `-O3` build with all enabled warnings promoted to errors passed, followed
by ordinary, maximum and unlimited cases. The Windows probe was rebuilt and
passed smoke followed by all 22 frame regressions. Production code was unchanged.

The latest integrated Web build verified exact preload archive bytes and passed
backend and browser smoke before the regressions above. Existing Emscripten
macro/unused-parameter and miniz diagnostics remain visible; this is not claimed
as a warning-free Web build. Browser reports are in `build/web-*.json`.

## Preserved rendering and artwork

Integration review also reproduced two isolated build-fixture failures introduced
by the new native extractor targets: frame mutation and runtime-archive fixtures
had copied CMakeLists.txt without its new tools/ sources. Their explicit copy
lists now include those sources. Fresh rebuilt frame mutants and actual
application archive-refusal controls passed after the fixes.

| Comparison | Result |
| --- | --- |
| Historical scene matrix | All eight complete HD/Cartoon, day/night, frame-1/frame-13 captures match the frozen pre-cleanup baseline exactly. |
| Historical wave path | All nine complete HD/fallback captures match the preserved baseline executable exactly. |
| Historical palm path | All four complete HD/partial-fallback captures match the preserved baseline driver exactly. |

Those optional historical comparisons ran in addition to the independent alpha,
clipping, restoration and fallback pixel controls in the routine gate. Reports
are in `build/maintenance/integrated-scenes`, `integrated-wave-history` and
`integrated-palm-history`. The runtime archive SHA-256 remains
`fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`.
Approved artwork, prompts, source files and art-direction learning records are
outside the code-maintenance changes.

## Original reference and limits

The knowledge base catalogs 176 guide observations and associates every ID once
with an explicitly tentative family, source context, story day, calendar window,
legacy fault or unresolved event. An independent review checked source hashes,
tag descriptions and crosswalk coverage. All original ADS/TTM names are present;
all ten ADS and 40 of 41 TTM decoded streams are identical. The report records the
remaining script edit, omitted bitmap and unused script variants without claiming
complete behavioral parity.

The inventory generator passed 20 behavioral controls followed by 18 isolated
compiled-source mutations. Each mutant required an advanced artifact timestamp,
an executed function witness and exactly one intended failure naming the source.
A fresh production dump matched all 2,452 golden files, and fresh JSON/Markdown
generation was byte-identical. The original input hashes remained unchanged.

The supplied original launched in DOSBox and was then relaunched successfully
in a window at the user's request. Its hashes, launch recipe and observed scope
are in [original-reference.md](knowledge-base/original-reference.md).
All 489 walk records match. All 23 declared RIFF/WAVE payloads match bundled
WAV prefixes. Original-resource script comparisons and catalog mappings remain
distinct from full behavioral parity.

Physical speakers, Linux desktop fullscreen negotiation, all original outcome
branches, the original sample-ID translation and complete malformed LZW
validation remain outside these passing checks. The corresponding concrete
findings are retained in BACKLOG.md. No new art pack or scene-command behavior
was introduced by this maintenance pass.
