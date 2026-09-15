# Maintenance post-merge audit

This audit began after PR 6 merged to main at
`4586f128ec50f8bc390f160f8c24466b95a8cc47`. The
[main CI run](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34938468373)
passed Windows, Linux, macOS and Web. The [verification record](maintenance-verification.md)
distinguishes those results from the initial local gate failure and later checks.
The complete follow-up PowerShell 5.1 gate subsequently passed without compiler
warnings and matched all 2,452 golden files. The interruption diagnosis and the
earlier unexplained palm failure remain documented separately.

## Review coverage

| Area | Review scope |
| --- | --- |
| Engine and resource lifecycle | Independent review of main startup/shutdown, ADS scheduling and slot lifetime, TTM decoding/tag ownership, parser aliases, walking transitions, sound lifetime, graphics and art selection. No new shipped-data regression, recurring scene leak or double-free was found. Global resource tables remain process-owned with one production parse call. |
| Platform adapters | Independent review of all four backends, the platform interface, PNG ownership adapter, Web page, audio ownership and graphics/event callers. Normal cleanup, borrowed pixels, Linux stop/join order, Web audio servicing and bounded log retention remain consistent. |
| Build and tools | Explicit-path extractor I/O, sound/walk helpers, shared Web builder, both PowerShell wrappers, CI workflow and test integration. The legacy sound layout remains explicitly limited; version-specific original walking equality is documented separately. |
| Original reference | Native resource comparison, pinned JavaScript execution and a distinct `.Z` decoder for three selected resources. Agreement is scoped to decoded indices and packed bytes, not original-executable scene behavior. |
| Art metadata | Original facts, HD proxies, export transforms, native capture records and acceptance are kept distinct. Arithmetic and file identity checks do not assign an aesthetic score. Approved artwork and existing learning records remain unchanged. |

## Findings and decisions

| Finding | Disposition |
| --- | --- |
| One unexplained native palm capture failure | Improve the existing assertion to preserve native exit status and output after its temporary directory is removed. Both forced-error diagnostics retained their evidence after cleanup; focused real smoke and eight regressions passed. No retry was added and no runtime cause is claimed fixed. |
| Drawing primitives and clip zones | Rectangle fill and pixel-based primitives do not use the active draw zone that sprites honor. Static script reachability is concrete; an original-versus-port visible defect is not established. Record SBREAKUP tag 34 as a targeted reference trace before changing behavior. |
| Post-open audio error results | Windows refill and macOS enqueue/start calls leave some return values unchecked. Add controlled error probes before choosing recovery semantics. Physical hardware faults were not reproduced. |
| Overlong TTM string parsing | A compiled isolated probe linked unmodified main TTM and utility sources. Short and 255-character strings retained delay six; a 256-character string with embedded SET_DELAY bytes changed delay/timer to 123. The parser stops copying and misidentifies the following byte as the terminator. Record bounded rejection/consumption work; no shipped-scene impact was established. |
| Large CLI seed parsing | The actual Windows executable accepted an overflowing positive decimal seed before version, while rejecting seed abc. Frame limits are fixed; seed still lacks errno/range checks and narrows to unsigned int. Record a fixed-range contract and cross-platform boundary probes as follow-up. |
| Stale audio comment | Correct the comment that called absent sound filenames incomplete data. The original RIFF payload evidence establishes content presence; sample-ID mapping still needs investigation. Playback behavior is unchanged. |
| Original and bundled pixel differences | Keep separate identities. All 79 selected images differ between distributions, despite matching native dimensions. Distinct decoder execution supports the original packed bytes; editing history and original palette/compositing remain unresolved. |
| Previously accepted Cartoon poses | Preserve acceptance and source images. The new original comparison led the user to request an inward angle for 024's trailing right foot and corrected left-forward/right-back leg order for 028/029. Record those targets separately; 026/027 lift remains undecided. Revised art requires a new motion review. |
| Interactive native test interruption | A separate full-gate smoke timed out after input enabled pause and disabled maxspeed. A cloned dump proved frame 158/400 and the normal Sleep loop; the user confirmed accidental input. Record the interruption and a test-isolation follow-up. It does not explain the earlier quick palm capture failure. |
| Optimization | Keep flip caching and damage tracking as measurement-led backlog work. This pass claims no measured performance saving. |

The [backlog](../BACKLOG.md) records each follow-up with evidence and a next action.
The existing resource-table ownership, unfinished scene commands, malformed LZW
validation and sample-ID mapping remain open. They are not silently reclassified
as fixed by a green build or matching asset dimensions.

This was a source audit with bounded behavioral tests. It is not exhaustive
fuzzing, long-duration heap profiling, a new line-by-line audit of vendored codecs,
physical audio testing or verification of every original scene outcome.
