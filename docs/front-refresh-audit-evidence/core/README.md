# Fresh core audit after PR 12

Audited main `71f3e5f8d158e4d6a7315fe633d3c9944a4b21e5`. The inspected core and extractor implementations are unchanged from baseline `4551081495eee81e5e5bf2d8b5f00a5619a176a2`. No introduced core blocker was found in this review.

`coverage-results.json` records the precise inspection scope, repository-relative source locations, Git blob IDs and worktree SHA256 fingerprints, existing backlog comparison, new findings and suggested backlog wording. `probe-evidence.json` records actual compiled controls and failure witnesses, using container paths rather than workstation paths.

Two existing boundary defects were reproduced: missing TTM tag metadata can return an unset offset or hang lookup, and the BMP dumper ignores an actual ENOSPC close failure. Neither is evidence of a normal shipped-scene regression. Both compiled probes use untouched engine source. The tag probe deliberately fills allocated memory to expose initialization dependence; it does not alter the engine's tag logic. The dump probe observes the real fclose result while the actual dumper writes an isolated output that points to `/dev/full`.

For a fresh reproduction, mount the approved repository read-only at `/src` in the existing `johnny-platform-cleanup:latest` image and a new writable scratch directory at `/out`. Run `python3 /src/build/front-refresh-postmerge-audit/core/run_probes.py`. The runner builds both small executables and records each command and witness. It requires a fresh output directory because the two output cases create their own folders. The retained image ID is in the coverage report; local availability is not a claim that this image is distributed publicly.

No tracked source was changed, no native user-interface window was opened, and no full gate was rerun for this subtask. The ownership review does not establish a leak-free application. No performance saving is claimed.
