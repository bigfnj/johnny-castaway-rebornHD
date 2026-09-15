# Legacy cleanup post-merge audit

The independent audit began after PR 4 was merged to main at
`50eb6f4bc4b1bea704d03bbdda360be216be7d31`. The merged checkout passed the full
Windows gate without warnings, all eight frozen-baseline scene comparisons, and
[four-platform main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34929288040).
Detailed phase and mutation evidence is in [the verification record](legacy-cleanup-verification.md).

## Coverage

| Review | Scope and evidence |
| --- | --- |
| Engine core, independent of its implementation author | Full ADS, TTM, resource, decompression, graphics, island, benchmark, dump and utility implementations/headers, with callers traced. Reviewed active versus owned layers, borrowed buffers, reset/release paths, command reachability and parser contracts. |
| Platform adapters, independent of their implementation author | Windows, Linux, macOS and Web backends, shared platform interface, PNG loaders/decoder and ZIP adapter. Reviewed construction failure, window/surface ownership, event dispatch, presentation, audio lifecycle and shared callers. |
| Application controls | Startup/CLI, configuration, art catalog, events, sound, story, walking, path selection, all three static data tables and the Web page. All 36 shipped walking node pairs have paths, at most five alternatives and six nodes, with valid headings/bookmarks. |
| Build, tools and records | CMake/runtime-data dependencies, CI/release, native/Unix/Web build paths, maintained test orchestration and negative controls, art inventory/validation/packing, original extraction helpers, legacy Visual Studio definitions and documentation. |

No introduced normal-playback regression was found. The complete review found
additional existing engine defects for a bounded follow-up: signed left shifts
in circle drawing, odd-width SCR decoding, consecutive zero-image BMP name
ownership, and one unused scene field. Follow-up implementation and validation
are still in progress; this record does not yet claim those fixes are delivered.

## Decisions and remaining work

| Decision or finding | Disposition |
| --- | --- |
| Preserve original rendering and art identity | The archive hash remains `fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`. No changes to assets, accepted source art, acceptance records or image-learning documentation. Controlled complete frames remain byte-identical to the pre-cleanup build. |
| Reachable unfinished commands | Retain the dispatch paths. Original-engine reference scenes are needed before implementing new semantics; exact opcodes and occurrence counts are in [the command review](legacy-command-review.md). |
| Memory ownership | Repeated scene/slot/graphics teardown is tested with tracked native allocations. Parsed resource tables remain intentionally process-owned. Full resource unload is prerequisite work for a future in-process restart or live pack replacement. |
| Older tooling | Record incomplete local Web page assembly and unchecked original-data extractor I/O in the backlog. The supported builder and packaged application do not depend on those helpers. |
| Large CLI frame limits | Record missing range/errno checks and uint32 counter wrap. Ordinary tested limits work; unsupported oversized values can defeat bounded execution. |
| Long Web debug sessions | The actual inline script retained all 100,000 supplied log lines in a Node/DOM fixture. This proves unbounded diagnostic retention, not a browser heap measurement or ordinary-playback leak. A bounded log policy is backlog work. |
| Remaining audio behavior | Source review identified Web scheduling starvation during the standalone GJHOT long-delay path and Linux ALSA setter/partial-write handling gaps. These predate cleanup. The backlog records concrete call paths and the advancing-clock/device-response tests needed next; no physical-audio result is claimed. |
| Optimization | Preserve behavior and keep flip caching/damage tracking as measurement-led proposals. This cleanup claims no new measured performance saving. |

[BACKLOG.md](../BACKLOG.md) holds actionable remaining items and earlier resolved
or rejected findings. A source review and bounded tests do not establish every
original-script semantic, physical audio device or desktop fullscreen behavior.
Vendored compression code is unchanged and exercised by the corpus, rather than
being a new line-by-line third-party audit. No exhaustive fuzzing or long-duration
cross-platform heap profiling was performed.
