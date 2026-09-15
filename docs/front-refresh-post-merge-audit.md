# Front walk delivery: post-merge audit

The audit examines merged main `71f3e5f8d158e4d6a7315fe633d3c9944a4b21e5`.
Its tree equals tested feature head `513398e33cd48954736c3130b2b2cb77356a3858`.
The [delivery verification](cartoon-front-refresh-verification.md) records the
approved complete front walk, its two replacement drawings and deployed ZIP.

Three parallel reviews covered engine behavior and ownership; platform,
rendering and build paths; and authoring, approval history and reproduction.
The root review independently checked merge/deployment identity, the new
boundary probes, the Web fullscreen observation and final documentation.
No engine, platform, vendored library or CMake source changed in this delivery.

The [retained audit records](front-refresh-audit-evidence/README.md) include core
coverage and 23 fingerprints, platform/build coverage for 36 files, and authoring
coverage with 175 fingerprints. These counts describe recorded evidence, not
a claim that every line received equal scrutiny.

## Validation

The [feature CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35027930677)
and [merged-main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35028462790)
passed Windows, Linux, macOS and Web. The local fresh full Windows gate passed
after a separately retained intermittent capture-marker failure and focused
diagnostic run. The verification document records each result distinctly.

The deployed main build passed the complete no-build smoke sequence, followed
by 31 native art-style regressions. Tests ran on inactive Windows desktops.
The source and deployed ZIP match the approved native-preview archive; local
EXE/SCR bytes and timestamps remained unchanged.

Fresh-main authoring checks passed smoke before regression: inventory 3 smoke
and 9 regression passes with 2 explicit Windows symlink-privilege skips;
history 1/22, pilot metadata 2/60, production catalog 3/63 and front helpers
2/15. History includes the 84-test future-promotion replay. Both catalog checks
passed; all six current runtime drawings and all 20 frozen review files
reproduced. All 48 protected evidence identities checked by the audit passed.

Supplemental windowless PNG and lifecycle checks passed, as did build-contract
controls and nine executed mutations. Two extra gate-order audit attempts did
not pass: PowerShell 5.1 could not discover `Get-FileHash` through its inherited
module path, and the PowerShell 7 whole fixture exceeded the scratch runner's
240-second deadline without retaining partial output. They are not counted as
green checks. The separate successful full/deployed gates used a cleaned child
environment; no cause is inferred for the supplemental timeout.

## Newly recorded existing defects

These findings concern existing code and are recorded in [BACKLOG.md](../BACKLOG.md).
They did not alter the approved walk or its test results.

| Finding | Evidence | Follow-up |
|---|---|---|
| Incomplete TTM tag tables leave offset fields uninitialized | Untouched `ttm.c` with a declared count of two and one scanned tag leaves a sentinel offset untouched. Deterministic allocator fill returns bogus offset 2779096485 for tag 65535; zero fill enters the lookup loop until the bounded probe timeout. Valid-tag and ordinary missing-tag controls pass. | Reject or explicitly bound incomplete tables, initialize every retained field, and ensure tag lookup progresses when an offset is zero. Test malformed tables alongside original resources. |
| Resource dumps can report normal return after output failure | Actual `dumpBmp` writes through a path targeting `/dev/full`. The observing wrapper records `fclose=-1`, `errno=28`, while the function returns normally; a regular output file succeeds. Other dump writers have the same unchecked output/close pattern but were not separately fault-injected. | Check write and close failures and name the output file; preserve valid golden output. |
| Web fullscreen toggle loses synchronization after browser exit | Merged `platform_web.c` toggles a private flag without observing browser fullscreen changes. An existing local Web build shows fullscreen false, true after Alt+Enter, false after `document.exitFullscreen()`, still false after the next Alt+Enter, then true on the following toggle. | Observe actual browser fullscreen state and handle failed/deferred requests; add enter, external-exit, denied-request and re-entry controls. |

The TTM probe uses malformed metadata, not a shipped-scene reproduction. Its
timeout is the observed defect and is not counted as a passing application
test. The dump probe uses real Linux output failure and an observing close
wrapper, not a mocked successful write.

The Web probe used an existing local build with recorded binary hashes, not a
fresh merged-main Web build. It establishes the observed fullscreen sequence;
its null exit/error fields do not prove engine liveness or error-free execution.
The source finding is independently visible in the merged implementation.

## Existing work retained

The audit retains the earlier raw-input cleanup, common audio startup ordering,
post-open device error handling, malformed config/LZW/string handling, primitive
clipping and unfinished TTM behavior items. Reachable unfinished commands remain
distinct from dead code. Process-owned resource arrays need an explicit unload
design before live restarts or pack switching; their lifetime alone does not
establish a recurring leak.

The native capture-marker failure recurred once. The failed temporary PPM was
removed by the test harness before inspection, so its existence is unknown.
The retained diagnostic run had 17 complete images and markers, and the separate
fresh full gate passed. The backlog now specifies preserving failed palm/wave
work directories and timeout output without weakening marker assertions.

No new performance improvement is claimed. Flip caching and damage tracking
remain profiling candidates. Physical audio, real Linux window-manager behavior,
all original story outcomes and every mirrored walking route were not re-reviewed
visually during this art delivery. Vendored libraries were not exhaustively
audited. Source review and bounded tests are not proof that all leaks or defects
are absent.

## Next art group

The entire reviewed six-drawing front walk is delivered. The next useful art
group is standing frame 017 plus its actual wait/turn transitions, traced from
the original scripts before generation. Keep the accepted walk intact and use
the same static, full-motion and native-scene checkpoints for the next family.
